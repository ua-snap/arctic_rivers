#!/usr/bin/env python
"""
Generate a SLURM script to run prep_for_rasdaman.py on the final combined NetCDF.

Usage:
  python generate_rasdaman_job.py \
    --scripts-dir /import/home/jdpaul3/arctic_rivers/processing \
    --input       /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_combined.nc \
    --output      /beegfs/CMIP6/jdpaul3/arctic_rivers_data/mhit_indices_combined_for_rasdaman.nc \
    --slurm-dir   /import/home/jdpaul3/arctic_rivers/processing/matlab/slurm

Example submission:
  sbatch slurm/rasdaman_prep.slurm
"""
import argparse
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description="Generate SLURM script for Rasdaman prep step")
    p.add_argument("--scripts-dir", required=True, help="Directory containing prep_for_rasdaman.py")
    p.add_argument("--input",       required=True, help="Input NetCDF (output of add_source_dim_mhit.py)")
    p.add_argument("--output",      required=True, help="Output Rasdaman-ready NetCDF path")
    p.add_argument("--slurm-dir",   required=True, help="Directory to write the SLURM script")
    p.add_argument("--conda-env",   default="snap-geo")
    p.add_argument("--memory",      default="16G")
    p.add_argument("--time",        default="1:00:00")
    p.add_argument("--partition",   default="t2small")
    args = p.parse_args()

    slurm_dir = Path(args.slurm_dir)
    slurm_dir.mkdir(parents=True, exist_ok=True)
    slurm_path = slurm_dir / "rasdaman_prep.slurm"

    script = f"""\
#!/bin/bash
#SBATCH --job-name=rasdaman_prep
#SBATCH --output={slurm_dir}/rasdaman_prep-%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem={args.memory}
#SBATCH --time={args.time}
#SBATCH --partition={args.partition}

source ~/.bashrc
conda activate {args.conda_env}

python {args.scripts_dir}/prep_for_rasdaman.py \\
    {args.input} \\
    {args.output}

echo "Rasdaman prep complete: {args.output}"
"""

    slurm_path.write_text(script)
    print(f"Wrote {slurm_path}")
    print()
    print("Submit with:")
    print(f"  sbatch {slurm_path}")


if __name__ == "__main__":
    main()
