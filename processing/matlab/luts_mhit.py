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
    # ma99 is not an official MHIT variable — derived in add_ma99.py as mean(ma12-ma23)
    "ma99":     {"category": "magnitude",      "units": "cfs",             "code_base": "python", "difference_method": "ratio",    "description": "Mean annual flow: average of monthly mean flows (ma12-ma23)."},
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

DATA_SOURCE_DICT = {
    "Title": "Alaskan river discharge, temperature, and climate data for a climate reference (1990-2021) and at mid-century (2034-2065)",
    "URL": "https://doi.org/10.18739/A25M62870",
    "Description": "The Regional Arctic System Model, the combined Weather Research & Forecasting Model and the Community Terrestrial Systems Model for climate and land surface processes, mizuRoute for river routing, and the River Basin Model for river temperature, was used to generate high-resolution spatial and temporal data for 49 major Alaskan river basins. This modeling framework was applied to compare Alaskan hydrology between historical (1990-2021) and mid-century (2035-2064) periods across six future scenarios. These scenarios include six dynamically downscaled projections: two pseudo-global warming simulations based on historical meteorology, and four directly downscaled global climate models under the Shared Socioeconomic Pathway (SSP) SSP2-4.5 and SSP3-7.0 emission pathways. The climate data encompass variables such as snowpack, evapotranspiration, precipitation (rain and snow), groundwater, river temperature and discharge, as well as heat flux to the ocean.",
    "Authors": "Dylan Blaskey, Keith Musselman, Andrew Newman, and Yifan Cheng",
    "Date": "2024",
    "Citation": "Dylan Blaskey, Keith Musselman, Andrew Newman, & Yifan Cheng. (2024). Alaskan river discharge, temperature, and climate data for a climate reference (1990-2021) and at mid-century (2034-2065). Arctic Data Center. doi:10.18739/A25M62870.",
}

GCM_METADATA_DICT = {
    "historical": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "ERA5 dynamically downscaled to 4km resolution over Alaska and the Yukon River Basin (1990-2021) using the Regional Arctic Systems Model (RASM), with the Community Terrestrial Systems Model (CTSM) as the land component and WRF as the atmospheric component.",
        "URL": "https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2023WR036217",
        "Citation": "Blaskey, D., Gooseff, M., Cheng, Y., Newman, A., Koch, J. C., & Musselman, K. (2024). A high-resolution, daily hindcast (1990-2021) of Alaskan river discharge and temperature from coupled and optimized physical models. Water Resources Research, 60(4), e2023WR036217. https://doi.org/10.1029/2023WR036217",
    },
    "PGWh": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "High hydroclimate change scenario using the pseudo-global warming (PGW) method at 4km resolution over Alaska and the Yukon River Basin, representing mid-21st century (2035-2065) conditions. Derived from the mean perturbations of the 75th-100th percentile of SSP2-4.5 CMIP6 models.",
        "URL": "https://gdex.ucar.edu/datasets/d614000/",
        "Citation": "Cheng, Y., Craig, A., Musselman, K., Bennett, A., Seefeldt, M., Hamman, J., & Newman, A. J. (2024). Multi-decadal historical regional hydroclimate simulation with two mid 21st century Pseudo-Global Warming futures over Alaska and the Yukon at 4 km resolution. UCAR/NCAR - GDEX. https://doi.org/10.5065/ZPSB-PS82",
    },
    "PGWm": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "Median hydroclimate change scenario using the pseudo-global warming (PGW) method at 4km resolution over Alaska and the Yukon River Basin, representing mid-21st century (2035-2065) conditions. Derived from the mean perturbations of the 25th-75th percentile of SSP2-4.5 CMIP6 models.",
        "URL": "https://gdex.ucar.edu/datasets/d614000/",
        "Citation": "Cheng, Y., Craig, A., Musselman, K., Bennett, A., Seefeldt, M., Hamman, J., & Newman, A. J. (2024). Multi-decadal historical regional hydroclimate simulation with two mid 21st century Pseudo-Global Warming futures over Alaska and the Yukon at 4 km resolution. UCAR/NCAR - GDEX. https://doi.org/10.5065/ZPSB-PS82",
    },
    "C2LE2": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "Downscaled CESM2-LE ensemble member 2, SSP3-7.0 scenario",
        "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
        "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bodai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393-1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
    },
    "C2LE4": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "Downscaled CESM2-LE ensemble member 4, SSP3-7.0 scenario",
        "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
        "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bodai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393-1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
    },
    "C2LE7": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "Downscaled CESM2-LE ensemble member 7, SSP3-7.0 scenario",
        "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
        "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bodai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393-1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
    },
    "C2LE9": {
        "Modeling Center": "National Center for Atmospheric Research (NCAR)",
        "Description": "Downscaled CESM2-LE ensemble member 9, SSP3-7.0 scenario",
        "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
        "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bodai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393-1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
    },
}
