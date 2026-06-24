#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import numpy as np
import xarray as xr
import dask

try:
    from dask.distributed import Client, LocalCluster
except Exception:
    Client = None
    LocalCluster = None


def parse_args():
    p = argparse.ArgumentParser(description="Combine Arctic Rivers NetCDF files")
    p.add_argument("--data-dir", default="/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/", help="Directory containing NetCDF files")
    p.add_argument("--wt-output", help="Output WT NetCDF file path (required unless --skip-wt)")
    p.add_argument("--q-output", required=True, help="Output Q NetCDF file path")
    p.add_argument("--workers", type=int, default=0, help="Number of Dask workers (0 disables Dask)")
    p.add_argument("--threads-per-worker", type=int, default=1, help="Threads per Dask worker")
    p.add_argument("--chunk-time", type=int, default=0, help="Optional chunk size for time dimension")
    p.add_argument("--skip-wt", action="store_true", help="Skip combining WT files (use when only Q needs to be (re)built)")
    args = p.parse_args()
    if not args.skip_wt and not args.wt_output:
        p.error("--wt-output is required unless --skip-wt is set")
    return args


def setup_dask(workers: int, threads: int):
    if workers > 0 and LocalCluster is not None:
        cluster = LocalCluster(n_workers=workers, threads_per_worker=threads, processes=True)
        client = Client(cluster)
        return client
    return None

def standardize_time_dimension(ds):
    if "time" in ds.dims:
        time_values = ds["time"].values
        if np.issubdtype(time_values.dtype, np.datetime64):
            # Normalize datetime64 to midnight (00:00:00) by casting to 'D' and back to 'ns'
            times = time_values.astype('datetime64[D]').astype('datetime64[ns]')
            ds = ds.assign_coords(time=times)
            return ds
        else:
            raise ValueError("Time dimension is not of datetime64 type.")
    else:
        raise ValueError("Dataset does not contain a time dimension.")


def convert_cms_to_cfs(ds, var_name):
    # Conversion factor from cubic meters per second to cubic feet per second
    conversion_factor = 35.3147
    ds[var_name] = ds[var_name] * conversion_factor
    # Update units attribute if it exists
    if "units" in ds[var_name].attrs:
        ds[var_name].attrs["units"] = "cfs"
    return ds


# The river-routing model is cold-started with empty channel storage at the start of
# each run, producing anomalously low/near-zero streamflow for the first several weeks.
# This is real model behavior, not a data error, but it biases any statistic that
# aggregates across all years of an era (e.g. daily climatology min, monthly means)
# since only one year out of ~32 is affected. historical and the historical-period
# halves of C2LE2/C2LE4/C2LE7/C2LE9 start 1990-01-01; the future-period halves of all
# 6 non-historical models start 2034-01-01. Confirmed via diagnostic plots that the
# artifact has resolved (merged into normal year-to-year variability) by day 60 in
# every (model, era) block; see PR description for the supporting plots.
SPINUP_ERA_STARTS = [np.datetime64("1990-01-01"), np.datetime64("2034-01-01")]
SPINUP_MASK_DAYS = 60


def mask_spinup(ds, var_name, n_days=SPINUP_MASK_DAYS):
    """Replace the first n_days of streamflow after each model-run start with NaN.

    Safe to apply unconditionally across all models: a model with no data at a given
    era start is already all-NaN there, so masking is a no-op for it.
    """
    time = ds["time"]
    mask = xr.zeros_like(time, dtype=bool)
    for start in SPINUP_ERA_STARTS:
        mask = mask | ((time >= start) & (time < start + np.timedelta64(n_days, "D")))
    ds[var_name] = ds[var_name].where(~mask)
    ds.attrs["Spinup_Masking"] = (
        f"Streamflow ({var_name}) values for the first {n_days} days after the start of "
        "each model run (1990-01-01 for `historical` and the historical-period halves of "
        "C2LE2/C2LE4/C2LE7/C2LE9; 2034-01-01 for the future-period halves of all 6 "
        "non-historical models) were replaced with NaN before any downstream statistics "
        "or climatologies were computed. The river-routing model is cold-started with "
        "empty channel storage at the start of each run, producing anomalously low/"
        "near-zero streamflow for the first several weeks; this is real model behavior, "
        "not a data error, but biases statistics that aggregate across all years of an "
        "era. Timesteps are preserved (not dropped). Does not apply to stream temperature."
    )
    return ds


