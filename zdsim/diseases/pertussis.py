"""
Pertussis (Whooping Cough) disease module for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np

class Pertussis(ss.Infection):
    """
    Pertussis disease module.
    
    Pertussis (whooping cough) is a highly contagious respiratory disease.
    The zero-dose vaccine (DTP) provides protection against pertussis.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define disease-specific parameters
        self.define_pars(
            beta=ss.peryear(0.25),  # High transmission rate
            init_prev=ss.bernoulli(p=0.02),  # Initial prevalence
            dur_inf=ss.lognorm_ex(mean=ss.years(0.25)),  # Duration of infection (weeks)
            p_death=ss.bernoulli(p=0.01),  # Low case fatality rate in general population
            p_severe=ss.bernoulli(p=0.05),  # Probability of severe disease
            age_susceptibility=ss.bernoulli(p=0.9),  # Very high susceptibility in children
            waning_immunity=ss.peryear(0.1),  # Immunity wanes over time
        )
        
        # Define all states for pertussis
        self.define_states(
            ss.BoolState('susceptible', default=True, label='Susceptible'),
            ss.BoolState('infected', label='Infected'),
            ss.BoolState('recovered', label='Recovered'),
            ss.FloatArr('ti_infected', label='Time of infection'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.FloatArr('rel_sus', default=1.0, label='Relative susceptibility'),
            ss.FloatArr('rel_trans', default=1.0, label='Relative transmission'),
            ss.BoolState('severe', label='Severe disease'),
            ss.BoolState('vaccinated', default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('immunity', default=0.0, label='Immunity level'),
            reset=True
        )
        
        self.update_pars(pars, **kwargs)
        return
    
    def step_state(self):
        """Handle state transitions and immunity waning"""
        sim = self.sim
        ti = sim.ti
        
        # Progress infectious -> recovered
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered] = False
            self.recovered[recovered] = True
            # Natural immunity after recovery
            self.immunity[recovered] = 0.7
        
        # Handle immunity waning
        self.update_immunity()
        
        # Trigger deaths
        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)
        
        return
    
    def update_immunity(self):
        """Update immunity levels with waning"""
        waning_rate = self.pars.waning_immunity.to_prob(self.sim.t.dt)
        has_immunity = (self.immunity > 0).uids
        if len(has_immunity):
            # Immunity wanes exponentially
            self.immunity[has_immunity] *= (1 - waning_rate)
            # Update relative susceptibility based on immunity
            self.rel_sus[has_immunity] = np.maximum(0, 1 - self.immunity[has_immunity])
    
    def set_prognoses(self, uids, sources=None):
        """Set prognoses upon infection"""
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti
        
        # Determine disease severity
        severe = self.pars.p_severe.rvs(uids)
        self.severe[uids] = severe
        
        p = self.pars
        
        # Sample duration of infection
        dur_inf = p.dur_inf.rvs(uids)
        
        # Determine who dies and who recovers and when
        will_die = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        
        return
    
    def step_die(self, uids):
        """Reset infected/recovered flags for dead agents"""
        self.susceptible[uids] = False
        self.infected[uids] = False
        self.recovered[uids] = False
        return
    
    def init_results(self):
        """Initialize results tracking"""
        super().init_results()
        # Additional results are defined in the states, no need to redefine here
        return
    
    def update_results(self):
        """Update results each timestep"""
        super().update_results()
        # Results are automatically tracked through the states
        return
