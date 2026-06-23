# hydrograph_by_comid

For a given COMID, plots daily-climatology hydrographs and stream temperature time series computed
on-the-fly from the raw combined NetCDF files against the same climatology
read from the preprocessed `daily_clim_*` Rasdaman coverage files. Designed for visual inspection of daily time series against the plots in the front end Hydroviz application.

## Usage

```
./hydrograph_by_comid.sh <COMID>
```

Produces `<COMID>_q.png` (streamflow) and `<COMID>_wt.png` (water
temperature) in the current directory.

Runs on a compute node via `srun` (partition `analysis`, conda env
`snap-geo`) — reading a single stream_id out of `combined_q.nc` /
`combined_wt.nc` requires scanning the whole file and is too slow/heavy for
the login node (can take a few minutes).

Example, for COMID 81000004 (this is what `./hydrograph_by_comid.sh 81000004` runs
under the hood):

```
srun --partition=analysis --time=00:30:00 --mem=16G --cpus-per-task=2 \
    --job-name=hydrograph_81000004 \
    bash -c "
        unset VIRTUAL_ENV PIPENV_ACTIVE
        export PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"
        source \"\$HOME/miniconda3/etc/profile.d/conda.sh\"
        conda activate snap-geo
        python hydrograph_by_comid.py 81000004
    "
```

Gray = historical era (1990-2021) min/max/mean. Green = projected era
(2034-2065) min/max/mean across all projection models, with shaded spread
between the model means. Streamflow uses a log y-axis; water temperature
uses linear.

Input file paths are hardcoded at the top of `hydrograph_by_comid.py`.
