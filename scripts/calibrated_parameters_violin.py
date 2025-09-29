"""
Violin plots for calibrated parameters across different diseases.

This script creates violin plots to visualize the distribution of calibrated
parameters for each disease in the zero-dose vaccination model.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sciris as sc
import json

def load_calibrated_parameters():
    """Load calibrated parameters from file."""
    try:
        with open('calibrated_parameters.json', 'r') as f:
            calibrated_params = json.load(f)
        return calibrated_params
    except FileNotFoundError:
        print("No calibrated parameters file found. Using default ranges.")
        return {}

def get_parameter_ranges():
    """Get parameter ranges for calibration from the calibration system."""
    
    # Parameter ranges from calibration_system.py
    param_ranges = {
        'diphtheria': {
            'beta': (0.1, 0.3),  # Transmission rate range
            'p_death': (0.05, 0.20),  # Case Fatality Rate (CFR) range
            'dur_inf': (14, 42)  # Duration of infection (days)
        },
        'tetanus': {
            'beta': (0.01, 0.05),  # Environmental exposure rate
            'p_death': (0.10, 0.20),  # Case Fatality Rate (CFR) range
            'dur_inf': (7, 21)  # Duration of infection (days)
        },
        'pertussis': {
            'beta': (0.2, 0.4),  # High transmission rate
            'p_death': (0.001, 0.01),  # Low Case Fatality Rate (CFR)
            'dur_inf': (21, 42)  # Duration of infection (days)
        },
        'hepatitis_b': {
            'beta': (0.05, 0.15),  # Moderate transmission rate
            'p_death': (0.01, 0.05),  # Case Fatality Rate (CFR) range
            'dur_inf': (30, 90)  # Long duration of infection (days)
        },
        'hib': {
            'beta': (0.08, 0.20),  # Moderate transmission rate
            'p_death': (0.02, 0.05),  # Case Fatality Rate (CFR) range
            'dur_inf': (7, 14)  # Short duration of infection (days)
        }
    }
    
    return param_ranges

def generate_parameter_distributions(param_ranges, n_samples=1000):
    """Generate parameter distributions based on calibration ranges."""
    
    distributions = {}
    
    for disease, ranges in param_ranges.items():
        distributions[disease] = {
            'beta': np.random.uniform(ranges['beta'][0], ranges['beta'][1], n_samples),
            'p_death': np.random.uniform(ranges['p_death'][0], ranges['p_death'][1], n_samples),
            'dur_inf': np.random.uniform(ranges['dur_inf'][0], ranges['dur_inf'][1], n_samples)
        }
    
    return distributions

def create_calibrated_violin_plots(calibrated_params, param_ranges):
    """Create violin plots for calibrated parameters."""
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Generate parameter distributions
    distributions = generate_parameter_distributions(param_ranges, n_samples=1000)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Calibrated Parameters Distribution\n(Violin Plots)', 
                 fontsize=16, fontweight='bold')
    
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    # 1. Beta (Transmission Rate) comparison
    ax1 = axes[0, 0]
    beta_data = []
    disease_labels = []
    source_labels = []
    
    for disease in diseases:
        # Add distribution data
        beta_data.extend(distributions[disease]['beta'])
        disease_labels.extend([disease] * len(distributions[disease]['beta']))
        source_labels.extend(['Calibration Range'] * len(distributions[disease]['beta']))
        
        # Add calibrated value if available
        if disease in calibrated_params:
            calibrated_beta = calibrated_params[disease]['beta']
            beta_data.extend([calibrated_beta] * 10)  # Repeat for visibility
            disease_labels.extend([disease] * 10)
            source_labels.extend(['Calibrated Value'] * 10)
    
    df_beta = pd.DataFrame({
        'Beta': beta_data,
        'Disease': disease_labels,
        'Source': source_labels
    })
    
    sns.violinplot(data=df_beta, x='Disease', y='Beta', hue='Source', ax=ax1, split=True)
    ax1.set_title('Transmission Rate (Beta)\nCalibration Range vs Calibrated Values', 
                  fontsize=12, fontweight='bold')
    ax1.set_ylabel('Beta (per year)')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # 2. Case Fatality Rate (CFR) comparison
    ax2 = axes[0, 1]
    cfr_data = []
    disease_labels_cfr = []
    source_labels_cfr = []
    
    for disease in diseases:
        # Add distribution data
        cfr_data.extend(distributions[disease]['p_death'])
        disease_labels_cfr.extend([disease] * len(distributions[disease]['p_death']))
        source_labels_cfr.extend(['Calibration Range'] * len(distributions[disease]['p_death']))
        
        # Add calibrated value if available
        if disease in calibrated_params:
            calibrated_cfr = calibrated_params[disease]['p_death']
            cfr_data.extend([calibrated_cfr] * 10)  # Repeat for visibility
            disease_labels_cfr.extend([disease] * 10)
            source_labels_cfr.extend(['Calibrated Value'] * 10)
    
    df_cfr = pd.DataFrame({
        'CFR': cfr_data,
        'Disease': disease_labels_cfr,
        'Source': source_labels_cfr
    })
    
    sns.violinplot(data=df_cfr, x='Disease', y='CFR', hue='Source', ax=ax2, split=True)
    ax2.set_title('Case Fatality Rate (CFR)\nCalibration Range vs Calibrated Values', 
                  fontsize=12, fontweight='bold')
    ax2.set_ylabel('CFR')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. Duration of Infection comparison
    ax3 = axes[1, 0]
    dur_data = []
    disease_labels_dur = []
    source_labels_dur = []
    
    for disease in diseases:
        # Add distribution data
        dur_data.extend(distributions[disease]['dur_inf'])
        disease_labels_dur.extend([disease] * len(distributions[disease]['dur_inf']))
        source_labels_dur.extend(['Calibration Range'] * len(distributions[disease]['dur_inf']))
        
        # Add calibrated value if available
        if disease in calibrated_params:
            calibrated_dur = calibrated_params[disease]['dur_inf']
            dur_data.extend([calibrated_dur] * 10)  # Repeat for visibility
            disease_labels_dur.extend([disease] * 10)
            source_labels_dur.extend(['Calibrated Value'] * 10)
    
    df_dur = pd.DataFrame({
        'Duration': dur_data,
        'Disease': disease_labels_dur,
        'Source': source_labels_dur
    })
    
    sns.violinplot(data=df_dur, x='Disease', y='Duration', hue='Source', ax=ax3, split=True)
    ax3.set_title('Duration of Infection\nCalibration Range vs Calibrated Values', 
                  fontsize=12, fontweight='bold')
    ax3.set_ylabel('Duration (days)')
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # 4. Parameter comparison across diseases
    ax4 = axes[1, 1]
    
    # Create a combined plot showing all parameters
    all_params = []
    param_names = []
    disease_names = []
    
    for disease in diseases:
        # Beta values
        all_params.extend(distributions[disease]['beta'])
        param_names.extend(['Beta'] * len(distributions[disease]['beta']))
        disease_names.extend([disease] * len(distributions[disease]['beta']))
        
        # CFR values (scaled for visibility)
        cfr_scaled = distributions[disease]['p_death'] * 10  # Scale up for visibility
        all_params.extend(cfr_scaled)
        param_names.extend(['CFR×10'] * len(cfr_scaled))
        disease_names.extend([disease] * len(cfr_scaled))
        
        # Duration values (scaled for visibility)
        dur_scaled = distributions[disease]['dur_inf'] / 10  # Scale down for visibility
        all_params.extend(dur_scaled)
        param_names.extend(['Duration/10'] * len(dur_scaled))
        disease_names.extend([disease] * len(dur_scaled))
    
    df_combined = pd.DataFrame({
        'Parameter_Value': all_params,
        'Parameter': param_names,
        'Disease': disease_names
    })
    
    sns.violinplot(data=df_combined, x='Disease', y='Parameter_Value', hue='Parameter', ax=ax4)
    ax4.set_title('All Parameters Combined\n(Normalized for Comparison)', 
                  fontsize=12, fontweight='bold')
    ax4.set_ylabel('Parameter Value (Normalized)')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_parameter_summary_table(calibrated_params, param_ranges):
    """Create a summary table of calibrated parameters."""
    
    print("\n" + "="*80)
    print("CALIBRATED PARAMETERS SUMMARY")
    print("="*80)
    
    for disease in ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']:
        print(f"\n{disease.upper()}:")
        print("-" * 40)
        
        ranges = param_ranges[disease]
        
        # Beta (Transmission Rate)
        if disease in calibrated_params:
            cal_beta = calibrated_params[disease]['beta']
            print(f"Beta (Transmission Rate):")
            print(f"  Calibrated: {cal_beta:.4f}")
            print(f"  Range: {ranges['beta'][0]:.3f} - {ranges['beta'][1]:.3f}")
            print(f"  Status: {'✓ Within range' if ranges['beta'][0] <= cal_beta <= ranges['beta'][1] else '✗ Outside range'}")
        else:
            print(f"Beta (Transmission Rate): Not calibrated")
            print(f"  Range: {ranges['beta'][0]:.3f} - {ranges['beta'][1]:.3f}")
        
        # CFR (Case Fatality Rate)
        if disease in calibrated_params:
            cal_cfr = calibrated_params[disease]['p_death']
            print(f"CFR (Case Fatality Rate):")
            print(f"  Calibrated: {cal_cfr:.4f}")
            print(f"  Range: {ranges['p_death'][0]:.3f} - {ranges['p_death'][1]:.3f}")
            print(f"  Status: {'✓ Within range' if ranges['p_death'][0] <= cal_cfr <= ranges['p_death'][1] else '✗ Outside range'}")
        else:
            print(f"CFR (Case Fatality Rate): Not calibrated")
            print(f"  Range: {ranges['p_death'][0]:.3f} - {ranges['p_death'][1]:.3f}")
        
        # Duration of Infection
        if disease in calibrated_params:
            cal_dur = calibrated_params[disease]['dur_inf']
            print(f"Duration of Infection:")
            print(f"  Calibrated: {cal_dur:.2f} days")
            print(f"  Range: {ranges['dur_inf'][0]:.0f} - {ranges['dur_inf'][1]:.0f} days")
            print(f"  Status: {'✓ Within range' if ranges['dur_inf'][0] <= cal_dur <= ranges['dur_inf'][1] else '✗ Outside range'}")
        else:
            print(f"Duration of Infection: Not calibrated")
            print(f"  Range: {ranges['dur_inf'][0]:.0f} - {ranges['dur_inf'][1]:.0f} days")
        
        # Fitness score (if available)
        if disease in calibrated_params and 'fitness' in calibrated_params[disease]:
            fitness = calibrated_params[disease]['fitness']
            print(f"Fitness Score: {fitness:.4f}")
            print(f"  Status: {'✓ Good fit' if fitness < 0.5 else '✗ Poor fit'}")

def main():
    """Main function to create calibrated parameters violin plots."""
    
    print("="*80)
    print("CALIBRATED PARAMETERS VIOLIN PLOTS")
    print("="*80)
    
    # Load calibrated parameters
    print("\n1. Loading calibrated parameters...")
    calibrated_params = load_calibrated_parameters()
    
    # Get parameter ranges
    print("\n2. Loading parameter ranges...")
    param_ranges = get_parameter_ranges()
    
    # Create violin plots
    print("\n3. Creating violin plots...")
    fig = create_calibrated_violin_plots(calibrated_params, param_ranges)
    plt.show()
    
    # Create parameter summary
    print("\n4. Parameter summary...")
    create_parameter_summary_table(calibrated_params, param_ranges)
    
    print(f"\n" + "="*80)
    print("CALIBRATED PARAMETERS VIOLIN PLOTS COMPLETED")
    print("="*80)
    print("The violin plots show the distribution of calibrated parameters")
    print("compared to their calibration ranges for each disease.")
    print("Calibrated values are highlighted to show their position within the ranges.")

if __name__ == '__main__':
    main()
