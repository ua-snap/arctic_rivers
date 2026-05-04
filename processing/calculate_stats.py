#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd
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
    p.add_argument("--q", required=True, help="Combined Q NetCDF file path")
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
    # Count non-NaN values to identify all-NaN groups
    count = ds.groupby(["month", "era"]).count(dim="time")
    monthly_mean = ds.groupby(["month", "era"]).mean(dim="time", skipna=True)
    
    # Replace 0's with NaN where all values were NaN (count == 0)
    orig_var = list(ds.data_vars)[0]
    monthly_mean[orig_var] = monthly_mean[orig_var].where(count[orig_var] > 0)

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
        units = info["units"]
        
        # Extract data for this specific month and drop month coordinate
        if month_num == "all":
            month_data = monthly_mean[orig_var].mean(dim="month", skipna=True)
        else:
            month_data = monthly_mean[orig_var].sel(month=month_num).drop_vars("month")
        
        # Clear existing attributes and set new ones
        month_data.attrs = {}
        
        # Create new variable (dimensions: model, stream_id, era)
        result_ds[stat_var_name] = month_data
        # Set only description and units
        result_ds[stat_var_name].attrs = {
            "description": description,
            "units": units
        }
    
    return result_ds


def add_source_dimension(result_ds):
    excluded_models = ['historical', 'PGWh', 'PGWm']
    source_index = pd.Index(['original_gcm', 'gcm_diff', 'gcm_diff_applied_to_cheng'], name='source')

    new_vars = {}
    for var_name in stat_var_dict.keys():
        da = result_ds[var_name]

        past = da.sel(era='1990-2021')
        future = da.sel(era='2034-2065')
        ratio = (future / past).where(~past['model'].isin(excluded_models))

        # gcm_diff: 1990-2021 slot is NaN, 2034-2065 slot is ratio
        gcm_diff_da = xr.concat(
            [xr.full_like(past, fill_value=np.nan), ratio],
            dim=pd.Index(['1990-2021', '2034-2065'], name='era'),
        )

        # gcm_diff_applied_to_cheng
        hist_baseline = da.sel(era='1990-2021', model='historical')  # dims: (stream_id,)
        future_applied = ratio * hist_baseline  # historical row stays NaN via ratio
        is_historical = past['model'] == 'historical'
        past_applied = xr.full_like(past, fill_value=np.nan).where(~is_historical, hist_baseline)
        gcm_diff_applied_da = xr.concat(
            [past_applied, future_applied],
            dim=pd.Index(['1990-2021', '2034-2065'], name='era'),
        )

        combined = xr.concat([da, gcm_diff_da, gcm_diff_applied_da], dim=source_index)
        combined.attrs = da.attrs
        new_vars[var_name] = combined

    result = xr.Dataset(new_vars)
    result.attrs = result_ds.attrs
    return result


def add_metadata(ds):
    # these must be strings to be netCDF serializable
    ds.attrs["Data_Source"] = str(data_source_dict)
    ds.attrs["GCM_Metadata"] = str(gcm_metadata_dict)
    return ds


def main():
    # Suppress dask chunking warnings
    dask.config.set({"array.slicing.split_large_chunks": False})
    args = parse_args()
    client = setup_dask(args.workers, args.threads_per_worker)

    print("Loading dataset...")
    q_ds = xr.open_dataset(args.q, chunks={"time": args.chunk_time} if args.chunk_time > 0 else None)

    print("Assigning era coordinate...")
    q_ds = assign_era(q_ds)

    print("Calculating statistics...")
    q_stats = calculate_statistics(q_ds)

    print("Adding source dimension...")
    q_stats = add_source_dimension(q_stats)

    print("Adding metadata...")
    q_stats = add_metadata(q_stats)

    print("Saving Q statistics to NetCDF...")
    q_stats.to_netcdf(args.q_output)
    print("Q statistics saved to", args.q_output)

    if client is not None:
        client.close()

if __name__ == "__main__":
    main()