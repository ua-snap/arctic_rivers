#!/usr/bin/env python3
"""Add source dimension to mhit_indices.nc.

Transforms (era, model, stream_id) → (source, era, model, stream_id) with three
source values: original_gcm, gcm_diff, gcm_diff_applied_to_cheng.

Usage:
  cd /import/home/jdpaul3/arctic_rivers/processing/matlab
  conda activate snap-geo
  python add_source_dim_mhit.py \\
    --input  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \\
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_sourced.nc
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

sys.path.insert(0, str(Path(__file__).parent))
from luts_mhit import DATA_SOURCE_DICT, GCM_METADATA_DICT, MHIT_STATS

EXCLUDED_MODELS = ["historical", "PGWh", "PGWm"]
SOURCE_INDEX = pd.Index(["original_gcm", "gcm_diff", "gcm_diff_applied_to_cheng"], name="source")


def parse_args():
    p = argparse.ArgumentParser(description="Add source dimension to mhit_indices.nc")
    p.add_argument("--input", required=True, help="Input mhit_indices.nc path")
    p.add_argument("--output", required=True, help="Output path for sourced NetCDF")
    return p.parse_args()


def build_sourced_variable(da: xr.DataArray, difference_method: str) -> xr.DataArray:
    past = da.sel(era="1990-2021")    # (model, stream_id)
    future = da.sel(era="2034-2065")  # (model, stream_id)
    is_excluded = past["model"].isin(EXCLUDED_MODELS)

    if difference_method == "ratio":
        safe_past = past.where(past != 0, other=0.01)
        gcm_diff = (future / safe_past).where(~is_excluded)
    else:  # absolute
        gcm_diff = (future - past).where(~is_excluded)

    # source=gcm_diff: 1990-2021 slot is all NaN; 2034-2065 slot holds the change signal
    gcm_diff_da = xr.concat(
        [xr.full_like(past, fill_value=np.nan), gcm_diff],
        dim=pd.Index(["1990-2021", "2034-2065"], name="era"),
    )

    # source=gcm_diff_applied_to_cheng
    hist_baseline = da.sel(era="1990-2021", model="historical")  # (stream_id,)

    if difference_method == "ratio":
        future_applied = gcm_diff * hist_baseline
    else:
        future_applied = gcm_diff + hist_baseline

    # 1990-2021 slot: NaN for all models except historical, which gets hist_baseline
    is_hist = past["model"] == "historical"
    past_applied = xr.full_like(past, fill_value=np.nan).where(~is_hist, hist_baseline)
    applied_da = xr.concat(
        [past_applied, future_applied],
        dim=pd.Index(["1990-2021", "2034-2065"], name="era"),
    )

    combined = xr.concat([da, gcm_diff_da, applied_da], dim=SOURCE_INDEX)
    combined.attrs = da.attrs
    return combined


def main():
    args = parse_args()
    print(f"Opening {args.input} ...")
    ds = xr.open_dataset(args.input)
    print(f"  Dimensions: {dict(ds.dims)}")
    print(f"  Variables:  {list(ds.data_vars)}")

    new_vars = {}
    for var_name, meta in MHIT_STATS.items():
        if var_name not in ds:
            print(f"  WARNING: {var_name} not in dataset, skipping")
            continue
        new_vars[var_name] = build_sourced_variable(ds[var_name], meta["difference_method"])
        print(f"  {var_name} ({meta['difference_method']}) ... done")

    print("Assembling output dataset ...")
    out_ds = xr.Dataset(new_vars, attrs=ds.attrs)
    # NetCDF global attributes must be strings
    out_ds.attrs["Data_Source"] = str(DATA_SOURCE_DICT)
    out_ds.attrs["GCM_Metadata"] = str(GCM_METADATA_DICT)

    encoding = {
        v: {"zlib": True, "complevel": 4, "dtype": "float32"}
        for v in out_ds.data_vars
    }

    print(f"Writing {args.output} ...")
    out_ds.to_netcdf(args.output, encoding=encoding)

    print("\nDone.")
    print(f"  Output dimensions: {dict(out_ds.dims)}")
    print(f"  Sources: {out_ds['source'].values.tolist()}")
    print(f"  Models:  {out_ds['model'].values.tolist()}")
    print(f"  Eras:    {out_ds['era'].values.tolist()}")


if __name__ == "__main__":
    main()
