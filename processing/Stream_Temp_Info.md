# Alaskan River Stream Temperature Statistics

Rasdaman coverage: `ak_hydro_segments_wt_stats`

## Source Dataset

**[Alaskan river discharge, temperature, and climate data for a climate reference (1990-2021) and at mid-century (2034-2065)](https://doi.org/10.18739/A25M62870)**
*Dylan Blaskey, Keith Musselman, Andrew Newman, and Yifan Cheng — Arctic Data Center, 2024*

This dataset was produced using the Regional Arctic System Model (RASM), combining the Weather Research & Forecasting Model (WRF) and Community Terrestrial Systems Model (CTSM) for climate and land surface processes, mizuRoute for river routing, and the River Basin Model for river temperature. The framework generates high-resolution spatial and temporal data for 49 major Alaskan river basins, comparing historical (1990–2021) and mid-century (2035–2064) conditions across six future scenarios: two pseudo-global warming simulations (SSP2-4.5) and four directly downscaled global climate models (SSP3-7.0).

---

## Dimensions

| Dimension | Index | Values | Description |
|-----------|-------|--------|-------------|
| `model` | 0 | `C2LE2` | Downscaled CESM2-LE ensemble member 2, SSP3-7.0 |
| `model` | 1 | `C2LE4` | Downscaled CESM2-LE ensemble member 4, SSP3-7.0 |
| `model` | 2 | `C2LE7` | Downscaled CESM2-LE ensemble member 7, SSP3-7.0 |
| `model` | 3 | `C2LE9` | Downscaled CESM2-LE ensemble member 9, SSP3-7.0 |
| `model` | 4 | `PGWh` | Pseudo-global warming — high scenario (75th–100th percentile of SSP2-4.5 CMIP6 models) |
| `model` | 5 | `PGWm` | Pseudo-global warming — median scenario (25th–75th percentile of SSP2-4.5 CMIP6 models) |
| `model` | 6 | `historical` | ERA5 dynamically downscaled to 4km over Alaska and Yukon (1990–2021) |
| `source` | 0 | `original_gcm` | Output directly from the GCM |
| `source` | 1 | `gcm_diff` | Difference between GCM future and historical |
| `source` | 2 | `gcm_diff_applied_to_cheng` | GCM difference applied to the Cheng et al. historical baseline |
| `era` | 0 | `1990-2021` | Historical reference period |
| `era` | 1 | `2034-2065` | Mid-century future period |

### Model References

| Model | Modeling Center | Reference |
|-------|----------------|-----------|
| `historical` | NCAR | [Cheng et al. 2025, JGR: Atmospheres](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2024JD041185)  &  [Blaskey et al. 2024, WRR](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2023WR036217)|
| `PGWh` / `PGWm` | NCAR | [UCAR/NCAR GDEX, doi:10.5065/ZPSB-PS82](https://gdex.ucar.edu/datasets/d614000/) |
| `C2LE2`, `C2LE4`, `C2LE7`, `C2LE9` | NCAR | [Rodgers et al. 2021, Earth Syst. Dynam.](https://esd.copernicus.org/articles/12/1393/2021/) |

---

## Variables

| Variable | Units | Description |
|----------|-------|-------------|
| `wt_ann_max_temp_mean` | °C | Mean (over era years) of the annual maximum daily stream temperature |
| `wt_ann_max_temp_doy_mean` | day of year | Mean (over era years) Julian day of the annual maximum daily stream temperature |
| `wt_7d_max_temp_mean` | °C | Mean (over era years) of the annual maximum 7-day rolling average stream temperature |
| `wt_7d_max_temp_doy_mean` | day of year | Mean (over era years) Julian day of the center of the annual maximum 7-day rolling average |
| `wt_cdd_may_sept_mean` | °C·days | Mean (over era years) annual cumulative degree days above 0°C, May through September |
| `wt_days_gt13_mean` | days | Mean annual count of days with stream temperature > 13°C |
| `wt_days_gt18_mean` | days | Mean annual count of days with stream temperature > 18°C |
| `wt_days_gt20_mean` | days | Mean annual count of days with stream temperature > 20°C |
| `wt_mean_jan` | °C | Mean of monthly mean stream temperatures for January |
| `wt_mean_feb` | °C | Mean of monthly mean stream temperatures for February |
| `wt_mean_mar` | °C | Mean of monthly mean stream temperatures for March |
| `wt_mean_apr` | °C | Mean of monthly mean stream temperatures for April |
| `wt_mean_may` | °C | Mean of monthly mean stream temperatures for May |
| `wt_mean_jun` | °C | Mean of monthly mean stream temperatures for June |
| `wt_mean_jul` | °C | Mean of monthly mean stream temperatures for July |
| `wt_mean_aug` | °C | Mean of monthly mean stream temperatures for August |
| `wt_mean_sep` | °C | Mean of monthly mean stream temperatures for September |
| `wt_mean_oct` | °C | Mean of monthly mean stream temperatures for October |
| `wt_mean_nov` | °C | Mean of monthly mean stream temperatures for November |
| `wt_mean_dec` | °C | Mean of monthly mean stream temperatures for December |
| `wt_min_jan` | °C | Minimum monthly mean stream temperature for January across all years in era |
| `wt_min_feb` | °C | Minimum monthly mean stream temperature for February across all years in era |
| `wt_min_mar` | °C | Minimum monthly mean stream temperature for March across all years in era |
| `wt_min_apr` | °C | Minimum monthly mean stream temperature for April across all years in era |
| `wt_min_may` | °C | Minimum monthly mean stream temperature for May across all years in era |
| `wt_min_jun` | °C | Minimum monthly mean stream temperature for June across all years in era |
| `wt_min_jul` | °C | Minimum monthly mean stream temperature for July across all years in era |
| `wt_min_aug` | °C | Minimum monthly mean stream temperature for August across all years in era |
| `wt_min_sep` | °C | Minimum monthly mean stream temperature for September across all years in era |
| `wt_min_oct` | °C | Minimum monthly mean stream temperature for October across all years in era |
| `wt_min_nov` | °C | Minimum monthly mean stream temperature for November across all years in era |
| `wt_min_dec` | °C | Minimum monthly mean stream temperature for December across all years in era |
| `wt_max_jan` | °C | Maximum monthly mean stream temperature for January across all years in era |
| `wt_max_feb` | °C | Maximum monthly mean stream temperature for February across all years in era |
| `wt_max_mar` | °C | Maximum monthly mean stream temperature for March across all years in era |
| `wt_max_apr` | °C | Maximum monthly mean stream temperature for April across all years in era |
| `wt_max_may` | °C | Maximum monthly mean stream temperature for May across all years in era |
| `wt_max_jun` | °C | Maximum monthly mean stream temperature for June across all years in era |
| `wt_max_jul` | °C | Maximum monthly mean stream temperature for July across all years in era |
| `wt_max_aug` | °C | Maximum monthly mean stream temperature for August across all years in era |
| `wt_max_sep` | °C | Maximum monthly mean stream temperature for September across all years in era |
| `wt_max_oct` | °C | Maximum monthly mean stream temperature for October across all years in era |
| `wt_max_nov` | °C | Maximum monthly mean stream temperature for November across all years in era |
| `wt_max_dec` | °C | Maximum monthly mean stream temperature for December across all years in era |


> All variables use `NaN` as the fill value for missing data.
