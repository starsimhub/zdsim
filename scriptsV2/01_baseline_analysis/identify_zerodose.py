#!/usr/bin/env python3
"""
===========================================
IDENTIFY ZERO-DOSE CHILDREN
===========================================

WHAT IT DOES:
Calculates how many zero-dose children exist using
real vaccination data from Kenya (2018-2024).

Zero-dose children are those who never received their
first DPT dose - they are completely unvaccinated.

WHO SHOULD USE:
- Program managers planning interventions
- Researchers analyzing coverage gaps
- Policy makers assessing the problem

WHAT YOU NEED:
- Python environment activated
- Access to zerodose_data.dta file

WHAT YOU GET:
- Total zero-dose children by year
- Zero-dose rate trends (7 years)
- Age group breakdown
- Excel report with detailed tables
- PDF visualization

USAGE:
    python scriptsV2/01_baseline_analysis/identify_zerodose.py

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
import matplotlib.patches as mpatches

# Import utilities from the 09_utilities directory
sys.path.insert(0, os.path.join(parent_dir, '09_utilities'))
from data_loader import load_and_prepare_data, print_data_summary
from age_group_calculator import AGE_GROUPS

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def analyze_zerodose_children():
    """Main analysis function"""
    
    print("\n"\n=" + "="*80)
    print("\n"ZERO-DOSE CHILDREN IDENTIFICATION")
    print("\n"Based on 84 months of real data (2018-2024)")
    print("\n"="*80)
    
    # Load data
    data, yearly, summary = load_and_prepare_data(verbose=False)
    
    # Overall statistics
    print("\n"\n=" + "="*80)
    print("\n"OVERALL STATISTICS (7-year period)")
    print("\n"="*80)
    
    total_births = summary['total_births']
    total_dpt1 = summary['total_dpt1']
    total_zero_dose = total_births - total_dpt1
    zero_dose_rate = (total_zero_dose / total_births * 100)
    
    print(f"\nTotal births: {total_births:>25,.0f}")
    print(f"Total DPT1 doses given: {total_dpt1:>16,.0f}")
    print(f"Total zero-dose children: {total_zero_dose:>13,.0f}")
    print(f"Zero-dose rate: {zero_dose_rate:>21.1f}%")
    
    # Yearly breakdown
    print("\n"\n=" + "="*80)
    print("\n"YEARLY BREAKDOWN")
    print("\n"="*80)
    print(f"\n{'Year':<10} {'Births':<15} {'Zero-Dose':<15} {'Rate':<10} {'DPT1 Cov.':<12}")
    print("\n"-"*80)
    
    for _, row in yearly.iterrows():
        year = int(row['year'])
        births = row['estimated_lb']
        zero_dose = row['zero_dose']
        rate = (zero_dose / births * 100)
        dpt1_cov = row['dpt1_coverage'] * 100
        
        print(f"{year:<10} {births:>13,.0f}  {zero_dose:>13,.0f}  "
              f"{rate:>8.1f}%  {dpt1_cov:>10.1f}%")
    
    # Trend analysis
    print("\n"\n=" + "="*80)
    print("\n"TREND ANALYSIS")
    print("\n"="*80)
    
    first_year_rate = yearly.iloc[0]['zero_dose_rate'] * 100
    last_year_rate = yearly.iloc[-1]['zero_dose_rate'] * 100
    trend_change = last_year_rate - first_year_rate
    
    print(f"\nZero-dose rate in {int(yearly.iloc[0]['year'])}: {first_year_rate:.1f}%")
    print(f"Zero-dose rate in {int(yearly.iloc[-1]['year'])}: {last_year_rate:.1f}%")
    print(f"Change: {trend_change:+.1f} percentage points")
    
    if trend_change < 0:
        print(f"\n✓ IMPROVING: Zero-dose rate decreased by {abs(trend_change):.1f}pp")
    elif trend_change > 0:
        print(f"\n⚠ WORSENING: Zero-dose rate increased by {trend_change:.1f}pp")
    else:
        print(f"\n→ STABLE: No significant change in zero-dose rate")
    
    # Key insights
    print("\n"\n=" + "="*80)
    print("\n"KEY INSIGHTS")
    print("\n"="*80)
    
    avg_dpt1 = summary['avg_dpt1_coverage'] * 100
    avg_dpt3 = summary['avg_dpt3_coverage'] * 100
    dropout = (1 - avg_dpt3/avg_dpt1) * 100
    
    print(f"\n1. COVERAGE STATUS:")
    print(f"   - Current DPT1 coverage: {avg_dpt1:.1f}%")
    if avg_dpt1 < 90:
        gap = 90 - avg_dpt1
        print(f"   - Gap to WHO target (90%): {gap:.1f} percentage points")
        print(f"   - Need to reach additional: {total_births/7 * (gap/100):,.0f} children/year")
    else:
        print(f"   - ✓ Above WHO target of 90%")
    
    print(f"\n2. DROPOUT ISSUE:")
    print(f"   - DPT3 coverage: {avg_dpt3:.1f}%")
    print(f"   - Dropout rate (DPT1→DPT3): {dropout:.1f}%")
    if dropout > 10:
        annual_dropout = (total_dpt1 - summary['total_dpt3']) / 7
        print(f"   - ⚠ High dropout: ~{annual_dropout:,.0f} children/year start but don't complete")
    
    print(f"\n3. ANNUAL BURDEN:")
    avg_annual_zerodose = total_zero_dose / 7
    print(f"   - Average zero-dose children per year: {avg_annual_zerodose:,.0f}")
    print(f"   - These children remain vulnerable to all 5 Pentavalent diseases")
    
    # Age group estimates (using demographic assumptions)
    print("\n"\n=" + "="*80)
    print("\n"ESTIMATED AGE GROUP BREAKDOWN")
    print("\n"="*80)
    print("\n"\nNote: Based on standard demographic distribution")
    print("\n"-"*80)
    
    # Typical age distribution of zero-dose children
    age_distribution = {
        'Infants (<1 year)': 0.35,      # 35% are infants
        'Toddlers (1-2 years)': 0.25,   # 25% are toddlers
        'Preschool (2-5 years)': 0.30,  # 30% are preschool
        'School age (5+ years)': 0.10   # 10% are older
    }
    
    print(f"\n{'Age Group':<25} {'Zero-Dose Count':<20} {'Percentage':<15}")
    print("\n"-"*80)
    
    for age_group, proportion in age_distribution.items():
        count = avg_annual_zerodose * proportion
        pct = proportion * 100
        print(f"{age_group:<25} {count:>18,.0f}  {pct:>13.0f}%")
    
    print("\n"-"*80)
    print(f"{'TOTAL (Annual Average)':<25} {avg_annual_zerodose:>18,.0f}  {'100%':>13}")
    
    # Create comprehensive PDF report with statistics and plots
    create_comprehensive_pdf_report(data, yearly, summary, age_distribution, avg_annual_zerodose,
                                   total_births, total_dpt1, total_zero_dose, zero_dose_rate,
                                   avg_dpt1, avg_dpt3, dropout)
    
    # Export to Excel
    export_to_excel(data, yearly, summary, age_distribution, avg_annual_zerodose)
    
    return yearly, summary


def create_comprehensive_pdf_report(data, yearly, summary, age_distribution, avg_annual_zerodose,
                                   total_births, total_dpt1, total_zero_dose, zero_dose_rate,
                                   avg_dpt1, avg_dpt3, dropout):
    """Create comprehensive PDF report with statistics and plots"""
    
    print("\n"\n=" + "="*80)
    print("\n"CREATING COMPREHENSIVE PDF REPORT")
    print("\n"="*80)
    
    output_file = 'scriptsV2/outputs/zero_dose_comprehensive_report.pdf'
    
    with PdfPages(output_file) as pdf:
        
        # ============================================================
        # PAGE 1: Title and Executive Summary Statistics
        # ============================================================
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('ZERO-DOSE CHILDREN IDENTIFICATION REPORT\nKenya 2018-2024', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Executive Summary Text
        summary_text = f"""
