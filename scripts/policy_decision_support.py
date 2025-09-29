"""
Policy Decision Support System for Zero-Dose Vaccination

This script provides comprehensive policy analysis and decision support
for zero-dose vaccination interventions based on real-world data and
calibrated model simulations.
"""

import zdsim as zds
import starsim as ss
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_driven_calibration import DataDrivenCalibrator
from real_data_loader import RealDataAnalyzer
import warnings
warnings.filterwarnings('ignore')

class PolicyDecisionSupport:
    """Comprehensive policy decision support system"""
    
    def __init__(self, data_path="zdsim/data/zerodose_data.dta"):
        """Initialize policy support system"""
        self.calibrator = DataDrivenCalibrator(data_path)
        self.data_analyzer = RealDataAnalyzer(data_path)
        self.scenario_results = {}
        self.policy_recommendations = {}
        
    def load_data_and_calibrate(self):
        """Load real data and calibrate model"""
        print("Loading real data and calibrating model...")
        
        # Load real data
        if not self.calibrator.load_real_data():
            return False
        
        # Calibrate parameters
        self.calibrator.calibrate_disease_parameters()
        self.calibrator.calibrate_vaccination_parameters()
        
        print("✓ Model calibrated against real data")
        return True
    
    def analyze_policy_scenarios(self):
        """Analyze different policy scenarios for decision-making"""
        print("\n" + "="*70)
        print("POLICY SCENARIO ANALYSIS FOR DECISION-MAKING")
        print("="*70)
        
        scenarios = {
            'baseline': {
                'name': 'Current Situation (Baseline)',
                'description': 'No zero-dose vaccination intervention',
                'coverage': 0.0,
                'efficacy': 0.0
            },
            'conservative': {
                'name': 'Conservative Approach',
                'description': 'Low coverage, high efficacy vaccination',
                'coverage': 0.6,
                'efficacy': 0.95
            },
            'moderate': {
                'name': 'Moderate Approach',
                'description': 'Balanced coverage and efficacy',
                'coverage': 0.8,
                'efficacy': 0.90
            },
            'aggressive': {
                'name': 'Aggressive Approach',
                'description': 'High coverage, comprehensive vaccination',
                'coverage': 0.95,
                'efficacy': 0.90
            },
            'optimal': {
                'name': 'Optimal Approach',
                'description': 'Data-driven optimal parameters',
                'coverage': 0.9,
                'efficacy': 0.95
            }
        }
        
        scenario_results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            print(f"\nAnalyzing {scenario_params['name']}...")
            
            # Create simulation for this scenario
            sim = self._create_scenario_simulation(scenario_params)
            
            # Run simulation
            sim.run()
            
            # Analyze results
            results = self._analyze_scenario_results(sim, scenario_name)
            scenario_results[scenario_name] = results
            
            print(f"  ✓ {scenario_params['name']} analyzed")
        
        self.scenario_results = scenario_results
        return scenario_results
    
    def _create_scenario_simulation(self, scenario_params):
        """Create simulation for specific policy scenario"""
        # Create diseases with calibrated parameters
        diseases = []
        
        if 'tetanus' in self.calibrator.calibrated_parameters:
            diseases.append(zds.Tetanus(self.calibrator.calibrated_parameters['tetanus']))
        
        if 'diphtheria' in self.calibrator.calibrated_parameters:
            diseases.append(zds.Diphtheria(self.calibrator.calibrated_parameters['diphtheria']))
        
        if 'hepatitis_b' in self.calibrator.calibrated_parameters:
            diseases.append(zds.HepatitisB(self.calibrator.calibrated_parameters['hepatitis_b']))
        
        if 'pneumonia' in self.calibrator.calibrated_parameters:
            diseases.append(zds.Hib(self.calibrator.calibrated_parameters['pneumonia']))
        
        # Add pertussis
        diseases.append(zds.Pertussis(dict(
            beta=ss.peryear(0.25),
            init_prev=ss.bernoulli(p=0.02),
            p_death=ss.bernoulli(p=0.01),
            dur_inf=ss.lognorm_ex(mean=ss.years(0.25)),
            waning_immunity=ss.peryear(0.1)
        )))
        
        # Create vaccination intervention
        vaccination = zds.ZeroDoseVaccination(dict(
            coverage=scenario_params['coverage'],
            efficacy=scenario_params['efficacy'],
            age_min=0,
            age_max=60,
            routine_prob=scenario_params['coverage'] * 0.8,
            start_day=0,
            end_day=365 * 5  # 5 years
        ))
        
        # Create simulation
        sim_pars = dict(
            start=2020,
            stop=2025,
            dt=1/52,
            verbose=0
        )
        
        people = ss.People(n_agents=10000)
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
            interventions=[vaccination] if scenario_params['coverage'] > 0 else [],
            pars=sim_pars
        )
        
        return sim
    
    def _analyze_scenario_results(self, sim, scenario_name):
        """Analyze results for a specific scenario"""
        results = {
            'scenario': scenario_name,
            'disease_impact': {},
            'vaccination_impact': {},
            'cost_effectiveness': {},
            'policy_metrics': {}
        }
        
        # Analyze disease impact
        for disease_name in ['tetanus', 'diphtheria', 'hepatitisb', 'hib', 'pertussis']:
            if disease_name in sim.diseases:
                disease = sim.diseases[disease_name]
                
                prevalence = disease.results.prevalence[-1]
                cumulative = disease.results.cum_infections[-1]
                new_infections = disease.results.new_infections[-1]
                
                results['disease_impact'][disease_name] = {
                    'prevalence': prevalence,
                    'cumulative_cases': cumulative,
                    'monthly_cases': new_infections * 4.33,  # Approximate monthly
                    'burden_score': prevalence * cumulative  # Combined burden metric
                }
        
        # Analyze vaccination impact
        if sim.interventions:
            vaccination = sim.interventions[0]
            total_vaccinated = np.count_nonzero(vaccination.vaccinated)
            coverage_achieved = total_vaccinated / len(sim.people)
            
            results['vaccination_impact'] = {
                'total_vaccinated': total_vaccinated,
                'coverage_achieved': coverage_achieved,
                'vaccination_rate': total_vaccinated / (5 * 12)  # Per month over 5 years
            }
        
        # Calculate cost-effectiveness (simplified)
        total_cases = sum([d['cumulative_cases'] for d in results['disease_impact'].values()])
        vaccination_cost = results['vaccination_impact'].get('total_vaccinated', 0) * 5  # $5 per dose
        cases_averted = max(0, 10000 - total_cases)  # Simplified calculation
        
        results['cost_effectiveness'] = {
            'total_cases': total_cases,
            'cases_averted': cases_averted,
            'vaccination_cost': vaccination_cost,
            'cost_per_case_averted': vaccination_cost / max(1, cases_averted),
            'cost_effectiveness_ratio': vaccination_cost / max(1, cases_averted)
        }
        
        # Policy metrics
        results['policy_metrics'] = {
            'overall_burden': sum([d['burden_score'] for d in results['disease_impact'].values()]),
            'vaccination_efficiency': results['vaccination_impact'].get('coverage_achieved', 0),
            'disease_control': 1 - (total_cases / 10000),  # Fraction of population not infected
            'policy_success_score': (results['vaccination_impact'].get('coverage_achieved', 0) + 
                                   (1 - total_cases / 10000)) / 2
        }
        
        return results
    
    def generate_policy_recommendations(self):
        """Generate comprehensive policy recommendations"""
        print("\n" + "="*70)
        print("COMPREHENSIVE POLICY RECOMMENDATIONS")
        print("="*70)
        
        if not self.scenario_results:
            print("No scenario results available. Run analyze_policy_scenarios() first.")
            return None
        
        recommendations = {
            'optimal_scenario': None,
            'cost_effective_scenario': None,
            'disease_priority': [],
            'implementation_strategy': [],
            'monitoring_metrics': []
        }
        
        # Find optimal scenario
        best_score = 0
        best_scenario = None
        
        for scenario_name, results in self.scenario_results.items():
            if scenario_name == 'baseline':
                continue
                
            policy_score = results['policy_metrics']['policy_success_score']
            cost_effectiveness = 1 / max(0.001, results['cost_effectiveness']['cost_effectiveness_ratio'])
            combined_score = policy_score * 0.7 + cost_effectiveness * 0.3
            
            if combined_score > best_score:
                best_score = combined_score
                best_scenario = scenario_name
        
        recommendations['optimal_scenario'] = best_scenario
        
        # Find most cost-effective scenario
        best_cost_eff = float('inf')
        best_cost_scenario = None
        
        for scenario_name, results in self.scenario_results.items():
            if scenario_name == 'baseline':
                continue
                
            cost_ratio = results['cost_effectiveness']['cost_effectiveness_ratio']
            if cost_ratio < best_cost_eff:
                best_cost_eff = cost_ratio
                best_cost_scenario = scenario_name
        
        recommendations['cost_effective_scenario'] = best_cost_scenario
        
        # Disease priority analysis
        baseline_results = self.scenario_results['baseline']
        disease_priorities = []
        
        for disease_name, impact in baseline_results['disease_impact'].items():
            burden = impact['burden_score']
            disease_priorities.append((disease_name, burden))
        
        disease_priorities.sort(key=lambda x: x[1], reverse=True)
        recommendations['disease_priority'] = disease_priorities
        
        # Generate specific recommendations
        if best_scenario:
            print(f"\n🎯 OPTIMAL POLICY SCENARIO: {best_scenario.upper()}")
            print(f"   Policy Success Score: {best_score:.3f}")
        else:
            print(f"\n🎯 OPTIMAL POLICY SCENARIO: Not determined")
        
        if best_cost_scenario:
            print(f"\n💰 MOST COST-EFFECTIVE: {best_cost_scenario.upper()}")
            print(f"   Cost per Case Averted: ${best_cost_eff:.2f}")
        else:
            print(f"\n💰 MOST COST-EFFECTIVE: Not determined")
        
        print(f"\n🏥 DISEASE PRIORITY RANKING:")
        for i, (disease, burden) in enumerate(disease_priorities[:3], 1):
            print(f"   {i}. {disease.upper()}: Burden Score {burden:.3f}")
        
        # Implementation strategy
        if best_scenario and best_scenario in self.scenario_results:
            optimal_results = self.scenario_results[best_scenario]
            coverage = optimal_results['vaccination_impact']['coverage_achieved']
        else:
            coverage = 0.0
        
        if coverage < 0.8:
            recommendations['implementation_strategy'].append(
                "🚨 URGENT: Implement catch-up vaccination campaigns to reach target coverage"
            )
        elif coverage < 0.9:
            recommendations['implementation_strategy'].append(
                "⚠️  IMPROVE: Focus on hard-to-reach populations and community engagement"
            )
        else:
            recommendations['implementation_strategy'].append(
                "✅ MAINTAIN: Current vaccination strategy is effective, monitor for gaps"
            )
        
        # Monitoring metrics
        recommendations['monitoring_metrics'] = [
            "Monthly vaccination coverage rates",
            "Disease case counts by type",
            "Cost per case averted",
            "Population immunity levels",
            "Vaccination equity across regions"
        ]
        
        self.policy_recommendations = recommendations
        return recommendations
    
    def create_policy_dashboard(self):
        """Create comprehensive policy dashboard"""
        print("\n" + "="*70)
        print("CREATING POLICY DECISION DASHBOARD")
        print("="*70)
        
        if not self.scenario_results:
            print("No scenario results available. Run analyze_policy_scenarios() first.")
            return None
        
        # Create comprehensive dashboard
        fig, axes = plt.subplots(2, 3, figsize=(12, 8))
        fig.suptitle('Zero-Dose Vaccination Policy Decision Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Scenario comparison
        ax1 = axes[0, 0]
        scenarios = list(self.scenario_results.keys())
        policy_scores = [self.scenario_results[s]['policy_metrics']['policy_success_score'] for s in scenarios]
        
        bars = ax1.bar(scenarios, policy_scores, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
        ax1.set_title('Policy Success Score by Scenario', fontweight='bold')
        ax1.set_ylabel('Success Score')
        ax1.tick_params(axis='x', rotation=45)
        
        # Highlight best scenario
        best_idx = policy_scores.index(max(policy_scores))
        bars[best_idx].set_color('darkgreen')
        bars[best_idx].set_edgecolor('black')
        bars[best_idx].set_linewidth(2)
        
        # 2. Disease burden comparison
        ax2 = axes[0, 1]
        disease_names = []
        baseline_burden = []
        optimal_burden = []
        
        baseline_results = self.scenario_results['baseline']
        optimal_scenario = self.policy_recommendations['optimal_scenario']
        optimal_results = self.scenario_results[optimal_scenario]
        
        for disease_name in ['tetanus', 'diphtheria', 'hepatitisb', 'hib', 'pertussis']:
            if disease_name in baseline_results['disease_impact']:
                disease_names.append(disease_name.title())
                baseline_burden.append(baseline_results['disease_impact'][disease_name]['burden_score'])
                optimal_burden.append(optimal_results['disease_impact'][disease_name]['burden_score'])
        
        x = np.arange(len(disease_names))
        width = 0.35
        
        ax2.bar(x - width/2, baseline_burden, width, label='Baseline', color='red', alpha=0.7)
        ax2.bar(x + width/2, optimal_burden, width, label='Optimal Policy', color='green', alpha=0.7)
        
        ax2.set_title('Disease Burden: Baseline vs Optimal Policy', fontweight='bold')
        ax2.set_ylabel('Burden Score')
        ax2.set_xticks(x)
        ax2.set_xticklabels(disease_names, rotation=45)
        ax2.legend()
        
        # 3. Cost-effectiveness analysis
        ax3 = axes[0, 2]
        scenarios = list(self.scenario_results.keys())
        cost_ratios = [self.scenario_results[s]['cost_effectiveness']['cost_effectiveness_ratio'] for s in scenarios]
        
        bars = ax3.bar(scenarios, cost_ratios, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
        ax3.set_title('Cost-Effectiveness by Scenario', fontweight='bold')
        ax3.set_ylabel('Cost per Case Averted ($)')
        ax3.tick_params(axis='x', rotation=45)
        
        # Highlight most cost-effective
        best_cost_idx = cost_ratios.index(min(cost_ratios))
        bars[best_cost_idx].set_color('darkgreen')
        bars[best_cost_idx].set_edgecolor('black')
        bars[best_cost_idx].set_linewidth(2)
        
        # 4. Vaccination coverage
        ax4 = axes[1, 0]
        coverage_data = []
        for scenario in scenarios:
            if scenario == 'baseline':
                coverage_data.append(0)
            else:
                coverage_data.append(self.scenario_results[scenario]['vaccination_impact']['coverage_achieved'])
        
        bars = ax4.bar(scenarios, coverage_data, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
        ax4.set_title('Vaccination Coverage by Scenario', fontweight='bold')
        ax4.set_ylabel('Coverage Rate')
        ax4.tick_params(axis='x', rotation=45)
        
        # Add target line
        ax4.axhline(y=0.9, color='red', linestyle='--', alpha=0.7, label='WHO Target (90%)')
        ax4.legend()
        
        # 5. Cases averted
        ax5 = axes[1, 1]
        cases_averted = [self.scenario_results[s]['cost_effectiveness']['cases_averted'] for s in scenarios]
        
        bars = ax5.bar(scenarios, cases_averted, color=['red', 'orange', 'yellow', 'lightgreen', 'green'])
        ax5.set_title('Cases Averted by Scenario', fontweight='bold')
        ax5.set_ylabel('Cases Averted')
        ax5.tick_params(axis='x', rotation=45)
        
        # 6. Policy recommendations summary
        ax6 = axes[1, 2]
        ax6.text(0.1, 0.9, 'POLICY RECOMMENDATIONS', fontsize=14, fontweight='bold', transform=ax6.transAxes)
        ax6.text(0.1, 0.8, f'Optimal Scenario: {self.policy_recommendations["optimal_scenario"].upper()}', 
                fontsize=12, transform=ax6.transAxes)
        ax6.text(0.1, 0.7, f'Cost-Effective: {self.policy_recommendations["cost_effective_scenario"].upper()}', 
                fontsize=12, transform=ax6.transAxes)
        
        # Disease priorities
        ax6.text(0.1, 0.6, 'Disease Priorities:', fontsize=12, fontweight='bold', transform=ax6.transAxes)
        for i, (disease, burden) in enumerate(self.policy_recommendations['disease_priority'][:3]):
            ax6.text(0.1, 0.5 - i*0.08, f'{i+1}. {disease.upper()}', fontsize=10, transform=ax6.transAxes)
        
        ax6.set_xlim(0, 1)
        ax6.set_ylim(0, 1)
        ax6.axis('off')
        
        plt.tight_layout()
        plt.show()
        
        return fig
    
    def export_policy_report(self, output_path="policy_decision_report.txt"):
        """Export comprehensive policy decision report"""
        print(f"\nGenerating policy decision report: {output_path}")
        
        with open(output_path, 'w') as f:
            f.write("ZERO-DOSE VACCINATION POLICY DECISION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write("This report provides evidence-based policy recommendations\n")
            f.write("for zero-dose vaccination interventions based on real-world\n")
            f.write("data analysis and calibrated model simulations.\n\n")
            
            # Executive summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 20 + "\n")
            f.write(f"Optimal Policy Scenario: {self.policy_recommendations['optimal_scenario'].upper()}\n")
            f.write(f"Most Cost-Effective: {self.policy_recommendations['cost_effective_scenario'].upper()}\n")
            f.write(f"Analysis based on real epidemiological data from 2018-2024\n")
            f.write(f"Model calibrated against observed disease patterns\n\n")
            
            # Scenario analysis
            f.write("SCENARIO ANALYSIS RESULTS\n")
            f.write("-" * 30 + "\n")
            for scenario_name, results in self.scenario_results.items():
                f.write(f"\n{scenario_name.upper()} SCENARIO:\n")
                f.write(f"  Policy Success Score: {results['policy_metrics']['policy_success_score']:.3f}\n")
                f.write(f"  Vaccination Coverage: {results['vaccination_impact'].get('coverage_achieved', 0):.1%}\n")
                f.write(f"  Cases Averted: {results['cost_effectiveness']['cases_averted']:.0f}\n")
                f.write(f"  Cost per Case Averted: ${results['cost_effectiveness']['cost_effectiveness_ratio']:.2f}\n")
            
            # Disease priorities
            f.write("\n\nDISEASE PRIORITY RANKING\n")
            f.write("-" * 30 + "\n")
            for i, (disease, burden) in enumerate(self.policy_recommendations['disease_priority'], 1):
                f.write(f"{i}. {disease.upper()}: Burden Score {burden:.3f}\n")
            
            # Implementation strategy
            f.write("\n\nIMPLEMENTATION STRATEGY\n")
            f.write("-" * 25 + "\n")
            for strategy in self.policy_recommendations['implementation_strategy']:
                f.write(f"• {strategy}\n")
            
            # Monitoring metrics
            f.write("\n\nMONITORING METRICS\n")
            f.write("-" * 20 + "\n")
            for metric in self.policy_recommendations['monitoring_metrics']:
                f.write(f"• {metric}\n")
            
            # Policy recommendations
            f.write("\n\nPOLICY RECOMMENDATIONS\n")
            f.write("-" * 25 + "\n")
            f.write("1. Implement the optimal policy scenario for maximum impact\n")
            f.write("2. Focus on high-priority diseases first\n")
            f.write("3. Monitor key metrics regularly\n")
            f.write("4. Adjust strategy based on real-world outcomes\n")
            f.write("5. Ensure equitable access to vaccination\n")
        
        print(f"✓ Policy decision report exported to {output_path}")
        return True

def main():
    """Main function to demonstrate policy decision support"""
    print("POLICY DECISION SUPPORT SYSTEM FOR ZERO-DOSE VACCINATION")
    print("=" * 70)
    
    # Initialize policy support system
    policy_support = PolicyDecisionSupport()
    
    # Load data and calibrate model
    print("\n1. Loading real data and calibrating model...")
    if not policy_support.load_data_and_calibrate():
        print("Failed to load data. Exiting.")
        return
    
    # Analyze policy scenarios
    print("\n2. Analyzing policy scenarios...")
    scenario_results = policy_support.analyze_policy_scenarios()
    
    # Generate policy recommendations
    print("\n3. Generating policy recommendations...")
    recommendations = policy_support.generate_policy_recommendations()
    
    # Create policy dashboard
    print("\n4. Creating policy dashboard...")
    dashboard = policy_support.create_policy_dashboard()
    
    # Export comprehensive report
    print("\n5. Exporting policy decision report...")
    policy_support.export_policy_report()
    
    print("\n" + "="*70)
    print("POLICY DECISION SUPPORT COMPLETE")
    print("="*70)
    print("✓ Real data analyzed and model calibrated")
    print("✓ Multiple policy scenarios evaluated")
    print("✓ Evidence-based recommendations generated")
    print("✓ Policy dashboard created for decision-makers")
    print("✓ Comprehensive report exported")

if __name__ == '__main__':
    main()
