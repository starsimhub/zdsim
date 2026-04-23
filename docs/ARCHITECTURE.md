# zdsim Architecture

A compact agent-based model built on [Starsim](https://starsim.org) that answers a single research question:

> **How many tetanus cases and tetanus deaths are averted if routine DTP1/pentavalent delivery in Kenya is scaled up enough to roughly halve the under-5 zero-dose share?**

Per Rono et al. (2024), tetanus is the only DTP-bracket disease still endemic in Kenya (diphtheria is eliminated, neonatal tetanus is near elimination, pertussis and measles are under marked control). **Tetanus is therefore the only disease simulated** — it is the sentinel outcome for zero-dose / DTP1 coverage gaps.

This document walks through the moving parts end-to-end — with Mermaid diagrams, a class map, module tables, and a timestep trace.

---

## Table of contents

1. [System at a glance](#1-system-at-a-glance)
2. [Repository map](#2-repository-map)
3. [Data → calibration → simulation flow](#3-data--calibration--simulation-flow)
4. [Core data structures](#4-core-data-structures)
5. [Simulation anatomy (what lives inside `ss.Sim`)](#5-simulation-anatomy-what-lives-inside-sssim)
6. [Timestep execution order](#6-timestep-execution-order)
7. [Tetanus disease module](#7-tetanus-disease-module)
8. [ZeroDoseVaccination intervention](#8-zerodosevaccination-intervention)
9. [Analyzers and outputs](#9-analyzers-and-outputs)
10. [Population scaling to Kenya anchors](#10-population-scaling-to-kenya-anchors)
11. [Design decisions](#11-design-decisions)

---

## 1. System at a glance

```mermaid
flowchart LR
    XLSX[("zerodose_data_formated.xlsx<br/>monthly HMIS counts<br/>DPT1 to DPT3, estimated_lb,<br/>tetanus cases")]
    CAL["calibrate.py<br/>grid search over routine_prob"]
    JSON[("calibration.json<br/>reference + scale-up parameter sets")]
    RUN["run_simulation.py<br/>baseline + reference + scale-up sims"]
    OUT[("outputs/<br/>summary JSON<br/>PNG plots<br/>zdsim_report.pdf")]
    WORKFLOW["research_workflow.py<br/>one-command wrapper"]

    XLSX -->|DTP1 coverage proxy + births + tetanus cases| CAL
    CAL -->|writes| JSON
    JSON -->|loaded at startup| RUN
    XLSX -->|context plots + tetanus fit| RUN
    RUN --> OUT

    WORKFLOW -.->|ensures| JSON
    WORKFLOW -.->|invokes| RUN

    style XLSX fill:#fef9c3,stroke:#ca8a04,color:#000
    style CAL fill:#dbeafe,stroke:#2563eb,color:#000
    style JSON fill:#fef9c3,stroke:#ca8a04,color:#000
    style RUN fill:#dcfce7,stroke:#16a34a,color:#000
    style OUT fill:#f3e8ff,stroke:#9333ea,color:#000
    style WORKFLOW fill:#ffe4e6,stroke:#e11d48,color:#000
```

**Two stages by design.** Calibration is slow (it sweeps 14 short sims in a grid); simulation is fast. Separating them lets researchers re-run scenarios without recalibrating each time.

---

## 2. Repository map

```
zdsim/
├── run_simulation.py              ▶ entry point — all runtime config in main()
├── calibrate.py                   🔧 standalone grid-search calibrator
├── research_workflow.py           🎛 convenience wrapper (calibrate → simulate)
│
├── zdsim/                         📦 importable package
│   ├── __init__.py                exposes ZeroDoseVaccination + Tetanus
│   ├── interventions.py           ZeroDoseVaccination
│   ├── zerodose_calibration.py    SimulationParameters + build_calibration_parameters
│   ├── zerodose_data.py           xlsx loader + DTP1/zero-dose proxy
│   ├── analysis.py                YearlyRecorder, metrics, result extraction
│   ├── plots.py                   matplotlib figure generation
│   ├── reporting.py               PDF report generator (reportlab)
│   └── diseases/
│       └── tetanus.py             environmental SIS + waning + 4 age bands
│
├── zdsim/data/zerodose_data_formated.xlsx
├── calibration.json               generated; auto-detected by run_simulation.py
├── outputs/                       generated per run
├── tests/test_smoke.py
└── docs/
    ├── ARCHITECTURE.md            ← this file
    └── Zero-Dose Vaccination ABM Report.pdf
```

---

## 3. Data → calibration → simulation flow

### 3a. From xlsx to empirical proxy

```mermaid
flowchart LR
    SHEET["Sheet1<br/>monthly rows<br/>year · month · dpt1 · dpt3<br/>· estimated_lb · tetanus"]

    subgraph ZD ["zerodose_data.py"]
        A1["monthly_births = estimated_lb / 12"]
        A2["coverage = clip dpt1 / monthly_births, 0, 1"]
        A3["zerodose = 1 minus coverage"]
        A4["mean_zerodose_proxy<br/>approximately 16.5 percent"]
        SHEET --> A1 --> A2 --> A3 --> A4
    end

    style A4 fill:#fef3c7,stroke:#f59e0b,color:#000
```

### 3b. Calibration grid search

```mermaid
flowchart TD
    EMP["empirical zero-dose target<br/>e.g. 0.165"]
    BASE["build_calibration_parameters<br/>→ base SimulationParameters"]

    GRID["grid_search_reference_routine<br/>for rp in linspace 0.018 to 0.090 in 14 steps:<br/>build sim · run in parallel · measure ZD<br/>pick rp that minimises abs ZD minus target"]

    REF["reference parameters<br/>routine_prob = rp*"]
    INT["scale-up parameters<br/>routine_prob = min 0.12, rp* × 2.3<br/>coverage = min 0.88, cov + 0.02, 0.85"]

    OUT_JSON[("calibration.json<br/>schema_version<br/>calibration_metadata<br/>reference_parameters<br/>scale_up_parameters")]

    EMP --> GRID
    BASE --> GRID
    GRID --> REF
    REF --> INT
    REF --> OUT_JSON
    INT --> OUT_JSON
```

**Each of the 14 trial sims is short and small** — `CALIB_N_AGENTS = 10,000` agents over `CALIB_YEARS = 8` years — and they run in parallel via `ss.multi_run`, so the whole grid completes in tens of seconds.

### 3c. Simulation stage (runtime)

```mermaid
flowchart LR
    JSON[("calibration.json")]
    REFB["reference parameters<br/>(seed = 42)"]
    INTB["scale-up parameters<br/>(seed = 42, same seed)"]

    JSON --> REFB
    JSON --> INTB

    REFB -->|build_simulation(with_intervention=False)| SIMB["sim_baseline<br/>20 000 agents · 2025–2030"]
    REFB -->|build_simulation(with_intervention=True)|  SIMR["sim_ref<br/>20 000 agents · 2025–2030"]
    INTB -->|build_simulation(with_intervention=True)|  SIMI["sim_int<br/>20 000 agents · 2025–2030"]

    SIMB & SIMR & SIMI -->|ss.multi_run, parallel| AGG["compute metrics<br/>zerodose_fraction_under5<br/>tetanus_metrics<br/>get_rows from YearlyRecorder"]
    AGG --> SUMMARY["summary dict"]
    SUMMARY --> JOUT[("zerodose_demo_summary.json")]
    SUMMARY --> PDF[("zdsim_report.pdf<br/>reportlab")]
    SUMMARY --> PLOTS[("PNG plots")]
```

---

## 4. Core data structures

### SimulationParameters

A frozen dataclass — immutable, copy-on-write via `dataclasses.replace`. **Everything** needed to build one scenario is in here; `build_simulation` reads from nothing else.

```mermaid
classDiagram
    class SimulationParameters {
        +int seed
        +float birth_rate
        +float death_rate
        +float fertility_rate
        +int household_contacts
        +int community_contacts
        +float tetanus_init_p
        +float intervention_routine_prob
        +float intervention_coverage
        +float intervention_efficacy
        +float intervention_age_min
        +float intervention_age_max
        +float intervention_booster_age_max
        +float intervention_booster_interval_years
        +dict data_derived
        +as_log_dict() dict
        +from_dict(d) SimulationParameters
    }

    class build_calibration_parameters {
        +seed
        +df
        +population
        +empirical
    }

    class with_intervention_delivery {
        +base
        +routine_prob
        +coverage
    }

    build_calibration_parameters ..> SimulationParameters : creates
    with_intervention_delivery ..> SimulationParameters : copies and updates
```

Fields come from three places:

| Origin | Fields |
|---|---|
| **Derived from xlsx** | `birth_rate` (from `estimated_lb`), `fertility_rate` (from `birth_rate`), `intervention_coverage` (mean DTP1 proxy), `tetanus_init_p` (scaled from reported monthly cases) |
| **Derived by calibration** | `intervention_routine_prob` |
| **Fixed constants** | `household_contacts = 5`, `community_contacts = 15`, `intervention_efficacy = 0.9`, age window `[0, 5]` yr, boosters disabled (`booster_age_max = 0`) |

---

## 5. Simulation anatomy (what lives inside `ss.Sim`)

Every scenario is one `ss.Sim` instance composed of five groups of modules.

```mermaid
flowchart TB
    subgraph SIM ["ss.Sim · start – stop · dt = 1/52 yr · rand_seed = pars.seed"]
        direction TB

        subgraph PPL ["People"]
            P1["ss.People<br/>n_agents = 20 000<br/>age_data: LMIC pyramid exp(-0.022 × a)"]
        end

        subgraph NETS ["Networks"]
            N1["ss.RandomNet name=household<br/>n_contacts = 5 · dur = 0"]
            N2["ss.RandomNet name=community<br/>n_contacts = 15 · dur = 0"]
        end

        subgraph DEM ["Demographics"]
            D1["ss.Pregnancy fertility_rate per 1000 women 15-49/yr"]
            D2["ss.Deaths death_rate per 1000/yr"]
        end

        subgraph DIS ["Diseases"]
            X2["Tetanus"]
        end

        subgraph INV ["Interventions"]
            I1["ZeroDoseVaccination<br/>coverage · efficacy · routine_prob<br/>age in 0 to 5 yr"]
        end

        subgraph ANA ["Analyzers (optional)"]
            A1["YearlyRecorder<br/>zero-dose share + tetanus deaths per year"]
        end
    end

    I1 -.->|sets immunity · rel_sus| DIS
    DIS -.->|ti_dead| ANA
    I1 -.->|vaccinated state| ANA
```

The **baseline** scenario is identical except no `ZeroDoseVaccination` module is attached, so every under-5 is zero-dose by definition.

---

## 6. Timestep execution order

Starsim runs these phases in order on each of the ~260 weekly timesteps in a 5-year projection window.

```mermaid
sequenceDiagram
    autonumber
    participant Sim as ss.Sim
    participant Dem as Demographics
    participant Net as Networks
    participant Dis as Tetanus
    participant Inv as ZeroDoseVaccination
    participant Ana as YearlyRecorder

    loop every timestep ti
        Sim->>Dem: step — pregnancies, births, background deaths
        Sim->>Net: step — refresh contact pairs
        Sim->>Dis: step — wound draws by age band
        Sim->>Dis: step_state — recover, wane, schedule deaths
        Sim->>Dis: step_die — clear state for the dead
        Sim->>Inv: step — only if ti in timepoints
        Note right of Inv: check_eligibility<br/>p_vx Bernoulli filter<br/>set immunity and rel_sus on tetanus
        Sim->>Ana: step — record tetanus deaths every step<br/>record ZD snapshot on year boundaries
    end
```

Within each step the vaccination intervention runs **after** the disease, so immunity acquired this week influences next week's wound-to-infection draws — not this week's.

---

## 7. Tetanus disease module

Tetanus is implemented as `zdsim/diseases/tetanus.py`; it inherits from `ss.Infection` but sets `beta = 0` because real-world tetanus is not person-to-person.

```mermaid
classDiagram
    class ss_Infection {
        <<Starsim base>>
        +BoolState susceptible
        +BoolState infected
        +FloatArr rel_sus
        +set_prognoses(uids)
        +step()
        +step_state()
        +step_die(uids)
    }

    class Tetanus {
        +FloatArr immunity
        +BoolState vaccinated
        +FloatArr ti_vaccinated
        +FloatArr ti_dead
    }

    ss_Infection <|-- Tetanus
```

### Environmental SIS with four age bands

Tetanus is the only disease modelled, and it differs structurally from a standard SIR module: **no person-to-person β** — agents acquire tetanus from wound exposure at an age-specific rate.

```mermaid
stateDiagram-v2
    direction LR
    [*] --> S : birth or init_prev

    state "Wound draw" as W
    S --> W : wound_rate of age_band times dt
    W --> S : immunity blocks, prob = immunity
    W --> I : one minus immunity infection draw

    I --> R : dur_inf mean 3 months
    I --> Dead : age-band CFR

    R --> R : waning event 0.055 per yr, immunity x 0.5
    R --> S : immunity below 0.1, fully susceptible
```

**Four age bands** (resolved from `age * 365` days):

| Band | Ages | Wound rate/yr | CFR |
|---|---|---|---|
| Neonatal | 0–28 days | **0.0111** | **71.8%** |
| Peri-neonatal | 29–60 days | **0.0213** | **52.1%** |
| Childhood | 2 months – 15 years | **0.0637** | **48.0%** |
| Adult | 15+ years | **0.6346** | **32.7%** |

Each event type (wound, infection, waning, death) has its own RNG stream (`ss.random()`) so streams are CRN-stable across scenarios.

---

## 8. ZeroDoseVaccination intervention

```mermaid
flowchart TD
    START(["step called"])
    T{"sim.ti in<br/>self.timepoints?"}
    EL["check_eligibility<br/>age in 0 to 5 yr<br/>AND zero_dose"]
    DRAW["p_vx.filter on eligible_uids"]
    APPLY["_apply_vaccine_effects"]
    SET["tetanus module:<br/>vaccinated uids = True<br/>ti_vaccinated uids = ti<br/>immunity uids = efficacy 0.9<br/>rel_sus uids = 1 minus efficacy"]
    NO(["return empty uids — skip"])
    STATE["module state update:<br/>self.zero_dose uids = False<br/>self.vaccinated uids = True<br/>self.doses_received uids += 1"]

    START --> T
    T -->|yes| EL
    T -->|no| NO
    EL -->|UIDs| DRAW
    DRAW -->|filtered UIDs| STATE
    STATE --> APPLY
    APPLY --> SET
```

### Per-step probability logic

```python
if pars.year is not None:        # campaign mode
    p = pars.coverage
else:                            # routine mode (default)
    p = pars.routine_prob * pars.coverage
```

| Mode | Enabled when | Timepoints | Per-step p |
|---|---|---|---|
| **Routine** | `year=None` (default) | every step in `[start_day, end_day]` | `routine_prob × coverage` |
| **Campaign** | `year=[y1, y2, ...]` | timesteps nearest to each target year | `coverage` |

**Why this shape?** `routine_prob` is the per-week probability a given child encounters the health system; `coverage` is the probability they actually get jabbed conditional on that encounter. Multiplying gives the weekly vaccination probability.

Although the intervention conceptually represents a DTP1/pentavalent first dose, the only disease whose state it modifies is tetanus — that's the sentinel outcome in Rono et al. (2024).

---

## 9. Analyzers and outputs

### YearlyRecorder

```mermaid
flowchart TD
    S1["sim advances by 1 week"]
    S2["YearlyRecorder.step"]
    S3["tetanus_deaths_by_year of year += tetanus_deaths_at_step"]
    S4{"year boundary?<br/>first step of a new year"}
    S5["append row:<br/>calendar_year<br/>zerodose_under5_fraction<br/>n_children_under5<br/>n_zero_dose_under5"]
    S6["continue"]

    S1 --> S2 --> S3 --> S4
    S4 -->|yes| S5
    S4 -->|no| S6
```

### Output computation graph

```mermaid
flowchart LR
    SB["sim_baseline"] --> B1["base_zd"]
    SR["sim_ref"] --> R1["ref_zd<br/>zerodose_fraction_under5"]
    SI["sim_int"] --> I1["int_zd"]
    SR --> R2["tet_ref<br/>tetanus_metrics"]
    SI --> I2["tet_int"]
    SB --> B3["rows_base"]
    SR --> R3["rows_ref<br/>get_rows"]
    SI --> I3["rows_int"]

    R1 & I1 --> REL["relative reduction percent<br/>ref_zd minus int_zd, over ref_zd, times 100"]
    R2 & I2 --> TAV["tetanus cases averted<br/>tet_ref.total minus tet_int.total"]
    B3 & R3 & I3 --> DEATHS["tetanus deaths averted<br/>sum of d_ref minus d_int"]

    REL & TAV & DEATHS --> SCALED["population_scaled_projection<br/>multiplied by Kenya anchors"]

    SCALED --> J[("zerodose_demo_summary.json")]
    J --> PDF[("zdsim_report.pdf")]
    B3 & R3 & I3 --> PNGS[("PNG plots")]
```

### Output files (all under `outputs/`)

| File | What it shows |
|---|---|
| `zerodose_demo_summary.json` | Full summary dict (metrics + yearly rows + scaled projections) |
| `zerodose_impact.png` | End-of-window bar chart: empirical vs baseline vs reference vs scale-up ZD share |
| `projection_zerodose_20y.png` | Yearly ZD share trajectory |
| `projection_tetanus_deaths.png` | Yearly tetanus deaths (no-intervention vs reference vs intervention) |
| `projection_cumulative_deaths_averted.png` | Cumulative tetanus deaths averted vs no-intervention |
| `tetanus_reference_vs_intervention.png` | New tetanus infections over time |
| `calibration_before.png` / `calibration_after.png` | Monthly tetanus fit: over-predicting vs calibrated model vs data |
| `admin_data_dtp1_zerodose_timeseries.png` | Empirical DTP1 / zero-dose proxies from xlsx |
| `admin_data_dpt123_vs_births.png` | DPT1/3 dose counts vs estimated live births |
| `zdsim_report.pdf` | Narrative PDF report (title → abstract → methods → results → discussion) |

---

## 10. Population scaling to Kenya anchors

Agent counts are small (20k) for speed, so headline figures are scaled to Kenya national anchors.

```
KENYA_UNDER5_POPULATION     = 7,200,000    # UN WPP 2024
KENYA_ANNUAL_LIVE_BIRTHS    = 1,270,000    # WHO/UNICEF WUENIC 2024
model_births_per_year       = n_agents × birth_rate / 1000
scale                       = KENYA_ANNUAL_LIVE_BIRTHS / model_births_per_year

zero_dose_children_reached          = (ref_zd − int_zd) × 7_200_000
total_tetanus_deaths_averted_scaled = tetanus_deaths_averted × scale
tetanus_cases_averted_scaled        = tet_av × scale
```

---

## 11. Design decisions

| Decision | Rationale |
|---|---|
| **Tetanus is the only modelled disease** | The project brief (Rono et al. 2024) explicitly selects tetanus as the DTP-bracket sentinel because diphtheria is eliminated, neonatal tetanus is near elimination, and pertussis/measles are under marked control in Kenya. Modelling the other four pentavalent diseases would add noise without changing the research question. |
| **Calibration split from simulation** | Grid search is expensive (14 short sims, albeit parallelised); scenario runs are cheap. Separating means researchers tweak and rerun without re-sweeping. |
| **All three scenario arms share the same seed by default** | Matched counterfactual — noise cancels and observed deltas are attributable to the intervention, not RNG draws. |
| **`SimulationParameters` is frozen** | Immutable value type; scenarios are built via `dataclasses.replace`, so one parameter set can never mutate another. |
| **Tetanus = SIS + wound exposure** | Real tetanus doesn't transmit person-to-person, and immunity wanes — modeling it as SIR would misrepresent both. |
| **`dt = 1/52` (weekly)** | Coarse enough to run a 5-year × 20k-agent simulation in seconds; fine enough to resolve the 28-day neonatal tetanus window. |
| **All runtime config in `run_simulation.py:main()`** | No `argparse` — researchers change one file in one place. Calibration config still lives in `calibrate.py`'s CLI since it's a tool, not an experiment. |
| **Boosters disabled by default (`booster_age_max = 0`)** | Real EPI systems in low-coverage settings do not deliver annual adult pentavalent boosters; enabling them would produce unrealistic long-horizon dynamics. |
| **One RNG stream per tetanus event type** | Common Random Numbers: flipping `routine_prob` in the scale-up arm changes vaccination draws without shifting wound/infection/death draws, so signal > noise. |
| **Kenya anchors applied post-hoc** | The ABM runs on 20k cohort agents; real-world headcounts come from a deterministic multiplier — keeps simulation cheap and makes the scaling assumption explicit. |
| **`ss.multi_run` for scenarios and grid search** | Parallelises the three scenario runs and the 14 calibration grid points; a full workflow completes in under a minute on a laptop. |

---

*Last verified against source: `run_simulation.py`, `zdsim/interventions.py`, `zdsim/diseases/tetanus.py`, `zdsim/zerodose_calibration.py`, `zdsim/analysis.py`, `zdsim/plots.py`.*
