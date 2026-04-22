# `docs/` — Reference documents

Human-readable reference material for the project. **Not** the auto-generated
API reference — there is no API site yet; see `../zdsim/README.md` for the
package layout.

| File | What it is |
|---|---|
| `Zero-Dose Vaccination ABM Report.pdf`   | Original Rono et al. (2024) Project 2-2A-7 brief that defines the research question and parameter values used in the model. |
| `Zero-Dose Vaccination ABM Report.docx`  | Editable source of the above. |
| `zero_dose_project_alignment.md`         | Mapping of every claim in the brief to the corresponding code path. Update whenever you change `run_simulation.py` or a disease module. |

To regenerate the **run-time** PDF report (`zdsim_report.pdf`), use:

```bash
python -m zdsim.reporting outputs/zerodose_demo_summary.json
```

That script uses `reportlab` and mirrors the structure of the Rono et al.
brief.
