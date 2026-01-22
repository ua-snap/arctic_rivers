#!/bin/bash
#SBATCH -J daily_climatology
#SBATCH -p analysis
#SBATCH --cpus-per-task=28
#SBATCH --mem=750G
#SBATCH --time=8:00:00
#SBATCH -o /import/home/jdpaul3/arctic_rivers/processing/slurm/%x-%j.out
#SBATCH -e /import/home/jdpaul3/arctic_rivers/processing/slurm/%x-%j.err

set -eo pipefail

echo "Starting daily climatology job at $(date)"
echo "Job running on node: $HOSTNAME"

# First, deactivate any existing virtual environments
echo "Deactivating any existing virtual environments..."
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "Found active virtual environment: $VIRTUAL_ENV"
    unset VIRTUAL_ENV
fi
if [[ -n "${PIPENV_ACTIVE:-}" ]]; then
    echo "Found active pipenv environment"
    unset PIPENV_ACTIVE
fi

# Reset PATH to remove any virtual environment modifications
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Activate conda environment
echo "Activating conda environment: snap-geo"
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate snap-geo

# Verify conda environment activation
if [[ "$CONDA_DEFAULT_ENV" != "snap-geo" ]]; then
    echo "ERROR: Failed to activate conda environment snap-geo"
    echo "Current environment: $CONDA_DEFAULT_ENV"
    exit 1
fi

echo "Successfully activated conda environment: $CONDA_DEFAULT_ENV"
echo "Python location: $(which python)"
echo "Python version: $(python --version)"

# Run the script
python /import/home/jdpaul3/arctic_rivers/processing/calculate_daily_climatology.py --wt /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_wt.nc --q /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/combined_q.nc --wt-output /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/daily_clim_wt.nc --q-output /import/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/daily_clim_q.nc --workers 6 --threads-per-worker 4 --chunk-time 365

# Check exit status
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "Processing completed successfully at $(date)"
else
    echo "Processing failed with exit code $EXIT_CODE at $(date)"
    if [ $EXIT_CODE -eq 137 ] || [ $EXIT_CODE -eq 9 ]; then
        echo "This appears to be a memory-related failure. Consider increasing the memory allocation."
    fi
    exit $EXIT_CODE
fi
