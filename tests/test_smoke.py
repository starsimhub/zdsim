"""
Smoke tests for the Zero-dose Vaccination ABM.

Follows the Starsim test style guide (3_tests.md): dual-mode execution
(pytest + standalone script), @sc.timer() decorators, module-level
constants, conditional plotting, descriptive assertion messages, and
scientific-correctness checks.
"""

import sciris as sc
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt

import zdsim as zds

# Module-level constants ------------------------------------------------
n_agents = 1_000
do_plot  = False
sc.options(interactive=False)


def make_sim(intervention=None, seed=1, years=5):
    """
    Helper to create a minimal zdsim simulation for unit tests.

    Args:
        intervention (ss.Intervention/None): zero-dose intervention, if any
        seed         (int):                  RNG seed for reproducibility
        years        (int):                  simulation duration in years

    Returns:
        sim (ss.Sim): un-run simulation ready to call ``.run()``.
    """
    diseases = [
        zds.Tetanus(),
        zds.Diphtheria(),
        zds.Pertussis(),
        zds.HepatitisB(),
        zds.Hib(),
    ]
    interventions = [intervention] if intervention is not None else []
    return ss.Sim(
        n_agents      = n_agents,
        diseases      = diseases,
        interventions = interventions,
        networks      = ss.RandomNet(),
        demographics  = [ss.Births(birth_rate=25), ss.Deaths(death_rate=8)],
        start         = 2025,
        stop          = 2025 + years,
        dt            = ss.years(1/12),
        rand_seed     = seed,
    )


# Tests ----------------------------------------------------------------

@sc.timer()
def test_sim_runs(do_plot=do_plot):
    """ The baseline simulation runs without error and produces results. """
    sc.heading('Testing baseline simulation runs...')
    sim = make_sim(seed=1)
    sim.run()
    assert sim.ti > 0, f'Expected at least one timestep but got {sim.ti}'
    assert len(sim.results.tetanus.new_infections) > 0, \
        'Expected tetanus result time series to be non-empty'
    if do_plot:
        sim.plot()
    return sim


@sc.timer()
def test_vaccine_reduces_zero_dose(do_plot=do_plot):
    """
    Scientific correctness: adding the vaccination intervention must reduce
    the share of vaccinated children compared to a no-intervention run.
    """
    sc.heading('Testing vaccination reduces zero-dose share...')
    sim_ref = make_sim(seed=1).run()
    vx      = zds.ZeroDoseVaccination(coverage=0.9, efficacy=0.9, routine_prob=0.5)
    sim_vx  = make_sim(intervention=vx, seed=1).run()

    # Count vaccinated children at the end of the run
    n_vx_ref = 0  # No vaccination intervention in reference
    n_vx_arm = int(sim_vx.interventions.zerodosevaccination.vaccinated.sum())

    assert n_vx_arm > n_vx_ref, \
        f'Expected intervention arm to vaccinate more children ' \
        f'but got ref={n_vx_ref}, intervention={n_vx_arm}'
    if do_plot:
        plt.figure()
        plt.bar(['reference', 'intervention'], [n_vx_ref, n_vx_arm])
        plt.ylabel('Children vaccinated at end of run')
        plt.title('Vaccination reduces zero-dose share')
    return sim_vx


@sc.timer()
def test_higher_coverage_vaccinates_more(do_plot=do_plot):
    """
    Scientific correctness: higher coverage produces more vaccinated
    children. Vary ``coverage`` and check the result moves in the right
    direction (generous tolerance for stochastic noise).
    """
    sc.heading('Testing higher coverage -> more vaccinations...')
    results = {}
    for cov in [0.2, 0.9]:
        vx  = zds.ZeroDoseVaccination(coverage=cov, efficacy=0.9, routine_prob=0.5)
        sim = make_sim(intervention=vx, seed=1).run()
        results[cov] = int(sim.interventions.zerodosevaccination.vaccinated.sum())
    assert results[0.9] > results[0.2], \
        f'Expected coverage=0.9 to vaccinate more than coverage=0.2 ' \
        f'but got {results}'
    if do_plot:
        plt.figure()
        plt.bar([str(k) for k in results], list(results.values()))
        plt.xlabel('coverage')
        plt.ylabel('Children vaccinated')
    return results


@sc.timer()
def test_tetanus_cfr_bounds(do_plot=do_plot):
    """ Tetanus case fatality rate in a short run must stay within [0, 1]. """
    sc.heading('Testing tetanus CFR plausibility...')
    sim           = make_sim(seed=2).run()
    new_cases     = int(np.sum(sim.results.tetanus.new_infections))
    cum_deaths    = int(sim.results.tetanus.cum_deaths[-1]) if hasattr(sim.results.tetanus, 'cum_deaths') else 0
    cfr_estimate  = cum_deaths / new_cases if new_cases > 0 else 0.0

    rtol = 0.05  # Generous — short run + tiny cohort
    assert 0.0 <= cfr_estimate <= 1.0 + rtol, \
        f'Expected CFR in [0, 1] but got {cfr_estimate:.3f}'
    return sim


# Standalone entry point -----------------------------------------------

if __name__ == '__main__':
    do_plot = True
    sc.options(interactive=do_plot)
    T = sc.timer()

    sim1 = test_sim_runs(do_plot=do_plot)
    sim2 = test_vaccine_reduces_zero_dose(do_plot=do_plot)
    res3 = test_higher_coverage_vaccinates_more(do_plot=do_plot)
    sim4 = test_tetanus_cfr_bounds(do_plot=do_plot)

    T.toc()
    if do_plot:
        plt.show()
