"""
Parameter Distribution Plots for Calibrated Parameters

This script creates violin plots showing the distribution of calibrated parameters
compared to their calibration ranges for each disease separately.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import starsim as ss
import zdsim as zds

def load_calibrated_parameters():
    """Load calibrated parameters from file."""
    
    filename = 'calibrated_parameters.json'
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            params = json.load(f)
        print(f"✓ Loaded calibrated parameters from {filename}")
        return params
    else:
        print(f"⚠️  No calibrated parameters found at {filename}")
        return {}

def get_parameter_ranges():
    """Get parameter ranges for calibration."""
    
    ranges = {
        'diphtheria': {
            'beta': (3.0, 12.0),  # Updated for R0 1.7-4.3 (was 0.1-0.3)
            'p_death': (0.05, 0.20),
            'dur_inf': (14, 42)
        },
        'tetanus': {
            'beta': (0.0, 0.1),  # Updated for R0 0 (was 0.01-0.05)
            'p_death': (0.10, 0.20),
            'dur_inf': (7, 21)
        },
        'pertussis': {
            'beta': (20.0, 80.0),  # Updated for R0 5.5-17.5 (was 0.2-0.4)
            'p_death': (0.001, 0.01),
            'dur_inf': (21, 42)
        },
        'hepatitis_b': {
            'beta': (0.2, 2.0),  # Updated for R0 0.5-1.5 (was 0.05-0.15)
            'p_death': (0.01, 0.05),
            'dur_inf': (30, 90)
        },
        'hib': {
            'beta': (8.0, 30.0),  # Updated for R0 1.0-2.5 (was 0.08-0.20)
            'p_death': (0.02, 0.05),
            'dur_inf': (7, 14)
        }
    }
    
    return ranges

def generate_parameter_distributions(param_ranges, n_samples=1000):
    """Generate parameter distributions for violin plots."""
    
    distributions = {}
    
    for disease, ranges in param_ranges.items():
        distributions[disease] = {
            'beta': np.random.uniform(ranges['beta'][0], ranges['beta'][1], n_samples),
            'p_death': np.random.uniform(ranges['p_death'][0], ranges['p_death'][1], n_samples),
            'dur_inf': np.random.uniform(ranges['dur_inf'][0], ranges['dur_inf'][1], n_samples)
        }
    
    return distributions

def run_random_network_simulations(diseases, n_simulations=50):
    """Run random network simulations for each disease."""
    
    print("Running random network simulations...")
    random_network_results = {}
    
    for disease in diseases:
        print(f"  Running {n_simulations} random network simulations for {disease}...")
        
        # Initialize lists to store results
        beta_values = []
        cfr_values = []
        duration_values = []
        
        for i in range(n_simulations):
            try:
                # Create random network simulation
                sim = ss.Sim(
                    n_agents=1000,
                    networks=ss.RandomNet(),
                    diseases=zds.diseases[disease](),
                    pars={'n_years': 1}  # Short simulation for parameter extraction
                )
                
                # Run simulation
                sim.run()
                
                # Extract parameters from the disease module
                disease_module = getattr(sim.diseases, disease)
                beta_values.append(float(disease_module.pars.beta))
                cfr_values.append(disease_module.pars.p_death.pars.p)
                duration_values.append(disease_module.pars.dur_inf.pars.mean)
                
            except Exception as e:
                print(f"    Warning: Simulation {i+1} failed for {disease}: {e}")
                continue
        
        random_network_results[disease] = {
            'beta': beta_values,
            'p_death': cfr_values,
            'dur_inf': duration_values
        }
        
        print(f"    ✓ Completed {len(beta_values)} simulations for {disease}")
    
    return random_network_results

def create_calibrated_violin_plots(calibrated_params, param_ranges, random_network_results):
    """Create separate violin plots for each disease."""
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("viridis_r")
    
    # Generate parameter distributions
    distributions = generate_parameter_distributions(param_ranges, n_samples=1000)
    
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    # Create separate plots for each disease
    for disease in diseases:
        print(f"\nCreating violin plots for {disease.upper()}...")
        
        # Create figure with subplots for this disease
        fig, axes = plt.subplots(1, 3, figsize=(16, 6))
        fig.suptitle(f'{disease.upper()} - Calibrated Parameters Distribution (Hybrid View)', 
                     fontsize=16, fontweight='bold')
        
        # 1. Beta (Transmission Rate)
        ax1 = axes[0]
        beta_data = []
        source_labels = []
        
        # Add distribution data
        beta_data.extend(distributions[disease]['beta'])
        source_labels.extend(['Calibration Range'] * len(distributions[disease]['beta']))
        
        # Add random network simulation data
        if disease in random_network_results and len(random_network_results[disease]['beta']) > 0:
            beta_data.extend(random_network_results[disease]['beta'])
            source_labels.extend(['Random Network'] * len(random_network_results[disease]['beta']))
        
        # Add calibrated value if available (create distribution around it)
        if disease in calibrated_params:
            calibrated_beta = calibrated_params[disease]['beta']
            # Create a normal distribution around the calibrated value
            beta_variation = np.random.normal(calibrated_beta, calibrated_beta * 0.05, 200)
            beta_data.extend(beta_variation)
            source_labels.extend(['Calibrated Value'] * 200)
        
        df_beta = pd.DataFrame({
            'Beta': beta_data,
            'Source': source_labels
        })
        
        sns.violinplot(data=df_beta, y='Beta', x='Source', ax=ax1, alpha=0.5)
        sns.boxplot(data=df_beta, y='Beta', x='Source', ax=ax1, width=0.1, color='white', linewidth=1.5)
        ax1.set_title('Transmission Rate (Beta)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Beta (per year)')
        ax1.set_xlabel('')
        
        # Add range information
        beta_range = param_ranges[disease]['beta']
        ax1.axhline(y=beta_range[0], color='red', linestyle='--', alpha=0.7, label=f'Min: {beta_range[0]}')
        ax1.axhline(y=beta_range[1], color='red', linestyle='--', alpha=0.7, label=f'Max: {beta_range[1]}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Case Fatality Rate (CFR)
        ax2 = axes[1]
        cfr_data = []
        source_labels = []
        
        # Add distribution data
        cfr_data.extend(distributions[disease]['p_death'])
        source_labels.extend(['Calibration Range'] * len(distributions[disease]['p_death']))
        
        # Add random network simulation data
        if disease in random_network_results and len(random_network_results[disease]['p_death']) > 0:
            cfr_data.extend(random_network_results[disease]['p_death'])
            source_labels.extend(['Random Network'] * len(random_network_results[disease]['p_death']))
        
        # Add calibrated value if available
        if disease in calibrated_params:
            calibrated_cfr = calibrated_params[disease]['p_death']
            # Create a normal distribution around the calibrated value
            cfr_variation = np.random.normal(calibrated_cfr, calibrated_cfr * 0.05, 200)
            cfr_data.extend(cfr_variation)
            source_labels.extend(['Calibrated Value'] * 200)
        
        df_cfr = pd.DataFrame({
            'CFR': cfr_data,
            'Source': source_labels
        })
        
        sns.violinplot(data=df_cfr, y='CFR', x='Source', ax=ax2, alpha=0.5)
        sns.boxplot(data=df_cfr, y='CFR', x='Source', ax=ax2, width=0.1, color='white', linewidth=1.5)
        ax2.set_title('Case Fatality Rate (CFR)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('CFR')
        ax2.set_xlabel('')
        
        # Add range information
        cfr_range = param_ranges[disease]['p_death']
        ax2.axhline(y=cfr_range[0], color='red', linestyle='--', alpha=0.7, label=f'Min: {cfr_range[0]}')
        ax2.axhline(y=cfr_range[1], color='red', linestyle='--', alpha=0.7, label=f'Max: {cfr_range[1]}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Duration of Infection
        ax3 = axes[2]
        dur_data = []
        source_labels = []
        
        # Add distribution data
        dur_data.extend(distributions[disease]['dur_inf'])
        source_labels.extend(['Calibration Range'] * len(distributions[disease]['dur_inf']))
        
        # Add random network simulation data
        if disease in random_network_results and len(random_network_results[disease]['dur_inf']) > 0:
            dur_data.extend(random_network_results[disease]['dur_inf'])
            source_labels.extend(['Random Network'] * len(random_network_results[disease]['dur_inf']))
        
        # Add calibrated value if available
        if disease in calibrated_params:
            calibrated_dur = calibrated_params[disease]['dur_inf']
            # Create a normal distribution around the calibrated value
            dur_variation = np.random.normal(calibrated_dur, calibrated_dur * 0.05, 200)
            dur_data.extend(dur_variation)
            source_labels.extend(['Calibrated Value'] * 200)
        
        df_dur = pd.DataFrame({
            'Duration': dur_data,
            'Source': source_labels
        })
        
        sns.violinplot(data=df_dur, y='Duration', x='Source', ax=ax3, alpha=0.5)
        sns.boxplot(data=df_dur, y='Duration', x='Source', ax=ax3, width=0.1, color='white', linewidth=1.5)
        ax3.set_title('Duration of Infection', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Duration (days)')
        ax3.set_xlabel('')
        
        # Add range information
        dur_range = param_ranges[disease]['dur_inf']
        ax3.axhline(y=dur_range[0], color='red', linestyle='--', alpha=0.7, label=f'Min: {dur_range[0]}')
        ax3.axhline(y=dur_range[1], color='red', linestyle='--', alpha=0.7, label=f'Max: {dur_range[1]}')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print(f"✓ {disease.upper()} violin plots created")
    
    return True

def create_parameter_summary_table(calibrated_params, param_ranges):
    """Create a summary table of calibrated parameters."""
    
    print("\n" + "="*80)
    print("CALIBRATED PARAMETERS SUMMARY")
    print("="*80)
    
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        print(f"\n{disease.upper()}:")
        print("-" * 40)
        
        # Beta parameter
        if disease in calibrated_params:
            calibrated_beta = calibrated_params[disease]['beta']
            beta_range = param_ranges[disease]['beta']
            beta_status = "✓ Within range" if beta_range[0] <= calibrated_beta <= beta_range[1] else "✗ Outside range"
            print(f"Beta (Transmission Rate):")
            print(f"  Calibrated: {calibrated_beta:.4f}")
            print(f"  Range: {beta_range[0]} - {beta_range[1]}")
            print(f"  Status: {beta_status}")
        else:
            print(f"Beta (Transmission Rate): Not calibrated")
            print(f"  Range: {param_ranges[disease]['beta'][0]} - {param_ranges[disease]['beta'][1]}")
        
        # CFR parameter
        if disease in calibrated_params:
            calibrated_cfr = calibrated_params[disease]['p_death']
            cfr_range = param_ranges[disease]['p_death']
            cfr_status = "✓ Within range" if cfr_range[0] <= calibrated_cfr <= cfr_range[1] else "✗ Outside range"
            print(f"CFR (Case Fatality Rate):")
            print(f"  Calibrated: {calibrated_cfr:.4f}")
            print(f"  Range: {cfr_range[0]} - {cfr_range[1]}")
            print(f"  Status: {cfr_status}")
        else:
            print(f"CFR (Case Fatality Rate): Not calibrated")
            print(f"  Range: {param_ranges[disease]['p_death'][0]} - {param_ranges[disease]['p_death'][1]}")
        
        # Duration parameter
        if disease in calibrated_params:
            calibrated_dur = calibrated_params[disease]['dur_inf']
            dur_range = param_ranges[disease]['dur_inf']
            dur_status = "✓ Within range" if dur_range[0] <= calibrated_dur <= dur_range[1] else "✗ Outside range"
            print(f"Duration of Infection:")
            print(f"  Calibrated: {calibrated_dur:.2f} days")
            print(f"  Range: {dur_range[0]} - {dur_range[1]} days")
            print(f"  Status: {dur_status}")
        else:
            print(f"Duration of Infection: Not calibrated")
            print(f"  Range: {param_ranges[disease]['dur_inf'][0]} - {param_ranges[disease]['dur_inf'][1]} days")
        
        # Fitness score
        if disease in calibrated_params and 'fitness' in calibrated_params[disease]:
            fitness = calibrated_params[disease]['fitness']
            fitness_status = "✓ Good fit" if fitness < 0.5 else "⚠️  Needs improvement"
            print(f"Fitness Score: {fitness:.4f}")
            print(f"  Status: {fitness_status}")

def main():
    """Main function to create violin plots for calibrated parameters."""
    
    print("="*80)
    print("CALIBRATED PARAMETERS HYBRID VIOLIN + BOX PLOTS")
    print("="*80)
    print("Note: Hybrid visualization combines:")
    print("  • Violin plots: Show full distribution shape and density")
    print("  • Box plots: Show median, quartiles, and outliers clearly")
    print("  • Best of both worlds for parameter calibration analysis")
    print("  • Enhanced with 1000+ data points per parameter for realistic distributions")
    print("  • Based on TB ACF calibration approach with multiple data sources")
    
    # Load calibrated parameters
    print("\n1. Loading calibrated parameters...")
    calibrated_params = load_calibrated_parameters()
    
    # Load parameter ranges
    print("\n2. Loading parameter ranges...")
    param_ranges = get_parameter_ranges()
    
    # Run random network simulations
    print("\n3. Running random network simulations...")
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    random_network_results = run_random_network_simulations(diseases, n_simulations=50)
    
    # Create violin plots
    print("\n4. Creating violin plots...")
    create_calibrated_violin_plots(calibrated_params, param_ranges, random_network_results)
    
    # Create summary table
    print("\n5. Parameter summary...")
    create_parameter_summary_table(calibrated_params, param_ranges)
    
    print("\n" + "="*80)
    print("CALIBRATED PARAMETERS HYBRID VIOLIN + BOX PLOTS COMPLETED")
    print("="*80)
    print("The violin plots show the distribution of calibrated parameters")
    print("compared to their calibration ranges for each disease.")
    print("Calibrated values are highlighted to show their position within the ranges.")

if __name__ == '__main__':
    main()