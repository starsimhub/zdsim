# `zdsim/diseases/` — Disease modules

One `ss.Infection` subclass per pathogen in the pentavalent (DTP-HepB-Hib) +
tetanus set. All modules share a common pattern:

1. Declare parameters (including `ss.bernoulli` / `ss.lognorm_ex`
   distributions) via `define_pars`.
2. Declare per-agent states via `define_states` (booleans like `severe`,
   floats like `immunity`).
3. Implement `set_prognoses` (schedule recovery vs death on new infection)
   and `step_state` (recover / die / wane).
4. Override `step_die` to clear custom boolean states for dying agents.

## Modules

| File | Pathogen | Notes |
|---|---|---|
| `diphtheria.py`  | *Corynebacterium diphtheriae* | Standard SIR dynamics with severity flag and vaccine-derived immunity. |
| `pertussis.py`   | *Bordetella pertussis*        | SIR with age-specific severity and exponential waning. |
| `hib.py`         | *Haemophilus influenzae* type b | SIR with meningitis flag (~30% of cases). |
| `hepatitis_b.py` | Hepatitis B virus             | SIR with chronic-carrier subset (age-dependent). |
| `tetanus.py`     | *Clostridium tetani*          | **Not** person-to-person; β=0. Wound-exposure model with age-specific wound rates and CFRs; waning back to susceptible completes an SIS cycle. |

## Vaccination

All five modules expose a `vaccinated`, `ti_vaccinated`, and `immunity`
state. The `ZeroDoseVaccination` intervention (see `zdsim/interventions.py`)
sets `immunity = efficacy` and `rel_sus = 1 − efficacy` on each of these
modules when a child is vaccinated. Immunity decays inside each module's
`step_state`.

See the repository-level `Readme.md` for parameter sources and calibration
procedure.
