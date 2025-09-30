#!/usr/bin/env python3
"""
Zero-Dose Data Extraction Script

This script extracts and analyzes data from the zerodose_data.dta file,
providing comprehensive data exploration and export capabilities.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_zerodose_data():
    """Load data from the zerodose_data.dta file"""
    
    print("Loading zero-dose data from .dta file...")
    
    try:
        # Load Stata file
        data_file = 'zdsim/data/zerodose_data.dta'
        data = pd.read_stata(data_file)
        print(f"✓ Successfully loaded .dta file: {len(data)} records, {len(data.columns)} columns")
        return data
    except Exception as e:
        print(f"❌ Error loading .dta file: {e}")
        
        # Try loading Excel file as backup
        try:
            excel_file = 'zdsim/data/zerodose_data.xlsx'
            data = pd.read_excel(excel_file)
            print(f"✓ Successfully loaded .xlsx file: {len(data)} records, {len(data.columns)} columns")
            return data
        except Exception as e2:
            print(f"❌ Error loading .xlsx file: {e2}")
            return None

def explore_data_structure(data):
    """Explore the structure of the zero-dose data"""
    
    print("\n" + "="*80)
    print("ZERO-DOSE DATA STRUCTURE EXPLORATION")
    print("="*80)
    
    print(f"Dataset Overview:")
    print(f"  Total records: {len(data):,}")
    print(f"  Total columns: {len(data.columns)}")
    print(f"  Memory usage: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print(f"\nColumn Information:")
    print("-" * 50)
    for i, col in enumerate(data.columns):
        dtype = data[col].dtype
        non_null = data[col].count()
        null_count = len(data) - non_null
        print(f"{i+1:2d}. {col:<30} | {str(dtype):<15} | {non_null:>6} non-null | {null_count:>4} null")
    
    return data

def analyze_disease_columns(data):
    """Analyze disease-specific columns in the data"""
    
    print("\n" + "="*60)
    print("DISEASE-SPECIFIC COLUMNS ANALYSIS")
    print("="*60)
    
    # Define disease columns based on the real data loader
    disease_columns = {
        'diphtheria': ['diphtheria'],
        'tetanus': ['tetanus'],
        'pertussis': ['pertussis'],
        'hepatitis_b': ['hepatitis_b', 'hepatitisb_positive'],
        'hib': ['hib'],
        'pneumonia': ['pneumonia', 'lower_rti', 'other_acute_lower_resp_infe'],
        'measles': ['measles', 'measles1', 'measles2'],
        'tuberculosis': ['presumed_tuberculosis', 'respiratory_tuberculosis', 'other_tuberculosis']
    }
    
    # Vaccination columns
    vaccine_columns = {
        'dpt': ['dpt1', 'dpt2', 'dpt3'],
        'opv': ['opv0', 'opv1', 'opv2', 'opv3'],
        'bcg': ['bcg'],
        'measles': ['measles1', 'measles2'],
        'hepatitis_b': ['hepatitisb_positive'],
        'pneumococcal': ['pneumococal1', 'pneumococal2', 'pneumococal3'],
        'rotavirus': ['rota1', 'rota2', 'rota3']
    }
    
    # Demographic columns
    demographic_columns = {
        'births': ['estimated_lb', 'estimated_deliveries'],
        'age_groups': ['fic_at_1yr', 'fic_under_1yr', 'fic_above_2yrs']
    }
    
    print("Disease Columns Found:")
    print("-" * 30)
    for disease, columns in disease_columns.items():
        found_columns = [col for col in columns if col in data.columns]
        if found_columns:
            print(f"  {disease.upper()}: {found_columns}")
            for col in found_columns:
                if col in data.columns:
                    unique_vals = data[col].nunique()
                    print(f"    - {col}: {unique_vals} unique values")
    
    print(f"\nVaccination Columns Found:")
    print("-" * 30)
    for vaccine, columns in vaccine_columns.items():
        found_columns = [col for col in columns if col in data.columns]
        if found_columns:
            print(f"  {vaccine.upper()}: {found_columns}")
            for col in found_columns:
                if col in data.columns:
                    unique_vals = data[col].nunique()
                    print(f"    - {col}: {unique_vals} unique values")
    
    print(f"\nDemographic Columns Found:")
    print("-" * 30)
    for demo, columns in demographic_columns.items():
        found_columns = [col for col in columns if col in data.columns]
        if found_columns:
            print(f"  {demo.upper()}: {found_columns}")
            for col in found_columns:
                if col in data.columns:
                    unique_vals = data[col].nunique()
                    print(f"    - {col}: {unique_vals} unique values")
    
    return disease_columns, vaccine_columns, demographic_columns

def analyze_disease_prevalence(data):
    """Analyze disease prevalence in the data"""
    
    print("\n" + "="*60)
    print("DISEASE PREVALENCE ANALYSIS")
    print("="*60)
    
    # Disease columns to analyze
    disease_cols = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib', 
                   'presumed_tuberculosis', 'respiratory_tuberculosis', 'other_tuberculosis']
    
    print("Disease Prevalence:")
    print("-" * 40)
    for col in disease_cols:
        if col in data.columns:
            # Handle different data types
            if data[col].dtype in ['object', 'category']:
                # Categorical data
                value_counts = data[col].value_counts()
                print(f"  {col}:")
                for val, count in value_counts.items():
                    pct = count / len(data) * 100
                    print(f"    {val}: {count:,} ({pct:.1f}%)")
            else:
                # Numeric data
                if data[col].max() > 1:
                    # Likely binary encoded (0/1)
                    positive = (data[col] > 0).sum()
                    prevalence = positive / len(data) * 100
                    print(f"  {col}: {positive:,} cases ({prevalence:.1f}%)")
                else:
                    # Likely already binary
                    positive = data[col].sum()
                    prevalence = positive / len(data) * 100
                    print(f"  {col}: {positive:,} cases ({prevalence:.1f}%)")
        else:
            print(f"  {col}: Column not found")

def analyze_vaccination_coverage(data):
    """Analyze vaccination coverage in the data"""
    
    print("\n" + "="*60)
    print("VACCINATION COVERAGE ANALYSIS")
    print("="*60)
    
    # Vaccination columns to analyze
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'opv0', 'opv1', 'opv2', 'opv3', 
                   'bcg', 'measles1', 'measles2', 'hepatitisb_positive']
    
    print("Vaccination Coverage:")
    print("-" * 40)
    for col in vaccine_cols:
        if col in data.columns:
            if data[col].dtype in ['object', 'category']:
                # Categorical data
                value_counts = data[col].value_counts()
                print(f"  {col}:")
                for val, count in value_counts.items():
                    pct = count / len(data) * 100
                    print(f"    {val}: {count:,} ({pct:.1f}%)")
            else:
                # Numeric data
                if data[col].max() > 1:
                    # Likely binary encoded (0/1)
                    vaccinated = (data[col] > 0).sum()
                    coverage = vaccinated / len(data) * 100
                    print(f"  {col}: {vaccinated:,} vaccinated ({coverage:.1f}%)")
                else:
                    # Likely already binary
                    vaccinated = data[col].sum()
                    coverage = vaccinated / len(data) * 100
                    print(f"  {col}: {vaccinated:,} vaccinated ({coverage:.1f}%)")
        else:
            print(f"  {col}: Column not found")

def create_data_visualization(data):
    """Create comprehensive data visualization"""
    
    print("\n" + "="*60)
    print("CREATING DATA VISUALIZATION")
    print("="*60)
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Zero-Dose Data Analysis\n(Extracted from zerodose_data.dta)', 
                 fontsize=16, fontweight='bold')
    
    # 1. Disease prevalence
    ax1 = axes[0, 0]
    disease_cols = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    prevalences = []
    diseases = []
    
    for col in disease_cols:
        if col in data.columns:
            if data[col].max() > 1:
                positive = (data[col] > 0).sum()
            else:
                positive = data[col].sum()
            prevalence = positive / len(data) * 100
            prevalences.append(prevalence)
            diseases.append(col.replace('_', ' ').title())
    
    if prevalences:
        bars = ax1.bar(diseases, prevalences, color=['red', 'orange', 'yellow', 'green', 'blue'], alpha=0.7)
        ax1.set_ylabel('Prevalence (%)')
        ax1.set_title('Disease Prevalence')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, prevalences):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(prevalences)*0.01,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Vaccination coverage
    ax2 = axes[0, 1]
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'bcg']
    coverages = []
    vaccines = []
    
    for col in vaccine_cols:
        if col in data.columns:
            if data[col].max() > 1:
                vaccinated = (data[col] > 0).sum()
            else:
                vaccinated = data[col].sum()
            coverage = vaccinated / len(data) * 100
            coverages.append(coverage)
            vaccines.append(col.upper())
    
    if coverages:
        bars = ax2.bar(vaccines, coverages, color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow'], alpha=0.7)
        ax2.set_ylabel('Coverage (%)')
        ax2.set_title('Vaccination Coverage')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, coverages):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(coverages)*0.01,
                    f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 3. Data completeness
    ax3 = axes[1, 0]
    completeness = []
    columns = []
    
    for col in data.columns:
        non_null = data[col].count()
        completeness_pct = non_null / len(data) * 100
        completeness.append(completeness_pct)
        columns.append(col)
    
    # Show top 10 most complete columns
    completeness_df = pd.DataFrame({'column': columns, 'completeness': completeness})
    top_columns = completeness_df.nlargest(10, 'completeness')
    
    bars = ax3.barh(range(len(top_columns)), top_columns['completeness'], alpha=0.7)
    ax3.set_xlabel('Completeness (%)')
    ax3.set_title('Data Completeness (Top 10 Columns)')
    ax3.set_yticks(range(len(top_columns)))
    ax3.set_yticklabels(top_columns['column'], fontsize=8)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, top_columns['completeness'])):
        ax3.text(value + 1, bar.get_y() + bar.get_height()/2,
                f'{value:.1f}%', ha='left', va='center', fontweight='bold')
    
    # 4. Data summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Create summary text
    summary_text = f"""
