import numpy as np
import starsim as ss
from enum import IntEnum
import starsim as ss
import numpy as np
from starsim.diseases.sir import SIR

class Pneumonia(SIR):
    """
    Pneumonia model targeting children under 5 years old.
    """

    def __init__(self, pars=None, *args, **kwargs):
        super().__init__()
        self.define_pars(
            beta      = ss.beta(0.8),
            init_prev = ss.bernoulli(p=0.01),
            dur_exp   = ss.normal(loc=ss.days(3)),
            dur_inf   = ss.lognorm_ex(mean=ss.days(7)),
            p_death   = ss.bernoulli(p=0.05),
            under5_sus_factor = 2.0  # Multiplier to increase risk for under 5s
        )
        self.update_pars(pars=pars, **kwargs)

        self.define_states(
            ss.State('exposed', label='Exposed'),
            ss.FloatArr('ti_exposed', label='Time of exposure'),
        )

    @property
    def infectious(self):
        return self.infected | self.exposed

    def make_new_cases(self):
        """
        Override default transmission to primarily target under-fives.
        """
        people = self.sim.people
        sus = self.susceptible.uids
        if len(sus) == 0:
            return

        # Weight susceptibility by age
        age = people.age[sus]
        weights = np.where(age < 5, self.pars.under5_sus_factor, 1.0)

        # Compute transmission probabilities
        beta_eff = self.pars.beta * self.rel_trans.mean()
        p_infect = 1 - np.exp(-beta_eff * weights)

        infected = sus[np.random.rand(len(sus)) < p_infect]
        if len(infected):
            self.set_prognoses(infected)

        return

    def set_prognoses(self, uids, source_uids=None):
        super().set_prognoses(uids, source_uids)
        ti = self.ti
        p = self.pars

        self.susceptible[uids] = False
        self.exposed[uids] = True
        self.ti_exposed[uids] = ti

        self.ti_infected[uids] = ti + p.dur_exp.rvs(uids)
        dur_inf = p.dur_inf.rvs(uids)

        will_die = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]

        self.ti_dead[dead_uids] = self.ti_infected[dead_uids] + dur_inf[will_die]
        self.ti_recovered[rec_uids] = self.ti_infected[rec_uids] + dur_inf[~will_die]
        return

    def step(self):
        ti = self.ti

        new_infections = (self.exposed & (self.ti_infected <= ti)).uids
        self.exposed[new_infections] = False
        self.infected[new_infections] = True

        new_recoveries = (self.infected & (self.ti_recovered <= ti)).uids
        self.infected[new_recoveries] = False
        self.recovered[new_recoveries] = True

        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            self.sim.people.request_death(deaths)

        return

    def step_die(self, uids):
        for state in ['susceptible', 'exposed', 'infected', 'recovered']:
            self.statesdict[state][uids] = False
        return

    def init_results(self):
        super().init_results()
        self.define_results(
            ss.Result('new_infections_u5', dtype=int, label='New infections <5'),
            ss.Result('new_deaths_u5', dtype=int, label='New deaths <5'),
        )

    def update_results(self):
        super().update_results()
        ti = self.ti
        age = self.sim.people.age

        self.results.new_infections_u5[ti] = np.count_nonzero((self.ti_exposed == ti) & (age < 5))
        self.results.new_deaths_u5[ti] = np.count_nonzero((self.ti_dead == ti) & (age < 5))


__all__ = ['PneumoniaState', 'Pneumonia2']

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

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    dis = Pneumonia()
    # routine = ss.routine_vx(name='penta', prob=0.6, start_year=2023, age_range=[5], product='pentadose')
    sim = ss.Sim(
        n_agents=10000,
        diseases=dis,
        start=2000,
        stop=2026,
        verbose=.25
    )
    sim.run()
    sim.plot()
    print(sim.pars)
    plt.show()