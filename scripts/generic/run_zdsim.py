

import sciris as sc
import numpy as np
import starsim as ss
import zdsim as zds


def make_sim(sim_pars=None):
    """Create and configure a tetanus simulation."""
    sim_params = dict(
        start=sc.date('1940-01-01'),
        stop=sc.date('2025-12-31')
    )
    if sim_pars:
        sim_params.update(sim_pars)


    # Create the product - a vaccine with 50% efficacy
    inv = zds.ZeroDoseVaccination(dict(
        start_day=0,
        end_day=365*50,
        coverage=0.5,
        efficacy=0.9,
        year=[1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
    ))

    pop = ss.People(n_agents=1000)
    tt = zds.Tetanus(dict(
        beta=0.1,
        init_prev=0.25,
    ))

    sim = ss.Sim(
        people=pop,
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),
        interventions=[inv],
        diseases=tt,
        demographics=[ss.Births(dict(birth_rate=5)), ss.Deaths(dict(death_rate=5))],
        pars=sim_params,
    )
    sim.pars.verbose = sim.pars.dt / 365
    return sim

if __name__ == '__main__':
    sim = make_sim()
    sim.run()
    tet : ss.Disease = sim.diseases['tetanus']
    
    tet.plot()