ZERO-DOSE DATA SUMMARY

Dataset: {len(data):,} records
Columns: {len(data.columns)} variables
Memory: {data.memory_usage(deep=True).sum() / 1024**2:.1f} MB

Disease Data:
"""
    
    disease_cols = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
    for col in disease_cols:
        if col in data.columns:
            if data[col].max() > 1:
                positive = (data[col] > 0).sum()
            else:
                positive = data[col].sum()
            prevalence = positive / len(data) * 100
            summary_text += f"• {col.replace('_', ' ').title()}: {prevalence:.1f}%\n"
    
    summary_text += f"\nVaccination Data:\n"
    vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'bcg']
    for col in vaccine_cols:
        if col in data.columns:
            if data[col].max() > 1:
                vaccinated = (data[col] > 0).sum()
            else:
                vaccinated = data[col].sum()
            coverage = vaccinated / len(data) * 100
            summary_text += f"• {col.upper()}: {coverage:.1f}%\n"
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('zerodose_data_extraction.pdf', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✓ Data visualization created and saved")

def export_data_summary(data):
    """Export data summary to files"""
    
    print("\n" + "="*60)
    print("EXPORTING DATA SUMMARY")
    print("="*60)
    
    # Export to CSV
    csv_file = 'zerodose_data_extracted.csv'
    data.to_csv(csv_file, index=False)
    print(f"✓ Data exported to CSV: {csv_file}")
    
    # Export summary statistics
    summary_file = 'zerodose_data_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("ZERO-DOSE DATA EXTRACTION SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Records: {len(data):,}\n")
        f.write(f"Total Columns: {len(data.columns)}\n")
        f.write(f"Memory Usage: {data.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
        
        f.write("COLUMN INFORMATION:\n")
        f.write("-" * 30 + "\n")
        for i, col in enumerate(data.columns):
            dtype = data[col].dtype
            non_null = data[col].count()
            null_count = len(data) - non_null
            f.write(f"{i+1:2d}. {col:<30} | {str(dtype):<15} | {non_null:>6} non-null | {null_count:>4} null\n")
        
        f.write("\nDISEASE PREVALENCE:\n")
        f.write("-" * 30 + "\n")
        disease_cols = ['diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib']
        for col in disease_cols:
            if col in data.columns:
                if data[col].max() > 1:
                    positive = (data[col] > 0).sum()
                else:
                    positive = data[col].sum()
                prevalence = positive / len(data) * 100
                f.write(f"{col}: {positive:,} cases ({prevalence:.1f}%)\n")
        
        f.write("\nVACCINATION COVERAGE:\n")
        f.write("-" * 30 + "\n")
        vaccine_cols = ['dpt1', 'dpt2', 'dpt3', 'bcg']
        for col in vaccine_cols:
            if col in data.columns:
                if data[col].max() > 1:
                    vaccinated = (data[col] > 0).sum()
                else:
                    vaccinated = data[col].sum()
                coverage = vaccinated / len(data) * 100
                f.write(f"{col}: {vaccinated:,} vaccinated ({coverage:.1f}%)\n")
    
    print(f"✓ Summary exported to: {summary_file}")
    
    return csv_file, summary_file

def main():
    """Main function to extract and analyze zero-dose data"""
    
    print("="*80)
    print("ZERO-DOSE DATA EXTRACTION")
    print("="*80)
    print(f"Extraction started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    data = load_zerodose_data()
    if data is None:
        print("❌ Could not load data from any source")
        return
    
    # Explore data structure
    explore_data_structure(data)
    
    # Analyze disease columns
    disease_cols, vaccine_cols, demo_cols = analyze_disease_columns(data)
    
    # Analyze disease prevalence
    analyze_disease_prevalence(data)
    
    # Analyze vaccination coverage
    analyze_vaccination_coverage(data)
    
    # Create visualization
    create_data_visualization(data)
    
    # Export data
    csv_file, summary_file = export_data_summary(data)
    
    print("\n" + "="*80)
    print("ZERO-DOSE DATA EXTRACTION COMPLETED")
    print("="*80)
    print("Files generated:")
    print(f"  - {csv_file}")
    print(f"  - {summary_file}")
    print("  - zerodose_data_extraction.pdf")
    print("\nKey insights:")
    print("  - Data successfully extracted from .dta file")
    print("  - Disease prevalence and vaccination coverage analyzed")
    print("  - Comprehensive data structure exploration completed")
    print("  - Data exported to multiple formats for further analysis")

if __name__ == '__main__':
    main()
