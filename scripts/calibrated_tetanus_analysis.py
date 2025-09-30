#!/usr/bin/env python3
"""
Calibrated Tetanus Analysis Script

This script uses the calibrated tetanus parameters from the JSON file
to run tetanus simulations with real-world data-driven parameters.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_calibrated_parameters():
    """Load calibrated parameters from JSON file"""
    
    print("Loading calibrated tetanus parameters...")
    
    # Try to load from the calibration results file
    calibration_files = [
        'tetanus_calibration_results.json',
        'calibrated_tetanus_parameters.json',
        'tetanus_calibration_summary.json'
    ]
    
    calibrated_params = None
    
    for file_path in calibration_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if 'best_parameters' in data:
                    calibrated_params = data['best_parameters']
                    print(f"✓ Loaded calibrated parameters from {file_path}")
                    break
                elif 'calibrated_parameters' in data:
                    calibrated_params = data['calibrated_parameters']
                    print(f"✓ Loaded calibrated parameters from {file_path}")
                    break
            except Exception as e:
                print(f"⚠ Could not load from {file_path}: {e}")
                continue
    
    if calibrated_params is None:
        print("⚠ No calibrated parameters found, using default calibrated values")
        # Use the calibrated values from the documentation
        calibrated_params = {
            'neonatal_wound_rate': 0.0111,
            'peri_neonatal_wound_rate': 0.0213,
            'childhood_wound_rate': 0.0637,
            'adult_wound_rate': 0.6346,
            'maternal_vaccination_efficacy': 0.743,
            'maternal_vaccination_coverage': 0.365,
            'neonatal_cfr': 0.718,
            'peri_neonatal_cfr': 0.521,
            'childhood_cfr': 0.480,
            'adult_cfr': 0.327
        }
    
    return calibrated_params

def create_calibrated_tetanus_simulation(n_agents=20000, start=2020, stop=2030):
    """Create tetanus simulation with calibrated parameters"""
    
    print("Creating tetanus simulation with calibrated parameters...")
    
    # Load calibrated parameters
    calibrated_params = load_calibrated_parameters()
    
    # Simulation parameters
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=n_agents)
    
    # Create tetanus disease with CALIBRATED parameters
    tetanus = zds.Tetanus(dict(
        beta=ss.peryear(0.0),  # Not transmissible (R0 = 0)
        init_prev=ss.bernoulli(p=0.001),  # Initial prevalence
        dur_inf=ss.lognorm_ex(mean=ss.years(3/12)),  # 3 months duration
        p_death=ss.bernoulli(p=0.1),  # General CFR
        p_severe=ss.bernoulli(p=0.3),  # Severe disease probability
        wound_rate=ss.peryear(0.1),  # General wound exposure rate
        waning=ss.peryear(0.055),  # Document requirement: waning=0.055
        
        # CALIBRATED AGE-SPECIFIC PARAMETERS
        neonatal_cfr=calibrated_params['neonatal_cfr'],
        peri_neonatal_cfr=calibrated_params['peri_neonatal_cfr'],
        childhood_cfr=calibrated_params['childhood_cfr'],
        adult_cfr=calibrated_params['adult_cfr'],
        
        # CALIBRATED AGE-SPECIFIC WOUND EXPOSURE RATES
        neonatal_wound_rate=ss.peryear(calibrated_params['neonatal_wound_rate']),
        peri_neonatal_wound_rate=ss.peryear(calibrated_params['peri_neonatal_wound_rate']),
        childhood_wound_rate=ss.peryear(calibrated_params['childhood_wound_rate']),
        adult_wound_rate=ss.peryear(calibrated_params['adult_wound_rate']),
        
        # CALIBRATED MATERNAL VACCINATION PARAMETERS
        maternal_vaccination_efficacy=calibrated_params['maternal_vaccination_efficacy'],
        maternal_vaccination_coverage=calibrated_params['maternal_vaccination_coverage'],
    ))
    
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
        diseases=[tetanus],
        networks=networks,
        demographics=demographics,
        pars=sim_pars
    )
    
    print(f"✓ Created calibrated tetanus simulation with {n_agents:,} agents")
    return sim

def create_calibrated_tetanus_vaccination_simulation(n_agents=20000, coverage=0.8, start=2020, stop=2030):
    """Create tetanus simulation with vaccination and calibrated parameters"""
    
    print("Creating tetanus vaccination simulation with calibrated parameters...")
    
    # Load calibrated parameters
    calibrated_params = load_calibrated_parameters()
    
    # Simulation parameters
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=n_agents)
    
    # Create tetanus disease with CALIBRATED parameters
    tetanus = zds.Tetanus(dict(
        beta=ss.peryear(0.0),  # Not transmissible (R0 = 0)
        init_prev=ss.bernoulli(p=0.001),  # Initial prevalence
        dur_inf=ss.lognorm_ex(mean=ss.years(3/12)),  # 3 months duration
        p_death=ss.bernoulli(p=0.1),  # General CFR
        p_severe=ss.bernoulli(p=0.3),  # Severe disease probability
        wound_rate=ss.peryear(0.1),  # General wound exposure rate
        waning=ss.peryear(0.055),  # Document requirement: waning=0.055
        
        # CALIBRATED AGE-SPECIFIC PARAMETERS
        neonatal_cfr=calibrated_params['neonatal_cfr'],
        peri_neonatal_cfr=calibrated_params['peri_neonatal_cfr'],
        childhood_cfr=calibrated_params['childhood_cfr'],
        adult_cfr=calibrated_params['adult_cfr'],
        
        # CALIBRATED AGE-SPECIFIC WOUND EXPOSURE RATES
        neonatal_wound_rate=ss.peryear(calibrated_params['neonatal_wound_rate']),
        peri_neonatal_wound_rate=ss.peryear(calibrated_params['peri_neonatal_wound_rate']),
        childhood_wound_rate=ss.peryear(calibrated_params['childhood_wound_rate']),
        adult_wound_rate=ss.peryear(calibrated_params['adult_wound_rate']),
        
        # CALIBRATED MATERNAL VACCINATION PARAMETERS
        maternal_vaccination_efficacy=calibrated_params['maternal_vaccination_efficacy'],
        maternal_vaccination_coverage=calibrated_params['maternal_vaccination_coverage'],
    ))
    
    # Create vaccination intervention
    vaccination = zds.ZeroDoseVaccination(dict(
        coverage=coverage,
        efficacy=0.95,
        age_min=0,      # 0 months
        age_max=60,      # 60 months (5 years)
        routine_prob=0.8,  # 80% annual routine vaccination
    ))
    
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
    
    # Create simulation with intervention
    sim = ss.Sim(
        people=people,
        diseases=[tetanus],
        networks=networks,
        demographics=demographics,
        interventions=[vaccination],
        pars=sim_pars
    )
    
    print(f"✓ Created calibrated tetanus vaccination simulation with {n_agents:,} agents")
    return sim

def plot_calibrated_tetanus_analysis(sim, title_suffix=""):
    """Create comprehensive tetanus analysis with calibrated parameters"""
    
    # Get tetanus disease
    tetanus = sim.diseases['tetanus']
    results = tetanus.results
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("viridis")
    
    # Create comprehensive figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'CALIBRATED TETANUS ANALYSIS{title_suffix}', fontsize=16, fontweight='bold')
    
    timevec = results.timevec
    
    # 1. Prevalence over time
    ax1 = axes[0, 0]
    prevalence = results.prevalence
    ax1.plot(timevec, prevalence, 'r-', linewidth=3, label='Tetanus Prevalence', alpha=0.8)
    ax1.fill_between(timevec, prevalence, alpha=0.3, color='red')
    ax1.set_title('Tetanus Prevalence Over Time\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time (years)')
    ax1.set_ylabel('Prevalence')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. Cumulative cases
    ax2 = axes[0, 1]
    cum_infections = results.cum_infections
    ax2.plot(timevec, cum_infections, 'b-', linewidth=3, label='Cumulative Cases', alpha=0.8)
    ax2.fill_between(timevec, cum_infections, alpha=0.3, color='blue')
    ax2.set_title('Cumulative Tetanus Cases\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Cumulative Cases')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Age-specific cases (if available)
    ax3 = axes[0, 2]
    if hasattr(tetanus, 'neonatal') and hasattr(tetanus, 'childhood') and hasattr(tetanus, 'adult'):
        neonatal_cases = np.sum(tetanus.neonatal)
        peri_neonatal_cases = np.sum(tetanus.peri_neonatal) if hasattr(tetanus, 'peri_neonatal') else 0
        childhood_cases = np.sum(tetanus.childhood)
        adult_cases = np.sum(tetanus.adult)
        
        segments = ['Neonatal', 'Peri-neonatal', 'Childhood', 'Adult']
        cases = [neonatal_cases, peri_neonatal_cases, childhood_cases, adult_cases]
        colors = ['red', 'orange', 'yellow', 'green']
        
        bars = ax3.bar(segments, cases, color=colors, alpha=0.7, edgecolor='black')
        ax3.set_title('Age-Specific Tetanus Cases\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Number of Cases')
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, cases):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(cases)*0.01,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'Age-specific data not available', ha='center', va='center', 
                transform=ax3.transAxes, fontsize=12)
        ax3.set_title('Age-Specific Tetanus Cases\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
    
    # 4. Calibrated parameters summary
    ax4 = axes[1, 0]
    ax4.axis('off')
    
    calibrated_params = load_calibrated_parameters()
    params_text = f"""
