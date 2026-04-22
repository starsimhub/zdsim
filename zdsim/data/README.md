# `zdsim/data/` — Administrative immunization data

Ships with the package so `run_simulation.py` works out of the box.

| File | Description |
|---|---|
| `zerodose_data_formated.xlsx` | Monthly administrative DTP1/DPT2/DPT3 counts and estimated live births (Kenya, 2018–2024). The only file read by the simulation. Loaded by `zdsim.zerodose_data.load_formatted_xlsx`. |

Required columns:

- `year`, `month` — calendar time of the row
- `estimated_lb` — estimated annual live births (divided by 12 for the monthly denominator)
- `dpt1`, `dpt2`, `dpt3` — monthly DTP dose counts (`dpt1` drives the zero-dose proxy)
- `tetanus`, `neonatal_tetanus`, `peri_neonatal_tetanus`, `diphtheria` — monthly case counts used to seed `init_prev`

To use a different workbook, pass its path to `load_formatted_xlsx()` or edit `main()` in `run_simulation.py`.

Do **not** commit secrets, Excel lock files (`~$*.xlsx`), or proprietary survey microdata to this folder.
