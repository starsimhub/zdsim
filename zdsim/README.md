# `zdsim/` — Core package

Python package that powers the Zero-dose Vaccination ABM. Import with
``import zdsim as zds``.

## Contents

| Module | What it contains |
|---|---|
| `__init__.py`             | Top-level exports: disease classes and `ZeroDoseVaccination`. |
| `version.py`              | Package version string. |
| `interventions.py`        | `ZeroDoseVaccination` intervention (`ss.Intervention`). |
| `diseases/`               | Disease modules (one `ss.Infection` subclass per pathogen). |
| `data/`                   | Administrative immunization data shipped with the package. |
| `zerodose_data.py`        | Loaders for `zerodose_data_formated.xlsx` + DTP1 coverage proxies. |
| `zerodose_calibration.py` | `SimulationParameterBundle` dataclass and calibration helpers. |
| `reporting.py`            | `reportlab`-based PDF report generator (`zdsim_report.pdf`). |

## Design

- Every probabilistic decision uses Starsim distributions (`ss.bernoulli`,
  `ss.random`) so CRN and reproducible seeding work out of the box.
- Parameters are collected in one `SimulationParameterBundle` object so that
  calibration output can be persisted to JSON and replayed in later runs.
- No global state — every function takes the sim / bundle it needs.

See the repository-level `Readme.md` for research-question context and
workflow instructions.
