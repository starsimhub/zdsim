#!/usr/bin/env python3
"""
Simple Tetanus Model Calibration

This script implements a streamlined tetanus calibration using smaller populations
and multiple simulations to efficiently match real-world target values.
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
DEBUG = True
N_TRIALS = [100, 10][DEBUG]
N_REPS = [3, 2][DEBUG]
N_AGENTS = [1000, 500][DEBUG]
N_WORKERS = min(4, sc.cpu_count())
DURATION = 2  # Years

def load_tetanus_targets():
    """Load tetanus targets from real data."""
    
    print("Loading tetanus targets from real data...")
    
    try:
        data_file = 'zdsim/data/zerodose_data.dta'
        data = pd.read_stata(data_file)
        
        # Extract tetanus data
        total_tetanus = data['tetanus'].sum()
        neonatal_cases = data['neonatal_tetanus'].sum()
        peri_neonatal_cases = data['peri_neonatal_tetanus'].sum()
        
        # Calculate targets
        neonatal_proportion = neonatal_cases / total_tetanus
        peri_neonatal_proportion = peri_neonatal_cases / total_tetanus
        
        targets = {
            'neonatal_proportion': neonatal_proportion,
            'peri_neonatal_proportion': peri_neonatal_proportion,
            'total_cases': total_tetanus,
            'neonatal_cases': neonatal_cases,
            'peri_neonatal_cases': peri_neonatal_cases
        }
        
        print(f"✓ Loaded targets:")
        print(f"  Neonatal proportion: {neonatal_proportion:.1%}")
        print(f"  Peri-neonatal proportion: {peri_neonatal_proportion:.1%}")
        
        return targets
        
    except Exception as e:
        print(f"⚠ Could not load real data: {e}")
        return {
            'neonatal_proportion': 0.227,
            'peri_neonatal_proportion': 0.00004,
            'total_cases': 50000,
            'neonatal_cases': 11340,
            'peri_neonatal_cases': 2
        }

def create_tetanus_simulation():
    """Create tetanus simulation."""
    
    print(f"Creating tetanus simulation with {N_AGENTS:,} agents...")
    
    # Create people
    people = ss.People(n_agents=N_AGENTS)
    
    # Create tetanus disease
    tetanus = zds.Tetanus(dict(
        neonatal_wound_rate=ss.peryear(0.5),
        peri_neonatal_wound_rate=ss.peryear(0.01),
        childhood_wound_rate=ss.peryear(0.1),
        adult_wound_rate=ss.peryear(0.05),
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
        ss.Births(dict(birth_rate=25)),
        ss.Deaths(dict(death_rate=8))
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=[tetanus],
        networks=networks,
        demographics=demographics,
        pars={'dur': DURATION*365, 'dt': 30}
    )
    
    return sim

def run_tetanus_calibration():
    """Run tetanus calibration."""
    
    print("="*80)
    print("SIMPLE TETANUS MODEL CALIBRATION")
    print("="*80)
    print(f"Configuration:")
    print(f"  Population: {N_AGENTS:,} agents")
    print(f"  Replicates: {N_REPS}")
    print(f"  Trials: {N_TRIALS:,}")
    print(f"  Workers: {N_WORKERS}")
    print(f"  Duration: {DURATION} years")
    print("")
    
    # Load targets
    targets = load_tetanus_targets()
    
    # Create simulation
    sim = create_tetanus_simulation()
    
    # Define calibration parameters
    calib_pars = {
        'neonatal_wound_rate': dict(low=0.01, high=2.0, guess=0.5, suggest_type='suggest_float', log=True),
        'peri_neonatal_wound_rate': dict(low=0.001, high=0.1, guess=0.01, suggest_type='suggest_float', log=True),
        'childhood_wound_rate': dict(low=0.01, high=1.0, guess=0.1, suggest_type='suggest_float', log=True),
        'adult_wound_rate': dict(low=0.01, high=1.0, guess=0.05, suggest_type='suggest_float', log=True),
        'maternal_vaccination_efficacy': dict(low=0.3, high=0.9, guess=0.6, suggest_type='suggest_float', log=False),
        'maternal_vaccination_coverage': dict(low=0.2, high=0.8, guess=0.4, suggest_type='suggest_float', log=False),
    }
    
    # Create calibration components
    components = []
    
    # Neonatal proportion component
    neonatal_comp = ss.Binomial(
        name='Neonatal Tetanus Proportion',
        weight=8.0,
        conform='prevalent',
        expected=pd.DataFrame({
            'x': [int(targets['neonatal_proportion'] * 1000)],
            'n': [1000],
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_neonatal,
            'n': sim.results.tetanus.n_infected,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    # Peri-neonatal proportion component
    peri_neonatal_comp = ss.Binomial(
        name='Peri-neonatal Tetanus Proportion',
        weight=3.0,
        conform='prevalent',
        expected=pd.DataFrame({
            'x': [int(targets['peri_neonatal_proportion'] * 1000)],
            'n': [1000],
        }, index=pd.Index([ss.date('2018-06-01')], name='t')),
        extract_fn=lambda sim: pd.DataFrame({
            'x': sim.results.tetanus.n_peri_neonatal,
            'n': sim.results.tetanus.n_infected,
        }, index=pd.Index(sim.results.timevec, name='t')),
    )
    
    components = [neonatal_comp, peri_neonatal_comp]
    
    # Set component properties
    for comp in components:
        comp.n_boot = 1
        comp.combine_reps = 'sum'
        comp.combine_kwargs = dict(numeric_only=True)
    
    # Create calibration
    print("Creating calibration system...")
    calib = ss.Calibration(
        calib_pars=calib_pars,
        sim=sim,
        build_fn=lambda sim, calib_pars, n_reps=1: ss.MultiSim(apply_parameters(sim, calib_pars), n_reps=n_reps).run(),
        build_kw=dict(n_reps=N_REPS),
        reseed=True,
        components=components,
        total_trials=N_TRIALS,
        db_name='simple_tetanus_calibration.db',
        continue_db=False,
        keep_db=True,
        n_workers=N_WORKERS,
        study_name='Simple_Tetanus_Calibration',
        die=False,
        debug=DEBUG,
    )
    
    print("✓ Created calibration system")
    
    # Run calibration
    print(f"\nRunning calibration with {N_TRIALS:,} trials...")
    T = sc.timer()
    
    try:
        calib.calibrate()
        print("✓ Calibration completed successfully")
    except KeyboardInterrupt:
        print("⚠ Calibration interrupted by user")
    except Exception as e:
        print(f"⚠ Calibration failed: {e}")
        import traceback
        traceback.print_exc()
    
    T.toc()
    
    # Save results
    calib.save_csv('simple_tetanus_calib_pars.csv', top_k=50)
    
    # Create summary
    print("\nGenerating calibration summary...")
    generate_summary(calib, targets)
    
    print("\n" + "="*80)
    print("SIMPLE TETANUS CALIBRATION COMPLETED")
    print("="*80)
    print("Results saved to:")
    print("  - simple_tetanus_calib_pars.csv")
    print("  - simple_tetanus_calibration_summary.md")

def apply_parameters(sim, calib_pars):
    """Apply calibrated parameters to simulation."""
    
    tetanus = sim.diseases['tetanus']
    
    if 'neonatal_wound_rate' in calib_pars:
        tetanus.pars.neonatal_wound_rate = ss.peryear(calib_pars['neonatal_wound_rate'])
    if 'peri_neonatal_wound_rate' in calib_pars:
        tetanus.pars.peri_neonatal_wound_rate = ss.peryear(calib_pars['peri_neonatal_wound_rate'])
    if 'childhood_wound_rate' in calib_pars:
        tetanus.pars.childhood_wound_rate = ss.peryear(calib_pars['childhood_wound_rate'])
    if 'adult_wound_rate' in calib_pars:
        tetanus.pars.adult_wound_rate = ss.peryear(calib_pars['adult_wound_rate'])
    if 'maternal_vaccination_efficacy' in calib_pars:
        tetanus.pars.maternal_vaccination_efficacy = calib_pars['maternal_vaccination_efficacy']
    if 'maternal_vaccination_coverage' in calib_pars:
        tetanus.pars.maternal_vaccination_coverage = calib_pars['maternal_vaccination_coverage']
    
    return sim

def generate_summary(calib, targets):
    """Generate calibration summary."""
    
    try:
        results_df = pd.read_csv('simple_tetanus_calib_pars.csv')
    except:
        print("⚠ Could not load calibration results")
        return
    
    # Create summary
    summary = []
    summary.append("# Simple Tetanus Model Calibration Summary")
    summary.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary.append("")
    
    # Summary statistics
    summary.append("## Calibration Summary")
    summary.append(f"- Total trials: {len(results_df)}")
    summary.append(f"- Best fitness: {results_df['value'].min():.4f}")
    summary.append(f"- Mean fitness: {results_df['value'].mean():.4f}")
    summary.append("")
    
    # Best parameters
    summary.append("## Best Parameters")
    best_params = results_df.iloc[0]
    param_cols = [col for col in results_df.columns if col.startswith('params_')]
    
    for param in param_cols:
        param_name = param.replace('params_', '').replace('_', ' ').title()
        summary.append(f"- {param_name}: {best_params[param]:.4f}")
    
    summary.append("")
    
    # Target values
    summary.append("## Target Values")
    summary.append(f"- Neonatal proportion: {targets['neonatal_proportion']:.1%}")
    summary.append(f"- Peri-neonatal proportion: {targets['peri_neonatal_proportion']:.1%}")
    summary.append("")
    
    # Save summary
    with open('simple_tetanus_calibration_summary.md', 'w') as f:
        f.write('\n'.join(summary))
    
    print("✓ Calibration summary generated")

def main():
    """Main function."""
    
    try:
        run_tetanus_calibration()
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
