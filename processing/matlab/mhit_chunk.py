#!/usr/bin/env python
"""
Per-chunk worker for the MHIT SLURM pipeline.

Two modes:
  extract  -- reads a slice of combined_q.nc and writes per-stream CSVs for MATLAB
  pack     -- reads MATLAB results.csv and writes a partial NetCDF

Usage (extract):
  python mhit_chunk.py extract \
    --start-idx 0 --end-idx 500 \
    --q-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --drain-csv /beegfs/CMIP6/jdpaul3/arctic_rivers_data/drainage_area_lookup.csv \
    --out-dir /tmp/mhit_csvs_0_500

Usage (pack):
  python mhit_chunk.py pack \
    --start-idx 0 --end-idx 500 \
    --results-csv /tmp/mhit_out_0_500/results.csv \
    --q-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --partial-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_partial/partial_0_500.nc
"""
import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from luts_mhit import MHIT_STATS, STAT_NAMES

ERA_CUTOFF = np.datetime64("2022-01-01")
ERA_LABELS = ["1990-2021", "2034-2065"]
SEP = "__"   # separator between comid, model, era in filenames


def get_era(time_values):
    """Return boolean mask: True = era 0 (1990-2021), False = era 1 (2034-2065)."""
    return time_values < ERA_CUTOFF


def extract(args):
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading q-nc slice [{args.start_idx}:{args.end_idx}]...")
    ds = xr.open_dataset(args.q_nc, decode_times=True)
    stream_ids = ds["stream_id"].values
    models = ds["model"].values.tolist()

    chunk_stream_ids = stream_ids[args.start_idx:args.end_idx]
    chunk_ds = ds.isel(stream_id=slice(args.start_idx, args.end_idx))
    # Load into memory once: shape (n_model, n_time, n_stream)
    q_all = chunk_ds["IRFroutedRunoff"].values  # float32 array
    time_vals = chunk_ds["time"].values  # numpy datetime64

    ds.close()

    print(f"  {len(chunk_stream_ids)} streams, {len(models)} models, {len(time_vals)} time steps")

    # Split time into eras
    era0_mask = time_vals < ERA_CUTOFF
    era1_mask = ~era0_mask
    era_masks = [era0_mask, era1_mask]

    # Build date arrays once per era
    era_dates = []
    for mask in era_masks:
        t = pd.DatetimeIndex(time_vals[mask])
        era_dates.append({"year": t.year.values, "month": t.month.values, "day": t.day.values})

    # Read drainage area lookup
    print("Loading drainage area lookup...")
    drain_df = pd.read_csv(args.drain_csv)
    drain_df["comid"] = drain_df["comid"].astype(np.int64)
    drain_lookup = dict(zip(drain_df["comid"], drain_df["uparea_mi2"]))

    # Write per-stream CSVs and drainageArea.csv
    da_rows = []
    n_written = 0

    for s_idx, comid in enumerate(chunk_stream_ids):
        da_mi2 = drain_lookup.get(int(comid), float("nan"))
        for m_idx, model in enumerate(models):
            for e_idx, era_label in enumerate(ERA_LABELS):
                mask = era_masks[e_idx]
                q_series = q_all[m_idx, mask, s_idx]

                # Skip if entirely NaN
                if np.all(np.isnan(q_series)):
                    continue

                dates = era_dates[e_idx]
                df = pd.DataFrame({
                    "year":      dates["year"],
                    "month":     dates["month"],
                    "day":       dates["day"],
                    "discharge": q_series,
                })
                # Write the extracted series as-is; this code does not explicitly
                # convert NaN discharge values before exporting the CSV.
                basename = f"{comid}{SEP}{model}{SEP}{era_label}"
                csv_path = out_dir / f"{basename}.csv"
                df.to_csv(csv_path, index=False)
                da_rows.append({"fileName": basename, "drainageArea": da_mi2})
                n_written += 1

    # Write drainageArea.csv for MATLAB
    da_df = pd.DataFrame(da_rows)
    da_df.to_csv(out_dir / "drainageArea.csv", index=False)

    print(f"Wrote {n_written} discharge CSVs + drainageArea.csv to {out_dir}")


