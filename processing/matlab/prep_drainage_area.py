#!/usr/bin/env python
"""
One-time preprocessing: extract drainage area per COMID from AK_Rivers.gpkg
and write a simple CSV lookup used by each SLURM chunk job.

Usage:
  python prep_drainage_area.py \
    --gpkg /beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/AK_Rivers.gpkg \
    --q-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --out /beegfs/CMIP6/jdpaul3/arctic_rivers_data/drainage_area_lookup.csv
"""
import argparse
import geopandas as gpd
import pandas as pd
import xarray as xr
import numpy as np


KM2_TO_MI2 = 0.386102


def main():
    p = argparse.ArgumentParser(description="Extract drainage area lookup CSV from AK_Rivers.gpkg")
    p.add_argument("--gpkg", default="/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/AK_Rivers.gpkg",
                   help="Path to AK_Rivers.gpkg (shared dataset, default is the canonical location)")
    p.add_argument("--q-nc", required=True,
                   help="Path to combined_q.nc (used to get the canonical stream_id list)")
    p.add_argument("--out", required=True,
                   help="Output CSV path for drainage_area_lookup.csv")
    args = p.parse_args()

    print("Reading stream_ids from NetCDF...")
    ds = xr.open_dataset(args.q_nc)
    stream_ids = ds["stream_id"].values.astype(np.int64)
    ds.close()
    print(f"  {len(stream_ids)} stream_ids")

    print("Reading AK_Rivers.gpkg...")
    gdf = gpd.read_file(args.gpkg, layer="AK_Rivers")
    gdf = gdf[["COMID", "uparea"]].rename(columns={"COMID": "comid", "uparea": "uparea_km2"})
    gdf["comid"] = gdf["comid"].astype(np.int64)
    gdf["uparea_mi2"] = gdf["uparea_km2"] * KM2_TO_MI2
    print(f"  {len(gdf)} entries in AK_Rivers.gpkg")

    nc_df = pd.DataFrame({"comid": stream_ids})
    merged = nc_df.merge(gdf[["comid", "uparea_mi2"]], on="comid", how="left")

    n_missing = merged["uparea_mi2"].isna().sum()
    if n_missing > 0:
        print(f"  WARNING: {n_missing} stream_ids have no drainage area in AK_Rivers.gpkg (will be NaN)")

    merged.to_csv(args.out, index=False)
    print(f"Wrote {len(merged)} rows to {args.out}")
    print(f"  Valid drainage areas: {merged['uparea_mi2'].notna().sum()}")


if __name__ == "__main__":
    main()