CALIBRATED PARAMETERS SUMMARY

Age-Specific CFR:
• Neonatal: {calibrated_params['neonatal_cfr']:.1%}
• Peri-neonatal: {calibrated_params['peri_neonatal_cfr']:.1%}
• Childhood: {calibrated_params['childhood_cfr']:.1%}
• Adult: {calibrated_params['adult_cfr']:.1%}

Wound Exposure Rates:
• Neonatal: {calibrated_params['neonatal_wound_rate']:.4f}/year
• Peri-neonatal: {calibrated_params['peri_neonatal_wound_rate']:.4f}/year
• Childhood: {calibrated_params['childhood_wound_rate']:.4f}/year
• Adult: {calibrated_params['adult_wound_rate']:.4f}/year

Maternal Vaccination:
• Efficacy: {calibrated_params['maternal_vaccination_efficacy']:.1%}
• Coverage: {calibrated_params['maternal_vaccination_coverage']:.1%}
"""
    
    ax4.text(0.05, 0.95, params_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # 5. Simulation results summary
    ax5 = axes[1, 1]
    ax5.axis('off')
    
    total_cases = cum_infections[-1] if len(cum_infections) > 0 else 0
    total_new_cases = np.sum(results.new_infections) if len(results.new_infections) > 0 else 0
    peak_prevalence = np.max(prevalence) if len(prevalence) > 0 else 0
    final_prevalence = prevalence[-1] if len(prevalence) > 0 else 0
    
    results_text = f"""
