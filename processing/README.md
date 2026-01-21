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

Notes:
- SLURM logs (`.out/.err`) are written to the provided `<path/to/slurm/files>` directory.
- The SLURM job uses the `analysis` partition by default, but this can be changed using optional params. See `generate_combine_job.py` for all optional params.

## Compute daily climatologies from combined files

TBD