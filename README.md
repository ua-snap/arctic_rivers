# Arctic Rivers
Modeled streamflow and stream temperature data in the Arctic.

## SLURM Batch Job
- Use `scripts/combine_arctic_rivers.sbatch` to run `combine_arctic_rivers.py` on a SLURM cluster.
- Specify partition, memory, CPUs, and time via `sbatch` options; set the output path via `OUTPUT` env var.

Example:

```bash
sbatch -p short --mem=64G --cpus-per-task=8 --time=24:00:00 \
	--export=ALL,OUTPUT=/import/home/jdpaul3/arctic_rivers/combined.nc \
	/import/home/jdpaul3/arctic_rivers/scripts/combine_arctic_rivers.sbatch
```

- Optional overrides via env vars: `PARTITION`, `CPUS`, `MEM`, `TIME`, `PYTHON`.
- To run without SLURM:

```bash
python /import/home/jdpaul3/arctic_rivers/combine_arctic_rivers.py \
	--output /import/home/jdpaul3/arctic_rivers/combined.nc
```

## SLURM File Generator
- Generate a `.slurm` file with explicit SBATCH params (no env-var overrides):

```bash
python scripts/generate_combine_slurm.py \
	--output-nc /import/home/jdpaul3/arctic_rivers/combined.nc \
	--slurm-file /import/home/jdpaul3/arctic_rivers/processing/combine_arctic_rivers.slurm \
	--partition short --mem 64G --cpus 8 --time 24:00:00 --job-name arctic-combine

# Submit manually
sbatch /import/home/jdpaul3/arctic_rivers/processing/combine_arctic_rivers.slurm
```

Project overview here: https://geonarrative.usgs.gov/arcticriversproject/

Data release analysis here: https://arcticdata.io/catalog/view/doi%3A10.18739%2FA25M62870 and corresponding output datasets here: https://arcticdata.io/catalog/view/doi%3A10.18739%2FA25M62870

Entire dataset has been copied to local storage at `/beegfs/CMIP6/arctic-cmip6/Arctic_Rivers_Data/`

![image](https://github.com/user-attachments/assets/dcda7f42-d4ac-479b-b20d-1b2e5a43db4d)
