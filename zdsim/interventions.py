"""
Intervention modules for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np
import sciris as sc

class ZeroDoseVaccination(ss.Intervention):
    """
    Zero-dose vaccination intervention.
    
    This intervention targets children who have received zero doses of routine vaccines
    and provides them with the DTP-HepB-Hib vaccine.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # Define intervention parameters
        self.define_pars(
            start_day=0,  # Start day of intervention
            end_day=365*50,  # End day of intervention
            coverage=0.8,  # Coverage rate
            efficacy=0.9,  # Vaccine efficacy
            age_min=0,  # Minimum age for vaccination (months)
            age_max=60,  # Maximum age for vaccination (months)
            year=None,  # Specific years for campaign delivery
            routine_prob=0.1,  # Annual probability for routine delivery
        )
        
        # Define states for tracking vaccination
        self.define_states(
            ss.BoolState('vaccinated', default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('doses_received', default=0, label='Number of doses received'),
        )
        
        self.update_pars(pars, **kwargs)
        return
    
    def init_pre(self, sim):
        """Initialize the intervention"""
        super().init_pre(sim)
        
        # Set up time points for vaccination
        if self.pars.year is not None:
            # Campaign delivery
            self.timepoints = []
            for year in self.pars.year:
                ti = sim.t.yearvec.searchsorted(year)
                if ti < len(sim.t.yearvec):
                    self.timepoints.append(ti)
        else:
            # Routine delivery - every timestep within the intervention period
            dt_years = sim.t.dt.years if hasattr(sim.t.dt, 'years') else sim.t.dt
            start_ti = int(self.pars.start_day / (dt_years * 365))
            end_ti = int(self.pars.end_day / (dt_years * 365))
            self.timepoints = list(range(start_ti, min(end_ti, len(sim.t))))
        
        return
    
    def check_eligibility(self):
        """Check who is eligible for vaccination"""
        sim = self.sim
        people = sim.people
        
        # Age eligibility (convert to months)
        age_months = people.age * 12
        age_eligible = (age_months >= self.pars.age_min) & (age_months <= self.pars.age_max)
        
        # Not already vaccinated
        not_vaccinated = ~self.vaccinated
        
        # Combine eligibility criteria
        eligible = age_eligible & not_vaccinated
        
        return eligible.uids
    
    def step(self):
        """Deliver vaccination on eligible timesteps"""
        sim = self.sim
        if sim is None:
            return ss.uids()
        ti = sim.ti
        
        if ti not in self.timepoints:
            return ss.uids()
        
        # Check eligibility
        eligible_uids = self.check_eligibility()
        if len(eligible_uids) == 0:
            return ss.uids()
        
        # Determine who gets vaccinated based on coverage
        if self.pars.year is not None:
            # Campaign delivery - use coverage probability
            prob = self.pars.coverage
        else:
            # Routine delivery: intensity × administrative coverage proxy (both in [0, 1])
            prob = float(self.pars.routine_prob) * float(self.pars.coverage)
            prob = min(1.0, max(0.0, prob))
        
        # Simple random selection based on probability
        n_eligible = len(eligible_uids)
        n_vaccinate = int(n_eligible * prob)
        if n_vaccinate > 0:
            # Randomly select who gets vaccinated
            np.random.seed(int(ti))  # Ensure reproducibility
            selected_indices = np.random.choice(n_eligible, size=n_vaccinate, replace=False)
            vaccinated_uids = eligible_uids[selected_indices]
        else:
            vaccinated_uids = ss.uids()
        
        if len(vaccinated_uids):
            # Apply vaccination
            self.vaccinated[vaccinated_uids] = True
            self.ti_vaccinated[vaccinated_uids] = ti
            self.doses_received[vaccinated_uids] += 1
            
            # Apply vaccine efficacy to diseases
            self.apply_vaccine_effects(vaccinated_uids)
        
        return vaccinated_uids
    
    def apply_vaccine_effects(self, uids):
        """Apply vaccine effects to all target diseases"""
        sim = self.sim
        
        # List of target diseases
        target_diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
        
        for disease_name in target_diseases:
            if disease_name in sim.diseases:
                disease = sim.diseases[disease_name]
                
                # Set vaccinated status in disease module
                disease.vaccinated[uids] = True
                disease.ti_vaccinated[uids] = sim.ti
                
                # Apply immunity based on vaccine efficacy
                immunity_level = self.pars.efficacy
                disease.immunity[uids] = immunity_level
                
                # Update relative susceptibility
                disease.rel_sus[uids] = 1 - immunity_level
        
        return
    
    def init_results(self):
        """Initialize results tracking"""
        super().init_results()
        # Results are automatically tracked through the states
        return
    
    def update_results(self):
        """Update results each timestep"""
        super().update_results()
        # Results are automatically tracked through the states
        return


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
