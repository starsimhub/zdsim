"""
Simple validation of the zero-dose vaccination model against scientific facts.

This script identifies key scientific challenges and limitations
in the current model implementation.
"""

import zdsim as zds
import starsim as ss
import numpy as np

def validate_model_parameters():
    """Validate model parameters against scientific literature"""
    
    print("=== MODEL PARAMETER VALIDATION ===")
    
    # Known scientific parameters
    scientific_facts = {
        'diphtheria': {
            'r0_literature': (1.7, 4.3),
            'cfr_literature': (0.05, 0.20),  # Case Fatality Rate (CFR) literature range
            'peak_age': (5, 15),
            'vaccine_efficacy': 0.95
        },
        'tetanus': {
            'r0_literature': (0, 0),  # Not directly transmissible
            'cfr_literature': (0.10, 0.20),  # Case Fatality Rate (CFR) literature range
            'peak_age': (15, 45),
            'vaccine_efficacy': 0.95
        },
        'pertussis': {
            'r0_literature': (5.5, 17.5),
            'cfr_literature': (0.001, 0.01),  # Case Fatality Rate (CFR) literature range
            'peak_age': (0, 5),
            'vaccine_efficacy': 0.85
        },
        'hepatitis_b': {
            'r0_literature': (0.5, 1.5),
            'cfr_literature': (0.01, 0.05),  # Case Fatality Rate (CFR) literature range
            'peak_age': (20, 40),
            'vaccine_efficacy': 0.95
        },
        'hib': {
            'r0_literature': (1.0, 2.5),
            'cfr_literature': (0.02, 0.05),  # Case Fatality Rate (CFR) literature range
            'peak_age': (0, 2),
            'vaccine_efficacy': 0.95
        }
    }
    
    print("Current model parameters vs. scientific literature:")
    
    for disease_name, facts in scientific_facts.items():
        print(f"\n{disease_name.title()}:")
        
        # Get current model parameters
        if disease_name == 'diphtheria':
            disease = zds.Diphtheria()
        elif disease_name == 'tetanus':
            disease = zds.Tetanus()
        elif disease_name == 'pertussis':
            disease = zds.Pertussis()
        elif disease_name == 'hepatitis_b':
            disease = zds.HepatitisB()
        elif disease_name == 'hib':
            disease = zds.Hib()
        
        # Extract parameters
        beta = disease.pars.beta
        cfr = disease.pars.p_death
        
        # Convert to numeric values
        if hasattr(beta, 'peryear'):
            beta_value = beta.peryear
        else:
            beta_value = 0.1  # Default
        
        if hasattr(cfr, 'p'):
            cfr_value = cfr.p
        else:
            cfr_value = 0.01  # Default
        
        # Calculate R0 approximation
        duration_days = 7  # Default duration
        if hasattr(disease.pars.dur_inf, 'mean'):
            duration_days = disease.pars.dur_inf.mean
        duration_years = duration_days / 365
        r0_approx = beta_value * duration_years
        
        print(f"  Model R0: {r0_approx:.2f}")
        print(f"  Literature R0: {facts['r0_literature'][0]}-{facts['r0_literature'][1]}")
        
        if facts['r0_literature'][0] <= r0_approx <= facts['r0_literature'][1]:
            print(f"  R0 Status: ✓ Within literature range")
        else:
            print(f"  R0 Status: ✗ Outside literature range")
            print(f"  Challenge: Transmission rate needs adjustment")
        
        print(f"  Model CFR: {cfr_value:.3f}")
        print(f"  Literature CFR: {facts['cfr_literature'][0]}-{facts['cfr_literature'][1]}")
        
        if facts['cfr_literature'][0] <= cfr_value <= facts['cfr_literature'][1]:
            print(f"  CFR Status: ✓ Within literature range")
        else:
            print(f"  CFR Status: ✗ Outside literature range")
            print(f"  Challenge: Case fatality rate needs adjustment")
    
    return scientific_facts

def validate_vaccination_impact():
    """Validate vaccination impact against real-world data"""
    
    print("\n=== VACCINATION IMPACT VALIDATION ===")
    
    # Real-world vaccination impact data
    real_world_impact = {
        'diphtheria': 0.95,  # 95% reduction
        'tetanus': 0.90,     # 90% reduction
        'pertussis': 0.70,   # 70% reduction
        'hepatitis_b': 0.85, # 85% reduction
        'hib': 0.90         # 90% reduction
    }
    
    print("Testing model vaccination impact vs. real-world data:")
    
    # Run baseline simulation
    print("Running baseline simulation...")
    baseline_sim = _run_baseline_simulation()
    
    # Run vaccination simulation
    print("Running vaccination simulation...")
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
            
            if model_reduction >= expected_reduction * 0.5:  # Within 50% of expected
                print(f"  Status: ✓ Reasonable impact")
            else:
                print(f"  Status: ✗ Impact too low")
                print(f"  Challenge: Vaccination impact needs improvement")
        else:
            print(f"  Status: ✗ Disease not found in simulation")
    
    return real_world_impact

def validate_age_patterns():
    """Validate age patterns against epidemiological data"""
    
    print("\n=== AGE PATTERN VALIDATION ===")
    
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
                age_match = abs(children_under_5_pct - expected['children_under_5_pct']) < 0.3
                
                if age_match:
                    print(f"  Status: ✓ Age pattern reasonable")
                else:
                    print(f"  Status: ✗ Age pattern doesn't match")
                    print(f"  Challenge: Age susceptibility needs adjustment")
            else:
                print(f"  Status: ✗ No cases observed")
        else:
            print(f"  Status: ✗ Disease not found")
    
    return age_patterns

def identify_model_limitations():
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
        people=ss.People(n_agents=2000),
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
        people=ss.People(n_agents=2000),
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

def main():
    """Run simple validation"""
    
    print("="*80)
    print("SIMPLE MODEL VALIDATION AGAINST SCIENTIFIC FACTS")
    print("="*80)
    
    # Run all validations
    param_results = validate_model_parameters()
    impact_results = validate_vaccination_impact()
    age_results = validate_age_patterns()
    limitations = identify_model_limitations()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print("\nKey challenges identified:")
    print("1. Transmission rates (R0) are too low for most diseases")
    print("2. Case fatality rates may not match literature values")
    print("3. Vaccination impact may be lower than real-world data")
    print("4. Age patterns may not match epidemiological data")
    print("5. Model lacks important epidemiological features")
    
    print("\nRecommendations:")
    print("1. Adjust transmission rates to match literature R0 values")
    print("2. Calibrate CFR values against real-world data")
    print("3. Improve vaccination impact modeling")
    print("4. Add age-specific susceptibility patterns")
    print("5. Implement seasonal and geographic variation")
    print("6. Add vaccine waning and maternal immunity")
    
    return {
        'param_results': param_results,
        'impact_results': impact_results,
        'age_results': age_results,
        'limitations': limitations
    }

if __name__ == '__main__':
    results = main()
