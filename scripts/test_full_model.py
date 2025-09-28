"""
Test the full zero-dose vaccination model with all diseases.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt

def test_full_model():
    """Test the full model with all diseases and vaccination"""
    
    print("Testing full zero-dose vaccination model...")
    
    # Create simulation parameters
    sim_pars = dict(
        start=2020,
        stop=2025,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=5000)
    
    # Create all diseases
    diseases = [
        zds.Diphtheria(dict(
            beta=ss.peryear(0.15),
            init_prev=ss.bernoulli(p=0.01)
        )),
        zds.Tetanus(dict(
            beta=ss.peryear(0.02),
            init_prev=ss.bernoulli(p=0.001)
        )),
        zds.Pertussis(dict(
            beta=ss.peryear(0.25),
            init_prev=ss.bernoulli(p=0.02)
        )),
        zds.HepatitisB(dict(
            beta=ss.peryear(0.08),
            init_prev=ss.bernoulli(p=0.005)
        )),
        zds.Hib(dict(
            beta=ss.peryear(0.12),
            init_prev=ss.bernoulli(p=0.01)
        ))
    ]
    
    # Create vaccination intervention
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=0.7,      # 70% coverage
        efficacy=0.9,      # 90% efficacy
        age_min=0,         # 0 months
        age_max=60,        # 60 months
        routine_prob=0.1   # 10% annual routine vaccination
    ))
    
    # Create networks and demographics
    networks = [ss.RandomNet(dict(n_contacts=8, dur=0))]
    demographics = [
        ss.Births(dict(birth_rate=25)),
        ss.Deaths(dict(death_rate=8))
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=diseases,
        networks=networks,
        demographics=demographics,
        interventions=[vaccination],
        pars=sim_pars
    )
    
    # Run simulation
    sim.run()
    
    # Analyze results
    print("\n=== DISEASE PREVALENCE RESULTS ===")
    for disease_name in ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']:
        if disease_name in sim.diseases:
            disease = sim.diseases[disease_name]
            prevalence = disease.results.prevalence
            print(f"{disease_name.title()}:")
            print(f"  Initial: {prevalence[0]:.4f}")
            print(f"  Final: {prevalence[-1]:.4f}")
            print(f"  Max: {np.max(prevalence):.4f}")
    
    # Vaccination results
    total_vaccinated = np.count_nonzero(vaccination.vaccinated)
    print(f"\n=== VACCINATION RESULTS ===")
    print(f"Total vaccinated: {total_vaccinated}")
    print(f"Vaccination coverage: {total_vaccinated/len(people):.2%}")
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    disease_names = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for i, disease_name in enumerate(disease_names):
        if disease_name in sim.diseases:
            ax = axes[i]
            disease = sim.diseases[disease_name]
            timevec = disease.results.timevec
            prevalence = disease.results.prevalence
            
            ax.plot(timevec, prevalence, linewidth=2, label=f'{disease_name.title()} Prevalence')
            ax.set_xlabel('Time (years)')
            ax.set_ylabel('Prevalence')
            ax.set_title(f'{disease_name.title()} Prevalence')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    # Hide the last subplot
    axes[-1].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    return sim

if __name__ == '__main__':
    sim = test_full_model()
    print("\nFull model test completed successfully!")