SIMULATION RESULTS SUMMARY

Total Cases: {total_cases:.0f}
New Cases: {total_new_cases:.0f}
Peak Prevalence: {peak_prevalence:.4f}
Final Prevalence: {final_prevalence:.4f}

Population: {len(sim.people):,}
Simulation: {sim.pars.start}-{sim.pars.stop}
Duration: {sim.pars.stop - sim.pars.start} years
"""
    
    ax5.text(0.05, 0.95, results_text, transform=ax5.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    # 6. Vaccination impact (if applicable)
    ax6 = axes[1, 2]
    if hasattr(tetanus, 'vaccinated'):
        vaccinated_count = np.sum(tetanus.vaccinated)
        total_pop = len(sim.people)
        coverage_rate = vaccinated_count / total_pop if total_pop > 0 else 0
        
        categories = ['Vaccinated', 'Unvaccinated']
        values = [vaccinated_count, total_pop - vaccinated_count]
        colors = ['green', 'lightcoral']
        
        ax6.pie(values, labels=categories, autopct='%1.1f%%', colors=colors, startangle=90)
        ax6.set_title('Vaccination Status\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
    else:
        ax6.text(0.5, 0.5, 'No vaccination data', ha='center', va='center', 
                transform=ax6.transAxes, fontsize=12)
        ax6.set_title('Vaccination Status\n(Calibrated Parameters)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def run_calibrated_tetanus_comparison():
    """Run baseline vs vaccination comparison with calibrated parameters"""
    
    print("="*80)
    print("CALIBRATED TETANUS ANALYSIS - BASELINE vs VACCINATION")
    print("="*80)
    
    # Create baseline simulation
    print("\n1. Running baseline simulation (no vaccination)...")
    baseline_sim = create_calibrated_tetanus_simulation(n_agents=20000, start=2020, stop=2030)
    baseline_sim.run()
    
    # Create vaccination simulation
    print("2. Running vaccination simulation...")
    vaccination_sim = create_calibrated_tetanus_vaccination_simulation(n_agents=20000, coverage=0.8, start=2020, stop=2030)
    vaccination_sim.run()
    
    # Create detailed plots for both scenarios
    print("3. Creating calibrated analysis plots...")
    
    # Baseline plots
    fig1 = plot_calibrated_tetanus_analysis(baseline_sim, " - BASELINE (No Vaccination)")
    plt.show()
    
    # Vaccination plots
    fig2 = plot_calibrated_tetanus_analysis(vaccination_sim, " - WITH VACCINATION")
    plt.show()
    
    # Comparison analysis
    print("\n4. Calculating vaccination impact with calibrated parameters...")
    
    baseline_tetanus = baseline_sim.diseases['tetanus']
    vaccination_tetanus = vaccination_sim.diseases['tetanus']
    
    baseline_cases = baseline_tetanus.results.cum_infections[-1]
    vaccination_cases = vaccination_tetanus.results.cum_infections[-1]
    cases_averted = baseline_cases - vaccination_cases
    reduction_percent = (cases_averted / baseline_cases * 100) if baseline_cases > 0 else 0
    
    # Print results
    print(f"\nCALIBRATED TETANUS VACCINATION IMPACT RESULTS:")
    print(f"Baseline Cases: {baseline_cases:.0f}")
    print(f"Vaccination Cases: {vaccination_cases:.0f}")
    print(f"Cases Averted: {cases_averted:.0f}")
    print(f"Case Reduction: {reduction_percent:.1f}%")
    
    # Create comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('CALIBRATED TETANUS VACCINATION IMPACT COMPARISON', fontsize=16, fontweight='bold')
    
    # Prevalence comparison
    ax1 = axes[0, 0]
    timevec = baseline_tetanus.results.timevec
    baseline_prev = baseline_tetanus.results.prevalence
    vaccination_prev = vaccination_tetanus.results.prevalence
    ax1.plot(timevec, baseline_prev, 'r-', linewidth=3, label='Baseline (Calibrated)', alpha=0.8)
    ax1.plot(timevec, vaccination_prev, 'b-', linewidth=3, label='With Vaccination (Calibrated)', alpha=0.8)
    ax1.set_title('Tetanus Prevalence Comparison\n(Calibrated Parameters)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Time (years)')
    ax1.set_ylabel('Prevalence')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative cases comparison
    ax2 = axes[0, 1]
    baseline_cum = baseline_tetanus.results.cum_infections
    vaccination_cum = vaccination_tetanus.results.cum_infections
    ax2.plot(timevec, baseline_cum, 'r-', linewidth=3, label='Baseline (Calibrated)', alpha=0.8)
    ax2.plot(timevec, vaccination_cum, 'b-', linewidth=3, label='With Vaccination (Calibrated)', alpha=0.8)
    ax2.set_title('Cumulative Tetanus Cases\n(Calibrated Parameters)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Cumulative Cases')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Impact summary
    ax3 = axes[1, 0]
    categories = ['Cases Averted']
    values = [cases_averted]
    colors = ['lightblue']
    bars = ax3.bar(categories, values, color=colors, alpha=0.8, edgecolor='black')
    ax3.set_title('Vaccination Impact Summary\n(Calibrated Parameters)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Number Averted')
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # Reduction percentages
    ax4 = axes[1, 1]
    reduction_categories = ['Case Reduction']
    reduction_values = [reduction_percent]
    colors = ['lightgreen']
    bars = ax4.bar(reduction_categories, reduction_values, color=colors, alpha=0.8, edgecolor='black')
    ax4.set_title('Reduction Percentages\n(Calibrated Parameters)', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Reduction (%)')
    ax4.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar, value in zip(bars, reduction_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nCalibrated tetanus analysis completed!")
    print(f"Vaccination shows {reduction_percent:.1f}% reduction in tetanus cases with calibrated parameters.")
    
    return {
        'baseline_cases': baseline_cases,
        'vaccination_cases': vaccination_cases,
        'cases_averted': cases_averted,
        'reduction_percent': reduction_percent
    }

def main():
    """Main function to run calibrated tetanus analysis"""
    
    print("CALIBRATED TETANUS ANALYSIS")
    print("="*50)
    print("This script uses calibrated tetanus parameters from real-world data")
    print("to provide accurate tetanus simulations and analysis.")
    print("")
    
    # Run calibrated comparison
    results = run_calibrated_tetanus_comparison()
    
    print("\n" + "="*50)
    print("CALIBRATED TETANUS ANALYSIS COMPLETED")
    print("="*50)
    print("✓ Used calibrated parameters from real-world data")
    print("✓ Analyzed baseline vs vaccination scenarios")
    print("✓ Generated comprehensive visualizations")
    print("✓ Calculated vaccination impact with calibrated parameters")

if __name__ == '__main__':
    main()
