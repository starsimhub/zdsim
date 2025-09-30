#!/usr/bin/env python3
"""
Comprehensive Disease Analysis including Influenza

This script provides a comprehensive analysis of all diseases including influenza,
comparing baseline vs vaccination scenarios with detailed epidemiological insights.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def create_comprehensive_simulation(n_agents=20000, start=2020, stop=2030):
    """Create comprehensive simulation with all diseases including influenza"""
    
    print("Creating comprehensive simulation with all diseases...")
    
    # Simulation parameters
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=n_agents)
    
    # Create all diseases including influenza
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
        )),
        zds.Influenza(dict(
            beta=ss.peryear(0.42),
            init_prev=ss.bernoulli(p=0.05)
        )),
        zds.Tuberculosis(dict(
            beta=ss.peryear(0.625),
            init_prev=ss.bernoulli(p=0.02),
            treatment_efficacy=0.85
        ))
    ]
    
    # Create networks
    networks = [
        ss.RandomNet(dict(n_contacts=8, dur=0), name='household'),
        ss.RandomNet(dict(n_contacts=15, dur=0), name='community')
    ]
    
    # Create demographics
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
        pars=sim_pars
    )
    
    print(f"✓ Created comprehensive simulation with {n_agents:,} agents")
    print(f"✓ Diseases included: Diphtheria, Tetanus, Pertussis, Hepatitis B, Hib, Influenza")
    
    return sim

def create_vaccination_simulation(n_agents=20000, coverage=0.8, start=2020, stop=2030):
    """Create vaccination simulation with all diseases including influenza"""
    
    print("Creating vaccination simulation with all diseases...")
    
    # Simulation parameters
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1/52,
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=n_agents)
    
    # Create all diseases including influenza
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
        )),
        zds.Influenza(dict(
            beta=ss.peryear(0.42),
            init_prev=ss.bernoulli(p=0.05)
        ))
    ]
    
    # Create vaccination intervention
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=coverage,
        efficacy=0.9,
        age_min=0,
        age_max=60,
        routine_prob=0.2
    ))
    
    # Create networks and demographics
    networks = [
        ss.RandomNet(dict(n_contacts=8, dur=0), name='household'),
        ss.RandomNet(dict(n_contacts=15, dur=0), name='community')
    ]
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
    
    print(f"✓ Created vaccination simulation with {n_agents:,} agents")
    print(f"✓ Vaccination coverage: {coverage:.1%}")
    
    return sim

def analyze_disease_characteristics():
    """Analyze characteristics of all diseases including influenza"""
    
    print("\n" + "="*80)
    print("DISEASE CHARACTERISTICS ANALYSIS")
    print("="*80)
    
    # Disease characteristics from literature
    disease_info = {
        'diphtheria': {
            'r0_range': (1.7, 4.3),
            'cfr_range': (0.05, 0.20),
            'peak_age': '5-15 years',
            'transmission': 'Person-to-person',
            'vaccine_type': 'DTP'
        },
        'tetanus': {
            'r0_range': (0, 0),
            'cfr_range': (0.10, 0.20),
            'peak_age': '15-45 years',
            'transmission': 'Environmental',
            'vaccine_type': 'DTP'
        },
        'pertussis': {
            'r0_range': (5.5, 17.5),
            'cfr_range': (0.001, 0.01),
            'peak_age': '0-5 years',
            'transmission': 'Person-to-person',
            'vaccine_type': 'DTP'
        },
        'hepatitis_b': {
            'r0_range': (0.5, 1.5),
            'cfr_range': (0.01, 0.05),
            'peak_age': '20-40 years',
            'transmission': 'Person-to-person',
            'vaccine_type': 'HepB'
        },
        'hib': {
            'r0_range': (1.0, 2.5),
            'cfr_range': (0.02, 0.05),
            'peak_age': '0-2 years',
            'transmission': 'Person-to-person',
            'vaccine_type': 'Hib'
        },
        'influenza': {
            'r0_range': (1.4, 2.8),
            'cfr_range': (0.001, 0.01),
            'peak_age': 'All ages',
            'transmission': 'Person-to-person',
            'vaccine_type': 'Seasonal'
        }
    }
    
    print("Disease Characteristics Summary:")
    print("-" * 50)
    
    for disease, info in disease_info.items():
        print(f"\n{disease.upper()}:")
        print(f"  R0 Range: {info['r0_range'][0]}-{info['r0_range'][1]}")
        print(f"  CFR Range: {info['cfr_range'][0]:.1%}-{info['cfr_range'][1]:.1%}")
        print(f"  Peak Age: {info['peak_age']}")
        print(f"  Transmission: {info['transmission']}")
        print(f"  Vaccine Type: {info['vaccine_type']}")
    
    return disease_info

def run_comprehensive_analysis():
    """Run comprehensive analysis including influenza"""
    
    print("="*80)
    print("COMPREHENSIVE DISEASE ANALYSIS INCLUDING INFLUENZA")
    print("="*80)
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Analyze disease characteristics
    disease_info = analyze_disease_characteristics()
    
    # Run baseline simulation
    print("\n" + "="*60)
    print("RUNNING BASELINE SIMULATION")
    print("="*60)
    baseline_sim = create_comprehensive_simulation()
    baseline_sim.run()
    
    # Run vaccination simulation
    print("\n" + "="*60)
    print("RUNNING VACCINATION SIMULATION")
    print("="*60)
    vaccination_sim = create_vaccination_simulation()
    vaccination_sim.run()
    
    # Analyze results
    print("\n" + "="*60)
    print("ANALYZING RESULTS")
    print("="*60)
    
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitisb', 'hib', 'influenza']
    results = {}
    
    for disease in diseases:
        if disease in baseline_sim.diseases and disease in vaccination_sim.diseases:
            baseline_disease = baseline_sim.diseases[disease]
            vaccination_disease = vaccination_sim.diseases[disease]
            
            # Get results
            baseline_prev = baseline_disease.results.prevalence
            vaccination_prev = vaccination_disease.results.prevalence
            baseline_cum = baseline_disease.results.cum_infections[-1]
            vaccination_cum = vaccination_disease.results.cum_infections[-1]
            
            # Calculate impact
            cases_averted = baseline_cum - vaccination_cum
            reduction = (cases_averted / baseline_cum * 100) if baseline_cum > 0 else 0
            
            results[disease] = {
                'baseline_prevalence': baseline_prev[-1],
                'vaccination_prevalence': vaccination_prev[-1],
                'baseline_cumulative': baseline_cum,
                'vaccination_cumulative': vaccination_cum,
                'cases_averted': cases_averted,
                'reduction_percent': reduction
            }
    
    # Print results
    print("\n" + "="*60)
    print("COMPREHENSIVE RESULTS SUMMARY")
    print("="*60)
    
    total_cases_averted = 0
    for disease, result in results.items():
        print(f"\n{disease.upper()}:")
        print(f"  Baseline - Final prevalence: {result['baseline_prevalence']:.4f}")
        print(f"  Vaccination - Final prevalence: {result['vaccination_prevalence']:.4f}")
        print(f"  Baseline cumulative cases: {result['baseline_cumulative']:,.0f}")
        print(f"  Vaccination cumulative cases: {result['vaccination_cumulative']:,.0f}")
        print(f"  Cases averted: {result['cases_averted']:,.0f}")
        print(f"  Reduction: {result['reduction_percent']:.1f}%")
        total_cases_averted += result['cases_averted']
    
    print(f"\nTOTAL CASES AVERTED: {total_cases_averted:,.0f}")
    
    # Create comprehensive plots
    print("\n" + "="*60)
    print("CREATING COMPREHENSIVE PLOTS")
    print("="*60)
    create_comprehensive_plots(baseline_sim, vaccination_sim, results)
    
    # Generate influenza-specific analysis
    print("\n" + "="*60)
    print("INFLUENZA-SPECIFIC ANALYSIS")
    print("="*60)
    analyze_influenza_specifics(baseline_sim, vaccination_sim)
    
    print("\n" + "="*80)
    print("COMPREHENSIVE ANALYSIS COMPLETED")
    print("="*80)
    print("✓ All diseases analyzed including influenza")
    print("✓ Baseline vs vaccination comparison completed")
    print("✓ Comprehensive plots generated")
    print("✓ Influenza-specific insights provided")
    
    return baseline_sim, vaccination_sim, results

def create_comprehensive_plots(baseline_sim, vaccination_sim, results):
    """Create comprehensive visualization plots"""
    
    print("Creating comprehensive visualization plots...")
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Comprehensive Disease Analysis Including Influenza\n(Baseline vs Vaccination)', 
                 fontsize=16, fontweight='bold')
    
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitisb', 'hib', 'influenza']
    
    for i, disease in enumerate(diseases):
        if i < 6:  # Only plot first 6 diseases
            row = i // 3
            col = i % 3
            ax = axes[row, col]
            
            if disease in baseline_sim.diseases and disease in vaccination_sim.diseases:
                baseline_disease = baseline_sim.diseases[disease]
                vaccination_disease = vaccination_sim.diseases[disease]
                
                timevec = baseline_disease.results.timevec
                baseline_prev = baseline_disease.results.prevalence
                vaccination_prev = vaccination_disease.results.prevalence
                
                ax.plot(timevec, baseline_prev, 'r-', linewidth=2, label='Baseline', alpha=0.8)
                ax.plot(timevec, vaccination_prev, 'b-', linewidth=2, label='Vaccination', alpha=0.8)
                
                ax.set_xlabel('Time (years)')
                ax.set_ylabel('Prevalence')
                ax.set_title(f'{disease.title()} Prevalence')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Add impact annotation
                if disease in results:
                    reduction = results[disease]['reduction_percent']
                    ax.text(0.05, 0.95, f'Reduction: {reduction:.1f}%', 
                           transform=ax.transAxes, fontsize=10, 
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('comprehensive_disease_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create impact summary plot
    create_impact_summary_plot(results)
    
    print("✓ Comprehensive plots created and saved")

def create_impact_summary_plot(results):
    """Create impact summary plot"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Cases averted plot
    diseases = list(results.keys())
    cases_averted = [results[d]['cases_averted'] for d in diseases]
    reduction_percent = [results[d]['reduction_percent'] for d in diseases]
    
    # Plot cases averted
    bars1 = ax1.bar(diseases, cases_averted, color='skyblue', alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Cases Averted')
    ax1.set_title('Cases Averted by Disease')
    ax1.set_xticklabels([d.title() for d in diseases], rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars1, cases_averted):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cases_averted)*0.01,
                f'{value:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot reduction percentage
    bars2 = ax2.bar(diseases, reduction_percent, color='lightcoral', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Reduction (%)')
    ax2.set_title('Disease Reduction by Vaccination')
    ax2.set_xticklabels([d.title() for d in diseases], rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars2, reduction_percent):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(reduction_percent)*0.01,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('disease_impact_summary.pdf', dpi=300, bbox_inches='tight')
    plt.show()

def analyze_influenza_specifics(baseline_sim, vaccination_sim):
    """Analyze influenza-specific characteristics"""
    
    print("Analyzing influenza-specific characteristics...")
    
    if 'influenza' in baseline_sim.diseases:
        baseline_influenza = baseline_sim.diseases['influenza']
        vaccination_influenza = vaccination_sim.diseases['influenza']
        
        # Analyze seasonal patterns
        timevec = baseline_influenza.results.timevec
        baseline_prev = baseline_influenza.results.prevalence
        vaccination_prev = vaccination_influenza.results.prevalence
        
        print(f"\nInfluenza Analysis:")
        print(f"  Baseline final prevalence: {baseline_prev[-1]:.4f}")
        print(f"  Vaccination final prevalence: {vaccination_prev[-1]:.4f}")
        print(f"  Peak prevalence (baseline): {np.max(baseline_prev):.4f}")
        print(f"  Peak prevalence (vaccination): {np.max(vaccination_prev):.4f}")
        
        # Calculate seasonal variation
        if len(baseline_prev) > 52:  # At least one year of data
            # Calculate coefficient of variation as measure of seasonality
            cv_baseline = np.std(baseline_prev) / np.mean(baseline_prev) if np.mean(baseline_prev) > 0 else 0
            cv_vaccination = np.std(vaccination_prev) / np.mean(vaccination_prev) if np.mean(vaccination_prev) > 0 else 0
            
            print(f"  Seasonal variation (baseline): {cv_baseline:.3f}")
            print(f"  Seasonal variation (vaccination): {cv_vaccination:.3f}")
        
        # Analyze age distribution if available
        if hasattr(baseline_sim.people, 'age'):
            infected_uids = baseline_influenza.infected.uids
            if len(infected_uids) > 0:
                infected_ages = baseline_sim.people.age[infected_uids]
                mean_age = np.mean(infected_ages)
                print(f"  Mean age of infected: {mean_age:.1f} years")
        
        print(f"  Note: Influenza shows seasonal patterns and affects all age groups")
        print(f"  Note: While not in zero-dose programs, influenza modeling provides")
        print(f"        important insights for respiratory disease transmission")
    else:
        print("  Influenza not found in simulation results")

def main():
    """Main function to run comprehensive analysis"""
    
    try:
        baseline_sim, vaccination_sim, results = run_comprehensive_analysis()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print("Files generated:")
        print("  - comprehensive_disease_analysis.pdf")
        print("  - disease_impact_summary.pdf")
        print("\nKey insights:")
        print("  - All diseases including influenza analyzed")
        print("  - Baseline vs vaccination impact quantified")
        print("  - Influenza-specific seasonal patterns identified")
        print("  - Comprehensive epidemiological insights provided")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
