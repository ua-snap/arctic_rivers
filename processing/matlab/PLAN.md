# MHIT SLURM Pipeline — Plan & Progress

**Goal:** Run MHIT + custom MATLAB functions on `combined_q.nc` to produce a NetCDF of 47 hydrological statistics for all 34,346 stream segments, 7 models, and 2 eras.

**Status:** Implementation in progress

---

## Context

### Input
- **File:** `/beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc`
- **Variable:** `IRFroutedRunoff(model, time, stream_id)` — float, NaN fill, **units: cfs (already)**
- **Dimensions:** model=7, time=23216 (days since 1990-01-01, proleptic_gregorian), stream_id=34346
- **Models:** historical, PGWh, PGWm, C2LE2, C2LE4, C2LE7, C2LE9
- **Era split** (matching existing calculate_stats.py):
  - Era 1 `"1990-2021"`: time < 2022-01-01
  - Era 2 `"2034-2065"`: time ≥ 2022-01-01

### Reference Output
- **File:** `/beegfs/CMIP6/jdpaul3/arctic_rivers_data/stats_q_diff.nc`
- **Dimensions:** source=3, era=2, model=7, stream_id=34346
- **Our output** will use simpler `(era, model, stream_id)` — no source dimension

### Drainage Area
- **File:** `/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/AK_Rivers.gpkg` — layer `AK_Rivers`
- **Column:** `uparea` (float, km²), keyed on `COMID`
- `stream_id` in combined_q.nc == `COMID` in AK_Rivers.gpkg (verified: 81000004 is first in both)
- **Conversion:** km² × 0.386102 → mi² (MHIT and custom stats use mi² for normalization)
- Preprocessing step writes `drainage_area_lookup.csv` once (COMID, uparea_mi2)

### MHIT Tool
- **Repo:** https://github.com/mabouali/MHIT/tree/master
- **MATLAB:** R2023b at `/usr/local/pkg/manual/MATLAB/R2023b/bin/matlab`
- **Module:** `module load MATLAB/R2023b`
- **Core function:** `mhit_getAllIndices(discharge, year, month, day, drainageArea)`
- **Batch function:** `mhit_getAllInd_AllFiles(inputDIR, fileExtension)` → returns HydInd table
- **CSV input format:** `year,month,day,discharge` (header required, one file per stream×model×era)
- **drainageArea.csv format:** `fileName,drainageArea` (fileName without .csv extension)

---

## Statistics to Compute (47 total)

Source: https://github.com/ua-snap/hydroviz/blob/main/data/streamflow_statistics_description_table.csv

### MHIT-based (35 stats, code_base=mhit)
| Stat | Category | Description |
|------|----------|-------------|
| MA3 | magnitude | CV of annual daily flows (mean of annual CVs) |
| MA4 | magnitude | SD/mean of percentiles of log-transformed flow |
| MA12–MA23 | magnitude | Mean monthly flows (Jan–Dec) |
| MH14 | magnitude | Median of annual max / median annual flow |
| MH20 | magnitude | Mean annual max / drainage area (cfs/mi²) |
| ML17 | magnitude | Base flow: mean(annual 7-day min / annual mean) |
| DH1–DH5 | duration | Annual max N-day moving avg (N=1,3,7,30,90) |
| DH15 | duration | High flow pulse duration (>75th pct) |
| DL1–DL5 | duration | Annual min N-day moving avg (N=1,3,7,30,90) |
| DL16 | duration | Low flow pulse duration (<25th pct) |
| FH1 | frequency | High pulse count (>75th pct, mean/yr) |
| FH5 | frequency | Flood freq (>median, mean/yr) |
| FH6 | frequency | Flood freq (>3×median, mean/yr) |
| FH7 | frequency | Flood freq (>7×median, mean/yr) |
| FL1 | frequency | Low pulse count (<25th pct, mean/yr) |
| FL3 | frequency | Low pulse count (<5% mean, mean/yr) |
| RA1 | rate_of_change | Mean rise rate (cfs/day) |
| RA3 | rate_of_change | Mean fall rate (cfs/day) |
| RA8 | rate_of_change | Median annual reversals (days) |
| TH1 | timing | Julian date of annual max (median) |
| TL1 | timing | Julian date of annual min (median) |

