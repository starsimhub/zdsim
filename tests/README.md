# `tests/` — Smoke and correctness tests

Follow the [Starsim test style](https://github.com/starsimhub/styleguide/blob/main/3_tests.md):
each test file is runnable **both** by `pytest` and as a standalone script
(an `if __name__ == '__main__':` block enables plotting and calls each
`test_*` function).

## Running

```bash
pip install pytest sciris starsim
pytest tests -q                       # All tests, quiet
python tests/test_smoke.py            # Standalone with plots enabled
python tests/test_vaccine_effect.py   # Another scenario
```

Tests use small agent counts (`n_agents=1_000`) and should each finish in a
few seconds. Scientific-correctness tests (e.g. vaccination reduces
zero-dose share) use generous tolerances to avoid stochastic flakiness.

## Adding tests

Follow the template in `test_smoke.py`:

1. Module docstring + imports.
2. Module-level constants (`n_agents`, `do_plot`, `sc.options(interactive=False)`).
3. Helper `make_sim()`.
4. `@sc.timer()`-decorated `test_<feature>` functions that `return` the sim.
5. `if __name__ == '__main__':` block that calls each test with plotting on.