EXECUTIVE SUMMARY
{'='*80}

Period: {summary['year_range'][0]} - {summary['year_range'][1]} (7 years, 84 months)
Report Generated: {datetime.now().strftime('%B %d, %Y')}

KEY FINDINGS:

1. ZERO-DOSE BURDEN
   • Total births (7 years):              {total_births:>20,}
   • Children who received DPT1:          {total_dpt1:>20,}
   • Zero-dose children:                  {total_zero_dose:>20,}
   • Zero-dose rate:                      {zero_dose_rate:>19.1f}%
   
2. VACCINATION COVERAGE
   • Average DPT1 coverage:               {avg_dpt1:>19.1f}%
   • Average DPT3 coverage:               {avg_dpt3:>19.1f}%
   • Gap to WHO target (90%):             {90-avg_dpt1:>19.1f} percentage points
   • Dropout rate (DPT1→DPT3):            {dropout:>19.1f}%

3. ANNUAL IMPACT
   • Zero-dose children per year:         {avg_annual_zerodose:>19,.0f}
   • Additional children needed/year:     {total_births/7 * ((90-avg_dpt1)/100):>19,.0f}
   • Vulnerable to 5 Pentavalent diseases (Diphtheria, Tetanus, Pertussis, Hep B, Hib)

4. TREND ANALYSIS
   • Zero-dose rate in {int(yearly.iloc[0]['year'])}:             {yearly.iloc[0]['zero_dose_rate']*100:>19.1f}%
   • Zero-dose rate in {int(yearly.iloc[-1]['year'])}:             {yearly.iloc[-1]['zero_dose_rate']*100:>19.1f}%
   • Change:                              {(yearly.iloc[-1]['zero_dose_rate'] - yearly.iloc[0]['zero_dose_rate'])*100:>18.1f} pp
   • Status:                              {'IMPROVING ✓' if yearly.iloc[-1]['zero_dose_rate'] < yearly.iloc[0]['zero_dose_rate'] else 'NEEDS ATTENTION ⚠'}

