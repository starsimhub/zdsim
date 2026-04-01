"""
Legacy entry point: the supported demonstration is `run_simulation.py` at the repo root.

From the repository root:

    python run_simulation.py
"""

import os
import sys

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.insert(0, root)
    os.chdir(root)
    from run_simulation import main

    sys.exit(main())
