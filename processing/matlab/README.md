# MHIT Hydrological Statistics Pipeline

Computes 52 hydrological statistics for all 34,346 stream segments across 7 climate models and 2 eras using the [MHIT](https://github.com/mabouali/MHIT) MATLAB library plus custom seasonal statistics. Jobs are distributed across SLURM so that stream segments are processed in parallel chunks.

See this paper for more details about MHIT: https://www.sciencedirect.com/science/article/pii/S1574954116300115?via%3Dihub#bb0110

See page 47 of this document for definitions of the hydrologic indices: https://pubs.usgs.gov/of/2006/1093/report.pdf

> **Paths in examples below use `jdpaul3` as a placeholder.** Replace all paths with your own account and data directories. No user-specific paths are hardcoded in the scripts themselves — all paths are passed as arguments.

---

## Output

A NetCDF file at a path of your choosing (passed as `--output-nc` to `generate_mhit_jobs.py`), then post-processed by steps 7 and 8 below.

Final output dimensions: `source=3`, `era=2`, `model=7`, `stream_id=34346`  
Variables: 53 float32 statistics (40 MHIT-based + 12 custom seasonal + `ma99`; see `luts_mhit.py` for names, units, descriptions)

---

## One-time setup

### 1. Add MATLAB to your shell environment

```bash
echo "module load MATLAB/R2023b" >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
matlab -batch "disp('MATLAB OK')"
```

### 2. Clone the MHIT repo

Choose any location. Pass this path as `--mhit-dir` in step 4.

```bash
# Example — replace with your preferred location
git clone https://github.com/mabouali/MHIT /beegfs/CMIP6/jdpaul3/MHIT
```

### 3. Generate the drainage area lookup CSV

Uses the `snap-geo` conda environment.

```bash
conda activate snap-geo

# Example paths — replace <your-output-dir> with your own
python /import/home/jdpaul3/arctic_rivers/processing/matlab/prep_drainage_area.py \
    --gpkg  /beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/AK_Rivers.gpkg \
    --q-nc  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --out   /beegfs/CMIP6/<username>/arctic_rivers_data/drainage_area_lookup.csv
```

Arguments:

| Argument | Required | Description |
|----------|----------|-------------|
| `--q-nc` | yes | Path to `combined_q.nc` (provides the master stream_id list) |
| `--out`  | yes | Where to write `drainage_area_lookup.csv` |
| `--gpkg` | no | Path to `AK_Rivers.gpkg`; defaults to the shared copy at `/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/AK_Rivers.gpkg` |

This reads the `uparea` column (km²) from `AK_Rivers.gpkg`, converts to mi², and writes a two-column CSV (`comid`, `uparea_mi2`) covering all stream IDs. Run only once; the output is read by every chunk job.

---

## Running the pipeline

### 4. Generate SLURM scripts

```bash
conda activate snap-geo

# Example paths — replace jdpaul3 with your username throughout
python /import/home/jdpaul3/arctic_rivers/processing/matlab/generate_mhit_jobs.py \
    --scripts-dir  /import/home/jdpaul3/arctic_rivers/processing/matlab \
    --q-nc         /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --drain-csv    /beegfs/CMIP6/jdpaul3/arctic_rivers_data/drainage_area_lookup.csv \
    --staging-dir  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_partial \
    --output-nc    /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \
    --slurm-dir    /import/home/jdpaul3/arctic_rivers/processing/matlab/slurm \
    --mhit-dir     /beegfs/CMIP6/jdpaul3/MHIT
```

All path arguments are required. This writes two scripts into your `--slurm-dir`:

| Script | Purpose |
|--------|---------|
| `slurm/mhit_chunks.slurm` | SLURM job array — one task per 500-stream chunk (~69 tasks) |
| `slurm/mhit_merge.slurm`  | Single merge job — concatenates partial NetCDFs into final output |

The `slurm/` directory is excluded from git tracking (see `.gitignore`).

Optional tuning arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--chunk-size` | 500 | Streams per SLURM task |
| `--cpus` | 4 | CPUs per task (used by MATLAB `parfor`) |
| `--memory` | 16G / 64GB | Memory per task (merge task needs more memory) |
| `--time` | 4:00:00 | Walltime per task |
| `--partition` | t2small | SLURM partition |
| `--max-concurrent` | 20 | Max simultaneously running array tasks |
| `--conda-env` | snap-geo | Conda environment for Python steps |
| `--cleanup` | off | Delete `partial_*.nc` files from staging dir after a successful merge |

### 5. Test with a single task before submitting all

```bash
sbatch --array=0-0 slurm/mhit_chunks.slurm
```

Check the log in `slurm/mhit_chunks-<JOBID>_0.out` and verify:
- CSVs were extracted successfully
- MATLAB ran without errors and produced `results.csv`
- The partial NetCDF was written to the staging directory

### 6. Submit the full run

```bash
ARRAY_JOB_ID=$(sbatch --parsable slurm/mhit_chunks.slurm)
sbatch --dependency=afterok:$ARRAY_JOB_ID slurm/mhit_merge.slurm
```

If submitted like above, the merge job will not start until all chunk tasks complete successfully. If any task fails, the merge job will not run; fix and resubmit failed tasks (they will skip already-completed chunks).

### 7. Add ma99 (mean annual flow)

Computes `ma99` — the average of monthly mean flows `ma12`–`ma23` — and appends it to the output as a 53rd variable. Can be run on a **login node** (file is ~96 MB, pure xarray math).

```bash
conda activate snap-geo
python /import/home/jdpaul3/arctic_rivers/processing/matlab/add_ma99.py \
    --input  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_ma99.nc
```

### 8. Add source dimension

Transforms the dataset from `(era, model, stream_id)` to `(source, era, model, stream_id)` by computing change signals for the C2LE ensemble models. Can be run on a **login node**.

The three source values are:

| source | Description |
|--------|-------------|
| `original_gcm` | The 53 statistics as-is from steps 6–7 |
| `gcm_diff` | Change signal between C2LE models' future and historical eras (ratio for flow/duration/rate stats; absolute difference for timing/frequency stats) |
| `gcm_diff_applied_to_blaskey` | `gcm_diff` applied to the `historical` model 1990–2021 baseline (Blaskey)|

`historical`, `PGWh`, and `PGWm` are excluded from `gcm_diff` and `gcm_diff_applied_to_blaskey` (no paired future/historical run).

```bash
conda activate snap-geo
python /import/home/jdpaul3/arctic_rivers/processing/matlab/add_source_dim_mhit.py \
    --input  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_ma99.nc \
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_combined.nc
```

### 9. Prepare for Rasdaman ingestion

Converts string dimensions (`model`, `era`, `source`) to integer indices and stores the string-to-integer mappings in each coordinate's `encoding` attribute, as required by Rasdaman.

Generate and submit the SLURM job:

```bash
python /import/home/jdpaul3/arctic_rivers/processing/matlab/generate_rasdaman_job.py \
    --scripts-dir /import/home/jdpaul3/arctic_rivers/processing \
    --input       /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_combined.nc \
    --output      /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_combined_for_rasdaman.nc \
    --slurm-dir   /import/home/jdpaul3/arctic_rivers/processing/matlab/slurm

sbatch slurm/rasdaman_prep.slurm
```

Optional arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--memory` | 16G | Memory for the SLURM job |
| `--time` | 1:00:00 | Walltime |
| `--partition` | t2small | SLURM partition |
| `--conda-env` | snap-geo | Conda environment |

---

## Per-chunk job internals

Each SLURM task does the following for its stream index range `[start:end]`:

1. **Extract** (`mhit_chunk.py extract`) — reads the stream slice from `combined_q.nc`, splits by era (`< 2022-01-01` → `1990-2021`; `≥ 2022-01-01` → `2034-2065`), and writes one CSV per `(comid, model, era)` combination to a temp directory. Also writes `drainageArea.csv` for MATLAB. Total ~7,000 CSVs per task.

2. **MATLAB** (`mhit_runner.m`) — loads MHIT MFiles, starts a `parfor` pool, and processes all CSVs:
   - Calls `mhit_getAllIndices` for the 40 MHIT-based statistics
   - Calls `custom_stats` for the 12 custom seasonal statistics
   - Writes `results.csv` to the output directory

3. **Pack** (`mhit_chunk.py pack`) — reads `results.csv`, reshapes into `(era, model, stream_id)` arrays, and writes a partial NetCDF.

4. **Cleanup** — removes the temp directory.

---

## Files

| File | Description |
|------|-------------|
| `luts_mhit.py` | Metadata (units, description, category) for all 53 statistics |
| `prep_drainage_area.py` | One-time: extract drainage area from `AK_Rivers.gpkg` → CSV |
| `mhit_chunk.py` | Python worker: `extract` and `pack` modes |
| `mhit_runner.m` | MATLAB orchestrator: reads env vars, runs MHIT + custom stats |
| `custom_stats.m` | MATLAB function: 12 custom seasonal statistics |
| `generate_mhit_jobs.py` | Generates `slurm/mhit_chunks.slurm` and `slurm/mhit_merge.slurm` |
| `merge_mhit_chunks.py` | Merges partial NetCDFs into final output |
| `add_ma99.py` | Post-processing step 7: adds `ma99` (mean of `ma12`–`ma23`) |
| `add_source_dim_mhit.py` | Post-processing step 8: adds `source` dimension with change signals |
| `generate_rasdaman_job.py` | Post-processing step 9: generates SLURM script for Rasdaman prep |
| `.gitignore` | Excludes `slurm/` from version control |

---

## Conda environment

All Python steps use the **`snap-geo`** conda environment:

```bash
conda activate snap-geo
```

Key packages: `xarray 2024.11.0`, `pandas 2.2.2`, `numpy 1.26.4`, `geopandas 0.14.4`, `fiona 1.9.4`

> **Note:** The `snap-geo` environment's Python binary is `python`, not `python3`. Scripts use `#!/usr/bin/env python` and the SLURM jobs call `python` explicitly.

---

## Restarting after interruption

If the pipeline is interrupted partway through:

- Already-completed partial NetCDFs are preserved in `--staging-dir`. The chunk job skips any task whose `partial_<start>_<end>.nc` already exists, so it is safe to resubmit the full array.
- Re-run step 4 (`generate_mhit_jobs.py`) to regenerate the SLURM scripts if needed (they are not modified by running jobs), then resubmit.

---

## A note about custom stats

Not all statistics from the CONUS Hydroviz project (see here: https://github.com/ua-snap/hydroviz/blob/main/data/streamflow_statistics_description_table.csv) are available via MHIT. For these statistics, we use base MATLAB to compute formulas based on the descriptions of the statistics. See the inline documentation in `custom_stats.m` to better understand the processing steps.