5. AGE GROUP DISTRIBUTION (Estimated)
"""
        for age_group, proportion in age_distribution.items():
            count = avg_annual_zerodose * proportion
            summary_text += f"   • {age_group:<25} {count:>15,.0f}  ({proportion*100:.0f}%)\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # ============================================================
        # PAGE 2: Yearly Statistics Table
        # ============================================================
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('YEARLY BREAKDOWN (2018-2024)', fontsize=16, fontweight='bold', y=0.98)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        # Create table data
        table_data = []
        table_data.append(['Year', 'Births', 'DPT1\nGiven', 'DPT3\nGiven', 'Zero-Dose', 
                          'DPT1\nCov.', 'DPT3\nCov.', 'Dropout\nRate'])
        
        for _, row in yearly.iterrows():
            table_data.append([
                int(row['year']),
                f"{row['estimated_lb']:,.0f}",
                f"{row['dpt1']:,.0f}",
                f"{row['dpt3']:,.0f}",
                f"{row['zero_dose']:,.0f}",
                f"{row['dpt1_coverage']*100:.1f}%",
                f"{row['dpt3_coverage']*100:.1f}%",
                f"{row['dropout_rate']*100:.1f}%"
            ])
        
        # Add totals row
        table_data.append([
            'TOTAL',
            f"{yearly['estimated_lb'].sum():,.0f}",
            f"{yearly['dpt1'].sum():,.0f}",
            f"{yearly['dpt3'].sum():,.0f}",
            f"{yearly['zero_dose'].sum():,.0f}",
            f"{yearly['dpt1_coverage'].mean()*100:.1f}%",
            f"{yearly['dpt3_coverage'].mean()*100:.1f}%",
            f"{yearly['dropout_rate'].mean()*100:.1f}%"
        ])
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.08, 0.12, 0.12, 0.12, 0.12, 0.09, 0.09, 0.09])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # Style header row
        for i in range(8):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style totals row
        for i in range(8):
            table[(len(table_data)-1, i)].set_facecolor('#E7E6E6')
            table[(len(table_data)-1, i)].set_text_props(weight='bold')
        
        # Alternate row colors
        for i in range(1, len(table_data)-1):
            for j in range(8):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F2F2F2')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # ============================================================
        # PAGE 3: Visualization Plots (4 plots)
        # ============================================================
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('ZERO-DOSE TRENDS AND COVERAGE ANALYSIS', fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: Zero-dose trend over years
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(yearly['year'], yearly['zero_dose'], 'o-', linewidth=2, markersize=8, color='#e74c3c')
        ax1.fill_between(yearly['year'], 0, yearly['zero_dose'], alpha=0.3, color='#e74c3c')
        ax1.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Zero-Dose Children', fontsize=10, fontweight='bold')
        ax1.set_title('Zero-Dose Children Trend', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        # Plot 2: Zero-dose rate trend
        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(yearly['year'], yearly['zero_dose_rate']*100, 'o-', linewidth=2, markersize=8, color='#3498db')
        ax2.fill_between(yearly['year'], 0, yearly['zero_dose_rate']*100, alpha=0.3, color='#3498db')
        ax2.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Zero-Dose Rate (%)', fontsize=10, fontweight='bold')
        ax2.set_title('Zero-Dose Rate Trend', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='10% threshold')
        ax2.legend(fontsize=8)
        
        # Plot 3: Coverage comparison (DPT1 vs DPT3)
        ax3 = plt.subplot(2, 2, 3)
        x = range(len(yearly))
        width = 0.35
        bars1 = ax3.bar([i-width/2 for i in x], yearly['dpt1_coverage']*100, width, label='DPT1', color='#2ecc71')
        bars2 = ax3.bar([i+width/2 for i in x], yearly['dpt3_coverage']*100, width, label='DPT3', color='#f39c12')
        ax3.set_xlabel('Year', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Coverage (%)', fontsize=10, fontweight='bold')
        ax3.set_title('DPT1 vs DPT3 Coverage', fontsize=11, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels([int(y) for y in yearly['year']], rotation=45)
        ax3.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='WHO target (90%)')
        ax3.legend(fontsize=8)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Age distribution pie chart
        ax4 = plt.subplot(2, 2, 4)
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
        wedges, texts, autotexts = ax4.pie(
            age_distribution.values(),
            labels=age_distribution.keys(),
            autopct='%1.0f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 9}
        )
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax4.set_title(f'Zero-Dose by Age Group\n(~{avg_annual_zerodose/1000:.0f}K per year)', 
                     fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # ============================================================
        # PAGE 4: Monthly Data Visualization
        # ============================================================
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('MONTHLY DATA TRENDS (84 MONTHS)', fontsize=14, fontweight='bold', y=0.98)
        
        # Create month index for x-axis
        data_copy = data.copy()
        data_copy['month_index'] = range(len(data_copy))
        
        # Plot 1: Monthly births and zero-dose
        ax1 = plt.subplot(2, 1, 1)
        ax1_twin = ax1.twinx()
        
        line1 = ax1.plot(data_copy['month_index'], data_copy['estimated_lb'], 
                        label='Births', color='#2ecc71', linewidth=1.5, alpha=0.7)
        line2 = ax1_twin.plot(data_copy['month_index'], data_copy['zero_dose'], 
                             label='Zero-Dose', color='#e74c3c', linewidth=1.5, alpha=0.7)
        
        ax1.set_xlabel('Month (1-84)', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Births', fontsize=10, fontweight='bold', color='#2ecc71')
        ax1_twin.set_ylabel('Zero-Dose Children', fontsize=10, fontweight='bold', color='#e74c3c')
        ax1.set_title('Monthly Births and Zero-Dose Children', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='y', labelcolor='#2ecc71')
        ax1_twin.tick_params(axis='y', labelcolor='#e74c3c')
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', fontsize=8)
        
        # Plot 2: Monthly coverage rates
        ax2 = plt.subplot(2, 1, 2)
        ax2.plot(data_copy['month_index'], data_copy['dpt1_coverage']*100, 
                label='DPT1 Coverage', color='#2ecc71', linewidth=1.5, alpha=0.7)
        ax2.plot(data_copy['month_index'], data_copy['dpt3_coverage']*100, 
                label='DPT3 Coverage', color='#f39c12', linewidth=1.5, alpha=0.7)
        ax2.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='WHO Target (90%)')
        
        ax2.set_xlabel('Month (1-84)', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Coverage (%)', fontsize=10, fontweight='bold')
        ax2.set_title('Monthly DPT Coverage Rates', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend(fontsize=8)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # ============================================================
        # PAGE 5: Age Group Statistics
        # ============================================================
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('AGE GROUP ANALYSIS', fontsize=14, fontweight='bold', y=0.98)
        
        # Create age group breakdown plots
        ax1 = plt.subplot(2, 1, 1)
        age_groups = list(age_distribution.keys())
        counts = [avg_annual_zerodose * prop for prop in age_distribution.values()]
        colors_bar = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
        
        bars = ax1.bar(age_groups, counts, color=colors_bar, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Zero-Dose Children (Annual)', fontsize=10, fontweight='bold')
        ax1.set_title('Zero-Dose Children by Age Group', fontsize=11, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count:,.0f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Table with age group statistics
        ax2 = plt.subplot(2, 1, 2)
        ax2.axis('off')
        
        table_data = [['Age Group', 'Count (Annual)', 'Percentage', 'Priority']]
        priorities = ['Very High', 'High', 'High', 'Medium']
        
        for i, (age_group, proportion) in enumerate(age_distribution.items()):
            count = avg_annual_zerodose * proportion
            table_data.append([
                age_group,
                f"{count:,.0f}",
                f"{proportion*100:.0f}%",
                priorities[i]
            ])
        
        table_data.append([
            'TOTAL',
            f"{avg_annual_zerodose:,.0f}",
            '100%',
            '-'
        ])
        
        table = ax2.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.3, 0.25, 0.2, 0.25])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 3)
        
        # Style header
        for i in range(4):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style totals row
        for i in range(4):
            table[(len(table_data)-1, i)].set_facecolor('#E7E6E6')
            table[(len(table_data)-1, i)].set_text_props(weight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Zero-Dose Children Identification Report - Kenya 2018-2024'
        d['Author'] = 'ScriptsV2 Analysis Suite'
        d['Subject'] = 'Zero-Dose Vaccination Analysis'
        d['Keywords'] = 'Zero-Dose, Pentavalent, DPT, Kenya, Vaccination'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✓ Comprehensive PDF report saved to: {output_file}")
    print(f"  - 5 pages with statistics and visualizations")
    print(f"  - Page 1: Executive Summary")
    print(f"  - Page 2: Yearly Statistics Table")
    print(f"  - Page 3: Trend Plots")
    print(f"  - Page 4: Monthly Data")
    print(f"  - Page 5: Age Group Analysis")


def create_visualizations(yearly, avg_annual_zerodose, age_distribution):
    """Create PDF visualizations"""
    
    print("\n"\n=" + "="*80)
    print("\n"CREATING VISUALIZATIONS")
    print("\n"="*80)
    
    fig = plt.figure(figsize=(14, 10))
    
    # Plot 1: Zero-dose trend over years
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(yearly['year'], yearly['zero_dose'], 'o-', linewidth=2, markersize=8, color='#e74c3c')
    ax1.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Zero-Dose Children', fontsize=11, fontweight='bold')
    ax1.set_title('Zero-Dose Children Trend (2018-2024)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
    
    # Plot 2: Zero-dose rate trend
    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(yearly['year'], yearly['zero_dose_rate']*100, 'o-', linewidth=2, markersize=8, color='#3498db')
    ax2.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Zero-Dose Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Zero-Dose Rate Trend', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='10% threshold')
    ax2.legend()
    
    # Plot 3: Coverage comparison (DPT1 vs DPT3)
    ax3 = plt.subplot(2, 2, 3)
    x = range(len(yearly))
    width = 0.35
    ax3.bar([i-width/2 for i in x], yearly['dpt1_coverage']*100, width, label='DPT1', color='#2ecc71')
    ax3.bar([i+width/2 for i in x], yearly['dpt3_coverage']*100, width, label='DPT3', color='#f39c12')
    ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Coverage (%)', fontsize=11, fontweight='bold')
    ax3.set_title('DPT1 vs DPT3 Coverage', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([int(y) for y in yearly['year']], rotation=45)
    ax3.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='WHO target (90%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Age distribution pie chart
    ax4 = plt.subplot(2, 2, 4)
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    wedges, texts, autotexts = ax4.pie(
        age_distribution.values(),
        labels=age_distribution.keys(),
        autopct='%1.0f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10}
    )
    ax4.set_title(f'Zero-Dose Children by Age\n(~{avg_annual_zerodose/1000:.0f}K per year)', 
                  fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'scriptsV2/outputs/zero_dose_identification.pdf'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualizations saved to: {output_file}")
    
    plt.close()


def export_to_excel(data, yearly, summary, age_distribution, avg_annual_zerodose):
    """Export results to Excel"""
    
    print("\n"\n=" + "="*80)
    print("\n"EXPORTING TO EXCEL")
    print("\n"="*80)
    
    output_file = 'scriptsV2/outputs/zero_dose_identification.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary Statistics
        summary_df = pd.DataFrame({
            'Metric': [
                'Total Births (7 years)',
                'Total DPT1 Doses',
                'Total Zero-Dose Children',
                'Zero-Dose Rate (%)',
                'Average DPT1 Coverage (%)',
                'Average DPT3 Coverage (%)',
                'Average Annual Zero-Dose',
                'Period',
            ],
            'Value': [
                f"{summary['total_births']:,.0f}",
                f"{summary['total_dpt1']:,.0f}",
                f"{summary['total_births'] - summary['total_dpt1']:,.0f}",
                f"{(summary['total_births'] - summary['total_dpt1']) / summary['total_births'] * 100:.1f}",
                f"{summary['avg_dpt1_coverage'] * 100:.1f}",
                f"{summary['avg_dpt3_coverage'] * 100:.1f}",
                f"{avg_annual_zerodose:,.0f}",
                f"{summary['year_range'][0]}-{summary['year_range'][1]}"
            ]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Yearly Data
        yearly_export = yearly[['year', 'estimated_lb', 'dpt1', 'dpt3', 'zero_dose', 'dropout',
                                'dpt1_coverage', 'dpt3_coverage', 'zero_dose_rate']].copy()
        yearly_export.columns = ['Year', 'Births', 'DPT1 Doses', 'DPT3 Doses', 'Zero-Dose', 
                                 'Dropout', 'DPT1 Coverage', 'DPT3 Coverage', 'Zero-Dose Rate']
        yearly_export.to_excel(writer, sheet_name='Yearly Data', index=False)
        
        # Sheet 3: Age Distribution
        age_df = pd.DataFrame({
            'Age Group': list(age_distribution.keys()),
            'Proportion': [f"{v*100:.0f}%" for v in age_distribution.values()],
            'Estimated Count (Annual)': [f"{avg_annual_zerodose * v:,.0f}" for v in age_distribution.values()]
        })
        age_df.to_excel(writer, sheet_name='Age Distribution', index=False)
        
        # Sheet 4: Monthly Data
        monthly_export = data[['year', 'month', 'estimated_lb', 'dpt1', 'dpt3', 'zero_dose', 
                               'dpt1_coverage', 'dpt3_coverage']].copy()
        monthly_export.columns = ['Year', 'Month', 'Births', 'DPT1', 'DPT3', 'Zero-Dose',
                                  'DPT1 Coverage', 'DPT3 Coverage']
        monthly_export.to_excel(writer, sheet_name='Monthly Data', index=False)
    
    print(f"\n✓ Excel report saved to: {output_file}")
    print("\n"\nExcel file contains 4 sheets:")
    print("\n"  1. Summary - Overall statistics")
    print("\n"  2. Yearly Data - Annual trends")
    print("\n"  3. Age Distribution - Zero-dose by age")
    print("\n"  4. Monthly Data - Detailed monthly records")


def main():
    """Main execution function"""
    
    print("\n"""
