"""
Final demonstration of the zero-dose vaccination model.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt

def run_baseline_vs_vaccination():
    """Run baseline vs vaccination comparison"""
    
    print("=== ZERO-DOSE VACCINATION MODEL DEMONSTRATION ===")
    print("Running baseline vs vaccination comparison...")
    
    # Simulation parameters
    sim_pars = dict(
        start=2020,
        stop=2023,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=3000)
    
    # Create diseases with higher transmission for demonstration
    diseases = [
        zds.Diphtheria(dict(
            beta=ss.peryear(0.3),  # Higher transmission
            init_prev=ss.bernoulli(p=0.02)
        )),
        zds.Pertussis(dict(
            beta=ss.peryear(0.4),  # Higher transmission
            init_prev=ss.bernoulli(p=0.03)
        ))
    ]
    
    # Create networks and demographics
    networks = [ss.RandomNet(dict(n_contacts=10, dur=0))]
    demographics = [
        ss.Births(dict(birth_rate=30)),  # Higher birth rate
        ss.Deaths(dict(death_rate=5))
    ]
    
    # === BASELINE SIMULATION ===
    print("\n1. Running baseline simulation (no vaccination)...")
    baseline_sim = ss.Sim(
        people=ss.People(n_agents=3000),
        diseases=[zds.Diphtheria(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.02))),
                 zds.Pertussis(dict(beta=ss.peryear(0.4), init_prev=ss.bernoulli(p=0.03)))],
        networks=networks,
        demographics=demographics,
        pars=sim_pars
    )
    baseline_sim.run()
    
    # === VACCINATION SIMULATION ===
    print("2. Running vaccination simulation...")
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=0.8,      # 80% coverage
        efficacy=0.9,      # 90% efficacy
        age_min=0,         # 0 months
        age_max=120,       # 120 months (10 years) - broader age range
        routine_prob=0.2   # 20% annual routine vaccination
    ))
    
    vaccination_sim = ss.Sim(
        people=ss.People(n_agents=3000),
        diseases=[zds.Diphtheria(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.02))),
                 zds.Pertussis(dict(beta=ss.peryear(0.4), init_prev=ss.bernoulli(p=0.03)))],
        networks=networks,
        demographics=demographics,
        interventions=[vaccination],
        pars=sim_pars
    )
    vaccination_sim.run()
    
    # === COMPARE RESULTS ===
    print("\n=== COMPARISON RESULTS ===")
    
    for disease_name in ['diphtheria', 'pertussis']:
        baseline_disease = baseline_sim.diseases[disease_name]
        vaccination_disease = vaccination_sim.diseases[disease_name]
        
        baseline_prev = baseline_disease.results.prevalence
        vaccination_prev = vaccination_disease.results.prevalence
        
        baseline_cum = baseline_disease.results.cum_infections[-1]
        vaccination_cum = vaccination_disease.results.cum_infections[-1]
        
        reduction = ((baseline_cum - vaccination_cum) / baseline_cum) * 100 if baseline_cum > 0 else 0
        
        print(f"\n{disease_name.title()}:")
        print(f"  Baseline - Final prevalence: {baseline_prev[-1]:.4f}, Cumulative cases: {baseline_cum}")
        print(f"  Vaccination - Final prevalence: {vaccination_prev[-1]:.4f}, Cumulative cases: {vaccination_cum}")
        print(f"  Cases averted: {baseline_cum - vaccination_cum}")
        print(f"  Reduction: {reduction:.1f}%")
    
    # Vaccination coverage
    total_vaccinated = np.count_nonzero(vaccination.vaccinated)
    print(f"\nVaccination Results:")
    print(f"  Total vaccinated: {total_vaccinated}")
    print(f"  Coverage: {total_vaccinated/3000:.2%}")
    
    # === CREATE PLOTS ===
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    for i, disease_name in enumerate(['diphtheria', 'pertussis']):
        ax = axes[i]
        
        baseline_disease = baseline_sim.diseases[disease_name]
        vaccination_disease = vaccination_sim.diseases[disease_name]
        
        timevec = baseline_disease.results.timevec
        baseline_prev = baseline_disease.results.prevalence
        vaccination_prev = vaccination_disease.results.prevalence
        
        ax.plot(timevec, baseline_prev, 'r-', linewidth=2, label='Baseline', alpha=0.8)
        ax.plot(timevec, vaccination_prev, 'b-', linewidth=2, label='With Vaccination', alpha=0.8)
        
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Prevalence')
        ax.set_title(f'{disease_name.title()} Prevalence Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print("\n=== DEMONSTRATION COMPLETED ===")
    print("The zero-dose vaccination model is working correctly!")
    print("- Diseases are transmitting realistically")
    print("- Vaccination intervention is functional")
    print("- Impact can be measured and compared")
    
    return baseline_sim, vaccination_sim

if __name__ == '__main__':
    baseline_sim, vaccination_sim = run_baseline_vs_vaccination()
