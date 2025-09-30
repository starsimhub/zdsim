#!/usr/bin/env python3
"""
Final Tetanus Model Calibration

This script implements a working tetanus calibration that properly handles
the Starsim structure and saves results to JSON.
"""

import numpy as np
import pandas as pd
import starsim as ss
import zdsim as zds
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

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

def run_tetanus_simulation_with_params(params):
    """Run tetanus simulation with given parameters."""
    
    try:
        # Create people
        people = ss.People(n_agents=1000)
        
        # Create tetanus disease with parameters
        tetanus = zds.Tetanus(dict(
            neonatal_wound_rate=ss.peryear(params.get('neonatal_wound_rate', 0.5)),
            peri_neonatal_wound_rate=ss.peryear(params.get('peri_neonatal_wound_rate', 0.01)),
            childhood_wound_rate=ss.peryear(params.get('childhood_wound_rate', 0.1)),
            adult_wound_rate=ss.peryear(params.get('adult_wound_rate', 0.05)),
            neonatal_cfr=params.get('neonatal_cfr', 0.8),
            peri_neonatal_cfr=params.get('peri_neonatal_cfr', 0.4),
            childhood_cfr=params.get('childhood_cfr', 0.1),
            adult_cfr=params.get('adult_cfr', 0.2),
            maternal_vaccination_efficacy=params.get('maternal_vaccination_efficacy', 0.6),
            maternal_vaccination_coverage=params.get('maternal_vaccination_coverage', 0.4),
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
            pars={'dur': 2*365, 'dt': 30}
        )
        
        # Run simulation
        sim.run()
        
        # Extract results
        tetanus_results = sim.diseases[0]  # First disease is tetanus
        
        neonatal_cases = np.sum(tetanus_results.neonatal)
        peri_neonatal_cases = np.sum(tetanus_results.peri_neonatal)
        total_cases = np.sum(tetanus_results.infected)
        
        # Calculate proportions
        neonatal_proportion = neonatal_cases / total_cases if total_cases > 0 else 0
        peri_neonatal_proportion = peri_neonatal_cases / total_cases if total_cases > 0 else 0
        
        return {
            'neonatal_cases': int(neonatal_cases),
            'peri_neonatal_cases': int(peri_neonatal_cases),
            'total_cases': int(total_cases),
            'neonatal_proportion': float(neonatal_proportion),
            'peri_neonatal_proportion': float(peri_neonatal_proportion)
        }
        
    except Exception as e:
        print(f"⚠ Simulation failed: {e}")
        return None

def run_tetanus_calibration():
    """Run tetanus calibration with parameter optimization."""
    
    print("="*80)
    print("FINAL TETANUS MODEL CALIBRATION")
    print("="*80)
    print("Running parameter optimization to match real-world data...")
    print("")
    
    # Load targets
    targets = load_tetanus_targets()
    
    # Define parameter ranges
    param_ranges = {
        'neonatal_wound_rate': (0.01, 2.0),
        'peri_neonatal_wound_rate': (0.001, 0.1),
        'childhood_wound_rate': (0.01, 1.0),
        'adult_wound_rate': (0.01, 1.0),
        'maternal_vaccination_efficacy': (0.3, 0.9),
        'maternal_vaccination_coverage': (0.2, 0.8),
        'neonatal_cfr': (0.5, 0.95),
        'peri_neonatal_cfr': (0.2, 0.8),
        'childhood_cfr': (0.05, 0.5),
        'adult_cfr': (0.1, 0.6)
    }
    
    # Run parameter optimization
    print("Running parameter optimization...")
    best_params = None
    best_score = float('inf')
    best_results = None
    calibration_history = []
    
    n_trials = 20  # Number of parameter combinations to try
    
    for trial in range(n_trials):
        print(f"Trial {trial + 1}/{n_trials}...")
        
        # Generate random parameters within ranges
        params = {}
        for param, (low, high) in param_ranges.items():
            if param in ['neonatal_wound_rate', 'peri_neonatal_wound_rate', 'childhood_wound_rate', 'adult_wound_rate']:
                # Log scale for wound rates
                params[param] = np.exp(np.random.uniform(np.log(low), np.log(high)))
            else:
                # Linear scale for other parameters
                params[param] = np.random.uniform(low, high)
        
        # Run simulation
        results = run_tetanus_simulation_with_params(params)
        
        if results is not None:
            # Calculate score based on target matching
            neonatal_error = abs(results['neonatal_proportion'] - targets['neonatal_proportion'])
            peri_neonatal_error = abs(results['peri_neonatal_proportion'] - targets['peri_neonatal_proportion'])
            
            # Weighted score (neonatal is more important)
            score = 0.8 * neonatal_error + 0.2 * peri_neonatal_error
            
            # Store trial results
            trial_result = {
                'trial': trial + 1,
                'parameters': params,
                'results': results,
                'score': score,
                'neonatal_error': neonatal_error,
                'peri_neonatal_error': peri_neonatal_error
            }
            calibration_history.append(trial_result)
            
            # Update best if this is better
            if score < best_score:
                best_score = score
                best_params = params.copy()
                best_results = results.copy()
                print(f"  ✓ New best score: {score:.4f}")
                print(f"    Neonatal proportion: {results['neonatal_proportion']:.1%} (target: {targets['neonatal_proportion']:.1%})")
                print(f"    Peri-neonatal proportion: {results['peri_neonatal_proportion']:.1%} (target: {targets['peri_neonatal_proportion']:.1%})")
            else:
                print(f"  Score: {score:.4f}")
        else:
            print(f"  ⚠ Simulation failed")
    
    # Create results dictionary
    results = {
        'calibration_metadata': {
            'timestamp': datetime.now().isoformat(),
            'n_trials': n_trials,
            'n_agents': 1000,
            'duration_years': 2,
            'optimization_method': 'random_search'
        },
        'target_values': targets,
        'best_parameters': best_params,
        'best_results': best_results,
        'best_score': float(best_score),
        'calibration_summary': {
            'total_trials': n_trials,
            'successful_trials': len([t for t in calibration_history if t['results'] is not None]),
            'failed_trials': len([t for t in calibration_history if t['results'] is None]),
            'best_trial': min(range(len(calibration_history)), key=lambda i: calibration_history[i]['score']) + 1 if calibration_history else None,
            'optimization_direction': 'minimize'
        },
        'calibration_history': calibration_history
    }
    
    # Save to JSON file
    json_file = 'tetanus_calibration_results.json'
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Calibration results saved to: {json_file}")
    
    # Print summary
    if best_params is not None:
        print(f"\nCALIBRATION SUMMARY:")
        print(f"  Best score: {best_score:.4f}")
        print(f"  Best parameters:")
        for param, value in best_params.items():
            print(f"    {param}: {value:.4f}")
        print(f"  Best results:")
        print(f"    Neonatal proportion: {best_results['neonatal_proportion']:.1%} (target: {targets['neonatal_proportion']:.1%})")
        print(f"    Peri-neonatal proportion: {best_results['peri_neonatal_proportion']:.1%} (target: {targets['peri_neonatal_proportion']:.1%})")
        print(f"    Total cases: {best_results['total_cases']:,}")
        print(f"    Neonatal cases: {best_results['neonatal_cases']:,}")
        print(f"    Peri-neonatal cases: {best_results['peri_neonatal_cases']:,}")
    
    return results

def main():
    """Main function."""
    
    try:
        results = run_tetanus_calibration()
        
        print("\n" + "="*80)
        print("TETANUS CALIBRATION COMPLETED SUCCESSFULLY")
        print("="*80)
        print("Results saved to: tetanus_calibration_results.json")
        print("Key findings:")
        if results['best_parameters']:
            print(f"  Best score: {results['best_score']:.4f}")
            print(f"  Successful trials: {results['calibration_summary']['successful_trials']}")
            print(f"  Best parameters found for tetanus model optimization")
            print(f"  Neonatal proportion achieved: {results['best_results']['neonatal_proportion']:.1%}")
            print(f"  Peri-neonatal proportion achieved: {results['best_results']['peri_neonatal_proportion']:.1%}")
        else:
            print("  No successful trials - check simulation parameters")
            
    except Exception as e:
        print(f"❌ Calibration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
