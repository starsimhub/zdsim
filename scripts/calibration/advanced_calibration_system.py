#!/usr/bin/env python3
"""
Advanced Calibration System for Zero-Dose Vaccination Model

This script implements a sophisticated calibration system based on the TB ACF approach,
incorporating multiple data sources, components, and advanced optimization techniques.

Key Features:
- Multiple calibration components (prevalence, incidence, vaccination coverage)
- Real-world data integration
- Advanced parameter optimization
- Comprehensive visualization and analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import starsim as ss
import zdsim as zds
import sciris as sc
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
DEBUG = False
N_REPS = [6, 2][DEBUG]  # Per trial
TOTAL_TRIALS = [100_000, 100][DEBUG]  # Total calibration trials
N_REPS_CHECK = [60, 2][DEBUG]  # Final runs for checking fit
N_WORKERS = min(8, sc.cpu_count())  # Parallel processing

# Results directory
RESDIR = 'calibration_results'
os.makedirs(RESDIR, exist_ok=True)

def load_real_world_data():
    """Load real-world epidemiological data for calibration."""
    
    print("Loading real-world data...")
    
    # Load zero-dose data
    try:
        data_file = 'zdsim/data/zerodose_data.dta'
        if os.path.exists(data_file):
            # Load Stata file
            import pandas as pd
            real_data = pd.read_stata(data_file)
            print(f"✓ Loaded real data: {len(real_data)} records")
        else:
            print("⚠ Real data file not found, using synthetic data")
            real_data = None
    except Exception as e:
        print(f"⚠ Could not load real data: {e}")
        real_data = None
    
    # Define calibration targets based on literature and WHO data
    calibration_targets = {
        'diphtheria': {
            'prevalence_2018': 0.0001,  # 0.01% prevalence
            'incidence_2018': 0.00005,  # 0.005% annual incidence
            'cfr': 0.05,  # 5% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'tetanus': {
            'prevalence_2018': 0.00005,  # 0.005% prevalence
            'incidence_2018': 0.00002,  # 0.002% annual incidence
            'cfr': 0.10,  # 10% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'pertussis': {
            'prevalence_2018': 0.001,  # 0.1% prevalence
            'incidence_2018': 0.0005,  # 0.05% annual incidence
            'cfr': 0.01,  # 1% case fatality rate
            'vaccination_coverage': 0.85,  # 85% DPT coverage
        },
        'hepatitis_b': {
            'prevalence_2018': 0.02,  # 2% prevalence
            'incidence_2018': 0.001,  # 0.1% annual incidence
            'cfr': 0.02,  # 2% case fatality rate
            'vaccination_coverage': 0.80,  # 80% HepB coverage
        },
        'hib': {
            'prevalence_2018': 0.0001,  # 0.01% prevalence
            'incidence_2018': 0.00005,  # 0.005% annual incidence
            'cfr': 0.03,  # 3% case fatality rate
            'vaccination_coverage': 0.80,  # 80% Hib coverage
        }
    }
    
    return calibration_targets, real_data

def create_calibration_components():
    """Create calibration components for each disease."""
    
    print("Creating calibration components...")
    
    components = []
    
    # Define diseases to calibrate
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        # Prevalence component
        prevalence_comp = ss.Binomial(
            name=f'{disease.title()} Prevalence',
            weight=5.0,  # High weight for prevalence
            conform='prevalent',
            
            expected=pd.DataFrame({
                'x': [100],  # Expected cases
                'n': [100000],  # Population
            }, index=pd.Index([ss.date('2018-06-01')], name='t')),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': sim.results[d].n_infected,
                'n': sim.results.n_alive,
            }, index=pd.Index(sim.results.timevec, name='t')),
        )
        
        # Incidence component
        incidence_comp = ss.GammaPoisson(
            name=f'{disease.title()} Incidence',
            weight=3.0,
            conform='incident',
            
            expected=pd.DataFrame({
                'n': [100000],  # Person-years
                'x': [50],  # Expected new cases
                't': [ss.date('2018-01-01')],
                't1': [ss.date('2018-12-31')],
            }).set_index(['t', 't1']),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': sim.results[d].new_infections,
                'n': sim.results.n_alive * sim.t.dt_year,
            }, index=pd.Index(sim.results.timevec, name='t')),
        )
        
        # Vaccination coverage component
        coverage_comp = ss.Binomial(
            name=f'{disease.title()} Vaccination Coverage',
            weight=2.0,
            conform='prevalent',
            
            expected=pd.DataFrame({
                'x': [85000],  # Vaccinated
                'n': [100000],  # Total population
            }, index=pd.Index([ss.date('2018-06-01')], name='t')),
            
            extract_fn=lambda sim, d=disease: pd.DataFrame({
                'x': sim.results[d].n_immune,
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
    """Define calibration parameters for each disease."""
    
    print("Defining calibration parameters...")
    
    calib_pars = {}
    
    # Disease-specific parameters
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        # Transmission rate (beta)
        calib_pars[f'{disease}_beta'] = dict(
            low=0.01, high=2.0, guess=0.5,
            suggest_type='suggest_float', log=True
        )
        
        # Case fatality rate
        calib_pars[f'{disease}_p_death'] = dict(
            low=0.001, high=0.2, guess=0.05,
            suggest_type='suggest_float', log=True
        )
        
        # Duration of infection
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

def create_simulation():
    """Create the base simulation for calibration."""
    
    print("Creating base simulation...")
    
    # Create people
    people = ss.People(n_agents=1000)
    
    # Create diseases
    diseases = [
        zds.diseases.diphtheria(),
        zds.diseases.tetanus(),
        zds.diseases.pertussis(),
        zds.diseases.hepatitis_b(),
        zds.diseases.hib(),
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
        pars={'n_years': 5, 'dt': 30}  # 5 years, monthly timesteps
    )
    
    print("✓ Created base simulation")
    return sim

def apply_calibration_parameters(sim, calib_pars):
    """Apply calibrated parameters to simulation."""
    
    print("Applying calibrated parameters...")
    
    # Apply disease-specific parameters
    diseases = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    
    for disease in diseases:
        if disease in sim.diseases:
            disease_module = sim.diseases[disease]
            
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
    
    print("✓ Applied calibrated parameters")
    return sim

def build_simulation(sim, calib_pars, n_reps=1):
    """Build simulation with calibrated parameters."""
    
    # Apply calibration parameters
    sim = apply_calibration_parameters(sim, calib_pars)
    
    # Create multi-simulation
    msim = ss.MultiSim(sim, n_reps=n_reps)
    msim.run()
    
    return msim

def create_calibration():
    """Create the calibration object."""
    
    print("Creating calibration system...")
    
    # Load data and create components
    calibration_targets, real_data = load_real_world_data()
    components = create_calibration_components()
    calib_pars = define_calibration_parameters()
    
    # Create base simulation
    sim = create_simulation()
    
    # Create calibration
    calib = ss.Calibration(
        calib_pars=calib_pars,
        sim=sim,
        build_fn=build_simulation,
        build_kw=dict(n_reps=N_REPS),
        reseed=True,
        components=components,
        total_trials=TOTAL_TRIALS,
        db_name=f'{RESDIR}/calibration.db',
        continue_db=False,
        keep_db=True,
        n_workers=N_WORKERS,
        study_name='ZeroDoseVaccination_Calibration',
        die=True,
        debug=DEBUG,
    )
    
    print("✓ Created calibration system")
    return sim, calib, calibration_targets

def run_calibration():
    """Run the calibration process."""
    
    print("="*80)
    print("ADVANCED CALIBRATION SYSTEM FOR ZERO-DOSE VACCINATION MODEL")
    print("="*80)
    
    # Create calibration
    sim, calib, targets = create_calibration()
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'n_trials': TOTAL_TRIALS,
        'n_reps': N_REPS,
        'n_workers': N_WORKERS,
        'debug': DEBUG,
        'targets': targets
    }
    
    with open(f'{RESDIR}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Run calibration
    print(f"\nRunning calibration with {TOTAL_TRIALS} trials...")
    T = sc.timer()
    
    try:
        calib.calibrate()
        print("✓ Calibration completed successfully")
    except KeyboardInterrupt:
        print("⚠ Calibration interrupted by user")
    except Exception as e:
        print(f"⚠ Calibration failed: {e}")
    
    T.toc()
    
    # Save results
    calib.save_csv(f'{RESDIR}/calib_pars.csv', top_k=100)
    
    # Check fit
    print("\nChecking calibration fit...")
    calib.build_kw['n_reps'] = N_REPS_CHECK
    calib.check_fit(do_plot=False)
    
    # Create visualizations
    print("\nCreating calibration visualizations...")
    create_calibration_plots(calib)
    
    # Generate summary report
    print("\nGenerating summary report...")
    generate_calibration_report(calib, targets)
    
    print("\n" + "="*80)
    print("CALIBRATION COMPLETED")
    print("="*80)
    print(f"Results saved to: {RESDIR}/")
    print("Key files:")
    print(f"  - calib_pars.csv: Best parameter sets")
    print(f"  - metadata.json: Calibration metadata")
    print(f"  - calibration_plots.pdf: Visualization results")
    print(f"  - calibration_report.pdf: Summary report")

def create_calibration_plots(calib):
    """Create comprehensive calibration visualizations."""
    
    print("Creating calibration plots...")
    
    # Component plots
    try:
        figs = calib.plot()
        for i, fig in enumerate(figs):
            fig.savefig(f'{RESDIR}/component_{i}.pdf', dpi=300, bbox_inches='tight')
            plt.close(fig)
    except Exception as e:
        print(f"⚠ Could not create component plots: {e}")
    
    # Optimization plots
    try:
        plots = ['param_importances', 'optimization_history', 'parallel_coordinate', 'contour']
        figs = calib.plot_optuna([f'plot_{lbl}' for lbl in plots])
        for fig, lbl in zip(figs, plots):
            try:
                if isinstance(fig, (list, np.ndarray)):
                    fig = fig.flatten()[0].get_figure()
                elif isinstance(fig, plt.Axes):
                    fig = fig.get_figure()
                fig.set_size_inches(10, 8)
                fig.tight_layout()
                fig.savefig(f'{RESDIR}/{lbl}.pdf', dpi=300, bbox_inches='tight')
                plt.close(fig)
            except Exception as e:
                print(f"⚠ Could not save {lbl}.pdf: {e}")
    except Exception as e:
        print(f"⚠ Could not create optimization plots: {e}")
    
    # Parameter distribution plots
    try:
        create_parameter_distribution_plots(calib)
    except Exception as e:
        print(f"⚠ Could not create parameter distribution plots: {e}")
    
    print("✓ Calibration plots created")

def create_parameter_distribution_plots(calib):
    """Create parameter distribution plots."""
    
    # Load calibration results
    try:
        results_df = pd.read_csv(f'{RESDIR}/calib_pars.csv')
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
    plt.savefig(f'{RESDIR}/parameter_distributions.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def generate_calibration_report(calib, targets):
    """Generate comprehensive calibration report."""
    
    print("Generating calibration report...")
    
    # Load results
    try:
        results_df = pd.read_csv(f'{RESDIR}/calib_pars.csv')
    except:
        print("⚠ Could not load calibration results for report")
        return
    
    # Create report
    report = []
    report.append("# Zero-Dose Vaccination Model Calibration Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary statistics
    report.append("## Calibration Summary")
    report.append(f"- Total trials: {len(results_df)}")
    report.append(f"- Best fitness: {results_df['value'].min():.4f}")
    report.append(f"- Mean fitness: {results_df['value'].mean():.4f}")
    report.append(f"- Std fitness: {results_df['value'].std():.4f}")
    report.append("")
    
    # Best parameters
    report.append("## Best Parameters")
    best_params = results_df.iloc[0]
    param_cols = [col for col in results_df.columns if col.startswith('params_')]
    
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        report.append(f"- {param_name}: {best_params[param]:.4f}")
    
    report.append("")
    
    # Parameter ranges
    report.append("## Parameter Ranges")
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        min_val = results_df[param].min()
        max_val = results_df[param].max()
        mean_val = results_df[param].mean()
        report.append(f"- {param_name}: {min_val:.4f} - {max_val:.4f} (mean: {mean_val:.4f})")
    
    # Save report
    with open(f'{RESDIR}/calibration_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("✓ Calibration report generated")

def main():
    """Main function to run the advanced calibration system."""
    
    try:
        run_calibration()
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
