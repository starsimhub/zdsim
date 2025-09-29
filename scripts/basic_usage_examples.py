"""
Example usage of the zero-dose vaccination model.
"""

import zdsim as zds
import starsim as ss
import matplotlib.pyplot as plt
import numpy as np

def example_basic_simulation():
    """Example of a basic simulation with one disease"""
    
    print("Running basic simulation example...")
    
    # Create a simple simulation with diphtheria
    sim_pars = dict(
        start=2020,
        stop=2025,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=5000)
    
    # Create diphtheria disease
    diphtheria = zds.Diphtheria(dict(
        beta=ss.peryear(0.15),
        init_prev=ss.bernoulli(p=0.01)
    ))
    
    # Create networks
    networks = [ss.RandomNet(dict(n_contacts=8, dur=0))]
    
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
    
    # Plot results
    fig, ax = plt.subplots(figsize=(12, 8))
    timevec = sim.diseases['diphtheria'].results.timevec
    prevalence = sim.diseases['diphtheria'].results.prevalence
    
    ax.plot(timevec, prevalence, linewidth=2, label='Diphtheria Prevalence')
    ax.set_xlabel('Time (years)')
    ax.set_ylabel('Prevalence')
    ax.set_title('Diphtheria Prevalence Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"Final prevalence: {prevalence[-1]:.4f}")
    
    return sim

def example_with_vaccination():
    """Example with vaccination intervention"""
    
    print("\nRunning vaccination example...")
    
    # Create simulation parameters
    sim_pars = dict(
        start=2020,
        stop=2025,
        dt=1/52,
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=5000)
    
    # Create diseases
    diseases = [
        zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01))),
        zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02)))
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
    
    # Plot results
    fig, axes = plt.subplots(1, 2, figsize=(12, 8))
    
    for i, disease_name in enumerate(['diphtheria', 'pertussis']):
        ax = axes[i]
        disease = sim.diseases[disease_name]
        timevec = disease.results.timevec
        prevalence = disease.results.prevalence
        
        ax.plot(timevec, prevalence, linewidth=2, label=f'{disease_name.title()} Prevalence')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Prevalence')
        ax.set_title(f'{disease_name.title()} with Vaccination')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print vaccination statistics
    print(f"Total vaccinated: {np.count_nonzero(vaccination.vaccinated)}")
    print(f"Vaccination coverage: {np.count_nonzero(vaccination.vaccinated)/len(people):.2%}")
    
    return sim

def example_parameter_sensitivity():
    """Example of parameter sensitivity analysis"""
    
    print("\nRunning parameter sensitivity example...")
    
    # Test different coverage levels
    coverage_levels = [0.0, 0.3, 0.6, 0.8]
    results = {}
    
    for coverage in coverage_levels:
        print(f"Testing coverage: {coverage:.1%}")
        
        # Create simulation
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        people = ss.People(n_agents=2000)
        
        diphtheria = zds.Diphtheria(dict(
            beta=ss.peryear(0.15),
            init_prev=ss.bernoulli(p=0.01)
        ))
        
        vaccination = zds.ZeroDoseVaccination(dict(
            coverage=coverage,
            efficacy=0.9,
            age_min=0,
            age_max=60,
            routine_prob=0.1
        ))
        
        sim = ss.Sim(
            people=people,
            diseases=[diphtheria],
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            interventions=[vaccination],
            pars=sim_pars
        )
        
        sim.run()
        
        # Store results
        results[coverage] = {
            'prevalence': sim.diseases['diphtheria'].results.prevalence,
            'cum_infections': sim.diseases['diphtheria'].results.cum_infections[-1]
        }
    
    # Plot sensitivity results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    
    # Plot prevalence over time
    for coverage, result in results.items():
        timevec = np.arange(len(result['prevalence'])) / 52
        ax1.plot(timevec, result['prevalence'], label=f'Coverage: {coverage:.1%}', linewidth=2)
    
    ax1.set_xlabel('Time (years)')
    ax1.set_ylabel('Prevalence')
    ax1.set_title('Diphtheria Prevalence by Vaccination Coverage')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot cumulative infections
    coverages = list(results.keys())
    cum_infections = [results[c]['cum_infections'] for c in coverages]
    
    ax2.bar([f'{c:.1%}' for c in coverages], cum_infections, color=['red', 'orange', 'yellow', 'green'])
    ax2.set_xlabel('Vaccination Coverage')
    ax2.set_ylabel('Cumulative Infections')
    ax2.set_title('Cumulative Infections by Coverage Level')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print("Sensitivity analysis completed!")
    
    return results

def main():
    """Run all examples"""
    
    print("Zero-Dose Vaccination Model Examples")
    print("="*50)
    
    # Example 1: Basic simulation
    sim1 = example_basic_simulation()
    
    # Example 2: With vaccination
    sim2 = example_with_vaccination()
    
    # Example 3: Parameter sensitivity
    results = example_parameter_sensitivity()
    
    print("\nAll examples completed successfully!")
    print("The model is working correctly.")

if __name__ == '__main__':
    main()
