#!/usr/bin/env python3
"""
Tetanus Data Analysis

This script provides comprehensive analysis of tetanus data from the zerodose_data.dta file,
including age-specific segments, vaccination coverage, and epidemiological patterns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_tetanus_data():
    """Load and extract tetanus-specific data from the .dta file"""
    
    print("Loading tetanus data from zerodose_data.dta...")
    
    try:
        # Load the full dataset
        data_file = 'zdsim/data/zerodose_data.dta'
        data = pd.read_stata(data_file)
        print(f"✓ Successfully loaded data: {len(data)} records, {len(data.columns)} columns")
        
        # Extract tetanus-specific columns
        tetanus_columns = [
            'tetanus', 'neonatal_tetanus', 'peri_neonatal_tetanus', 
            'tetanus_inpatient', 'year', 'month', 'estimated_lb', 'estimated_deliveries',
            'fic_at_1yr', 'fic_under_1yr', 'fic_above_2yrs'
        ]
        
        # Filter to available tetanus columns
        available_columns = [col for col in tetanus_columns if col in data.columns]
        tetanus_data = data[available_columns].copy()
        
        print(f"✓ Extracted tetanus data: {len(tetanus_data)} records, {len(tetanus_data.columns)} columns")
        print(f"✓ Tetanus columns: {available_columns}")
        
        return tetanus_data, data
        
    except Exception as e:
        print(f"❌ Error loading tetanus data: {e}")
        return None, None

def analyze_tetanus_prevalence(tetanus_data):
    """Analyze tetanus prevalence patterns"""
    
    print("\n" + "="*80)
    print("TETANUS PREVALENCE ANALYSIS")
    print("="*80)
    
    # Overall tetanus cases
    if 'tetanus' in tetanus_data.columns:
        total_tetanus = tetanus_data['tetanus'].sum()
        print(f"Total Tetanus Cases: {total_tetanus:,}")
        print(f"Average per record: {total_tetanus / len(tetanus_data):.1f}")
        print(f"Range: {tetanus_data['tetanus'].min()} - {tetanus_data['tetanus'].max()}")
    
    # Neonatal tetanus analysis
    if 'neonatal_tetanus' in tetanus_data.columns:
        neonatal_cases = tetanus_data['neonatal_tetanus'].sum()
        print(f"\nNeonatal Tetanus Cases: {neonatal_cases:,}")
        print(f"Average per record: {neonatal_cases / len(tetanus_data):.1f}")
        print(f"Range: {tetanus_data['neonatal_tetanus'].min()} - {tetanus_data['neonatal_tetanus'].max()}")
        
        # Calculate neonatal tetanus rate per 1000 births
        if 'estimated_lb' in tetanus_data.columns:
            total_births = tetanus_data['estimated_lb'].sum()
            if total_births > 0:
                neonatal_rate = (neonatal_cases / total_births) * 1000
                print(f"Neonatal Tetanus Rate: {neonatal_rate:.2f} per 1000 births")
    
    # Peri-neonatal tetanus analysis
    if 'peri_neonatal_tetanus' in tetanus_data.columns:
        peri_neonatal_cases = tetanus_data['peri_neonatal_tetanus'].sum()
        print(f"\nPeri-neonatal Tetanus Cases: {peri_neonatal_cases:,}")
        print(f"Average per record: {peri_neonatal_cases / len(tetanus_data):.1f}")
        print(f"Range: {tetanus_data['peri_neonatal_tetanus'].min()} - {tetanus_data['peri_neonatal_tetanus'].max()}")
    
    # Tetanus inpatient analysis
    if 'tetanus_inpatient' in tetanus_data.columns:
        inpatient_cases = tetanus_data['tetanus_inpatient'].sum()
        print(f"\nTetanus Inpatient Cases: {inpatient_cases:,}")
        print(f"Average per record: {inpatient_cases / len(tetanus_data):.1f}")
        print(f"Range: {tetanus_data['tetanus_inpatient'].min()} - {tetanus_data['tetanus_inpatient'].max()}")
    
    return {
        'total_tetanus': tetanus_data['tetanus'].sum() if 'tetanus' in tetanus_data.columns else 0,
        'neonatal_cases': tetanus_data['neonatal_tetanus'].sum() if 'neonatal_tetanus' in tetanus_data.columns else 0,
        'peri_neonatal_cases': tetanus_data['peri_neonatal_tetanus'].sum() if 'peri_neonatal_tetanus' in tetanus_data.columns else 0,
        'inpatient_cases': tetanus_data['tetanus_inpatient'].sum() if 'tetanus_inpatient' in tetanus_data.columns else 0
    }

def analyze_temporal_patterns(tetanus_data):
    """Analyze temporal patterns in tetanus data"""
    
    print("\n" + "="*60)
    print("TEMPORAL PATTERNS ANALYSIS")
    print("="*60)
    
    # Year analysis
    if 'year' in tetanus_data.columns:
        year_analysis = tetanus_data.groupby('year').agg({
            'tetanus': 'sum',
            'neonatal_tetanus': 'sum',
            'peri_neonatal_tetanus': 'sum',
            'tetanus_inpatient': 'sum'
        }).reset_index()
        
        print("Tetanus Cases by Year:")
        print("-" * 40)
        for _, row in year_analysis.iterrows():
            print(f"  {int(row['year'])}: Total={row['tetanus']:.0f}, Neonatal={row['neonatal_tetanus']:.0f}, Peri-neonatal={row['peri_neonatal_tetanus']:.0f}, Inpatient={row['tetanus_inpatient']:.0f}")
    
    # Month analysis
    if 'month' in tetanus_data.columns:
        month_analysis = tetanus_data.groupby('month').agg({
            'tetanus': 'sum',
            'neonatal_tetanus': 'sum',
            'peri_neonatal_tetanus': 'sum',
            'tetanus_inpatient': 'sum'
        }).reset_index()
        
        print(f"\nTetanus Cases by Month:")
        print("-" * 40)
        for _, row in month_analysis.iterrows():
            print(f"  {row['month']}: Total={row['tetanus']:.0f}, Neonatal={row['neonatal_tetanus']:.0f}, Peri-neonatal={row['peri_neonatal_tetanus']:.0f}, Inpatient={row['tetanus_inpatient']:.0f}")
    
    return year_analysis if 'year' in tetanus_data.columns else None, month_analysis if 'month' in tetanus_data.columns else None

def analyze_age_specific_patterns(tetanus_data):
    """Analyze age-specific tetanus patterns"""
    
    print("\n" + "="*60)
    print("AGE-SPECIFIC TETANUS PATTERNS")
    print("="*60)
    
    # Age group analysis
    age_columns = ['fic_at_1yr', 'fic_under_1yr', 'fic_above_2yrs']
    available_age_columns = [col for col in age_columns if col in tetanus_data.columns]
    
    if available_age_columns:
        print("Age Group Analysis:")
        print("-" * 30)
        for col in available_age_columns:
            age_group_name = col.replace('fic_', '').replace('_', ' ').title()
            total_cases = tetanus_data[col].sum()
            avg_cases = tetanus_data[col].mean()
            print(f"  {age_group_name}: {total_cases:.0f} total, {avg_cases:.1f} average per record")
    
    # Neonatal vs peri-neonatal comparison
    if 'neonatal_tetanus' in tetanus_data.columns and 'peri_neonatal_tetanus' in tetanus_data.columns:
        neonatal_total = tetanus_data['neonatal_tetanus'].sum()
        peri_neonatal_total = tetanus_data['peri_neonatal_tetanus'].sum()
        
        print(f"\nNeonatal vs Peri-neonatal Comparison:")
        print(f"  Neonatal tetanus: {neonatal_total:.0f} cases")
        print(f"  Peri-neonatal tetanus: {peri_neonatal_total:.0f} cases")
        print(f"  Ratio (Neonatal:Peri-neonatal): {neonatal_total/peri_neonatal_total:.2f}" if peri_neonatal_total > 0 else "  Ratio: N/A")
    
    return available_age_columns

def create_tetanus_visualization(tetanus_data, year_analysis, month_analysis):
    """Create comprehensive tetanus visualization"""
    
    print("\n" + "="*60)
    print("CREATING TETANUS VISUALIZATION")
    print("="*60)
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Tetanus Data Analysis\n(Extracted from zerodose_data.dta)', 
                 fontsize=16, fontweight='bold')
    
    # 1. Tetanus cases by type
    ax1 = axes[0, 0]
    tetanus_types = []
    tetanus_cases = []
    
    if 'tetanus' in tetanus_data.columns:
        tetanus_types.append('Total Tetanus')
        tetanus_cases.append(tetanus_data['tetanus'].sum())
    
    if 'neonatal_tetanus' in tetanus_data.columns:
        tetanus_types.append('Neonatal')
        tetanus_cases.append(tetanus_data['neonatal_tetanus'].sum())
    
    if 'peri_neonatal_tetanus' in tetanus_data.columns:
        tetanus_types.append('Peri-neonatal')
        tetanus_cases.append(tetanus_data['peri_neonatal_tetanus'].sum())
    
    if 'tetanus_inpatient' in tetanus_data.columns:
        tetanus_types.append('Inpatient')
        tetanus_cases.append(tetanus_data['tetanus_inpatient'].sum())
    
    if tetanus_types:
        colors = ['red', 'orange', 'yellow', 'green']
        bars = ax1.bar(tetanus_types, tetanus_cases, color=colors[:len(tetanus_types)], alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Number of Cases')
        ax1.set_title('Tetanus Cases by Type')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, tetanus_cases):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(tetanus_cases)*0.01,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Temporal trends
    ax2 = axes[0, 1]
    if year_analysis is not None and len(year_analysis) > 1:
        ax2.plot(year_analysis['year'], year_analysis['tetanus'], 'o-', linewidth=2, markersize=6, label='Total Tetanus')
        if 'neonatal_tetanus' in year_analysis.columns:
            ax2.plot(year_analysis['year'], year_analysis['neonatal_tetanus'], 's-', linewidth=2, markersize=6, label='Neonatal')
        if 'peri_neonatal_tetanus' in year_analysis.columns:
            ax2.plot(year_analysis['year'], year_analysis['peri_neonatal_tetanus'], '^-', linewidth=2, markersize=6, label='Peri-neonatal')
        
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Cases')
        ax2.set_title('Tetanus Trends Over Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'Insufficient temporal data', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Temporal Trends')
    
    # 3. Monthly patterns
    ax3 = axes[1, 0]
    if month_analysis is not None and len(month_analysis) > 1:
        months = month_analysis['month']
        tetanus_by_month = month_analysis['tetanus']
        
        bars = ax3.bar(range(len(months)), tetanus_by_month, alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Month')
        ax3.set_ylabel('Number of Cases')
        ax3.set_title('Tetanus Cases by Month')
        ax3.set_xticks(range(len(months)))
        ax3.set_xticklabels(months, rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, tetanus_by_month):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(tetanus_by_month)*0.01,
                    f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'Insufficient monthly data', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('Monthly Patterns')
    
    # 4. Data summary
    ax4 = axes[1, 1]
    ax4.axis('off')
    
    # Create summary text
    summary_text = f"""
