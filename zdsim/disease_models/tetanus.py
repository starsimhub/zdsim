import starsim as ss
import numpy as np

__all__ = ['Tetanus']


class Tetanus(ss.Infection):
    """
    Tetanus infection model following SIS (Susceptible-Infected-Susceptible) structure.
    
    Model specifications:
    - Beta: 1.3 (transmission rate)
    - Gamma: 3/12 (recovery rate - 3 months)
    - Waning: 0.055 (immunity waning rate)
    - Vaccination probability: 0.25
    - Vaccine efficacy: 0.9 (90%)
    """
    def __init__(self, pars=None, **kwargs):
        super().__init__()

        self.define_pars(
            beta = ss.rate_prob(1.3),           # Transmission rate (Beta)
            gamma = ss.rate_prob(3/12),         # Recovery rate (Gamma) - 3 months
            waning = ss.rate_prob(0.055),       # Immunity waning rate
            p_death = ss.bernoulli(p=0.05),     # Mortality rate
            vaccine_efficacy = 0.9,             # Vaccine efficacy (90%)
            vaccine_prob = 0.25,                # Vaccination probability
        )
        self.update_pars(pars=pars, **kwargs)

        # Define states for SIS model
        self.define_states(
            ss.State('susceptible', default=True, label='Susceptible'),
            ss.State('infected', label='Infected'),
            ss.State('immune', label='Immune'),         # Temporary immunity from vaccination
            ss.FloatArr('ti_infected', label='Time of infection'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.FloatArr('ti_waned', label='Time of immunity waning'),
            ss.FloatArr('time_vaccinated', label='Time of vaccination'),
        )
        
        # Initialize with some infections if specified
        # This will be called after the simulation is initialized
        
        return

    def step(self):
        super().step()
        sim = self.sim

        # Use current indices of susceptibles
        sus_idx = np.where(self.susceptible)[0]
        inf = self.infected
        
        if np.sum(inf) > 0:
            inf_prop = np.sum(inf) / len(self.susceptible)
            # Handle both rate_prob objects and floats
            if hasattr(self.pars.beta, 'p'):
                beta_value = self.pars.beta.p
            else:
                beta_value = self.pars.beta
            transmission_prob = beta_value * inf_prop
            will_infect = np.random.random(len(sus_idx)) < transmission_prob
            new_infections = sus_idx[will_infect]
        else:
            background_prob = 0.001  # Small background transmission rate
            will_infect = np.random.random(len(sus_idx)) < background_prob
            new_infections = sus_idx[will_infect]
        
        if len(new_infections):
            self.set_prognoses(new_infections)
        
        # Apply recovery and immunity waning
        self.apply_recovery()
        self.apply_waning()
        
        return

    def set_prognoses(self, uids, source_uids=None):
        super().set_prognoses(uids, source_uids)
        ti = self.sim.ti
        
        # Convert to proper Starsim indices
        idx = ss.uids(uids)
        
        # Set infection states
        self.susceptible[idx] = False
        self.infected[idx] = True
        self.ti_infected[idx] = ti
        
        # Set recovery time
        if hasattr(self.pars.gamma, 'rvs'):
            recovery_time = self.pars.gamma.rvs(len(uids))
        else:
            recovery_time = np.random.exponential(1/self.pars.gamma, len(uids))
        self.ti_recovered[idx] = ti + recovery_time
        
        return

    def step_state(self):
        ti = self.ti

        # Progress infected to recovered (SIS - back to susceptible)
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        self.infected[recovered] = False
        self.susceptible[recovered] = True  # SIS: recovered become susceptible again

        # Trigger deaths
        dead = (self.ti_dead <= ti).uids
        if len(dead):
            self.sim.people.request_death(dead)
        return

    def apply_waning(self):
        """Apply immunity waning to recovered individuals"""
        ti = self.sim.ti
        
        # Find recovered individuals whose immunity has waned
        waned = (self.immune) & (self.ti_waned <= ti)
        if np.sum(waned) > 0:
            idx = ss.uids(np.where(waned)[0])
            self.immune[idx] = False
            self.susceptible[idx] = True
            self.ti_waned[idx] = np.inf
        
        return

    def apply_recovery(self):
        """Apply recovery to infected individuals"""
        ti = self.sim.ti
        
        # Find infected individuals who should recover
        recovered = (self.infected) & (self.ti_recovered <= ti)
        if np.sum(recovered) > 0:
            idx = ss.uids(np.where(recovered)[0])
            self.infected[idx] = False
            self.immune[idx] = True
            self.ti_recovered[idx] = np.inf
            
            # Set waning time for recovered individuals
            if hasattr(self.pars.waning, 'rvs'):
                waning_time = self.pars.waning.rvs(len(idx))
            else:
                waning_time = np.random.exponential(1/self.pars.waning, len(idx))
            self.ti_waned[idx] = ti + waning_time
        
        return

    def step_die(self, uids):
        for state in ['susceptible', 'infected', 'immune']:
            if hasattr(self, state):
                arr = getattr(self, state)
                idx = ss.uids(uids)
                arr[idx] = False
        return

    def vaccinate(self, uids):
        """Vaccinate specified individuals"""
        ti = self.ti
        p = self.pars
        
        # Apply vaccination probability
        vacc_prob = p.vaccine_prob
        effective_vacc = np.random.random(len(uids)) < vacc_prob
        vacc_uids = uids[effective_vacc]
        
        if len(vacc_uids) == 0:
            return 0
        
        # Mark vaccination time
        self.time_vaccinated[vacc_uids] = ti
        
        # Apply vaccine efficacy to determine immunity
        effective = np.random.random(len(vacc_uids)) < p.vaccine_efficacy
        immune_uids = vacc_uids[effective]
        
        if len(immune_uids) > 0:
            self.immune[immune_uids] = True
            self.susceptible[immune_uids] = False
            
            # Set immunity waning time
            if hasattr(p.waning, 'rvs'):
                waning_duration = p.waning.rvs(immune_uids)
            else:
                # If waning is a float, convert to time steps
                waning_duration = np.full(len(immune_uids), 1.0 / p.waning)  # Convert rate to duration
            self.ti_waned[immune_uids] = ti + waning_duration
        
        return len(immune_uids)



    def initialize_infections(self):
        """Initialize the population with some infections"""
        p = self.pars
        n_agents = len(self.susceptible)
        
        # Calculate number of initial infections
        n_init_inf = int(n_agents * p.init_prev)
        
        if n_init_inf > 0:
            # Randomly select individuals to be initially infected
            init_inf_uids = np.random.choice(n_agents, size=n_init_inf, replace=False)
            self.set_prognoses(init_inf_uids)
        
        return

    def step_birth(self, uids, **kwargs):
        # Newborns start as susceptible
        idx = ss.uids(uids)
        self.susceptible[idx] = True
        self.infected[idx] = False
        self.immune[idx] = False
        self.ti_infected[idx] = np.inf
        self.ti_recovered[idx] = np.inf
        self.ti_waned[idx] = np.inf
        return


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    dis = Tetanus()
    sim = ss.Sim(
        n_agents=10000,
        diseases=dis,
        start=2000,
        stop=2026,
        verbose=.25
    )
    sim.run()
    sim.plot()
    plt.show()