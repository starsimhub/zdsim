"""
Real Data Loader and Analyzer for Zero-Dose Vaccination Model

This script loads and analyzes real-world epidemiological data to inform
model parameters and validate outcomes for policy decision-making.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class RealDataAnalyzer:
    """Analyze real-world epidemiological data for model calibration"""
    
    def __init__(self, data_path="zdsim/data/zerodose_data.dta"):
        """Initialize with real data path"""
        self.data_path = data_path
        self.data = None
        self.disease_columns = {}
        self.vaccine_columns = {}
        self.demographic_columns = {}
        
    def load_data(self):
        """Load real-world data from Stata file"""
        try:
            print("Loading real-world epidemiological data...")
            self.data = pd.read_stata(self.data_path)
            print(f"✓ Data loaded: {self.data.shape[0]} months, {self.data.shape[1]} variables")
            
            # Identify column categories
            self._categorize_columns()
            return True
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return False
    
    def _categorize_columns(self):
        """Categorize columns by type for analysis"""
        
        # Disease case columns
        self.disease_columns = {
            'tetanus': ['tetanus', 'neonatal_tetanus', 'peri_neonatal_tetanus', 'tetanus_inpatient'],
            'diphtheria': ['diphtheria'],
            'pertussis': [],  # Not directly available in data
            'hepatitis_b': ['hepatitisb_positive', 'hepatitis'],
            'hib': [],  # Not directly available, but pneumonia might be proxy
            'pneumonia': ['pneumonia', 'lower_rti', 'other_acute_lower_resp_infe'],
            'measles': ['measles', 'measles1', 'measles2'],
            'tuberculosis': ['presumed_tuberculosis', 'respiratory_tuberculosis', 'other_tuberculosis']
        }
        
        # Vaccination coverage columns
        self.vaccine_columns = {
            'dpt': ['dpt1', 'dpt2', 'dpt3'],
            'opv': ['opv0', 'opv1', 'opv2', 'opv3'],
            'bcg': ['bcg'],
            'measles': ['measles1', 'measles2'],
            'hepatitis_b': ['hepatitisb_positive'],
            'pneumococcal': ['pneumococal1', 'pneumococal2', 'pneumococal3'],
            'rotavirus': ['rota1', 'rota2', 'rota3']
        }
        
        # Demographic columns
        self.demographic_columns = {
            'births': ['estimated_lb', 'estimated_deliveries'],
            'age_groups': ['fic_at_1yr', 'fic_under_1yr', 'fic_above_2yrs']
        }
    
    def analyze_disease_burden(self):
        """Analyze real disease burden patterns"""
        if self.data is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        print("\n" + "="*60)
        print("REAL-WORLD DISEASE BURDEN ANALYSIS")
        print("="*60)
        
        disease_analysis = {}
        
        for disease, columns in self.disease_columns.items():
            if not columns:
                continue
                
            print(f"\n{disease.upper()} ANALYSIS:")
            print("-" * 40)
            
            # Get available columns for this disease
            available_cols = [col for col in columns if col in self.data.columns]
            
            if not available_cols:
                print(f"  No data available for {disease}")
                continue
            
            # Calculate statistics
            disease_data = self.data[available_cols].sum(axis=1)  # Sum across related columns
            
            stats = {
                'mean_monthly_cases': disease_data.mean(),
                'std_monthly_cases': disease_data.std(),
                'min_monthly_cases': disease_data.min(),
                'max_monthly_cases': disease_data.max(),
                'total_cases': disease_data.sum(),
                'trend': self._calculate_trend(disease_data),
                'seasonality': self._analyze_seasonality(disease_data)
            }
            
            disease_analysis[disease] = stats
            
            print(f"  Mean monthly cases: {stats['mean_monthly_cases']:.0f}")
            print(f"  Range: {stats['min_monthly_cases']:.0f} - {stats['max_monthly_cases']:.0f}")
            print(f"  Total cases (6 years): {stats['total_cases']:.0f}")
            print(f"  Trend: {stats['trend']:.2f} cases/month")
            
        return disease_analysis
    
    def analyze_vaccination_coverage(self):
        """Analyze real vaccination coverage patterns"""
        if self.data is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        print("\n" + "="*60)
        print("REAL-WORLD VACCINATION COVERAGE ANALYSIS")
        print("="*60)
        
        vaccine_analysis = {}
        
        for vaccine, columns in self.vaccine_columns.items():
            if not columns:
                continue
                
            print(f"\n{vaccine.upper()} VACCINATION:")
            print("-" * 40)
            
            # Get available columns for this vaccine
            available_cols = [col for col in columns if col in self.data.columns]
            
            if not available_cols:
                print(f"  No data available for {vaccine}")
                continue
            
            # Calculate coverage statistics
            vaccine_data = self.data[available_cols]
            
            stats = {
                'mean_coverage': vaccine_data.mean().mean(),
                'coverage_trend': self._calculate_trend(vaccine_data.mean(axis=1)),
                'coverage_consistency': vaccine_data.std().mean(),
                'max_coverage': vaccine_data.max().max(),
                'min_coverage': vaccine_data.min().min()
            }
            
            vaccine_analysis[vaccine] = stats
            
            print(f"  Mean coverage: {stats['mean_coverage']:.0f} doses/month")
            print(f"  Coverage range: {stats['min_coverage']:.0f} - {stats['max_coverage']:.0f}")
            print(f"  Coverage trend: {stats['coverage_trend']:.2f} doses/month")
            
        return vaccine_analysis
    
    def calculate_disease_rates(self):
        """Calculate disease incidence rates from real data"""
        if self.data is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        print("\n" + "="*60)
        print("DISEASE INCIDENCE RATES (Real Data)")
        print("="*60)
        
        # Estimate population (using births as proxy)
        births_per_month = self.data['estimated_lb'].mean()
        estimated_population = births_per_month * 12 * 25  # Rough estimate: births * 12 months * 25 years avg lifespan
        
        disease_rates = {}
        
        for disease, columns in self.disease_columns.items():
            if not columns:
                continue
                
            available_cols = [col for col in columns if col in self.data.columns]
            if not available_cols:
                continue
            
            # Calculate monthly cases
            monthly_cases = self.data[available_cols].sum(axis=1)
            
            # Calculate rates
            annual_cases = monthly_cases.mean() * 12
            incidence_rate = annual_cases / estimated_population
            
            disease_rates[disease] = {
                'annual_cases': annual_cases,
                'incidence_rate': incidence_rate,
                'monthly_rate': monthly_cases.mean()
            }
            
            print(f"{disease.upper()}:")
            print(f"  Annual cases: {annual_cases:.0f}")
            print(f"  Incidence rate: {incidence_rate:.6f} (per person per year)")
            print(f"  Monthly rate: {monthly_cases.mean():.0f} cases/month")
        
        return disease_rates
    
    def _calculate_trend(self, data):
        """Calculate linear trend in data"""
        x = np.arange(len(data))
        y = data.values
        trend = np.polyfit(x, y, 1)[0]  # Linear slope
        return trend
    
    def _analyze_seasonality(self, data):
        """Analyze seasonal patterns in disease data"""
        if len(data) < 12:
            return "Insufficient data for seasonality analysis"
        
        # Group by month
        months = self.data['month'].values[:len(data)]
        monthly_means = data.groupby(months).mean()
        
        # Find peak and low months
        peak_month = monthly_means.idxmax()
        low_month = monthly_means.idxmin()
        peak_value = monthly_means.max()
        low_value = monthly_means.min()
        
        seasonality_ratio = peak_value / low_value if low_value > 0 else float('inf')
        
        return {
            'peak_month': peak_month,
            'low_month': low_month,
            'seasonality_ratio': seasonality_ratio,
            'monthly_pattern': monthly_means.to_dict()
        }
    
    def create_policy_insights(self):
        """Generate insights for policy makers"""
        if self.data is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        print("\n" + "="*60)
        print("POLICY INSIGHTS FROM REAL DATA")
        print("="*60)
        
        insights = {}
        
        # Disease burden insights
        disease_analysis = self.analyze_disease_burden()
        if disease_analysis:
            insights['disease_burden'] = self._generate_disease_insights(disease_analysis)
        
        # Vaccination insights
        vaccine_analysis = self.analyze_vaccination_coverage()
        if vaccine_analysis:
            insights['vaccination'] = self._generate_vaccination_insights(vaccine_analysis)
        
        # Priority diseases
        insights['priority_diseases'] = self._identify_priority_diseases(disease_analysis)
        
        return insights
    
    def _generate_disease_insights(self, disease_analysis):
        """Generate disease-specific policy insights"""
        insights = []
        
        for disease, stats in disease_analysis.items():
            if disease == 'tetanus':
                if stats['mean_monthly_cases'] > 500:
                    insights.append(f"🚨 HIGH PRIORITY: Tetanus cases are high ({stats['mean_monthly_cases']:.0f}/month) - immediate vaccination needed")
                elif stats['trend'] > 0:
                    insights.append(f"⚠️  WARNING: Tetanus cases increasing ({stats['trend']:.1f}/month) - vaccination coverage may be declining")
            
            elif disease == 'diphtheria':
                if stats['mean_monthly_cases'] > 1:
                    insights.append(f"🚨 CRITICAL: Diphtheria cases present ({stats['mean_monthly_cases']:.1f}/month) - outbreak risk")
                else:
                    insights.append(f"✅ GOOD: Diphtheria cases controlled ({stats['mean_monthly_cases']:.1f}/month)")
            
            elif disease == 'pneumonia':
                if stats['mean_monthly_cases'] > 500000:
                    insights.append(f"🚨 MAJOR BURDEN: Pneumonia cases very high ({stats['mean_monthly_cases']:.0f}/month) - Hib vaccination priority")
                elif stats['trend'] > 0:
                    insights.append(f"⚠️  CONCERN: Pneumonia cases increasing - review Hib vaccination")
        
        return insights
    
    def _generate_vaccination_insights(self, vaccine_analysis):
        """Generate vaccination-specific policy insights"""
        insights = []
        
        for vaccine, stats in vaccine_analysis.items():
            if vaccine == 'dpt':
                if stats['mean_coverage'] < 100000:  # Assuming this is dose count
                    insights.append(f"🚨 LOW DPT COVERAGE: {stats['mean_coverage']:.0f} doses/month - increase routine vaccination")
                elif stats['coverage_trend'] < 0:
                    insights.append(f"⚠️  DECLINING DPT: Coverage decreasing ({stats['coverage_trend']:.0f}/month) - investigate barriers")
                else:
                    insights.append(f"✅ GOOD DPT: Coverage stable at {stats['mean_coverage']:.0f} doses/month")
            
            elif vaccine == 'measles':
                if stats['mean_coverage'] < 50000:
                    insights.append(f"🚨 LOW MEASLES COVERAGE: {stats['mean_coverage']:.0f} doses/month - campaign needed")
                elif stats['coverage_trend'] < 0:
                    insights.append(f"⚠️  DECLINING MEASLES: Coverage decreasing - outbreak risk")
        
        return insights
    
    def _identify_priority_diseases(self, disease_analysis):
        """Identify priority diseases for policy focus"""
        if not disease_analysis:
            return []
        
        priorities = []
        
        # Sort by mean monthly cases
        sorted_diseases = sorted(disease_analysis.items(), 
                               key=lambda x: x[1]['mean_monthly_cases'], 
                               reverse=True)
        
        for i, (disease, stats) in enumerate(sorted_diseases[:3]):  # Top 3
            priority_level = "HIGH" if i == 0 else "MEDIUM" if i == 1 else "LOW"
            priorities.append(f"{priority_level} PRIORITY: {disease.upper()} ({stats['mean_monthly_cases']:.0f} cases/month)")
        
        return priorities
    
    def export_policy_report(self, output_path="policy_insights_report.txt"):
        """Export comprehensive policy report"""
        if self.data is None:
            print("No data loaded. Call load_data() first.")
            return False
        
        print(f"\nGenerating policy report: {output_path}")
        
        with open(output_path, 'w') as f:
            f.write("ZERO-DOSE VACCINATION POLICY INSIGHTS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Data Source: {self.data_path}\n")
            f.write(f"Analysis Period: {self.data['year'].min()}-{self.data['year'].max()}\n")
            f.write(f"Total Observations: {len(self.data)} months\n\n")
            
            # Disease burden section
            f.write("DISEASE BURDEN ANALYSIS\n")
            f.write("-" * 30 + "\n")
            disease_analysis = self.analyze_disease_burden()
            if disease_analysis:
                for disease, stats in disease_analysis.items():
                    f.write(f"\n{disease.upper()}:\n")
                    f.write(f"  Mean monthly cases: {stats['mean_monthly_cases']:.0f}\n")
                    f.write(f"  Total cases (6 years): {stats['total_cases']:.0f}\n")
                    f.write(f"  Trend: {stats['trend']:.2f} cases/month\n")
            
            # Vaccination coverage section
            f.write("\n\nVACCINATION COVERAGE ANALYSIS\n")
            f.write("-" * 35 + "\n")
            vaccine_analysis = self.analyze_vaccination_coverage()
            if vaccine_analysis:
                for vaccine, stats in vaccine_analysis.items():
                    f.write(f"\n{vaccine.upper()}:\n")
                    f.write(f"  Mean coverage: {stats['mean_coverage']:.0f} doses/month\n")
                    f.write(f"  Coverage trend: {stats['coverage_trend']:.2f} doses/month\n")
            
            # Policy insights section
            f.write("\n\nPOLICY RECOMMENDATIONS\n")
            f.write("-" * 25 + "\n")
            insights = self.create_policy_insights()
            if insights:
                if 'disease_burden' in insights:
                    f.write("\nDisease Burden Insights:\n")
                    for insight in insights['disease_burden']:
                        f.write(f"  {insight}\n")
                
                if 'vaccination' in insights:
                    f.write("\nVaccination Insights:\n")
                    for insight in insights['vaccination']:
                        f.write(f"  {insight}\n")
                
                if 'priority_diseases' in insights:
                    f.write("\nPriority Diseases:\n")
                    for priority in insights['priority_diseases']:
                        f.write(f"  {priority}\n")
        
        print(f"✓ Policy report exported to {output_path}")
        return True

def main():
    """Main function to demonstrate real data analysis"""
    print("REAL DATA ANALYSIS FOR POLICY DECISION-MAKING")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = RealDataAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        return
    
    # Perform comprehensive analysis
    print("\n1. Analyzing disease burden...")
    disease_analysis = analyzer.analyze_disease_burden()
    
    print("\n2. Analyzing vaccination coverage...")
    vaccine_analysis = analyzer.analyze_vaccination_coverage()
    
    print("\n3. Calculating disease rates...")
    disease_rates = analyzer.calculate_disease_rates()
    
    print("\n4. Generating policy insights...")
    insights = analyzer.create_policy_insights()
    
    print("\n5. Exporting policy report...")
    analyzer.export_policy_report()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE - POLICY INSIGHTS GENERATED")
    print("="*60)
    print("✓ Real data loaded and analyzed")
    print("✓ Disease burden patterns identified")
    print("✓ Vaccination coverage assessed")
    print("✓ Policy recommendations generated")
    print("✓ Report exported for decision-makers")

if __name__ == '__main__':
    main()
