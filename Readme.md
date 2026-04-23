# zdsim — Zero-dose vaccination ABM

Agent-based model (built on [Starsim](https://starsim.org)) that estimates how many **tetanus cases and tetanus deaths are averted** when routine DTP1/pentavalent delivery is scaled up enough to roughly halve the under-5 **zero-dose** share in Kenya. Following Rono et al. (2024), **tetanus is the only disease simulated**: diphtheria is eliminated, neonatal tetanus is near elimination, and pertussis and measles are under marked control, so tetanus is the DTP-bracket sentinel.

**Research question (Rono et al. 2024, Project 2-2A-7):** How many tetanus cases will be averted if we reduce the prevalence of zero-dose vaccination by 50% among under-fives by 2025?

**Answer format:** Each run writes `outputs/zerodose_demo_summary.json`. Read `research_question_tetanus.modeled_answer.tetanus_cases_averted_total` for the headline number, and the accompanying PNG plots / PDF report for context.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design, module diagrams, and parameter reference.

---

## Install

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Run

```bash
python research_workflow.py
```

That's it. On first run it calibrates the model to the included Kenya HMIS data (`zdsim/data/zerodose_data_formated.xlsx`), saves `calibration.json`, then runs the reference vs scale-up simulations and writes `outputs/`.

Subsequent runs reuse the same `calibration.json` — delete it, or set `FRESH_CALIBRATION = True` in `research_workflow.py`, to recalibrate.

### Configure

All runtime parameters live in plain `main()` functions — no CLI to memorise.

| To change... | Edit `main()` in |
|---|---|
| Projection horizon (`start`, `stop`), agent count, seed, data path, output folder, scale-up aggressiveness | `run_simulation.py` |
| Calibration grid size, short-run length, data path | `calibrate.py` |
| Force recalibration on next run | `research_workflow.py` (`FRESH_CALIBRATION = True`) |

Running `calibrate.py` or `run_simulation.py` directly also works — the wrapper just chains them.

---

## Outputs (under `outputs/`)

| File | Contents |
|---|---|
| `zerodose_demo_summary.json` | Full summary: empirical means, calibrated parameters, end-of-run zero-dose fractions, yearly rows, benefit summaries. Overwritten on each run. |
| `zdsim_report.pdf` | Narrative report (title → abstract → methods → results with figures → discussion). Regenerate from an existing summary: `python -m zdsim.reporting outputs/zerodose_demo_summary.json`. |
| `zerodose_impact.png` | End-of-window bar chart: reference vs intervention zero-dose share |
| `projection_zerodose_20y.png` | Yearly zero-dose trajectory, reference vs intervention |
| `projection_tetanus_deaths.png` | Yearly tetanus deaths (no-intervention vs reference vs intervention) |
| `projection_cumulative_deaths_averted.png` | Cumulative tetanus deaths averted vs no-intervention |
| `tetanus_reference_vs_intervention.png` | New tetanus infections over time |
| `admin_data_dtp1_zerodose_timeseries.png` | Empirical DTP1 / zero-dose proxy from the xlsx |
| `admin_data_dpt123_vs_births.png` | DPT1/2/3 dose counts relative to estimated live births |
| `admin_data_disease_context.png` | Monthly pneumonia / measles / tetanus case counts (descriptive only — not modelled) |

Open the folder (macOS) to view figures:

```bash
open outputs/
```

PNGs are gitignored; they appear after you run the workflow.

---

## How it works (short version)

1. **Data.** Monthly Kenya HMIS rows (2018–2024) in `zdsim/data/zerodose_data_formated.xlsx`. The `dpt1 / estimated_lb/12` ratio gives the **DTP1 coverage proxy**; `1 − coverage` is the **zero-dose proxy** (~16.5%).
2. **Calibration.** `calibrate.py` grid-searches `routine_prob ∈ [0.018, 0.090]` so the simulated end-of-window zero-dose share matches that empirical proxy. The resulting **reference parameter set** plus a **scale-up parameter set** (higher `routine_prob`, higher `coverage` cap) is saved to `calibration.json`. Zero-dose is defined as the absence of DTP1/pentavalent first-dose; the only disease module simulated is tetanus.
3. **Simulation.** `run_simulation.py` builds two `ss.Sim`s from those parameter sets (20 000 agents, weekly steps, 2025–2030 by default) and runs them in parallel with a **matched seed** so observed deltas are attributable to the intervention, not RNG draws.
4. **Report.** Summary metrics are scaled to Kenya national anchors (7.2 M under-fives, 1.27 M annual births) and written to JSON + PNGs + PDF.

---

## Scope and limitations

- **Modeled, not measured.** Outputs are illustrative unless you recalibrate to data you supply. Headline national or global counts (e.g. WHO's 14.3 M global zero-dose children) are **not** recomputed here — cite them from [WHO](https://www.who.int/news-room/fact-sheets/detail/immunization-coverage) or [WUENIC](https://www.who.int/teams/immunization-vaccines-and-biologicals/immunization-analysis-and-insights/global-monitoring/immunization-coverage/who-unicef-estimates-of-national-immunization-coverage).
- **Cohort focus.** The population is initialised with children 0–5 years only; intervention targets ages 0–5 yr. All burden metrics are dominated by childhood segments.
- **No geography.** Contact structure is two `ss.RandomNet` networks (`household`, `community`) — no counties, no spatial stratification, no co-infection connectors.
- **Tetanus only.** Diphtheria, pertussis, hepatitis B and Hib are *not* simulated as separate modules — the brief treats them as eliminated or controlled in Kenya and uses tetanus as the sentinel.
- **Tetanus uses an environmental wound-exposure model**, not person-to-person β (see `zdsim/diseases/tetanus.py`). This differs from the Rono brief's teaching abstraction of β = 1.3.
- **Vaccine efficacy matches the brief** (`intervention_efficacy = 0.9`); the "50% ZD reduction by 2025" target is not hard-coded — it's what the scale-up parameter set is tuned to approach.

For a full design walkthrough with Mermaid diagrams, see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## License

MIT — see [LICENSE](LICENSE).
