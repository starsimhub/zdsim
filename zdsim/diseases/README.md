# `zdsim/diseases/` — Disease modules

A single `ss.Infection` subclass: `Tetanus`.

Per Rono et al. (2024), tetanus is the only DTP-bracket disease still endemic
in Kenya (diphtheria is eliminated, neonatal tetanus is near elimination,
pertussis is under marked control). It therefore serves as the sentinel
outcome for zero-dose / DTP1 coverage gaps — the research question in the
brief is explicitly about "tetanus cases averted".

## Module

| File | Pathogen | Dynamics |
|---|---|---|
| `tetanus.py` | *Clostridium tetani* | **Not** person-to-person (`beta=0`). Wound-exposure model with four age bands (neonatal / peri-neonatal / childhood / adult), each with its own annual wound rate and CFR. Immunity wanes (default 0.055/yr) back to susceptible, giving the SIS cycle described in the brief. |

## Vaccination coupling

The module exposes `vaccinated`, `ti_vaccinated`, and `immunity` states. The
`ZeroDoseVaccination` intervention (see `zdsim/interventions.py`) sets
`immunity = efficacy` and `rel_sus = 1 − efficacy` on tetanus when a child is
vaccinated. Immunity then wanes inside `step_state` at `waning_immunity`.

See the repository-level `Readme.md` for parameter sources and calibration
procedure.
