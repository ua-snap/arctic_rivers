## Combine NCAR hydrology data

Combine all NetCDFs from the Arctic Rivers dataset into two outputs: one for daily stream temperature, and one for daily streamflow.

Main scripts:
- [processing/generate_combine_job.py](processing/generate_combine_job.py): writes a `.slurm` file to submit
- [processing/combine_arctic_rivers.py](processing/combine_arctic_rivers.py): does the combination work

Usage:
```bash
python generate_combine_job.py <processing_script> <path/to/source/data> <path/to/output/wt/file> <path/to/output/q/file> <path/to/slurm/files>

sbatch <path/to/slurm/files>/combine_netcdf.slurm
```

Example (use your own directories for outputs):

```bash
python generate_combine_job.py /import/home/jdpaul3/arctic_rivers/processing/combine_arctic_rivers.py /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_wt.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_q.nc /import/home/jdpaul3/arctic_rivers/processing/slurm/

sbatch /import/home/jdpaul3/arctic_rivers/processing/slurm/combine_netcdf.slurm
```


## Compute daily climatologies from combined files

Calculate daily climatologies (min/mean/max) for each day of year, era (1990-2021 and 2034-2065), model, and stream_id from the combined dataset.

Main scripts:
- [processing/generate_climatology_job.py](processing/generate_climatology_job.py): writes a `.slurm` file to submit
- [processing/calculate_daily_climatology.py](processing/calculate_daily_climatology.py): does the climatology calculation work

Usage:
```bash
python generate_climatology_job.py <processing_script> <path/to/combined/wt/file> <path/to/combined/q/file> <path/to/output/wt/climatology/file> <path/to/output/q/climatology/file> <path/to/slurm/files>

sbatch <path/to/slurm/files>/daily_climatology.slurm
```

Example (use your own directories for outputs):

```bash
python generate_climatology_job.py /import/home/jdpaul3/arctic_rivers/processing/calculate_daily_climatology.py /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_wt.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_q.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/daily_clim_wt.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/daily_clim_q.nc /import/home/jdpaul3/arctic_rivers/processing/slurm/

sbatch /import/home/jdpaul3/arctic_rivers/processing/slurm/daily_climatology.slurm
```

## Compute hydrological statistics from combined files

Calculate hydrological stats (monthly means) for each era (1990-2021 and 2034-2065), model, and stream_id from the combined dataset.

Main scripts:
- [processing/generate_stats_job.py](processing/generate_stats_job.py): writes a `.slurm` file to submit
- [processing/calculate_stats.py](processing/calculate_stats.py): does the stats calculation work

Usage:
```bash
python generate_stats_job.py <processing_script> <path/to/combined/wt/file> <path/to/combined/q/file> <path/to/output/wt/stats/file> <path/to/output/q/stats/file> <path/to/slurm/files>

sbatch <path/to/slurm/files>/hydro_statistics.slurm
```

Example (use your own directories for outputs):

```bash
python generate_stats_job.py /import/home/jdpaul3/arctic_rivers/processing/calculate_stats.py /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_wt.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_q.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/stats_wt.nc /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/stats_q.nc /import/home/jdpaul3/arctic_rivers/processing/slurm/

sbatch /import/home/jdpaul3/arctic_rivers/processing/slurm/hydro_statistics.slurm
```


## Notes:
Notes:
- Each job take 5-10 minutes to run on the `analysis` partition once resources are allocated.
- The SLURM jobs use the `analysis` partition by default, but this can be changed using optional params in the `generate_*.py` scripts.
- The SLURM jobs assume you have a conda environment named `snap-geo`. Revise `generate_*.py` scripts if you would like to use a different environment. 
- SLURM logs (`.out/.err`) are written to the provided `<path/to/slurm/files>` directory.