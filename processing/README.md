python generate_combine_job.py \
    /import/home/jdpaul3/arctic_rivers/processing/combine_arctic_rivers.py \
    /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data \
    /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_wt.nc \
    /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_q.nc \
    /import/home/jdpaul3/arctic_rivers/processing/slurm/

sbatch /import/home/jdpaul3/arctic_rivers/processing/slurm/combine_netcdf.slurm