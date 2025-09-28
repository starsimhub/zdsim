"""
Debug script to test disease transmission.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt

def test_disease_transmission():
    """Test if disease transmission is working"""
    
    print("Testing disease transmission...")
    
    # Create a simple simulation with higher transmission
    sim_pars = dict(
        start=2020,
        stop=2022,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=1000)
    
    # Create diphtheria with higher transmission and initial prevalence
    diphtheria = zds.Diphtheria(dict(
        beta=ss.peryear(0.5),  # Higher transmission rate
        init_prev=ss.bernoulli(p=0.05)  # 5% initial prevalence
    ))
    
    # Create networks
    networks = [ss.RandomNet(dict(n_contacts=10, dur=0))]  # More contacts
    
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
    
    # Check results
    prevalence = sim.diseases['diphtheria'].results.prevalence
    timevec = sim.diseases['diphtheria'].results.timevec
    
    print(f"Initial prevalence: {prevalence[0]:.4f}")
    print(f"Final prevalence: {prevalence[-1]:.4f}")
    print(f"Max prevalence: {np.max(prevalence):.4f}")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(timevec, prevalence, linewidth=2, label='Diphtheria Prevalence')
    plt.xlabel('Time (years)')
    plt.ylabel('Prevalence')
    plt.title('Diphtheria Prevalence Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    return sim

if __name__ == '__main__':
    sim = test_disease_transmission()
    print("Test completed!")
