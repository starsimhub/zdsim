"""
One-command wrapper for the zdsim project.

What this does:

1. If ``calibration.json`` is missing (or ``FRESH_CALIBRATION`` is True below),
   runs ``calibrate.py`` to generate it.
2. Runs ``run_simulation.py`` to produce outputs in ``outputs/``.

How to configure:

- Force a fresh calibration:  set ``FRESH_CALIBRATION = True`` below.
- Change simulation horizon, agent count, seed, data file, etc.:
      edit ``main()`` in ``run_simulation.py``.
- Change calibration grid, short-run size, data file, etc.:
      edit ``main()`` in ``calibrate.py``.

Usage:

    python research_workflow.py
"""

import os
import subprocess
import sys


ROOT             = os.path.dirname(os.path.abspath(__file__))
PYTHON           = sys.executable
CALIBRATE_SCRIPT = os.path.join(ROOT, "calibrate.py")
RUN_SCRIPT       = os.path.join(ROOT, "run_simulation.py")
CALIBRATION_FILE = os.path.join(ROOT, "calibration.json")

FRESH_CALIBRATION = False


def main():
    """ Ensure calibration.json exists, then run the simulation. """
    if FRESH_CALIBRATION or not os.path.isfile(CALIBRATION_FILE):
        reason = "requested" if FRESH_CALIBRATION else "missing"
        print(f"Calibration step ({reason}).")
        subprocess.run(
            [PYTHON, CALIBRATE_SCRIPT, "--out", CALIBRATION_FILE],
            check=True,
            cwd=ROOT,
        )
    else:
        print(f"Using existing calibration: {CALIBRATION_FILE}")

    print("Simulation step.")
    subprocess.run([PYTHON, RUN_SCRIPT], check=True, cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
