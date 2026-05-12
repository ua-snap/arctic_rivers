#!/usr/bin/env python
"""
Generate SLURM job array script for the MHIT hydrological statistics pipeline.

Usage:
  python generate_mhit_jobs.py \
    --scripts-dir /import/home/jdpaul3/arctic_rivers/processing/matlab \
    --q-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc \
    --drain-csv /beegfs/CMIP6/jdpaul3/arctic_rivers_data/drainage_area_lookup.csv \
    --staging-dir /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_partial \
    --output-nc /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices.nc \
    --slurm-dir /import/home/jdpaul3/arctic_rivers/processing/matlab/slurm \
    --conda-env snap-geo \
    --mhit-dir /beegfs/CMIP6/jdpaul3/MHIT \
    --chunk-size 500 \
    --cpus 4 \
    --memory 16G \
    --time 4:00:00 \
    --partition analysis \
    --max-concurrent 20

This writes two SLURM scripts into --slurm-dir:
  mhit_chunks.slurm   -- job array for all chunk jobs
  mhit_merge.slurm    -- single final merge job (submit after array completes)

Example submission:
  ARRAY_JOB_ID=$(sbatch --parsable slurm/mhit_chunks.slurm)
  sbatch --dependency=afterok:$ARRAY_JOB_ID slurm/mhit_merge.slurm
"""
import argparse
import math
from pathlib import Path

import xarray as xr


def get_n_streams(q_nc):
    ds = xr.open_dataset(q_nc, decode_times=False)
    n = len(ds["stream_id"])
    ds.close()
    return n


