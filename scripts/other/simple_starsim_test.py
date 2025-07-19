#!/usr/bin/env python3
"""
Simple Starsim API test to understand the correct way to access population information.
"""

import starsim as ss
import numpy as np

def test_starsim_api():
    """Test different ways to access Starsim population information"""
    print("TESTING STARSIM API")
    print("=" * 40)
    
    # Create a simple simulation
    sim = ss.Sim(
        n_agents=1000,
        start=2020,
        stop=2025,
        verbose=0
    )
    
    print(f"Simulation created:")
    print(f"  n_agents parameter: 1000")
    
    # Try different ways to access population
    try:
        print(f"  len(sim.people): {len(sim.people)}")
    except AttributeError as e:
        print(f"  len(sim.people): AttributeError - {e}")
    
    try:
        print(f"  sim.people: {type(sim.people)}")
        if hasattr(sim.people, '__len__'):
            print(f"  sim.people length: {len(sim.people)}")
    except AttributeError as e:
        print(f"  sim.people: AttributeError - {e}")
    
    try:
        print(f"  hasattr(sim, 'people'): {hasattr(sim, 'people')}")
    except:
        print(f"  hasattr(sim, 'people'): Error checking")
    
    try:
        print(f"  hasattr(sim, 'n_agents'): {hasattr(sim, 'n_agents')}")
    except:
        print(f"  hasattr(sim, 'n_agents'): Error checking")
    
    try:
        print(f"  sim.pars.n_agents: {sim.pars.n_agents}")
    except AttributeError as e:
        print(f"  sim.pars.n_agents: AttributeError - {e}")
    
    try:
        print(f"  dir(sim): {[attr for attr in dir(sim) if not attr.startswith('_') and 'agent' in attr.lower()]}")
    except:
        print(f"  dir(sim): Error listing attributes")
    
    # List all available attributes
    try:
        all_attrs = [attr for attr in dir(sim) if not attr.startswith('_')]
        print(f"  All attributes: {all_attrs}")
    except:
        print(f"  All attributes: Error listing")
    
    # Run the simulation
    print(f"\nRunning simulation...")
    sim.run()
    
    print(f"\nAfter running simulation:")
    
    try:
        print(f"  len(sim.people): {len(sim.people)}")
    except AttributeError as e:
        print(f"  len(sim.people): AttributeError - {e}")
    
    try:
        print(f"  sim.pars.n_agents: {sim.pars.n_agents}")
    except AttributeError as e:
        print(f"  sim.pars.n_agents: AttributeError - {e}")
    
    # Test accessing people attributes
    if hasattr(sim, 'people'):
        try:
            print(f"  sim.people.age: {type(sim.people.age)}")
            if hasattr(sim.people.age, '__len__'):
                print(f"  sim.people.age length: {len(sim.people.age)}")
        except AttributeError as e:
            print(f"  sim.people.age: AttributeError - {e}")
        
        try:
            print(f"  sim.people.alive: {type(sim.people.alive)}")
            if hasattr(sim.people.alive, '__len__'):
                print(f"  sim.people.alive length: {len(sim.people.alive)}")
        except AttributeError as e:
            print(f"  sim.people.alive: AttributeError - {e}")
    
    return sim

if __name__ == "__main__":
    sim = test_starsim_api() 