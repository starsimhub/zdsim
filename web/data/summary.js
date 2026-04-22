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
  "zero_dose_fraction_under5_model_reference": 0.17218543046357615,
  "zero_dose_fraction_under5_model_scale_up": 0.0867430441898527,
  "relative_reduction_percent_model": 49.62230895127785,
  "projection_calendar_start": 2025,
  "projection_calendar_stop": 2030,
  "projection_yearly_reference": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9718169098540875,
      "n_children_under5": 5003,
      "n_zero_dose_under5": 4862,
      "disease_attributable_deaths": 95
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.2755026061057334,
      "n_children_under5": 4029,
      "n_zero_dose_under5": 1110,
      "disease_attributable_deaths": 38
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.09273021001615508,
      "n_children_under5": 3095,
      "n_zero_dose_under5": 287,
      "disease_attributable_deaths": 43
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.055875831485587585,
      "n_children_under5": 2255,
      "n_zero_dose_under5": 126,
      "disease_attributable_deaths": 50
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.07202216066481995,
      "n_children_under5": 1444,
      "n_zero_dose_under5": 104,
      "disease_attributable_deaths": 56
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.1716171617161716,
      "n_children_under5": 606,
      "n_zero_dose_under5": 104,
      "disease_attributable_deaths": 1
    }
  ],
  "projection_yearly_scale_up": [
    {
      "calendar_year": 2025,
      "zerodose_under5_fraction": 0.9408354987007795,
      "n_children_under5": 5003,
      "n_zero_dose_under5": 4707,
      "disease_attributable_deaths": 68
    },
    {
      "calendar_year": 2026,
      "zerodose_under5_fraction": 0.05107327905255366,
      "n_children_under5": 4053,
      "n_zero_dose_under5": 207,
      "disease_attributable_deaths": 21
    },
    {
      "calendar_year": 2027,
      "zerodose_under5_fraction": 0.014423076923076924,
      "n_children_under5": 3120,
      "n_zero_dose_under5": 45,
      "disease_attributable_deaths": 30
    },
    {
      "calendar_year": 2028,
      "zerodose_under5_fraction": 0.018014059753954304,
      "n_children_under5": 2276,
      "n_zero_dose_under5": 41,
      "disease_attributable_deaths": 38
    },
    {
      "calendar_year": 2029,
      "zerodose_under5_fraction": 0.031506849315068496,
      "n_children_under5": 1460,
      "n_zero_dose_under5": 46,
      "disease_attributable_deaths": 58
    },
    {
      "calendar_year": 2030,
      "zerodose_under5_fraction": 0.0864600326264274,
      "n_children_under5": 613,
      "n_zero_dose_under5": 53,
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
      2030
    ],
    "mean_annual_reduction_zerodose_share_pp": 8.28753472451158,
    "cumulative_zerodose_share_reduction_pp_years": 49.72520834706948,
    "sum_annual_zero_dose_children_gap": 1494.0
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
    "total_reference_deaths": 283.0,
    "total_intervention_deaths": 215.0,
    "total_deaths_averted": 68.0,
    "mean_annual_deaths_averted": 11.333333333333334
  },
  "projection_yearly_deaths_comparison": [
    {
      "calendar_year": 2025,
      "reference_deaths": 95,
      "intervention_deaths": 68,
      "deaths_averted": 27
    },
    {
      "calendar_year": 2026,
      "reference_deaths": 38,
      "intervention_deaths": 21,
      "deaths_averted": 17
    },
    {
      "calendar_year": 2027,
      "reference_deaths": 43,
      "intervention_deaths": 30,
      "deaths_averted": 13
    },
    {
      "calendar_year": 2028,
      "reference_deaths": 50,
      "intervention_deaths": 38,
      "deaths_averted": 12
    },
    {
      "calendar_year": 2029,
      "reference_deaths": 56,
      "intervention_deaths": 58,
      "deaths_averted": -2
    },
    {
      "calendar_year": 2030,
      "reference_deaths": 1,
      "intervention_deaths": 0,
      "deaths_averted": 1
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
      "reference_total": 555.0,
      "intervention_total": 369.0,
      "tetanus_cases_averted_total": 186.0,
      "by_calendar_year": [
        {
          "calendar_year": 2025,
          "reference_tetanus_cases": 207.0,
          "intervention_tetanus_cases": 130.0,
          "tetanus_cases_averted": 77.0
        },
        {
          "calendar_year": 2026,
          "reference_tetanus_cases": 72.0,
          "intervention_tetanus_cases": 41.0,
          "tetanus_cases_averted": 31.0
        },
        {
          "calendar_year": 2027,
          "reference_tetanus_cases": 93.0,
          "intervention_tetanus_cases": 61.0,
          "tetanus_cases_averted": 32.0
        },
        {
          "calendar_year": 2028,
          "reference_tetanus_cases": 97.0,
          "intervention_tetanus_cases": 75.0,
          "tetanus_cases_averted": 22.0
        },
        {
          "calendar_year": 2029,
          "reference_tetanus_cases": 85.0,
          "intervention_tetanus_cases": 61.0,
          "tetanus_cases_averted": 24.0
        },
        {
          "calendar_year": 2030,
          "reference_tetanus_cases": 1.0,
          "intervention_tetanus_cases": 1.0,
          "tetanus_cases_averted": 0.0
        }
      ],
      "modeled_zero_dose_relative_reduction_percent_end_window": 49.62230895127785,
      "tetanus_cases_averted_calendar_year_2025": 77.0,
      "reference_tetanus_cases_calendar_year_2025": 207.0,
      "intervention_tetanus_cases_calendar_year_2025": 130.0
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
    "zero_dose_children_reference_end": 1239735,
    "zero_dose_children_intervention_end": 624550,
    "zero_dose_children_reached_at_end": 615185,
    "mean_annual_children_additionally_vaccinated": 105252,
    "cumulative_child_years_zd_gap_closed": 631510,
    "total_disease_deaths_averted_scaled": 690880,
    "mean_annual_disease_deaths_averted_scaled": 115147,
    "tetanus_cases_averted_scaled": 1889760,
    "interpretation": "Scaled estimates show the real-world order of magnitude for Kenya. Zero-dose fractions are model outputs; absolute counts apply those fractions to the Kenya under-5 population or annual birth cohort. Disease death estimates carry additional uncertainty from model structure and should be treated as illustrative, not as epidemiological projections."
  }
};