def main():
    p = argparse.ArgumentParser(description="Generate MHIT SLURM job array")
    p.add_argument("--scripts-dir",   required=True,  help="Directory containing mhit_chunk.py and mhit_runner.m")
    p.add_argument("--q-nc",          required=True,  help="Path to combined_q.nc")
    p.add_argument("--drain-csv",     required=True,  help="Path to drainage_area_lookup.csv")
    p.add_argument("--staging-dir",   required=True,  help="Directory for partial NetCDF files")
    p.add_argument("--output-nc",     required=True,  help="Final merged output NetCDF path")
    p.add_argument("--slurm-dir",     required=True,  help="Directory to write SLURM scripts")
    p.add_argument("--conda-env",     default="snap-geo")
    p.add_argument("--mhit-dir",      required=True, help="Root of cloned MHIT repo (must contain MFiles/)")
    p.add_argument("--chunk-size",    type=int, default=500)
    p.add_argument("--cpus",          type=int, default=4)
    p.add_argument("--memory",        default="16G")
    p.add_argument("--time",          default="4:00:00")
    p.add_argument("--partition",     default="analysis")
    p.add_argument("--max-concurrent", type=int, default=20, help="Max simultaneous array tasks")
    p.add_argument("--cleanup", action="store_true",
                   help="Delete partial_*.nc files after a successful merge")
    args = p.parse_args()

    slurm_dir  = Path(args.slurm_dir)
    scripts_dir = Path(args.scripts_dir)
    staging_dir = Path(args.staging_dir)
    slurm_dir.mkdir(parents=True, exist_ok=True)

    n_streams = get_n_streams(args.q_nc)
    n_chunks  = math.ceil(n_streams / args.chunk_size)
    last_idx  = n_chunks - 1

    print(f"Streams: {n_streams},  chunk size: {args.chunk_size},  jobs: {n_chunks}")

    mfiles_dir = str(Path(args.mhit_dir) / "MFiles")

    # ---------- chunk job array ----------
    chunk_script = slurm_dir / "mhit_chunks.slurm"
    chunk_content = f"""#!/bin/bash
#SBATCH -J mhit_chunks
#SBATCH -p {args.partition}
#SBATCH --cpus-per-task={args.cpus}
#SBATCH --mem={args.memory}
#SBATCH --time={args.time}
#SBATCH --array=0-{last_idx}%{args.max_concurrent}
#SBATCH -o {slurm_dir}/%x-%A_%a.out
#SBATCH -e {slurm_dir}/%x-%A_%a.err

set -eo pipefail

echo "Task ${{SLURM_ARRAY_TASK_ID}} / {last_idx} starting on $HOSTNAME at $(date)"

# Activate conda
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate {args.conda_env}
if [[ "$CONDA_DEFAULT_ENV" != "{args.conda_env}" ]]; then
    echo "ERROR: Failed to activate conda env {args.conda_env}"
    exit 1
fi

# Compute stream index range for this task
TASK_ID=${{SLURM_ARRAY_TASK_ID}}
START_IDX=$(( TASK_ID * {args.chunk_size} ))
END_IDX=$(( START_IDX + {args.chunk_size} ))
if [ $END_IDX -gt {n_streams} ]; then END_IDX={n_streams}; fi

# Working directories
WORK_DIR=$(mktemp -d)
CSV_DIR="${{WORK_DIR}}/csvs"
OUT_DIR="${{WORK_DIR}}/results"
PARTIAL_NC="{staging_dir}/partial_${{START_IDX}}_${{END_IDX}}.nc"
mkdir -p "${{CSV_DIR}}" "${{OUT_DIR}}"

echo "Stream range: ${{START_IDX}} - ${{END_IDX}}"
echo "Working dir: $WORK_DIR"

# Skip if partial NetCDF already exists (allows safe resubmission)
if [ -f "${{PARTIAL_NC}}" ]; then
    echo "Partial NetCDF already exists, skipping: ${{PARTIAL_NC}}"
    rm -rf "$WORK_DIR"
    exit 0
fi

# Step 1: Extract CSVs
echo "--- Step 1: Extracting CSVs ---"
python {scripts_dir}/mhit_chunk.py extract \\
    --start-idx ${{START_IDX}} \\
    --end-idx   ${{END_IDX}} \\
    --q-nc      {args.q_nc} \\
    --drain-csv {args.drain_csv} \\
    --out-dir   "${{CSV_DIR}}"

# Step 2: Run MATLAB
echo "--- Step 2: Running MATLAB ---"
export MHIT_CSV_DIR="${{CSV_DIR}}"
export MHIT_OUT_DIR="${{OUT_DIR}}"
export MHIT_MFILES="{mfiles_dir}"
export MHIT_NCORES="{args.cpus}"

module load MATLAB/R2023b
matlab -batch "run('{scripts_dir}/mhit_runner.m')"

# Step 3: Pack results into partial NetCDF
echo "--- Step 3: Packing NetCDF ---"
python {scripts_dir}/mhit_chunk.py pack \\
    --start-idx   ${{START_IDX}} \\
    --end-idx     ${{END_IDX}} \\
    --results-csv "${{OUT_DIR}}/results.csv" \\
    --q-nc        {args.q_nc} \\
    --partial-nc  "${{PARTIAL_NC}}"

# Cleanup temp files
rm -rf "$WORK_DIR"
echo "Task ${{SLURM_ARRAY_TASK_ID}} completed at $(date)"
"""
    chunk_script.write_text(chunk_content)
    print(f"Wrote: {chunk_script}")

    # ---------- merge job ----------
    merge_script = slurm_dir / "mhit_merge.slurm"
    merge_content = f"""#!/bin/bash
#SBATCH -J mhit_merge
#SBATCH -p {args.partition}
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=2:00:00
#SBATCH -o {slurm_dir}/%x-%j.out
#SBATCH -e {slurm_dir}/%x-%j.err

set -eo pipefail

echo "Merge job starting on $HOSTNAME at $(date)"

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate {args.conda_env}
if [[ "$CONDA_DEFAULT_ENV" != "{args.conda_env}" ]]; then
    echo "ERROR: Failed to activate conda env {args.conda_env}"
    exit 1
fi

python {scripts_dir}/merge_mhit_chunks.py \\
    --partial-dir {staging_dir} \\
    --output      {args.output_nc} \\
    --q-nc        {args.q_nc}{" \\\n    --cleanup" if args.cleanup else ""}

echo "Merge completed at $(date)"
echo "Output: {args.output_nc}"
"""
    merge_script.write_text(merge_content)
    print(f"Wrote: {merge_script}")

    print()
    print("Submit with:")
    print(f"  ARRAY_JOB_ID=$(sbatch --parsable {chunk_script})")
    print(f"  sbatch --dependency=afterok:$ARRAY_JOB_ID {merge_script}")
    print()
    print(f"Total jobs: {n_chunks} chunks + 1 merge")
    print(f"Max concurrent: {args.max_concurrent}")


if __name__ == "__main__":
    main()
