# MHIT Hydrological Statistics Pipeline — Plan & Progress

---

## Phase 1: Compute MHIT statistics — COMPLETE

`mhit_indices.nc` produced successfully at `/beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc`

- Dimensions: `era=2, model=7, stream_id=34346`
- Variables: 52 float32 hydrological statistics
- Coverage: 78.6% valid — expected, because `historical` only covers era `1990-2021` and `PGWh`/`PGWm` only cover era `2034-2065`; all (model, era) combinations that have input data produced output

---

## Phase 2: Add source dimension — TOMORROW

### Goal

Transform `mhit_indices.nc` from `(era, model, stream_id)` to `(source, era, model, stream_id)` by adding a `source` dimension with three values, mirroring the pattern established in `processing/calculate_stats.py`.

### Source dimension values

| source | Description |
|--------|-------------|
| `original_gcm` | The 52 MHIT stats as-is from Phase 1 |
| `gcm_diff` | Change signal between C2LE models' future and historical eras |
| `gcm_diff_applied_to_cheng` | `gcm_diff` applied to the `historical` model 1990-2021 baseline |

### Models excluded from gcm_diff

`['historical', 'PGWh', 'PGWm']` — same as `calculate_stats.py`.
- `historical` has no future era to diff against
- `PGWh`/`PGWm` are single-era projections with no paired historical run

C2LE2, C2LE4, C2LE7, C2LE9 get `gcm_diff` and `gcm_diff_applied_to_cheng`.

### gcm_diff computation

For each variable `da` (shape `era, model, stream_id`):
```python
past   = da.sel(era='1990-2021')   # shape: (model, stream_id)
future = da.sel(era='2034-2065')   # shape: (model, stream_id)
```

`gcm_diff` is computed **per variable** using the `difference_method` field in `luts_mhit.py` (38 ratio stats, 14 absolute stats):

**Ratio stats** (magnitudes, durations in cfs, rate-of-change):
```python
safe_past = past.where(past != 0, other=0.01)   # guard zero division
gcm_diff = (future / safe_past).where(~past["model"].isin(excluded_models))
```

**Absolute stats** (timing in julian days, frequency in events/yr, lf1/sum_mag):
```python
gcm_diff = (future - past).where(~past["model"].isin(excluded_models))
```

In the output:
- `source=gcm_diff, era=1990-2021` → all NaN (no past-era change signal)
- `source=gcm_diff, era=2034-2065` → NaN for excluded models, ratio/diff for C2LE models

### gcm_diff_applied_to_cheng computation

```python
hist_baseline = da.sel(era='1990-2021', model='historical')  # shape: (stream_id,)
```

**Ratio stats:**
```python
future_applied = gcm_diff * hist_baseline   # NaN for excluded models via gcm_diff; C2LE 2034-2065 only
```

**Absolute stats:**
```python
future_applied = gcm_diff + hist_baseline
```

For both methods, the 1990-2021 slot is NaN for all models except `historical`, which gets `hist_baseline`:
```python
is_hist      = past["model"] == "historical"
past_applied = xr.full_like(past, fill_value=np.nan).where(~is_hist, hist_baseline)
```

Then concatenate back into era dimension and concat all three sources:
```python
source_index   = pd.Index(['original_gcm', 'gcm_diff', 'gcm_diff_applied_to_cheng'], name='source')
gcm_diff_da    = xr.concat([xr.full_like(past, np.nan), gcm_diff],
                            dim=pd.Index(['1990-2021', '2034-2065'], name='era'))
applied_da     = xr.concat([past_applied, future_applied],
                            dim=pd.Index(['1990-2021', '2034-2065'], name='era'))
combined       = xr.concat([da, gcm_diff_da, applied_da], dim=source_index)
```

Result layout (same for both methods):

| model / era | 1990-2021 | 2034-2065 |
|-------------|-----------|-----------|
| `historical` | `hist_baseline` (observed) | NaN |
| `C2LE*` | NaN | adjusted future projection |
| `PGWh`, `PGWm` | NaN | NaN |

### Absolute stats in luts_mhit.py (14 total)

`sum_mag`, `lf1`, `fh1`, `fh5`, `fh6`, `fh7`, `fl1`, `fl3`, `spr_freq`, `sum_freq`, `th1`, `tl1`, `spr_ord`, `sum_ord`

### File to create

**`processing/matlab/add_source_dim_mhit.py`**

Standalone Python script — no SLURM needed (96 MB input, pure xarray math, runs in minutes).

Must be run from `processing/matlab/` (or add that dir to `sys.path`) so that `from luts_mhit import MHIT_STATS` resolves. Uses `snap-geo` conda env.

```
Usage:
  cd /import/home/jdpaul3/arctic_rivers/processing/matlab
  conda activate snap-geo
  python add_source_dim_mhit.py \
    --input  /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \
    --output /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_sourced.nc
```

