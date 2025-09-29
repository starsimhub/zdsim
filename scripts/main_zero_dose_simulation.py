"""
Zero-dose vaccination simulation script.

This script runs both baseline (no vaccination) and vaccination scenarios
and compares the results.
"""

import sciris as sc
import numpy as np
import starsim as ss
import zdsim as zds
import matplotlib.pyplot as plt
import seaborn as sns

def make_baseline_sim():
    """Create baseline simulation without vaccination"""
    
    # Simulation parameters
    sim_pars = dict(
        start=2020,
        stop=2030,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    n_agents = 50000
    people = ss.People(n_agents=n_agents)
    
    # Create diseases
    diseases = [
        zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01))),
        zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001))),
        zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02))),
        zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005))),
        zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
    ]
    
    # Create networks
    networks = [
        ss.RandomNet(dict(n_contacts=5, dur=0), name='household'),  # Household contacts
        ss.RandomNet(dict(n_contacts=15, dur=0), name='community')  # Community contacts
    ]
    
    # Create demographics
    demographics = [
        ss.Births(dict(birth_rate=25)),  # 25 births per 1000 per year
        ss.Deaths(dict(death_rate=8))    # 8 deaths per 1000 per year
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=diseases,
        networks=networks,
        demographics=demographics,
        pars=sim_pars
    )
    
    return sim

def make_vaccination_sim():
    """Create simulation with zero-dose vaccination intervention"""
    
    # Start with baseline simulation
    sim = make_baseline_sim()
    
    # Add vaccination intervention
    vaccination = zds.ZeroDoseVaccination(dict(
        start_day=0,
        end_day=365*10,  # 10 years
        coverage=0.8,    # 80% coverage
        efficacy=0.9,    # 90% efficacy
        age_min=0,       # 0 months
        age_max=60,      # 60 months (5 years)
        routine_prob=0.1 # 10% annual routine vaccination
    ))
    
    # Add intervention to simulation
    sim.pars.interventions = [vaccination]
    
    return sim

def run_simulation(sim, label):
    """Run simulation and return results"""
    print(f"Running {label} simulation...")
    sim.run()
    print(f"Completed {label} simulation")
    return sim

def compare_results(baseline_sim, vaccination_sim):
    """Compare results between baseline and vaccination scenarios"""
    
    # Extract results
    baseline_results = {}
    vaccination_results = {}
    
    # Collect disease-specific results
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease_name in diseases:
        if disease_name in baseline_sim.diseases:
            baseline_disease = baseline_sim.diseases[disease_name]
            vaccination_disease = vaccination_sim.diseases[disease_name]
            
            baseline_results[disease_name] = {
                'prevalence': baseline_disease.results.prevalence,
                'new_infections': baseline_disease.results.new_infections,
                'cum_infections': baseline_disease.results.cum_infections,
                'deaths': baseline_disease.results.new_deaths if hasattr(baseline_disease.results, 'new_deaths') else None
            }
            
            vaccination_results[disease_name] = {
                'prevalence': vaccination_disease.results.prevalence,
                'new_infections': vaccination_disease.results.new_infections,
                'cum_infections': vaccination_disease.results.cum_infections,
                'deaths': vaccination_disease.results.new_deaths if hasattr(vaccination_disease.results, 'new_deaths') else None
            }
    
    # Calculate impact metrics
    impact_metrics = {}
    
    for disease_name in diseases:
        if disease_name in baseline_results:
            baseline_cum = baseline_results[disease_name]['cum_infections'][-1]
            vaccination_cum = vaccination_results[disease_name]['cum_infections'][-1]
            
            # Calculate percentage reduction
            reduction = ((baseline_cum - vaccination_cum) / baseline_cum) * 100 if baseline_cum > 0 else 0
            
            impact_metrics[disease_name] = {
                'baseline_cumulative': baseline_cum,
                'vaccination_cumulative': vaccination_cum,
                'reduction_percent': reduction,
                'cases_averted': baseline_cum - vaccination_cum
            }
    
    return baseline_results, vaccination_results, impact_metrics

