#!/usr/bin/env python
"""
Merge partial NetCDF chunks from MHIT pipeline into a single output file.

Usage:
  python merge_mhit_chunks.py \
    --partial-dir /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_partial \
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \
    --q-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc
"""
import argparse
from pathlib import Path

import numpy as np
import xarray as xr


def main():
    p = argparse.ArgumentParser(description="Merge MHIT partial NetCDFs")
    p.add_argument("--partial-dir", required=True, help="Directory of partial_*.nc files")
    p.add_argument("--output",      required=True, help="Output NetCDF path")
    p.add_argument("--q-nc",        required=True, help="combined_q.nc (used for expected stream_ids)")
    p.add_argument("--cleanup",     action="store_true",
                   help="Delete partial_*.nc files after a successful merge")
    args = p.parse_args()

    partial_dir = Path(args.partial_dir)
    partials = sorted(partial_dir.glob("partial_*.nc"))
    if not partials:
        raise FileNotFoundError(f"No partial_*.nc files found in {partial_dir}")
    print(f"Found {len(partials)} partial files")

    # Load expected stream_id order from combined_q.nc
    ds_ref = xr.open_dataset(args.q_nc, decode_times=False)
    expected_stream_ids = ds_ref["stream_id"].values
    ds_ref.close()

    # Open all partials and concat along stream_id
    print("Opening partial datasets...")
    datasets = [xr.open_dataset(p) for p in partials]
    combined = xr.concat(datasets, dim="stream_id")

    # Reindex to canonical stream_id order (handles any missing chunks as NaN)
    print("Reindexing to canonical stream_id order...")
    combined = combined.reindex(stream_id=expected_stream_ids)

    # Sort by stream_id (should already be sorted but ensure consistency)
    combined = combined.sortby("stream_id")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Writing {out_path}...")
    combined.to_netcdf(out_path)
    print("Done.")

    for d in datasets:
        d.close()

    if args.cleanup:
        print("Cleaning up partial files...")
        for p in partials:
            p.unlink()
        print(f"Deleted {len(partials)} partial files from {partial_dir}")


if __name__ == "__main__":
    main()
