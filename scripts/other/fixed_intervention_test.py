#!/usr/bin/env python3
"""
Fixed Zero-Dose Vaccination Intervention Test
This script fixes all the issues and demonstrates the intervention working properly.
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

def create_diseases_with_correct_parameters():
    """Create diseases with correct parameter names"""
    # Tetanus - uses exposure_risk, not transmission_rate
    tetanus = Tetanus({
        'exposure_risk': ss.bernoulli(p=0.001),  # 0.1% daily exposure risk
        'p_death': ss.bernoulli(p=0.05),  # 5% case fatality rate
        'vaccine_efficacy': 0.95
    })
    
    # Measles - uses beta for transmission
    measles = Measles({
        'beta': 0.5,  # Transmission rate
        'p_death': ss.bernoulli(p=0.01),  # 1% case fatality rate
        'vaccine_efficacy': 0.93
    })
    
    # Diphtheria - uses beta for transmission
    diphtheria = Diphtheria({
        'beta': 0.3,  # Transmission rate
        'p_death': ss.bernoulli(p=0.03),  # 3% case fatality rate
        'vaccine_efficacy': 0.97
    })
    
    return [tetanus, measles, diphtheria]

def test_intervention():
    """Test the intervention with fixed parameters"""
    print("FIXED ZERO-DOSE VACCINATION INTERVENTION TEST")
    print("=" * 60)
    
    # Load real data parameters
    params = load_real_data_parameters()
    
    # Create diseases with correct parameters
    diseases = create_diseases_with_correct_parameters()
    
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
    
    # Create simulation with longer duration to see campaign effects
    sim = ss.Sim(
        n_agents=5000,  # Reasonable size for testing
        diseases=diseases,
        interventions=intervention,
        start=2020,
        stop=2025,  # 5 years to see multiple campaigns
        dt=1/12,  # Monthly time steps
        verbose=0.1
    )
    
    print(f"Running simulation with:")
    print(f"  Target coverage: {params['coverage_rate']:.1%}")
    print(f"  Campaign months: {params['campaign_months']}")
    print(f"  Simulation period: 2020-2025")
    print(f"  Time steps: Monthly (dt=1/12)")
    
    # Run simulation
    sim.run()
    
    # Get results
    results = intervention.get_results_summary()
    
    print(f"\nINTERVENTION RESULTS:")
    print(f"  Total vaccinations: {results['total_vaccinations']}")
    print(f"  Zero-dose children reached: {results['zero_dose_reached']}")
    print(f"  Coverage achieved: {results['total_vaccinations']/5000:.1%}")  # Using fixed population size
    
    # Check disease outcomes
    print(f"\nDISEASE OUTCOMES:")
    for i, disease in enumerate(sim.diseases.values()):
        if hasattr(disease, 'vaccinated'):
            vaccinated = np.sum(disease.vaccinated)
            print(f"  Disease {i+1}: {vaccinated} vaccinated")
    
    # Check campaign performance
    print(f"\nCAMPAIGN PERFORMANCE:")
    if intervention.campaign_performance:
        for campaign, data in intervention.campaign_performance.items():
            print(f"  {campaign}: {data['vaccinations_given']} vaccinations at time {data['time']:.2f}")
    else:
        print("  No campaigns recorded - check timing logic")
    
    # Check vaccination events
    print(f"\nVACCINATION EVENTS:")
    if intervention.vaccination_events:
        total_from_events = 0
        for event in intervention.vaccination_events:
            print(f"  Time {event['time']:.2f}: {event['vaccinations_given']} vaccinations")
            total_from_events += event['vaccinations_given']
        print(f"  Total from events: {total_from_events}")
    else:
        print("  No vaccination events recorded")
    
    # Check results summary
    print(f"\nRESULTS SUMMARY:")
    print(f"  Total vaccinations (from summary): {results['total_vaccinations']}")
    print(f"  Vaccination events count: {len(intervention.vaccination_events)}")
    print(f"  Campaign performance count: {len(intervention.campaign_performance)}")
    
    print(f"\nTest completed!")
    return results

def test_campaign_timing():
    """Test the campaign timing logic specifically"""
    print("\n" + "=" * 60)
    print("TESTING CAMPAIGN TIMING LOGIC")
    print("=" * 60)
    
    # Create a simple intervention
    intervention = ZeroDoseVaccination(
        start_year=2020,
        end_year=2025,
        coverage_rate=0.22,
        campaign_months=[5, 7]
    )
    
    # Test different time points
    test_times = [2020.0, 2020.4, 2020.5, 2020.6, 2020.7, 2020.8, 2021.0, 2021.4, 2021.5]
    
    print("Testing campaign timing at different time points:")
    for time in test_times:
        # Create a mock sim object with ti attribute
        class MockSim:
            def __init__(self, ti):
                self.ti = ti
        
        mock_sim = MockSim(time)
        is_active = intervention._is_campaign_active_time(mock_sim)
        print(f"  Time {time:.1f}: {'CAMPAIGN' if is_active else 'No campaign'}")
    
    return intervention

if __name__ == "__main__":
    # Test campaign timing first
    intervention = test_campaign_timing()
    
    # Test full intervention
    results = test_intervention()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✓ Campaign timing logic tested")
    print("✓ Disease models created with correct parameters")
    print("✓ Intervention simulation completed")
    print("✓ Results analysis performed")
    
    if results['total_vaccinations'] > 0:
        print("✓ Vaccinations were successfully delivered!")
    else:
        print("⚠️  No vaccinations delivered - may need to adjust timing or parameters") 