"""
Simple test of the zero-dose vaccination model.
"""

import zdsim as zds
import starsim as ss
import numpy as np

def test_basic_vaccination():
    """Test basic vaccination functionality"""
    
    print("Testing basic vaccination functionality...")
    
    # Create a simple simulation
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
        beta=ss.peryear(0.15),
        init_prev=ss.bernoulli(p=0.01)
    ))
    
    # Create vaccination intervention
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=0.5,      # 50% coverage
        efficacy=0.9,      # 90% efficacy
        age_min=0,         # 0 months
        age_max=60,        # 60 months
        routine_prob=0.1   # 10% annual routine vaccination
    ))
    
    # Create networks and demographics
    networks = [ss.RandomNet(dict(n_contacts=5, dur=0))]
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
        interventions=[vaccination],
        pars=sim_pars
    )
    
    # Run simulation
    sim.run()
    
    # Check results
    final_prevalence = sim.diseases['diphtheria'].results.prevalence[-1]
    total_vaccinated = np.count_nonzero(vaccination.vaccinated)
    
    print(f"Final prevalence: {final_prevalence:.4f}")
    print(f"Total vaccinated: {total_vaccinated}")
    print(f"Vaccination coverage: {total_vaccinated/len(people):.2%}")
    
    return sim

if __name__ == '__main__':
    sim = test_basic_vaccination()
    print("Test completed successfully!")
