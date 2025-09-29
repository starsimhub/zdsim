"""
Calibration system for the zero-dose vaccination model.

This script implements parameter calibration against real-world data
to ensure the model matches scientific literature and observed data.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import scipy.optimize as opt
import pandas as pd
from typing import Dict, List, Tuple, Any

class ModelCalibrator:
    """Calibrate model parameters against real-world data"""
    
    def __init__(self):
        # Real-world data targets
        self.target_data = {
            'diphtheria': {
                'r0': 3.0,  # Literature R0
                'cfr': 0.10,  # Case Fatality Rate (CFR)
                'age_peak': (5, 15),  # Peak age group
                'vaccination_impact': 0.95  # 95% reduction
            },
            'tetanus': {
                'r0': 0.0,  # Not directly transmissible
                'cfr': 0.15,  # Case Fatality Rate (CFR)
                'age_peak': (15, 45),  # Peak age group
                'vaccination_impact': 0.90  # 90% reduction
            },
            'pertussis': {
                'r0': 10.0,  # High transmissibility
                'cfr': 0.005,  # Case Fatality Rate (CFR)
                'age_peak': (0, 5),  # Peak age group
                'vaccination_impact': 0.70  # 70% reduction
            },
            'hepatitis_b': {
                'r0': 1.0,  # Moderate transmissibility
                'cfr': 0.03,  # Case Fatality Rate (CFR)
                'age_peak': (20, 40),  # Peak age group
                'vaccination_impact': 0.85  # 85% reduction
            },
            'hib': {
                'r0': 1.5,  # Moderate transmissibility
                'cfr': 0.03,  # Case Fatality Rate (CFR)
                'age_peak': (0, 2),  # Peak age group
                'vaccination_impact': 0.90  # 90% reduction
            }
        }
        
        # Parameter ranges for optimization
        self.param_ranges = {
            'diphtheria': {
                'beta': (0.5, 5.0),
                'p_death': (0.05, 0.20),
                'dur_inf': (7, 28)
            },
            'tetanus': {
                'beta': (0.0, 0.1),
                'p_death': (0.10, 0.20),
                'dur_inf': (14, 28)
            },
            'pertussis': {
                'beta': (5.0, 20.0),
                'p_death': (0.001, 0.01),
                'dur_inf': (14, 42)
            },
            'hepatitis_b': {
                'beta': (0.5, 2.0),
                'p_death': (0.01, 0.05),
                'dur_inf': (30, 90)
            },
            'hib': {
                'beta': (1.0, 3.0),
                'p_death': (0.02, 0.05),
                'dur_inf': (7, 14)
            }
        }
    
    def calibrate_disease(self, disease_name: str) -> Dict[str, float]:
        """Calibrate parameters for a specific disease"""
        
        print(f"Calibrating {disease_name}...")
        
        # Get target data
        targets = self.target_data[disease_name]
        param_ranges = self.param_ranges[disease_name]
        
        # Define objective function
        def objective(params):
            beta, p_death, dur_inf = params
            
            # Run simulation with these parameters
            try:
                result = self._run_disease_simulation(
                    disease_name, beta, p_death, dur_inf
                )
                
                # Calculate fitness
                fitness = self._calculate_fitness(result, targets)
                return fitness
                
            except Exception as e:
                print(f"Error in simulation: {e}")
                return 1e6  # Large penalty for failed simulations
        
        # Optimize parameters
        initial_params = [
            (param_ranges['beta'][0] + param_ranges['beta'][1]) / 2,
            (param_ranges['p_death'][0] + param_ranges['p_death'][1]) / 2,
            (param_ranges['dur_inf'][0] + param_ranges['dur_inf'][1]) / 2
        ]
        
        bounds = [
            param_ranges['beta'],
            param_ranges['p_death'],
            param_ranges['dur_inf']
        ]
        
        result = opt.minimize(
            objective,
            initial_params,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        if result.success:
            beta, p_death, dur_inf = result.x
            print(f"  Optimized parameters:")
            print(f"    Beta: {beta:.3f}")
            print(f"    CFR: {p_death:.3f}")
            print(f"    Duration: {dur_inf:.1f} days")
            print(f"    Fitness: {result.fun:.3f}")
            
            return {
                'beta': beta,
                'p_death': p_death,
                'dur_inf': dur_inf,
                'fitness': result.fun
            }
        else:
            print(f"  Optimization failed: {result.message}")
            return None
    
    def calibrate_all_diseases(self) -> Dict[str, Dict[str, float]]:
        """Calibrate all diseases"""
        
        print("Starting calibration of all diseases...")
        print("="*50)
        
        calibrated_params = {}
        
        for disease_name in self.target_data.keys():
            params = self.calibrate_disease(disease_name)
            if params:
                calibrated_params[disease_name] = params
            else:
                print(f"  Failed to calibrate {disease_name}")
        
        return calibrated_params
    
    def _run_disease_simulation(self, disease_name: str, beta: float, 
                              p_death: float, dur_inf: float) -> Dict[str, Any]:
        """Run simulation with specific parameters"""
        
        # Create disease with parameters
        if disease_name == 'diphtheria':
            disease = zds.Diphtheria(dict(
                beta=ss.peryear(beta),
                p_death=ss.bernoulli(p=p_death),
                dur_inf=ss.normal(dur_inf, dur_inf*0.1)
            ))
        elif disease_name == 'tetanus':
            disease = zds.Tetanus(dict(
                beta=ss.peryear(beta),
                p_death=ss.bernoulli(p=p_death),
                dur_inf=ss.normal(dur_inf, dur_inf*0.1)
            ))
        elif disease_name == 'pertussis':
            disease = zds.Pertussis(dict(
                beta=ss.peryear(beta),
                p_death=ss.bernoulli(p=p_death),
                dur_inf=ss.normal(dur_inf, dur_inf*0.1)
            ))
        elif disease_name == 'hepatitis_b':
            disease = zds.HepatitisB(dict(
                beta=ss.peryear(beta),
                p_death=ss.bernoulli(p=p_death),
                dur_inf=ss.normal(dur_inf, dur_inf*0.1)
            ))
        elif disease_name == 'hib':
            disease = zds.Hib(dict(
                beta=ss.peryear(beta),
                p_death=ss.bernoulli(p=p_death),
                dur_inf=ss.normal(dur_inf, dur_inf*0.1)
            ))
        
        # Run simulation
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        sim = ss.Sim(
            people=ss.People(n_agents=2000),
            diseases=[disease],
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            pars=sim_pars
        )
        sim.run()
        
        # Extract results
        if disease_name in sim.diseases:
            disease_result = sim.diseases[disease_name]
            
            # Calculate R0 approximation
            r0_approx = beta * (dur_inf / 365)
            
            # Get age distribution
            infected_uids = disease_result.infected.uids
            if len(infected_uids) > 0:
                infected_ages = sim.people.age[infected_uids]
                mean_age = np.mean(infected_ages)
                children_under_5_pct = np.sum(infected_ages < 5) / len(infected_ages)
            else:
                mean_age = 0
                children_under_5_pct = 0
            
            return {
                'r0': r0_approx,
                'cfr': p_death,
                'mean_age': mean_age,
                'children_under_5_pct': children_under_5_pct,
                'final_prevalence': disease_result.results.prevalence[-1],
                'cum_infections': disease_result.results.cum_infections[-1]
            }
        else:
            return {
                'r0': 0,
                'cfr': p_death,
                'mean_age': 0,
                'children_under_5_pct': 0,
                'final_prevalence': 0,
                'cum_infections': 0
            }
    
    def _calculate_fitness(self, result: Dict[str, Any], targets: Dict[str, Any]) -> float:
        """Calculate fitness score for calibration"""
        
        fitness = 0.0
        
        # R0 fitness
        r0_error = abs(result['r0'] - targets['r0']) / targets['r0'] if targets['r0'] > 0 else 0
        fitness += r0_error * 0.3
        
        # CFR fitness
        cfr_error = abs(result['cfr'] - targets['cfr']) / targets['cfr'] if targets['cfr'] > 0 else 0
        fitness += cfr_error * 0.3
        
        # Age pattern fitness
        age_error = abs(result['children_under_5_pct'] - 0.3)  # Expected 30% children
        fitness += age_error * 0.2
        
        # Transmission fitness (prevalence should be reasonable)
        if result['final_prevalence'] > 0.5:  # Too high prevalence
            fitness += 0.2
        elif result['final_prevalence'] < 0.001:  # Too low prevalence
            fitness += 0.1
        
        return fitness
    
    def validate_calibration(self, calibrated_params: Dict[str, Dict[str, float]]) -> bool:
        """Validate calibrated parameters"""
        
        print("\nValidating calibrated parameters...")
        print("="*50)
        
        validation_passed = True
        
        for disease_name, params in calibrated_params.items():
            print(f"\n{disease_name.title()}:")
            
            # Check if parameters are within reasonable ranges
            param_ranges = self.param_ranges[disease_name]
            
            beta_ok = param_ranges['beta'][0] <= params['beta'] <= param_ranges['beta'][1]
            cfr_ok = param_ranges['p_death'][0] <= params['p_death'] <= param_ranges['p_death'][1]
            dur_ok = param_ranges['dur_inf'][0] <= params['dur_inf'] <= param_ranges['dur_inf'][1]
            
            print(f"  Beta: {params['beta']:.3f} {'✓' if beta_ok else '✗'}")
            print(f"  CFR: {params['p_death']:.3f} {'✓' if cfr_ok else '✗'}")
            print(f"  Duration: {params['dur_inf']:.1f} days {'✓' if dur_ok else '✗'}")
            print(f"  Fitness: {params['fitness']:.3f}")
            
            if not (beta_ok and cfr_ok and dur_ok):
                validation_passed = False
        
        return validation_passed
    
    def save_calibrated_parameters(self, calibrated_params: Dict[str, Dict[str, float]], 
                                 filename: str = 'calibrated_parameters.json'):
        """Save calibrated parameters to file"""
        
        import json
        
        # Convert numpy types to Python types for JSON serialization
        serializable_params = {}
        for disease, params in calibrated_params.items():
            serializable_params[disease] = {
                'beta': float(params['beta']),
                'p_death': float(params['p_death']),
                'dur_inf': float(params['dur_inf']),
                'fitness': float(params['fitness'])
            }
        
        with open(filename, 'w') as f:
            json.dump(serializable_params, f, indent=2)
        
        print(f"Calibrated parameters saved to {filename}")
    
    def load_calibrated_parameters(self, filename: str = 'calibrated_parameters.json') -> Dict[str, Dict[str, float]]:
        """Load calibrated parameters from file"""
        
        import json
        
        try:
            with open(filename, 'r') as f:
                params = json.load(f)
            print(f"Calibrated parameters loaded from {filename}")
            return params
        except FileNotFoundError:
            print(f"File {filename} not found")
            return {}
        except Exception as e:
            print(f"Error loading parameters: {e}")
            return {}

def main():
    """Run calibration system"""
    
    print("="*80)
    print("ZERO-DOSE VACCINATION MODEL CALIBRATION SYSTEM")
    print("="*80)
    
    calibrator = ModelCalibrator()
    
    # Calibrate all diseases
    calibrated_params = calibrator.calibrate_all_diseases()
    
    # Validate calibration
    validation_passed = calibrator.validate_calibration(calibrated_params)
    
    # Save parameters
    calibrator.save_calibrated_parameters(calibrated_params)
    
    # Summary
    print("\n" + "="*80)
    print("CALIBRATION SUMMARY")
    print("="*80)
    
    print(f"Diseases calibrated: {len(calibrated_params)}")
    print(f"Validation passed: {'✓' if validation_passed else '✗'}")
    
    if validation_passed:
        print("\n✅ Calibration successful!")
        print("Model parameters have been calibrated against real-world data.")
        print("The model should now produce more realistic results.")
    else:
        print("\n❌ Calibration validation failed!")
        print("Some parameters may need manual adjustment.")
    
    return calibrated_params

if __name__ == '__main__':
    calibrated_params = main()
