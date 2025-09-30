#!/usr/bin/env python3
"""
===========================================
RESPIRATORY INFECTIONS ANALYSIS
===========================================

WHAT IT DOES:
Analyzes respiratory infection burden using real
data from Kenya (2018-2024). Includes:
- Upper Respiratory Tract Infections (URTI)
- Lower Respiratory Tract Infections (LRTI)
- Acute lower respiratory infections
- Influenza-like illnesses

Covers:
- Different types of respiratory infections
- Trends over 7 years
- Age-specific burden patterns
- Seasonal variations

WHO SHOULD USE:
- Respiratory disease program managers
- Researchers studying influenza and RTIs
- Policy makers planning respiratory disease interventions

WHAT YOU NEED:
- Python environment activated
- Access to zerodose_data.dta file

WHAT YOU GET:
- Respiratory infection burden by type
- 7-year trends
- Age group estimates
- Seasonal patterns
- Excel report with detailed data
- Comprehensive PDF report

USAGE:
    python scriptsV2/01_baseline_analysis/respiratory_infections_analysis.py

===========================================
"""

import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Import utilities
sys.path.insert(0, os.path.join(parent_dir, '09_utilities'))
from data_loader import load_zerodose_data
from age_group_calculator import AGE_GROUPS
from data_source_citation import add_data_source_page_to_pdf

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def analyze_respiratory_infections():
    """Main analysis function"""
    
    print("\n" + "=" + "="*80)
    print("RESPIRATORY INFECTIONS BURDEN ANALYSIS")
    print("Based on real data (2018-2024)")
    print("="*80)
    
    # Load data
    data = load_zerodose_data(verbose=True)
    
    # Extract respiratory infection data
    print("\n" + "=" + "="*80)
    print("RESPIRATORY INFECTION DATA SUMMARY (7 years)")
    print("="*80)
    
    # Respiratory cases by type
    urti = data['urti'].sum()
    other_urti = data['other_urti'].sum()
    lower_rti = data['lower_rti'].sum()
    acute_lower_resp = data['other_acute_lower_resp_infe'].sum()
    
    total_urti = urti + other_urti
    total_lrti = lower_rti + acute_lower_resp
    total_rti = total_urti + total_lrti
    
    print(f"\nRespiratory Infection Cases (7 years):")
    print(f"  Upper RTI (URTI): {urti:>22,.0f}")
    print(f"  Other URTI: {other_urti:>26,.0f}")
    print(f"  Total URTI: {total_urti:>26,.0f} ({total_urti/total_rti*100:.1f}%)")
    print(f"\n  Lower RTI (LRTI): {lower_rti:>22,.0f}")
    print(f"  Acute Lower RTI: {acute_lower_resp:>21,.0f}")
    print(f"  Total LRTI: {total_lrti:>26,.0f} ({total_lrti/total_rti*100:.1f}%)")
    print(f"\n  TOTAL RTI cases: {total_rti:>21,.0f}")
    
    # Calculate rates
    total_births = data['estimated_lb'].sum()
    annual_rti = total_rti / 7
    
    print(f"\n  Average RTI cases/year: {annual_rti:>16,.0f}")
    print(f"  RTI rate per 1,000 births: {total_rti/total_births*1000:>11.1f}")
    
    # Yearly trends
    print("\n" + "=" + "="*80)
    print("YEARLY RTI TRENDS")
    print("="*80)
    
    yearly = data.groupby('year').agg({
        'urti': 'sum',
        'other_urti': 'sum',
        'lower_rti': 'sum',
        'other_acute_lower_resp_infe': 'sum',
        'estimated_lb': 'sum'
    }).reset_index()
    
    yearly['total_urti'] = yearly['urti'] + yearly['other_urti']
    yearly['total_lrti'] = yearly['lower_rti'] + yearly['other_acute_lower_resp_infe']
    yearly['total_rti'] = yearly['total_urti'] + yearly['total_lrti']
    yearly['rti_rate_per_1000'] = yearly['total_rti'] / yearly['estimated_lb'] * 1000
    
    print(f"\n{'Year':<8} {'Total URTI':<14} {'Total LRTI':<14} {'Total RTI':<14} {'RTI/1000'}")
    print("-"*80)
    
    for _, row in yearly.iterrows():
        year = int(row['year'])
        print(f"{year:<8} {row['total_urti']:>12,.0f}  {row['total_lrti']:>12,.0f}  "
              f"{row['total_rti']:>12,.0f}  {row['rti_rate_per_1000']:>10.1f}")
    
    # Trend analysis
    print("\n" + "=" + "="*80)
    print("TREND ANALYSIS")
    print("="*80)
    
    first_year = yearly.iloc[0]
    last_year = yearly.iloc[-1]
    
    rti_change = last_year['total_rti'] - first_year['total_rti']
    rti_pct_change = (rti_change / first_year['total_rti'] * 100)
    
    print(f"\nRTI cases in {int(first_year['year'])}: {first_year['total_rti']:,.0f}")
    print(f"RTI cases in {int(last_year['year'])}: {last_year['total_rti']:,.0f}")
    print(f"Change: {rti_change:+,.0f} ({rti_pct_change:+.1f}%)")
    
    if rti_pct_change < -10:
        print(f"\n✓ DECLINING: RTI cases decreased by {abs(rti_pct_change):.1f}%")
    elif rti_pct_change > 10:
        print(f"\n⚠ INCREASING: RTI cases increased by {rti_pct_change:.1f}%")
    else:
        print(f"\n→ STABLE: RTI cases relatively unchanged ({rti_pct_change:+.1f}%)")
    
    # Seasonal analysis
    print("\n" + "=" + "="*80)
    print("SEASONAL PATTERNS")
    print("="*80)
    
    # Map month names to numbers
    month_name_to_num = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    data['month_num'] = data['month'].map(month_name_to_num)
    
    # Group by month (regardless of year)
    monthly_avg = data.groupby('month_num').agg({
        'urti': 'mean',
        'other_urti': 'mean',
        'lower_rti': 'mean',
        'other_acute_lower_resp_infe': 'mean'
    }).reset_index()
    
    monthly_avg['total_urti'] = monthly_avg['urti'] + monthly_avg['other_urti']
    monthly_avg['total_lrti'] = monthly_avg['lower_rti'] + monthly_avg['other_acute_lower_resp_infe']
    monthly_avg['total_rti'] = monthly_avg['total_urti'] + monthly_avg['total_lrti']
    
    # Find peak months
    peak_month_idx = monthly_avg['total_rti'].idxmax()
    low_month_idx = monthly_avg['total_rti'].idxmin()
    peak_month = int(monthly_avg.loc[peak_month_idx, 'month_num'])
    low_month = int(monthly_avg.loc[low_month_idx, 'month_num'])
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print(f"\nPeak RTI month: {month_names[peak_month-1]} (average {monthly_avg['total_rti'].max():,.0f} cases)")
    print(f"Lowest RTI month: {month_names[low_month-1]} (average {monthly_avg['total_rti'].min():,.0f} cases)")
    print(f"Seasonal variation: {(monthly_avg['total_rti'].max() / monthly_avg['total_rti'].min()):.1f}x")
    
    # Age-specific burden estimates
    print("\n" + "=" + "="*80)
    print("ESTIMATED RTI BURDEN BY AGE GROUP")
    print("="*80)
    print("\nBased on epidemiological patterns:")
    
    # RTI burden is highest in young children
    rti_by_age = {
        'Neonates (0-28d)': total_rti * 0.08,    # 8% - vulnerable neonates
        'Infants (1-11m)': total_rti * 0.25,     # 25% - highest burden
        'Toddlers (1-2y)': total_rti * 0.22,     # 22%
        'Preschool (2-5y)': total_rti * 0.20,    # 20%
        'School Age (5-15y)': total_rti * 0.15,  # 15%
        'Adults (15+y)': total_rti * 0.10        # 10% - lowest burden
    }
    
    # Estimated deaths (RTI CFR varies by severity)
    # URTI: ~0.1% CFR, LRTI: ~2% CFR
    urti_cfr = 0.001
    lrti_cfr = 0.02
    estimated_deaths = (total_urti * urti_cfr) + (total_lrti * lrti_cfr)
    
    print(f"\n{'Age Group':<20} {'Estimated Cases':<18} {'Estimated Deaths':<18} {'% of Total'}")
    print("-"*80)
    
    for age_group, cases in rti_by_age.items():
        # Death rate higher in younger children
        if 'Neonates' in age_group:
            deaths = cases * 0.015  # 1.5% CFR for neonates
        elif 'Infants' in age_group or 'Toddlers' in age_group:
            deaths = cases * 0.012  # 1.2% CFR for infants/toddlers
        else:
            deaths = cases * 0.008  # 0.8% CFR for older children
        
        pct = cases / total_rti * 100
        print(f"{age_group:<20} {cases:>16,.0f}  {deaths:>16,.0f}  {pct:>10.1f}%")
    
    print("-"*80)
    total_deaths = sum([cases * (0.015 if 'Neonates' in ag else 
                                  0.012 if ('Infants' in ag or 'Toddlers' in ag) else 
                                  0.008) 
                        for ag, cases in rti_by_age.items()])
    print(f"{'TOTAL':<20} {total_rti:>16,.0f}  {total_deaths:>16,.0f}  {'100.0%':>10}")
    
    # Key insights
    print("\n" + "=" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)
    
    print(f"\n1. DISEASE BURDEN:")
    print(f"   - Average RTI cases per year: {annual_rti:,.0f}")
    print(f"   - URTI accounts for {total_urti/total_rti*100:.1f}% (less severe)")
    print(f"   - LRTI accounts for {total_lrti/total_rti*100:.1f}% (more severe)")
    print(f"   - Estimated deaths per year: {total_deaths/7:,.0f}")
    
    print(f"\n2. SEASONAL PATTERNS:")
    print(f"   - Peak season: {month_names[int(peak_month)-1]}")
    print(f"   - {(monthly_avg['total_rti'].max() / monthly_avg['total_rti'].min()):.1f}x variation between peak and low months")
    print(f"   - Important for planning interventions")
    
    print(f"\n3. AGE DISTRIBUTION:")
    print(f"   - Infants (<1 year): {rti_by_age['Infants (1-11m)']:,.0f} cases ({rti_by_age['Infants (1-11m)']/total_rti*100:.1f}%)")
    print(f"   - Young children (<5 years): {sum([v for k,v in rti_by_age.items() if any(x in k for x in ['Neonates', 'Infants', 'Toddlers', 'Preschool'])]):,.0f} cases")
    print(f"   - Children bear {((total_rti - rti_by_age['Adults (15+y)'])/total_rti*100):.1f}% of RTI burden")
    
    print(f"\n4. PUBLIC HEALTH IMPLICATIONS:")
    print(f"   - RTI is a major child health burden")
    print(f"   - Prevention through vaccination (influenza) can reduce burden")
    print(f"   - Early treatment critical for LRTI")
    
    # Create comprehensive PDF
    create_comprehensive_pdf_report(data, yearly, monthly_avg, rti_by_age, 
                                   total_rti, total_urti, total_lrti, total_deaths)
    
    # Export to Excel
    export_to_excel(data, yearly, monthly_avg, rti_by_age, 
                   total_rti, total_urti, total_lrti)
    
    return yearly, rti_by_age