def pack(args):
    print(f"Packing results for chunk [{args.start_idx}:{args.end_idx}]...")

    results_df = pd.read_csv(args.results_csv)

    # Parse comid, model, era from fileName column
    parsed = results_df["fileName"].str.split(SEP, expand=True)
    results_df["comid"] = parsed[0].astype(np.int64)
    results_df["model"] = parsed[1]
    results_df["era"] = parsed[2]

    # Get canonical coords from q-nc
    ds = xr.open_dataset(args.q_nc, decode_times=False)
    all_stream_ids = ds["stream_id"].values
    models = ds["model"].values.tolist()
    ds.close()

    chunk_stream_ids = all_stream_ids[args.start_idx:args.end_idx]
    n_stream = len(chunk_stream_ids)
    n_model = len(models)
    n_era = len(ERA_LABELS)
    n_stat = len(STAT_NAMES)

    # Build result array: (era, model, stream_id, stat)
    data = np.full((n_era, n_model, n_stream, n_stat), np.nan, dtype=np.float32)

    comid_to_chunk_idx = {int(c): i for i, c in enumerate(chunk_stream_ids)}
    model_to_idx = {m: i for i, m in enumerate(models)}
    era_to_idx = {e: i for i, e in enumerate(ERA_LABELS)}

    for _, row in results_df.iterrows():
        comid = int(row["comid"])
        model = row["model"]
        era = row["era"]
        s_i = comid_to_chunk_idx.get(comid)
        m_i = model_to_idx.get(model)
        e_i = era_to_idx.get(era)
        if s_i is None or m_i is None or e_i is None:
            continue
        for st_i, stat in enumerate(STAT_NAMES):
            if stat in row:
                val = row[stat]
                data[e_i, m_i, s_i, st_i] = float(val) if pd.notna(val) else np.nan

    # Build xarray Dataset
    out_ds = xr.Dataset(
        coords={
            "era":       (["era"],       ERA_LABELS),
            "model":     (["model"],     models),
            "stream_id": (["stream_id"], chunk_stream_ids),
        }
    )
    for st_i, stat in enumerate(STAT_NAMES):
        meta = MHIT_STATS[stat]
        out_ds[stat] = xr.DataArray(
            data[:, :, :, st_i].astype(np.float32),
            dims=["era", "model", "stream_id"],
            attrs={
                "units":             meta["units"],
                "description":       meta["description"],
                "category":          meta["category"],
                "code_base":         meta["code_base"],
                "difference_method": meta["difference_method"],
            }
        )

    out_path = Path(args.partial_nc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_ds.to_netcdf(out_path)
    print(f"Wrote {out_path}  (era={n_era}, model={n_model}, stream_id={n_stream})")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="mode", required=True)

    e = sub.add_parser("extract", help="NetCDF slice → per-stream CSVs")
    e.add_argument("--start-idx", type=int, required=True)
    e.add_argument("--end-idx",   type=int, required=True)
    e.add_argument("--q-nc",      required=True)
    e.add_argument("--drain-csv", required=True)
    e.add_argument("--out-dir",   required=True)

    pk = sub.add_parser("pack", help="MATLAB results.csv → partial NetCDF")
    pk.add_argument("--start-idx",   type=int, required=True)
    pk.add_argument("--end-idx",     type=int, required=True)
    pk.add_argument("--results-csv", required=True)
    pk.add_argument("--q-nc",        required=True)
    pk.add_argument("--partial-nc",  required=True)

    args = p.parse_args()
    if args.mode == "extract":
        extract(args)
    else:
        pack(args)


if __name__ == "__main__":
    main()
