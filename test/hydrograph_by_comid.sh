#!/usr/bin/env bash
# Generate raw-vs-processed hydrograph QA plots for a given COMID.
# Runs on a compute node (via srun) since reading a single stream_id out of
# combined_q.nc / combined_wt.nc requires scanning the full file and is too
# slow/heavy for the login node.
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <COMID>" >&2
    exit 1
fi

COMID="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

srun --partition=analysis --time=00:30:00 --mem=16G --cpus-per-task=2 \
    --job-name="hydrograph_${COMID}" \
    bash -c "
        unset VIRTUAL_ENV PIPENV_ACTIVE
        export PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"
        source \"\$HOME/miniconda3/etc/profile.d/conda.sh\"
        conda activate snap-geo
        python '${SCRIPT_DIR}/hydrograph_by_comid.py' '${COMID}'
    "
