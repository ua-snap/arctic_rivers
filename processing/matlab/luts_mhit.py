#!/usr/bin/env python
# Metadata for the 52 hydrological statistics computed by the MHIT pipeline.
# Source: https://github.com/ua-snap/hydroviz/blob/main/data/streamflow_statistics_description_table.csv

MHIT_STATS = {
    # --- Magnitude ---
    "ma3":      {"category": "magnitude",      "units": "percent",         "code_base": "mhit",   "difference_method": "ratio",    "description": "Coefficient of variation (std/mean) of annual daily flows; mean of annual CVs."},
    "ma4":      {"category": "magnitude",      "units": "percent",         "code_base": "mhit",   "difference_method": "ratio",    "description": "Standard deviation of percentiles of log-transformed flow divided by mean of those percentiles."},
    "ma12":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for January."},
    "ma13":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for February."},
    "ma14":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for March."},
    "ma15":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for April."},
    "ma16":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for May."},
    "ma17":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for June."},
    "ma18":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for July."},
    "ma19":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for August."},
    "ma20":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for September."},
    "ma21":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for October."},
    "ma22":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for November."},
    "ma23":     {"category": "magnitude",      "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean of monthly flow values for December."},
    "mh14":     {"category": "magnitude",      "units": "dimensionless",   "code_base": "mhit",   "difference_method": "ratio",    "description": "Median of (annual maximum flow / median annual flow) ratios."},
    "mh20":     {"category": "magnitude",      "units": "cfs_per_sqmi",    "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum flow divided by drainage area (specific discharge)."},
    "ml17":     {"category": "magnitude",      "units": "dimensionless",   "code_base": "mhit",   "difference_method": "ratio",    "description": "Base flow index: mean of annual (7-day minimum flow / mean annual flow) ratios."},
    "spr_mag":  {"category": "magnitude",      "units": "cfs_per_sqmi",    "code_base": "matlab", "difference_method": "ratio",    "description": "Median spring (April-June) maximum flow divided by drainage area."},
    "sum_cv":   {"category": "magnitude",      "units": "percent",         "code_base": "matlab", "difference_method": "ratio",    "description": "Median annual coefficient of variation of summer (July-September) flows."},
    "sum_mag":  {"category": "magnitude",      "units": "cfs_per_sqmi",    "code_base": "matlab", "difference_method": "absolute", "description": "Median summer (July-September) minimum flow divided by drainage area."},
    # --- Duration ---
    "dh1":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum 1-day average flow."},
    "dh2":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum 3-day average flow."},
    "dh3":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum 7-day average flow."},
    "dh4":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum 30-day average flow."},
    "dh5":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual maximum 90-day average flow."},
    "dh15":     {"category": "duration",       "units": "days_per_year",   "code_base": "mhit",   "difference_method": "ratio",    "description": "Median annual average duration of high flow pulses (above 75th percentile)."},
    "dl1":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual minimum 1-day average flow."},
    "dl2":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual minimum 3-day average flow."},
    "dl3":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual minimum 7-day average flow."},
    "dl4":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual minimum 30-day average flow."},
    "dl5":      {"category": "duration",       "units": "cfs",             "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean annual minimum 90-day average flow."},
    "dl16":     {"category": "duration",       "units": "days_per_year",   "code_base": "mhit",   "difference_method": "ratio",    "description": "Median annual average duration of low flow pulses (below 25th percentile)."},
    "lf1":      {"category": "duration",       "units": "days_per_year",   "code_base": "matlab", "difference_method": "absolute", "description": "Median annual number of days below threshold of 0.1 cfs per square mile."},
    "spr_dur3": {"category": "duration",       "units": "cfs",             "code_base": "matlab", "difference_method": "ratio",    "description": "Median spring (April-June) maximum 3-day moving average flow."},
    "spr_dur7": {"category": "duration",       "units": "cfs",             "code_base": "matlab", "difference_method": "ratio",    "description": "Median spring (April-June) maximum 7-day moving average flow."},
    "sum_dur3": {"category": "duration",       "units": "cfs",             "code_base": "matlab", "difference_method": "ratio",    "description": "Median summer (July-September) minimum 3-day moving average flow."},
    "sum_dur7": {"category": "duration",       "units": "cfs",             "code_base": "matlab", "difference_method": "ratio",    "description": "Median summer (July-September) minimum 7-day moving average flow."},
    # --- Frequency ---
    "fh1":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual count of high flow pulses above 75th percentile."},
    "fh5":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual flood frequency above median flow."},
    "fh6":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual flood frequency above 3 times median flow."},
    "fh7":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual flood frequency above 7 times median flow."},
    "fl1":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual count of low flow pulses below 25th percentile."},
    "fl3":      {"category": "frequency",      "units": "events_per_year", "code_base": "mhit",   "difference_method": "absolute", "description": "Mean annual count of events below 5 percent of mean flow."},
    "spr_freq": {"category": "frequency",      "units": "events_per_year", "code_base": "matlab", "difference_method": "absolute", "description": "Median spring (April-June) count of flow events above 10th percentile of full record."},
    "sum_freq": {"category": "frequency",      "units": "events_per_year", "code_base": "matlab", "difference_method": "absolute", "description": "Median summer (July-September) count of flow events below 90th percentile of full record."},
    # --- Rate of change ---
    "ra1":      {"category": "rate_of_change", "units": "cfs_per_day",     "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean rise rate: mean of positive daily flow changes."},
    "ra3":      {"category": "rate_of_change", "units": "cfs_per_day",     "code_base": "mhit",   "difference_method": "ratio",    "description": "Mean fall rate: mean of negative daily flow changes."},
    "ra8":      {"category": "rate_of_change", "units": "days_per_year",   "code_base": "mhit",   "difference_method": "ratio",    "description": "Median annual number of flow direction reversals."},
    # --- Timing ---
    "th1":      {"category": "timing",         "units": "julian_day",      "code_base": "mhit",   "difference_method": "absolute", "description": "Median Julian date of annual maximum flow."},
    "tl1":      {"category": "timing",         "units": "julian_day",      "code_base": "mhit",   "difference_method": "absolute", "description": "Median Julian date of annual minimum flow."},
    "spr_ord":  {"category": "timing",         "units": "julian_day",      "code_base": "matlab", "difference_method": "absolute", "description": "Median Julian date of spring (April-June) maximum flow."},
    "sum_ord":  {"category": "timing",         "units": "julian_day",      "code_base": "matlab", "difference_method": "absolute", "description": "Median Julian date of summer (July-September) minimum flow."},
}

STAT_NAMES = list(MHIT_STATS.keys())