def open_wt(files, chunk_time, use_parallel):
    # Group files by model/scenario
    model_groups = {}
    for f in files: 
        model = f.name.split("_")[1]  # Extract model name from filename (e.g., hC2LE2, historical)
        # if model name is not "historical", drop the first character (the "f" or "h" prefix) because these just denote the different time periods
        if model != "historical":
            model = model[1:]
        if model not in model_groups:
            model_groups[model] = []
        model_groups[model].append(f)
    
    # Load each model separately
    model_datasets = []
    for model, model_files in sorted(model_groups.items()):
        def preprocess(ds):
            ds = ds[["T_stream"]].sel(no_seg=1).drop_vars("no_seg")
            return ds
        
        kwargs = {"combine": "nested", "concat_dim": "time", "parallel": use_parallel, "preprocess": preprocess}
        if chunk_time and chunk_time > 0:
            kwargs["chunks"] = {"time": chunk_time}
        
        ds = xr.open_mfdataset(sorted(model_files), **kwargs)
        ds = ds.sortby("time")
        ds = ds.assign_coords(model=model)
        model_datasets.append(ds)
    
    # Concatenate along model dimension with outer join to handle different time ranges
    combined = xr.concat(model_datasets, dim="model", join="outer", fill_value=np.nan)

    # Rename the "hru" dimension to "stream_id" and convert to integer
    combined = combined.rename({"hru": "stream_id"})
    combined["stream_id"] = combined["stream_id"].astype(int)

    # Normalize time to midnight after concatenation
    combined = standardize_time_dimension(combined)

    return combined


def open_q(files, chunk_time, use_parallel):
    # Group files by model/scenario
    model_groups = {}
    for f in files:
        model = f.name.split("_")[1]  # Extract model name from filename (e.g., hC2LE2, historical)
        # if model name is not "historical", drop the first character (the "f" or "h" prefix) because these just denote the different time periods
        if model != "historical":
            model = model[1:]
        if model not in model_groups:
            model_groups[model] = []
        model_groups[model].append(f)
        
  # Load each model separately
    model_datasets = []
    for model, model_files in sorted(model_groups.items()):
        def preprocess(ds):
            # check for duplicates in the "seg" dimension: we need to drop duplicates (they should be identical, just pick the first value)
            if "seg" in ds.dims:
                _, index = np.unique(ds["seg"], return_index=True)
                ds = ds.isel(seg=index)
            ds = ds[["IRFroutedRunoff"]]
            return ds
        
        kwargs = {"combine": "nested", "concat_dim": "time", "parallel": use_parallel, "preprocess": preprocess}
        if chunk_time and chunk_time > 0:
            kwargs["chunks"] = {"time": chunk_time}
        
        ds = xr.open_mfdataset(sorted(model_files), **kwargs)
        ds = ds.sortby("time")
        ds = ds.assign_coords(model=model)
        model_datasets.append(ds)
    
    # Concatenate along model dimension with outer join to handle different time ranges
    combined = xr.concat(model_datasets, dim="model", join="outer", fill_value=np.nan)

    # Rename the "seg" dimension to "stream_id" and convert to integer
    combined = combined.rename({"seg": "stream_id"})
    combined["stream_id"] = combined["stream_id"].astype(int)

    # Normalize time to midnight after concatenation
    combined = standardize_time_dimension(combined)

    # Convert from cms to cfs
    combined = convert_cms_to_cfs(combined, "IRFroutedRunoff")

    # Mask the model cold-start spin-up window (see mask_spinup docstring)
    combined = mask_spinup(combined, "IRFroutedRunoff")

    return combined


def main():
    # Suppress dask chunking warnings
    dask.config.set({"array.slicing.split_large_chunks": False})
    args = parse_args()
    data_dir = Path(args.data_dir)

    q_files = sorted(data_dir.glob("*_Q.nc"))
    if not q_files:
        print("No Q files found. Exiting...", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Found {len(q_files)} Q files to combine.")

    if not args.skip_wt:
        wt_files = sorted(data_dir.glob("*_WT.nc"))
        if not wt_files:
            print("No WT files found. Exiting...", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Found {len(wt_files)} WT files to combine.")

    client = setup_dask(args.workers, args.threads_per_worker)

    # When using Dask workers, disable parallel to avoid NetCDF threading issues
    use_parallel = (args.workers == 0)

    if not args.skip_wt:
        combined_wt = open_wt(wt_files, args.chunk_time, use_parallel)
        combined_wt.to_netcdf(args.wt_output)
        print(f"Combined WT dataset saved to {args.wt_output}")
    else:
        print("--skip-wt set: not combining WT files.")

    combined_q = open_q(q_files, args.chunk_time, use_parallel)
    combined_q.to_netcdf(args.q_output)
    print(f"Combined Q dataset saved to {args.q_output}")

    if client is not None:
        client.close()


if __name__ == "__main__":
    main()
