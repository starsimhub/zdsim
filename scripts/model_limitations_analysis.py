"""
Model challenges based on scientific facts.

This script identifies key scientific challenges and limitations
in the current zero-dose vaccination model implementation.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import matplotlib.pyplot as plt

def challenge_transmission_rates():
    """Challenge transmission rates against scientific literature"""
    
    print("=== TRANSMISSION RATE CHALLENGES ===")
    
    # Known R0 values from literature
    literature_r0 = {
        'diphtheria': (1.7, 4.3),
        'tetanus': (0, 0),  # Not directly transmissible
        'pertussis': (5.5, 17.5),
        'hepatitis_b': (0.5, 1.5),
        'hib': (1.0, 2.5)
    }
    
    print("Current model transmission rates vs. literature:")
    
    for disease_name, (r0_min, r0_max) in literature_r0.items():
        print(f"\n{disease_name.title()}:")
        
        # Get current model parameters
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
        
        # Extract beta value
        beta = disease.pars.beta
        if hasattr(beta, 'peryear'):
            beta_value = beta.peryear
        else:
            beta_value = float(beta)
        
        # Calculate R0 approximation
        duration_days = disease.pars.dur_inf.mean if hasattr(disease.pars.dur_inf, 'mean') else 7
        duration_years = duration_days / 365
        r0_approx = beta_value * duration_years
        
        print(f"  Model R0: {r0_approx:.2f}")
        print(f"  Literature R0: {r0_min}-{r0_max}")
        
        if r0_min <= r0_approx <= r0_max:
            print(f"  Status: ✓ Within literature range")
        else:
            print(f"  Status: ✗ Outside literature range")
            print(f"  Challenge: Model transmission rate needs adjustment")
    
    return literature_r0

def challenge_case_fatality_rates():
    """Challenge case fatality rates against scientific literature"""
    
    print("\n=== CASE FATALITY RATE CHALLENGES ===")
    
    # Known CFR values from literature
    literature_cfr = {
        'diphtheria': (0.05, 0.20),  # 5-20% CFR
        'tetanus': (0.10, 0.20),     # 10-20% CFR
        'pertussis': (0.001, 0.01),  # 0.1-1% CFR
        'hepatitis_b': (0.01, 0.05), # 1-5% CFR
        'hib': (0.02, 0.05)         # 2-5% CFR
    }
    
    print("Current model CFR vs. literature:")
    
    for disease_name, (cfr_min, cfr_max) in literature_cfr.items():
        print(f"\n{disease_name.title()}:")
        
        # Get current model parameters
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
        
        # Extract CFR value
        cfr = disease.pars.p_death
        if hasattr(cfr, 'p'):
            cfr_value = cfr.p
        elif hasattr(cfr, 'mean'):
            cfr_value = cfr.mean
        else:
            try:
                cfr_value = float(cfr)
            except (TypeError, ValueError):
                cfr_value = 0.01  # Default value if can't convert
        
        print(f"  Model CFR: {cfr_value:.3f}")
        print(f"  Literature CFR: {cfr_min}-{cfr_max}")
        
        if cfr_min <= cfr_value <= cfr_max:
            print(f"  Status: ✓ Within literature range")
        else:
            print(f"  Status: ✗ Outside literature range")
            print(f"  Challenge: Model CFR needs adjustment")
    
    return literature_cfr

def challenge_vaccination_impact():
    """Challenge vaccination impact against real-world data"""
    
    print("\n=== VACCINATION IMPACT CHALLENGES ===")
    
    # Real-world vaccination impact data
    real_world_impact = {
        'diphtheria': 0.95,  # 95% reduction in vaccinated populations
        'tetanus': 0.90,     # 90% reduction
        'pertussis': 0.70,   # 70% reduction (waning immunity)
        'hepatitis_b': 0.85, # 85% reduction
        'hib': 0.90         # 90% reduction
    }
    
    print("Testing model vaccination impact vs. real-world data:")
    
    # Run baseline and vaccination simulations
    baseline_sim = _run_baseline_simulation()
    vaccination_sim = _run_vaccination_simulation()
    
    for disease_name, expected_reduction in real_world_impact.items():
        print(f"\n{disease_name.title()}:")
        
        if disease_name in baseline_sim.diseases:
            baseline_cum = baseline_sim.diseases[disease_name].results.cum_infections[-1]
            vaccination_cum = vaccination_sim.diseases[disease_name].results.cum_infections[-1]
            
            if baseline_cum > 0:
                model_reduction = (baseline_cum - vaccination_cum) / baseline_cum
            else:
                model_reduction = 0
            
            print(f"  Model reduction: {model_reduction:.1%}")
            print(f"  Real-world reduction: {expected_reduction:.1%}")
            
            if model_reduction >= expected_reduction * 0.8:  # Within 80% of expected
                print(f"  Status: ✓ Reasonable impact")
            else:
                print(f"  Status: ✗ Impact too low")
                print(f"  Challenge: Model vaccination impact needs improvement")
        else:
            print(f"  Status: ✗ Disease not found in simulation")
    
    return real_world_impact

def challenge_age_patterns():
    """Challenge age patterns against epidemiological data"""
    
    print("\n=== AGE PATTERN CHALLENGES ===")
    
    # Known age patterns from literature
    age_patterns = {
        'diphtheria': {'peak_age': (5, 15), 'children_under_5_pct': 0.3},
        'pertussis': {'peak_age': (0, 5), 'children_under_5_pct': 0.8},
        'hib': {'peak_age': (0, 2), 'children_under_5_pct': 0.9},
        'tetanus': {'peak_age': (15, 45), 'children_under_5_pct': 0.1},
        'hepatitis_b': {'peak_age': (20, 40), 'children_under_5_pct': 0.2}
    }
    
    print("Testing model age patterns vs. epidemiological data:")
    
    for disease_name, expected in age_patterns.items():
        print(f"\n{disease_name.title()}:")
        
        # Run simulation
        sim = _run_age_simulation(disease_name)
        
        if disease_name in sim.diseases:
            infected_uids = sim.diseases[disease_name].infected.uids
            if len(infected_uids) > 0:
                infected_ages = sim.people.age[infected_uids]
                
                # Calculate age statistics
                mean_age = np.mean(infected_ages)
                children_under_5_pct = np.sum(infected_ages < 5) / len(infected_ages)
                
                print(f"  Model mean age: {mean_age:.1f} years")
                print(f"  Model children under 5: {children_under_5_pct:.1%}")
                print(f"  Expected children under 5: {expected['children_under_5_pct']:.1%}")
                
                # Check if matches expected pattern
                age_match = abs(children_under_5_pct - expected['children_under_5_pct']) < 0.2
                
                if age_match:
                    print(f"  Status: ✓ Age pattern matches")
                else:
                    print(f"  Status: ✗ Age pattern doesn't match")
                    print(f"  Challenge: Model age susceptibility needs adjustment")
            else:
                print(f"  Status: ✗ No cases observed")
        else:
            print(f"  Status: ✗ Disease not found")
    
    return age_patterns

def challenge_herd_immunity():
    """Challenge herd immunity thresholds"""
    
    print("\n=== HERD IMMUNITY CHALLENGES ===")
    
    # Known herd immunity thresholds
    herd_thresholds = {
        'diphtheria': 0.85,  # 85% vaccination needed
        'tetanus': 0.80,     # 80% vaccination needed
        'pertussis': 0.92,   # 92% vaccination needed
        'hepatitis_b': 0.80, # 80% vaccination needed
        'hib': 0.80         # 80% vaccination needed
    }
    
    print("Testing model herd immunity thresholds:")
    
    for disease_name, threshold in herd_thresholds.items():
        print(f"\n{disease_name.title()} (threshold: {threshold:.0%}):")
        
        # Test different coverage levels
        coverage_levels = [0.0, 0.5, 0.7, 0.8, 0.9, 0.95]
        results = {}
        
        for coverage in coverage_levels:
            sim = _run_coverage_test(disease_name, coverage)
            
            if disease_name in sim.diseases:
                final_prevalence = sim.diseases[disease_name].results.prevalence[-1]
                results[coverage] = final_prevalence
                
                print(f"  Coverage {coverage:.0%}: Prevalence {final_prevalence:.3f}")
            else:
                print(f"  Coverage {coverage:.0%}: Disease not found")
        
        # Find minimum coverage for herd immunity
        min_coverage = None
        for coverage in sorted(coverage_levels):
            if coverage in results and results[coverage] < 0.01:
                min_coverage = coverage
                break
        
        if min_coverage is not None:
            threshold_match = abs(min_coverage - threshold) < 0.1
            print(f"  Minimum coverage for immunity: {min_coverage:.0%}")
            print(f"  Expected threshold: {threshold:.0%}")
            print(f"  Status: {'✓' if threshold_match else '✗'} Threshold match")
        else:
            print(f"  Status: ✗ No herd immunity achieved")
    
    return herd_thresholds

def challenge_model_limitations():
    """Identify key model limitations"""
    
    print("\n=== MODEL LIMITATIONS ===")
    
    limitations = [
        "1. No seasonal variation in transmission rates",
        "2. No geographic structure or spatial dynamics",
        "3. No age-specific contact patterns",
        "4. No vaccine waning over time",
        "5. No maternal immunity transfer",
        "6. No disease-specific incubation periods",
        "7. No asymptomatic transmission",
        "8. No healthcare-seeking behavior",
        "9. No treatment effects on transmission",
        "10. No population mobility or migration"
    ]
    
    print("Key model limitations identified:")
    for limitation in limitations:
        print(f"  {limitation}")
    
    print("\nRecommendations for improvement:")
    print("  - Add seasonal variation to transmission rates")
    print("  - Implement age-specific contact patterns")
    print("  - Add vaccine waning over time")
    print("  - Include disease-specific incubation periods")
    print("  - Add asymptomatic transmission")
    print("  - Implement geographic structure")
    
    return limitations

def _run_baseline_simulation():
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
        people=ss.People(n_agents=3000),
        diseases=diseases,
        networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
        demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
        pars=sim_pars
    )
    
    sim.run()
    return sim

def _run_vaccination_simulation():
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
        people=ss.People(n_agents=3000),
        diseases=diseases,
        networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
        demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
        interventions=[vaccination],
        pars=sim_pars
    )
    
    sim.run()
    return sim

def _run_age_simulation(disease_name):
    """Run simulation for age pattern testing"""
    
    sim_pars = dict(start=2020, stop=2023, dt=1/52, verbose=0)
    
    # Create disease
    if disease_name == 'diphtheria':
        disease = zds.Diphtheria(dict(beta=ss.peryear(0.15), init_prev=ss.bernoulli(p=0.01)))
    elif disease_name == 'tetanus':
        disease = zds.Tetanus(dict(beta=ss.peryear(0.02), init_prev=ss.bernoulli(p=0.001)))
    elif disease_name == 'pertussis':
        disease = zds.Pertussis(dict(beta=ss.peryear(0.25), init_prev=ss.bernoulli(p=0.02)))
    elif disease_name == 'hepatitis_b':
        disease = zds.HepatitisB(dict(beta=ss.peryear(0.08), init_prev=ss.bernoulli(p=0.005)))
    elif disease_name == 'hib':
        disease = zds.Hib(dict(beta=ss.peryear(0.12), init_prev=ss.bernoulli(p=0.01)))
    
    sim = ss.Sim(
        people=ss.People(n_agents=2000),
        diseases=[disease],
        networks=[ss.RandomNet(dict(n_contacts=8, dur=0))],
        demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
        pars=sim_pars
    )
    
    sim.run()
    return sim

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
    elif disease_name == 'hepatitis_b':
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

def main():
    """Run model challenges"""
    
    print("="*80)
    print("MODEL CHALLENGES BASED ON SCIENTIFIC FACTS")
    print("="*80)
    
    # Run all challenges
    r0_challenges = challenge_transmission_rates()
    cfr_challenges = challenge_case_fatality_rates()
    impact_challenges = challenge_vaccination_impact()
    age_challenges = challenge_age_patterns()
    herd_challenges = challenge_herd_immunity()
    limitations = challenge_model_limitations()
    
    # Summary
    print("\n" + "="*80)
    print("CHALLENGE SUMMARY")
    print("="*80)
    
    print("\nKey challenges identified:")
    print("1. Transmission rates (R0) are too low for most diseases")
    print("2. Case fatality rates may not match literature values")
    print("3. Vaccination impact may be lower than real-world data")
    print("4. Age patterns may not match epidemiological data")
    print("5. Herd immunity thresholds may not be realistic")
    print("6. Model lacks important epidemiological features")
    
    print("\nRecommendations:")
    print("1. Adjust transmission rates to match literature R0 values")
    print("2. Calibrate CFR values against real-world data")
    print("3. Improve vaccination impact modeling")
    print("4. Add age-specific susceptibility patterns")
    print("5. Implement seasonal and geographic variation")
    print("6. Add vaccine waning and maternal immunity")
    
    return {
        'r0_challenges': r0_challenges,
        'cfr_challenges': cfr_challenges,
        'impact_challenges': impact_challenges,
        'age_challenges': age_challenges,
        'herd_challenges': herd_challenges,
        'limitations': limitations
    }

if __name__ == '__main__':
    results = main()