TETANUS DATA SUMMARY

Dataset: {len(tetanus_data)} records
Time Period: {tetanus_data['year'].min():.0f}-{tetanus_data['year'].max():.0f}

Tetanus Cases:
"""
    
    if 'tetanus' in tetanus_data.columns:
        total_tetanus = tetanus_data['tetanus'].sum()
        summary_text += f"• Total: {total_tetanus:.0f} cases\n"
    
    if 'neonatal_tetanus' in tetanus_data.columns:
        neonatal_cases = tetanus_data['neonatal_tetanus'].sum()
        summary_text += f"• Neonatal: {neonatal_cases:.0f} cases\n"
    
    if 'peri_neonatal_tetanus' in tetanus_data.columns:
        peri_neonatal_cases = tetanus_data['peri_neonatal_tetanus'].sum()
        summary_text += f"• Peri-neonatal: {peri_neonatal_cases:.0f} cases\n"
    
    if 'tetanus_inpatient' in tetanus_data.columns:
        inpatient_cases = tetanus_data['tetanus_inpatient'].sum()
        summary_text += f"• Inpatient: {inpatient_cases:.0f} cases\n"
    
    if 'estimated_lb' in tetanus_data.columns:
        total_births = tetanus_data['estimated_lb'].sum()
        summary_text += f"\nBirths: {total_births:.0f} total\n"
        
        if 'neonatal_tetanus' in tetanus_data.columns:
            neonatal_rate = (neonatal_cases / total_births) * 1000
            summary_text += f"Neonatal Rate: {neonatal_rate:.2f} per 1000 births\n"
    
    ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=10, 
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('tetanus_data_analysis.pdf', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✓ Tetanus visualization created and saved")

def export_tetanus_analysis(tetanus_data, prevalence_stats):
    """Export tetanus analysis results"""
    
    print("\n" + "="*60)
    print("EXPORTING TETANUS ANALYSIS")
    print("="*60)
    
    # Export tetanus data to CSV
    csv_file = 'tetanus_data_analysis.csv'
    tetanus_data.to_csv(csv_file, index=False)
    print(f"✓ Tetanus data exported to: {csv_file}")
    
    # Export summary statistics
    summary_file = 'tetanus_analysis_summary.txt'
    with open(summary_file, 'w') as f:
        f.write("TETANUS DATA ANALYSIS SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Dataset: {len(tetanus_data)} records\n")
        f.write(f"Time Period: {tetanus_data['year'].min():.0f}-{tetanus_data['year'].max():.0f}\n\n")
        
        f.write("TETANUS PREVALENCE:\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total Tetanus Cases: {prevalence_stats['total_tetanus']:.0f}\n")
        f.write(f"Neonatal Tetanus Cases: {prevalence_stats['neonatal_cases']:.0f}\n")
        f.write(f"Peri-neonatal Tetanus Cases: {prevalence_stats['peri_neonatal_cases']:.0f}\n")
        f.write(f"Inpatient Tetanus Cases: {prevalence_stats['inpatient_cases']:.0f}\n")
        
        f.write("\nTETANUS RATES:\n")
        f.write("-" * 30 + "\n")
        if 'estimated_lb' in tetanus_data.columns:
            total_births = tetanus_data['estimated_lb'].sum()
            f.write(f"Total Births: {total_births:.0f}\n")
            if prevalence_stats['neonatal_cases'] > 0:
                neonatal_rate = (prevalence_stats['neonatal_cases'] / total_births) * 1000
                f.write(f"Neonatal Tetanus Rate: {neonatal_rate:.2f} per 1000 births\n")
        
        f.write("\nCOLUMN INFORMATION:\n")
        f.write("-" * 30 + "\n")
        for i, col in enumerate(tetanus_data.columns):
            dtype = tetanus_data[col].dtype
            non_null = tetanus_data[col].count()
            f.write(f"{i+1:2d}. {col:<30} | {str(dtype):<15} | {non_null:>6} non-null\n")
    
    print(f"✓ Summary exported to: {summary_file}")
    
    return csv_file, summary_file

def main():
    """Main function to run tetanus data analysis"""
    
    print("="*80)
    print("TETANUS DATA ANALYSIS")
    print("="*80)
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load tetanus data
    tetanus_data, full_data = load_tetanus_data()
    if tetanus_data is None:
        print("❌ Could not load tetanus data")
        return
    
    # Analyze tetanus prevalence
    prevalence_stats = analyze_tetanus_prevalence(tetanus_data)
    
    # Analyze temporal patterns
    year_analysis, month_analysis = analyze_temporal_patterns(tetanus_data)
    
    # Analyze age-specific patterns
    age_columns = analyze_age_specific_patterns(tetanus_data)
    
    # Create visualization
    create_tetanus_visualization(tetanus_data, year_analysis, month_analysis)
    
    # Export analysis
    csv_file, summary_file = export_tetanus_analysis(tetanus_data, prevalence_stats)
    
    print("\n" + "="*80)
    print("TETANUS DATA ANALYSIS COMPLETED")
    print("="*80)
    print("Files generated:")
    print(f"  - {csv_file}")
    print(f"  - {summary_file}")
    print("  - tetanus_data_analysis.pdf")
    print("\nKey insights:")
    print("  - Tetanus data successfully extracted and analyzed")
    print("  - Age-specific tetanus patterns identified")
    print("  - Temporal trends and seasonal patterns analyzed")
    print("  - Comprehensive tetanus epidemiology insights provided")

if __name__ == '__main__':
    main()
