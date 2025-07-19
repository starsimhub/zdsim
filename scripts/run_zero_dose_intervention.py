#!/usr/bin/env python3
"""
Zero-Dose Vaccination Intervention Demonstration Script
=======================================================

This script demonstrates the comprehensive zero-dose vaccination intervention
for children under 5 years old. It shows how to:

1. Set up a simulation with the intervention
2. Run baseline and intervention scenarios
3. Analyze the impact on zero-dose children
4. Generate comprehensive reports and visualizations
5. Export results for further analysis

The intervention targets children aged 0-5 years who have never received
any routine vaccinations, implementing evidence-based strategies from
successful vaccination campaigns worldwide.

Key Features Demonstrated:
- Age-targeted vaccination (0-5 years)
- Campaign-based delivery with seasonal timing
- Comprehensive tracking and analysis
- Integration with multiple vaccine-preventable diseases
- Evidence-based coverage rates and delivery strategies
"""

import sciris as sc
import numpy as np
import starsim as ss
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path to import zdsim
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zdsim import *
from zdsim.interventions import ZeroDoseVaccination


def create_baseline_simulation():
    """
    Create a baseline simulation without the zero-dose vaccination intervention.
    
    This represents the current state where no targeted intervention exists
    for reaching zero-dose children.
    """
    print("Creating baseline simulation (no zero-dose intervention)...")
    
    # Simulation parameters
    sim_params = dict(
        start=sc.date('2020-01-01'),
        stop=sc.date('2025-12-31'),
        dt=1/12,  # Monthly time steps
    )
    
    # Create population with realistic age distribution
    pop = ss.People(n_agents=10000)
    
    # Set up diseases with realistic parameters
    tetanus = Tetanus(dict(
        beta=0.001,  # Low transmission rate for tetanus (environmental)
        init_prev=0.01,  # 1% initial prevalence
        vaccine_prob=0.1,  # Low routine vaccination probability
        vaccine_efficacy=0.9,
    ))
    
    # Add other vaccine-preventable diseases
    measles = Measles(dict(
        beta=0.8,
        init_prev=0.005,
    ))
    
    diphtheria = Diphtheria(dict(
        beta=0.3,
        init_prev=0.001,
    ))
    
    # Create simulation without zero-dose intervention
    sim = ss.Sim(
        people=pop,
        diseases=[tetanus, measles, diphtheria],
        demographics=[
            ss.Births(dict(birth_rate=25)),  # 25 births per 1000 population per year
            ss.Deaths(dict(death_rate=8))    # 8 deaths per 1000 population per year
        ],
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),
        pars=sim_params,
    )
    
    sim.pars.verbose = 0.1  # Show progress every 10% of simulation
    return sim


def create_intervention_simulation():
    """
    Create a simulation with the zero-dose vaccination intervention.
    
    This represents the scenario where a targeted intervention is implemented
    to reach zero-dose children aged 0-5 years.
    """
    print("Creating intervention simulation (with zero-dose vaccination)...")
    
    # Simulation parameters
    sim_params = dict(
        start=sc.date('2020-01-01'),
        stop=sc.date('2025-12-31'),
        dt=1/12,  # Monthly time steps
    )
    
    # Create population with realistic age distribution
    pop = ss.People(n_agents=10000)
    
    # Set up diseases with same parameters as baseline
    tetanus = Tetanus(dict(
        beta=0.001,
        init_prev=0.01,
        vaccine_prob=0.1,  # Keep routine vaccination low to highlight intervention impact
        vaccine_efficacy=0.9,
    ))
    
    measles = Measles(dict(
        beta=0.8,
        init_prev=0.005,
    ))
    
    diphtheria = Diphtheria(dict(
        beta=0.3,
        init_prev=0.001,
    ))
    
    # Create the zero-dose vaccination intervention
    zero_dose_intervention = ZeroDoseVaccination(
        start_year=2020,
        end_year=2025,
        target_age_min=0,
        target_age_max=5,
        coverage_rate=0.85,  # Target 85% coverage of zero-dose children
        vaccine_efficacy=0.95,  # 95% vaccine efficacy
        campaign_frequency=2,  # 2 campaigns per year
        seasonal_timing=True,  # Account for seasonal patterns
        vaccine_type='pentacel',  # Pentacel vaccine (DTaP-IPV-Hib)
        tracking_level='detailed'
    )
    
    # Create simulation with zero-dose intervention
    sim = ss.Sim(
        people=pop,
        diseases=[tetanus, measles, diphtheria],
        interventions=[zero_dose_intervention],
        demographics=[
            ss.Births(dict(birth_rate=25)),
            ss.Deaths(dict(death_rate=8))
        ],
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),
        pars=sim_params,
    )
    
    sim.pars.verbose = 0.1
    return sim, zero_dose_intervention


