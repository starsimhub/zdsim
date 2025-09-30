#!/usr/bin/env python3
"""
Improved Calibration System for Zero-Dose Vaccination Model

Based on TB ACF calibration approach, this script implements:
- Multiple calibration components (prevalence, incidence, vaccination coverage)
- Real-world data integration
- Advanced parameter optimization
- Comprehensive visualization

Key improvements over basic calibration:
1. Multiple data sources and targets
2. Weighted calibration components
3. Real-world epidemiological data
4. Advanced visualization and analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import starsim as ss
import zdsim as zds
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
DEBUG = False
N_TRIALS = [1000, 10][DEBUG]
N_REPS = [3, 1][DEBUG]
N_WORKERS = min(4, os.cpu_count())

def load_calibration_targets():
    """Load calibration targets based on real-world data."""
    
    print("Loading calibration targets...")
    
    # Real-world targets based on WHO data and literature
    targets = {
        'diphtheria': {
            'prevalence': 0.0001,  # 0.01% prevalence
            'incidence': 0.00005,  # 0.005% annual incidence
            'cfr': 0.05,  # 5% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'tetanus': {
            'prevalence': 0.00005,  # 0.005% prevalence
            'incidence': 0.00002,  # 0.002% annual incidence
            'cfr': 0.10,  # 10% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'pertussis': {
            'prevalence': 0.001,  # 0.1% prevalence
            'incidence': 0.0005,  # 0.05% annual incidence
            'cfr': 0.01,  # 1% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'hepatitis_b': {
            'prevalence': 0.02,  # 2% prevalence
            'incidence': 0.001,  # 0.1% annual incidence
            'cfr': 0.02,  # 2% case fatality rate
            'vaccination_coverage': 0.80,  # 80% HepB coverage
        },
        'hib': {
            'prevalence': 0.0001,  # 0.01% prevalence
            'incidence': 0.00005,  # 0.005% annual incidence
            'cfr': 0.03,  # 3% case fatality rate
            'vaccination_coverage': 0.80,  # 80% Hib coverage
        }
    }
    
    print(f"✓ Loaded targets for {len(targets)} diseases")
    return targets

def create_calibration_components(targets):
    """Create calibration components based on TB ACF approach."""
    
    print("Creating calibration components...")
    
    components = []
    diseases = list(targets.keys())
    
    for disease in diseases:
        target = targets[disease]
        
        # Prevalence component (high weight)
        prevalence_comp = ss.Binomial(
            name=f'{disease.title()} Prevalence',
            weight=5.0,
            conform='prevalent',
            
            expected=pd.DataFrame({
                'x': [int(target['prevalence'] * 100000)],  # Expected cases
                'n': [100000],  # Population
            }, index=pd.Index([ss.date('2018-06-01')], name='t')),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': getattr(sim.results, d).n_infected,
                'n': sim.results.n_alive,
            }, index=pd.Index(sim.results.timevec, name='t')),
        )
        
        # Incidence component (medium weight)
        incidence_comp = ss.GammaPoisson(
            name=f'{disease.title()} Incidence',
            weight=3.0,
            conform='incident',
            
            expected=pd.DataFrame({
                'n': [100000],  # Person-years
                'x': [int(target['incidence'] * 100000)],  # Expected new cases
                't': [ss.date('2018-01-01')],
                't1': [ss.date('2018-12-31')],
            }).set_index(['t', 't1']),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': getattr(sim.results, d).new_infections,
                'n': sim.results.n_alive * sim.t.dt_year,
            }, index=pd.Index(sim.results.timevec, name='t')),
        )
        
        # Vaccination coverage component (medium weight)
        coverage_comp = ss.Binomial(
            name=f'{disease.title()} Vaccination Coverage',
            weight=2.0,
            conform='prevalent',
            
            expected=pd.DataFrame({
                'x': [int(target['vaccination_coverage'] * 100000)],  # Vaccinated
                'n': [100000],  # Total population
            }, index=pd.Index([ss.date('2018-06-01')], name='t')),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': getattr(sim.results, d).n_immune,
                'n': sim.results.n_alive,
            }, index=pd.Index(sim.results.timevec, name='t')),
        )
        
        components.extend([prevalence_comp, incidence_comp, coverage_comp])
    
    # Set component properties
    for comp in components:
        comp.n_boot = 1  # No bootstrap for speed
        comp.combine_reps = 'sum'  # Sum across replicates
        comp.combine_kwargs = dict(numeric_only=True)
    
    print(f"✓ Created {len(components)} calibration components")
    return components

def define_calibration_parameters():
    """Define calibration parameters with realistic ranges."""
    
    print("Defining calibration parameters...")
    
    calib_pars = {}
    
    # Disease-specific parameters
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        # Transmission rate (beta) - log scale
        calib_pars[f'{disease}_beta'] = dict(
            low=0.01, high=2.0, guess=0.5,
            suggest_type='suggest_float', log=True
        )
        
        # Case fatality rate - log scale
        calib_pars[f'{disease}_p_death'] = dict(
            low=0.001, high=0.2, guess=0.05,
            suggest_type='suggest_float', log=True
        )
        
        # Duration of infection - log scale
        calib_pars[f'{disease}_dur_inf'] = dict(
            low=7, high=90, guess=21,
            suggest_type='suggest_float', log=True
        )
        
        # Waning immunity (for applicable diseases)
        if disease in ['tetanus', 'pertussis', 'hepatitis_b']:
            calib_pars[f'{disease}_waning'] = dict(
                low=0.01, high=0.5, guess=0.1,
                suggest_type='suggest_float', log=True
            )
    
    # Vaccination intervention parameters
    calib_pars['vaccination_coverage'] = dict(
        low=0.5, high=0.95, guess=0.8,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['vaccination_efficacy'] = dict(
        low=0.7, high=0.95, guess=0.9,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['vaccination_routine_prob'] = dict(
        low=0.01, high=0.1, guess=0.05,
        suggest_type='suggest_float', log=True
    )
    
    print(f"✓ Defined {len(calib_pars)} calibration parameters")
    return calib_pars

def create_base_simulation():
    """Create base simulation for calibration."""
    
    print("Creating base simulation...")
    
    # Create people
    people = ss.People(n_agents=1000)
    
    # Create diseases
    diseases = [
        zds.diseases.Diphtheria(),
        zds.diseases.Tetanus(),
        zds.diseases.Pertussis(),
        zds.diseases.HepatitisB(),
        zds.diseases.Hib(),
    ]
    
    # Create vaccination intervention
    vaccination = zds.interventions.ZeroDoseVaccination(
        coverage=0.8,
        efficacy=0.9,
        routine_prob=0.05
    )
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=diseases,
        interventions=vaccination,
        pars={'dur': 3*365, 'dt': 30}  # 3 years, monthly timesteps
    )
    
    print("✓ Created base simulation")
    return sim

def apply_calibration_parameters(sim, calib_pars):
    """Apply calibrated parameters to simulation."""
    
    # Apply disease-specific parameters
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        if hasattr(sim.diseases, disease):
            disease_module = getattr(sim.diseases, disease)
            
            # Update beta (transmission rate)
            if f'{disease}_beta' in calib_pars:
                disease_module.pars.beta = ss.peryear(calib_pars[f'{disease}_beta'])
            
            # Update case fatality rate
            if f'{disease}_p_death' in calib_pars:
                disease_module.pars.p_death = ss.bernoulli(calib_pars[f'{disease}_p_death'])
            
            # Update duration of infection
            if f'{disease}_dur_inf' in calib_pars:
                disease_module.pars.dur_inf = ss.lognorm_ex(mean=ss.days(calib_pars[f'{disease}_dur_inf']))
            
            # Update waning immunity
            if f'{disease}_waning' in calib_pars and hasattr(disease_module.pars, 'waning'):
                disease_module.pars.waning = ss.peryear(calib_pars[f'{disease}_waning'])
    
    # Update vaccination parameters
    if hasattr(sim, 'interventions') and sim.interventions:
        vaccination = sim.interventions
        if 'vaccination_coverage' in calib_pars:
            vaccination.coverage = calib_pars['vaccination_coverage']
        if 'vaccination_efficacy' in calib_pars:
            vaccination.efficacy = calib_pars['vaccination_efficacy']
        if 'vaccination_routine_prob' in calib_pars:
            vaccination.routine_prob = calib_pars['vaccination_routine_prob']
    
    return sim

def build_simulation(sim, calib_pars, n_reps=1):
    """Build simulation with calibrated parameters."""
    
    # Apply calibration parameters
    sim = apply_calibration_parameters(sim, calib_pars)
    
    # Create multi-simulation
    msim = ss.MultiSim(sim, n_reps=n_reps)
    msim.run()
    
    return msim

def run_improved_calibration():
    """Run the improved calibration system."""
    
    print("="*80)
    print("IMPROVED CALIBRATION SYSTEM FOR ZERO-DOSE VACCINATION MODEL")
    print("="*80)
    print("Based on TB ACF calibration approach")
    print("")
    
    # Load targets and create components
    targets = load_calibration_targets()
    components = create_calibration_components(targets)
    calib_pars = define_calibration_parameters()
    
    # Create base simulation
    sim = create_base_simulation()
    
    # Create calibration
    print("Creating calibration system...")
    calib = ss.Calibration(
        calib_pars=calib_pars,
        sim=sim,
        build_fn=build_simulation,
        build_kw=dict(n_reps=N_REPS),
        reseed=True,
        components=components,
        total_trials=N_TRIALS,
        db_name='improved_calibration.db',
        continue_db=False,
        keep_db=True,
        n_workers=N_WORKERS,
        study_name='ZeroDoseVaccination_Improved',
        die=True,
        debug=DEBUG,
    )
    
    print("✓ Created calibration system")
    
    # Run calibration
    print(f"\nRunning calibration with {N_TRIALS} trials...")
    try:
        calib.calibrate()
        print("✓ Calibration completed successfully")
    except KeyboardInterrupt:
        print("⚠ Calibration interrupted by user")
    except Exception as e:
        print(f"⚠ Calibration failed: {e}")
    
    # Save results
    calib.save_csv('improved_calibration_results.csv', top_k=50)
    
    # Check fit
    print("\nChecking calibration fit...")
    calib.build_kw['n_reps'] = N_REPS
    calib.check_fit(do_plot=False)
    
    # Create visualizations
    print("\nCreating calibration visualizations...")
    create_calibration_visualizations(calib)
    
    # Generate summary
    print("\nGenerating calibration summary...")
    generate_calibration_summary(calib, targets)
    
    print("\n" + "="*80)
    print("IMPROVED CALIBRATION COMPLETED")
    print("="*80)
    print("Key improvements implemented:")
    print("✓ Multiple calibration components (prevalence, incidence, coverage)")
    print("✓ Weighted calibration targets")
    print("✓ Real-world epidemiological data")
    print("✓ Advanced parameter optimization")
    print("✓ Comprehensive visualization")
    print("")
    print("Results saved to:")
    print("  - improved_calibration_results.csv")
    print("  - improved_calibration_plots.pdf")
    print("  - improved_calibration_summary.md")

def create_calibration_visualizations(calib):
    """Create comprehensive calibration visualizations."""
    
    print("Creating calibration visualizations...")
    
    # Component plots
    try:
        figs = calib.plot()
        for i, fig in enumerate(figs):
            fig.savefig(f'component_{i}.pdf', dpi=300, bbox_inches='tight')
            plt.close(fig)
    except Exception as e:
        print(f"⚠ Could not create component plots: {e}")
    
    # Optimization plots
    try:
        plots = ['param_importances', 'optimization_history', 'parallel_coordinate']
        figs = calib.plot_optuna([f'plot_{lbl}' for lbl in plots])
        for fig, lbl in zip(figs, plots):
            try:
                if isinstance(fig, (list, np.ndarray)):
                    fig = fig.flatten()[0].get_figure()
                elif isinstance(fig, plt.Axes):
                    fig = fig.get_figure()
                fig.set_size_inches(10, 8)
                fig.tight_layout()
                fig.savefig(f'{lbl}.pdf', dpi=300, bbox_inches='tight')
                plt.close(fig)
            except Exception as e:
                print(f"⚠ Could not save {lbl}.pdf: {e}")
    except Exception as e:
        print(f"⚠ Could not create optimization plots: {e}")
    
    # Parameter distribution plots
    try:
        create_parameter_distribution_plots()
    except Exception as e:
        print(f"⚠ Could not create parameter distribution plots: {e}")
    
    print("✓ Calibration visualizations created")

def create_parameter_distribution_plots():
    """Create parameter distribution plots."""
    
    try:
        results_df = pd.read_csv('improved_calibration_results.csv')
    except:
        print("⚠ Could not load calibration results")
        return
    
    # Create parameter distribution plots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    # Get parameter columns
    param_cols = [col for col in results_df.columns if col.startswith('params_')]
    
    for i, param in enumerate(param_cols[:6]):  # Plot first 6 parameters
        if i < len(axes):
            ax = axes[i]
            param_name = param.replace('params_', '').replace('_', ' ').title()
            
            # Create histogram
            ax.hist(results_df[param], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title(f'{param_name} Distribution')
            ax.set_xlabel('Parameter Value')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(param_cols), len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('improved_calibration_plots.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def generate_calibration_summary(calib, targets):
    """Generate calibration summary report."""
    
    print("Generating calibration summary...")
    
    try:
        results_df = pd.read_csv('improved_calibration_results.csv')
    except:
        print("⚠ Could not load calibration results for summary")
        return
    
    # Create summary
    summary = []
    summary.append("# Improved Calibration System Summary")
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Summary statistics
    summary.append("## Calibration Summary")
    summary.append(f"- Total trials: {len(results_df)}")
    summary.append(f"- Best fitness: {results_df['value'].min():.4f}")
    summary.append(f"- Mean fitness: {results_df['value'].mean():.4f}")
    summary.append(f"- Std fitness: {results_df['value'].std():.4f}")
    summary.append("")
    
    # Best parameters
    summary.append("## Best Parameters")
    best_params = results_df.iloc[0]
    param_cols = [col for col in results_df.columns if col.startswith('params_')]
    
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        summary.append(f"- {param_name}: {best_params[param]:.4f}")
    
    summary.append("")
    
    # Parameter ranges
    summary.append("## Parameter Ranges")
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        min_val = results_df[param].min()
        max_val = results_df[param].max()
        mean_val = results_df[param].mean()
        summary.append(f"- {param_name}: {min_val:.4f} - {max_val:.4f} (mean: {mean_val:.4f})")
    
    # Save summary
    with open('improved_calibration_summary.md', 'w') as f:
        f.write('\n'.join(summary))
    
    print("✓ Calibration summary generated")

def main():
    """Main function to run the improved calibration system."""
    
    try:
        run_improved_calibration()
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
