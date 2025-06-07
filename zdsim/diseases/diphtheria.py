import starsim as ss
import numpy as np
from starsim.diseases.sir import SIR

class Diphtheria(SIR):
    """
    Diphtheria model using Starsim SIR base structure.
    Targets children under 5 with standard death rate and long infectious duration.
    """

    def __init__(self, pars=None, *args, **kwargs):
        super().__init__()
        self.define_pars(
            beta      = ss.beta(0.5),
            init_prev = ss.bernoulli(p=0.005),
            dur_inf   = ss.lognorm_ex(mean=ss.days(10), std=ss.days(3)),
            p_death   = ss.bernoulli(p=0.07),
            under5_sus_factor = 1.5
        )
        self.update_pars(pars=pars, **kwargs)

    def make_new_cases(self):
        people = self.sim.people
        sus = self.susceptible.uids
        if len(sus) == 0:
            return

        age = people.age[sus]
        weights = np.where(age < 5, self.pars.under5_sus_factor, 1.0)

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
        self.infected[uids] = True

        dur_inf = p.dur_inf.rvs(uids)
        self.ti_recovered[uids] = ti + dur_inf

        will_die = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
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
        self.results.new_infections_u5[ti] = np.count_nonzero((self.ti_infected == ti) & (age < 5))
        self.results.new_deaths_u5[ti] = np.count_nonzero((self.ti_dead == ti) & (age < 5))


if __name__ == '__main__':
    diph = Diphtheria()
    sim = ss.Sim(
        n_agents=10000,
        diseases=diph,
        start=2000,
        stop=2026,
        verbose=0.25
        )
    sim.run()
    sim.plot()

