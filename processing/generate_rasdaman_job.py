#!/usr/bin/env python3
"""
Generate a SLURM .slurm job for preparing processed Arctic Rivers NetCDF files for Rasdaman ingestion.

Usage:
  python generate_rasdaman_job.py \
    /path/to/prep_for_rasdaman.py \
    /path/to/input.nc \
    /path/to/output.nc \
    /path/to/slurm/scripts \
    --string-dims model era \
    --conda-env "snap-geo" \
    --job-name "rasdaman_prep" \
    --partition "analysis" \
    --memory "750G" \
    --cpus 28 \
    --time "2:00:00"

This writes a .slurm file into the specified scripts directory, which you can submit with sbatch.

Example submission:
    sbatch /path/to/slurm/scripts/rasdaman_prep.slurm

"""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate rasdaman preparation .slurm job file")
    parser.add_argument("rasdaman_script", help="Path to the prep_for_rasdaman.py script")
    parser.add_argument("input_nc", help="Path to input .nc file")
    parser.add_argument("output_nc", help="Path to output .nc file")
    parser.add_argument("slurm_dir", help="Directory to write the .slurm job file")
    parser.add_argument("--string-dims", nargs="*", default=["model", "era", "source"],
                        help="List of string dimensions to convert to integers")
    parser.add_argument("--conda-env", default="snap-geo", help="Conda environment name to activate")
    parser.add_argument("--job-name", default="rasdaman_prep")
    parser.add_argument("--partition", default="analysis")
    parser.add_argument("--memory", default="750G")
    parser.add_argument("--cpus", type=int, default=28)
    parser.add_argument("--time", default="2:00:00")
    args = parser.parse_args()

    slurm_dir = Path(args.slurm_dir)
    slurm_dir.mkdir(parents=True, exist_ok=True)
    slurm_path = slurm_dir / f"{args.job_name}.slurm"

    output_dir = Path(args.output_nc).parent
    output_dir.mkdir(parents=True, exist_ok=True)


    # Build rasdaman preparation command
    rasdaman_cmd = f"python {args.rasdaman_script} {args.input_nc} {args.output_nc}"
    if args.string_dims:
        rasdaman_cmd += f" --string-dims {' '.join(args.string_dims)}"

    content = f"""#!/bin/bash
#SBATCH -J {args.job_name}
#SBATCH -p {args.partition}
#SBATCH --cpus-per-task={args.cpus}
#SBATCH --mem={args.memory}
#SBATCH --time={args.time}
#SBATCH -o {slurm_dir}/%x-%j.out
#SBATCH -e {slurm_dir}/%x-%j.err

set -eo pipefail

echo "Starting rasdaman preparation job at $(date)"
echo "Job running on node: $HOSTNAME"

# First, deactivate any existing virtual environments
echo "Deactivating any existing virtual environments..."
if [[ -n "${{VIRTUAL_ENV:-}}" ]]; then
    echo "Found active virtual environment: $VIRTUAL_ENV"
    unset VIRTUAL_ENV
fi
if [[ -n "${{PIPENV_ACTIVE:-}}" ]]; then
    echo "Found active pipenv environment"
    unset PIPENV_ACTIVE
fi

# Reset PATH to remove any virtual environment modifications
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Activate conda environment
echo "Activating conda environment: {args.conda_env}"
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate {args.conda_env}

# Verify conda environment activation
if [[ "$CONDA_DEFAULT_ENV" != "{args.conda_env}" ]]; then
    echo "ERROR: Failed to activate conda environment {args.conda_env}"
    echo "Current environment: $CONDA_DEFAULT_ENV"
    exit 1
fi

echo "Successfully activated conda environment: $CONDA_DEFAULT_ENV"
echo "Python location: $(which python)"
echo "Python version: $(python --version)"

# Run the script
{rasdaman_cmd}

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
"""

    slurm_path.write_text(content)
    print(f"Wrote SLURM job: {slurm_path}")
    print(f"Submit with: sbatch {slurm_path}")

if __name__ == "__main__":
    main()
