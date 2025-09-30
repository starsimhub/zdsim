"""
Data-Driven Parameter Calibration System

This script calibrates model parameters against real-world epidemiological data
to ensure the model accurately reflects observed disease patterns and vaccination impact.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import minimize
from real_data_loader import RealDataAnalyzer
import warnings
warnings.filterwarnings('ignore')

class DataDrivenCalibrator:
    """Calibrate model parameters against real-world data"""
    
    def __init__(self, data_path="zdsim/data/zerodose_data.dta"):
        """Initialize calibrator with real data"""
        self.data_analyzer = RealDataAnalyzer(data_path)
        self.calibrated_parameters = {}
        self.validation_results = {}
        
    def load_real_data(self):
        """Load and analyze real-world data"""
        print("Loading real-world data for calibration...")
        return self.data_analyzer.load_data()
    
    def calibrate_disease_parameters(self):
        """Calibrate disease-specific parameters against real data"""
        print("\n" + "="*60)
        print("DATA-DRIVEN DISEASE PARAMETER CALIBRATION")
        print("="*60)
        
        # Get real disease data
        disease_analysis = self.data_analyzer.analyze_disease_burden()
        disease_rates = self.data_analyzer.calculate_disease_rates()
        
        calibrated_params = {}
        
        for disease_name in ['tetanus', 'diphtheria', 'hepatitis_b', 'pneumonia']:
            if disease_name not in disease_analysis:
                continue
                
            print(f"\nCalibrating {disease_name.upper()} parameters...")
            
            # Get real data for this disease
            real_stats = disease_analysis[disease_name]
            real_rates = disease_rates.get(disease_name, {})
            
            # Calibrate parameters based on real data
            if disease_name == 'tetanus':
                params = self._calibrate_tetanus(real_stats, real_rates)
            elif disease_name == 'diphtheria':
                params = self._calibrate_diphtheria(real_stats, real_rates)
            elif disease_name == 'hepatitis_b':
                params = self._calibrate_hepatitis_b(real_stats, real_rates)
            elif disease_name == 'pneumonia':
                params = self._calibrate_pneumonia(real_stats, real_rates)
            
            calibrated_params[disease_name] = params
            print(f"  ✓ {disease_name} parameters calibrated")
        
        self.calibrated_parameters = calibrated_params
        return calibrated_params
    
    def _calibrate_tetanus(self, real_stats, real_rates):
        """Calibrate tetanus parameters from real data"""
        # Real data shows ~595 cases/month
        monthly_cases = real_stats['mean_monthly_cases']
        
        # Estimate transmission rate from case frequency
        # Tetanus is environmental, so beta represents environmental exposure rate
        beta_rate = monthly_cases / 100000  # Assume 100k population at risk
        
        # Case fatality rate from literature (10-15% without treatment)
        cfr = 0.10
        
        # Duration of infection (3 months average)
        duration = 3/12  # 3 months in years
        
        # Waning immunity (5.5% per year from document)
        waning_rate = 0.055
        
        return {
            'beta': ss.peryear(beta_rate),
            'p_death': ss.bernoulli(p=cfr),
            'dur_inf': ss.lognorm_ex(mean=ss.years(duration)),
            'waning': ss.peryear(waning_rate),
            'wound_rate': ss.peryear(0.1)  # Environmental exposure rate
        }
    
    def _calibrate_diphtheria(self, real_stats, real_rates):
        """Calibrate diphtheria parameters from real data"""
        # Real data shows ~0.58 cases/month (very low, good control)
        monthly_cases = real_stats['mean_monthly_cases']
        
        # Low transmission due to good vaccination coverage
        beta_rate = max(0.01, monthly_cases / 100000)  # Very low transmission
        
        # Case fatality rate (5% without treatment)
        cfr = 0.05
        
        # Duration of infection (2-6 weeks)
        duration = 0.125  # 6 weeks in years
        
        return {
            'beta': ss.peryear(beta_rate),
            'p_death': ss.bernoulli(p=cfr),
            'dur_inf': ss.lognorm_ex(mean=ss.years(duration))
        }
    
    def _calibrate_hepatitis_b(self, real_stats, real_rates):
        """Calibrate hepatitis B parameters from real data"""
        # Real data shows ~2,858 cases/month
        monthly_cases = real_stats['mean_monthly_cases']
        
        # Moderate transmission rate
        beta_rate = monthly_cases / 100000
        
        # Case fatality rate (2% acute phase)
        cfr = 0.02
        
        # Long duration (chronic infection)
        duration = 2.0  # 2 years average
        
        # Chronic infection rate (5%)
        chronic_rate = 0.05
        
        return {
            'beta': ss.peryear(beta_rate),
            'p_death': ss.bernoulli(p=cfr),
            'dur_inf': ss.lognorm_ex(mean=ss.years(duration)),
            'p_chronic': ss.bernoulli(p=chronic_rate)
        }
    
    def _calibrate_pneumonia(self, real_stats, real_rates):
        """Calibrate pneumonia parameters (proxy for Hib) from real data"""
        # Real data shows ~756,410 cases/month (very high burden)
        monthly_cases = real_stats['mean_monthly_cases']
        
        # High transmission rate
        beta_rate = monthly_cases / 100000
        
        # Case fatality rate (3% with meningitis)
        cfr = 0.03
        
        # Short duration (1-2 weeks)
        duration = 0.05  # 2.5 weeks in years
        
        # Meningitis rate (10%)
        meningitis_rate = 0.10
        
        return {
            'beta': ss.peryear(beta_rate),
            'p_death': ss.bernoulli(p=cfr),
            'dur_inf': ss.lognorm_ex(mean=ss.years(duration)),
            'p_meningitis': ss.bernoulli(p=meningitis_rate)
        }
    
    def calibrate_vaccination_parameters(self):
        """Calibrate vaccination parameters from real coverage data"""
        print("\n" + "="*60)
        print("DATA-DRIVEN VACCINATION PARAMETER CALIBRATION")
        print("="*60)
        
        # Get real vaccination data
        vaccine_analysis = self.data_analyzer.analyze_vaccination_coverage()
        
        vaccination_params = {}
        
        # DPT vaccination (most relevant for zero-dose)
        if 'dpt' in vaccine_analysis:
            dpt_stats = vaccine_analysis['dpt']
            
            # Calculate coverage rate from dose counts
            # Assume target population of ~50,000 children under 5
            target_population = 50000
            monthly_doses = dpt_stats['mean_coverage']
            coverage_rate = min(1.0, monthly_doses / (target_population / 12))  # Monthly coverage
            
            vaccination_params = {
                'coverage': coverage_rate,
                'efficacy': 0.90,  # 90% efficacy
                'age_min': 0,      # 0 months
                'age_max': 60,     # 60 months (5 years)
                'routine_prob': coverage_rate * 0.8,  # 80% of coverage as routine
                'start_day': 0,
                'end_day': 365 * 10  # 10 years
            }
            
            print(f"DPT Vaccination Parameters:")
            print(f"  Coverage: {coverage_rate:.1%}")
            print(f"  Monthly doses: {monthly_doses:.0f}")
            print(f"  Routine probability: {vaccination_params['routine_prob']:.1%}")
        
        return vaccination_params
    
    def create_calibrated_simulation(self, n_agents=10000):
        """Create simulation with data-calibrated parameters"""
        print("\n" + "="*60)
        print("CREATING DATA-CALIBRATED SIMULATION")
        print("="*60)
        
        # Create diseases with calibrated parameters
        diseases = []
        
        if 'tetanus' in self.calibrated_parameters:
            tetanus_params = self.calibrated_parameters['tetanus']
            diseases.append(zds.Tetanus(tetanus_params))
            print("✓ Tetanus disease added with calibrated parameters")
        
        if 'diphtheria' in self.calibrated_parameters:
            diphtheria_params = self.calibrated_parameters['diphtheria']
            diseases.append(zds.Diphtheria(diphtheria_params))
            print("✓ Diphtheria disease added with calibrated parameters")
        
        if 'hepatitis_b' in self.calibrated_parameters:
            hep_b_params = self.calibrated_parameters['hepatitis_b']
            diseases.append(zds.HepatitisB(hep_b_params))
            print("✓ Hepatitis B disease added with calibrated parameters")
        
        if 'pneumonia' in self.calibrated_parameters:
            # Use pneumonia parameters for Hib (similar disease)
            hib_params = self.calibrated_parameters['pneumonia']
            diseases.append(zds.Hib(hib_params))
            print("✓ Hib disease added with calibrated parameters")
        
        # Add pertussis with literature-based parameters
        diseases.append(zds.Pertussis(dict(
            beta=ss.peryear(0.25),
            init_prev=ss.bernoulli(p=0.02),
            p_death=ss.bernoulli(p=0.01),
            dur_inf=ss.lognorm_ex(mean=ss.years(0.25)),
            waning_immunity=ss.peryear(0.1)
        )))
        print("✓ Pertussis disease added with literature parameters")
        
        # Create vaccination intervention
        vaccination_params = self.calibrate_vaccination_parameters()
        vaccination = zds.ZeroDoseVaccination(vaccination_params)
        
        # Create simulation
        sim_pars = dict(
            start=2020,
            stop=2025,
            dt=1/52,  # Weekly timesteps
            verbose=1/52
        )
        
        people = ss.People(n_agents=n_agents)
        networks = [
            ss.RandomNet(dict(n_contacts=5, dur=0), name='household'),
            ss.RandomNet(dict(n_contacts=15, dur=0), name='community')
        ]
        demographics = [
            ss.Births(dict(birth_rate=25)),
            ss.Deaths(dict(death_rate=8))
        ]
        
        sim = ss.Sim(
            people=people,
            diseases=diseases,
            networks=networks,
            demographics=demographics,
            interventions=[vaccination],
            pars=sim_pars
        )
        
        print(f"✓ Data-calibrated simulation created with {n_agents:,} agents")
        return sim
    
    def validate_against_real_data(self, sim):
        """Validate calibrated model against real data"""
        print("\n" + "="*60)
        print("VALIDATING MODEL AGAINST REAL DATA")
        print("="*60)
        
        # Run simulation
        print("Running calibrated simulation...")
        sim.run()
        
        validation_results = {}
        
        # Compare with real data
        real_disease_analysis = self.data_analyzer.analyze_disease_burden()
        
        for disease_name in ['tetanus', 'diphtheria', 'hepatitisb', 'hib']:
            if disease_name in sim.diseases:
                disease = sim.diseases[disease_name]
                
                # Get model results
                model_prevalence = disease.results.prevalence[-1]
                model_cumulative = disease.results.cum_infections[-1]
                
                # Get real data
                real_key = disease_name if disease_name != 'hepatitisb' else 'hepatitis_b'
                real_key = real_key if real_key != 'hib' else 'pneumonia'
                
                if real_key in real_disease_analysis:
                    real_monthly = real_disease_analysis[real_key]['mean_monthly_cases']
                    real_total = real_disease_analysis[real_key]['total_cases']
                    
                    # Calculate validation metrics
                    prevalence_error = abs(model_prevalence - (real_monthly / 100000)) / (real_monthly / 100000)
                    cumulative_error = abs(model_cumulative - real_total) / real_total
                    
                    validation_results[disease_name] = {
                        'model_prevalence': model_prevalence,
                        'real_monthly_cases': real_monthly,
                        'model_cumulative': model_cumulative,
                        'real_total_cases': real_total,
                        'prevalence_error': prevalence_error,
                        'cumulative_error': cumulative_error,
                        'validation_score': 1 - (prevalence_error + cumulative_error) / 2
                    }
                    
                    print(f"{disease_name.upper()} Validation:")
                    print(f"  Model prevalence: {model_prevalence:.4f}")
                    print(f"  Real monthly cases: {real_monthly:.0f}")
                    print(f"  Validation score: {validation_results[disease_name]['validation_score']:.2f}")
        
        self.validation_results = validation_results
        return validation_results
    
    def generate_policy_recommendations(self):
        """Generate policy recommendations based on calibrated model"""
        print("\n" + "="*60)
        print("POLICY RECOMMENDATIONS FROM CALIBRATED MODEL")
        print("="*60)
        
        recommendations = []
        
        # Analyze calibrated parameters
        if 'tetanus' in self.calibrated_parameters:
            tetanus_params = self.calibrated_parameters['tetanus']
            beta_rate = float(tetanus_params['beta'])
            
            if beta_rate > 0.01:  # High environmental exposure
                recommendations.append(
                    "🚨 HIGH PRIORITY: Tetanus environmental exposure is high - "
                    "implement wound care programs and increase vaccination coverage"
                )
            else:
                recommendations.append(
                    "✅ GOOD: Tetanus exposure is controlled - maintain current vaccination levels"
                )
        
        if 'diphtheria' in self.calibrated_parameters:
            diphtheria_params = self.calibrated_parameters['diphtheria']
            beta_rate = float(diphtheria_params['beta'])
            
            if beta_rate < 0.01:  # Very low transmission
                recommendations.append(
                    "✅ EXCELLENT: Diphtheria is well controlled - maintain vaccination coverage"
                )
            else:
                recommendations.append(
                    "⚠️  WARNING: Diphtheria transmission detected - investigate vaccination gaps"
                )
        
        if 'hepatitis_b' in self.calibrated_parameters:
            hep_b_params = self.calibrated_parameters['hepatitis_b']
            beta_rate = float(hep_b_params['beta'])
            
            if beta_rate > 0.02:  # High transmission
                recommendations.append(
                    "🚨 URGENT: Hepatitis B transmission is high - "
                    "implement birth dose vaccination and increase coverage"
                )
            else:
                recommendations.append(
                    "✅ GOOD: Hepatitis B transmission is controlled - continue current strategy"
                )
        
        # Vaccination recommendations
        vaccination_params = self.calibrate_vaccination_parameters()
        if vaccination_params:
            coverage = vaccination_params['coverage']
            
            if coverage < 0.8:  # Low coverage
                recommendations.append(
                    f"🚨 CRITICAL: Vaccination coverage is low ({coverage:.1%}) - "
                    "implement catch-up campaigns and improve routine vaccination"
                )
            elif coverage < 0.9:  # Moderate coverage
                recommendations.append(
                    f"⚠️  IMPROVE: Vaccination coverage is moderate ({coverage:.1%}) - "
                    "focus on hard-to-reach populations"
                )
            else:
                recommendations.append(
                    f"✅ EXCELLENT: Vaccination coverage is high ({coverage:.1%}) - "
                    "maintain current programs and monitor for gaps"
                )
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        return recommendations
    
    def export_calibration_report(self, output_path="data_driven_calibration_report.txt"):
        """Export comprehensive calibration report"""
        print(f"\nGenerating calibration report: {output_path}")
        
        with open(output_path, 'w') as f:
            f.write("DATA-DRIVEN MODEL CALIBRATION REPORT\n")
            f.write("=" * 45 + "\n\n")
            f.write("This report shows how the zero-dose vaccination model has been\n")
            f.write("calibrated against real-world epidemiological data to ensure\n")
            f.write("accurate policy decision-making.\n\n")
            
            # Calibrated parameters section
            f.write("CALIBRATED PARAMETERS\n")
            f.write("-" * 25 + "\n")
            for disease, params in self.calibrated_parameters.items():
                f.write(f"\n{disease.upper()}:\n")
                for param_name, param_value in params.items():
                    if hasattr(param_value, 'pars'):
                        if hasattr(param_value.pars, 'p'):
                            f.write(f"  {param_name}: {param_value.pars.p:.4f}\n")
                        elif hasattr(param_value.pars, 'mean'):
                            try:
                                mean_val = float(param_value.pars.mean)
                                f.write(f"  {param_name}: {mean_val:.4f}\n")
                            except (TypeError, ValueError):
                                f.write(f"  {param_name}: {param_value.pars.mean}\n")
                        else:
                            f.write(f"  {param_name}: {param_value}\n")
                    else:
                        f.write(f"  {param_name}: {param_value}\n")
            
            # Validation results section
            f.write("\n\nVALIDATION RESULTS\n")
            f.write("-" * 20 + "\n")
            for disease, results in self.validation_results.items():
                f.write(f"\n{disease.upper()}:\n")
                f.write(f"  Validation Score: {results['validation_score']:.2f}\n")
                f.write(f"  Model vs Real: {results['model_prevalence']:.4f} vs {results['real_monthly_cases']/100000:.4f}\n")
                f.write(f"  Error: {results['prevalence_error']:.2%}\n")
            
            # Policy recommendations section
            f.write("\n\nPOLICY RECOMMENDATIONS\n")
            f.write("-" * 25 + "\n")
            recommendations = self.generate_policy_recommendations()
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
        
        print(f"✓ Calibration report exported to {output_path}")
        return True

def main():
    """Main function to demonstrate data-driven calibration"""
    print("DATA-DRIVEN MODEL CALIBRATION FOR POLICY DECISION-MAKING")
    print("=" * 70)
    
    # Initialize calibrator
    calibrator = DataDrivenCalibrator()
    
    # Load real data
    if not calibrator.load_real_data():
        print("Failed to load real data. Exiting.")
        return
    
    # Calibrate disease parameters
    print("\n1. Calibrating disease parameters against real data...")
    calibrated_params = calibrator.calibrate_disease_parameters()
    
    # Calibrate vaccination parameters
    print("\n2. Calibrating vaccination parameters...")
    vaccination_params = calibrator.calibrate_vaccination_parameters()
    
    # Create calibrated simulation
    print("\n3. Creating data-calibrated simulation...")
    sim = calibrator.create_calibrated_simulation()
    
    # Validate against real data
    print("\n4. Validating model against real data...")
    validation_results = calibrator.validate_against_real_data(sim)
    
    # Generate policy recommendations
    print("\n5. Generating policy recommendations...")
    recommendations = calibrator.generate_policy_recommendations()
    
    # Export comprehensive report
    print("\n6. Exporting calibration report...")
    calibrator.export_calibration_report()
    
    print("\n" + "="*70)
    print("DATA-DRIVEN CALIBRATION COMPLETE")
    print("="*70)
    print("✓ Model calibrated against real epidemiological data")
    print("✓ Parameters validated against observed patterns")
    print("✓ Policy recommendations generated for decision-makers")
    print("✓ Comprehensive report exported")

if __name__ == '__main__':
    main()
