window.ZDSIM_SUMMARY = {
  "data_file": "/Users/mine/git/zdsim/zdsim/data/zerodose_data_formated.xlsx",
  "population_assumption": null,
  "calibration_source": "/Users/mine/git/zdsim/calibration.json",
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
  "zero_dose_fraction_under5_model_reference": 0.17333333333333334,
  "zero_dose_fraction_under5_model_scale_up": 0.0728476821192053,
  "relative_reduction_percent_model": 57.97249108507388,
  "projection_calendar_start": 2025,
  "projection_calendar_stop": 2030,
  "projection_yearly_reference": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9712057588482303,
      "n_children_under5": 5001,
      "n_zero_dose_under5": 4857,
      "disease_attributable_deaths": 81
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.21993553186213738,
      "n_children_under5": 4033,
      "n_zero_dose_under5": 887,
      "disease_attributable_deaths": 40
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.07104173303599873,
      "n_children_under5": 3139,
      "n_zero_dose_under5": 223,
      "disease_attributable_deaths": 43
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.052,
      "n_children_under5": 2250,
      "n_zero_dose_under5": 117,
      "disease_attributable_deaths": 46
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.07275320970042796,
      "n_children_under5": 1402,
      "n_zero_dose_under5": 102,
      "disease_attributable_deaths": 62
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.17218543046357615,
      "n_children_under5": 604,
      "n_zero_dose_under5": 104,
      "disease_attributable_deaths": 0
    }
  ],
  "projection_yearly_scale_up": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9320135972805439,
      "n_children_under5": 5001,
      "n_zero_dose_under5": 4661,
      "disease_attributable_deaths": 66
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.032138442521631644,
      "n_children_under5": 4045,
      "n_zero_dose_under5": 130,
      "disease_attributable_deaths": 27
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.013616212792906902,
      "n_children_under5": 3158,
      "n_zero_dose_under5": 43,
      "disease_attributable_deaths": 37
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.018926056338028168,
      "n_children_under5": 2272,
      "n_zero_dose_under5": 43,
      "disease_attributable_deaths": 37
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.03036723163841808,
      "n_children_under5": 1416,
      "n_zero_dose_under5": 43,
      "disease_attributable_deaths": 55
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.07236842105263158,
      "n_children_under5": 608,
      "n_zero_dose_under5": 44,
      "disease_attributable_deaths": 1
    }
  ],
  "projection_benefit_summary": {
    "projection_years": [
      2025,
      2026,
      2027,
      2028,
      2029,
      2030
    ],
    "mean_annual_reduction_zerodose_share_pp": 7.661528371436837,
    "cumulative_zerodose_share_reduction_pp_years": 45.969170228621024,
    "sum_annual_zero_dose_children_gap": 1326.0
  },
  "projection_death_benefit_summary": {
    "projection_years": [
      2025,
      2026,
      2027,
      2028,
      2029,
      2030
    ],
    "total_reference_deaths": 272.0,
    "total_intervention_deaths": 223.0,
    "total_deaths_averted": 49.0,
    "mean_annual_deaths_averted": 8.166666666666666
  },
  "projection_yearly_deaths_comparison": [
    {
      "calendar_year": 2025,
      "reference_deaths": 81,
      "intervention_deaths": 66,
      "deaths_averted": 15
    },
    {
      "calendar_year": 2026,
      "reference_deaths": 40,
      "intervention_deaths": 27,
      "deaths_averted": 13
    },
    {
      "calendar_year": 2027,
      "reference_deaths": 43,
      "intervention_deaths": 37,
      "deaths_averted": 6
    },
    {
      "calendar_year": 2028,
      "reference_deaths": 46,
      "intervention_deaths": 37,
      "deaths_averted": 9
    },
    {
      "calendar_year": 2029,
      "reference_deaths": 62,
      "intervention_deaths": 55,
      "deaths_averted": 7
    },
    {
      "calendar_year": 2030,
      "reference_deaths": 0,
      "intervention_deaths": 1,
      "deaths_averted": -1
    }
  ],
  "disease_deaths_note": "Counts are deaths attributed to pentavalent disease modules in the simulation (diphtheria, tetanus, pertussis, hepatitis B, Hib), not all-cause mortality. Yearly totals are stochastic; with few agents or short runs, cumulative \u201caverted\u201d deaths can occasionally be negative\u2014in that case prefer longer projections, larger n_agents, or multiple seeds.",
  "n_agents": 5000,
  "years": 5,
  "who_context_url": "https://www.who.int/news-room/fact-sheets/detail/immunization-coverage",
  "calibration_short_run_years": 8,
  "calibration_short_run_agents": 10000,
  "research_question_tetanus": {
    "question": "How many tetanus cases will be averted if we reduce prevalence of zero-dose vaccination by 50% among under-fives by the year 2025?",
    "modeled_answer": {
      "metric": "new_tetanus_infections_in_simulated_cohort",
      "reference_total": 524.0,
      "intervention_total": 355.0,
      "tetanus_cases_averted_total": 169.0,
      "by_calendar_year": [
        {
          "calendar_year": 2025,
          "reference_tetanus_cases": 169.0,
          "intervention_tetanus_cases": 114.0,
          "tetanus_cases_averted": 55.0
        },
        {
          "calendar_year": 2026,
          "reference_tetanus_cases": 88.0,
          "intervention_tetanus_cases": 55.0,
          "tetanus_cases_averted": 33.0
        },
        {
          "calendar_year": 2027,
          "reference_tetanus_cases": 90.0,
          "intervention_tetanus_cases": 59.0,
          "tetanus_cases_averted": 31.0
        },
        {
          "calendar_year": 2028,
          "reference_tetanus_cases": 105.0,
          "intervention_tetanus_cases": 61.0,
          "tetanus_cases_averted": 44.0
        },
        {
          "calendar_year": 2029,
          "reference_tetanus_cases": 71.0,
          "intervention_tetanus_cases": 65.0,
          "tetanus_cases_averted": 6.0
        },
        {
          "calendar_year": 2030,
          "reference_tetanus_cases": 1.0,
          "intervention_tetanus_cases": 1.0,
          "tetanus_cases_averted": 0.0
        }
      ],
      "modeled_zero_dose_relative_reduction_percent_end_window": 57.97249108507388,
      "tetanus_cases_averted_calendar_year_2025": 55.0,
      "reference_tetanus_cases_calendar_year_2025": 169.0,
      "intervention_tetanus_cases_calendar_year_2025": 114.0
    },
    "interpretation": "New tetanus infections are from the Starsim tetanus module (not national statistics). They depend on n_agents. By default both arms use the same RNG seed (fair counterfactual); if you pass --seed-intervention with a different value, arms are independent and averted counts can be noisy or negative. Modeled ZD reduction is in modeled_zero_dose_relative_reduction_percent_end_window (not fixed at 50%)."
  },
  "population_scaled_projection": {
    "anchor_label": "Kenya national (official sources, 2024)",
    "anchor_under5_population": 7200000,
    "anchor_annual_live_births": 1270000,
    "anchor_source": "UN World Population Prospects 2024; WHO/UNICEF WUENIC 2024 revision (released July 2025)",
    "count_scale_factor": 10160.0,
    "count_scale_note": "Disease counts scaled by real_annual_births / model_annual_births (1,270,000 / 125). Zero-dose shares apply to any population without rescaling.",
    "zero_dose_children_reference_end": 1248000,
    "zero_dose_children_intervention_end": 524503,
    "zero_dose_children_reached_at_end": 723497,
    "mean_annual_children_additionally_vaccinated": 97301,
    "cumulative_child_years_zd_gap_closed": 583808,
    "total_disease_deaths_averted_scaled": 497840,
    "mean_annual_disease_deaths_averted_scaled": 82973,
    "tetanus_cases_averted_scaled": 1717040,
    "interpretation": "Scaled estimates show the real-world order of magnitude for Kenya. Zero-dose fractions are model outputs; absolute counts apply those fractions to the Kenya under-5 population or annual birth cohort. Disease death estimates carry additional uncertainty from model structure and should be treated as illustrative, not as epidemiological projections."
  }
};
