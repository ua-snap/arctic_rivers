from luts import data_source_dict, gcm_metadata_dict  # noqa: F401 — re-exported for convenience

wt_clim_var_dict = {
    "doy_min": {
        "description": "Minimum daily stream temperature for day of year across all years in era",
        "units": "degC",
    },
    "doy_max": {
        "description": "Maximum daily stream temperature for day of year across all years in era",
        "units": "degC",
    },
    "doy_mean": {
        "description": "Mean daily stream temperature for day of year across all years in era",
        "units": "degC",
    },
}

_MONTH_NAMES = ["jan", "feb", "mar", "apr", "may", "jun",
                "jul", "aug", "sep", "oct", "nov", "dec"]
_MONTH_LABELS = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]

wt_stat_var_dict = {
    # ── Threshold exceedance ─────────────────────────────────────────────────
    "wt_days_gt13_mean": {
        "description": "Mean annual count of days with stream temperature > 13°C.",
        "units": "days/yr",
    },
    "wt_days_gt18_mean": {
        "description": "Mean annual count of days with stream temperature > 18°C.",
        "units": "days/yr",
    },
    "wt_days_gt20_mean": {
        "description": "Mean annual count of days with stream temperature > 20°C.",
        "units": "days/yr",
    },
    # ── Monthly mean temperature ─────────────────────────────────────────────
    **{
        f"wt_mean_{mname}": {
            "description": f"Mean of monthly mean stream temperatures for {mlabel}.",
            "units": "degC",
        }
        for mname, mlabel in zip(_MONTH_NAMES, _MONTH_LABELS)
    },
    # ── Monthly minimum temperature ──────────────────────────────────────────
    **{
        f"wt_min_{mname}": {
            "description": f"Minimum monthly mean stream temperature for {mlabel} across all years in era.",
            "units": "degC",
        }
        for mname, mlabel in zip(_MONTH_NAMES, _MONTH_LABELS)
    },
    # ── Monthly maximum temperature ──────────────────────────────────────────
    **{
        f"wt_max_{mname}": {
            "description": f"Maximum monthly mean stream temperature for {mlabel} across all years in era.",
            "units": "degC",
        }
        for mname, mlabel in zip(_MONTH_NAMES, _MONTH_LABELS)
    },
    # ── Annual maximum daily temperature ─────────────────────────────────────
    "wt_ann_max_temp_mean": {
        "description": "Mean (over era years) of the annual maximum daily stream temperature.",
        "units": "degC",
    },
    "wt_ann_max_temp_doy_mean": {
        "description": "Mean (over era years) Julian day of the annual maximum daily stream temperature.",
        "units": "day of year",
    },
    # ── Maximum 7-day rolling average temperature ─────────────────────────────
    "wt_7d_max_temp_mean": {
        "description": "Mean (over era years) of the annual maximum 7-day rolling average stream temperature.",
        "units": "degC",
    },
    "wt_7d_max_temp_doy_mean": {
        "description": "Mean (over era years) Julian day of the center of the annual maximum 7-day rolling average.",
        "units": "day of year",
    },
    # ── Cumulative degree days ────────────────────────────────────────────────
    "wt_cdd_may_sept_mean": {
        "description": "Mean (over era years) annual cumulative degree days above 0°C, May through September.",
        "units": "degC days",
    },
}
