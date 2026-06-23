#!/usr/bin/env python3
"""
For a given COMID, plot daily-climatology hydrographs from both the raw
combined NetCDF files (computed on the fly) and the preprocessed daily
climatology files, stacked one over the other, for visual QA of the
preprocessing pipeline.

Usage: python hydrograph_by_comid.py <COMID>
"""
import sys
import datetime

import numpy as np
import xarray as xr
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW_Q = "/beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_q.nc"
RAW_WT = "/beegfs/CMIP6/jdpaul3/arctic_rivers_data/combined_wt.nc"
CLIM_Q = "/beegfs/CMIP6/jdpaul3/arctic_rivers_data/daily_clim_q_06152026.nc"
CLIM_WT = "/beegfs/CMIP6/jdpaul3/arctic_rivers_data/daily_clim_wt_06152026.nc"

HIST_MODEL = "historical"
HIST_ERA = "1990-2021"
PROJ_ERA = "2034-2065"

# matches Q's units (cfs); floor used only so zero-flow days remain visible
# at the bottom of a log-scale axis instead of being dropped as invalid.
LOG_FLOOR = 0.01

VAR_CONFIG = {
    "q": dict(
        raw_path=RAW_Q,
        clim_path=CLIM_Q,
        raw_var="IRFroutedRunoff",
        label="Streamflow",
        ylabel="Streamflow (cfs)",
        log_scale=True,
    ),
    "wt": dict(
        raw_path=RAW_WT,
        clim_path=CLIM_WT,
        raw_var="T_stream",
        label="Water Temperature",
        ylabel="Water Temperature (degC)",
        log_scale=False,
    ),
}


def assign_era(ds):
    time_values = ds["time"].values
    eras = np.where(time_values < np.datetime64("2022-01-01"), HIST_ERA, PROJ_ERA)
    return ds.assign_coords(era=("time", eras))


def calculate_daily_climatology(ds, var_name):
    ds = ds.assign_coords(doy=("time", ds["time"].dt.dayofyear.values))
    count = ds.groupby(["doy", "era"]).count(dim="time")
    daily_min = ds.groupby(["doy", "era"]).min(dim="time", skipna=True)
    daily_mean = ds.groupby(["doy", "era"]).mean(dim="time", skipna=True)
    daily_max = ds.groupby(["doy", "era"]).max(dim="time", skipna=True)

    daily_min[var_name] = daily_min[var_name].where(count[var_name] > 0)
    daily_mean[var_name] = daily_mean[var_name].where(count[var_name] > 0)
    daily_max[var_name] = daily_max[var_name].where(count[var_name] > 0)

    return xr.Dataset(
        {
            "doy_min": daily_min[var_name],
            "doy_mean": daily_mean[var_name],
            "doy_max": daily_max[var_name],
        }
    )


def build_panel(ds):
    """Reduce a (model, doy, era) climatology dataset to the curves needed for one plot panel."""
    models = list(ds.model.values)
    proj_models = [m for m in models if m != HIST_MODEL]

    hist = ds.sel(model=HIST_MODEL, era=HIST_ERA)
    proj = ds.sel(model=proj_models, era=PROJ_ERA)

    return {
        "doy": ds.doy.values,
        "hist_min": hist.doy_min.values,
        "hist_mean": hist.doy_mean.values,
        "hist_max": hist.doy_max.values,
        "proj_max": proj.doy_max.max(dim="model").values,
        "proj_min": proj.doy_min.min(dim="model").values,
        "proj_mean": proj.doy_mean.mean(dim="model").values,
        "proj_mean_lo": proj.doy_mean.min(dim="model").values,
        "proj_mean_hi": proj.doy_mean.max(dim="model").values,
    }


