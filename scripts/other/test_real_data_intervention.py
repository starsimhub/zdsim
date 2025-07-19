#!/usr/bin/env python3
"""
Simple test of the zero-dose vaccination intervention with real data parameters
"""

import starsim as ss
import numpy as np
import json
import os

# Import our custom modules
from zdsim.interventions import ZeroDoseVaccination
from zdsim.disease_models.tetanus import Tetanus
from zdsim.disease_models.measles import Measles
from zdsim.disease_models.diphtheria import Diphtheria

def load_real_data_parameters():
    """Load parameters derived from real data analysis"""
    if os.path.exists('intervention_parameters.json'):
        with open('intervention_parameters.json', 'r') as f:
            params = json.load(f)
        print("Loaded parameters from real data analysis:")
        print(f"  Target coverage rate: {params['coverage_rate']:.1%}")
        print(f"  Campaign months: {params['campaign_months']}")
        print(f"  Zero-dose rate: {params['zero_dose_rate']:.1%}")
        return params
    else:
        print("Warning: intervention_parameters.json not found, using defaults")
        return {
            'coverage_rate': 0.22,
            'campaign_months': [5, 7],
            'zero_dose_rate': 0.93
        }

def test_intervention():
    """Test the intervention with real data parameters"""
    print("TESTING ZERO-DOSE VACCINATION INTERVENTION WITH REAL DATA PARAMETERS")
    print("=" * 70)
    
    # Load real data parameters
    params = load_real_data_parameters()
    
    # Create diseases
    tetanus = Tetanus()
    measles = Measles()
    diphtheria = Diphtheria()
    
    # Create zero-dose vaccination intervention with real parameters
    intervention = ZeroDoseVaccination(
        start_year=2020,
        end_year=2025,
        target_age_min=0,
        target_age_max=5,
        coverage_rate=params['coverage_rate'],
        vaccine_efficacy=0.95,
        campaign_frequency=2,
        seasonal_timing=True
    )
    
    # Create simulation
    sim = ss.Sim(
        n_agents=1000,  # Small population for testing
        diseases=[tetanus, measles, diphtheria],
        interventions=intervention,
        start=2020,
        stop=2025,
        dt=1/12,  # Monthly time steps
        verbose=0.1
    )
    
    print(f"Running simulation with:")
    print(f"  Population size: {sim.pars.n_agents}")
    print(f"  Target coverage: {params['coverage_rate']:.1%}")
    print(f"  Campaign months: {params['campaign_months']}")
    print(f"  Simulation period: 2020-2025")
    
    # Run simulation
    sim.run()
    
    # Get results
    results = intervention.get_results_summary()
    
    print(f"\nINTERVENTION RESULTS:")
    print(f"  Total vaccinations: {results['total_vaccinations']}")
    print(f"  Zero-dose children reached: {results['zero_dose_reached']}")
    print(f"  Coverage achieved: {results['total_vaccinations']/sim.pars.n_agents:.1%}")
    
    # Check disease outcomes
    print(f"\nDISEASE OUTCOMES:")
    for disease_name, disease in sim.diseases.items():
        if hasattr(disease, 'vaccinated'):
            vaccinated = np.sum(disease.vaccinated)
            print(f"  {disease_name}: {vaccinated} vaccinated")
    
    print(f"\nTest completed successfully!")
    return results

if __name__ == "__main__":
    test_intervention() 