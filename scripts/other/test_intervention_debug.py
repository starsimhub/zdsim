#!/usr/bin/env python3
"""
Simple test script to debug the Zero-Dose Vaccination intervention
"""

import starsim as ss
import numpy as np
from zdsim.interventions import ZeroDoseVaccination
from zdsim.disease_models.tetanus import Tetanus

def test_intervention():
    """Test the intervention and check tracking"""
    print("=== TESTING ZERO-DOSE VACCINATION INTERVENTION ===")
    
    # Create a simple tetanus disease
    tetanus = Tetanus({
        'exposure_risk': ss.bernoulli(p=0.001),
        'p_death': ss.bernoulli(p=0.05),
        'vaccine_efficacy': 0.95
    })
    
    # Create intervention
    intervention = ZeroDoseVaccination(
        start_year=2020,
        end_year=2025,
        target_age_min=0,
        target_age_max=5,
        coverage_rate=0.22,
        vaccine_efficacy=0.95,
        campaign_frequency=2,
        seasonal_timing=True
    )
    
    # Create simulation - pass intervention as a list
    sim = ss.Sim(
        n_agents=1000,
        diseases=[tetanus],  # Pass as list
        interventions=[intervention],  # Pass as list
        start=2020,
        stop=2025,
        dt=1/12,
        verbose=0
    )
    
    # Run simulation
    sim.run()
    
    # Check intervention results immediately after simulation
    print(f"\n=== INTERVENTION RESULTS (IMMEDIATE) ===")
    print(f"Intervention object ID: {id(intervention)}")
    print(f"Vaccination events: {len(intervention.vaccination_events)}")
    
    if intervention.vaccination_events:
        total_vaccinations = sum([event['vaccinations_given'] for event in intervention.vaccination_events])
        print(f"Total vaccinations given: {total_vaccinations}")
        
        for i, event in enumerate(intervention.vaccination_events):
            print(f"  Event {i+1}: Time {event['time']:.2f}, {event['vaccinations_given']} vaccinations")
    
    print(f"Campaign performance: {len(intervention.campaign_performance)} campaigns")
    if intervention.campaign_performance:
        for campaign_id, data in intervention.campaign_performance.items():
            print(f"  {campaign_id}: {data['vaccinations_given']} vaccinations at time {data['time']:.2f}")
    
    print(f"Zero-dose children reached: {len(intervention.tracking_data['zero_dose_reached'])}")
    
    # Check if intervention is still in simulation
    print(f"\n=== SIMULATION INTERVENTION CHECK ===")
    if hasattr(sim, 'interventions') and sim.interventions:
        for i, interv in enumerate(sim.interventions):
            print(f"Intervention {i}: {type(interv).__name__}, ID: {id(interv)}")
            if isinstance(interv, ZeroDoseVaccination):
                print(f"  Vaccination events: {len(interv.vaccination_events)}")
                if interv.vaccination_events:
                    total = sum([event['vaccinations_given'] for event in interv.vaccination_events])
                    print(f"  Total vaccinations: {total}")
    
    # Try to get results summary
    try:
        results = intervention.get_results_summary()
        print(f"\nResults summary:")
        print(f"  Total vaccinations: {results['total_vaccinations']}")
        print(f"  Zero-dose reached: {results['zero_dose_reached']}")
    except Exception as e:
        print(f"Error getting results summary: {e}")
    
    return intervention, sim

if __name__ == "__main__":
    intervention, sim = test_intervention() 