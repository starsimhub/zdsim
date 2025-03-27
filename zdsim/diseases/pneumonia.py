import numpy as np
import starsim as ss
from enum import IntEnum

__all__ = ['PneumoniaState', 'Pneumonia']

class PneumoniaState(IntEnum):
    SUSCEPTIBLE = 0
    INFECTED    = 1
    RECOVERED   = 2
    DEAD        = 3

class Pneumonia(ss.Infection):
    """
    A simple acute pneumonia model.

    States:
      - SUSCEPTIBLE → INFECTED: Based on transmission
      - INFECTED → RECOVERED or DEAD: Based on duration and probabilities
    """
    def __init__(self, pars=None, **kwargs):
        super().__init__()

        self.define_pars(
            beta        = ss.beta(0.2),                  # Transmission rate
            init_prev   = ss.bernoulli(0.01),            # Initial prevalence
            dur_inf     = ss.normal(loc=ss.days(10)),    # Duration of illness
            p_death     = ss.bernoulli(0.03),            # Case fatality rate
        )
        self.update_pars(pars, **kwargs)

        self.define_states(
            ss.State('susceptible', default=True),
            ss.State('infected'),
            ss.State('recovered'),
            ss.FloatArr('ti_infected'),
            ss.FloatArr('ti_recovered'),
            ss.FloatArr('ti_dead'),
            ss.FloatArr('rel_sus', default=1.0),
            ss.FloatArr('rel_trans', default=1.0),
        )

    @property
    def infectious(self):
        return self.infected

    def set_prognoses(self, uids, sources=None):
        super().set_prognoses(uids, sources)
        ti = self.ti
        p = self.pars

        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti

        dur_inf = p.dur_inf.rvs(uids)
        will_die = p.p_death.rvs(uids)

        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]

    def step_state(self):
        ti = self.ti
        rec_uids = (self.infected & (self.ti_recovered <= ti)).uids
        self.infected[rec_uids] = False
        self.recovered[rec_uids] = True

        death_uids = (self.ti_dead <= ti).uids
        if len(death_uids):
            self.sim.people.request_death(death_uids)

    def step_die(self, uids):
        self.susceptible[uids] = False
        self.infected[uids] = False
        self.recovered[uids] = False

    def init_results(self):
        super().init_results()
        self.define_results(
            ss.Result('pneumonia_prevalence', dtype=float, label='Prevalence'),
            ss.Result('pne_susceptible', dtype=int, label='Susceptible'),
            ss.Result('pne_infected', dtype=int, label='Infected'),
            ss.Result('pne_recovered', dtype=int, label='Recovered'),
            ss.Result('pne_deaths', dtype=int, label='Deaths'),
        )

    def update_results(self):
        super().update_results()
        ti = self.ti
        uids = self.sim.people.auids
        state_sus = self.susceptible[uids]
        state_inf = self.infected[uids]
        state_rec = self.recovered[uids]
        state_dead = self.sim.people.dead[uids]

        self.results.pneumonia_prevalence[ti] = np.sum(state_inf) / len(uids)
        self.results.pne_susceptible[ti] = np.sum(state_sus)
        self.results.pne_infected[ti] = np.sum(state_inf)
        self.results.pne_recovered[ti] = np.sum(state_rec)
        self.results.pne_deaths[ti] = np.sum(state_dead)

