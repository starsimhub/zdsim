# `web/` — Static SPA viewer (data drop-zone)

Intended location for the single-page web viewer referenced in the
repository `Readme.md`. The viewer reads simulation outputs from
`web/data/summary.json` (or the embedded `summary.js`) and renders them
client-side.

| Path | Purpose |
|---|---|
| `data/`              | Drop-zone for `zerodose_demo_summary.json` and generated `summary.js`. Populated after each `run_simulation.py` execution. |
| `index.html`         | (To be added) SPA viewer entry point. |
| `serve.py` / `open_spa.py` | (To be added) Static file servers for local viewing. |

To serve whatever is in this folder locally (no Python deps beyond the
stdlib):

```bash
python -m http.server 8765 --directory web
# then visit http://127.0.0.1:8765/index.html
```

Outputs are also available without the SPA in `outputs/` (PDF report, PNG
figures, JSON summary).
