"""Run calibration (if needed) and then run the simulation.

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
