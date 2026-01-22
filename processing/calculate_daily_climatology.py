#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import numpy as np
import xarray as xr
import dask
from luts import clim_var_dict, data_source_dict, gcm_metadata_dict


try:
    from dask.distributed import Client, LocalCluster
except Exception:
    Client = None
    LocalCluster = None


def parse_args():
    p = argparse.ArgumentParser(description="Calculate Daily Climatologies from combined Arctic Rivers NetCDF files")
    p.add_argument("--wt", required=True, help="Combined WT NetCDF file path")
    p.add_argument("--q", required=True, help="Combined Q NetCDF file path")
    p.add_argument("--wt-output", required=True, help="Output WT daily climatology NetCDF file path")
    p.add_argument("--q-output", required=True, help="Output Q daily climatology NetCDF file path")
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


def assign_era(ds):
    # split into two eras based on time coordinate and create a new coordinate "era"
    # eras values should be "1990-2021" and "2034-2065"
    time_values = ds["time"].values
    eras = np.where(time_values < np.datetime64("2022-01-01"), "1990-2021", "2034-2065")
    ds = ds.assign_coords(era=("time", eras))
    return ds


def calculate_daily_climatology(ds):
    # Add dayofyear as a coordinate
    ds = ds.assign_coords(dayofyear=("time", ds["time"].dt.dayofyear.values))
    
    # Group by dayofyear and era, compute statistics
    # This preserves stream_id and model dimensions automatically
    daily_min = ds.groupby(["dayofyear", "era"]).min(dim="time", skipna=True)
    daily_mean = ds.groupby(["dayofyear", "era"]).mean(dim="time", skipna=True)
    daily_max = ds.groupby(["dayofyear", "era"]).max(dim="time", skipna=True)

    # Round stats to 3 decimal places
    daily_min = daily_min.round(3)
    daily_mean = daily_mean.round(3)
    daily_max = daily_max.round(3)

    # Rename dayofyear to doy
    daily_min = daily_min.rename({"dayofyear": "doy"})
    daily_mean = daily_mean.rename({"dayofyear": "doy"})
    daily_max = daily_max.rename({"dayofyear": "doy"})
    
    # Get the main variable name and create output dataset
    var_name = list(daily_min.data_vars)[0]
    result = xr.Dataset({
        "doy_min": daily_min[var_name],
        "doy_mean": daily_mean[var_name],
        "doy_max": daily_max[var_name]
    })
    return result


def add_metadata(ds):
    for var_name, info in clim_var_dict.items():
        if var_name in ds:
            ds[var_name].attrs["description"] = info["description"]
            ds[var_name].attrs["units"] = info["units"]
    ds.attrs["Data_Source"] = data_source_dict
    ds.attrs["GCM_Metadata"] = gcm_metadata_dict
    return ds


def main():
    # Suppress dask chunking warnings
    dask.config.set({"array.slicing.split_large_chunks": False})
    args = parse_args()
    client = setup_dask(args.workers, args.threads_per_worker)

    print("Loading datasets...")
    wt_ds = xr.open_dataset(args.wt, chunks={"time": args.chunk_time} if args.chunk_time > 0 else None)
    q_ds = xr.open_dataset(args.q, chunks={"time": args.chunk_time} if args.chunk_time > 0 else None)

    print("Assigning era coordinate...")
    wt_ds = assign_era(wt_ds)
    q_ds = assign_era(q_ds)

    print("Calculating daily climatologies...")
    wt_daily_clim = calculate_daily_climatology(wt_ds)
    q_daily_clim = calculate_daily_climatology(q_ds)

    print("Adding metadata...")
    wt_daily_clim = add_metadata(wt_daily_clim)
    q_daily_clim = add_metadata(q_daily_clim)

    wt_daily_clim.to_netcdf(args.wt_output)
    print("WT daily climatology saved to", args.wt_output)
    q_daily_clim.to_netcdf(args.q_output)
    print("Q daily climatology saved to", args.q_output)

    if client is not None:
        client.close()

if __name__ == "__main__":
    main()