# NCAR "Arctic Rivers" Data Processing Pipeline

## 1. Combine hydrology outputs

Combine all NetCDFs from the Arctic Rivers dataset into two outputs: one for daily stream temperature (`WT`), and one for daily streamflow (`Q`). Streamflow is converted from cubic meters per second (cms) to cubic feet per second (cfs) to match other hydrology coverages. Source data lives here at `/import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data`

#### Main scripts:
- [processing/generate_combine_job.py](processing/generate_combine_job.py): writes a `.slurm` file to submit
- [processing/combine_arctic_rivers.py](processing/combine_arctic_rivers.py): does the combination work

#### Usage:

```bash
python generate_combine_job.py <processing_script> <path/to/source/data> <path/to/output/wt/file> <path/to/output/q/file> <path/to/slurm/files>
```
```bash
sbatch <path/to/slurm/files>/combine_netcdf.slurm
```

Example (use your own directories for outputs):

```bash
python generate_combine_job.py combine_arctic_rivers.py /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data /import/beegfs/CMIP6/jdpaul3/arctic_rivers/combined_wt.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/combined_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/combine_netcdf.slurm
```


## 2. Compute daily climatologies from combined files

Calculate daily climatologies (min/mean/max) for each day of year, era (1990-2021 and 2034-2065), model, and stream_id from the combined dataset. The script calculates daily climatologies for both streamflow and temperature.

#### Main scripts:
- [processing/generate_climatology_job.py](processing/generate_climatology_job.py): writes a `.slurm` file to submit
- [processing/calculate_daily_climatology.py](processing/calculate_daily_climatology.py): does the climatology calculation work

#### Usage:

```bash
python generate_climatology_job.py <processing_script> <path/to/combined/wt/file> <path/to/combined/q/file> <path/to/output/wt/climatology/file> <path/to/output/q/climatology/file> <path/to/slurm/files>
```
```bash
sbatch <path/to/slurm/files>/daily_climatology.slurm
```

Example (use your own directories for outputs):

```bash
python generate_climatology_job.py calculate_daily_climatology.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers/combined_wt.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/combined_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/daily_clim_wt.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/daily_clim_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/daily_climatology.slurm
```

## 3. Compute streamflow statistics from combined files

Calculate streamflow stats (monthly means) for each era (1990-2021 and 2034-2065), model, and stream_id from the combined dataset. See section 5 for the analogous stream temperature statistics.

#### Main scripts:
- [processing/generate_stats_job.py](processing/generate_stats_job.py): writes a `.slurm` file to submit
- [processing/calculate_stats.py](processing/calculate_stats.py): does the stats calculation work

#### Usage:

```bash
python generate_stats_job.py <processing_script> <path/to/combined/q/file> <path/to/output/q/stats/file> <path/to/slurm/files>
```
```bash
sbatch <path/to/slurm/files>/streamflow_stats.slurm
```

Example (use your own directories for outputs):

```bash
python generate_stats_job.py calculate_stats.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers/combined_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/stats_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/streamflow_stats.slurm
```

## 5. Compute stream temperature statistics from combined files

Calculate stream temperature statistics for each era (1990-2021 and 2034-2065), model, and stream_id from the combined WT dataset. Statistics include: mean annual days above 13/18/20°C; monthly min/mean/max temperatures; annual maximum daily temperature (magnitude and Julian day); maximum 7-day rolling average temperature (magnitude and Julian day); and cumulative degree days above 0°C for May–September.

#### Main scripts:
- [processing/generate_wt_stats_job.py](processing/generate_wt_stats_job.py): writes a `.slurm` file to submit
- [processing/calculate_wt_stats.py](processing/calculate_wt_stats.py): does the stats calculation work

#### Usage:

```bash
python generate_wt_stats_job.py <processing_script> <path/to/combined/wt/file> <path/to/output/wt/stats/file> <path/to/slurm/files>
```
```bash
sbatch <path/to/slurm/files>/stream_temp_stats.slurm
```

Example (use your own directories for outputs):

```bash
python generate_wt_stats_job.py calculate_wt_stats.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_wt.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers_data/wt_stats.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/stream_temp_stats.slurm
```


## 4. Prep for Rasdaman ingestion

Convert string dimensions to integers and add encoding dictionaries to dimension metadata. Convert all variables to `float32` data type. Run once per output file: streamflow statistics, streamflow climatology, and stream temperature statistics. Change the slurm job name when calling `generate_rasdaman_job.py` in order to create individually named slurm job scripts to submit. 

#### Main scripts:
- [processing/generate_rasdaman_job.py](processing/generate_rasdaman_job.py): writes a `.slurm` file to submit
- [processing/prep_for_rasdaman.py](processing/prep_for_rasdaman.py): does the Rasdaman prep work

#### Usage:

```bash
python generate_rasdaman_job.py <processing_script> <path/to/input/file> <path/to/output/file> <path/to/slurm/files>
```
```bash
sbatch <path/to/slurm/files>/rasdaman_prep.slurm
```

Example (use your own directories for outputs):

```bash
python generate_rasdaman_job.py prep_for_rasdaman.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers/stats_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/stats_q_for_rasdaman.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/ --job-name "rasdaman_stats_prep"
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/rasdaman_stats_prep.slurm
```
```bash
python generate_rasdaman_job.py prep_for_rasdaman.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers/daily_clim_q.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/daily_clim_q_for_rasdaman.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/ --job-name "rasdaman_daily_clim_prep"
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/rasdaman_daily_clim_prep.slurm
```
```bash
python generate_rasdaman_job.py prep_for_rasdaman.py /import/beegfs/CMIP6/jdpaul3/arctic_rivers_data/wt_stats.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers_data/wt_stats_for_rasdaman.nc /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/ --job-name "rasdaman_wt_stats_prep"
```
```bash
sbatch /import/beegfs/CMIP6/jdpaul3/arctic_rivers/slurm/rasdaman_wt_stats_prep.slurm
```


## Notes:
- Each job take < 5 minutes to run on the `analysis` partition once resources are allocated.
- The SLURM jobs use the `analysis` partition by default, but this can be changed using optional params in the `generate_*.py` scripts.
- The SLURM jobs assume you have a conda environment named `snap-geo`. Revise `generate_*.py` scripts if you would like to use a different environment. 
- SLURM logs (`*.out` and `*.err`) are written to the provided `<path/to/slurm/files>` directory. Consult these first when troubleshooting. 