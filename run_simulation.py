import json
import os
import sys
from dataclasses import replace

import numpy as np
import pandas as pd
import starsim as ss

import zdsim as zds
from zdsim.analysis import ( YearlyRecorder,  align_rows, context_monthly_means, get_rows,
                            load_calibration, tetanus_metrics, zerodose_fraction_under5)
from zdsim.plots import save_calibration_plots, save_projection_plots
from zdsim.reporting import generate_report_pdf
from zdsim.zerodose_calibration import (
    build_calibration_parameters,
    empirical_summary_from_dataframe,
    with_intervention_delivery,
)
from zdsim.zerodose_data import default_formatted_xlsx_path, load_formatted_xlsx

CALIBRATION_SCHEMA_VERSION = "1"
DEFAULT_N_AGENTS = 20_000
DEFAULT_CALIBRATION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")
CALIB_YEARS = 8
CALIB_N_AGENTS = 10_000

KENYA_UNDER5_POPULATION = 7_200_000
KENYA_ANNUAL_LIVE_BIRTHS = 1_270_000
KENYA_ANCHOR_SOURCE = "UN WPP 2024; WHO/UNICEF WUENIC 2024 revision"

def default_age_pyramid():
   # LMIC declining-pyramid age distribution (birth_rate~25/1000, death_rate~8/1000). 
   # TODO: Replace this function if you have data on the age distribution.
    ages = np.arange(0, 81)
    return pd.DataFrame({"age": ages, "value": np.exp(-0.022 * ages)})

def build_simulation(pars, *, n_agents, start, stop, record_yearly=False, with_intervention=True):
    """ Build one simulation from a parameter set.

    When ``with_intervention`` is False no ``ZeroDoseVaccination`` module is
    attached, producing a true no-intervention baseline.
    """
    people = ss.People(n_agents=n_agents, age_data=default_age_pyramid())
    pars = pars
    interventions = None
    if with_intervention:
        interventions = [
            zds.ZeroDoseVaccination(
                dict(
                    start_day=0,
                    end_day=365 * int(stop - start),
                    coverage=pars.intervention_coverage,
                    efficacy=pars.intervention_efficacy,
                    age_min=pars.intervention_age_min,
                    age_max=pars.intervention_age_max,
                    routine_prob=pars.intervention_routine_prob,
                )
            )
        ]
    sim = ss.Sim(
        people=people,
        diseases=[ zds.Tetanus(dict(init_prev=ss.bernoulli(p=pars.tetanus_init_p)))],
        networks=[ ss.RandomNet(dict(n_contacts=pars.community_contacts, dur=0), name="community")],
        demographics=[ss.Pregnancy(fertility_rate=pars.fertility_rate), ss.Deaths(dict(death_rate=pars.death_rate))],
        interventions=interventions,
        analyzers=[YearlyRecorder()] if record_yearly else None,
        pars=dict(start=start, stop=stop, dt=1 / 52, verbose=0, rand_seed=int(pars.seed)),
    )
    return sim


def grid_search_reference_routine(empirical_zd, base_pars, *, n_agents, calib_years, start):
    """ Pick ``routine_prob`` that best matches the empirical zero-dose target.

    All grid points run in parallel via ``ss.multi_run``.
    """
    stop_short = int(start + calib_years)
    rp_grid = [float(rp) for rp in np.linspace(0.018, 0.090, 14)]
    sims = [
        build_simulation(
            with_intervention_delivery(base_pars, routine_prob=rp),
            n_agents=n_agents,
            start=start,
            stop=stop_short,
        )
        for rp in rp_grid
    ]
    finished_sims = ss.multi_run(sims)
    best_rp, best_zd, best_err = rp_grid[0], float("nan"), np.inf
    for rp, sim in zip(rp_grid, finished_sims):
        zd = float(zerodose_fraction_under5(sim))
        err = abs(zd - empirical_zd)
        if err < best_err:
            best_rp, best_zd, best_err = rp, zd, err
    return best_rp, best_zd


