"""
BCG (Bacille Calmette-Guérin) vaccination intervention for tuberculosis prevention.

This intervention implements BCG vaccination for tuberculosis prevention,
using data from BCG vaccination coverage in the real dataset.
"""

import starsim as ss
import numpy as np

class BCGVaccination(ss.Intervention):
    """
    BCG vaccination intervention for tuberculosis prevention.
    
    BCG (Bacille Calmette-Guérin) is a vaccine against tuberculosis.
    It is typically given at birth or in early childhood and provides
    protection against severe forms of TB, especially in children.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define BCG vaccination parameters
        self.define_pars(
            coverage=0.8,  # 80% coverage rate
            efficacy=0.6,  # 60% efficacy against TB
            age_min=0,  # 0 months (birth)
            age_max=12,  # 12 months (1 year)
            routine_prob=0.1,  # 10% annual routine vaccination
            start_day=0,  # Start immediately
            end_day=365*10,  # Continue for 10 years
            waning_rate=ss.peryear(0.02),  # 2% per year waning
            birth_dose_prob=0.8,  # 80% receive birth dose
            catch_up_prob=0.2,  # 20% catch-up vaccination
        )
        
        # Define intervention states
        self.define_states(
            ss.BoolState('vaccinated', default=False, label='BCG Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of BCG vaccination'),
            ss.FloatArr('immunity_level', default=0.0, label='BCG immunity level'),
            ss.BoolState('birth_dose', default=False, label='Birth dose received'),
            ss.BoolState('catch_up', default=False, label='Catch-up vaccination'),
            reset=True
        )
        
        self.update_pars(pars, **kwargs)
        return
    
    def initialize(self, sim):
        """Initialize BCG vaccination intervention"""
        super().initialize(sim)
        
        # Initialize vaccination states
        self.vaccinated = ss.BoolArr(sim.people.n_agents, default=False)
        self.ti_vaccinated = ss.FloatArr(sim.people.n_agents, default=0.0)
        self.immunity_level = ss.FloatArr(sim.people.n_agents, default=0.0)
        self.birth_dose = ss.BoolArr(sim.people.n_agents, default=False)
        self.catch_up = ss.BoolArr(sim.people.n_agents, default=False)
        
        return
    
    def apply(self, sim):
        """Apply BCG vaccination intervention"""
        
        # Birth dose vaccination
        if hasattr(sim, 'demographics'):
            births = sim.demographics.get('births', None)
            if births is not None:
                new_births = births.new_births.uids
                if len(new_births) > 0:
                    self._vaccinate_births(sim, new_births)
        
        # Routine vaccination
        self._routine_vaccination(sim)
        
        # Catch-up vaccination
        self._catch_up_vaccination(sim)
        
        # Update immunity levels
        self._update_immunity(sim)
        
        return
    
    def _vaccinate_births(self, sim, new_births):
        """Vaccinate newborns with BCG"""
        if len(new_births) == 0:
            return
        
        # Birth dose probability
        birth_prob = self.pars.birth_dose_prob
        vaccinate = np.random.random(len(new_births)) < birth_prob
        
        if np.any(vaccinate):
            vaccinate_uids = new_births[vaccinate]
            self._vaccinate_individuals(sim, vaccinate_uids, birth_dose=True)
    
    def _routine_vaccination(self, sim):
        """Routine BCG vaccination"""
        # Get eligible individuals (age 0-12 months, not vaccinated)
        eligible_uids = self._get_eligible_individuals(sim)
        
        if len(eligible_uids) == 0:
            return
        
        # Routine vaccination probability
        routine_prob = self.pars.routine_prob * sim.t.dt
        vaccinate = np.random.random(len(eligible_uids)) < routine_prob
        
        if np.any(vaccinate):
            vaccinate_uids = eligible_uids[vaccinate]
            self._vaccinate_individuals(sim, vaccinate_uids, birth_dose=False)
    
    def _catch_up_vaccination(self, sim):
        """Catch-up BCG vaccination for older children"""
        # Get eligible individuals (age 1-5 years, not vaccinated)
        eligible_uids = self._get_catch_up_eligible(sim)
        
        if len(eligible_uids) == 0:
            return
        
        # Catch-up vaccination probability
        catch_up_prob = self.pars.catch_up_prob * sim.t.dt
        vaccinate = np.random.random(len(eligible_uids)) < catch_up_prob
        
        if np.any(vaccinate):
            vaccinate_uids = eligible_uids[vaccinate]
            self._vaccinate_individuals(sim, vaccinate_uids, birth_dose=False, catch_up=True)
    
    def _get_eligible_individuals(self, sim):
        """Get individuals eligible for routine BCG vaccination"""
        # Age 0-12 months, not vaccinated
        age_months = sim.people.age * 12
        age_eligible = (age_months >= self.pars.age_min) & (age_months <= self.pars.age_max)
        not_vaccinated = ~self.vaccinated
        
        eligible = age_eligible & not_vaccinated
        return np.where(eligible)[0]
    
    def _get_catch_up_eligible(self, sim):
        """Get individuals eligible for catch-up BCG vaccination"""
        # Age 1-5 years, not vaccinated
        age_months = sim.people.age * 12
        age_eligible = (age_months >= 12) & (age_months <= 60)  # 1-5 years
        not_vaccinated = ~self.vaccinated
        
        eligible = age_eligible & not_vaccinated
        return np.where(eligible)[0]
    
    def _vaccinate_individuals(self, sim, uids, birth_dose=False, catch_up=False):
        """Vaccinate specific individuals"""
        if len(uids) == 0:
            return
        
        # Set vaccination status
        self.vaccinated[uids] = True
        self.ti_vaccinated[uids] = sim.t.ti
        
        # Set immunity level
        self.immunity_level[uids] = self.pars.efficacy
        
        # Set dose type
        if birth_dose:
            self.birth_dose[uids] = True
        if catch_up:
            self.catch_up[uids] = True
        
        # Apply to tuberculosis disease if present
        if 'tuberculosis' in sim.diseases:
            tb_disease = sim.diseases['tuberculosis']
            tb_disease.vaccinated[uids] = True
            tb_disease.ti_vaccinated[uids] = sim.t.ti
            tb_disease.immunity[uids] = self.pars.efficacy
    
    def _update_immunity(self, sim):
        """Update BCG immunity levels over time"""
        vaccinated_uids = self.vaccinated.uids
        if len(vaccinated_uids) == 0:
            return
        
        # Calculate waning
        waning_rate = self.pars.waning_rate
        waning_prob = waning_rate * sim.t.dt
        
        # Apply waning to immunity levels
        current_immunity = self.immunity_level[vaccinated_uids]
        waning = np.random.random(len(vaccinated_uids)) < waning_prob
        
        if np.any(waning):
            waning_uids = vaccinated_uids[waning]
            # Reduce immunity by 10% per waning event
            self.immunity_level[waning_uids] *= 0.9
            
            # Remove vaccination if immunity drops below threshold
            low_immunity = self.immunity_level[waning_uids] < 0.1
            if np.any(low_immunity):
                remove_uids = waning_uids[low_immunity]
                self.vaccinated[remove_uids] = False
                self.immunity_level[remove_uids] = 0.0
    
    def get_coverage(self, sim):
        """Get current BCG vaccination coverage"""
        total_population = len(sim.people)
        vaccinated_count = np.sum(self.vaccinated)
        return vaccinated_count / total_population if total_population > 0 else 0.0
    
    def get_age_coverage(self, sim, age_min=0, age_max=12):
        """Get BCG vaccination coverage for specific age group"""
        age_months = sim.people.age * 12
        age_mask = (age_months >= age_min) & (age_months <= age_max)
        
        if np.sum(age_mask) == 0:
            return 0.0
        
        age_vaccinated = self.vaccinated[age_mask]
        return np.sum(age_vaccinated) / np.sum(age_mask)
