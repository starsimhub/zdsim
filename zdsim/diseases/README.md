# `zdsim/diseases/` — Disease modules

One `ss.Infection` subclass per pathogen in the pentavalent (DTP-HepB-Hib)
set plus tetanus. All modules share a common pattern:

1. Declare parameters (including `ss.bernoulli` / `ss.lognorm_ex`
   distributions) via `define_pars`.
2. Declare per-agent states via `define_states` (booleans like `severe`,
   floats like `immunity`).
3. Implement `set_prognoses` (schedule recovery vs death on new infection)
   and `step_state` (recover / die / wane).
4. Override `step_die` to clear custom boolean states for dying agents.

## Modules

| File | Pathogen | Dynamics |
|---|---|---|
| `diphtheria.py`  | *Corynebacterium diphtheriae*   | S → I → R with person-to-person transmission (β = 6.0/yr, target R0 ≈ 3, duration ≈ 0.5 yr). `severe` flag and ~5% CFR. Recovered agents gain permanent immunity=0.8. |
| `pertussis.py`   | *Bordetella pertussis*          | S → I → R with β = 46.0/yr (target R0 ≈ 11.5, duration ≈ 0.25 yr). Exponential waning of immunity at `waning_immunity=0.1/yr`, so reinfection becomes possible as immunity decays. |
| `hib.py`         | *Haemophilus influenzae* type b | S → I → R with β = 17.5/yr (target R0 ≈ 1.75, duration ≈ 0.1 yr). Per-infection `meningitis` flag (default 10% of cases) in addition to `severe`. |
| `hepatitis_b.py` | Hepatitis B virus               | S → I → R with β = 0.5/yr (target R0 ≈ 1.0, duration ≈ 2.0 yr). A fraction `p_chronic` (default 5%) of new infections stay infected indefinitely as chronic carriers (they never transition to recovered). |
| `tetanus.py`     | *Clostridium tetani*            | **Not** person-to-person; `beta=0`. Wound-exposure model with four age segments (neonatal / peri-neonatal / childhood / adult), each with its own annual wound rate and CFR. Immunity wanes (default 0.055/yr) back to susceptible, completing an SIS cycle. |

## Vaccination coupling

All five modules expose a `vaccinated`, `ti_vaccinated`, and `immunity`
state. The `ZeroDoseVaccination` intervention (see
`zdsim/interventions.py`) sets `immunity = efficacy` and `rel_sus = 1 −
efficacy` on each of these modules when a child is vaccinated. Immunity
then decays inside each module's `step_state` (for pertussis and tetanus
explicitly; diphtheria/Hib/HepB treat immunity as terminal once set).

## What is NOT modeled

- **Cross-disease interactions** (co-infection effects).
- **Maternal immunisation** — previous drafts included neonatal maternal
  tetanus immunity; that logic was removed in the 3.3.3 port because this
  cohort initialises from age 0+ and the surface was never exercised.
- **Age-dependent severity / case-fatality** for the pentavalent set
  (tetanus is the exception — its CFR *is* age-stratified).

See the repository-level `Readme.md` for parameter sources and calibration
procedure.
