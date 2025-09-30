"""
Tetanus disease module for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np

class Tetanus(ss.Infection):
    """
    Tetanus disease module with age-specific segments.
    
    Tetanus is caused by Clostridium tetani bacteria and is not directly transmissible
    between people. It occurs through wound contamination. The zero-dose vaccine (DTP)
    provides protection against tetanus.
    
    Age-specific segments:
    - Neonatal tetanus (0-28 days): High CFR, maternal vaccination protection
    - Peri-neonatal tetanus (29-60 days): Moderate CFR
    - Childhood tetanus (2 months-15 years): Lower CFR, vaccination protection
    - Adult tetanus (15+ years): Variable CFR, occupational exposure
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define disease-specific parameters
        # Tetanus is not directly transmissible (R0 = 0)
        # Document requirements: Beta=1.3, gamma=3/12, waning=0.055
        self.define_pars(
            beta=ss.peryear(0.0),  # Not transmissible (R0 = 0)
            init_prev=ss.bernoulli(p=0.001),  # Very low initial prevalence
            dur_inf=ss.lognorm_ex(mean=ss.years(3/12)),  # Document requirement: gamma=3/12 (3 months)
            p_death=ss.bernoulli(p=0.1),  # Case Fatality Rate (CFR): 10% without treatment
            p_severe=ss.bernoulli(p=0.3),  # High probability of severe disease
            wound_rate=ss.peryear(0.1),  # Annual wound exposure rate
            waning=ss.peryear(0.055),  # Document requirement: waning=0.055
            
            # Age-specific parameters
            neonatal_cfr=0.8,  # Neonatal tetanus CFR: 80%
            peri_neonatal_cfr=0.4,  # Peri-neonatal tetanus CFR: 40%
            childhood_cfr=0.1,  # Childhood tetanus CFR: 10%
            adult_cfr=0.2,  # Adult tetanus CFR: 20%
            
            # Age-specific wound exposure rates
            neonatal_wound_rate=ss.peryear(0.05),  # Lower wound rate in neonates
            peri_neonatal_wound_rate=ss.peryear(0.08),  # Moderate wound rate
            childhood_wound_rate=ss.peryear(0.15),  # Higher wound rate in active children
            adult_wound_rate=ss.peryear(0.12),  # Adult wound rate
            
            # Maternal vaccination protection for neonates
            maternal_vaccination_efficacy=0.8,  # 80% protection from maternal vaccination
            maternal_vaccination_coverage=0.6,  # 60% maternal vaccination coverage
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
            
            # Age-specific tetanus segments
            ss.BoolState('neonatal', default=False, label='Neonatal tetanus (0-28 days)'),
            ss.BoolState('peri_neonatal', default=False, label='Peri-neonatal tetanus (29-60 days)'),
            ss.BoolState('childhood', default=False, label='Childhood tetanus (2 months-15 years)'),
            ss.BoolState('adult', default=False, label='Adult tetanus (15+ years)'),
            
            # Maternal vaccination status
            ss.BoolState('maternal_vaccinated', default=False, label='Maternal vaccination'),
            ss.FloatArr('maternal_immunity', default=0.0, label='Maternal immunity level'),
            
            reset=True
        )
        
        self.update_pars(pars, **kwargs)
        return
    
    def step(self):
        """Handle tetanus-specific transmission (wound exposure) with age-specific segments"""
        # Tetanus is not directly transmissible, but occurs through wound exposure
        # Simulate wound exposure events with age-specific rates
        sim = self.sim
        ti = sim.ti
        
        # Get age in days for age-specific calculations
        age_days = sim.people.age * 365
        
        # Check for new wound exposures by age group
        susceptible = self.susceptible & ~self.vaccinated
        if len(susceptible):
            susceptible_uids = susceptible.uids
            age_days_susceptible = age_days[susceptible_uids]
            
            # Neonatal tetanus (0-28 days)
            neonatal_mask = age_days_susceptible <= 28
            if np.any(neonatal_mask):
                neonatal_uids = susceptible_uids[neonatal_mask]
                self._handle_age_specific_wounds(neonatal_uids, 'neonatal', ti)
            
            # Peri-neonatal tetanus (29-60 days)
            peri_neonatal_mask = (age_days_susceptible > 28) & (age_days_susceptible <= 60)
            if np.any(peri_neonatal_mask):
                peri_neonatal_uids = susceptible_uids[peri_neonatal_mask]
                self._handle_age_specific_wounds(peri_neonatal_uids, 'peri_neonatal', ti)
            
            # Childhood tetanus (2 months-15 years)
            childhood_mask = (age_days_susceptible > 60) & (age_days_susceptible <= 15*365)
            if np.any(childhood_mask):
                childhood_uids = susceptible_uids[childhood_mask]
                self._handle_age_specific_wounds(childhood_uids, 'childhood', ti)
            
            # Adult tetanus (15+ years)
            adult_mask = age_days_susceptible > 15*365
            if np.any(adult_mask):
                adult_uids = susceptible_uids[adult_mask]
                self._handle_age_specific_wounds(adult_uids, 'adult', ti)
        
        return ss.uids()
    
    def _handle_age_specific_wounds(self, uids, age_group, ti):
        """Handle wound exposure for specific age group"""
        if len(uids) == 0:
            return
        
        # Get age-specific wound rate
        if age_group == 'neonatal':
            wound_rate = self.pars.neonatal_wound_rate.to_prob(self.sim.t.dt)
        elif age_group == 'peri_neonatal':
            wound_rate = self.pars.peri_neonatal_wound_rate.to_prob(self.sim.t.dt)
        elif age_group == 'childhood':
            wound_rate = self.pars.childhood_wound_rate.to_prob(self.sim.t.dt)
        elif age_group == 'adult':
            wound_rate = self.pars.adult_wound_rate.to_prob(self.sim.t.dt)
        else:
            wound_rate = self.pars.wound_rate.to_prob(self.sim.t.dt)
        
        # Calculate number of wounds
        n_susceptible = len(uids)
        n_wounds = int(n_susceptible * wound_rate)
        
        if n_wounds > 0:
            np.random.seed(int(ti))  # Ensure reproducibility
            selected_indices = np.random.choice(n_susceptible, size=n_wounds, replace=False)
            wound_exposure = uids[selected_indices]
            self.ti_wound[wound_exposure] = ti
            
            # Calculate tetanus risk based on immunity and age group
            immunity_protection = self.immunity[wound_exposure]
            
            # Maternal vaccination protection for neonates
            if age_group == 'neonatal':
                maternal_protection = self.maternal_immunity[wound_exposure]
                total_protection = np.maximum(immunity_protection, maternal_protection)
            else:
                total_protection = immunity_protection
            
            tetanus_risk = 1 - total_protection
            
            # Simple random selection for tetanus cases
            n_tetanus = int(len(wound_exposure) * np.mean(tetanus_risk))
            if n_tetanus > 0:
                tetanus_indices = np.random.choice(len(wound_exposure), size=n_tetanus, replace=False)
                tetanus_cases = wound_exposure[tetanus_indices]
                self.set_prognoses(tetanus_cases, sources=-1, age_group=age_group)
    
    def set_prognoses(self, uids, sources=None, age_group=None):
        """Set prognoses upon infection with age-specific segments"""
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti
        
        # Set age-specific tetanus segment
        if age_group:
            if age_group == 'neonatal':
                self.neonatal[uids] = True
            elif age_group == 'peri_neonatal':
                self.peri_neonatal[uids] = True
            elif age_group == 'childhood':
                self.childhood[uids] = True
            elif age_group == 'adult':
                self.adult[uids] = True
        
        # Determine disease severity
        severe = self.pars.p_severe.rvs(uids)
        self.severe[uids] = severe
        
        p = self.pars
        
        # Sample duration of infection
        dur_inf = p.dur_inf.rvs(uids)
        
        # Determine CFR based on age group
        if age_group == 'neonatal':
            cfr = p.neonatal_cfr
        elif age_group == 'peri_neonatal':
            cfr = p.peri_neonatal_cfr
        elif age_group == 'childhood':
            cfr = p.childhood_cfr
        elif age_group == 'adult':
            cfr = p.adult_cfr
        else:
            cfr = p.p_death.p if hasattr(p.p_death, 'p') else 0.1  # Default CFR
        
        # Determine who dies and who recovers and when
        will_die = np.random.random(len(uids)) < cfr
        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        
        return
    
    def initialize_maternal_vaccination(self, sim):
        """Initialize maternal vaccination status for neonates"""
        # This would be called when new births occur
        # For now, we'll set maternal vaccination status based on coverage
        if hasattr(sim, 'demographics'):
            births = sim.demographics.get('births', None)
            if births is not None:
                new_births = births.new_births.uids
                if len(new_births) > 0:
                    # Set maternal vaccination status based on coverage
                    maternal_coverage = self.pars.maternal_vaccination_coverage
                    maternal_vaccinated = np.random.random(len(new_births)) < maternal_coverage
                    
                    self.maternal_vaccinated[new_births] = maternal_vaccinated
                    self.maternal_immunity[new_births] = np.where(
                        maternal_vaccinated, 
                        self.pars.maternal_vaccination_efficacy, 
                        0.0
                    )
    
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
