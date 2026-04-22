# `docs/` — reference documents

Human-readable reference material for the project. **Not** the
auto-generated API reference — there is no API site; see
`../zdsim/README.md` for the package layout.

| File | What it is |
|---|---|
| `Zero-Dose Vaccination ABM Report.pdf`  | Original Rono et al. (2024) Project 2-2A-7 brief that defines the research question and parameter values used in the model. |
| `Zero-Dose Vaccination ABM Report.docx` | Editable source of the above. |

To regenerate the **run-time** PDF report (`zdsim_report.pdf`), use:

```bash
python -m zdsim.reporting outputs/zerodose_demo_summary.json
```

That script uses `reportlab` and mirrors the structure of the Rono et al.
brief.
