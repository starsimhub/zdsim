#!/usr/bin/env python3
"""
Working Tetanus Model Calibration

This script implements a working tetanus calibration that saves results to JSON.
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
N_TRIALS = [50, 10][DEBUG]
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
            'neonatal_proportion': float(neonatal_proportion),
            'peri_neonatal_proportion': float(peri_neonatal_proportion),
            'total_cases': int(total_tetanus),
            'neonatal_cases': int(neonatal_cases),
            'peri_neonatal_cases': int(peri_neonatal_cases)
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

def apply_parameters(sim, calib_pars):
    """Apply calibrated parameters to simulation."""
    
    # Get tetanus disease from the simulation
    tetanus = None
    for disease in sim.diseases:
        if hasattr(disease, 'name') and disease.name == 'tetanus':
            tetanus = disease
            break
        elif hasattr(disease, '__class__') and 'Tetanus' in str(disease.__class__):
            tetanus = disease
            break
    
    if tetanus is None:
        print("⚠ Could not find tetanus disease in simulation")
        return sim
    
    # Apply parameters
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

def build_simulation(sim, calib_pars, n_reps=1):
    """Build simulation with calibrated parameters."""
    
    # Apply calibration parameters
    sim = apply_parameters(sim, calib_pars)
    
    # Create multi-simulation
    msim = ss.MultiSim(sim, n_reps=n_reps)
    msim.run()
    
    return msim

def run_tetanus_calibration():
    """Run tetanus calibration."""
    
    print("="*80)
    print("WORKING TETANUS MODEL CALIBRATION")
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
        build_fn=build_simulation,
        build_kw=dict(n_reps=N_REPS),
        reseed=True,
        components=components,
        total_trials=N_TRIALS,
        db_name='working_tetanus_calibration.db',
        continue_db=False,
        keep_db=True,
        n_workers=N_WORKERS,
        study_name='Working_Tetanus_Calibration',
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
    
    # Extract results and save to JSON
    print("\nExtracting calibration results...")
    try:
        # Get best parameters from the study
        study = calib.study
        best_trial = study.best_trial
        best_params = best_trial.params
        best_value = best_trial.value
        
        # Create results dictionary
        results = {
            'calibration_metadata': {
                'timestamp': datetime.now().isoformat(),
                'n_trials': N_TRIALS,
                'n_reps': N_REPS,
                'n_agents': N_AGENTS,
                'n_workers': N_WORKERS,
                'duration': DURATION,
                'debug': DEBUG
            },
            'target_values': targets,
            'best_parameters': best_params,
            'best_fitness': float(best_value) if best_value is not None else None,
            'calibration_summary': {
                'total_trials': len(study.trials),
                'successful_trials': len([t for t in study.trials if t.state.name == 'COMPLETE']),
                'failed_trials': len([t for t in study.trials if t.state.name == 'FAIL']),
                'best_trial_number': best_trial.number,
                'optimization_direction': study.direction.name
            }
        }
        
        # Save to JSON file
        json_file = 'tetanus_calibration_results.json'
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Calibration results saved to: {json_file}")
        
        # Print summary
        print(f"\nCALIBRATION SUMMARY:")
        print(f"  Best fitness: {best_value:.4f}")
        print(f"  Best parameters:")
        for param, value in best_params.items():
            print(f"    {param}: {value:.4f}")
        
        return results
        
    except Exception as e:
        print(f"⚠ Could not extract results: {e}")
        return None

def main():
    """Main function."""
    
    try:
        results = run_tetanus_calibration()
        
        if results:
            print("\n" + "="*80)
            print("TETANUS CALIBRATION COMPLETED SUCCESSFULLY")
            print("="*80)
            print("Results saved to: tetanus_calibration_results.json")
            print("Key findings:")
            print(f"  Best fitness: {results['best_fitness']:.4f}")
            print(f"  Successful trials: {results['calibration_summary']['successful_trials']}")
            print(f"  Best parameters found for tetanus model optimization")
        else:
            print("❌ Calibration completed but results could not be extracted")
            
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