def run_demo(*, n_agents, start, stop, seed, seed_intervention, out_dir, data_path,
             scale_routine_factor, scale_coverage_cap, population, calibration_file=None,
             save_calibration=None):
    """ Run the full workflow and return the summary dict. """
    os.makedirs(out_dir, exist_ok=True)
    empirical = None
    empirical_zd = 0.165
    data_file = None
    df = None
    if data_path is not None:
        df = load_formatted_xlsx(data_path)
        empirical = empirical_summary_from_dataframe(df)
        empirical_zd = float(empirical["mean_zerodose_proxy"])
        data_file = os.path.abspath(data_path)
        print(f"Data {data_file}: mean zero-dose proxy {empirical_zd:.1%}.")
    else:
        print(f"No data file; using fallback zero-dose target {empirical_zd:.1%}.")

    base_pars = build_calibration_parameters(seed=seed, df=df, population=population, empirical=empirical)
    if not calibration_file or not os.path.isfile(calibration_file):
        raise FileNotFoundError(
            "Calibration file is required. Run calibrate.py first or set CALIBRATION_FILE to a valid path."
        )
    meta, ref_pars, scaleup_pars = load_calibration(calibration_file)
    calibration_source = f"loaded: {os.path.abspath(calibration_file)}"
    print(f"Loaded calibration from {calibration_file}.")

    inv_seed = int(seed) if seed_intervention is None else int(seed_intervention)
    ref_pars = replace(ref_pars, seed=int(seed))
    scaleup_pars = replace(scaleup_pars, seed=inv_seed)

    scenarios = {
        "counterfactual": dict(pars=ref_pars,     with_intervention=False, label="No intervention (counterfactual)"),
        "baseline":       dict(pars=ref_pars,     with_intervention=True,  label="Baseline (calibrated current program)"),
        "intervention":   dict(pars=scaleup_pars, with_intervention=True,  label="Scale-up toward 50% zero-dose reduction"),
    }

    print(f"Projection window {start}-{stop}, seeds reference={seed} intervention={inv_seed}.")
    print(f"Running {len(scenarios)} scenarios in parallel: {', '.join(scenarios)}.")

    names = list(scenarios)
    sims = [
        build_simulation(
            scenarios[name]["pars"], n_agents=n_agents, start=start, stop=stop,
            record_yearly=True, with_intervention=scenarios[name]["with_intervention"],
        )
        for name in names
    ]
    finished_sims = ss.multi_run(sims)

    results = {}
    for name, sim in zip(names, finished_sims):
        results[name] = dict(
            sim=sim,
            rows=get_rows(sim),
            zd=float(zerodose_fraction_under5(sim)),
            tetanus=tetanus_metrics(sim),
        )

    cf, base, intr = results["counterfactual"], results["baseline"], results["intervention"]
    rel = 100.0 * (base["zd"] - intr["zd"]) / base["zd"] if base["zd"] > 0 else float("nan")
    tet_averted = float(base["tetanus"]["total"] - intr["tetanus"]["total"])

    years, base_year, int_year = align_rows(base["rows"], intr["rows"])
    if years:
        zd_gap = np.array([base_year[y]["zerodose_under5_fraction"] - int_year[y]["zerodose_under5_fraction"] for y in years], dtype=float)
        d_ref = np.array([base_year[y]["tetanus_deaths"] for y in years], dtype=float)
        d_int = np.array([int_year[y]["tetanus_deaths"] for y in years], dtype=float)
    else:
        zd_gap, d_ref, d_int = np.array([]), np.array([]), np.array([])
    tetanus_deaths_averted = float(np.sum(d_ref - d_int)) if years else 0.0
    model_births = n_agents * (float(ref_pars.birth_rate) / 1000.0)
    scale = KENYA_ANNUAL_LIVE_BIRTHS / model_births if model_births > 0 else 1.0

    tet_by_year = []
    tbby = base["tetanus"]["by_calendar_year"]
    tiby = intr["tetanus"]["by_calendar_year"]
    for y in sorted(set(tbby) | set(tiby)):
        r = float(tbby.get(y, 0.0))
        i = float(tiby.get(y, 0.0))
        tet_by_year.append(dict(
            calendar_year=int(y),
            baseline_tetanus_cases=r,
            inv_tetanus_cases=i,
            tetanus_cases_averted=r - i,
        ))

    summary = dict(
        schema_version=CALIBRATION_SCHEMA_VERSION,
        data_file=data_file,
        calibration_source=calibration_source,
        projection_calendar_start=int(start),
        projection_calendar_stop=int(stop),
        years=int(stop - start),
        n_agents=int(n_agents),
        calibration_short_run_years=meta.get("calib_years", CALIB_YEARS),
        calibration_short_run_agents=meta.get("n_agents_calib", CALIB_N_AGENTS),
        empirical_zerodose_proxy_dtp1=empirical,
        empirical_disease_context_monthly=context_monthly_means(df),
        zero_dose_fraction_under5_empirical_proxy=float(empirical_zd),
        zero_dose_fraction_under5_model_counterfactual_no_intervention=cf["zd"],
        zero_dose_fraction_under5_model_baseline=base["zd"],
        zero_dose_fraction_under5_model_scale_up=intr["zd"],
        relative_reduction_percent_model=float(rel),
        model_reference_routine_prob=float(ref_pars.intervention_routine_prob),
        model_scale_up_routine_prob=float(scaleup_pars.intervention_routine_prob),
        model_scale_up_coverage=float(scaleup_pars.intervention_coverage),
        calibration_reference_parameters=ref_pars.as_log_dict(),
        calibration_scale_up_parameters=scaleup_pars.as_log_dict(),
        projection_yearly_baseline=base["rows"],
        projection_yearly_scale_up=intr["rows"],
        projection_benefit_summary=dict(
            projection_years=years,
            mean_annual_reduction_zerodose_share_pp=float(np.mean(zd_gap) * 100.0) if years else 0.0,
            cumulative_zerodose_share_reduction_pp_years=float(np.sum(zd_gap) * 100.0) if years else 0.0,
            sum_annual_zero_dose_children_gap=float(
                np.sum([base_year[y]["n_zero_dose_under5"] - int_year[y]["n_zero_dose_under5"] for y in years])
            ) if years else 0.0,
        ),
        projection_tetanus_death_benefit_summary=dict(
            projection_years=years,
            total_baseline_tetanus_deaths=float(np.sum(d_ref)) if years else 0.0,
            total_inv_tetanus_deaths=float(np.sum(d_int)) if years else 0.0,
            total_tetanus_deaths_averted=tetanus_deaths_averted,
            mean_annual_tetanus_deaths_averted=float(np.mean(d_ref - d_int)) if years else 0.0,
        ),
        research_question_tetanus=dict(
            question="How many tetanus cases will be averted if we reduce prevalence of zero-dose vaccination by 50% among under-fives by the year 2025?",
            modeled_answer=dict(
                metric="new_tetanus_infections_in_simulated_cohort",
                baseline_total=float(base["tetanus"]["total"]),
                inv_total=float(intr["tetanus"]["total"]),
                tetanus_cases_averted_total=tet_averted,
                by_calendar_year=tet_by_year,
                modeled_zero_dose_relative_reduction_percent_end_window=float(rel),
            ),
        ),
        population_scaled_projection=dict(
            anchor_label="Kenya national 2024 anchors",
            anchor_source=KENYA_ANCHOR_SOURCE,
            count_scale_factor=float(scale),
            zero_dose_children_baseline_end=int(round(base["zd"] * KENYA_UNDER5_POPULATION)),
            zero_dose_children_inv_end=int(round(intr["zd"] * KENYA_UNDER5_POPULATION)),
            zero_dose_children_reached_at_end=int(round((base["zd"] - intr["zd"]) * KENYA_UNDER5_POPULATION)),
            mean_annual_children_additionally_vaccinated=int(round(((base["zd"] - intr["zd"]) * KENYA_UNDER5_POPULATION) / (len(years) or 1))),
            cumulative_child_years_zd_gap_closed=int(round(((base["zd"] - intr["zd"]) * KENYA_UNDER5_POPULATION) * (len(years) or 1))),
            total_tetanus_deaths_averted_scaled=int(round(tetanus_deaths_averted * scale)),
            mean_annual_tetanus_deaths_averted_scaled=int(round((tetanus_deaths_averted * scale) / (len(years) or 1))),
            tetanus_cases_averted_scaled=int(round(tet_averted * scale)),
        ),
    )

    out_path = os.path.join(out_dir, "zerodose_demo_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote {out_path}")
    for p in save_projection_plots(df, cf["rows"], base["rows"], intr["rows"], empirical_zd,
                                   cf["zd"], base["zd"], intr["zd"],
                                   cf["sim"], base["sim"], intr["sim"], out_dir):
        print(f"Wrote {p}")
    try:
        for p in save_calibration_plots(df, ref_pars, base_pars, n_agents=n_agents, out_dir=out_dir,
                                        build_simulation=build_simulation,
                                        age_pyramid=default_age_pyramid()):
            print(f"Wrote {p}")
    except Exception as e:
        print(f"Calibration plots skipped: {e}")
    try:
        pdf = generate_report_pdf(summary, out_dir, pdf_name="zdsim_report.pdf")
        print(f"Wrote {pdf}")
    except Exception as e:
        print(f"PDF generation skipped: {e}")
    print(f"Tetanus cases: baseline={base['tetanus']['total']:.0f}, intervention={intr['tetanus']['total']:.0f}, averted={tet_averted:.0f}")
    print(f"Zero-dose under-5: empirical={empirical_zd:.1%}, counterfactual={cf['zd']:.1%}, baseline={base['zd']:.1%}, intervention={intr['zd']:.1%} ({rel:.1f}% relative reduction).")
    return summary


