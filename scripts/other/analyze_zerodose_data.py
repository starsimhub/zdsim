#!/usr/bin/env python3
"""
Analyze Zero-Dose Vaccination Data
This script analyzes the real vaccination data to extract realistic parameters
for the zero-dose vaccination intervention.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_and_analyze_data():
    """Load and analyze the zero-dose vaccination data"""
    print("Loading zero-dose vaccination data...")
    
    # Load the data
    df = pd.read_csv('data/zerodose_data.csv')
    
    print(f"Data loaded: {len(df)} records from {df['year'].min()} to {df['year'].max()}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def analyze_vaccination_coverage(df):
    """Analyze vaccination coverage patterns"""
    print("\n=== VACCINATION COVERAGE ANALYSIS ===")
    
    # Key vaccination columns
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'measles1', 'measles2', 'opv1', 'opv2', 'opv3', 'bcg']
    
    # Calculate annual averages
    annual_data = df.groupby('year')[vaccine_cols].mean()
    
    print("\nAnnual Average Vaccination Coverage:")
    print(annual_data.round(0))
    
    # Calculate coverage rates relative to estimated live births
    coverage_rates = {}
    for vaccine in vaccine_cols:
        if vaccine in df.columns and 'estimated_lb' in df.columns:
            coverage = (df[vaccine] / df['estimated_lb'] * 100).mean()
            coverage_rates[vaccine] = coverage
            print(f"{vaccine.upper()}: {coverage:.1f}% coverage")
    
    # Analyze zero-dose children (those not receiving DPT1)
    if 'dpt1' in df.columns and 'estimated_lb' in df.columns:
        zero_dose_rate = ((df['estimated_lb'] - df['dpt1']) / df['estimated_lb'] * 100).mean()
        print(f"\nZero-dose children (no DPT1): {zero_dose_rate:.1f}%")
    
    return coverage_rates, annual_data

def analyze_disease_incidence(df):
    """Analyze disease incidence patterns"""
    print("\n=== DISEASE INCIDENCE ANALYSIS ===")
    
    # Key disease columns
    disease_cols = ['tetanus', 'measles', 'diphtheria', 'pneumonia', 'poliomyelitis']
    
    # Calculate annual averages
    annual_diseases = df.groupby('year')[disease_cols].mean()
    
    print("\nAnnual Average Disease Cases:")
    print(annual_diseases.round(0))
    
    # Calculate case rates per 100,000 population
    if 'estimated_lb' in df.columns:
        case_rates = {}
        for disease in disease_cols:
            if disease in df.columns:
                rate = (df[disease] / df['estimated_lb'] * 100000).mean()
                case_rates[disease] = rate
                print(f"{disease.upper()}: {rate:.1f} cases per 100,000 population")
    
    return case_rates, annual_diseases

def analyze_seasonal_patterns(df):
    """Analyze seasonal patterns in vaccination and disease"""
    print("\n=== SEASONAL PATTERN ANALYSIS ===")
    
    # Convert month names to numbers
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['month_num'] = df['month'].map(month_map)
    
    # Analyze vaccination patterns by month
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'measles1', 'measles2']
    monthly_vaccines = df.groupby('month_num')[vaccine_cols].mean()
    
    print("\nMonthly Average Vaccination Coverage:")
    print(monthly_vaccines.round(0))
    
    # Analyze disease patterns by month
    disease_cols = ['tetanus', 'measles', 'diphtheria']
    monthly_diseases = df.groupby('month_num')[disease_cols].mean()
    
    print("\nMonthly Average Disease Cases:")
    print(monthly_diseases.round(0))
    
    return monthly_vaccines, monthly_diseases

def analyze_age_distribution(df):
    """Analyze age-specific patterns"""
    print("\n=== AGE DISTRIBUTION ANALYSIS ===")
    
    # Age-specific columns
    age_cols = ['fic_under_1yr', 'fic_at_1yr', 'fic_above_2yrs']
    
    if all(col in df.columns for col in age_cols):
        annual_age_data = df.groupby('year')[age_cols].mean()
        
        print("\nAnnual Average Age Distribution:")
        print(annual_age_data.round(0))
        
        # Calculate age-specific vaccination rates
        if 'dpt1' in df.columns:
            under1_rate = (df['fic_under_1yr'] / df['estimated_lb'] * 100).mean()
            at1_rate = (df['fic_at_1yr'] / df['estimated_lb'] * 100).mean()
            above2_rate = (df['fic_above_2yrs'] / df['estimated_lb'] * 100).mean()
            
            print(f"\nAge-specific vaccination rates:")
            print(f"Under 1 year: {under1_rate:.1f}%")
            print(f"At 1 year: {at1_rate:.1f}%")
            print(f"Above 2 years: {above2_rate:.1f}%")
    
    return annual_age_data if all(col in df.columns for col in age_cols) else None

def create_visualizations(df, coverage_rates, case_rates, monthly_vaccines, monthly_diseases):
    """Create comprehensive visualizations of the data"""
    print("\n=== CREATING VISUALIZATIONS ===")
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Zero-Dose Vaccination Data Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Vaccination coverage over time
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'measles1', 'measles2']
    annual_data = df.groupby('year')[vaccine_cols].mean()
    
    for vaccine in vaccine_cols:
        if vaccine in annual_data.columns:
            axes[0, 0].plot(annual_data.index, annual_data[vaccine], marker='o', label=vaccine.upper())
    
    axes[0, 0].set_title('Vaccination Coverage Over Time')
    axes[0, 0].set_xlabel('Year')
    axes[0, 0].set_ylabel('Number of Vaccinations')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Disease incidence over time
    disease_cols = ['tetanus', 'measles', 'diphtheria']
    annual_diseases = df.groupby('year')[disease_cols].mean()
    
    for disease in disease_cols:
        if disease in annual_diseases.columns:
            axes[0, 1].plot(annual_diseases.index, annual_diseases[disease], marker='s', label=disease.upper())
    
    axes[0, 1].set_title('Disease Incidence Over Time')
    axes[0, 1].set_xlabel('Year')
    axes[0, 1].set_ylabel('Number of Cases')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Monthly vaccination patterns
    if monthly_vaccines is not None:
        for vaccine in vaccine_cols:
            if vaccine in monthly_vaccines.columns:
                axes[0, 2].plot(monthly_vaccines.index, monthly_vaccines[vaccine], marker='o', label=vaccine.upper())
        
        axes[0, 2].set_title('Monthly Vaccination Patterns')
        axes[0, 2].set_xlabel('Month')
        axes[0, 2].set_ylabel('Average Vaccinations')
        axes[0, 2].set_xticks(range(1, 13))
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
    
    # Plot 4: Monthly disease patterns
    if monthly_diseases is not None:
        for disease in disease_cols:
            if disease in monthly_diseases.columns:
                axes[1, 0].plot(monthly_diseases.index, monthly_diseases[disease], marker='s', label=disease.upper())
        
        axes[1, 0].set_title('Monthly Disease Patterns')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].set_ylabel('Average Cases')
        axes[1, 0].set_xticks(range(1, 13))
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 5: Coverage rates comparison
    if coverage_rates:
        vaccines = list(coverage_rates.keys())
        rates = list(coverage_rates.values())
        
        bars = axes[1, 1].bar(vaccines, rates, alpha=0.7)
        axes[1, 1].set_title('Vaccination Coverage Rates')
        axes[1, 1].set_xlabel('Vaccine')
        axes[1, 1].set_ylabel('Coverage Rate (%)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                           f'{rate:.1f}%', ha='center', va='bottom')
    
    # Plot 6: Case rates comparison
    if case_rates:
        diseases = list(case_rates.keys())
        rates = list(case_rates.values())
        
        bars = axes[1, 2].bar(diseases, rates, alpha=0.7, color='red')
        axes[1, 2].set_title('Disease Case Rates')
        axes[1, 2].set_xlabel('Disease')
        axes[1, 2].set_ylabel('Cases per 100,000 Population')
        axes[1, 2].tick_params(axis='x', rotation=45)
        axes[1, 2].grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            axes[1, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                           f'{rate:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('zerodose_data_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Visualizations saved as 'zerodose_data_analysis.png'")

def generate_intervention_parameters(df, coverage_rates, case_rates):
    """Generate realistic intervention parameters based on the data"""
    print("\n=== GENERATING INTERVENTION PARAMETERS ===")
    
    # Calculate realistic parameters
    params = {}
    
    # Coverage rate based on actual DPT1 coverage
    if 'dpt1' in coverage_rates:
        current_coverage = coverage_rates['dpt1']
        target_coverage = min(current_coverage + 15, 95)  # Aim for 15% improvement, max 95%
        params['coverage_rate'] = target_coverage / 100
        print(f"Current DPT1 coverage: {current_coverage:.1f}%")
        print(f"Target coverage: {target_coverage:.1f}%")
    
    # Campaign timing based on seasonal patterns
    # Analyze which months have highest vaccination rates
    if 'dpt1' in df.columns:
        monthly_dpt1 = df.groupby('month')['dpt1'].mean()
        peak_months = monthly_dpt1.nlargest(2).index.tolist()
        
        # Define month mapping
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
            'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        params['campaign_months'] = [month_map[month] for month in peak_months if month in month_map]
        print(f"Peak vaccination months: {peak_months}")
    
    # Disease transmission rates based on actual incidence
    if case_rates:
        params['disease_rates'] = {}
        for disease, rate in case_rates.items():
            # Convert to daily transmission probability
            daily_rate = rate / 365 / 100000  # Convert annual rate to daily probability
            params['disease_rates'][disease] = daily_rate
            print(f"{disease} daily transmission rate: {daily_rate:.6f}")
    
    # Population size based on estimated live births
    if 'estimated_lb' in df.columns:
        avg_population = df['estimated_lb'].mean()
        params['population_size'] = int(avg_population)
        print(f"Average population size: {avg_population:,.0f}")
    
    # Zero-dose children estimate
    if 'dpt1' in df.columns and 'estimated_lb' in df.columns:
        zero_dose_rate = ((df['estimated_lb'] - df['dpt1']) / df['estimated_lb']).mean()
        params['zero_dose_rate'] = zero_dose_rate
        print(f"Zero-dose children rate: {zero_dose_rate:.1%}")
    
    return params

def main():
    """Main analysis function"""
    print("ZERO-DOSE VACCINATION DATA ANALYSIS")
    print("=" * 50)
    
    # Load and analyze data
    df = load_and_analyze_data()
    
    # Analyze different aspects
    coverage_rates, annual_data = analyze_vaccination_coverage(df)
    case_rates, annual_diseases = analyze_disease_incidence(df)
    monthly_vaccines, monthly_diseases = analyze_seasonal_patterns(df)
    annual_age_data = analyze_age_distribution(df)
    
    # Create visualizations
    create_visualizations(df, coverage_rates, case_rates, monthly_vaccines, monthly_diseases)
    
    # Generate intervention parameters
    params = generate_intervention_parameters(df, coverage_rates, case_rates)
    
    # Save parameters
    import json
    with open('intervention_parameters.json', 'w') as f:
        json.dump(params, f, indent=2, default=str)
    
    print(f"\nParameters saved to 'intervention_parameters.json'")
    print("\nAnalysis completed!")

if __name__ == "__main__":
    main() 