Script structure (mirrors `calculate_stats.py`):
1. Open `mhit_indices.nc`
2. For each of the 52 variables, compute `gcm_diff` and `gcm_diff_applied_to_cheng` slices using the per-variable `difference_method` from `luts_mhit.py`
3. `xr.concat([original, gcm_diff_da, gcm_diff_applied_da], dim=source_index)` to build each variable
4. Assemble into an `xr.Dataset` with encoding/compression
5. Write to output path

Output structure:
```
dimensions: source=3, era=2, model=7, stream_id=34346
coordinates:
  source: ['original_gcm', 'gcm_diff', 'gcm_diff_applied_to_cheng']
  era:    ['1990-2021', '2034-2065']
  model:  ['C2LE2', 'C2LE4', 'C2LE7', 'C2LE9', 'PGWh', 'PGWm', 'historical']
  stream_id: int64[34346]
variables: 52 float32 statistics, dims (source, era, model, stream_id)
```

### Verification after running

Check these after the script completes:

1. Dimensions and coordinate values correct
2. `source=original_gcm` values match original `mhit_indices.nc` exactly
3. `gcm_diff` is NaN for historical/PGWh/PGWm across both eras
4. `gcm_diff` era=1990-2021 is all NaN for C2LE models too
5. `gcm_diff` era=2034-2065 has valid values for all 4 C2LE models
6. `gcm_diff_applied_to_cheng` era=1990-2021 is only non-NaN for `model=historical`
7. `gcm_diff_applied_to_cheng` era=2034-2065 is only non-NaN for C2LE models
8. Sanity check a ratio stat (e.g., `ma16`): `gcm_diff_applied[C2LE2, 2034-2065] ≈ original[C2LE2, 2034-2065] / original[C2LE2, 1990-2021] × original[historical, 1990-2021]`
9. Sanity check an absolute stat (e.g., `th1`): `gcm_diff[C2LE2, 2034-2065] = original[C2LE2, 2034-2065] − original[C2LE2, 1990-2021]`

### Checklist

- [ ] Write `add_source_dim_mhit.py`
- [ ] Run script, write `mhit_indices_sourced.nc`
- [ ] Verify structure and spot-check values
- [ ] Decide on final output filename (overwrite `mhit_indices.nc` or keep `_sourced` suffix)

---

## Phase 1 Reference

### Input
- **File:** `/beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc`
- **Variable:** `IRFroutedRunoff(model, time, stream_id)` — float, NaN fill, units: cfs
- **Models:** historical, PGWh, PGWm, C2LE2, C2LE4, C2LE7, C2LE9
- **Era split:** `< 2022-01-01` → `1990-2021`; `≥ 2022-01-01` → `2034-2065`

### Files (all in `processing/matlab/`)
| File | Description |
|------|-------------|
| `luts_mhit.py` | Metadata for all 52 statistics (units, category, difference_method) |
| `prep_drainage_area.py` | One-time: extract drainage area from AK_Rivers.gpkg → CSV |
| `mhit_chunk.py` | Python worker: `extract` (NetCDF → CSVs) and `pack` (results.csv → partial NetCDF) |
| `mhit_runner.m` | MATLAB orchestrator: reads env vars, runs MHIT + custom_stats via parfor |
| `custom_stats.m` | MATLAB: 12 custom seasonal statistics |
| `generate_mhit_jobs.py` | Generates SLURM job array + merge job scripts |
| `merge_mhit_chunks.py` | Concatenates partial NetCDFs → final output |
| `README.md` | Full setup and run instructions |

### Key bugs fixed during Phase 1
- MATLAB `readtable` auto-detects `_` as delimiter for `drainageArea.csv` → added `'Delimiter', ','`
- `custom_stats.m` crashed on empty spring/summer seasons at era boundaries → added `isempty` guards
- `ra8` units `"days"` triggered xarray CF time-decoding → changed to `"days_per_year"`
- MATLAB `readtable` renames mixed-case CSV headers → switched to column-position access `{:,1}`, `{:,2}`
- Water year clipping (partial boundary years cause MHIT `cellfun` errors) → clip to complete water years
- Scattered NaN discharge days crash `mhit_get_colwellMat` → drop NaN rows before passing to MHIT

---

## Resuming a Session

Point a new Claude session at this file:
> "Continue the MHIT pipeline work described in `/import/home/jdpaul3/arctic_rivers/processing/matlab/PLAN.md`. We are on Phase 2."

Key references for Phase 2:
1. This file
2. `/import/home/jdpaul3/arctic_rivers/processing/matlab/luts_mhit.py` — `difference_method` per stat
3. Reference implementation of `add_source_dimension()` — fetch with WebFetch:
   `https://raw.githubusercontent.com/ua-snap/arctic_rivers/add_diff/processing/calculate_stats.py`
4. `/beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc` — Phase 1 output (input to Phase 2)