def main():
    """ Set all run values here and execute. """
    n_agents = DEFAULT_N_AGENTS
    start = 2025
    stop = 2030
    seed = 42
    seed_intervention = None

    data_path = default_formatted_xlsx_path()
    use_data = True

    scale_routine_factor = 2.3
    scale_coverage_cap = 0.88
    population = None

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    calibration_file = DEFAULT_CALIBRATION_FILE if os.path.isfile(DEFAULT_CALIBRATION_FILE) else None
    save_calibration = None

    if not use_data:
        data_path = None
    elif data_path and not os.path.isfile(data_path):
        print(f"Data file not found: {data_path}.", file=sys.stderr)
        return 1

    if not calibration_file:
        print(
            f"Calibration file not found at {DEFAULT_CALIBRATION_FILE}. "
            "Run calibrate.py first to generate calibrated values.",
            file=sys.stderr,
        )
        return 1
    print(f"Using calibration file {calibration_file}.")

    run_demo(
        n_agents=int(n_agents),
        start=int(start),
        stop=int(stop),
        seed=int(seed),
        seed_intervention=seed_intervention,
        out_dir=out_dir,
        data_path=data_path,
        scale_routine_factor=float(scale_routine_factor),
        scale_coverage_cap=float(scale_coverage_cap),
        population=population,
        calibration_file=calibration_file,
        save_calibration=save_calibration,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
