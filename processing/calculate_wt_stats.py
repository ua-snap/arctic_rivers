#!/usr/bin/env python3
import argparse
import numpy as np
import pandas as pd
import xarray as xr
import dask
from luts_wt import wt_stat_var_dict, data_source_dict, gcm_metadata_dict


try:
    from dask.distributed import Client, LocalCluster
except Exception:
    Client = None
    LocalCluster = None


def parse_args():
    p = argparse.ArgumentParser(description="Calculate stream temperature statistics from combined Arctic Rivers NetCDF files")
    p.add_argument("--wt", required=True, help="Combined WT NetCDF file path")
    p.add_argument("--wt-output", required=True, help="Output WT statistics NetCDF file path")
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
    time_values = ds["time"].values
    eras = np.where(time_values < np.datetime64("2022-01-01"), "1990-2021", "2034-2065")
    ds = ds.assign_coords(era=("time", eras))
    return ds


def get_annual_max_timing(T_era):
    """For each year in T_era, return (annual_max_val, annual_max_doy) with a 'year' dimension.

    annual_max_doy is the Julian day (1-366) when the maximum value occurs.
    For the 7-day rolling average use case, the 'time' dimension of T_era has already been
    replaced by the rolling mean values, so the timing reflects the center of that window.
    """
    years = sorted(int(y) for y in np.unique(T_era.time.dt.year.values))
    max_vals = []
    max_doys = []
    for yr in years:
        T_yr = T_era.sel(time=slice(f"{yr}-01-01", f"{yr}-12-31"))
        if T_yr.sizes["time"] == 0:
            continue
        doy_yr = T_yr.time.dt.dayofyear
        has_data = T_yr.notnull().any(dim="time")
        # Fill all-NaN slices with a sentinel so argmax never errors.
        # The sentinel position is masked out by has_data below.
        T_yr_safe = T_yr.fillna(-9999.0)
        idx = T_yr_safe.argmax(dim="time").compute()
        max_val = T_yr.isel(time=idx).where(has_data)
        max_doy = doy_yr.isel(time=idx).where(has_data).astype(float)
        max_vals.append(max_val.assign_coords(year=yr).expand_dims("year"))
        max_doys.append(max_doy.assign_coords(year=yr).expand_dims("year"))
    return xr.concat(max_vals, dim="year"), xr.concat(max_doys, dim="year")


def calculate_statistics(ds):
    era_slices = {"1990-2021": slice("1990", "2021"), "2034-2065": slice("2034", "2065")}
    era_results = []

    for era_name, era_slice in era_slices.items():
        era_data = ds.sel(time=era_slice)
        T = era_data["T_stream"]
        results = {}

        # ── Threshold exceedance: mean annual count of days above threshold ──
        has_valid_year = T.notnull().groupby("time.year").any(dim="time")
        for thresh, var_name in [
            (13.0, "wt_days_gt13_mean"),
            (18.0, "wt_days_gt18_mean"),
            (20.0, "wt_days_gt20_mean"),
        ]:
            annual_count = (T > thresh).groupby("time.year").sum(dim="time")
            results[var_name] = annual_count.where(has_valid_year).mean(dim="year", skipna=True)

        # ── Monthly min/mean/max: mean across all months of each type in era ──
        monthly = T.resample(time="ME").mean()
        month_count = monthly.groupby("time.month").count(dim="time")
        by_month_mean = monthly.groupby("time.month").mean(dim="time", skipna=True)
        by_month_min  = monthly.groupby("time.month").min(dim="time", skipna=True)
        by_month_max  = monthly.groupby("time.month").max(dim="time", skipna=True)
        month_names = ["jan", "feb", "mar", "apr", "may", "jun",
                       "jul", "aug", "sep", "oct", "nov", "dec"]
        for stat_key, by_month in [
            ("mean", by_month_mean),
            ("min",  by_month_min),
            ("max",  by_month_max),
        ]:
            masked = by_month.where(month_count > 0)
            for m, mname in enumerate(month_names, 1):
                results[f"wt_{stat_key}_{mname}"] = masked.sel(month=m).drop_vars("month")

        # ── Annual maximum daily temperature: magnitude and Julian day ────────
        ann_max_val, ann_max_doy = get_annual_max_timing(T)
        results["wt_ann_max_temp_mean"]     = ann_max_val.mean(dim="year", skipna=True)
        results["wt_ann_max_temp_doy_mean"] = ann_max_doy.mean(dim="year", skipna=True)

        # ── Max 7-day rolling average: magnitude and Julian day of center ──────
        rolling7 = T.rolling(time=7, center=True, min_periods=4).mean()
        r7_max_val, r7_max_doy = get_annual_max_timing(rolling7)
        results["wt_7d_max_temp_mean"]     = r7_max_val.mean(dim="year", skipna=True)
        results["wt_7d_max_temp_doy_mean"] = r7_max_doy.mean(dim="year", skipna=True)

        # ── Cumulative degree days above 0°C, May–September ───────────────────
        may_sept_mask = T.time.dt.month.isin([5, 6, 7, 8, 9]).values
        may_sept_T = T.isel(time=may_sept_mask).clip(min=0)
        annual_cdd = may_sept_T.groupby("time.year").sum(dim="time", skipna=True)
        has_valid_may_sept = may_sept_T.notnull().groupby("time.year").any(dim="time")
        results["wt_cdd_may_sept_mean"] = annual_cdd.where(has_valid_may_sept).mean(dim="year", skipna=True)

        era_results.append((era_name, results))

    # ── Build result dataset with era dimension ───────────────────────────────
    result_ds = xr.Dataset()
    result_ds["stream_id"] = ds["stream_id"]
    result_ds["model"]     = ds["model"]
    result_ds["era"]       = xr.DataArray(["1990-2021", "2034-2065"], dims=["era"])

    var_names = list(era_results[0][1].keys())
    for var_name in var_names:
        era_das = []
        for era_name, results in era_results:
            da = results[var_name].assign_coords(era=era_name).expand_dims("era")
            era_das.append(da)
        combined = xr.concat(era_das, dim="era").round(3)
        combined.attrs = {}
        result_ds[var_name] = combined

    for var_name, info in wt_stat_var_dict.items():
        if var_name in result_ds:
            result_ds[var_name].attrs = {
                "description": info["description"],
                "units": info["units"],
            }

    return result_ds


