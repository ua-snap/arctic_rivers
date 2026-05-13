#!/usr/bin/env python3
"""Compute ma99 (mean annual flow = average of monthly means ma12-ma23) and add it to mhit_indices.nc.

Run this before add_source_dim_mhit.py.

Usage:
  conda activate snap-geo
  python add_ma99.py \\
    --input  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \\
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc
"""
import argparse

import xarray as xr

MA_MONTHLY = [f"ma{i}" for i in range(12, 24)]


def parse_args():
    p = argparse.ArgumentParser(description="Add ma99 (mean of ma12-ma23) to mhit_indices.nc")
    p.add_argument("--input", required=True, help="Input mhit_indices.nc path")
    p.add_argument("--output", required=True, help="Output path (can overwrite input)")
    return p.parse_args()


def main():
    args = parse_args()
    print(f"Opening {args.input} ...")
    ds = xr.open_dataset(args.input)
    print(f"  Dimensions: {dict(ds.dims)}")

    print(f"Computing ma99 = mean({', '.join(MA_MONTHLY)}) ...")
    ma99 = xr.concat([ds[v] for v in MA_MONTHLY], dim="month").mean(dim="month")
    ma99.attrs = {
        "description": "Mean annual flow: average of monthly mean flows (ma12-ma23).",
        "units": "cfs",
    }
    ds = ds.assign(ma99=ma99)

    encoding = {
        v: {"zlib": True, "complevel": 4, "dtype": "float32"}
        for v in ds.data_vars
    }

    print(f"Writing {args.output} ...")
    ds.to_netcdf(args.output, encoding=encoding)
    print("Done.")
    print(f"  Variables now: {list(ds.data_vars)}")


if __name__ == "__main__":
    main()