def analyze_results(baseline_sim, intervention_sim, intervention):
    """
    Analyze and compare results between baseline and intervention scenarios.
    """
    print("\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    # Get intervention results summary
    intervention_summary = intervention.get_results_summary()
    
    # Compare disease outcomes
    print("\n1. INTERVENTION IMPACT SUMMARY:")
    print("-" * 40)
    print(f"Intervention Period: {intervention_summary['intervention_period']}")
    print(f"Target Population: {intervention_summary['target_population']}")
    print(f"Total Vaccinations Given: {intervention_summary['total_vaccinations']:,}")
    print(f"Zero-Dose Children Reached: {intervention_summary['zero_dose_reached']:,}")
    
    if intervention_summary['total_vaccinations'] > 0:
        zero_dose_percentage = intervention_summary['effectiveness_metrics']['zero_dose_percentage']
        print(f"Percentage of Vaccinations to Zero-Dose Children: {zero_dose_percentage:.1f}%")
    
    # Compare disease outcomes
    print("\n2. DISEASE OUTCOME COMPARISON:")
    print("-" * 40)
    
    for disease_name in ['tetanus', 'measles', 'diphtheria']:
        if disease_name in baseline_sim.results and disease_name in intervention_sim.results:
            baseline_cases = baseline_sim.results[disease_name]['n_infected']
            intervention_cases = intervention_sim.results[disease_name]['n_infected']
            
            baseline_total = np.sum(baseline_cases)
            intervention_total = np.sum(intervention_cases)
            cases_averted = baseline_total - intervention_total
            
            print(f"\n{disease_name.upper()}:")
            print(f"  Baseline cases: {baseline_total:,.0f}")
            print(f"  Intervention cases: {intervention_total:,.0f}")
            print(f"  Cases averted: {cases_averted:,.0f}")
            
            if baseline_total > 0:
                reduction_percentage = (cases_averted / baseline_total) * 100
                print(f"  Reduction: {reduction_percentage:.1f}%")
    
    # Coverage analysis
    print("\n3. COVERAGE ANALYSIS BY AGE:")
    print("-" * 40)
    coverage_by_age = intervention_summary['coverage_by_age']
    for age, data in coverage_by_age.items():
        if data['total_eligible'] > 0:
            coverage_pct = data['coverage_rate'] * 100
            print(f"Age {age}: {coverage_pct:.1f}% coverage ({data['vaccinated']}/{data['total_eligible']})")
    
    # Campaign performance
    print("\n4. CAMPAIGN PERFORMANCE:")
    print("-" * 40)
    campaign_performance = intervention_summary['campaign_performance']
    for campaign, data in campaign_performance.items():
        print(f"{campaign}: {data['vaccinations_given']} vaccinations, {data['zero_dose_reached']} zero-dose children reached")
    
    return intervention_summary


def create_comprehensive_plots(baseline_sim, intervention_sim, intervention):
    """
    Create comprehensive visualizations comparing baseline and intervention scenarios.
    """
    print("\nGenerating comprehensive visualizations...")
    
    # Create a large figure with multiple subplots
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Zero-Dose Vaccination Intervention: Comprehensive Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Disease cases over time comparison
    for i, disease_name in enumerate(['tetanus', 'measles', 'diphtheria']):
        if disease_name in baseline_sim.results and disease_name in intervention_sim.results:
            baseline_cases = baseline_sim.results[disease_name]['n_infected']
            intervention_cases = intervention_sim.results[disease_name]['n_infected']
            
            time_points = np.arange(len(baseline_cases)) * baseline_sim.pars.dt
            
            row = i
            col = 0
            
            axes[row, col].plot(time_points, baseline_cases, 'r-', linewidth=2, label='Baseline', alpha=0.8)
            axes[row, col].plot(time_points, intervention_cases, 'b-', linewidth=2, label='With Intervention', alpha=0.8)
            axes[row, col].set_title(f'{disease_name.upper()} Cases Over Time', fontweight='bold')
            axes[row, col].set_xlabel('Time (years)')
            axes[row, col].set_ylabel('Number of Cases')
            axes[row, col].legend()
            axes[row, col].grid(True, alpha=0.3)
    
    # Plot 2: Intervention-specific results
    intervention.plot_results(figsize=(8, 6))
    
    # Plot 3: Age distribution comparison
    baseline_ages = baseline_sim.people.age
    intervention_ages = intervention_sim.people.age
    
    axes[0, 1].hist(baseline_ages, bins=20, alpha=0.7, color='red', label='Baseline', density=True)
    axes[0, 1].hist(intervention_ages, bins=20, alpha=0.7, color='blue', label='Intervention', density=True)
    axes[0, 1].set_title('Population Age Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Age (years)')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 4: Vaccination coverage over time
    if hasattr(intervention, 'tracking_data') and intervention.tracking_data['vaccinations_given']:
        vaccination_dates = [v['date'] for v in intervention.tracking_data['vaccinations_given']]
        axes[0, 2].hist(vaccination_dates, bins=20, alpha=0.7, color='green')
        axes[0, 2].set_title('Vaccinations Over Time', fontweight='bold')
        axes[0, 2].set_xlabel('Date')
        axes[0, 2].set_ylabel('Number of Vaccinations')
        axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 5: Zero-dose children reached over time
    if intervention.tracking_data['zero_dose_reached']:
        zero_dose_times = [z['time'] for z in intervention.tracking_data['zero_dose_reached']]
        axes[1, 1].hist(zero_dose_times, bins=20, alpha=0.7, color='orange')
        axes[1, 1].set_title('Zero-Dose Children Reached Over Time', fontweight='bold')
        axes[1, 1].set_xlabel('Simulation Time')
        axes[1, 1].set_ylabel('Number of Zero-Dose Children')
        axes[1, 1].grid(True, alpha=0.3)
    
    # Plot 6: Coverage achievement by age
    coverage_by_age = intervention.coverage_by_age
    ages = list(coverage_by_age.keys())
    coverage_rates = [coverage_by_age[age]['coverage_rate'] * 100 for age in ages]
    
    axes[1, 2].bar(ages, coverage_rates, alpha=0.7, color='purple')
    axes[1, 2].axhline(y=intervention.coverage_rate * 100, color='red', linestyle='--', 
                       linewidth=2, label=f'Target ({intervention.coverage_rate*100:.1f}%)')
    axes[1, 2].set_title('Coverage Rate by Age', fontweight='bold')
    axes[1, 2].set_xlabel('Age (years)')
    axes[1, 2].set_ylabel('Coverage Rate (%)')
    axes[1, 2].legend()
    axes[1, 2].grid(True, alpha=0.3)
    
    # Plot 7: Gender distribution of vaccinated children
    if intervention.tracking_data['gender_distribution']:
        gender_counts = {}
        for gender in intervention.tracking_data['gender_distribution']:
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        if gender_counts:
            genders = list(gender_counts.keys())
            counts = list(gender_counts.values())
            axes[2, 0].pie(counts, labels=genders, autopct='%1.1f%%', startangle=90)
            axes[2, 0].set_title('Gender Distribution of Vaccinated Children', fontweight='bold')
    
    # Plot 8: Campaign performance
    campaign_performance = intervention._analyze_campaign_performance()
    if campaign_performance:
        campaigns = list(campaign_performance.keys())
        vaccinations = [campaign_performance[c]['vaccinations_given'] for c in campaigns]
        zero_dose_reached = [campaign_performance[c]['zero_dose_reached'] for c in campaigns]
        
        x = np.arange(len(campaigns))
        width = 0.35
        
        axes[2, 1].bar(x - width/2, vaccinations, width, label='Total Vaccinations', alpha=0.7)
        axes[2, 1].bar(x + width/2, zero_dose_reached, width, label='Zero-Dose Reached', alpha=0.7)
        axes[2, 1].set_title('Campaign Performance', fontweight='bold')
        axes[2, 1].set_xlabel('Campaign Period')
        axes[2, 1].set_ylabel('Number of Children')
        axes[2, 1].set_xticks(x)
        axes[2, 1].set_xticklabels(campaigns, rotation=45)
        axes[2, 1].legend()
        axes[2, 1].grid(True, alpha=0.3)
    
    # Plot 9: Summary statistics
    summary_stats = intervention.get_results_summary()
    axes[2, 2].axis('off')
    
    stats_text = f"""
    INTERVENTION SUMMARY
    
    Total Vaccinations: {summary_stats['total_vaccinations']:,}
    Zero-Dose Reached: {summary_stats['zero_dose_reached']:,}
    
    Coverage Target: {intervention.coverage_rate*100:.1f}%
    Vaccine Efficacy: {intervention.vaccine_efficacy*100:.1f}%
    
    Campaign Frequency: {intervention.campaign_frequency}/year
    Target Age Range: {intervention.target_age_min}-{intervention.target_age_max} years
    
    Average Age Vaccinated: {summary_stats['effectiveness_metrics']['average_age_vaccinated']:.1f} years
    """
    
    axes[2, 2].text(0.1, 0.9, stats_text, transform=axes[2, 2].transAxes, 
                    fontsize=12, verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('zero_dose_intervention_comprehensive_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Comprehensive analysis plot saved as 'zero_dose_intervention_comprehensive_analysis.png'")


def export_detailed_results(intervention):
    """
    Export detailed results for further analysis.
    """
    print("\nExporting detailed results...")
    
    # Export vaccination data
    vaccination_file = intervention.export_results()
    
    # Export summary statistics
    summary = intervention.get_results_summary()
    summary_df = pd.DataFrame([summary])
    summary_file = f"zero_dose_intervention_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary_df.to_csv(summary_file, index=False)
    
    # Export coverage by age
    coverage_data = []
    for age, data in summary['coverage_by_age'].items():
        coverage_data.append({
            'age': age,
            'total_eligible': data['total_eligible'],
            'vaccinated': data['vaccinated'],
            'coverage_rate': data['coverage_rate'],
            'target_coverage': intervention.coverage_rate,
            'achievement_percentage': (data['coverage_rate'] / intervention.coverage_rate * 100) if intervention.coverage_rate > 0 else 0
        })
    
    coverage_df = pd.DataFrame(coverage_data)
    coverage_file = f"zero_dose_coverage_by_age_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    coverage_df.to_csv(coverage_file, index=False)
    
    print(f"Results exported to:")
    print(f"  - {vaccination_file}")
    print(f"  - {summary_file}")
    print(f"  - {coverage_file}")


def main():
    """
    Main function to run the complete zero-dose vaccination intervention demonstration.
    """
    print("="*80)
    print("ZERO-DOSE VACCINATION INTERVENTION DEMONSTRATION")
    print("="*80)
    print("This demonstration shows the impact of a targeted vaccination intervention")
    print("designed to reach zero-dose children aged 0-5 years.")
    print()
    
    try:
        # Create and run baseline simulation
        print("STEP 1: Running baseline simulation...")
        baseline_sim = create_baseline_simulation()
        baseline_sim.run()
        print("✓ Baseline simulation completed")
        
        # Create and run intervention simulation
        print("\nSTEP 2: Running intervention simulation...")
        intervention_sim, intervention = create_intervention_simulation()
        intervention_sim.run()
        print("✓ Intervention simulation completed")
        
        # Analyze results
        print("\nSTEP 3: Analyzing results...")
        summary = analyze_results(baseline_sim, intervention_sim, intervention)
        
        # Create visualizations
        print("\nSTEP 4: Creating visualizations...")
        create_comprehensive_plots(baseline_sim, intervention_sim, intervention)
        
        # Export results
        print("\nSTEP 5: Exporting results...")
        export_detailed_results(intervention)
        
        print("\n" + "="*80)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("Key files generated:")
        print("  - zero_dose_intervention_comprehensive_analysis.png")
        print("  - zero_dose_vaccination_results_*.csv")
        print("  - zero_dose_intervention_summary_*.csv")
        print("  - zero_dose_coverage_by_age_*.csv")
        print()
        print("The intervention successfully demonstrated:")
        print("  ✓ Age-targeted vaccination (0-5 years)")
        print("  ✓ Campaign-based delivery with seasonal timing")
        print("  ✓ Comprehensive tracking and analysis")
        print("  ✓ Integration with multiple vaccine-preventable diseases")
        print("  ✓ Evidence-based coverage rates and delivery strategies")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Please check that all required dependencies are installed and the simulation setup is correct.")
        raise


if __name__ == "__main__":
    main() 