### Custom MATLAB (12 stats, code_base=matlab)
| Stat | Category | Description |
|------|----------|-------------|
| LF1 | duration | Days/yr below 0.1 cfs/mi² × area threshold; median |
| SPR_DUR3 | duration | Spring (Apr–Jun) max 3-day moving avg; median |
| SPR_DUR7 | duration | Spring (Apr–Jun) max 7-day moving avg; median |
| SUM_DUR3 | duration | Summer (Jul–Sep) min 3-day moving avg; median |
| SUM_DUR7 | duration | Summer (Jul–Sep) min 7-day moving avg; median |
| SPR_FREQ | frequency | Apr–Jun events above 10th pct of full record; median |
| SUM_FREQ | frequency | Jul–Sep events below 90th pct of full record; median |
| SPR_MAG | magnitude | Median(annual spring max / drainage area) (cfs/mi²) |
| SUM_CV | magnitude | Median of annual summer CV (Jul–Sep) |
| SUM_MAG | magnitude | Median(annual summer min / drainage area) (cfs/mi²) |
| SPR_ORD | timing | Julian date of spring (Apr–Jun) max; median |
| SUM_ORD | timing | Julian date of summer (Jul–Sep) min; median |

---

## Architecture

### Pipeline Overview

```
[SETUP - run once]
  prep_drainage_area.py
    → reads AK_Rivers.gpkg, converts km² to mi²
    → writes drainage_area_lookup.csv (COMID, uparea_mi2)

[JOB GENERATION]
  generate_mhit_jobs.py
    → generates N SLURM scripts, one per stream_id chunk
    → or generates a SLURM job array

[PER-CHUNK JOBS - run in parallel]
  mhit_chunk_job.slurm  (for stream_ids [i : i+chunk_size])
    Step 1 (Python): mhit_chunk.py --mode extract
      → loads combined_q.nc slice for this chunk
      → splits by era (< or ≥ 2022-01-01)
      → writes CSVs: $TMPDIR/<comid>_<model>_<era>.csv
      → writes $TMPDIR/drainageArea.csv
    Step 2 (MATLAB): matlab -batch "mhit_runner('$TMPDIR', '$OUTDIR')"
      → addpath MHIT MFiles
      → mhit_getAllInd_AllFiles → HydInd table
      → custom_stats(discharge, dates, drainage_area) → CustomInd table
      → writetable(HydInd, '$OUTDIR/mhit_results.csv')
      → writetable(CustomInd, '$OUTDIR/custom_results.csv')
    Step 3 (Python): mhit_chunk.py --mode pack
      → reads mhit_results.csv + custom_results.csv
      → parses COMID/model/era from fileName
      → extracts the 47 target statistics
      → writes staging_dir/partial_mhit_<start>_<end>.nc
    Step 4: rm -rf $TMPDIR (cleanup CSVs)

[FINAL MERGE]
  merge_mhit_chunks.py
    → xr.open_mfdataset(staging_dir/partial_mhit_*.nc)
    → concat along stream_id
    → write final mhit_indices.nc
```

### Files to Create

```
arctic_rivers/processing/matlab/
├── PLAN.md                        ← this file
├── prep_drainage_area.py          ← one-time: extract drainage area to CSV
├── generate_mhit_jobs.py          ← generates SLURM scripts for all chunks
├── mhit_chunk.py                  ← Python worker: extract CSVs and pack NetCDF
├── mhit_runner.m                  ← MATLAB: calls MHIT + custom stats
├── custom_stats.m                 ← MATLAB: implements the 12 custom statistics
├── merge_mhit_chunks.py           ← merges partial NetCDFs into final output
└── luts_mhit.py                   ← stat names, descriptions, units metadata
```

### Chunking & SLURM Parameters
- **Chunk size:** 500 streams/job → ~69 jobs
- **CPUs per job:** 4 (for MATLAB parfor)
- **Memory per job:** 16 GB
- **Walltime:** 4 hours (conservative; MHIT is fast at ~12 min for many streams)
- **CSV volume per job:** 500 streams × 14 model×era combos × ~32 yrs × 365 days/yr × ~20 bytes/row ≈ 1.6 GB temporary (on $TMPDIR, deleted after packing)
- **Output per partial NC:** 47 vars × float32 × 2 eras × 7 models × 500 streams ≈ 13 MB

