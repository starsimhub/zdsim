#!/usr/bin/env python3
"""
Parallel Tetanus Model Calibration

This script implements comprehensive calibration of the tetanus model using
Starsim's multithreading capabilities with smaller populations and multiple
parallel simulations to efficiently match real-world target values.

Based on TB ACF calibration approach with:
- Smaller populations (1000 agents)
- Multiple parallel simulations (3-6 reps)
- Real-world data integration
- Advanced parameter optimization
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

# Configuration for parallel calibration
DEBUG = False
N_TRIALS = [1000, 50][DEBUG]  # Total calibration trials
N_REPS = [6, 2][DEBUG]  # Number of replicates per trial
N_AGENTS = [1000, 500][DEBUG]  # Smaller population for speed
N_WORKERS = min(8, sc.cpu_count())  # Parallel processing
DURATION = 3  # Years of simulation

# Results directory
RESDIR = 'tetanus_calibration_results'
os.makedirs(RESDIR, exist_ok=True)

def load_tetanus_targets():
    """Load tetanus-specific calibration targets from real data."""
    
    print("Loading tetanus calibration targets from real data...")
    
    try:
        # Load real tetanus data
        data_file = 'zdsim/data/zerodose_data.dta'
        data = pd.read_stata(data_file)
        
        # Extract tetanus-specific data
        tetanus_columns = ['tetanus', 'neonatal_tetanus', 'peri_neonatal_tetanus', 
                          'tetanus_inpatient', 'year', 'month', 'estimated_lb']
        tetanus_data = data[tetanus_columns].copy()
        
        # Calculate real-world targets
        total_tetanus = tetanus_data['tetanus'].sum()
        total_births = tetanus_data['estimated_lb'].sum()
        neonatal_cases = tetanus_data['neonatal_tetanus'].sum()
        peri_neonatal_cases = tetanus_data['peri_neonatal_tetanus'].sum()
        
        # Calculate rates and proportions
        years = len(tetanus_data['year'].unique())
        population_per_year = total_births / years
        
        # Target values based on real data
        targets = {
            'tetanus': {
                'prevalence': total_tetanus / (population_per_year * years * 1000),  # per 1000 population
                'incidence': total_tetanus / (population_per_year * years * 1000),  # per 1000 population per year
                'neonatal_proportion': neonatal_cases / total_tetanus,
                'peri_neonatal_proportion': peri_neonatal_cases / total_tetanus,
                'neonatal_rate_per_1000_births': (neonatal_cases / total_births) * 1000,
                'cfr': 0.1,  # 10% case fatality rate
                'vaccination_coverage': 0.6,  # 60% maternal vaccination coverage
            }
        }
        
        print(f"✓ Loaded tetanus targets from real data:")
        print(f"  Total tetanus cases: {total_tetanus:,}")
        print(f"  Neonatal cases: {neonatal_cases:,}")
        print(f"  Neonatal proportion: {targets['tetanus']['neonatal_proportion']:.1%}")
        print(f"  Peri-neonatal proportion: {targets['tetanus']['peri_neonatal_proportion']:.1%}")
        print(f"  Neonatal rate per 1000 births: {targets['tetanus']['neonatal_rate_per_1000_births']:.2f}")
        
        return targets
        
    except Exception as e:
        print(f"⚠ Could not load real data: {e}")
        print("Using synthetic targets based on literature...")
        
        # Fallback to literature-based targets
        targets = {
            'tetanus': {
                'prevalence': 0.00005,  # 0.005% prevalence
                'incidence': 0.00002,  # 0.002% annual incidence
                'neonatal_proportion': 0.227,  # 22.7% neonatal (from real data)
                'peri_neonatal_proportion': 0.00004,  # 0.004% peri-neonatal
                'neonatal_rate_per_1000_births': 0.03,  # 0.03 per 1000 births
                'cfr': 0.1,  # 10% case fatality rate
                'vaccination_coverage': 0.6,  # 60% maternal vaccination coverage
            }
        }
        
        return targets

def create_tetanus_calibration_components(targets):
    """Create tetanus-specific calibration components."""
    
    print("Creating tetanus calibration components...")
    
    components = []
    disease = 'tetanus'
    target = targets[disease]
    
    # 1. Overall tetanus prevalence component (high weight)
    prevalence_comp = ss.Binomial(
        name='Tetanus Prevalence',
        weight=5.0,
        conform='prevalent',
        
        expected=pd.DataFrame({
            'x': [int(target['prevalence'] * 100000)],  # Expected cases
            'n': [100000],  # Population
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_infected,
            'n': sim.results.n_alive,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    # 2. Neonatal tetanus proportion component (very high weight)
    neonatal_comp = ss.Binomial(
        name='Neonatal Tetanus Proportion',
        weight=8.0,  # Highest weight for neonatal tetanus
        conform='prevalent',
        
        expected=pd.DataFrame({
            'x': [int(target['neonatal_proportion'] * 1000)],  # Expected neonatal cases
            'n': [1000],  # Total tetanus cases
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_neonatal,
            'n': sim.results.tetanus.n_infected,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    # 3. Peri-neonatal tetanus proportion component (medium weight)
    peri_neonatal_comp = ss.Binomial(
        name='Peri-neonatal Tetanus Proportion',
        weight=3.0,
        conform='prevalent',
        
        expected=pd.DataFrame({
            'x': [int(target['peri_neonatal_proportion'] * 1000)],  # Expected peri-neonatal cases
            'n': [1000],  # Total tetanus cases
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_peri_neonatal,
            'n': sim.results.tetanus.n_infected,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    # 4. Tetanus incidence component (medium weight)
    incidence_comp = ss.GammaPoisson(
        name='Tetanus Incidence',
        weight=4.0,
        conform='incident',
        
        expected=pd.DataFrame({
            'n': [100000],  # Person-years
            'x': [int(target['incidence'] * 100000)],  # Expected new cases
            't': [ss.date('2018-01-01')],
            't1': [ss.date('2018-12-31')],
        }).set_index(['t', 't1']),
        
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.new_infections,
            'n': sim.results.n_alive * sim.t.dt_year,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    # 5. Maternal vaccination coverage component (medium weight)
    vaccination_comp = ss.Binomial(
        name='Maternal Vaccination Coverage',
        weight=3.0,
        conform='prevalent',
        
        expected=pd.DataFrame({
            'x': [int(target['vaccination_coverage'] * 100000)],  # Vaccinated mothers
            'n': [100000],  # Total population
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_maternal_vaccinated,
            'n': sim.results.n_alive,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    components = [prevalence_comp, neonatal_comp, peri_neonatal_comp, incidence_comp, vaccination_comp]
    
    # Set component properties for parallel processing
    for comp in components:
        comp.n_boot = 1  # No bootstrap for speed
        comp.combine_reps = 'sum'  # Sum across replicates
        comp.combine_kwargs = dict(numeric_only=True)
    
    print(f"✓ Created {len(components)} tetanus calibration components")
    return components

def define_tetanus_calibration_parameters():
    """Define tetanus-specific calibration parameters."""
    
    print("Defining tetanus calibration parameters...")
    
    calib_pars = {}
    
    # Age-specific wound exposure rates (key parameters for tetanus)
    calib_pars['neonatal_wound_rate'] = dict(
        low=0.01, high=2.0, guess=0.5,
        suggest_type='suggest_float', log=True
    )
    
    calib_pars['peri_neonatal_wound_rate'] = dict(
        low=0.001, high=0.1, guess=0.01,
        suggest_type='suggest_float', log=True
    )
    
    calib_pars['childhood_wound_rate'] = dict(
        low=0.01, high=1.0, guess=0.1,
        suggest_type='suggest_float', log=True
    )
    
    calib_pars['adult_wound_rate'] = dict(
        low=0.01, high=1.0, guess=0.05,
        suggest_type='suggest_float', log=True
    )
    
    # Age-specific case fatality rates
    calib_pars['neonatal_cfr'] = dict(
        low=0.5, high=0.95, guess=0.8,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['peri_neonatal_cfr'] = dict(
        low=0.2, high=0.8, guess=0.4,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['childhood_cfr'] = dict(
        low=0.05, high=0.5, guess=0.1,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['adult_cfr'] = dict(
        low=0.1, high=0.6, guess=0.2,
        suggest_type='suggest_float', log=False
    )
    
    # Maternal vaccination parameters
    calib_pars['maternal_vaccination_efficacy'] = dict(
        low=0.3, high=0.9, guess=0.6,
        suggest_type='suggest_float', log=False
    )
    
    calib_pars['maternal_vaccination_coverage'] = dict(
        low=0.2, high=0.8, guess=0.4,
        suggest_type='suggest_float', log=False
    )
    
    # General tetanus parameters
    calib_pars['tetanus_dur_inf'] = dict(
        low=7, high=90, guess=21,
        suggest_type='suggest_float', log=True
    )
    
    calib_pars['tetanus_waning'] = dict(
        low=0.01, high=0.5, guess=0.055,
        suggest_type='suggest_float', log=True
    )
    
    print(f"✓ Defined {len(calib_pars)} tetanus calibration parameters")
    return calib_pars

def create_tetanus_simulation():
    """Create base tetanus simulation for calibration."""
    
    print("Creating base tetanus simulation...")
    
    # Create people with smaller population
    people = ss.People(n_agents=N_AGENTS)
    
    # Create tetanus disease with default parameters
    tetanus = zds.Tetanus(dict(
        # Default parameters (will be calibrated)
        neonatal_wound_rate=ss.peryear(0.1),
        peri_neonatal_wound_rate=ss.peryear(0.01),
        childhood_wound_rate=ss.peryear(0.05),
        adult_wound_rate=ss.peryear(0.03),
        neonatal_cfr=0.8,
        peri_neonatal_cfr=0.4,
        childhood_cfr=0.1,
        adult_cfr=0.2,
        maternal_vaccination_efficacy=0.6,
        maternal_vaccination_coverage=0.4,
        dur_inf=ss.lognorm_ex(mean=ss.years(3/12)),
        p_severe=ss.bernoulli(p=0.3),
        waning=ss.peryear(0.055),
    ))
    
    # Create networks and demographics
    networks = [
        ss.RandomNet(dict(n_contacts=8, dur=0), name='household'),
        ss.RandomNet(dict(n_contacts=15, dur=0), name='community')
    ]
    demographics = [
        ss.Births(dict(birth_rate=25)),  # 25 per 1000 population
        ss.Deaths(dict(death_rate=8))    # 8 per 1000 population
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=[tetanus],
        networks=networks,
        demographics=demographics,
        pars={'dur': DURATION*365, 'dt': 30}  # 3 years, monthly timesteps
    )
    
    print(f"✓ Created tetanus simulation with {N_AGENTS:,} agents")
    return sim

def apply_tetanus_calibration_parameters(sim, calib_pars):
    """Apply calibrated parameters to tetanus simulation."""
    
    # Get tetanus disease module
    tetanus = sim.diseases['tetanus']
    
    # Apply age-specific wound exposure rates
    if 'neonatal_wound_rate' in calib_pars:
        tetanus.pars.neonatal_wound_rate = ss.peryear(calib_pars['neonatal_wound_rate'])
    if 'peri_neonatal_wound_rate' in calib_pars:
        tetanus.pars.peri_neonatal_wound_rate = ss.peryear(calib_pars['peri_neonatal_wound_rate'])
    if 'childhood_wound_rate' in calib_pars:
        tetanus.pars.childhood_wound_rate = ss.peryear(calib_pars['childhood_wound_rate'])
    if 'adult_wound_rate' in calib_pars:
        tetanus.pars.adult_wound_rate = ss.peryear(calib_pars['adult_wound_rate'])
    
    # Apply age-specific case fatality rates
    if 'neonatal_cfr' in calib_pars:
        tetanus.pars.neonatal_cfr = calib_pars['neonatal_cfr']
    if 'peri_neonatal_cfr' in calib_pars:
        tetanus.pars.peri_neonatal_cfr = calib_pars['peri_neonatal_cfr']
    if 'childhood_cfr' in calib_pars:
        tetanus.pars.childhood_cfr = calib_pars['childhood_cfr']
    if 'adult_cfr' in calib_pars:
        tetanus.pars.adult_cfr = calib_pars['adult_cfr']
    
    # Apply maternal vaccination parameters
    if 'maternal_vaccination_efficacy' in calib_pars:
        tetanus.pars.maternal_vaccination_efficacy = calib_pars['maternal_vaccination_efficacy']
    if 'maternal_vaccination_coverage' in calib_pars:
        tetanus.pars.maternal_vaccination_coverage = calib_pars['maternal_vaccination_coverage']
    
    # Apply general parameters
    if 'tetanus_dur_inf' in calib_pars:
        tetanus.pars.dur_inf = ss.lognorm_ex(mean=ss.days(calib_pars['tetanus_dur_inf']))
    if 'tetanus_waning' in calib_pars:
        tetanus.pars.waning = ss.peryear(calib_pars['tetanus_waning'])
    
    return sim

def build_tetanus_simulation(sim, calib_pars, n_reps=1):
    """Build tetanus simulation with calibrated parameters."""
    
    # Apply calibration parameters
    sim = apply_tetanus_calibration_parameters(sim, calib_pars)
    
    # Create multi-simulation for parallel processing
    msim = ss.MultiSim(sim, n_reps=n_reps)
    msim.run()
    
    return msim

def run_parallel_tetanus_calibration():
    """Run parallel tetanus calibration system."""
    
    print("="*80)
    print("PARALLEL TETANUS MODEL CALIBRATION")
    print("="*80)
    print("Key features:")
    print(f"✓ Population size: {N_AGENTS:,} agents (optimized for speed)")
    print(f"✓ Number of replicates: {N_REPS} (parallel processing)")
    print(f"✓ Total trials: {N_TRIALS:,}")
    print(f"✓ Number of workers: {N_WORKERS}")
    print(f"✓ Simulation duration: {DURATION} years")
    print("")
    
    # Load targets and create components
    targets = load_tetanus_targets()
    components = create_tetanus_calibration_components(targets)
    calib_pars = define_tetanus_calibration_parameters()
    
    # Create base simulation
    sim = create_tetanus_simulation()
    
    # Create calibration system
    print("Creating parallel calibration system...")
    calib = ss.Calibration(
        calib_pars=calib_pars,
        sim=sim,
        build_fn=build_tetanus_simulation,
        build_kw=dict(n_reps=N_REPS),
        reseed=True,
        components=components,
        total_trials=N_TRIALS,
        db_name=f'{RESDIR}/tetanus_calibration.db',
        continue_db=False,
        keep_db=True,
        n_workers=N_WORKERS,
        study_name='Tetanus_Parallel_Calibration',
        die=False,  # Don't die on errors
        debug=DEBUG,
    )
    
    print("✓ Created parallel calibration system")
    
    # Save metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'n_trials': N_TRIALS,
        'n_reps': N_REPS,
        'n_agents': N_AGENTS,
        'n_workers': N_WORKERS,
        'duration': DURATION,
        'debug': DEBUG,
        'targets': targets
    }
    
    with open(f'{RESDIR}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Run calibration
    print(f"\nRunning parallel calibration with {N_TRIALS:,} trials...")
    T = sc.timer()
    
    try:
        calib.calibrate()
        print("✓ Parallel calibration completed successfully")
    except KeyboardInterrupt:
        print("⚠ Calibration interrupted by user")
    except Exception as e:
        print(f"⚠ Calibration failed: {e}")
        import traceback
        traceback.print_exc()
    
    T.toc()
    
    # Save results
    calib.save_csv(f'{RESDIR}/tetanus_calib_pars.csv', top_k=100)
    
    # Check fit
    print("\nChecking calibration fit...")
    calib.build_kw['n_reps'] = N_REPS * 2  # More reps for final check
    calib.check_fit(do_plot=False)
    
    # Create visualizations
    print("\nCreating calibration visualizations...")
    create_tetanus_calibration_plots(calib)
    
    # Generate summary report
    print("\nGenerating summary report...")
    generate_tetanus_calibration_report(calib, targets)
    
    print("\n" + "="*80)
    print("PARALLEL TETANUS CALIBRATION COMPLETED")
    print("="*80)
    print(f"Results saved to: {RESDIR}/")
    print("Key files:")
    print(f"  - tetanus_calib_pars.csv: Best parameter sets")
    print(f"  - metadata.json: Calibration metadata")
    print(f"  - tetanus_calibration_plots.pdf: Visualization results")
    print(f"  - tetanus_calibration_report.md: Summary report")

def create_tetanus_calibration_plots(calib):
    """Create comprehensive tetanus calibration visualizations."""
    
    print("Creating tetanus calibration plots...")
    
    # Component plots
    try:
        figs = calib.plot()
        for i, fig in enumerate(figs):
            fig.savefig(f'{RESDIR}/tetanus_component_{i}.pdf', dpi=300, bbox_inches='tight')
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
                fig.savefig(f'{RESDIR}/tetanus_{lbl}.pdf', dpi=300, bbox_inches='tight')
                plt.close(fig)
            except Exception as e:
                print(f"⚠ Could not save tetanus_{lbl}.pdf: {e}")
    except Exception as e:
        print(f"⚠ Could not create optimization plots: {e}")
    
    # Parameter distribution plots
    try:
        create_tetanus_parameter_distribution_plots()
    except Exception as e:
        print(f"⚠ Could not create parameter distribution plots: {e}")
    
    print("✓ Tetanus calibration plots created")

def create_tetanus_parameter_distribution_plots():
    """Create tetanus parameter distribution plots."""
    
    try:
        # Load calibration results
        results_df = pd.read_csv(f'{RESDIR}/tetanus_calib_pars.csv')
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
    plt.savefig(f'{RESDIR}/tetanus_parameter_distributions.pdf', dpi=300, bbox_inches='tight')
    plt.close()

def generate_tetanus_calibration_report(calib, targets):
    """Generate comprehensive tetanus calibration report."""
    
    print("Generating tetanus calibration report...")
    
    # Load results
    try:
        results_df = pd.read_csv(f'{RESDIR}/tetanus_calib_pars.csv')
    except:
        print("⚠ Could not load calibration results for report")
        return
    
    # Create report
    report = []
    report.append("# Parallel Tetanus Model Calibration Report")
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
    report.append("## Best Tetanus Parameters")
    best_params = results_df.iloc[0]
    param_cols = [col for col in results_df.columns if col.startswith('params_')]
    
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        report.append(f"- {param_name}: {best_params[param]:.4f}")
    
    report.append("")
    
    # Target values
    report.append("## Calibration Targets")
    tetanus_target = targets['tetanus']
    report.append(f"- Neonatal proportion: {tetanus_target['neonatal_proportion']:.1%}")
    report.append(f"- Peri-neonatal proportion: {tetanus_target['peri_neonatal_proportion']:.1%}")
    report.append(f"- Neonatal rate per 1000 births: {tetanus_target['neonatal_rate_per_1000_births']:.2f}")
    report.append(f"- Tetanus prevalence: {tetanus_target['prevalence']:.4f}")
    report.append(f"- Maternal vaccination coverage: {tetanus_target['vaccination_coverage']:.1%}")
    report.append("")
    
    # Technical details
    report.append("## Technical Implementation")
    report.append(f"- Population size: {N_AGENTS:,} agents")
    report.append(f"- Number of replicates: {N_REPS}")
    report.append(f"- Number of workers: {N_WORKERS}")
    report.append(f"- Simulation duration: {DURATION} years")
    report.append(f"- Total trials: {N_TRIALS:,}")
    report.append("")
    
    # Key improvements
    report.append("## Key Improvements")
    report.append("1. **Parallel Processing**: Multiple workers for faster calibration")
    report.append("2. **Smaller Population**: Optimized for speed while maintaining accuracy")
    report.append("3. **Multiple Replicates**: Better statistical power")
    report.append("4. **Real Data Integration**: Based on actual tetanus data")
    report.append("5. **Age-Specific Parameters**: Neonatal, peri-neonatal, childhood, adult")
    report.append("6. **Maternal Vaccination**: Realistic vaccination parameters")
    report.append("")
    
    # Save report
    with open(f'{RESDIR}/tetanus_calibration_report.md', 'w') as f:
        f.write('\n'.join(report))
    
    print("✓ Tetanus calibration report generated")

def main():
    """Main function to run parallel tetanus calibration."""
    
    try:
        run_parallel_tetanus_calibration()
    except Exception as e:
        print(f"❌ Parallel tetanus calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
