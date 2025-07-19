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
            beta=0.3,  # daily, for R0 ≈ 3 and dur_inf=10 days (Kenya-tuned)
            init_prev=ss.bernoulli(p=0.001),  # 0.1% initial prevalence
            dur_inf=ss.normal(loc=10),        # days
            p_death=ss.bernoulli(p=0.05),     # 5% case fatality
            under5_sus_factor=1.5,            # 50% higher susceptibility for under-5s
            vaccine_efficacy=0.95,            # Vaccine efficacy
        )
        self.update_pars(pars=pars, **kwargs)

        # Add vaccination states
        self.define_states(
            ss.State('vaccinated', label='Vaccinated'),  # Added vaccination state
            ss.State('immune', label='Immune'),         # Added immunity state
            ss.FloatArr('time_vaccinated', label='Time of vaccination'),  # Added vaccination time
        )

    def make_new_cases(self):
        people = self.sim.people
        # Only susceptible, non-vaccinated, non-immune individuals can be infected
        sus = (self.susceptible & ~self.vaccinated & ~self.immune).uids
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

    def step_die(self, uids):
        # Reset all states for dead agents
        for state in ['susceptible', 'infected', 'recovered', 'vaccinated', 'immune']:
            self.statesdict[state][uids] = False
        return

    def vaccinate(self, uids):
        """Vaccinate specified individuals"""
        ti = self.ti
        p = self.pars
        
        # Mark as vaccinated
        self.vaccinated[uids] = True
        self.time_vaccinated[uids] = ti
        
        # Apply vaccine efficacy to determine immunity
        # Use numpy random instead of starsim distribution for simplicity
        effective = np.random.random(len(uids)) < p.vaccine_efficacy
        immune_uids = uids[effective]
        self.immune[immune_uids] = True
        
        # Remove from susceptible if immune
        self.susceptible[immune_uids] = False
        
        return len(immune_uids)


if __name__ == '__main__':
    import matplotlib.pyplot as plt
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
    plt.show()

    # --- Simple test for CI or development ---
    def test_diphtheria():
        test_diph = Diphtheria()
        test_sim = ss.Sim(n_agents=100, diseases=test_diph, start=2020, stop=2022, verbose=0)
        test_sim.run()
        # Check that results are present and simulation completed
        assert hasattr(test_sim, 'results'), 'Simulation did not generate results.'
        assert test_sim.results.t[-1] == 2022, 'Simulation did not reach stop year.'
        print('Diphtheria test passed.')

    test_diphtheria()

