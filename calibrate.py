#!/usr/bin/env python3
""" Calibrate zdsim and write a reusable calibration JSON. """

import argparse
import json
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone

import starsim as ss

from zdsim.zerodose_calibration import (
    build_calibration_parameters,
    empirical_summary_from_dataframe,
    with_intervention_delivery,
)
from zdsim.analysis import zerodose_fraction_under5
from zdsim.zerodose_data import default_formatted_xlsx_path, load_formatted_xlsx

# Import shared calibration helpers from run_simulation.
from run_simulation import (
    CALIBRATION_SCHEMA_VERSION,
    build_simulation,
)

DEFAULT_OUT = "calibration.json"


def _build_trial_sim(sim, calib_pars, *, base_pars, n_agents, start, calib_years):
    """ Build one short-run sim for an Optuna trial. """
    rp = float(calib_pars["routine_prob"]["value"])
    rand_seed = calib_pars.get("rand_seed", int(base_pars.seed))
    trial_pars = with_intervention_delivery(base_pars, routine_prob=rp)
    trial_pars = replace(trial_pars, seed=int(rand_seed))
    trial_sim = build_simulation(
        trial_pars,
        n_agents=n_agents,
        start=start,
        stop=int(start + calib_years),
        with_intervention=True,
    )
    return trial_sim


def _eval_zero_dose_mismatch(sim, *, expected):
    """ Squared error between modelled and empirical zero-dose share. """
    model_zd = float(zerodose_fraction_under5(sim))
    return float((model_zd - float(expected)) ** 2)


