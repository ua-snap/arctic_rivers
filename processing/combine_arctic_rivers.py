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
    p.add_argument("--wt-output", required=True, help="Output WT NetCDF file path")
    p.add_argument("--q-output", required=True, help="Output Q NetCDF file path")
    p.add_argument("--workers", type=int, default=0, help="Number of Dask workers (0 disables Dask)")
    p.add_argument("--threads-per-worker", type=int, default=1, help="Threads per Dask worker")
    p.add_argument("--chunk-time", type=int, default=0, help="Optional chunk size for time dimension")
    return p.parse_args()


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

    return combined


def main():
    # Suppress dask chunking warnings
    dask.config.set({"array.slicing.split_large_chunks": False})
    args = parse_args()
    data_dir = Path(args.data_dir)

    wt_files = sorted(data_dir.glob("*_WT.nc"))
    q_files = sorted(data_dir.glob("*_Q.nc"))

    if not wt_files:
        print("No WT files found. Exiting...", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Found {len(wt_files)} WT files to combine.")

    if not q_files:
        print("No Q files found. Exiting...", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Found {len(q_files)} Q files to combine.")

    client = setup_dask(args.workers, args.threads_per_worker)
    
    # When using Dask workers, disable parallel to avoid NetCDF threading issues
    use_parallel = (args.workers == 0)

    combined_wt = open_wt(wt_files, args.chunk_time, use_parallel)
    combined_q = open_q(q_files, args.chunk_time, use_parallel)

    combined_wt.to_netcdf(args.wt_output)
    print(f"Combined WT dataset saved to {args.wt_output}")

    combined_q.to_netcdf(args.q_output)
    print(f"Combined Q dataset saved to {args.q_output}")

    if client is not None:
        client.close()


if __name__ == "__main__":
    main()
