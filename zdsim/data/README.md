# `zdsim/data/` — Administrative immunization data

Ships with the package so `run_simulation.py` works out of the box.

| File | Format | What it is |
|---|---|---|
| `zerodose_data_formated.xlsx` | Excel | Monthly administrative DTP1/DPT2/DPT3 counts and estimated live births (Kenya, 2018–2024). Primary input. Loaded by `zdsim.zerodose_data.load_formatted_xlsx`. |
| `zerodose_data.xlsx`          | Excel | Raw/unformatted snapshot (archived for reference). |
| `zerodose_data.dta`           | Stata | Original source file from the partner survey. Not consumed by the code directly. |

The formatted xlsx is the only file the simulation reads by default. Point
at a different workbook via `run_simulation.py --data <path>` as long as it
has the same columns (`date`, `dpt1_children`, `estimated_lb`, …).

**Do not** commit secrets, lock files (`~$*.xlsx`), or proprietary survey
microdata to this folder.
