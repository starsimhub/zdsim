#!/usr/bin/env python3
"""
Debug script to test the zero-dose vaccination intervention
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import starsim as ss
import sciris as sc
import numpy as np
from zdsim import *
from zdsim.interventions import ZeroDoseVaccination

def test_intervention():
    """Test the intervention with a simple simulation"""
    
    print("Creating test simulation...")
    
    # Create a simple simulation
    sim_params = dict(
        start=sc.date('2020-01-01'),
        stop=sc.date('2021-01-01'),
        dt=1/12,  # Monthly time steps
    )
    
    # Create population
    pop = ss.People(n_agents=1000)
    
    # Set up tetanus disease
    tetanus = Tetanus(dict(
        beta=0.001,
        init_prev=0.01,
        vaccine_prob=0.0,  # No routine vaccination
        vaccine_efficacy=0.9,
    ))
    
    # Create intervention
    intervention = ZeroDoseVaccination(
        start_year=2020,
        end_year=2021,
        target_age_min=0,
        target_age_max=5,
        coverage_rate=0.85,
        vaccine_efficacy=0.95,
        campaign_frequency=2,
        seasonal_timing=True,
        vaccine_type='pentacel',
        tracking_level='detailed'
    )
    
    # Create simulation
    sim = ss.Sim(
        people=pop,
        diseases=[tetanus],
        interventions=[intervention],
        demographics=[
            ss.Births(dict(birth_rate=25)),
            ss.Deaths(dict(death_rate=8))
        ],
        pars=sim_params,
    )
    
    # Run the simulation for a few steps to initialize everything
    print("Running simulation for 3 steps...")
    
    # Run the simulation
    sim.run()
    
    print(f"Final population size: {len(sim.people)}")
    print(f"Final age range: {sim.people.age.min():.1f} - {sim.people.age.max():.1f}")
    print(f"Final children under 5: {np.sum(sim.people.age < 5)}")
    print(f"Final children 0-5: {np.sum((sim.people.age >= 0) & (sim.people.age <= 5))}")
    
    # Check vaccination status
    print(f"Final already vaccinated: {np.sum(tetanus.vaccinated)}")
    print(f"Final immune: {np.sum(tetanus.immune)}")
    
    # Check target population
    target_pop = intervention._get_target_population(sim)
    print(f"Final target population size: {len(target_pop)}")
    
    if len(target_pop) > 0:
        print(f"Final target ages: {sim.people.age[target_pop]}")
        # Check if vaccination arrays are initialized
        if hasattr(tetanus, 'vaccinated') and len(tetanus.vaccinated) > 0:
            print(f"Final target vaccinated: {tetanus.vaccinated[target_pop]}")
        else:
            print("Final target vaccinated: Array not initialized")
    
    print("\nSimulation completed.")
    
    print("\nSimulation completed.")

if __name__ == "__main__":
    test_intervention() 