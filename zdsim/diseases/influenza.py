"""
Influenza disease module for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np

class Influenza(ss.Infection):
    """
    Influenza disease module.
    
    Influenza is a highly contagious respiratory viral infection that can cause
    seasonal epidemics and pandemics. While not typically included in zero-dose
    vaccination programs, it's important for comprehensive disease modeling.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define disease-specific parameters
        # Literature R0: 1.4-2.8 for seasonal influenza
        # Target R0 ≈ 2.1 (mid-range), with duration ≈ 0.05 years (2.5 weeks)
        # Beta = R0 / duration = 2.1 / 0.05 = 42.0 per year
        self.define_pars(
            beta=ss.peryear(42.0),  # High transmission rate
            init_prev=ss.bernoulli(p=0.05),  # Initial prevalence (seasonal)
            dur_inf=ss.lognorm_ex(mean=ss.years(0.05)),  # Duration of infection (2.5 weeks)
            p_death=ss.bernoulli(p=0.001),  # Case Fatality Rate (CFR): 0.1% in general population
            p_severe=ss.bernoulli(p=0.1),  # Probability of severe disease
            age_susceptibility=ss.bernoulli(p=0.8),  # High susceptibility across ages
            seasonal_amplitude=0.3,  # Seasonal variation amplitude
            waning_immunity=ss.peryear(0.5),  # Immunity wanes quickly (6 months)
        )
        
        # Define all states for influenza
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
        super().step_state()
        
        # Handle recovery
        ti = self.t.ti
        recover_inds = (self.infected & (ti >= self.ti_recovered)).uids
        if len(recover_inds):
            self.infected[recover_inds] = False
            self.recovered[recover_inds] = True
            self.susceptible[recover_inds] = False
        
        # Handle death
        die_inds = (self.infected & (ti >= self.ti_dead)).uids
        if len(die_inds):
            self.infected[die_inds] = False
            self.susceptible[die_inds] = False
        
        # Handle immunity waning
        if hasattr(self.pars, 'waning_immunity'):
            waning_rate = self.pars.waning_immunity
            immune_inds = self.recovered.uids
            if len(immune_inds):
                waning_prob = waning_rate * self.t.dt
                lose_immunity = np.random.random(len(immune_inds)) < waning_prob
                if np.any(lose_immunity):
                    lose_inds = immune_inds[lose_immunity]
                    self.recovered[lose_inds] = False
                    self.susceptible[lose_inds] = True
        
        return
    
    def get_beta(self):
        """Get transmission rate with seasonal variation"""
        base_beta = self.pars.beta
        
        # Add seasonal variation (simplified)
        if hasattr(self.pars, 'seasonal_amplitude'):
            # Simple seasonal pattern (peak in winter)
            year_fraction = (self.t.ti % 365) / 365
            seasonal_factor = 1 + self.pars.seasonal_amplitude * np.sin(2 * np.pi * year_fraction)
            return base_beta * seasonal_factor
        
        return base_beta