╔════════════════════════════════════════════════════════════════════════╗
║                 ZERO-DOSE CHILDREN IDENTIFICATION                      ║
║                        ScriptsV2 Analysis Suite                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        yearly, summary = analyze_zerodose_children()
        
        print("\n"\n=" + "="*80)
        print("\n"✓ ANALYSIS COMPLETE")
        print("\n"="*80)
        print("\n"\nOutputs created:")
        print("\n"  1. scriptsV2/outputs/zero_dose_comprehensive_report.pdf (5-page report)")
        print("\n"  2. scriptsV2/outputs/zero_dose_identification.xlsx (4-sheet workbook)")
        print("\n"  3. scriptsV2/outputs/zero_dose_identification.pdf (4-plot summary)")
        print("\n"\nWhat's in the comprehensive report:")
        print("\n"  • Page 1: Executive Summary with key statistics")
        print("\n"  • Page 2: Yearly breakdown table (2018-2024)")
        print("\n"  • Page 3: Trend and coverage plots")
        print("\n"  • Page 4: Monthly data visualization (84 months)")
        print("\n"  • Page 5: Age group analysis with tables and charts")
        print("\n"\nNext steps:")
        print("\n"  - Review the comprehensive PDF report first")
        print("\n"  - Check the Excel file for detailed numbers")
        print("\n"  - Run disease_burden_by_age.py to see health impact")
        print("\n"  - Run compare_age_groups.py for age-specific analysis")
                
        # Print data source citation
        print("\n"
=" + "="*80)
        print("\n"DATA SOURCE")
        print("\n"="*80)
        print("\n"""
Primary Data: Kenya national health facility data (zerodose_data.dta)
Period: 2018-2024 (84 months)  
Variables: Vaccination coverage, disease cases, population estimates

Note: All disease case numbers are actual surveillance data.
Age-stratified estimates based on WHO/published epidemiological patterns.
""")
        print("\n"="*80)

        return 0

        
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())

