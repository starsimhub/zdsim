"""
Epidemiological validation against real-world data.

This script validates the model against known epidemiological patterns,
outbreak dynamics, and disease-specific characteristics.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def validate_epidemic_curves():
    """Validate that disease transmission follows expected epidemic curves"""
    
    print("=== EPIDEMIC CURVE VALIDATION ===")
    
    # Test each disease for realistic epidemic patterns
    diseases_to_test = [
        ('diphtheria', zds.Diphtheria(dict(beta=ss.peryear(0.2), init_prev=ss.bernoulli(p=0.01)))),
        ('pertussis', zds.Pertussis(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.02)))),
        ('hib', zds.Hib(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01))))
    ]
    
    results = {}
    
    for disease_name, disease in diseases_to_test:
        print(f"\n{disease_name.title()}:")
        
        # Run simulation
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        sim = ss.Sim(
            people=ss.People(n_agents=5000),
            diseases=[disease],
            networks=[ss.RandomNet(dict(n_contacts=10, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            pars=sim_pars
        )
        sim.run()
        
        # Analyze epidemic curve
        prevalence = sim.diseases[disease_name].results.prevalence
        timevec = sim.diseases[disease_name].results.timevec
        
        # Check for realistic epidemic pattern
        max_prev = np.max(prevalence)
        peak_time = timevec[np.argmax(prevalence)]
        final_prev = prevalence[-1]
        
        # Validate epidemic characteristics
        has_peak = max_prev > 0.01  # At least 1% peak prevalence
        reasonable_peak = max_prev < 0.5  # Not more than 50% peak prevalence
        epidemic_ends = final_prev < max_prev * 0.1  # Ends at <10% of peak
        
        print(f"  Peak prevalence: {max_prev:.3f} {'✓' if has_peak else '✗'}")
        print(f"  Peak time: {peak_time:.1f} years {'✓' if peak_time > 0 else '✗'}")
        print(f"  Final prevalence: {final_prev:.3f} {'✓' if epidemic_ends else '✗'}")
        print(f"  Realistic peak: {'✓' if reasonable_peak else '✗'}")
        
        results[disease_name] = {
            'max_prevalence': max_prev,
            'peak_time': peak_time,
            'final_prevalence': final_prev,
            'has_realistic_curve': has_peak and reasonable_peak and epidemic_ends
        }
    
    return results

def validate_age_distribution():
    """Validate age distribution of cases matches epidemiological patterns"""
    
    print("\n=== AGE DISTRIBUTION VALIDATION ===")
    
    # Known age patterns from literature
    expected_patterns = {
        'diphtheria': {'peak_age': (5, 15), 'children_under_5_pct': 0.3},
        'pertussis': {'peak_age': (0, 5), 'children_under_5_pct': 0.8},
        'hib': {'peak_age': (0, 2), 'children_under_5_pct': 0.9},
        'tetanus': {'peak_age': (15, 45), 'children_under_5_pct': 0.1},  # Adults more at risk
        'hepatitisb': {'peak_age': (20, 40), 'children_under_5_pct': 0.2}
    }
    
    results = {}
    
    for disease_name, expected in expected_patterns.items():
        print(f"\n{disease_name.title()}:")
        
        # Create disease
        if disease_name == 'diphtheria':
            disease = zds.Diphtheria(dict(beta=ss.peryear(0.2), init_prev=ss.bernoulli(p=0.01)))
        elif disease_name == 'pertussis':
            disease = zds.Pertussis(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.02)))
        elif disease_name == 'hib':
            disease = zds.Hib(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
        elif disease_name == 'tetanus':
            disease = zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001)))
        elif disease_name == 'hepatitisb':
            disease = zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005)))
        
        # Run simulation
        sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
        sim = ss.Sim(
            people=ss.People(n_agents=5000),
            diseases=[disease],
            networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
            demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
            pars=sim_pars
        )
        sim.run()
        
        # Analyze age distribution of cases
        infected_uids = sim.diseases[disease_name].infected.uids
        if len(infected_uids) > 0:
            infected_ages = sim.people.age[infected_uids]
            
            # Calculate age statistics
            mean_age = np.mean(infected_ages)
            median_age = np.median(infected_ages)
            children_under_5_pct = np.sum(infected_ages < 5) / len(infected_ages)
            
            # Validate against expected patterns
            expected_children_pct = expected['children_under_5_pct']
            children_match = abs(children_under_5_pct - expected_children_pct) < 0.2
            
            print(f"  Mean age: {mean_age:.1f} years")
            print(f"  Median age: {median_age:.1f} years")
            print(f"  Children under 5: {children_under_5_pct:.1%} "
                  f"(expected: {expected_children_pct:.1%}) {'✓' if children_match else '✗'}")
            
            results[disease_name] = {
                'mean_age': mean_age,
                'median_age': median_age,
                'children_under_5_pct': children_under_5_pct,
                'matches_expected': children_match
            }
        else:
            print(f"  No cases observed")
            results[disease_name] = {'matches_expected': False}
    
    return results

def validate_seasonal_patterns():
    """Validate seasonal patterns if implemented"""
    
    print("\n=== SEASONAL PATTERN VALIDATION ===")
    
    # Note: Current model doesn't implement seasonality, but we can check for it
    print("Note: Current model does not implement seasonal patterns.")
    print("This is a limitation - many diseases show seasonal variation.")
    print("Recommendation: Add seasonal variation to transmission rates.")
    
    return {'seasonal_implemented': False}

def validate_herd_immunity():
    """Validate herd immunity thresholds"""
    
    print("\n=== HERD IMMUNITY VALIDATION ===")
    
    # Known herd immunity thresholds
    thresholds = {
        'diphtheria': 0.85,
        'tetanus': 0.80,
        'pertussis': 0.92,
        'hepatitisb': 0.80,
        'hib': 0.80
    }
    
    results = {}
    
    for disease_name, threshold in thresholds.items():
        print(f"\n{disease_name.title()} (threshold: {threshold:.0%}):")
        
        # Test different vaccination coverage levels
        coverage_levels = [0.0, 0.5, 0.7, 0.8, 0.9, 0.95]
        coverage_results = {}
        
        for coverage in coverage_levels:
            # Run simulation with this coverage
            sim = _run_coverage_test(disease_name, coverage)
            
            # Get final prevalence
            final_prevalence = sim.diseases[disease_name].results.prevalence[-1]
            coverage_results[coverage] = final_prevalence
            
            # Check if below threshold
            below_threshold = final_prevalence < 0.01
            print(f"  Coverage {coverage:.0%}: Prevalence {final_prevalence:.3f} "
                  f"{'✓' if below_threshold else '✗'}")
        
        # Find minimum coverage for herd immunity
        min_coverage = None
        for coverage in sorted(coverage_levels):
            if coverage_results[coverage] < 0.01:
                min_coverage = coverage
                break
        
        threshold_match = min_coverage is not None and abs(min_coverage - threshold) < 0.1
        
        results[disease_name] = {
            'coverage_results': coverage_results,
            'min_coverage_for_immunity': min_coverage,
            'expected_threshold': threshold,
            'matches_expected': threshold_match
        }
    
    return results

def validate_vaccine_waning():
    """Validate vaccine waning patterns"""
    
    print("\n=== VACCINE WANING VALIDATION ===")
    
    # Known waning patterns
    waning_patterns = {
        'diphtheria': {'waning_rate': 0.05, 'duration_years': 10},
        'tetanus': {'waning_rate': 0.02, 'duration_years': 10},
        'pertussis': {'waning_rate': 0.10, 'duration_years': 5},  # Faster waning
        'hepatitisb': {'waning_rate': 0.01, 'duration_years': 20},  # Long-lasting
        'hib': {'waning_rate': 0.03, 'duration_years': 5}
    }
    
    results = {}
    
    for disease_name, expected in waning_patterns.items():
        print(f"\n{disease_name.title()}:")
        
        # Test immunity waning over time
        sim = _run_waning_test(disease_name)
        
        # Analyze immunity levels over time
        if hasattr(sim.diseases[disease_name], 'immunity'):
            immunity_levels = sim.diseases[disease_name].immunity
            mean_immunity = np.mean(immunity_levels)
            
            print(f"  Mean immunity level: {mean_immunity:.3f}")
            print(f"  Expected waning rate: {expected['waning_rate']:.1%} per year")
            print(f"  Expected duration: {expected['duration_years']} years")
            
            results[disease_name] = {
                'mean_immunity': mean_immunity,
                'expected_waning_rate': expected['waning_rate'],
                'expected_duration': expected['duration_years']
            }
        else:
            print(f"  No immunity tracking implemented")
            results[disease_name] = {'immunity_tracked': False}
    
    return results

def validate_outbreak_dynamics():
    """Validate outbreak dynamics and superspreading events"""
    
    print("\n=== OUTBREAK DYNAMICS VALIDATION ===")
    
    # Test for realistic outbreak patterns
    results = {}
    
    # Run multiple simulations to check for variability
    n_simulations = 10
    outbreak_sizes = []
    
    for i in range(n_simulations):
        sim = _run_outbreak_simulation()
        
        # Get total cases
        total_cases = 0
        for disease_name in ['diphtheria', 'pertussis', 'hib']:
            if disease_name in sim.diseases:
                total_cases += sim.diseases[disease_name].results.cum_infections[-1]
        
        outbreak_sizes.append(total_cases)
    
    # Analyze outbreak variability
    mean_outbreak = np.mean(outbreak_sizes)
    std_outbreak = np.std(outbreak_sizes)
    cv = std_outbreak / mean_outbreak if mean_outbreak > 0 else 0
    
    print(f"Mean outbreak size: {mean_outbreak:.0f} cases")
    print(f"Standard deviation: {std_outbreak:.0f} cases")
    print(f"Coefficient of variation: {cv:.3f}")
    
    # Check for realistic variability (CV should be 0.2-0.8)
    realistic_variability = 0.2 <= cv <= 0.8
    
    print(f"Realistic variability: {'✓' if realistic_variability else '✗'}")
    
    results = {
        'mean_outbreak_size': mean_outbreak,
        'std_outbreak_size': std_outbreak,
        'coefficient_of_variation': cv,
        'realistic_variability': realistic_variability
    }
    
    return results

def _run_coverage_test(disease_name, coverage):
    """Run simulation with specific vaccination coverage"""
    
    sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
    
    # Create disease
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

def _run_waning_test(disease_name):
    """Run simulation to test immunity waning"""
    
    sim_pars = dict(start=2020, stop=2025, dt=1/52, verbose=0)
    
    # Create disease
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

def _run_outbreak_simulation():
    """Run simulation to test outbreak dynamics"""
    
    sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
    
    diseases = [
        zds.Diphtheria(dict(beta=ss.peryear(0.2), init_prev=ss.bernoulli(p=0.01))),
        zds.Pertussis(dict(beta=ss.peryear(0.3), init_prev=ss.bernoulli(p=0.02))),
        zds.Hib(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
    ]
    
    sim = ss.Sim(
        people=ss.People(n_agents=3000),
        diseases=diseases,
        networks=[ss.RandomNet(dict(n_contacts=10, dur=0))],
        demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
        pars=sim_pars
    )
    
    sim.run()
    return sim

def main():
    """Run epidemiological validation"""
    
    print("="*80)
    print("EPIDEMIOLOGICAL VALIDATION")
    print("="*80)
    
    # Run all validations
    epidemic_results = validate_epidemic_curves()
    age_results = validate_age_distribution()
    seasonal_results = validate_seasonal_patterns()
    herd_results = validate_herd_immunity()
    waning_results = validate_vaccine_waning()
    outbreak_results = validate_outbreak_dynamics()
    
    # Summary
    print("\n" + "="*80)
    print("EPIDEMIOLOGICAL VALIDATION SUMMARY")
    print("="*80)
    
    total_checks = 0
    passed_checks = 0
    
    # Count epidemic curve validations
    for disease, result in epidemic_results.items():
        total_checks += 1
        if result['has_realistic_curve']:
            passed_checks += 1
    
    # Count age distribution validations
    for disease, result in age_results.items():
        total_checks += 1
        if result.get('matches_expected', False):
            passed_checks += 1
    
    # Count herd immunity validations
    for disease, result in herd_results.items():
        total_checks += 1
        if result.get('matches_expected', False):
            passed_checks += 1
    
    # Count outbreak dynamics
    total_checks += 1
    if outbreak_results.get('realistic_variability', False):
        passed_checks += 1
    
    success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"Total checks: {total_checks}")
    print(f"Passed checks: {passed_checks}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n✅ EPIDEMIOLOGICAL VALIDATION: PASSED")
        print("Model behavior matches epidemiological patterns.")
    elif success_rate >= 60:
        print("\n⚠️  EPIDEMIOLOGICAL VALIDATION: PARTIAL")
        print("Some epidemiological patterns need adjustment.")
    else:
        print("\n❌ EPIDEMIOLOGICAL VALIDATION: FAILED")
        print("Model needs significant revision for epidemiological accuracy.")
    
    return {
        'epidemic_results': epidemic_results,
        'age_results': age_results,
        'seasonal_results': seasonal_results,
        'herd_results': herd_results,
        'waning_results': waning_results,
        'outbreak_results': outbreak_results,
        'success_rate': success_rate
    }

if __name__ == '__main__':
    results = main()
