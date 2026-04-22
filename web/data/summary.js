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
  "zero_dose_fraction_under5_model_reference": 0.19932998324958123,
  "zero_dose_fraction_under5_model_scale_up": 0.09165302782324058,
  "relative_reduction_percent_model": 54.019447386155775,
  "projection_calendar_start": 2025,
  "projection_calendar_stop": 2030,
  "projection_yearly_reference": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9750149910053968,
      "n_children_under5": 5003,
      "n_zero_dose_under5": 4878,
      "disease_attributable_deaths": 103
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.2852173913043478,
      "n_children_under5": 4025,
      "n_zero_dose_under5": 1148,
      "disease_attributable_deaths": 46
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.1000971817298348,
      "n_children_under5": 3087,
      "n_zero_dose_under5": 309,
      "disease_attributable_deaths": 53
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.0578806767586821,
      "n_children_under5": 2246,
      "n_zero_dose_under5": 130,
      "disease_attributable_deaths": 43
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.07435719249478805,
      "n_children_under5": 1439,
      "n_zero_dose_under5": 107,
      "disease_attributable_deaths": 54
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.19833333333333333,
      "n_children_under5": 600,
      "n_zero_dose_under5": 119,
      "disease_attributable_deaths": 1
    }
  ],
  "projection_yearly_scale_up": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9488307015790526,
      "n_children_under5": 5003,
      "n_zero_dose_under5": 4747,
      "disease_attributable_deaths": 69
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.052332757343865714,
      "n_children_under5": 4051,
      "n_zero_dose_under5": 212,
      "disease_attributable_deaths": 16
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.015685019206145966,
      "n_children_under5": 3124,
      "n_zero_dose_under5": 49,
      "disease_attributable_deaths": 29
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.01757469244288225,
      "n_children_under5": 2276,
      "n_zero_dose_under5": 40,
      "disease_attributable_deaths": 38
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.02604523646333105,
      "n_children_under5": 1459,
      "n_zero_dose_under5": 38,
      "disease_attributable_deaths": 58
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.09135399673735727,
      "n_children_under5": 613,
      "n_zero_dose_under5": 56,
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
    "mean_annual_reduction_zerodose_share_pp": 8.9846393808958,
    "cumulative_zerodose_share_reduction_pp_years": 53.9078362853748,
    "sum_annual_zero_dose_children_gap": 1549.0
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
    "total_reference_deaths": 300.0,
    "total_intervention_deaths": 211.0,
    "total_deaths_averted": 89.0,
    "mean_annual_deaths_averted": 14.833333333333334
  },
  "projection_yearly_deaths_comparison": [
    {
      "calendar_year": 2025,
      "reference_deaths": 103,
      "intervention_deaths": 69,
      "deaths_averted": 34
    },
    {
      "calendar_year": 2026,
      "reference_deaths": 46,
      "intervention_deaths": 16,
      "deaths_averted": 30
    },
    {
      "calendar_year": 2027,
      "reference_deaths": 53,
      "intervention_deaths": 29,
      "deaths_averted": 24
    },
    {
      "calendar_year": 2028,
      "reference_deaths": 43,
      "intervention_deaths": 38,
      "deaths_averted": 5
    },
    {
      "calendar_year": 2029,
      "reference_deaths": 54,
      "intervention_deaths": 58,
      "deaths_averted": -4
    },
    {
      "calendar_year": 2030,
      "reference_deaths": 1,
      "intervention_deaths": 1,
      "deaths_averted": 0
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
      "reference_total": 554.0,
      "intervention_total": 374.0,
      "tetanus_cases_averted_total": 180.0,
      "by_calendar_year": [
        {
          "calendar_year": 2025,
          "reference_tetanus_cases": 203.0,
          "intervention_tetanus_cases": 133.0,
          "tetanus_cases_averted": 70.0
        },
        {
          "calendar_year": 2026,
          "reference_tetanus_cases": 79.0,
          "intervention_tetanus_cases": 36.0,
          "tetanus_cases_averted": 43.0
        },
        {
          "calendar_year": 2027,
          "reference_tetanus_cases": 91.0,
          "intervention_tetanus_cases": 64.0,
          "tetanus_cases_averted": 27.0
        },
        {
          "calendar_year": 2028,
          "reference_tetanus_cases": 93.0,
          "intervention_tetanus_cases": 73.0,
          "tetanus_cases_averted": 20.0
        },
        {
          "calendar_year": 2029,
          "reference_tetanus_cases": 87.0,
          "intervention_tetanus_cases": 67.0,
          "tetanus_cases_averted": 20.0
        },
        {
          "calendar_year": 2030,
          "reference_tetanus_cases": 1.0,
          "intervention_tetanus_cases": 1.0,
          "tetanus_cases_averted": 0.0
        }
      ],
      "modeled_zero_dose_relative_reduction_percent_end_window": 54.019447386155775,
      "tetanus_cases_averted_calendar_year_2025": 70.0,
      "reference_tetanus_cases_calendar_year_2025": 203.0,
      "intervention_tetanus_cases_calendar_year_2025": 133.0
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
    "zero_dose_children_reference_end": 1435176,
    "zero_dose_children_intervention_end": 659902,
    "zero_dose_children_reached_at_end": 775274,
    "mean_annual_children_additionally_vaccinated": 114105,
    "cumulative_child_years_zd_gap_closed": 684630,
    "total_disease_deaths_averted_scaled": 904240,
    "mean_annual_disease_deaths_averted_scaled": 150707,
    "tetanus_cases_averted_scaled": 1828800,
    "interpretation": "Scaled estimates show the real-world order of magnitude for Kenya. Zero-dose fractions are model outputs; absolute counts apply those fractions to the Kenya under-5 population or annual birth cohort. Disease death estimates carry additional uncertainty from model structure and should be treated as illustrative, not as epidemiological projections."
  }
};
