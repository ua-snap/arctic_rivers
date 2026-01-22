#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import numpy as np
import xarray as xr
import dask
from luts import stat_var_dict, data_source_dict, gcm_metadata_dict


try:
    from dask.distributed import Client, LocalCluster
except Exception:
    Client = None
    LocalCluster = None

def parse_args():
    p = argparse.ArgumentParser(description="Calculate Hydrological Statistics from combined Arctic Rivers NetCDF files")
    p.add_argument("--wt", required=True, help="Combined WT NetCDF file path")
    p.add_argument("--q", required=True, help="Combined Q NetCDF file path")
    p.add_argument("--wt-output", required=True, help="Output WT statistics NetCDF file path")
    p.add_argument("--q-output", required=True, help="Output Q statistics NetCDF file path")
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


def calculate_statistics(ds):
    # for each stream id and model, get the monthly mean flow values for each month across all years in each era
    # create new variables for each month using the stat_var_dict

    # Add month as a coordinate
    ds = ds.assign_coords(month=("time", ds["time"].dt.month.values))
    
    # Group by month and era, compute statistics
    # This preserves stream_id and model dimensions automatically
    monthly_mean = ds.groupby(["month", "era"]).mean(dim="time", skipna=True)

    # Round to 3 decimal places
    monthly_mean = monthly_mean.round(3)
    
    # Get the original variable name
    orig_var = list(ds.data_vars)[0]
    
    # Create a new dataset with separate variables for each month
    result_ds = xr.Dataset()
    
    # Copy coordinate variables (not dimensions)
    result_ds["stream_id"] = ds["stream_id"]
    result_ds["model"] = ds["model"]
    result_ds["era"] = monthly_mean["era"]
    
    # Create a separate variable for each month
    for stat_var_name, info in stat_var_dict.items():
        month_num = info["month"]
        description = info["description"]
        
        # Extract data for this specific month and drop month coordinate
        month_data = monthly_mean[orig_var].sel(month=month_num).drop_vars("month")
        
        # Create new variable (dimensions: model, stream_id, era)
        result_ds[stat_var_name] = month_data
        # Set only description and units, remove long_name and coordinates
        result_ds[stat_var_name].attrs = {
            "description": description,
            "units": ds[orig_var].attrs.get("units", "")
        }
    
    return result_ds


def add_metadata(ds):
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

    print("Calculating statistics...")
    wt_stats = calculate_statistics(wt_ds)
    q_stats = calculate_statistics(q_ds)

    print("Adding metadata...")
    wt_stats = add_metadata(wt_stats)
    q_stats = add_metadata(q_stats)

    wt_stats.to_netcdf(args.wt_output)
    print("WT statistics saved to", args.wt_output)
    q_stats.to_netcdf(args.q_output)
    print("Q statistics saved to", args.q_output)

    if client is not None:
        client.close()

if __name__ == "__main__":
    main()