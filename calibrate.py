#!/usr/bin/env python3
"""
Calibrate zdsim parameters and save them to a JSON file.

Usage
-----
    python calibrate.py                          # uses bundled xlsx, saves calibration.json
    python calibrate.py --out my_cal.json        # custom output path
    python calibrate.py --no-data                # skip xlsx, use 16.5% ZD fallback
    python calibrate.py --n-agents-calib 20000   # more agents for tighter calibration

The saved file can then be passed to run_simulation.py to skip the grid-search:

    python run_simulation.py --calibration-file calibration.json

Workflow
--------
  1. Loads the administrative HMIS spreadsheet (zerodose_data_formated.xlsx).
  2. Computes the empirical DTP1 zero-dose proxy (mean over all months).
  3. Runs a grid search over ``routine_prob`` to match that proxy.
  4. Builds the reference bundle (calibrated delivery) and the scale-up bundle.
  5. Writes everything to a JSON file that run_simulation.py can load directly.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone

import numpy as np

from zdsim.zerodose_calibration import (
    SimulationParameterBundle,
    build_calibration_bundle,
    empirical_summary_from_dataframe,
    with_intervention_delivery,
)
from zdsim.zerodose_data import default_formatted_xlsx_path, load_formatted_xlsx

# Import the sim builder and grid-search from run_simulation (they live there
# because they depend on disease modules which would create circular imports
# inside the zdsim package itself).
from run_simulation import (
    CALIBRATION_SCHEMA_VERSION,
    build_sim_from_bundle,          # noqa: F401 – imported so callers don't need run_simulation
    grid_search_reference_routine,
)

DEFAULT_OUT = "calibration.json"


def run_calibration(
    *,
    n_agents_calib: int,
    calib_years: int,
    start: int,
    seed: int,
    data_path: str | None,
    scale_routine_factor: float,
    scale_coverage_cap: float,
    population: float | None,
    out: str,
) -> dict:
    """
    Run the calibration grid search and write results to *out* (JSON).

    Returns the calibration dict that was written.
    """
    # ------------------------------------------------------------------
    # Load data
    # ------------------------------------------------------------------
    empirical: dict | None = None
    empirical_zd = 0.165
    data_file_used: str | None = None
    df_data = None

    if data_path is not None:
        df_data = load_formatted_xlsx(data_path)
        empirical = empirical_summary_from_dataframe(df_data)
        empirical_zd = empirical["mean_zerodose_proxy"]
        data_file_used = os.path.abspath(data_path)
        print(
            f"Data ({data_file_used}): mean zero-dose proxy = "
            f"{empirical_zd:.1%} (±{empirical['std_zerodose_proxy']:.1%} across months)"
        )
    else:
        print(f"No data file — using fallback zero-dose target: {empirical_zd:.1%}")
    print()

    # ------------------------------------------------------------------
    # Build base bundle
    # ------------------------------------------------------------------
    base_bundle = build_calibration_bundle(
        seed=seed,
        df=df_data,
        population=population,
        empirical=empirical,
    )

    # ------------------------------------------------------------------
    # Grid search
    # ------------------------------------------------------------------
    print(
        f"Grid search: {calib_years} years, {n_agents_calib} agents, "
        f"coverage from data = {base_bundle.intervention_coverage:.4f} ..."
    )
    reference_rp, calib_zd = grid_search_reference_routine(
        empirical_zd,
        base_bundle,
        n_agents=n_agents_calib,
        calib_years=calib_years,
        start=start,
    )
    print(
        f"  Best routine_prob = {reference_rp:.6f}  "
        f"(model ZD = {calib_zd:.1%}, target = {empirical_zd:.1%})\n"
    )

    # ------------------------------------------------------------------
    # Build reference and scale-up bundles
    # ------------------------------------------------------------------
    reference_bundle = with_intervention_delivery(base_bundle, routine_prob=reference_rp)

    scale_rp = min(0.12, reference_rp * scale_routine_factor)
    scale_cov = float(
        min(scale_coverage_cap, max(reference_bundle.intervention_coverage + 0.02, 0.85))
    )
    scale_up_bundle = with_intervention_delivery(
        base_bundle, routine_prob=scale_rp, coverage=scale_cov
    )

    print("Reference bundle:")
    print(f"  routine_prob = {reference_bundle.intervention_routine_prob:.6f}")
    print(f"  coverage     = {reference_bundle.intervention_coverage:.4f}")
    print(f"  efficacy     = {reference_bundle.intervention_efficacy:.4f}")
    print()
    print("Scale-up bundle:")
    print(f"  routine_prob = {scale_up_bundle.intervention_routine_prob:.6f}")
    print(f"  coverage     = {scale_up_bundle.intervention_coverage:.4f}")
    print()

    # ------------------------------------------------------------------
    # Assemble and save
    # ------------------------------------------------------------------
    result: dict = {
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
            "empirical_zerodose_proxy": empirical_zd,
            "calibrated_routine_prob": reference_rp,
            "calibrated_model_zd": float(calib_zd),
            "scale_up_routine_prob": scale_rp,
            "scale_up_coverage": scale_cov,
        },
        "empirical": empirical,
        "reference_bundle": reference_bundle.as_log_dict(),
        "scale_up_bundle": scale_up_bundle.as_log_dict(),
    }

    out_abs = os.path.abspath(out)
    out_dir = os.path.dirname(out_abs)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_abs, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"Saved calibration → {out_abs}")
    print(f"  Run simulation with:  python run_simulation.py --calibration-file {out}")
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
        help="Coverage ceiling for the scale-up bundle (default: 0.88)",
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
    args = p.parse_args(argv)

    data_path = None if args.no_data else args.data
    if data_path and not os.path.isfile(data_path):
        print(
            f"Warning: data file not found: {data_path}\n"
            "Use --no-data to run without data.",
            file=sys.stderr,
        )
        return 1

    np.random.seed(args.seed)

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
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
