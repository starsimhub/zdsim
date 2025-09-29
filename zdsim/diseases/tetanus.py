"""
Tetanus disease module for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np

class Tetanus(ss.Infection):
    """
    Tetanus disease module.
    
    Tetanus is caused by Clostridium tetani bacteria and is not directly transmissible
    between people. It occurs through wound contamination. The zero-dose vaccine (DTP)
    provides protection against tetanus.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define disease-specific parameters
        # Document requirements: Beta=1.3, gamma=3/12, waning=0.055
        self.define_pars(
            beta=ss.peryear(1.3),  # Document requirement: Beta=1.3
            init_prev=ss.bernoulli(p=0.001),  # Very low initial prevalence
            dur_inf=ss.lognorm_ex(mean=ss.years(3/12)),  # Document requirement: gamma=3/12 (3 months)
            p_death=ss.bernoulli(p=0.1),  # Case Fatality Rate (CFR): 10% without treatment
            p_severe=ss.bernoulli(p=0.3),  # High probability of severe disease
            wound_rate=ss.peryear(0.1),  # Annual wound exposure rate
            waning=ss.peryear(0.055),  # Document requirement: waning=0.055
        )
        
        # Define all states for tetanus
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
            ss.FloatArr('ti_wound', label='Time of wound exposure'),
            reset=True
        )
        
        self.update_pars(pars, **kwargs)
        return
    
    def step(self):
        """Handle tetanus-specific transmission (wound exposure)"""
        # Tetanus is not directly transmissible, but occurs through wound exposure
        # Simulate wound exposure events
        sim = self.sim
        ti = sim.ti
        
        # Check for new wound exposures
        wound_rate = self.pars.wound_rate.to_prob(sim.t.dt)
        susceptible = self.susceptible & ~self.vaccinated
        if len(susceptible):
            # Simple random selection for wound exposure
            susceptible_uids = susceptible.uids
            n_susceptible = len(susceptible_uids)
            n_wounds = int(n_susceptible * wound_rate)
            if n_wounds > 0:
                np.random.seed(int(ti))  # Ensure reproducibility
                selected_indices = np.random.choice(n_susceptible, size=n_wounds, replace=False)
                wound_exposure = susceptible_uids[selected_indices]
                self.ti_wound[wound_exposure] = ti
                
                # Not all wounds lead to tetanus - depends on immunity
                immunity_protection = self.immunity[wound_exposure]
                tetanus_risk = 1 - immunity_protection
                
                # Simple random selection for tetanus cases
                n_tetanus = int(len(wound_exposure) * np.mean(tetanus_risk))
                if n_tetanus > 0:
                    tetanus_indices = np.random.choice(len(wound_exposure), size=n_tetanus, replace=False)
                    tetanus_cases = wound_exposure[tetanus_indices]
                    self.set_prognoses(tetanus_cases, sources=-1)  # Environmental source
        
        return ss.uids()
    
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
    
    def step_state(self):
        """Handle state transitions"""
        sim = self.sim
        ti = sim.ti
        
        # Progress infectious -> recovered
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered] = False
            self.recovered[recovered] = True
            # Natural immunity after recovery
            self.immunity[recovered] = 0.9
        
        # Handle waning immunity (document requirement: waning=0.055)
        waning_rate = self.pars.waning.to_prob(sim.t.dt)
        immune_agents = (self.immunity > 0).uids
        if len(immune_agents):
            # Use numpy random instead of creating new bernoulli distribution
            waning_events = np.random.random(len(immune_agents)) < waning_rate
            waning_uids = immune_agents[waning_events]
            if len(waning_uids):
                # Reduce immunity level
                self.immunity[waning_uids] *= 0.5  # Reduce immunity by half
                # If immunity drops below threshold, become susceptible again
                low_immunity = self.immunity[waning_uids] < 0.1
                if np.any(low_immunity):
                    susceptible_again = waning_uids[low_immunity]
                    self.immunity[susceptible_again] = 0.0
                    self.susceptible[susceptible_again] = True
                    self.recovered[susceptible_again] = False
        
        # Trigger deaths
        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)
        
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
