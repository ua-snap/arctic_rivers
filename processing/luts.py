# metadata for the daily climatology statistics
clim_var_dict = {
    "doy_min" : {
        "description" : "Minimum daily streamflow for day of year across all years in era",
        "units" : "cfs",
    },
    "doy_max" : {
        "description" : "Maximum daily streamflow for day of year across all years in era",
        "units" : "cfs",
    },
    "doy_mean" : {
        "description" : "Mean daily streamflow for day of year across all years in era",
        "units" : "cfs",
    },
}

# metadata for the monthly average statistics
stat_var_dict = {
        "ma12": {"month": 1, "description": "Mean of monthly flow values for January.", "units": "cfs"},
        "ma13": {"month": 2, "description": "Mean of monthly flow values for February.", "units": "cfs"},
        "ma14": {"month": 3, "description": "Mean of monthly flow values for March.", "units": "cfs"},
        "ma15": {"month": 4, "description": "Mean of monthly flow values for April.", "units": "cfs"},
        "ma16": {"month": 5, "description": "Mean of monthly flow values for May.", "units": "cfs"},
        "ma17": {"month": 6, "description": "Mean of monthly flow values for June.", "units": "cfs"},
        "ma18": {"month": 7, "description": "Mean of monthly flow values for July.", "units": "cfs"},
        "ma19": {"month": 8, "description": "Mean of monthly flow values for August.", "units": "cfs"},
        "ma20": {"month": 9, "description": "Mean of monthly flow values for September.", "units": "cfs"},
        "ma21": {"month": 10, "description": "Mean of monthly flow values for October.", "units": "cfs"},
        "ma22": {"month": 11, "description": "Mean of monthly flow values for November.", "units": "cfs"},
        "ma23": {"month": 12, "description": "Mean of monthly flow values for December.", "units": "cfs"},
    }


# encodings for netCDF, integers required for rasdaman ingest
encodings_lookup = {
    "model": {
        "C2LE2": 0,
        "C2LE4": 1,
        "C2LE7": 2,
        "C2LE9": 3,
        "historical": 4,
        "PGWh": 5,
        "PGWm": 6,
    },
    "era": {
        "1990_2021": 0,
        "2034_2065": 1,
    },
}
        

# reverse encodings for netCDF attributes
reverse_encodings_lookup = {
   
    "model": {
        0: "C2LE2",
        1: "C2LE4",
        2: "C2LE7",
        3: "C2LE9",
        4: "historical",
        5: "PGWh",
        6: "PGWm",
    },
    "era": {
        0: "1990_2021",
        1: "2034_2065",
    },
}

# information about the dataset itself
data_source_dict = {"Title":"Alaskan river discharge, temperature, and climate data for a climate reference (1990-2021) and at mid-century (2034-2065)",
                    "URL":"https://doi.org/10.18739/A25M62870",
                    "Description":"The Regional Arctic System Model, the combined Weather Research & Forecasting Model and the Community Terrestrial Systems Model for climate and land surface processes, mizuRoute for river routing, and the River Basin Model for river temperature, was used to generate high-resolution spatial and temporal data for 49 major Alaskan river basins. This modeling framework was applied to compare Alaskan hydrology between historical (1990-2021) and mid-century (2035-2064) periods across six future scenarios. These scenarios include six dynamically downscaled projections: two pseudo-global warming simulations based on historical meteorology, and four directly downscaled global climate models under the Shared Socioeconomic Pathway (SSP) SSP2-4.5 and SSP3-7.0 emission pathways. The climate data encompass variables such as snowpack, evapotranspiration, precipitation (rain and snow), groundwater, river temperature and discharge, as well as heat flux to the ocean.",
                    "Authors":"Dylan Blaskey, Keith Musselman, Andrew Newman, and Yifan Cheng",
                    "Date":"2024",
                    "Citation": "Dylan Blaskey, Keith Musselman, Andrew Newman, & Yifan Cheng. (2024). Alaskan river discharge, temperature, and climate data for a climate reference (1990-2021) and at mid-century (2034-2065). Arctic Data Center. doi:10.18739/A25M62870.",
                    }

# metadata about GCMs
gcm_metadata_dict = {"historical":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "ERA5 dynamically downscaled to 4km resolution",
                    "URL": "", #TODO: add URL if available
                    "Citation": "", #TODO: add Citation if available
                    },
                    "PGWh":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "", #TODO: add Description
                    "URL": "", #TODO: add URL if available
                    "Citation": "", #TODO: add Citation if available
                    },
                    "PGWm":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "", #TODO: add Description
                    "URL": "", #TODO: add URL if available
                    "Citation": "", #TODO: add Citation if available
                    },
                    "C2LE2":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "Downscaled CESM2-LE ensemble member 2, SSP3-7.0 scenario",
                    "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
                    "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bódai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393–1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
                    },
                    "C2LE4":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "Downscaled CESM2-LE ensemble member 4, SSP3-7.0 scenario",
                    "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
                    "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bódai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393–1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
                    },
                    "C2LE7":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "Downscaled CESM2-LE ensemble member 7, SSP3-7.0 scenario",
                    "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
                    "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bódai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393–1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
                    },
                    "C2LE9":
                    {"Modeling Center": "National Center for Atmospheric Research (NCAR)",
                    "Description": "Downscaled CESM2-LE ensemble member 9, SSP3-7.0 scenario",
                    "URL": "https://esd.copernicus.org/articles/12/1393/2021/",
                    "Citation": "Rodgers, K. B., Lee, S.-S., Rosenbloom, N., Timmermann, A., Danabasoglu, G., Deser, C., Edwards, J., Kim, J.-E., Simpson, I. R., Stein, K., Stuecker, M. F., Yamaguchi, R., Bódai, T., Chung, E.-S., Huang, L., Kim, W. M., Lamarque, J.-F., Lombardozzi, D. L., Wieder, W. R., and Yeager, S. G.: Ubiquity of human-induced changes in climate variability, Earth Syst. Dynam., 12, 1393–1411, https://doi.org/10.5194/esd-12-1393-2021, 2021.",
                    },
                    }