### Output NetCDF Structure
```
dimensions: era=2, model=7, stream_id=34346
coordinates: era (string), model (string), stream_id (int64)
data variables: 47 float32 variables (one per statistic)
    dims: (era, model, stream_id), fill_value=NaN
    attrs: description, units, category, difference_method
```

---

## Conda Environment

- Python scripts: base conda env (`/home/jdpaul3/miniconda3`)
  - Has: xarray 2025.9.1, numpy, pandas (verify fiona/geopandas availability)
- Drainage area prep: `hydroviz_shp` micromamba env (has fiona)
- MATLAB: `module load MATLAB/R2023b`

---

## Open Questions (Resolved)

| Question | Answer |
|----------|--------|
| Drainage area source | AK_Rivers.gpkg, `uparea` column (km²) → convert to mi² |
| IRFroutedRunoff units | Already cfs |
| Which indices | 47 from hydroviz table |
| Output dimensions | Simple (era, model, stream_id) |
| Source dimension | Not needed |

---

## Notes

- There are **52 statistics** total (not 47 as originally estimated): 17 duration, 8 frequency, 20 magnitude, 3 rate_of_change, 4 timing
- `snap-geo` conda env uses `python` binary (not `python3`) — all scripts use `#!/usr/bin/env python`
- MATLAB `-batch` mode: scripts read config via `getenv()` env vars set by the SLURM job
- CSV filename separator is `__` (double underscore): `<comid>__<model>__<era>.csv`
- `mhit_getAllIndices` returns struct fields `.MA`, `.ML`, `.MH`, `.FL`, `.FH`, `.DL`, `.DH`, `.TH`, `.TL`, `.RA` as 1D arrays; index i → statistic i (e.g., `MA(3)` = MA3)

## Progress Log

| Date | Status | Notes |
|------|--------|-------|
| 2026-05-12 | Planning complete | Architecture finalized |
| 2026-05-12 | Implementation complete | All 7 files written |

### Implementation Checklist
- [x] `luts_mhit.py` — 52-stat metadata dict
- [x] `prep_drainage_area.py` — one-time drainage area extraction
- [x] `mhit_chunk.py` — CSV extraction (extract mode) and NetCDF packing (pack mode)
- [x] `mhit_runner.m` — MATLAB orchestrator (parfor, MHIT + custom_stats)
- [x] `custom_stats.m` — 12 custom seasonal statistics
- [x] `generate_mhit_jobs.py` — generates mhit_chunks.slurm (job array) + mhit_merge.slurm
- [x] `merge_mhit_chunks.py` — concatenates partial NetCDFs → final output
- [ ] Clone MHIT repo: `git clone https://github.com/mabouali/MHIT /beegfs/CMIP6/jdpaul3/MHIT`
- [ ] Run `prep_drainage_area.py` once
- [ ] Test on small sample (10 streams, 1 model, 1 era)
- [ ] Generate jobs: `python generate_mhit_jobs.py ...`
- [ ] Full run

---

## Resuming a Session

If this session is interrupted, point a new Claude session at this file and say:
> "Continue the MHIT pipeline implementation described in `/import/home/jdpaul3/arctic_rivers/processing/matlab/PLAN.md`"

Key context to re-read:
1. This file (PLAN.md) — architecture, file list, progress checklist
2. `/import/home/jdpaul3/arctic_rivers/processing/generate_stats_job.py` — SLURM job generator style
3. `/import/home/jdpaul3/arctic_rivers/processing/calculate_stats.py` — era split logic, xarray patterns
4. `/import/home/jdpaul3/arctic_rivers/processing/luts.py` — metadata patterns
5. `ncdump -h /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc` — input NetCDF dims
6. MHIT README at https://github.com/mabouali/MHIT/tree/master — CSV format, mhit_getAllIndices signature
7. Stats table at https://github.com/ua-snap/hydroviz/blob/main/data/streamflow_statistics_description_table.csv
