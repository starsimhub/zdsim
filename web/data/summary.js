window.ZDSIM_SUMMARY = {
  "data_file": "/Users/mine/git/zdsim/zdsim/data/zerodose_data_formated.xlsx",
  "population_assumption": null,
  "seed_reference": 42,
  "seed_intervention": 10042,
  "empirical_zerodose_proxy_dtp1": {
    "mean_zerodose_proxy": 0.1647298685507964,
    "std_zerodose_proxy": 0.06431024802344402,
    "mean_dtp1_coverage_proxy": 0.8352701314492037,
    "n_months": 84,
    "years_span": "2018-2024"
  },
  "calibration_base_bundle": {
    "seed": 42,
    "birth_rate": 25.0,
    "death_rate": 8.0,
    "household_contacts": 5,
    "community_contacts": 15,
    "diphtheria_beta": 0.15,
    "tetanus_beta": 0.02,
    "pertussis_beta": 0.25,
    "hepatitis_b_beta": 0.08,
    "hib_beta": 0.12,
    "diphtheria_init_p": 0.01,
    "tetanus_init_p": 0.001,
    "pertussis_init_p": 0.02,
    "hepatitis_b_init_p": 0.005,
    "hib_init_p": 0.01,
    "intervention_routine_prob": 0.03,
    "intervention_coverage": 0.8352701314492037,
    "intervention_efficacy": 0.9,
    "intervention_age_min": 0.0,
    "intervention_age_max": 60.0,
    "data_derived": {
      "demographics": {
        "population_used": null,
        "mean_annual_live_births_estimated": 4954514.678571428,
        "birth_rate_source": "default (set --population to calibrate birth_rate from estimated_lb)"
      },
      "intervention_coverage_from_mean_dtp1_proxy": true
    }
  },
  "calibration_reference_bundle": {
    "seed": 42,
    "birth_rate": 25.0,
    "death_rate": 8.0,
    "household_contacts": 5,
    "community_contacts": 15,
    "diphtheria_beta": 0.15,
    "tetanus_beta": 0.02,
    "pertussis_beta": 0.25,
    "hepatitis_b_beta": 0.08,
    "hib_beta": 0.12,
    "diphtheria_init_p": 0.01,
    "tetanus_init_p": 0.001,
    "pertussis_init_p": 0.02,
    "hepatitis_b_init_p": 0.005,
    "hib_init_p": 0.01,
    "intervention_routine_prob": 0.03461538461538462,
    "intervention_coverage": 0.8352701314492037,
    "intervention_efficacy": 0.9,
    "intervention_age_min": 0.0,
    "intervention_age_max": 60.0,
    "data_derived": {
      "demographics": {
        "population_used": null,
        "mean_annual_live_births_estimated": 4954514.678571428,
        "birth_rate_source": "default (set --population to calibrate birth_rate from estimated_lb)"
      },
      "intervention_coverage_from_mean_dtp1_proxy": true
    }
  },
  "calibration_scale_up_bundle": {
    "seed": 10042,
    "birth_rate": 25.0,
    "death_rate": 8.0,
    "household_contacts": 5,
    "community_contacts": 15,
    "diphtheria_beta": 0.15,
    "tetanus_beta": 0.02,
    "pertussis_beta": 0.25,
    "hepatitis_b_beta": 0.08,
    "hib_beta": 0.12,
    "diphtheria_init_p": 0.01,
    "tetanus_init_p": 0.001,
    "pertussis_init_p": 0.02,
    "hepatitis_b_init_p": 0.005,
    "hib_init_p": 0.01,
    "intervention_routine_prob": 0.07961538461538462,
    "intervention_coverage": 0.8552701314492037,
    "intervention_efficacy": 0.9,
    "intervention_age_min": 0.0,
    "intervention_age_max": 60.0,
    "data_derived": {
      "demographics": {
        "population_used": null,
        "mean_annual_live_births_estimated": 4954514.678571428,
        "birth_rate_source": "default (set --population to calibrate birth_rate from estimated_lb)"
      },
      "intervention_coverage_from_mean_dtp1_proxy": true
    }
  },
  "model_reference_routine_prob": 0.03461538461538462,
  "model_scale_up_routine_prob": 0.07961538461538462,
  "model_scale_up_coverage": 0.8552701314492037,
  "zero_dose_fraction_under5_model_reference": 0.15074074074074073,
  "zero_dose_fraction_under5_model_scale_up": 0.0695266272189349,
  "relative_reduction_percent_model": 53.87668464591542,
  "projection_calendar_start": 2025,
  "projection_calendar_stop": 2055,
  "projection_yearly_reference": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9713432835820895,
      "n_children_under5": 1675,
      "n_zero_dose_under5": 1627,
      "disease_attributable_deaths": 1976
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.29356789444749865,
      "n_children_under5": 1819,
      "n_zero_dose_under5": 534,
      "disease_attributable_deaths": 1654
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.1762252346193952,
      "n_children_under5": 1918,
      "n_zero_dose_under5": 338,
      "disease_attributable_deaths": 988
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.1570862239841427,
      "n_children_under5": 2018,
      "n_zero_dose_under5": 317,
      "disease_attributable_deaths": 587
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.1414141414141414,
      "n_children_under5": 2079,
      "n_zero_dose_under5": 294,
      "disease_attributable_deaths": 435
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.12523277467411545,
      "n_children_under5": 2148,
      "n_zero_dose_under5": 269,
      "disease_attributable_deaths": 323
    },
    {
      "calendar_year": 2031,
      "zerodose_under5_fraction": 0.13349397590361445,
      "n_children_under5": 2075,
      "n_zero_dose_under5": 277,
      "disease_attributable_deaths": 239
    },
    {
      "calendar_year": 2032,
      "zerodose_under5_fraction": 0.1315,
      "n_children_under5": 2000,
      "n_zero_dose_under5": 263,
      "disease_attributable_deaths": 137
    },
    {
      "calendar_year": 2033,
      "zerodose_under5_fraction": 0.13396127681841968,
      "n_children_under5": 1911,
      "n_zero_dose_under5": 256,
      "disease_attributable_deaths": 105
    },
    {
      "calendar_year": 2034,
      "zerodose_under5_fraction": 0.1421024828314844,
      "n_children_under5": 1893,
      "n_zero_dose_under5": 269,
      "disease_attributable_deaths": 69
    },
    {
      "calendar_year": 2035,
      "zerodose_under5_fraction": 0.13991552270327348,
      "n_children_under5": 1894,
      "n_zero_dose_under5": 265,
      "disease_attributable_deaths": 74
    },
    {
      "calendar_year": 2036,
      "zerodose_under5_fraction": 0.14218009478672985,
      "n_children_under5": 1899,
      "n_zero_dose_under5": 270,
      "disease_attributable_deaths": 49
    },
    {
      "calendar_year": 2037,
      "zerodose_under5_fraction": 0.1418953909891248,
      "n_children_under5": 1931,
      "n_zero_dose_under5": 274,
      "disease_attributable_deaths": 27
    },
    {
      "calendar_year": 2038,
      "zerodose_under5_fraction": 0.14,
      "n_children_under5": 1950,
      "n_zero_dose_under5": 273,
      "disease_attributable_deaths": 20
    },
    {
      "calendar_year": 2039,
      "zerodose_under5_fraction": 0.1400718317085685,
      "n_children_under5": 1949,
      "n_zero_dose_under5": 273,
      "disease_attributable_deaths": 16
    },
    {
      "calendar_year": 2040,
      "zerodose_under5_fraction": 0.1426372498717291,
      "n_children_under5": 1949,
      "n_zero_dose_under5": 278,
      "disease_attributable_deaths": 11
    },
    {
      "calendar_year": 2041,
      "zerodose_under5_fraction": 0.1426403641881639,
      "n_children_under5": 1977,
      "n_zero_dose_under5": 282,
      "disease_attributable_deaths": 17
    },
    {
      "calendar_year": 2042,
      "zerodose_under5_fraction": 0.14889434889434888,
      "n_children_under5": 2035,
      "n_zero_dose_under5": 303,
      "disease_attributable_deaths": 8
    },
    {
      "calendar_year": 2043,
      "zerodose_under5_fraction": 0.15526802218114602,
      "n_children_under5": 2164,
      "n_zero_dose_under5": 336,
      "disease_attributable_deaths": 15
    },
    {
      "calendar_year": 2044,
      "zerodose_under5_fraction": 0.14292114695340502,
      "n_children_under5": 2232,
      "n_zero_dose_under5": 319,
      "disease_attributable_deaths": 8
    },
    {
      "calendar_year": 2045,
      "zerodose_under5_fraction": 0.13990529487731382,
      "n_children_under5": 2323,
      "n_zero_dose_under5": 325,
      "disease_attributable_deaths": 13
    },
    {
      "calendar_year": 2046,
      "zerodose_under5_fraction": 0.13071065989847716,
      "n_children_under5": 2364,
      "n_zero_dose_under5": 309,
      "disease_attributable_deaths": 18
    },
    {
      "calendar_year": 2047,
      "zerodose_under5_fraction": 0.13858466722830665,
      "n_children_under5": 2374,
      "n_zero_dose_under5": 329,
      "disease_attributable_deaths": 22
    },
    {
      "calendar_year": 2048,
      "zerodose_under5_fraction": 0.1426131511528608,
      "n_children_under5": 2342,
      "n_zero_dose_under5": 334,
      "disease_attributable_deaths": 19
    },
    {
      "calendar_year": 2049,
      "zerodose_under5_fraction": 0.1351237935375577,
      "n_children_under5": 2383,
      "n_zero_dose_under5": 322,
      "disease_attributable_deaths": 29
    },
    {
      "calendar_year": 2050,
      "zerodose_under5_fraction": 0.13953488372093023,
      "n_children_under5": 2408,
      "n_zero_dose_under5": 336,
      "disease_attributable_deaths": 30
    },
    {
      "calendar_year": 2051,
      "zerodose_under5_fraction": 0.14946193702670388,
      "n_children_under5": 2509,
      "n_zero_dose_under5": 375,
      "disease_attributable_deaths": 22
    },
    {
      "calendar_year": 2052,
      "zerodose_under5_fraction": 0.14708171206225681,
      "n_children_under5": 2570,
      "n_zero_dose_under5": 378,
      "disease_attributable_deaths": 27
    },
    {
      "calendar_year": 2053,
      "zerodose_under5_fraction": 0.14204973624717407,
      "n_children_under5": 2654,
      "n_zero_dose_under5": 377,
      "disease_attributable_deaths": 32
    },
    {
      "calendar_year": 2054,
      "zerodose_under5_fraction": 0.134009009009009,
      "n_children_under5": 2664,
      "n_zero_dose_under5": 357,
      "disease_attributable_deaths": 34
    },
    {
      "calendar_year": 2055,
      "zerodose_under5_fraction": 0.1502954209748892,
      "n_children_under5": 2708,
      "n_zero_dose_under5": 407,
      "disease_attributable_deaths": 2
    }
  ],
  "projection_yearly_scale_up": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9319402985074627,
      "n_children_under5": 1675,
      "n_zero_dose_under5": 1561,
      "disease_attributable_deaths": 1979
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.09140969162995595,
      "n_children_under5": 1816,
      "n_zero_dose_under5": 166,
      "disease_attributable_deaths": 1636
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.0641158221302999,
      "n_children_under5": 1934,
      "n_zero_dose_under5": 124,
      "disease_attributable_deaths": 973
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.06500488758553274,
      "n_children_under5": 2046,
      "n_zero_dose_under5": 133,
      "disease_attributable_deaths": 610
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.053860819828408006,
      "n_children_under5": 2098,
      "n_zero_dose_under5": 113,
      "disease_attributable_deaths": 389
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.05139972464433226,
      "n_children_under5": 2179,
      "n_zero_dose_under5": 112,
      "disease_attributable_deaths": 315
    },
    {
      "calendar_year": 2031,
      "zerodose_under5_fraction": 0.05629770992366412,
      "n_children_under5": 2096,
      "n_zero_dose_under5": 118,
      "disease_attributable_deaths": 234
    },
    {
      "calendar_year": 2032,
      "zerodose_under5_fraction": 0.04975124378109453,
      "n_children_under5": 2010,
      "n_zero_dose_under5": 100,
      "disease_attributable_deaths": 120
    },
    {
      "calendar_year": 2033,
      "zerodose_under5_fraction": 0.05578512396694215,
      "n_children_under5": 1936,
      "n_zero_dose_under5": 108,
      "disease_attributable_deaths": 91
    },
    {
      "calendar_year": 2034,
      "zerodose_under5_fraction": 0.055031446540880505,
      "n_children_under5": 1908,
      "n_zero_dose_under5": 105,
      "disease_attributable_deaths": 94
    },
    {
      "calendar_year": 2035,
      "zerodose_under5_fraction": 0.056162246489859596,
      "n_children_under5": 1923,
      "n_zero_dose_under5": 108,
      "disease_attributable_deaths": 77
    },
    {
      "calendar_year": 2036,
      "zerodose_under5_fraction": 0.05867082035306334,
      "n_children_under5": 1926,
      "n_zero_dose_under5": 113,
      "disease_attributable_deaths": 40
    },
    {
      "calendar_year": 2037,
      "zerodose_under5_fraction": 0.055926115956900974,
      "n_children_under5": 1949,
      "n_zero_dose_under5": 109,
      "disease_attributable_deaths": 28
    },
    {
      "calendar_year": 2038,
      "zerodose_under5_fraction": 0.06539235412474849,
      "n_children_under5": 1988,
      "n_zero_dose_under5": 130,
      "disease_attributable_deaths": 19
    },
    {
      "calendar_year": 2039,
      "zerodose_under5_fraction": 0.05583250249252243,
      "n_children_under5": 2006,
      "n_zero_dose_under5": 112,
      "disease_attributable_deaths": 13
    },
    {
      "calendar_year": 2040,
      "zerodose_under5_fraction": 0.05958938407611417,
      "n_children_under5": 1997,
      "n_zero_dose_under5": 119,
      "disease_attributable_deaths": 4
    },
    {
      "calendar_year": 2041,
      "zerodose_under5_fraction": 0.060264576188143064,
      "n_children_under5": 2041,
      "n_zero_dose_under5": 123,
      "disease_attributable_deaths": 12
    },
    {
      "calendar_year": 2042,
      "zerodose_under5_fraction": 0.05921364282330649,
      "n_children_under5": 2111,
      "n_zero_dose_under5": 125,
      "disease_attributable_deaths": 9
    },
    {
      "calendar_year": 2043,
      "zerodose_under5_fraction": 0.0636568848758465,
      "n_children_under5": 2215,
      "n_zero_dose_under5": 141,
      "disease_attributable_deaths": 21
    },
    {
      "calendar_year": 2044,
      "zerodose_under5_fraction": 0.057466260339573354,
      "n_children_under5": 2297,
      "n_zero_dose_under5": 132,
      "disease_attributable_deaths": 14
    },
    {
      "calendar_year": 2045,
      "zerodose_under5_fraction": 0.055322715842414084,
      "n_children_under5": 2386,
      "n_zero_dose_under5": 132,
      "disease_attributable_deaths": 15
    },
    {
      "calendar_year": 2046,
      "zerodose_under5_fraction": 0.051143451143451146,
      "n_children_under5": 2405,
      "n_zero_dose_under5": 123,
      "disease_attributable_deaths": 17
    },
    {
      "calendar_year": 2047,
      "zerodose_under5_fraction": 0.058212058212058215,
      "n_children_under5": 2405,
      "n_zero_dose_under5": 140,
      "disease_attributable_deaths": 20
    },
    {
      "calendar_year": 2048,
      "zerodose_under5_fraction": 0.061738765224695506,
      "n_children_under5": 2381,
      "n_zero_dose_under5": 147,
      "disease_attributable_deaths": 18
    },
    {
      "calendar_year": 2049,
      "zerodose_under5_fraction": 0.05116472545757072,
      "n_children_under5": 2404,
      "n_zero_dose_under5": 123,
      "disease_attributable_deaths": 15
    },
    {
      "calendar_year": 2050,
      "zerodose_under5_fraction": 0.05457529749692244,
      "n_children_under5": 2437,
      "n_zero_dose_under5": 133,
      "disease_attributable_deaths": 26
    },
    {
      "calendar_year": 2051,
      "zerodose_under5_fraction": 0.06296733569460843,
      "n_children_under5": 2541,
      "n_zero_dose_under5": 160,
      "disease_attributable_deaths": 19
    },
    {
      "calendar_year": 2052,
      "zerodose_under5_fraction": 0.059276366435719784,
      "n_children_under5": 2598,
      "n_zero_dose_under5": 154,
      "disease_attributable_deaths": 25
    },
    {
      "calendar_year": 2053,
      "zerodose_under5_fraction": 0.06066314996232103,
      "n_children_under5": 2654,
      "n_zero_dose_under5": 161,
      "disease_attributable_deaths": 26
    },
    {
      "calendar_year": 2054,
      "zerodose_under5_fraction": 0.052020958083832336,
      "n_children_under5": 2672,
      "n_zero_dose_under5": 139,
      "disease_attributable_deaths": 29
    },
    {
      "calendar_year": 2055,
      "zerodose_under5_fraction": 0.06934710438952416,
      "n_children_under5": 2711,
      "n_zero_dose_under5": 188,
      "disease_attributable_deaths": 0
    }
  ],
  "projection_benefit_summary": {
    "projection_years": [
      2025,
      2026,
      2027,
      2028,
      2029,
      2030,
      2031,
      2032,
      2033,
      2034,
      2035,
      2036,
      2037,
      2038,
      2039,
      2040,
      2041,
      2042,
      2043,
      2044,
      2045,
      2046,
      2047,
      2048,
      2049,
      2050,
      2051,
      2052,
      2053,
      2054,
      2055
    ],
    "mean_annual_reduction_zerodose_share_pp": 8.67263884543581,
    "cumulative_zerodose_share_reduction_pp_years": 268.8518042085101,
    "sum_annual_zero_dose_children_gap": 5714.0
  },
  "projection_death_benefit_summary": {
    "projection_years": [
      2025,
      2026,
      2027,
      2028,
      2029,
      2030,
      2031,
      2032,
      2033,
      2034,
      2035,
      2036,
      2037,
      2038,
      2039,
      2040,
      2041,
      2042,
      2043,
      2044,
      2045,
      2046,
      2047,
      2048,
      2049,
      2050,
      2051,
      2052,
      2053,
      2054,
      2055
    ],
    "total_reference_deaths": 7006.0,
    "total_intervention_deaths": 6888.0,
    "total_deaths_averted": 118.0,
    "mean_annual_deaths_averted": 3.806451612903226
  },
  "projection_yearly_deaths_comparison": [
    {
      "calendar_year": 2025,
      "reference_deaths": 1976,
      "intervention_deaths": 1979,
      "deaths_averted": -3
    },
    {
      "calendar_year": 2026,
      "reference_deaths": 1654,
      "intervention_deaths": 1636,
      "deaths_averted": 18
    },
    {
      "calendar_year": 2027,
      "reference_deaths": 988,
      "intervention_deaths": 973,
      "deaths_averted": 15
    },
    {
      "calendar_year": 2028,
      "reference_deaths": 587,
      "intervention_deaths": 610,
      "deaths_averted": -23
    },
    {
      "calendar_year": 2029,
      "reference_deaths": 435,
      "intervention_deaths": 389,
      "deaths_averted": 46
    },
    {
      "calendar_year": 2030,
      "reference_deaths": 323,
      "intervention_deaths": 315,
      "deaths_averted": 8
    },
    {
      "calendar_year": 2031,
      "reference_deaths": 239,
      "intervention_deaths": 234,
      "deaths_averted": 5
    },
    {
      "calendar_year": 2032,
      "reference_deaths": 137,
      "intervention_deaths": 120,
      "deaths_averted": 17
    },
    {
      "calendar_year": 2033,
      "reference_deaths": 105,
      "intervention_deaths": 91,
      "deaths_averted": 14
    },
    {
      "calendar_year": 2034,
      "reference_deaths": 69,
      "intervention_deaths": 94,
      "deaths_averted": -25
    },
    {
      "calendar_year": 2035,
      "reference_deaths": 74,
      "intervention_deaths": 77,
      "deaths_averted": -3
    },
    {
      "calendar_year": 2036,
      "reference_deaths": 49,
      "intervention_deaths": 40,
      "deaths_averted": 9
    },
    {
      "calendar_year": 2037,
      "reference_deaths": 27,
      "intervention_deaths": 28,
      "deaths_averted": -1
    },
    {
      "calendar_year": 2038,
      "reference_deaths": 20,
      "intervention_deaths": 19,
      "deaths_averted": 1
    },
    {
      "calendar_year": 2039,
      "reference_deaths": 16,
      "intervention_deaths": 13,
      "deaths_averted": 3
    },
    {
      "calendar_year": 2040,
      "reference_deaths": 11,
      "intervention_deaths": 4,
      "deaths_averted": 7
    },
    {
      "calendar_year": 2041,
      "reference_deaths": 17,
      "intervention_deaths": 12,
      "deaths_averted": 5
    },
    {
      "calendar_year": 2042,
      "reference_deaths": 8,
      "intervention_deaths": 9,
      "deaths_averted": -1
    },
    {
      "calendar_year": 2043,
      "reference_deaths": 15,
      "intervention_deaths": 21,
      "deaths_averted": -6
    },
    {
      "calendar_year": 2044,
      "reference_deaths": 8,
      "intervention_deaths": 14,
      "deaths_averted": -6
    },
    {
      "calendar_year": 2045,
      "reference_deaths": 13,
      "intervention_deaths": 15,
      "deaths_averted": -2
    },
    {
      "calendar_year": 2046,
      "reference_deaths": 18,
      "intervention_deaths": 17,
      "deaths_averted": 1
    },
    {
      "calendar_year": 2047,
      "reference_deaths": 22,
      "intervention_deaths": 20,
      "deaths_averted": 2
    },
    {
      "calendar_year": 2048,
      "reference_deaths": 19,
      "intervention_deaths": 18,
      "deaths_averted": 1
    },
    {
      "calendar_year": 2049,
      "reference_deaths": 29,
      "intervention_deaths": 15,
      "deaths_averted": 14
    },
    {
      "calendar_year": 2050,
      "reference_deaths": 30,
      "intervention_deaths": 26,
      "deaths_averted": 4
    },
    {
      "calendar_year": 2051,
      "reference_deaths": 22,
      "intervention_deaths": 19,
      "deaths_averted": 3
    },
    {
      "calendar_year": 2052,
      "reference_deaths": 27,
      "intervention_deaths": 25,
      "deaths_averted": 2
    },
    {
      "calendar_year": 2053,
      "reference_deaths": 32,
      "intervention_deaths": 26,
      "deaths_averted": 6
    },
    {
      "calendar_year": 2054,
      "reference_deaths": 34,
      "intervention_deaths": 29,
      "deaths_averted": 5
    },
    {
      "calendar_year": 2055,
      "reference_deaths": 2,
      "intervention_deaths": 0,
      "deaths_averted": 2
    }
  ],
  "disease_deaths_note": "Counts are deaths attributed to pentavalent disease modules in the simulation (diphtheria, tetanus, pertussis, hepatitis B, Hib), not all-cause mortality. Yearly totals are stochastic; with few agents or short runs, cumulative \u201caverted\u201d deaths can occasionally be negative\u2014in that case prefer longer projections, larger n_agents, or multiple seeds.",
  "n_agents": 20000,
  "years": 30,
  "who_context_url": "https://www.who.int/news-room/fact-sheets/detail/immunization-coverage",
  "calibration_short_run_years": 8,
  "calibration_short_run_agents": 10000,
  "research_question_tetanus": {
    "question": "How many tetanus cases will be averted if we reduce prevalence of zero-dose vaccination by 50% among under-fives by the year 2025?",
    "modeled_answer": {
      "metric": "new_tetanus_infections_in_simulated_cohort",
      "reference_total": 18621.0,
      "intervention_total": 18393.0,
      "tetanus_cases_averted_total": 228.0,
      "by_calendar_year": [
        {
          "calendar_year": 2025,
          "reference_tetanus_cases": 7319.0,
          "intervention_tetanus_cases": 7284.0,
          "tetanus_cases_averted": 35.0
        },
        {
          "calendar_year": 2026,
          "reference_tetanus_cases": 4007.0,
          "intervention_tetanus_cases": 3997.0,
          "tetanus_cases_averted": 10.0
        },
        {
          "calendar_year": 2027,
          "reference_tetanus_cases": 2271.0,
          "intervention_tetanus_cases": 2237.0,
          "tetanus_cases_averted": 34.0
        },
        {
          "calendar_year": 2028,
          "reference_tetanus_cases": 1349.0,
          "intervention_tetanus_cases": 1349.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2029,
          "reference_tetanus_cases": 853.0,
          "intervention_tetanus_cases": 817.0,
          "tetanus_cases_averted": 36.0
        },
        {
          "calendar_year": 2030,
          "reference_tetanus_cases": 558.0,
          "intervention_tetanus_cases": 555.0,
          "tetanus_cases_averted": 3.0
        },
        {
          "calendar_year": 2031,
          "reference_tetanus_cases": 418.0,
          "intervention_tetanus_cases": 404.0,
          "tetanus_cases_averted": 14.0
        },
        {
          "calendar_year": 2032,
          "reference_tetanus_cases": 318.0,
          "intervention_tetanus_cases": 272.0,
          "tetanus_cases_averted": 46.0
        },
        {
          "calendar_year": 2033,
          "reference_tetanus_cases": 254.0,
          "intervention_tetanus_cases": 260.0,
          "tetanus_cases_averted": -6.0
        },
        {
          "calendar_year": 2034,
          "reference_tetanus_cases": 218.0,
          "intervention_tetanus_cases": 257.0,
          "tetanus_cases_averted": -39.0
        },
        {
          "calendar_year": 2035,
          "reference_tetanus_cases": 200.0,
          "intervention_tetanus_cases": 189.0,
          "tetanus_cases_averted": 11.0
        },
        {
          "calendar_year": 2036,
          "reference_tetanus_cases": 134.0,
          "intervention_tetanus_cases": 113.0,
          "tetanus_cases_averted": 21.0
        },
        {
          "calendar_year": 2037,
          "reference_tetanus_cases": 81.0,
          "intervention_tetanus_cases": 55.0,
          "tetanus_cases_averted": 26.0
        },
        {
          "calendar_year": 2038,
          "reference_tetanus_cases": 52.0,
          "intervention_tetanus_cases": 51.0,
          "tetanus_cases_averted": 1.0
        },
        {
          "calendar_year": 2039,
          "reference_tetanus_cases": 38.0,
          "intervention_tetanus_cases": 16.0,
          "tetanus_cases_averted": 22.0
        },
        {
          "calendar_year": 2040,
          "reference_tetanus_cases": 17.0,
          "intervention_tetanus_cases": 17.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2041,
          "reference_tetanus_cases": 20.0,
          "intervention_tetanus_cases": 20.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2042,
          "reference_tetanus_cases": 15.0,
          "intervention_tetanus_cases": 21.0,
          "tetanus_cases_averted": -6.0
        },
        {
          "calendar_year": 2043,
          "reference_tetanus_cases": 28.0,
          "intervention_tetanus_cases": 26.0,
          "tetanus_cases_averted": 2.0
        },
        {
          "calendar_year": 2044,
          "reference_tetanus_cases": 27.0,
          "intervention_tetanus_cases": 31.0,
          "tetanus_cases_averted": -4.0
        },
        {
          "calendar_year": 2045,
          "reference_tetanus_cases": 24.0,
          "intervention_tetanus_cases": 32.0,
          "tetanus_cases_averted": -8.0
        },
        {
          "calendar_year": 2046,
          "reference_tetanus_cases": 39.0,
          "intervention_tetanus_cases": 28.0,
          "tetanus_cases_averted": 11.0
        },
        {
          "calendar_year": 2047,
          "reference_tetanus_cases": 37.0,
          "intervention_tetanus_cases": 32.0,
          "tetanus_cases_averted": 5.0
        },
        {
          "calendar_year": 2048,
          "reference_tetanus_cases": 43.0,
          "intervention_tetanus_cases": 36.0,
          "tetanus_cases_averted": 7.0
        },
        {
          "calendar_year": 2049,
          "reference_tetanus_cases": 42.0,
          "intervention_tetanus_cases": 46.0,
          "tetanus_cases_averted": -4.0
        },
        {
          "calendar_year": 2050,
          "reference_tetanus_cases": 50.0,
          "intervention_tetanus_cases": 43.0,
          "tetanus_cases_averted": 7.0
        },
        {
          "calendar_year": 2051,
          "reference_tetanus_cases": 52.0,
          "intervention_tetanus_cases": 48.0,
          "tetanus_cases_averted": 4.0
        },
        {
          "calendar_year": 2052,
          "reference_tetanus_cases": 52.0,
          "intervention_tetanus_cases": 52.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2053,
          "reference_tetanus_cases": 52.0,
          "intervention_tetanus_cases": 52.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2054,
          "reference_tetanus_cases": 52.0,
          "intervention_tetanus_cases": 52.0,
          "tetanus_cases_averted": 0.0
        },
        {
          "calendar_year": 2055,
          "reference_tetanus_cases": 1.0,
          "intervention_tetanus_cases": 1.0,
          "tetanus_cases_averted": 0.0
        }
      ],
      "modeled_zero_dose_relative_reduction_percent_end_window": 53.87668464591542,
      "tetanus_cases_averted_calendar_year_2025": 35.0,
      "reference_tetanus_cases_calendar_year_2025": 7319.0,
      "intervention_tetanus_cases_calendar_year_2025": 7284.0
    },
    "interpretation": "New tetanus infections are from the Starsim tetanus module (not national statistics). They depend on n_agents. By default both arms use the same RNG seed (fair counterfactual); if you pass --seed-intervention with a different value, arms are independent and averted counts can be noisy or negative. Modeled ZD reduction is in modeled_zero_dose_relative_reduction_percent_end_window (not fixed at 50%)."
  }
};