def plot_comparison(baseline_results, vaccination_results, impact_metrics):
    """Create comparison plots"""
    
    diseases = list(baseline_results.keys())
    n_diseases = len(diseases)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()
    
    # Plot prevalence for each disease
    for i, disease_name in enumerate(diseases):
        ax = axes[i]
        
        baseline_prev = baseline_results[disease_name]['prevalence']
        vaccination_prev = vaccination_results[disease_name]['prevalence']
        
        timevec = np.arange(len(baseline_prev)) / 52  # Convert to years
        
        ax.plot(timevec, baseline_prev, label='Baseline', linewidth=2, alpha=0.8)
        ax.plot(timevec, vaccination_prev, label='With Vaccination', linewidth=2, alpha=0.8)
        
        ax.set_title(f'{disease_name.title()} Prevalence')
        ax.set_xlabel('Time (years)')
        ax.set_ylabel('Prevalence')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Plot impact summary
    ax = axes[-1]
    disease_names = list(impact_metrics.keys())
    reductions = [impact_metrics[d]['reduction_percent'] for d in disease_names]
    
    bars = ax.bar(disease_names, reductions, color=['red', 'blue', 'green', 'orange', 'purple'])
    ax.set_title('Cases Averted by Vaccination')
    ax.set_ylabel('Reduction (%)')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, reduction in zip(bars, reductions):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{reduction:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
    
    return fig

def print_summary(impact_metrics):
    """Print summary of results"""
    
    print("\n" + "="*60)
    print("ZERO-DOSE VACCINATION IMPACT SUMMARY")
    print("="*60)
    
    total_cases_averted = 0
    
    for disease_name, metrics in impact_metrics.items():
        print(f"\n{disease_name.upper()}:")
        print(f"  Baseline cumulative cases: {metrics['baseline_cumulative']:,.0f}")
        print(f"  Vaccination cumulative cases: {metrics['vaccination_cumulative']:,.0f}")
        print(f"  Cases averted: {metrics['cases_averted']:,.0f}")
        print(f"  Reduction: {metrics['reduction_percent']:.1f}%")
        
        total_cases_averted += metrics['cases_averted']
    
    print(f"\nTOTAL CASES AVERTED: {total_cases_averted:,.0f}")
    print("="*60)

def main():
    """Main simulation function"""
    
    print("Starting Zero-Dose Vaccination Simulation")
    print("="*50)
    
    # Create and run baseline simulation
    baseline_sim = make_baseline_sim()
    baseline_sim = run_simulation(baseline_sim, "Baseline")
    
    # Create and run vaccination simulation
    vaccination_sim = make_vaccination_sim()
    vaccination_sim = run_simulation(vaccination_sim, "Vaccination")
    
    # Compare results
    baseline_results, vaccination_results, impact_metrics = compare_results(baseline_sim, vaccination_sim)
    
    # Create plots
    fig = plot_comparison(baseline_results, vaccination_results, impact_metrics)
    
    # Create tetanus-focused plots
    print("\n" + "="*60)
    print("TETANUS-FOCUSED ANALYSIS")
    print("="*60)
    
    # Use the new tetanus plotting functions
    try:
        fig_tetanus_baseline = zds.plots.plot_tetanus_focus(baseline_sim, "BASELINE - TETANUS FOCUS")
        plt.show()
        
        fig_tetanus_vaccination = zds.plots.plot_tetanus_focus(vaccination_sim, "VACCINATION - TETANUS FOCUS")
        plt.show()
        
        fig_tetanus_comparison = zds.plots.plot_tetanus_comparison(baseline_sim, vaccination_sim, "TETANUS COMPARISON")
        plt.show()
        
        print("Tetanus-focused plots created successfully!")
        
    except Exception as e:
        print(f"Note: Tetanus-focused plots could not be created: {e}")
        print("This is expected if the plotting functions are not yet available.")
    
    # Print summary
    print_summary(impact_metrics)
    
    # Save results
    results = {
        'baseline_results': baseline_results,
        'vaccination_results': vaccination_results,
        'impact_metrics': impact_metrics
    }
    
    sc.save('zerodose_simulation_results.obj', results)
    print("\nResults saved to 'zerodose_simulation_results.obj'")
    
    return baseline_sim, vaccination_sim, results

if __name__ == '__main__':
    baseline_sim, vaccination_sim, results = main()
