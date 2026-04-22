#!/usr/bin/env python3
"""
One-command workflow for researchers.

This helper makes the project easy to run without remembering many flags:

    python research_workflow.py            # full (2025-2055), auto-calibration
    python research_workflow.py --quick    # quick check (2025-2030, 5k agents)
    python research_workflow.py --paper    # paper horizon (2024-2025)
    python research_workflow.py --fresh-calibration

Behavior:
1) Ensures a calibration JSON exists (or regenerates it if requested).
2) Runs run_simulation.py using that calibration file.
3) Optionally opens output plots.
"""

import argparse
import os
import subprocess
import sys


ROOT             = os.path.dirname(os.path.abspath(__file__))
PYTHON           = sys.executable
CALIBRATE_SCRIPT = os.path.join(ROOT, "calibrate.py")
RUN_SCRIPT       = os.path.join(ROOT, "run_simulation.py")

DEFAULT_CALIBRATION = os.path.join(ROOT, "calibration.json")
DEFAULT_OUTPUT      = os.path.join(ROOT, "outputs")


def _run(cmd):
    """ Run command and stream output; raise on failure. """
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT)
    return


def _ensure_calibration(calibration_file, fresh):
    """ Generate the calibration file if missing or ``fresh`` is requested. """
    if fresh or not os.path.isfile(calibration_file):
        reason = "requested" if fresh else "missing"
        print(f"\nCalibration step ({reason})", flush=True)
        _run([PYTHON, CALIBRATE_SCRIPT, "--out", calibration_file])
    else:
        print(f"\nUsing existing calibration: {calibration_file}", flush=True)
    return


def main(argv=None):
    p = argparse.ArgumentParser(
        description=(
            "Research-friendly runner: auto-calibrate if needed, then run simulation."
        )
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--quick",
        action="store_true",
        help="Fast smoke run: 2025-2030, 5k agents",
    )
    mode.add_argument(
        "--paper",
        action="store_true",
        help="Paper policy horizon: 2024-2025 window",
    )
    p.add_argument(
        "--fresh-calibration",
        action="store_true",
        help="Force regeneration of calibration file before simulation",
    )
    p.add_argument(
        "--calibration-file",
        default=DEFAULT_CALIBRATION,
        help=f"Calibration JSON path (default: {DEFAULT_CALIBRATION})",
    )
    p.add_argument(
        "--n-agents",
        type=int,
        default=None,
        help="Override population size for this run",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override simulation seed for this run",
    )
    p.add_argument(
        "--out",
        default=DEFAULT_OUTPUT,
        help=f"Output folder (default: {DEFAULT_OUTPUT})",
    )
    p.add_argument(
        "--open-plots",
        action="store_true",
        help="Open generated PNG plots after run (macOS 'open')",
    )
    args = p.parse_args(argv)

    calibration_file = os.path.abspath(args.calibration_file)
    out_dir = os.path.abspath(args.out)

    # Presets
    start, stop, n_agents = 2025, 2055, 20_000
    if args.quick:
        start, stop, n_agents = 2025, 2030, 5_000
    elif args.paper:
        start, stop, n_agents = 2024, 2025, 20_000

    if args.n_agents is not None:
        n_agents = int(args.n_agents)

    print("=== zdsim researcher workflow ===", flush=True)
    print(f"Mode: {'quick' if args.quick else 'paper' if args.paper else 'full'}", flush=True)
    print(f"Window: {start}-{stop}", flush=True)
    print(f"Agents: {n_agents:,}", flush=True)
    print(f"Calibration file: {calibration_file}", flush=True)
    print(f"Outputs: {out_dir}", flush=True)

    _ensure_calibration(calibration_file=calibration_file, fresh=args.fresh_calibration)

    os.makedirs(out_dir, exist_ok=True)

    sim_cmd = [
        PYTHON,
        RUN_SCRIPT,
        "--calibration-file",
        calibration_file,
        "--start",
        str(start),
        "--stop",
        str(stop),
        "--n-agents",
        str(n_agents),
        "--out",
        out_dir,
    ]
    if args.seed is not None:
        sim_cmd.extend(["--seed", str(int(args.seed))])

    print("\nSimulation step", flush=True)
    _run(sim_cmd)

    print("\nDone.", flush=True)
    print(f"Summary JSON: {os.path.join(out_dir, 'zerodose_demo_summary.json')}", flush=True)
    print(f"Plots folder:  {out_dir}", flush=True)

    if args.open_plots:
        # Open the output folder (contains all generated PNGs and JSON).
        subprocess.run(["open", out_dir], check=False, cwd=ROOT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