def water_year_order(doy_values):
    """Index order that rotates calendar day-of-year so Oct 1 plots first and Sep 30 last."""
    water_year_start_doy = datetime.date(2001, 10, 1).timetuple().tm_yday
    after = [i for i, d in enumerate(doy_values) if d >= water_year_start_doy]
    before = [i for i, d in enumerate(doy_values) if d < water_year_start_doy]
    return after + before


def month_ticks(doy_values_ordered):
    ticks, labels = [], []
    for month in range(1, 13):
        target_doy = datetime.date(2001, month, 1).timetuple().tm_yday
        pos = np.where(doy_values_ordered == target_doy)[0]
        if len(pos):
            ticks.append(pos[0])
            labels.append(datetime.date(2001, month, 1).strftime("%b"))
    return ticks, labels


def plot_panel(ax, panel, cfg, title):
    order = water_year_order(panel["doy"])
    doy_ordered = panel["doy"][order]
    x = np.arange(len(order))

    def series(key):
        arr = np.asarray(panel[key], dtype=float)[order]
        if cfg["log_scale"]:
            arr = np.where(arr <= 0, LOG_FLOOR, arr)
        return arr

    ax.fill_between(x, series("hist_min"), series("hist_max"), color="gray", alpha=0.5, linewidth=0, label="Historical min–max")
    ax.plot(x, series("hist_mean"), color="white", linewidth=1.5, label="Historical mean", zorder=4)

    ax.fill_between(x, series("proj_mean_lo"), series("proj_mean_hi"), color="green", alpha=0.25, linewidth=0, label="Projected mean spread")
    ax.plot(x, series("proj_max"), color="darkgreen", linewidth=1.3, label="Projected max (all models)", zorder=3)
    ax.plot(x, series("proj_min"), color="lightgreen", linewidth=1.3, label="Projected min (all models)", zorder=3)
    ax.plot(x, series("proj_mean"), color="green", linewidth=1.5, label="Projected mean (all models)", zorder=4)

    if cfg["log_scale"]:
        ax.set_yscale("log")

    ticks, labels = month_ticks(doy_ordered)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlim(0, len(x) - 1)
    ax.set_ylabel(cfg["ylabel"])
    ax.set_title(title, fontsize=10)
    ax.grid(True, alpha=0.3, which="both" if cfg["log_scale"] else "major")


def load_processed_panel(comid, cfg):
    ds = xr.open_dataset(cfg["clim_path"])
    try:
        sub = ds.sel(stream_id=comid).load()
    except KeyError:
        raise SystemExit(f"COMID {comid} not found in {cfg['clim_path']}")
    return build_panel(sub)


def load_raw_panel(comid, cfg):
    ds = xr.open_dataset(cfg["raw_path"])
    try:
        sub = ds.sel(stream_id=comid).load()
    except KeyError:
        raise SystemExit(f"COMID {comid} not found in {cfg['raw_path']}")
    sub = assign_era(sub)
    clim = calculate_daily_climatology(sub, cfg["raw_var"])
    return build_panel(clim)


def make_figure(comid, var_key):
    cfg = VAR_CONFIG[var_key]

    # Validate against the small preprocessed file first so a bad COMID
    # fails fast, before paying the cost of reading the large raw file.
    processed_panel = load_processed_panel(comid, cfg)
    raw_panel = load_raw_panel(comid, cfg)

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), sharex=True)
    plot_panel(axes[0], raw_panel, cfg, f"COMID {comid} — {cfg['label']} — computed from raw data")
    plot_panel(axes[1], processed_panel, cfg, f"COMID {comid} — {cfg['label']} — preprocessed climatology file")
    axes[1].set_xlabel("Month (Water Year: Oct–Sep)")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.02), fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    out_path = f"{comid}_{var_key}.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {out_path}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(f"Usage: {sys.argv[0]} <COMID>")
    comid = int(sys.argv[1])

    for var_key in VAR_CONFIG:
        try:
            make_figure(comid, var_key)
        except SystemExit as exc:
            print(f"WARNING: skipping '{var_key}': {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
