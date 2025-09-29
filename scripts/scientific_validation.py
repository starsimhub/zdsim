"""
Scientific validation of the zero-dose vaccination model.

This script validates the model against known epidemiological facts,
disease parameters, and vaccination effectiveness data.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class ScientificValidator:
    """Validate model against scientific facts and epidemiological data"""
    
    def __init__(self):
        # Known epidemiological parameters from literature
        self.validation_data = {
            'diphtheria': {
                'r0_range': (1.7, 4.3),  # Basic reproduction number
                'cfr_range': (0.05, 0.20),  # Case Fatality Rate (CFR) range
                'incubation_days': (2, 5),
                'duration_days': (14, 28),
                'vaccine_efficacy': 0.95,  # DTP vaccine efficacy
                'age_susceptibility': 'children_5_15'  # Peak age group
            },
            'tetanus': {
                'r0_range': (0, 0),  # Not directly transmissible
                'cfr_range': (0.10, 0.20),  # Case Fatality Rate (CFR) range - high without treatment
                'incubation_days': (3, 21),
                'duration_days': (14, 28),
                'vaccine_efficacy': 0.95,
                'age_susceptibility': 'all_ages'  # Environmental exposure
            },
            'pertussis': {
                'r0_range': (5.5, 17.5),  # Very high transmissibility
                'cfr_range': (0.001, 0.01),  # Case Fatality Rate (CFR) range - low in general population
                'incubation_days': (7, 10),
                'duration_days': (21, 42),
                'vaccine_efficacy': 0.85,  # Wanes over time
                'age_susceptibility': 'infants_children'
            },
            'hepatitisb': {
                'r0_range': (0.5, 1.5),  # Moderate transmissibility
                'cfr_range': (0.01, 0.05),  # Case Fatality Rate (CFR) range - low acute phase
                'chronic_rate': 0.05,  # 5% become chronic
                'incubation_days': (45, 180),
                'duration_days': (30, 90),
                'vaccine_efficacy': 0.95,
                'age_susceptibility': 'all_ages'
            },
            'hib': {
                'r0_range': (1.0, 2.5),  # Moderate transmissibility
                'cfr_range': (0.02, 0.05),  # Case Fatality Rate (CFR) range - moderate with meningitis
                'meningitis_rate': 0.10,  # 10% develop meningitis
                'incubation_days': (2, 4),
                'duration_days': (7, 14),
                'vaccine_efficacy': 0.95,
                'age_susceptibility': 'children_under_5'
            }
        }
        
        # WHO vaccination coverage targets
        self.who_targets = {
            'diphtheria_coverage': 0.90,  # 90% coverage target
            'tetanus_coverage': 0.90,
            'pertussis_coverage': 0.90,
            'hepatitisb_coverage': 0.90,
            'hib_coverage': 0.90
        }
        
        # Expected impact ranges from literature
        self.expected_impact = {
            'diphtheria_reduction': (0.60, 0.95),  # 60-95% reduction
            'tetanus_reduction': (0.80, 0.99),   # 80-99% reduction
            'pertussis_reduction': (0.70, 0.90),  # 70-90% reduction
            'hepatitisb_reduction': (0.80, 0.95), # 80-95% reduction
            'hib_reduction': (0.85, 0.98)        # 85-98% reduction
        }
    
    def validate_disease_parameters(self):
        """Validate disease parameters against scientific literature"""
        
        print("=== DISEASE PARAMETER VALIDATION ===")
        
        validation_results = {}
        
        for disease_name, expected in self.validation_data.items():
            print(f"\n{disease_name.upper()}:")
            
            # Create disease instance
            if disease_name == 'diphtheria':
                disease = zds.Diphtheria()
            elif disease_name == 'tetanus':
                disease = zds.Tetanus()
            elif disease_name == 'pertussis':
                disease = zds.Pertussis()
            elif disease_name == 'hepatitisb':
                disease = zds.HepatitisB()
            elif disease_name == 'hib':
                disease = zds.Hib()
            
            # Validate parameters
            results = {}
            
            # Check beta (transmission rate)
            beta = disease.pars.beta
            if hasattr(beta, 'peryear'):
                beta_value = beta.peryear
            elif hasattr(beta, 'p'):
                beta_value = beta.p
            else:
                beta_value = float(beta)
            
            # Convert to R0 approximation (R0 ≈ beta * duration)
            duration_years = disease.pars.dur_inf.mean / 365 if hasattr(disease.pars.dur_inf, 'mean') else 0.1
            r0_approx = beta_value * duration_years
            
            r0_min, r0_max = expected['r0_range']
            r0_valid = r0_min <= r0_approx <= r0_max
            
            results['r0'] = {
                'value': r0_approx,
                'expected_range': expected['r0_range'],
                'valid': r0_valid
            }
            
            # Check case fatality rate
            cfr = disease.pars.p_death
            if hasattr(cfr, 'p'):
                cfr_value = cfr.p
            elif hasattr(cfr, 'peryear'):
                cfr_value = cfr.peryear
            elif hasattr(cfr, 'mean'):
                cfr_value = cfr.mean
            else:
                try:
                    cfr_value = float(cfr)
                except:
                    cfr_value = 0.01  # Default value
            
            cfr_min, cfr_max = expected['cfr_range']
            cfr_valid = cfr_min <= cfr_value <= cfr_max
            
            results['cfr'] = {
                'value': cfr_value,
                'expected_range': expected['cfr_range'],
                'valid': cfr_valid
            }
            
            # Print results
            print(f"  R0: {r0_approx:.2f} (expected: {r0_min}-{r0_max}) {'✓' if r0_valid else '✗'}")
            print(f"  CFR: {cfr_value:.3f} (expected: {cfr_min}-{cfr_max}) {'✓' if cfr_valid else '✗'}")
            
            validation_results[disease_name] = results
        
        return validation_results
    
    def validate_vaccination_impact(self):
        """Validate vaccination impact against expected ranges"""
        
        print("\n=== VACCINATION IMPACT VALIDATION ===")
        
        # Run baseline and vaccination simulations
        baseline_sim = self._run_baseline_simulation()
        vaccination_sim = self._run_vaccination_simulation()
        
        # Compare results
        impact_results = {}
        
        for disease_name in ['diphtheria', 'tetanus', 'pertussis', 'hepatitisb', 'hib']:
            if disease_name in baseline_sim.diseases:
                baseline_cum = baseline_sim.diseases[disease_name].results.cum_infections[-1]
                vaccination_cum = vaccination_sim.diseases[disease_name].results.cum_infections[-1]
                
                if baseline_cum > 0:
                    reduction = (baseline_cum - vaccination_cum) / baseline_cum
                    
                    # Get expected range
                    expected_key = f"{disease_name}_reduction"
                    if expected_key in self.expected_impact:
                        expected_min, expected_max = self.expected_impact[expected_key]
                        valid = expected_min <= reduction <= expected_max
                        
                        impact_results[disease_name] = {
                            'reduction': reduction,
                            'expected_range': self.expected_impact[expected_key],
                            'valid': valid
                        }
                        
                        print(f"{disease_name.title()}: {reduction:.1%} reduction "
                              f"(expected: {expected_min:.0%}-{expected_max:.0%}) "
                              f"{'✓' if valid else '✗'}")
        
        return impact_results
    
    def validate_age_susceptibility(self):
        """Validate age-specific susceptibility patterns"""
        
        print("\n=== AGE SUSCEPTIBILITY VALIDATION ===")
        
        # Create simulation with age-structured population
        sim_pars = dict(start=2020, stop=2022, dt=1/52, verbose=0)
        
        # Create population with specific age distribution
        people = ss.People(n_agents=10000)
        
        # Create diseases
        diseases = [
            zds.Diphtheria(dict(beta=ss.peryear(0.2), init_prev=ss.bernoulli(p=0.01))),
            zds.Pertussis(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.01))),
            zds.Hib(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
        ]
        
        sim = ss.Sim(
            people=people,
            diseases=diseases,
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            pars=sim_pars
        )
        
        sim.run()
        
        # Analyze age-specific patterns
        age_results = {}
        
        for disease_name in ['diphtheria', 'pertussis', 'hib']:
            if disease_name in sim.diseases:
                disease = sim.diseases[disease_name]
                
                # Get age distribution of infected
                infected_uids = disease.infected.uids
                if len(infected_uids) > 0:
                    infected_ages = sim.people.age[infected_uids]
                    
                    # Calculate age statistics
                    mean_age = np.mean(infected_ages)
                    median_age = np.median(infected_ages)
                    children_under_5 = np.sum(infected_ages < 5) / len(infected_ages)
                    
                    age_results[disease_name] = {
                        'mean_age': mean_age,
                        'median_age': median_age,
                        'children_under_5_pct': children_under_5
                    }
                    
                    print(f"{disease_name.title()}:")
                    print(f"  Mean age of infected: {mean_age:.1f} years")
                    print(f"  Children under 5: {children_under_5:.1%}")
        
        return age_results
    
    def validate_herd_immunity_thresholds(self):
        """Validate herd immunity thresholds"""
        
        print("\n=== HERD IMMUNITY THRESHOLD VALIDATION ===")
        
        # Known herd immunity thresholds
        herd_immunity_thresholds = {
            'diphtheria': 0.85,  # 85% vaccination needed
            'tetanus': 0.80,     # 80% vaccination needed
            'pertussis': 0.92,   # 92% vaccination needed (high R0)
            'hepatitisb': 0.80, # 80% vaccination needed
            'hib': 0.80          # 80% vaccination needed
        }
        
        # Test different vaccination coverage levels
        coverage_levels = [0.0, 0.5, 0.7, 0.8, 0.9, 0.95]
        results = {}
        
        for disease_name, threshold in herd_immunity_thresholds.items():
            print(f"\n{disease_name.title()} (threshold: {threshold:.0%}):")
            
            disease_results = {}
            
            for coverage in coverage_levels:
                # Run simulation with this coverage
                sim = self._run_simulation_with_coverage(disease_name, coverage)
                
                # Get final prevalence
                final_prevalence = sim.diseases[disease_name].results.prevalence[-1]
                
                disease_results[coverage] = final_prevalence
                
                # Check if below threshold (good)
                below_threshold = final_prevalence < 0.01  # Less than 1% prevalence
                
                print(f"  Coverage {coverage:.0%}: Prevalence {final_prevalence:.3f} "
                      f"{'✓' if below_threshold else '✗'}")
            
            results[disease_name] = disease_results
        
        return results
    
    def validate_vaccine_efficacy(self):
        """Validate vaccine efficacy against literature values"""
        
        print("\n=== VACCINE EFFICACY VALIDATION ===")
        
        # Known vaccine efficacy values
        efficacy_values = {
            'diphtheria': 0.95,
            'tetanus': 0.95,
            'pertussis': 0.85,  # Wanes over time
            'hepatitisb': 0.95,
            'hib': 0.95
        }
        
        # Test different efficacy levels
        test_efficacies = [0.0, 0.5, 0.7, 0.85, 0.95]
        results = {}
        
        for disease_name, expected_efficacy in efficacy_values.items():
            print(f"\n{disease_name.title()} (expected efficacy: {expected_efficacy:.0%}):")
            
            disease_results = {}
            
            for efficacy in test_efficacies:
                # Run simulation with this efficacy
                sim = self._run_simulation_with_efficacy(disease_name, efficacy)
                
                # Get final prevalence
                final_prevalence = sim.diseases[disease_name].results.prevalence[-1]
                
                disease_results[efficacy] = final_prevalence
                
                print(f"  Efficacy {efficacy:.0%}: Final prevalence {final_prevalence:.3f}")
            
            results[disease_name] = disease_results
        
        return results
    
    def _run_baseline_simulation(self):
        """Run baseline simulation without vaccination"""
        
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        
        diseases = [
            zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01))),
            zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001))),
            zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02))),
            zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005))),
            zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
        ]
        
        sim = ss.Sim(
            people=ss.People(n_agents=5000),
            diseases=diseases,
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            pars=sim_pars
        )
        
        sim.run()
        return sim
    
    def _run_vaccination_simulation(self):
        """Run simulation with vaccination"""
        
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        
        diseases = [
            zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01))),
            zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001))),
            zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02))),
            zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005))),
            zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
        ]
        
        vaccination = zds.ZeroDoseVaccination(dict(
            coverage=0.8,
            efficacy=0.9,
            age_min=0,
            age_max=60,
            routine_prob=0.2
        ))
        
        sim = ss.Sim(
            people=ss.People(n_agents=5000),
            diseases=diseases,
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            interventions=[vaccination],
            pars=sim_pars
        )
        
        sim.run()
        return sim
    
    def _run_simulation_with_coverage(self, disease_name, coverage):
        """Run simulation with specific vaccination coverage"""
        
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        
        # Create single disease
        if disease_name == 'diphtheria':
            disease = zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
        elif disease_name == 'tetanus':
            disease = zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001)))
        elif disease_name == 'pertussis':
            disease = zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02)))
        elif disease_name == 'hepatitisb':
            disease = zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005)))
        elif disease_name == 'hib':
            disease = zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
        
        vaccination = zds.ZeroDoseVaccination(dict(
            coverage=coverage,
            efficacy=0.9,
            age_min=0,
            age_max=60,
            routine_prob=0.2
        ))
        
        sim = ss.Sim(
            people=ss.People(n_agents=2000),
            diseases=[disease],
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            interventions=[vaccination],
            pars=sim_pars
        )
        
        sim.run()
        return sim
    
    def _run_simulation_with_efficacy(self, disease_name, efficacy):
        """Run simulation with specific vaccine efficacy"""
        
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        
        # Create single disease
        if disease_name == 'diphtheria':
            disease = zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
        elif disease_name == 'tetanus':
            disease = zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001)))
        elif disease_name == 'pertussis':
            disease = zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02)))
        elif disease_name == 'hepatitisb':
            disease = zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005)))
        elif disease_name == 'hib':
            disease = zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
        
        vaccination = zds.ZeroDoseVaccination(dict(
            coverage=0.8,
            efficacy=efficacy,
            age_min=0,
            age_max=60,
            routine_prob=0.2
        ))
        
        sim = ss.Sim(
            people=ss.People(n_agents=2000),
            diseases=[disease],
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            interventions=[vaccination],
            pars=sim_pars
        )
        
        sim.run()
        return sim
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        
        print("="*80)
        print("SCIENTIFIC VALIDATION REPORT")
        print("="*80)
        
        # Run all validations
        param_results = self.validate_disease_parameters()
        impact_results = self.validate_vaccination_impact()
        age_results = self.validate_age_susceptibility()
        herd_results = self.validate_herd_immunity_thresholds()
        efficacy_results = self.validate_vaccine_efficacy()
        
        # Summary
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        total_validations = 0
        passed_validations = 0
        
        # Count parameter validations
        for disease, results in param_results.items():
            for param, result in results.items():
                total_validations += 1
                if result['valid']:
                    passed_validations += 1
        
        # Count impact validations
        for disease, result in impact_results.items():
            total_validations += 1
            if result['valid']:
                passed_validations += 1
        
        success_rate = (passed_validations / total_validations) * 100 if total_validations > 0 else 0
        
        print(f"Total validations: {total_validations}")
        print(f"Passed validations: {passed_validations}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ MODEL VALIDATION: PASSED")
            print("The model parameters and behavior are consistent with scientific literature.")
        elif success_rate >= 60:
            print("\n⚠️  MODEL VALIDATION: PARTIAL")
            print("Some model parameters need adjustment to match scientific literature.")
        else:
            print("\n❌ MODEL VALIDATION: FAILED")
            print("Model parameters need significant revision to match scientific literature.")
        
        return {
            'param_results': param_results,
            'impact_results': impact_results,
            'age_results': age_results,
            'herd_results': herd_results,
            'efficacy_results': efficacy_results,
            'success_rate': success_rate
        }

def main():
    """Run scientific validation"""
    
    validator = ScientificValidator()
    results = validator.generate_validation_report()
    
    return results

if __name__ == '__main__':
    results = main()