def run_calibration(*, n_agents_calib, calib_years, start, seed, data_path,
                    scale_routine_factor, scale_coverage_cap, population, out,
                    total_trials, n_workers):
    """ Run Optuna calibration and write reference + scale-up parameter sets to ``out``. """
    empirical      = None
    empirical_zd   = 0.165
    data_file_used = None
    df_data        = None

    if data_path is not None:
        df_data = load_formatted_xlsx(data_path)
        empirical = empirical_summary_from_dataframe(df_data)
        empirical_zd = empirical["mean_zerodose_proxy"]
        data_file_used = os.path.abspath(data_path)
        print(
            f"Data {data_file_used}: mean zero-dose proxy "
            f"{empirical_zd:.1%} (+/-{empirical['std_zerodose_proxy']:.1%} across months)"
        )
    else:
        print(f"No data file; using fallback zero-dose target {empirical_zd:.1%}.")

    base_pars = build_calibration_parameters(
        seed=seed,
        df=df_data,
        population=population,
        empirical=empirical,
    )

    print(
        f"Optuna calibration: {calib_years}y, {n_agents_calib} agents, "
        f"{total_trials} trials..."
    )
    sim_template = build_simulation(
        base_pars,
        n_agents=n_agents_calib,
        start=start,
        stop=int(start + calib_years),
        with_intervention=True,
    )
    calib_pars = dict(
        routine_prob=dict(
            low=0.018,
            high=0.090,
            guess=float(base_pars.intervention_routine_prob),
            suggest_type="suggest_float",
        ),
    )
    calib = ss.Calibration(
        sim=sim_template,
        calib_pars=calib_pars,
        build_fn=_build_trial_sim,
        build_kw=dict(
            base_pars=base_pars,
            n_agents=n_agents_calib,
            start=start,
            calib_years=calib_years,
        ),
        eval_fn=_eval_zero_dose_mismatch,
        eval_kw=dict(expected=empirical_zd),
        total_trials=total_trials,
        n_workers=n_workers,
        reseed=True,
        debug=False,
        verbose=False,
    )
    calib.calibrate()
    reference_rp = float(calib.best_pars["routine_prob"])
    calib_sim = build_simulation(
        with_intervention_delivery(base_pars, routine_prob=reference_rp),
        n_agents=n_agents_calib,
        start=start,
        stop=int(start + calib_years),
        with_intervention=True,
    )
    calib_sim.run()
    calib_zd = float(zerodose_fraction_under5(calib_sim))

    print(
        f"Calibrated routine_prob={reference_rp:.6f} "
        f"(model ZD={calib_zd:.1%}, target={empirical_zd:.1%})."
    )

    reference_pars = with_intervention_delivery(base_pars, routine_prob=reference_rp)

    scale_rp = min(0.12, reference_rp * scale_routine_factor)
    scale_cov = float(
        min(scale_coverage_cap, max(reference_pars.intervention_coverage + 0.02, 0.85))
    )
    scale_up_pars = with_intervention_delivery(
        base_pars, routine_prob=scale_rp, coverage=scale_cov
    )

    print(
        f"Reference parameters: routine_prob={reference_pars.intervention_routine_prob:.6f}, "
        f"coverage={reference_pars.intervention_coverage:.4f}, "
        f"efficacy={reference_pars.intervention_efficacy:.4f}."
    )
    print(
        f"Scale-up parameters:  routine_prob={scale_up_pars.intervention_routine_prob:.6f}, "
        f"coverage={scale_up_pars.intervention_coverage:.4f}."
    )

    result = {
        "schema_version": CALIBRATION_SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "calibration_metadata": {
            "data_file": data_file_used,
            "n_agents_calib": n_agents_calib,
            "calib_years": calib_years,
            "projection_start": start,
            "seed": seed,
            "scale_routine_factor": scale_routine_factor,
            "scale_coverage_cap": scale_coverage_cap,
            "optuna_total_trials": int(total_trials),
            "optuna_n_workers": None if n_workers is None else int(n_workers),
            "empirical_zerodose_proxy": empirical_zd,
            "calibrated_routine_prob": reference_rp,
            "calibrated_model_zd": float(calib_zd),
            "scale_up_routine_prob": scale_rp,
            "scale_up_coverage": scale_cov,
        },
        "empirical": empirical,
        "reference_parameters": reference_pars.as_log_dict(),
        "scale_up_parameters": scale_up_pars.as_log_dict(),
    }

    out_abs = os.path.abspath(out)
    out_dir = os.path.dirname(out_abs)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved calibration to {out_abs}.")
    print(f"Run: python run_simulation.py --calibration-file {out}")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Calibrate zdsim and write a reusable calibration JSON. "
            "Pass the output to run_simulation.py via --calibration-file."
        )
    )
    p.add_argument(
        "--n-agents-calib",
        type=int,
        default=10_000,
        help="Agents used in each short calibration trial (default: 10 000)",
    )
    p.add_argument(
        "--calib-years",
        type=int,
        default=8,
        help="Length of each short calibration run in years (default: 8)",
    )
    p.add_argument(
        "--start",
        type=int,
        default=2025,
        help="First calendar year of calibration horizon (default: 2025)",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for the calibration grid search (default: 42)",
    )
    p.add_argument(
        "--data",
        default=default_formatted_xlsx_path(),
        help="Path to zerodose_data_formated.xlsx",
    )
    p.add_argument(
        "--no-data",
        action="store_true",
        help="Skip xlsx; use the 16.5%% fallback zero-dose proxy",
    )
    p.add_argument(
        "--scale-routine-factor",
        type=float,
        default=2.3,
        help="Scale-up routine_prob = min(0.12, reference × factor) (default: 2.3)",
    )
    p.add_argument(
        "--scale-coverage-cap",
        type=float,
        default=0.88,
        help="Coverage ceiling for the scale-up parameter set (default: 0.88)",
    )
    p.add_argument(
        "--population",
        type=float,
        default=None,
        help="Total population — enables birth_rate derivation from estimated_lb",
    )
    p.add_argument(
        "--out",
        default=DEFAULT_OUT,
        help=f"Output JSON path (default: {DEFAULT_OUT})",
    )
    p.add_argument(
        "--total-trials",
        type=int,
        default=40,
        help="Total Optuna trials for Starsim calibration (default: 40)",
    )
    p.add_argument(
        "--n-workers",
        type=int,
        default=None,
        help="Optuna worker count (default: all available cores)",
    )
    args = p.parse_args(argv)

    data_path = None if args.no_data else args.data
    if data_path and not os.path.isfile(data_path):
        print(
            f"Data file not found: {data_path}. Use --no-data to run without data.",
            file=sys.stderr,
        )
        return 1

    run_calibration(
        n_agents_calib=args.n_agents_calib,
        calib_years=args.calib_years,
        start=args.start,
        seed=args.seed,
        data_path=data_path,
        scale_routine_factor=args.scale_routine_factor,
        scale_coverage_cap=args.scale_coverage_cap,
        population=args.population,
        out=args.out,
        total_trials=args.total_trials,
        n_workers=args.n_workers,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
