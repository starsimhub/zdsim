"""
Tuberculosis disease module for zero-dose vaccination simulation.

This module implements tuberculosis (TB) disease modeling with BCG vaccination
intervention, using data from presumed_tuberculosis in the real dataset.
"""

import starsim as ss
import numpy as np

class Tuberculosis(ss.Infection):
    """
    Tuberculosis disease module.
    
    Tuberculosis is a bacterial infection caused by Mycobacterium tuberculosis.
    It primarily affects the lungs but can affect other parts of the body.
    BCG (Bacille Calmette-Guérin) vaccine provides protection against TB.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define disease-specific parameters
        # Literature R0: 0.5-2.0 for TB (moderate transmission)
        # Target R0 ≈ 1.25 (mid-range), with duration ≈ 2.0 years (chronic)
        # Beta = R0 / duration = 1.25 / 2.0 = 0.625 per year
        self.define_pars(
            beta=ss.peryear(0.625),  # Moderate transmission rate
            init_prev=ss.bernoulli(p=0.02),  # Initial prevalence (2% in endemic areas)
            dur_inf=ss.lognorm_ex(mean=ss.years(2.0)),  # Duration of infection (chronic, 2 years)
            p_death=ss.bernoulli(p=0.15),  # Case Fatality Rate (CFR): 15% without treatment
            p_severe=ss.bernoulli(p=0.3),  # Probability of severe disease
            p_latent=ss.bernoulli(p=0.1),  # Probability of latent TB (10% of infections)
            p_reactivation=ss.peryear(0.05),  # Reactivation rate from latent to active (5% per year)
            age_susceptibility=ss.bernoulli(p=0.7),  # Moderate susceptibility across ages
            hiv_susceptibility=ss.bernoulli(p=0.9),  # High susceptibility in HIV+ individuals
            treatment_rate=ss.peryear(0.8),  # Treatment rate (80% of cases treated)
            treatment_efficacy=0.85,  # Treatment efficacy (85% cure rate)
        )
        
        # Define all states for tuberculosis
        self.define_states(
            ss.BoolState('susceptible', default=True, label='Susceptible'),
            ss.BoolState('infected', label='Active TB'),
            ss.BoolState('latent', label='Latent TB'),
            ss.BoolState('recovered', label='Recovered'),
            ss.FloatArr('ti_infected', label='Time of infection'),
            ss.FloatArr('ti_latent', label='Time of latent infection'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.FloatArr('rel_sus', default=1.0, label='Relative susceptibility'),
            ss.FloatArr('rel_trans', default=1.0, label='Relative transmission'),
            ss.BoolState('severe', label='Severe disease'),
            ss.BoolState('treated', label='Under treatment'),
            ss.BoolState('vaccinated', default=False, label='BCG Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of BCG vaccination'),
            ss.FloatArr('immunity', default=0.0, label='BCG immunity level'),
            ss.BoolState('hiv_positive', default=False, label='HIV Positive'),
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
        
        # Determine if latent or active TB
        latent = self.pars.p_latent.rvs(uids)
        latent_uids = uids[latent]
        active_uids = uids[~latent]
        
        if len(latent_uids) > 0:
            self.infected[latent_uids] = False
            self.latent[latent_uids] = True
            self.ti_latent[latent_uids] = ti
        
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
        
        ti = self.t.ti
        
        # Handle latent to active TB reactivation
        latent_uids = self.latent.uids
        if len(latent_uids) > 0:
            reactivation_rate = self.pars.p_reactivation
            reactivation_prob = reactivation_rate * self.t.dt
            reactivate = np.random.random(len(latent_uids)) < reactivation_prob
            if np.any(reactivate):
                reactivate_uids = latent_uids[reactivate]
                self.latent[reactivate_uids] = False
                self.infected[reactivate_uids] = True
                self.ti_infected[reactivate_uids] = ti
        
        # Handle recovery
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
        
        # Handle treatment
        if hasattr(self.pars, 'treatment_rate'):
            treatment_rate = self.pars.treatment_rate
            treatment_prob = treatment_rate * self.t.dt
            infected_uids = self.infected.uids
            if len(infected_uids) > 0:
                treat = np.random.random(len(infected_uids)) < treatment_prob
                if np.any(treat):
                    treat_uids = infected_uids[treat]
                    self.treated[treat_uids] = True
                    
                    # Treatment efficacy
                    if hasattr(self.pars, 'treatment_efficacy'):
                        cure_prob = self.pars.treatment_efficacy
                        cured = np.random.random(len(treat_uids)) < cure_prob
                        if np.any(cured):
                            cured_uids = treat_uids[cured]
                            self.infected[cured_uids] = False
                            self.recovered[cured_uids] = True
                            self.treated[cured_uids] = False
        
        # Handle BCG immunity waning
        if hasattr(self.pars, 'bcg_waning'):
            waning_rate = self.pars.bcg_waning
            vaccinated_uids = self.vaccinated.uids
            if len(vaccinated_uids) > 0:
                waning_prob = waning_rate * self.t.dt
                lose_immunity = np.random.random(len(vaccinated_uids)) < waning_prob
                if np.any(lose_immunity):
                    lose_uids = vaccinated_uids[lose_immunity]
                    self.vaccinated[lose_uids] = False
                    self.immunity[lose_uids] = 0.0
        
        return
    
    def get_beta(self):
        """Get transmission rate with HIV co-infection effects"""
        base_beta = self.pars.beta
        
        # HIV co-infection increases transmission
        if hasattr(self, 'hiv_positive'):
            hiv_uids = self.hiv_positive.uids
            if len(hiv_uids) > 0:
                # HIV+ individuals have higher transmission
                hiv_factor = 2.0  # 2x higher transmission in HIV+ individuals
                return base_beta * hiv_factor
        
        return base_beta
    
    def get_susceptibility(self, uids):
        """Get susceptibility with HIV and BCG effects"""
        base_sus = np.ones(len(uids))
        
        # HIV increases susceptibility
        if hasattr(self, 'hiv_positive'):
            hiv_uids = self.hiv_positive[uids]
            if np.any(hiv_uids):
                base_sus[hiv_uids] *= 3.0  # 3x higher susceptibility in HIV+ individuals
        
        # BCG vaccination reduces susceptibility
        if hasattr(self, 'vaccinated'):
            vaccinated_uids = self.vaccinated[uids]
            if np.any(vaccinated_uids):
                bcg_efficacy = 0.6  # 60% efficacy against TB
                base_sus[vaccinated_uids] *= (1 - bcg_efficacy)
        
        return base_sus