def add_source_dimension(result_ds):
    excluded_models = ["historical", "PGWh", "PGWm"]
    source_index = pd.Index(
        ["original_gcm", "gcm_diff", "gcm_diff_applied_to_cheng"], name="source"
    )

    new_vars = {}
    for var_name in wt_stat_var_dict.keys():
        da   = result_ds[var_name]
        past = da.sel(era="1990-2021")
        future = da.sel(era="2034-2065")

        # Absolute difference (future − past); NaN for non-GCM models
        diff = (future - past).where(~past["model"].isin(excluded_models))

        # gcm_diff: past slot is NaN, future slot is the absolute difference
        gcm_diff_da = xr.concat(
            [xr.full_like(past, fill_value=np.nan), diff],
            dim=pd.Index(["1990-2021", "2034-2065"], name="era"),
        )

        # gcm_diff_applied_to_cheng: apply each GCM's delta to the historical baseline
        hist_baseline = da.sel(era="1990-2021", model="historical")  # (stream_id,)
        future_applied = diff + hist_baseline   # NaN for excluded models via diff
        is_historical  = past["model"] == "historical"
        past_applied   = xr.full_like(past, fill_value=np.nan).where(~is_historical, hist_baseline)
        gcm_diff_applied_da = xr.concat(
            [past_applied, future_applied],
            dim=pd.Index(["1990-2021", "2034-2065"], name="era"),
        )

        combined = xr.concat([da, gcm_diff_da, gcm_diff_applied_da], dim=source_index)
        combined.attrs = da.attrs
        new_vars[var_name] = combined

    result = xr.Dataset(new_vars)
    result.attrs = result_ds.attrs
    return result


def add_metadata(ds):
    ds.attrs["Data_Source"]   = str(data_source_dict)
    ds.attrs["GCM_Metadata"]  = str(gcm_metadata_dict)
    return ds


def main():
    dask.config.set({"array.slicing.split_large_chunks": False})
    args   = parse_args()
    client = setup_dask(args.workers, args.threads_per_worker)

    print("Loading dataset...")
    wt_ds = xr.open_dataset(
        args.wt,
        chunks={"time": args.chunk_time} if args.chunk_time > 0 else None,
    )

    print("Assigning era coordinate...")
    wt_ds = assign_era(wt_ds)

    print("Calculating statistics...")
    wt_stats = calculate_statistics(wt_ds)

    print("Adding source dimension...")
    wt_stats = add_source_dimension(wt_stats)

    print("Adding metadata...")
    wt_stats = add_metadata(wt_stats)

    print("Saving WT statistics to NetCDF...")
    wt_stats.to_netcdf(args.wt_output)
    print("WT statistics saved to", args.wt_output)

    if client is not None:
        client.close()


if __name__ == "__main__":
    main()