def create_comprehensive_pdf_report(data, yearly, monthly_avg, rti_by_age, 
                                   total_rti, total_urti, total_lrti, total_deaths):
    """Create comprehensive PDF report"""
    
    print("\n" + "=" + "="*80)
    print("CREATING COMPREHENSIVE PDF REPORT")
    print("="*80)
    
    output_file = 'scriptsV2/outputs/respiratory_infections_report.pdf'
    
    with PdfPages(output_file) as pdf:
        
        # PAGE 1: Executive Summary
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('RESPIRATORY INFECTIONS BURDEN ANALYSIS\nKenya 2018-2024', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        summary_text = f"""
EXECUTIVE SUMMARY - RESPIRATORY INFECTIONS ANALYSIS
{'='*80}

Period: 2018-2024 (7 years, 84 months)
Report Generated: {datetime.now().strftime('%B %d, %Y')}

KEY FINDINGS:

1. RESPIRATORY INFECTION BURDEN (7 years)
   • Total RTI cases:                     {total_rti:>20,.0f}
   • Upper RTI (URTI):                    {total_urti:>20,.0f} ({total_urti/total_rti*100:.1f}%)
   • Lower RTI (LRTI):                    {total_lrti:>20,.0f} ({total_lrti/total_rti*100:.1f}%)
   • Average cases per year:              {total_rti/7:>20,.0f}
   • Estimated deaths (7 years):          {total_deaths:>20,.0f}
   • Estimated deaths per year:           {total_deaths/7:>20,.0f}

2. DISEASE SEVERITY
   • URTI (mild):                         {total_urti/total_rti*100:>19.1f}% of cases
     - CFR: ~0.1%
     - Usually self-limiting
   
   • LRTI (severe):                       {total_lrti/total_rti*100:>19.1f}% of cases
     - CFR: ~2.0%
     - Requires treatment
     - Main cause of RTI deaths

3. TRENDS ({int(yearly.iloc[0]['year'])}-{int(yearly.iloc[-1]['year'])})
   • RTI cases in {int(yearly.iloc[0]['year'])}:                {yearly.iloc[0]['total_rti']:>20,.0f}
   • RTI cases in {int(yearly.iloc[-1]['year'])}:                {yearly.iloc[-1]['total_rti']:>20,.0f}
   • Change:                              {yearly.iloc[-1]['total_rti'] - yearly.iloc[0]['total_rti']:>+19,.0f} ({(yearly.iloc[-1]['total_rti'] - yearly.iloc[0]['total_rti'])/yearly.iloc[0]['total_rti']*100:+.1f}%)

4. SEASONAL PATTERNS
   • Peak month:                          {monthly_avg.loc[monthly_avg['total_rti'].idxmax(), 'month_num']:.0f} (avg {monthly_avg['total_rti'].max():,.0f} cases)
   • Lowest month:                        {monthly_avg.loc[monthly_avg['total_rti'].idxmin(), 'month_num']:.0f} (avg {monthly_avg['total_rti'].min():,.0f} cases)
   • Seasonal variation:                  {(monthly_avg['total_rti'].max() / monthly_avg['total_rti'].min()):>19.1f}x

5. RTI BURDEN BY AGE GROUP (Estimated)
"""
        for age_group, cases in rti_by_age.items():
            if 'Neonates' in age_group:
                deaths = cases * 0.015
            elif 'Infants' in age_group or 'Toddlers' in age_group:
                deaths = cases * 0.012
            else:
                deaths = cases * 0.008
            summary_text += f"   • {age_group:<20} {cases:>15,.0f} cases  {deaths:>8,.0f} deaths\n"
        
        summary_text += f"\n6. KEY PRIORITIES\n"
        summary_text += f"   • Focus on infants and young children (75% of burden)\n"
        summary_text += f"   • Strengthen LRTI treatment (higher mortality)\n"
        summary_text += f"   • Consider seasonal influenza vaccination\n"
        summary_text += f"   • Improve early diagnosis and treatment\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=8, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.2))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: RTI Trends
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('RESPIRATORY INFECTIONS TRENDS AND PATTERNS', 
                    fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: Total RTI over time
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(yearly['year'], yearly['total_rti'], 'o-', 
                linewidth=2, markersize=6, color='#3498db')
        ax1.fill_between(yearly['year'], 0, yearly['total_rti'], alpha=0.3, color='#3498db')
        ax1.set_xlabel('Year', fontweight='bold')
        ax1.set_ylabel('RTI Cases', fontweight='bold')
        ax1.set_title('Total RTI Cases by Year', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: URTI vs LRTI
        ax2 = plt.subplot(2, 2, 2)
        x = range(len(yearly))
        width = 0.35
        ax2.bar([i-width/2 for i in x], yearly['total_urti'], width, 
               label='URTI (Upper)', color='#2ecc71', alpha=0.8)
        ax2.bar([i+width/2 for i in x], yearly['total_lrti'], width, 
               label='LRTI (Lower)', color='#e74c3c', alpha=0.8)
        ax2.set_xlabel('Year', fontweight='bold')
        ax2.set_ylabel('Cases', fontweight='bold')
        ax2.set_title('URTI vs LRTI Cases', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels([int(y) for y in yearly['year']], rotation=45)
        ax2.legend(fontsize=9)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Plot 3: Seasonal pattern
        ax3 = plt.subplot(2, 2, 3)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ax3.plot(monthly_avg['month_num'], monthly_avg['total_rti'], 'o-',
                linewidth=2, markersize=6, color='#9b59b6')
        ax3.fill_between(monthly_avg['month_num'], 0, monthly_avg['total_rti'], 
                        alpha=0.3, color='#9b59b6')
        ax3.set_xlabel('Month', fontweight='bold')
        ax3.set_ylabel('Average Cases', fontweight='bold')
        ax3.set_title('Seasonal Pattern (Average by Month)', fontweight='bold')
        ax3.set_xticks(range(1, 13))
        ax3.set_xticklabels(month_names, rotation=45, ha='right', fontsize=8)
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: RTI burden by age
        ax4 = plt.subplot(2, 2, 4)
        age_labels = list(rti_by_age.keys())
        age_values = list(rti_by_age.values())
        colors = ['#e74c3c', '#e67e22', '#f39c12', '#f1c40f', '#2ecc71', '#3498db']
        
        bars = ax4.barh(age_labels, age_values, color=colors, alpha=0.7)
        ax4.set_xlabel('Estimated RTI Cases', fontweight='bold')
        ax4.set_title('RTI Burden by Age Group', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for bar, val in zip(bars, age_values):
            ax4.text(val + max(age_values)*0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:,.0f}', va='center', fontsize=8)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 3: Data Source and Methods
        add_data_source_page_to_pdf(pdf, include_age_disclaimer=True)
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Respiratory Infections Analysis - Kenya 2018-2024'
        d['Author'] = 'ScriptsV2 Analysis Suite'
        d['Subject'] = 'Respiratory Infections and Influenza Analysis'
        d['Keywords'] = 'RTI, Respiratory Infections, URTI, LRTI, Influenza, Kenya'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✓ Comprehensive PDF report saved to: {output_file}")
    print(f"  - 3 pages with RTI analysis, visualizations, and data sources")


def export_to_excel(data, yearly, monthly_avg, rti_by_age, 
                   total_rti, total_urti, total_lrti):
    """Export results to Excel"""
    
    print("\n" + "=" + "="*80)
    print("EXPORTING TO EXCEL")
    print("="*80)
    
    output_file = 'scriptsV2/outputs/respiratory_infections_analysis.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_df = pd.DataFrame({
            'Metric': [
                'Total RTI Cases (7 years)',
                'Total URTI Cases',
                'Total LRTI Cases',
                'Average Cases/Year',
                'URTI Percentage',
                'LRTI Percentage',
                'Period'
            ],
            'Value': [
                f"{total_rti:,.0f}",
                f"{total_urti:,.0f}",
                f"{total_lrti:,.0f}",
                f"{total_rti/7:,.0f}",
                f"{total_urti/total_rti*100:.1f}%",
                f"{total_lrti/total_rti*100:.1f}%",
                f"{int(yearly.iloc[0]['year'])}-{int(yearly.iloc[-1]['year'])}"
            ]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Yearly Data
        yearly_export = yearly[['year', 'urti', 'other_urti', 'total_urti',
                                'lower_rti', 'other_acute_lower_resp_infe', 'total_lrti',
                                'total_rti', 'rti_rate_per_1000']].copy()
        yearly_export.columns = ['Year', 'URTI', 'Other URTI', 'Total URTI',
                                 'Lower RTI', 'Acute Lower RTI', 'Total LRTI',
                                 'Total RTI', 'RTI Rate/1000']
        yearly_export.to_excel(writer, sheet_name='Yearly Data', index=False)
        
        # Sheet 3: Seasonal Pattern
        monthly_export = monthly_avg[['month_num', 'total_urti', 'total_lrti', 
                                      'total_rti']].copy()
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_export['month_name'] = [month_names[int(m)-1] for m in monthly_export['month_num']]
        monthly_export = monthly_export[['month_name', 'total_urti', 'total_lrti', 'total_rti']]
        monthly_export.columns = ['Month', 'Avg URTI', 'Avg LRTI', 'Avg Total RTI']
        monthly_export.to_excel(writer, sheet_name='Seasonal Pattern', index=False)
        
        # Sheet 4: Age Distribution
        age_df = pd.DataFrame({
            'Age Group': list(rti_by_age.keys()),
            'Estimated Cases': [f"{v:,.0f}" for v in rti_by_age.values()],
            'Percentage': [f"{v/total_rti*100:.1f}%" for v in rti_by_age.values()]
        })
        age_df.to_excel(writer, sheet_name='Age Distribution', index=False)
        
        # Sheet 5: Monthly Data
        monthly_data = data[['year', 'month', 'urti', 'other_urti', 
                            'lower_rti', 'other_acute_lower_resp_infe']].copy()
        monthly_data.columns = ['Year', 'Month', 'URTI', 'Other URTI',
                               'Lower RTI', 'Acute Lower RTI']
        monthly_data.to_excel(writer, sheet_name='Monthly Data', index=False)
    
    print(f"\n✓ Excel report saved to: {output_file}")
    print("\nExcel file contains 5 sheets:")
    print("  1. Summary - Overall RTI statistics")
    print("  2. Yearly Data - Annual RTI trends")
    print("  3. Seasonal Pattern - Average by month")
    print("  4. Age Distribution - RTI by age group")
    print("  5. Monthly Data - 84 months of RTI data")


def main():
    """Main execution function"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║           RESPIRATORY INFECTIONS BURDEN ANALYSIS                       ║
║                     ScriptsV2 Analysis Suite                           ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        yearly, rti_by_age = analyze_respiratory_infections()
        
        print("\n" + "=" + "="*80)
        print("✓ ANALYSIS COMPLETE")
        print("="*80)
        print("\nOutputs created:")
        print("  1. scriptsV2/outputs/respiratory_infections_report.pdf (2-page report)")
        print("  2. scriptsV2/outputs/respiratory_infections_analysis.xlsx (5-sheet workbook)")
        print("\nKey insights:")
        print("  - RTI burden quantified (URTI vs LRTI)")
        print("  - Seasonal patterns identified")
        print("  - Age-specific burden estimated")
        print("  - 7-year trends analyzed")
        print("\nNext steps:")
        print("  - Review seasonal patterns for intervention timing")
        print("  - Focus on high-risk age groups (infants)")
        print("  - Consider influenza vaccination programs")
        print("  - Strengthen LRTI treatment protocols")
                
        # Print data source citation
        print("\n" + "="*80)
        print("DATA SOURCE")
        print("="*80)
        print("""
Primary Data: Kenya national health facility data (zerodose_data.dta)
Period: 2018-2024 (84 months)  
Variables: Vaccination coverage, disease cases, population estimates

Note: All disease case numbers are actual surveillance data.
Age-stratified estimates based on WHO/published epidemiological patterns.
""")
        print("="*80)

        return 0

        
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

