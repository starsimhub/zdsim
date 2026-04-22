window.ZDSIM_SUMMARY = {
  "data_file": "/Users/mine/git/zdsim/zdsim/data/zerodose_data_formated.xlsx",
  "population_assumption": null,
  "calibration_source": "/Users/mine/git/zdsim/calibration.port.json",
  "seed_reference": 42,
  "seed_intervention": 42,
  "empirical_zerodose_proxy_dtp1": {
    "mean_zerodose_proxy": 0.1647298685507964,
    "std_zerodose_proxy": 0.06431024802344402,
    "mean_dtp1_coverage_proxy": 0.8352701314492037,
    "n_months": 84,
    "years_span": "2018-2024"
  },
  "calibration_reference_bundle": {
    "seed": 42,
    "birth_rate": 25.0,
    "death_rate": 8.0,
    "household_contacts": 5,
    "community_contacts": 15,
    "diphtheria_beta": 0.15,
    "pertussis_beta": 0.25,
    "hepatitis_b_beta": 0.08,
    "hib_beta": 0.12,
    "diphtheria_init_p": 0.01,
    "tetanus_init_p": 0.001,
    "pertussis_init_p": 0.02,
    "hepatitis_b_init_p": 0.005,
    "hib_init_p": 0.01,
    "intervention_routine_prob": 0.029076923076923077,
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
    "seed": 42,
    "birth_rate": 25.0,
    "death_rate": 8.0,
    "household_contacts": 5,
    "community_contacts": 15,
    "diphtheria_beta": 0.15,
    "pertussis_beta": 0.25,
    "hepatitis_b_beta": 0.08,
    "hib_beta": 0.12,
    "diphtheria_init_p": 0.01,
    "tetanus_init_p": 0.001,
    "pertussis_init_p": 0.02,
    "hepatitis_b_init_p": 0.005,
    "hib_init_p": 0.01,
    "intervention_routine_prob": 0.06687692307692307,
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
  "model_reference_routine_prob": 0.029076923076923077,
  "model_scale_up_routine_prob": 0.06687692307692307,
  "model_scale_up_coverage": 0.8552701314492037,
  "zero_dose_fraction_under5_model_reference": 0.17037037037037037,
  "zero_dose_fraction_under5_model_scale_up": 0.08031674208144797,
  "relative_reduction_percent_model": 52.85756443045445,
  "projection_calendar_start": 2025,
  "projection_calendar_stop": 2055,
  "projection_yearly_reference": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9744640447753735,
      "n_children_under5": 20011,
      "n_zero_dose_under5": 19500,
      "disease_attributable_deaths": 384
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.28012179208351456,
      "n_children_under5": 16093,
      "n_zero_dose_under5": 4508,
      "disease_attributable_deaths": 241
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.0893230422897572,
      "n_children_under5": 12438,
      "n_zero_dose_under5": 1111,
      "disease_attributable_deaths": 181
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.05409308008441631,
      "n_children_under5": 9003,
      "n_zero_dose_under5": 487,
      "disease_attributable_deaths": 184
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.07018488601687309,
      "n_children_under5": 5571,
      "n_zero_dose_under5": 391,
      "disease_attributable_deaths": 269
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.17612442202606138,
      "n_children_under5": 2379,
      "n_zero_dose_under5": 419,
      "disease_attributable_deaths": 265
    },
    {
      "calendar_year": 2031,
      "zerodose_under5_fraction": 0.17360235393022277,
      "n_children_under5": 2379,
      "n_zero_dose_under5": 413,
      "disease_attributable_deaths": 254
    },
    {
      "calendar_year": 2032,
      "zerodose_under5_fraction": 0.15606694560669457,
      "n_children_under5": 2390,
      "n_zero_dose_under5": 373,
      "disease_attributable_deaths": 216
    },
    {
      "calendar_year": 2033,
      "zerodose_under5_fraction": 0.15945611866501855,
      "n_children_under5": 2427,
      "n_zero_dose_under5": 387,
      "disease_attributable_deaths": 186
    },
    {
      "calendar_year": 2034,
      "zerodose_under5_fraction": 0.15381460213289583,
      "n_children_under5": 2438,
      "n_zero_dose_under5": 375,
      "disease_attributable_deaths": 201
    },
    {
      "calendar_year": 2035,
      "zerodose_under5_fraction": 0.1608222490931076,
      "n_children_under5": 2481,
      "n_zero_dose_under5": 399,
      "disease_attributable_deaths": 261
    },
    {
      "calendar_year": 2036,
      "zerodose_under5_fraction": 0.1594320486815416,
      "n_children_under5": 2465,
      "n_zero_dose_under5": 393,
      "disease_attributable_deaths": 417
    },
    {
      "calendar_year": 2037,
      "zerodose_under5_fraction": 0.16799046862589356,
      "n_children_under5": 2518,
      "n_zero_dose_under5": 423,
      "disease_attributable_deaths": 461
    },
    {
      "calendar_year": 2038,
      "zerodose_under5_fraction": 0.17285881892843175,
      "n_children_under5": 2557,
      "n_zero_dose_under5": 442,
      "disease_attributable_deaths": 498
    },
    {
      "calendar_year": 2039,
      "zerodose_under5_fraction": 0.1482362267142291,
      "n_children_under5": 2523,
      "n_zero_dose_under5": 374,
      "disease_attributable_deaths": 530
    },
    {
      "calendar_year": 2040,
      "zerodose_under5_fraction": 0.15387689848121502,
      "n_children_under5": 2502,
      "n_zero_dose_under5": 385,
      "disease_attributable_deaths": 524
    },
    {
      "calendar_year": 2041,
      "zerodose_under5_fraction": 0.15430861723446893,
      "n_children_under5": 2495,
      "n_zero_dose_under5": 385,
      "disease_attributable_deaths": 452
    },
    {
      "calendar_year": 2042,
      "zerodose_under5_fraction": 0.16022544283413848,
      "n_children_under5": 2484,
      "n_zero_dose_under5": 398,
      "disease_attributable_deaths": 372
    },
    {
      "calendar_year": 2043,
      "zerodose_under5_fraction": 0.1565362198168193,
      "n_children_under5": 2402,
      "n_zero_dose_under5": 376,
      "disease_attributable_deaths": 343
    },
    {
      "calendar_year": 2044,
      "zerodose_under5_fraction": 0.17772317772317772,
      "n_children_under5": 2442,
      "n_zero_dose_under5": 434,
      "disease_attributable_deaths": 305
    },
    {
      "calendar_year": 2045,
      "zerodose_under5_fraction": 0.1638349514563107,
      "n_children_under5": 2472,
      "n_zero_dose_under5": 405,
      "disease_attributable_deaths": 277
    },
    {
      "calendar_year": 2046,
      "zerodose_under5_fraction": 0.16126450580232093,
      "n_children_under5": 2499,
      "n_zero_dose_under5": 403,
      "disease_attributable_deaths": 256
    },
    {
      "calendar_year": 2047,
      "zerodose_under5_fraction": 0.15810920945395274,
      "n_children_under5": 2454,
      "n_zero_dose_under5": 388,
      "disease_attributable_deaths": 236
    },
    {
      "calendar_year": 2048,
      "zerodose_under5_fraction": 0.16183574879227053,
      "n_children_under5": 2484,
      "n_zero_dose_under5": 402,
      "disease_attributable_deaths": 251
    },
    {
      "calendar_year": 2049,
      "zerodose_under5_fraction": 0.15692684920310584,
      "n_children_under5": 2447,
      "n_zero_dose_under5": 384,
      "disease_attributable_deaths": 243
    },
    {
      "calendar_year": 2050,
      "zerodose_under5_fraction": 0.16306563391765186,
      "n_children_under5": 2453,
      "n_zero_dose_under5": 400,
      "disease_attributable_deaths": 234
    },
    {
      "calendar_year": 2051,
      "zerodose_under5_fraction": 0.1791290057518488,
      "n_children_under5": 2434,
      "n_zero_dose_under5": 436,
      "disease_attributable_deaths": 226
    },
    {
      "calendar_year": 2052,
      "zerodose_under5_fraction": 0.16408422725466826,
      "n_children_under5": 2517,
      "n_zero_dose_under5": 413,
      "disease_attributable_deaths": 193
    },
    {
      "calendar_year": 2053,
      "zerodose_under5_fraction": 0.1585318235064428,
      "n_children_under5": 2561,
      "n_zero_dose_under5": 406,
      "disease_attributable_deaths": 230
    },
    {
      "calendar_year": 2054,
      "zerodose_under5_fraction": 0.1469435736677116,
      "n_children_under5": 2552,
      "n_zero_dose_under5": 375,
      "disease_attributable_deaths": 194
    },
    {
      "calendar_year": 2055,
      "zerodose_under5_fraction": 0.17003891050583658,
      "n_children_under5": 2570,
      "n_zero_dose_under5": 437,
      "disease_attributable_deaths": 4
    }
  ],
  "projection_yearly_scale_up": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9429313877367448,
      "n_children_under5": 20011,
      "n_zero_dose_under5": 18869,
      "disease_attributable_deaths": 268
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.050898758416208535,
      "n_children_under5": 16189,
      "n_zero_dose_under5": 824,
      "disease_attributable_deaths": 106
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.012307447991106876,
      "n_children_under5": 12594,
      "n_zero_dose_under5": 155,
      "disease_attributable_deaths": 121
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.01739225552395537,
      "n_children_under5": 9142,
      "n_zero_dose_under5": 159,
      "disease_attributable_deaths": 153
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.029006013441811106,
      "n_children_under5": 5654,
      "n_zero_dose_under5": 164,
      "disease_attributable_deaths": 224
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.0759493670886076,
      "n_children_under5": 2449,
      "n_zero_dose_under5": 186,
      "disease_attributable_deaths": 263
    },
    {
      "calendar_year": 2031,
      "zerodose_under5_fraction": 0.07031888798037612,
      "n_children_under5": 2446,
      "n_zero_dose_under5": 172,
      "disease_attributable_deaths": 240
    },
    {
      "calendar_year": 2032,
      "zerodose_under5_fraction": 0.06836569579288027,
      "n_children_under5": 2472,
      "n_zero_dose_under5": 169,
      "disease_attributable_deaths": 201
    },
    {
      "calendar_year": 2033,
      "zerodose_under5_fraction": 0.06322529011604641,
      "n_children_under5": 2499,
      "n_zero_dose_under5": 158,
      "disease_attributable_deaths": 184
    },
    {
      "calendar_year": 2034,
      "zerodose_under5_fraction": 0.06582077716098335,
      "n_children_under5": 2522,
      "n_zero_dose_under5": 166,
      "disease_attributable_deaths": 197
    },
    {
      "calendar_year": 2035,
      "zerodose_under5_fraction": 0.06598586017282011,
      "n_children_under5": 2546,
      "n_zero_dose_under5": 168,
      "disease_attributable_deaths": 237
    },
    {
      "calendar_year": 2036,
      "zerodose_under5_fraction": 0.06845003933910307,
      "n_children_under5": 2542,
      "n_zero_dose_under5": 174,
      "disease_attributable_deaths": 380
    },
    {
      "calendar_year": 2037,
      "zerodose_under5_fraction": 0.07084785133565621,
      "n_children_under5": 2583,
      "n_zero_dose_under5": 183,
      "disease_attributable_deaths": 468
    },
    {
      "calendar_year": 2038,
      "zerodose_under5_fraction": 0.07599243856332703,
      "n_children_under5": 2645,
      "n_zero_dose_under5": 201,
      "disease_attributable_deaths": 494
    },
    {
      "calendar_year": 2039,
      "zerodose_under5_fraction": 0.059049079754601226,
      "n_children_under5": 2608,
      "n_zero_dose_under5": 154,
      "disease_attributable_deaths": 583
    },
    {
      "calendar_year": 2040,
      "zerodose_under5_fraction": 0.0693752395553852,
      "n_children_under5": 2609,
      "n_zero_dose_under5": 181,
      "disease_attributable_deaths": 551
    },
    {
      "calendar_year": 2041,
      "zerodose_under5_fraction": 0.06525911708253358,
      "n_children_under5": 2605,
      "n_zero_dose_under5": 170,
      "disease_attributable_deaths": 503
    },
    {
      "calendar_year": 2042,
      "zerodose_under5_fraction": 0.06556112610875434,
      "n_children_under5": 2593,
      "n_zero_dose_under5": 170,
      "disease_attributable_deaths": 402
    },
    {
      "calendar_year": 2043,
      "zerodose_under5_fraction": 0.06204963971176942,
      "n_children_under5": 2498,
      "n_zero_dose_under5": 155,
      "disease_attributable_deaths": 340
    },
    {
      "calendar_year": 2044,
      "zerodose_under5_fraction": 0.06463124504361618,
      "n_children_under5": 2522,
      "n_zero_dose_under5": 163,
      "disease_attributable_deaths": 319
    },
    {
      "calendar_year": 2045,
      "zerodose_under5_fraction": 0.07100823852491173,
      "n_children_under5": 2549,
      "n_zero_dose_under5": 181,
      "disease_attributable_deaths": 297
    },
    {
      "calendar_year": 2046,
      "zerodose_under5_fraction": 0.07381232822928936,
      "n_children_under5": 2547,
      "n_zero_dose_under5": 188,
      "disease_attributable_deaths": 269
    },
    {
      "calendar_year": 2047,
      "zerodose_under5_fraction": 0.0686626746506986,
      "n_children_under5": 2505,
      "n_zero_dose_under5": 172,
      "disease_attributable_deaths": 249
    },
    {
      "calendar_year": 2048,
      "zerodose_under5_fraction": 0.06590370955011839,
      "n_children_under5": 2534,
      "n_zero_dose_under5": 167,
      "disease_attributable_deaths": 245
    },
    {
      "calendar_year": 2049,
      "zerodose_under5_fraction": 0.0656704679512387,
      "n_children_under5": 2543,
      "n_zero_dose_under5": 167,
      "disease_attributable_deaths": 263
    },
    {
      "calendar_year": 2050,
      "zerodose_under5_fraction": 0.07094728497820056,
      "n_children_under5": 2523,
      "n_zero_dose_under5": 179,
      "disease_attributable_deaths": 254
    },
    {
      "calendar_year": 2051,
      "zerodose_under5_fraction": 0.0626984126984127,
      "n_children_under5": 2520,
      "n_zero_dose_under5": 158,
      "disease_attributable_deaths": 234
    },
    {
      "calendar_year": 2052,
      "zerodose_under5_fraction": 0.06725595695618755,
      "n_children_under5": 2602,
      "n_zero_dose_under5": 175,
      "disease_attributable_deaths": 212
    },
    {
      "calendar_year": 2053,
      "zerodose_under5_fraction": 0.0605831124574025,
      "n_children_under5": 2641,
      "n_zero_dose_under5": 160,
      "disease_attributable_deaths": 222
    },
    {
      "calendar_year": 2054,
      "zerodose_under5_fraction": 0.05688282138794084,
      "n_children_under5": 2637,
      "n_zero_dose_under5": 150,
      "disease_attributable_deaths": 242
    },
    {
      "calendar_year": 2055,
      "zerodose_under5_fraction": 0.08016560030109146,
      "n_children_under5": 2657,
      "n_zero_dose_under5": 213,
      "disease_attributable_deaths": 7
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
    "mean_annual_reduction_zerodose_share_pp": 9.277476675658686,
    "cumulative_zerodose_share_reduction_pp_years": 287.60177694541926,
    "sum_annual_zero_dose_children_gap": 11771.0
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
    "total_reference_deaths": 8888.0,
    "total_intervention_deaths": 8728.0,
    "total_deaths_averted": 160.0,
    "mean_annual_deaths_averted": 5.161290322580645
  },
  "projection_yearly_deaths_comparison": [
    {
      "calendar_year": 2025,
      "reference_deaths": 384,
      "intervention_deaths": 268,
      "deaths_averted": 116
    },
    {
      "calendar_year": 2026,
      "reference_deaths": 241,
      "intervention_deaths": 106,
      "deaths_averted": 135
    },
    {
      "calendar_year": 2027,
      "reference_deaths": 181,
      "intervention_deaths": 121,
      "deaths_averted": 60
    },
    {
      "calendar_year": 2028,
      "reference_deaths": 184,
      "intervention_deaths": 153,
      "deaths_averted": 31
    },
    {
      "calendar_year": 2029,
      "reference_deaths": 269,
      "intervention_deaths": 224,
      "deaths_averted": 45
    },
    {
      "calendar_year": 2030,
      "reference_deaths": 265,
      "intervention_deaths": 263,
      "deaths_averted": 2
    },
    {
      "calendar_year": 2031,
      "reference_deaths": 254,
      "intervention_deaths": 240,
      "deaths_averted": 14
    },
    {
      "calendar_year": 2032,
      "reference_deaths": 216,
      "intervention_deaths": 201,
      "deaths_averted": 15
    },
    {
      "calendar_year": 2033,
      "reference_deaths": 186,
      "intervention_deaths": 184,
      "deaths_averted": 2
    },
    {
      "calendar_year": 2034,
      "reference_deaths": 201,
      "intervention_deaths": 197,
      "deaths_averted": 4
    },
    {
      "calendar_year": 2035,
      "reference_deaths": 261,
      "intervention_deaths": 237,
      "deaths_averted": 24
    },
    {
      "calendar_year": 2036,
      "reference_deaths": 417,
      "intervention_deaths": 380,
      "deaths_averted": 37
    },
    {
      "calendar_year": 2037,
      "reference_deaths": 461,
      "intervention_deaths": 468,
      "deaths_averted": -7
    },
    {
      "calendar_year": 2038,
      "reference_deaths": 498,
      "intervention_deaths": 494,
      "deaths_averted": 4
    },
    {
      "calendar_year": 2039,
      "reference_deaths": 530,
      "intervention_deaths": 583,
      "deaths_averted": -53
    },
    {
      "calendar_year": 2040,
      "reference_deaths": 524,
      "intervention_deaths": 551,
      "deaths_averted": -27
    },
    {
      "calendar_year": 2041,
      "reference_deaths": 452,
      "intervention_deaths": 503,
      "deaths_averted": -51
    },
    {
      "calendar_year": 2042,
      "reference_deaths": 372,
      "intervention_deaths": 402,
      "deaths_averted": -30
    },
    {
      "calendar_year": 2043,
      "reference_deaths": 343,
      "intervention_deaths": 340,
      "deaths_averted": 3
    },
    {
      "calendar_year": 2044,
      "reference_deaths": 305,
      "intervention_deaths": 319,
      "deaths_averted": -14
    },
    {
      "calendar_year": 2045,
      "reference_deaths": 277,
      "intervention_deaths": 297,
      "deaths_averted": -20
    },
    {
      "calendar_year": 2046,
      "reference_deaths": 256,
      "intervention_deaths": 269,
      "deaths_averted": -13
    },
    {
      "calendar_year": 2047,
      "reference_deaths": 236,
      "intervention_deaths": 249,
      "deaths_averted": -13
    },
    {
      "calendar_year": 2048,
      "reference_deaths": 251,
      "intervention_deaths": 245,
      "deaths_averted": 6
    },
    {
      "calendar_year": 2049,
      "reference_deaths": 243,
      "intervention_deaths": 263,
      "deaths_averted": -20
    },
    {
      "calendar_year": 2050,
      "reference_deaths": 234,
      "intervention_deaths": 254,
      "deaths_averted": -20
    },
    {
      "calendar_year": 2051,
      "reference_deaths": 226,
      "intervention_deaths": 234,
      "deaths_averted": -8
    },
    {
      "calendar_year": 2052,
      "reference_deaths": 193,
      "intervention_deaths": 212,
      "deaths_averted": -19
    },
    {
      "calendar_year": 2053,
      "reference_deaths": 230,
      "intervention_deaths": 222,
      "deaths_averted": 8
    },
    {
      "calendar_year": 2054,
      "reference_deaths": 194,
      "intervention_deaths": 242,
      "deaths_averted": -48
    },
    {
      "calendar_year": 2055,
      "reference_deaths": 4,
      "intervention_deaths": 7,
      "deaths_averted": -3
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
      "reference_total": 22323.0,
      "intervention_total": 22117.0,
      "tetanus_cases_averted_total": 206.0,
      "by_calendar_year": [
        {
          "calendar_year": 2025,
          "reference_tetanus_cases": 787.0,
          "intervention_tetanus_cases": 513.0,
          "tetanus_cases_averted": 274.0
        },
        {
          "calendar_year": 2026,
          "reference_tetanus_cases": 410.0,
          "intervention_tetanus_cases": 216.0,
          "tetanus_cases_averted": 194.0
        },
        {
          "calendar_year": 2027,
          "reference_tetanus_cases": 343.0,
          "intervention_tetanus_cases": 263.0,
          "tetanus_cases_averted": 80.0
        },
        {
          "calendar_year": 2028,
          "reference_tetanus_cases": 373.0,
          "intervention_tetanus_cases": 289.0,
          "tetanus_cases_averted": 84.0
        },
        {
          "calendar_year": 2029,
          "reference_tetanus_cases": 356.0,
          "intervention_tetanus_cases": 291.0,
          "tetanus_cases_averted": 65.0
        },
        {
          "calendar_year": 2030,
          "reference_tetanus_cases": 321.0,
          "intervention_tetanus_cases": 284.0,
          "tetanus_cases_averted": 37.0
        },
        {
          "calendar_year": 2031,
          "reference_tetanus_cases": 385.0,
          "intervention_tetanus_cases": 338.0,
          "tetanus_cases_averted": 47.0
        },
        {
          "calendar_year": 2032,
          "reference_tetanus_cases": 387.0,
          "intervention_tetanus_cases": 346.0,
          "tetanus_cases_averted": 41.0
        },
        {
          "calendar_year": 2033,
          "reference_tetanus_cases": 363.0,
          "intervention_tetanus_cases": 348.0,
          "tetanus_cases_averted": 15.0
        },
        {
          "calendar_year": 2034,
          "reference_tetanus_cases": 399.0,
          "intervention_tetanus_cases": 373.0,
          "tetanus_cases_averted": 26.0
        },
        {
          "calendar_year": 2035,
          "reference_tetanus_cases": 805.0,
          "intervention_tetanus_cases": 715.0,
          "tetanus_cases_averted": 90.0
        },
        {
          "calendar_year": 2036,
          "reference_tetanus_cases": 1132.0,
          "intervention_tetanus_cases": 1043.0,
          "tetanus_cases_averted": 89.0
        },
        {
          "calendar_year": 2037,
          "reference_tetanus_cases": 1305.0,
          "intervention_tetanus_cases": 1312.0,
          "tetanus_cases_averted": -7.0
        },
        {
          "calendar_year": 2038,
          "reference_tetanus_cases": 1471.0,
          "intervention_tetanus_cases": 1516.0,
          "tetanus_cases_averted": -45.0
        },
        {
          "calendar_year": 2039,
          "reference_tetanus_cases": 1605.0,
          "intervention_tetanus_cases": 1697.0,
          "tetanus_cases_averted": -92.0
        },
        {
          "calendar_year": 2040,
          "reference_tetanus_cases": 1475.0,
          "intervention_tetanus_cases": 1584.0,
          "tetanus_cases_averted": -109.0
        },
        {
          "calendar_year": 2041,
          "reference_tetanus_cases": 1262.0,
          "intervention_tetanus_cases": 1360.0,
          "tetanus_cases_averted": -98.0
        },
        {
          "calendar_year": 2042,
          "reference_tetanus_cases": 1016.0,
          "intervention_tetanus_cases": 1105.0,
          "tetanus_cases_averted": -89.0
        },
        {
          "calendar_year": 2043,
          "reference_tetanus_cases": 967.0,
          "intervention_tetanus_cases": 988.0,
          "tetanus_cases_averted": -21.0
        },
        {
          "calendar_year": 2044,
          "reference_tetanus_cases": 817.0,
          "intervention_tetanus_cases": 885.0,
          "tetanus_cases_averted": -68.0
        },
        {
          "calendar_year": 2045,
          "reference_tetanus_cases": 748.0,
          "intervention_tetanus_cases": 783.0,
          "tetanus_cases_averted": -35.0
        },
        {
          "calendar_year": 2046,
          "reference_tetanus_cases": 708.0,
          "intervention_tetanus_cases": 742.0,
          "tetanus_cases_averted": -34.0
        },
        {
          "calendar_year": 2047,
          "reference_tetanus_cases": 664.0,
          "intervention_tetanus_cases": 686.0,
          "tetanus_cases_averted": -22.0
        },
        {
          "calendar_year": 2048,
          "reference_tetanus_cases": 673.0,
          "intervention_tetanus_cases": 699.0,
          "tetanus_cases_averted": -26.0
        },
        {
          "calendar_year": 2049,
          "reference_tetanus_cases": 615.0,
          "intervention_tetanus_cases": 641.0,
          "tetanus_cases_averted": -26.0
        },
        {
          "calendar_year": 2050,
          "reference_tetanus_cases": 628.0,
          "intervention_tetanus_cases": 665.0,
          "tetanus_cases_averted": -37.0
        },
        {
          "calendar_year": 2051,
          "reference_tetanus_cases": 559.0,
          "intervention_tetanus_cases": 594.0,
          "tetanus_cases_averted": -35.0
        },
        {
          "calendar_year": 2052,
          "reference_tetanus_cases": 577.0,
          "intervention_tetanus_cases": 593.0,
          "tetanus_cases_averted": -16.0
        },
        {
          "calendar_year": 2053,
          "reference_tetanus_cases": 607.0,
          "intervention_tetanus_cases": 635.0,
          "tetanus_cases_averted": -28.0
        },
        {
          "calendar_year": 2054,
          "reference_tetanus_cases": 561.0,
          "intervention_tetanus_cases": 609.0,
          "tetanus_cases_averted": -48.0
        },
        {
          "calendar_year": 2055,
          "reference_tetanus_cases": 4.0,
          "intervention_tetanus_cases": 4.0,
          "tetanus_cases_averted": 0.0
        }
      ],
      "modeled_zero_dose_relative_reduction_percent_end_window": 52.85756443045445,
      "tetanus_cases_averted_calendar_year_2025": 274.0,
      "reference_tetanus_cases_calendar_year_2025": 787.0,
      "intervention_tetanus_cases_calendar_year_2025": 513.0
    },
    "interpretation": "New tetanus infections are from the Starsim tetanus module (not national statistics). They depend on n_agents. By default both arms use the same RNG seed (fair counterfactual); if you pass --seed-intervention with a different value, arms are independent and averted counts can be noisy or negative. Modeled ZD reduction is in modeled_zero_dose_relative_reduction_percent_end_window (not fixed at 50%)."
  },
  "population_scaled_projection": {
    "anchor_label": "Kenya national (official sources, 2024)",
    "anchor_under5_population": 7200000,
    "anchor_annual_live_births": 1270000,
    "anchor_source": "UN World Population Prospects 2024; WHO/UNICEF WUENIC 2024 revision (released July 2025)",
    "count_scale_factor": 2540.0,
    "count_scale_note": "Disease counts scaled by real_annual_births / model_annual_births (1,270,000 / 500). Zero-dose shares apply to any population without rescaling.",
    "zero_dose_children_reference_end": 1226667,
    "zero_dose_children_intervention_end": 578281,
    "zero_dose_children_reached_at_end": 648386,
    "mean_annual_children_additionally_vaccinated": 117824,
    "cumulative_child_years_zd_gap_closed": 3652543,
    "total_disease_deaths_averted_scaled": 406400,
    "mean_annual_disease_deaths_averted_scaled": 13110,
    "tetanus_cases_averted_scaled": 523240,
    "interpretation": "Scaled estimates show the real-world order of magnitude for Kenya. Zero-dose fractions are model outputs; absolute counts apply those fractions to the Kenya under-5 population or annual birth cohort. Disease death estimates carry additional uncertainty from model structure and should be treated as illustrative, not as epidemiological projections."
  }
};
