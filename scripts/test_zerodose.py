"""
Test script for zero-dose vaccination simulation.
"""

import sys
import os
sys.path.append('/Users/mine/git/zdsim')

import zdsim as zds
import starsim as ss
import numpy as np

def test_disease_modules():
    """Test that disease modules can be imported and instantiated"""
    
    print("Testing disease modules...")
    
    # Test each disease module
    diseases = [
        zds.Diphtheria(),
        zds.Tetanus(),
        zds.Pertussis(),
        zds.HepatitisB(),
        zds.Hib()
    ]
    
    for disease in diseases:
        print(f"✓ {disease.__class__.__name__} created successfully")
    
    return diseases

def test_vaccination_intervention():
    """Test vaccination intervention"""
    
    print("\nTesting vaccination intervention...")
    
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=0.8,
        efficacy=0.9,
        age_min=0,
        age_max=60
    ))
    
    print("✓ ZeroDoseVaccination created successfully")
    return vaccination

def test_simple_simulation():
    """Test a simple simulation"""
    
    print("\nTesting simple simulation...")
    
    # Create a small simulation
    sim_pars = dict(
        start=2020,
        stop=2022,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=1000)
    
    # Create one disease
    diphtheria = zds.Diphtheria(dict(
        beta=ss.peryear(0.1),
        init_prev=ss.bernoulli(p=0.01)
    ))
    
    # Create networks
    networks = [ss.RandomNet(dict(n_contacts=5, dur=0))]
    
    # Create demographics
    demographics = [
        ss.Births(dict(birth_rate=25)),
        ss.Deaths(dict(death_rate=8))
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=[diphtheria],
        networks=networks,
        demographics=demographics,
        pars=sim_pars
    )
    
    # Run simulation
    sim.run()
    
    print("✓ Simple simulation completed successfully")
    print(f"  Final prevalence: {sim.diseases['diphtheria'].results.prevalence[-1]:.4f}")
    
    return sim

def main():
    """Run all tests"""
    
    print("Zero-Dose Vaccination Model Tests")
    print("="*40)
    
    try:
        # Test disease modules
        diseases = test_disease_modules()
        
        # Test vaccination intervention
        vaccination = test_vaccination_intervention()
        
        # Test simple simulation
        sim = test_simple_simulation()
        
        print("\n" + "="*40)
        print("All tests passed! ✓")
        print("The zero-dose vaccination model is ready to use.")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
