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
            # Routine delivery - use routine probability
            prob = self.pars.routine_prob
        
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
