#!/usr/bin/env python3
"""
===========================================
COMPREHENSIVE TRENDS OVER TIME
===========================================

WHAT IT DOES:
Analyzes all key metrics over 7 years (2018-2024):
- Zero-dose children trends
- Vaccination coverage (DPT1/2/3)
- Disease burden trends
- Dropout patterns

Combines insights from all baseline analyses into
one comprehensive trend report.

WHO SHOULD USE:
- Program managers monitoring progress
- Researchers analyzing long-term patterns
- Policy makers reviewing program performance

WHAT YOU NEED:
- Python environment activated
- Access to zerodose_data.dta file

WHAT YOU GET:
- Comprehensive trend analysis (7 years)
- All metrics in one report
- Trend direction indicators
- Excel report with all data
- Multi-page PDF with visualizations

USAGE:
    python scriptsV2/01_baseline_analysis/trends_over_time.py

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
from scipy import stats

# Import utilities
sys.path.insert(0, os.path.join(parent_dir, '09_utilities'))
from data_loader import load_and_prepare_data

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def analyze_comprehensive_trends():
    """Main analysis function"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE TRENDS ANALYSIS")
    print("7-Year Trends (2018-2024)")
    print("="*80)
    
    # Load data
    data, yearly, summary = load_and_prepare_data(verbose=True)
    
    # Calculate additional metrics
    yearly['dpt2_coverage'] = yearly['dpt2'] / yearly['estimated_lb']
    yearly['zero_dose_rate'] = yearly['zero_dose'] / yearly['estimated_lb']
    
    # Trend analysis for each metric
    print("\n" + "="*80)
    print("TREND ANALYSIS SUMMARY")
    print("="*80)
    
    metrics = {
        'Zero-dose rate': yearly['zero_dose_rate'].values * 100,
        'DPT1 coverage': yearly['dpt1_coverage'].values * 100,
        'DPT2 coverage': yearly['dpt2_coverage'].values * 100,
        'DPT3 coverage': yearly['dpt3_coverage'].values * 100,
        'Dropout rate': yearly['dropout_rate'].values * 100,
        'Tetanus cases': yearly['tetanus'].values,
        'Diphtheria cases': yearly['diphtheria'].values,
        'Hepatitis B cases': yearly['hepatitisb_positive'].values,
        'Pneumonia cases': yearly['pneumonia'].values,
    }
    
    trends = {}
    print(f"\n{'Metric':<25} {'2018':<12} {'2024':<12} {'Change':<12} {'Trend'}")
    print("-"*80)
    
    for metric_name, values in metrics.items():
        start_val = values[0]
        end_val = values[-1]
        change = end_val - start_val
        pct_change = (change / start_val * 100) if start_val != 0 else 0
        
        # Linear regression for trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        if p_value < 0.05:  # Significant trend
            if slope > 0:
                trend = "↑ Increasing"
            else:
                trend = "↓ Decreasing"
        else:
            trend = "→ Stable"
        
        trends[metric_name] = {
            'start': start_val,
            'end': end_val,
            'change': change,
            'pct_change': pct_change,
            'slope': slope,
            'p_value': p_value,
            'trend': trend
        }
        
        if 'rate' in metric_name.lower() or 'coverage' in metric_name.lower():
            print(f"{metric_name:<25} {start_val:>10.1f}%  {end_val:>10.1f}%  "
                  f"{change:>+9.1f}pp  {trend}")
        else:
            print(f"{metric_name:<25} {start_val:>10,.0f}  {end_val:>10,.0f}  "
                  f"{change:>+11,.0f}  {trend}")
    
    # Key findings
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    print("\n1. VACCINATION COVERAGE TRENDS:")
    dpt3_trend = trends['DPT3 coverage']
    if dpt3_trend['change'] > 2:
        print(f"   ✓ IMPROVING: DPT3 coverage increased by {dpt3_trend['change']:.1f}pp")
    elif dpt3_trend['change'] < -2:
        print(f"   ⚠ DECLINING: DPT3 coverage decreased by {abs(dpt3_trend['change']):.1f}pp")
    else:
        print(f"   → STABLE: DPT3 coverage relatively unchanged ({dpt3_trend['change']:+.1f}pp)")
    
    print("\n2. ZERO-DOSE TRENDS:")
    zd_trend = trends['Zero-dose rate']
    if zd_trend['change'] < -2:
        print(f"   ✓ IMPROVING: Zero-dose rate decreased by {abs(zd_trend['change']):.1f}pp")
    elif zd_trend['change'] > 2:
        print(f"   ⚠ WORSENING: Zero-dose rate increased by {zd_trend['change']:.1f}pp")
    else:
        print(f"   → STABLE: Zero-dose rate relatively unchanged ({zd_trend['change']:+.1f}pp)")
    
    print("\n3. DISEASE BURDEN TRENDS:")
    tetanus_trend = trends['Tetanus cases']
    if tetanus_trend['pct_change'] < -10:
        print(f"   ✓ DECLINING: Tetanus cases decreased by {abs(tetanus_trend['pct_change']):.1f}%")
    elif tetanus_trend['pct_change'] > 10:
        print(f"   ⚠ INCREASING: Tetanus cases increased by {tetanus_trend['pct_change']:.1f}%")
    else:
        print(f"   → STABLE: Tetanus cases relatively unchanged ({tetanus_trend['pct_change']:+.1f}%)")
    
    print("\n4. DROPOUT PATTERNS:")
    dropout_trend = trends['Dropout rate']
    avg_dropout = yearly['dropout_rate'].mean() * 100
    print(f"   Average dropout rate: {avg_dropout:.1f}%")
    if avg_dropout > 15:
        print(f"   ⚠ HIGH DROPOUT: More than 15% of children who start don't complete")
    elif avg_dropout > 10:
        print(f"   ⚠ MODERATE DROPOUT: 10-15% dropout rate needs attention")
    else:
        print(f"   ✓ LOW DROPOUT: Dropout rate under 10%")
    
    # Monthly patterns
    print("\n" + "="*80)
    print("SEASONAL PATTERNS (Monthly)")
    print("="*80)
    
    # Group by month name
    data['month_num'] = pd.to_datetime(data['month'], format='%B').dt.month
    monthly_avg = data.groupby('month_num').agg({
        'dpt1_coverage': 'mean',
        'dpt3_coverage': 'mean',
        'tetanus': 'mean'
    }).reset_index()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    print("\nAverage vaccination coverage by month:")
    print(f"{'Month':<8} {'DPT1 Cov.':<12} {'DPT3 Cov.':<12} {'Tetanus Cases'}")
    print("-"*80)
    for _, row in monthly_avg.iterrows():
        month_idx = int(row['month_num']) - 1
        print(f"{month_names[month_idx]:<8} {row['dpt1_coverage']*100:>10.1f}%  "
              f"{row['dpt3_coverage']*100:>10.1f}%  {row['tetanus']:>13,.0f}")
    
    # Performance against targets
    print("\n" + "="*80)
    print("PERFORMANCE AGAINST WHO TARGETS")
    print("="*80)
    
    who_target = 90.0
    current_dpt3 = yearly.iloc[-1]['dpt3_coverage'] * 100
    first_dpt3 = yearly.iloc[0]['dpt3_coverage'] * 100
    
    print(f"\nWHO DPT3 target: {who_target}%")
    print(f"DPT3 in 2018: {first_dpt3:.1f}% (gap: {who_target - first_dpt3:.1f}pp)")
    print(f"DPT3 in 2024: {current_dpt3:.1f}% (gap: {who_target - current_dpt3:.1f}pp)")
    print(f"Gap reduction: {(who_target - first_dpt3) - (who_target - current_dpt3):.1f}pp over 7 years")
    
    if current_dpt3 >= who_target:
        print(f"\n✓ TARGET ACHIEVED!")
    else:
        years_needed = (who_target - current_dpt3) / (dpt3_trend['change'] / 7) if dpt3_trend['change'] > 0 else float('inf')
        if years_needed < 20:
            print(f"\n→ At current trend, will reach target in ~{years_needed:.0f} years")
        else:
            print(f"\n⚠ Current trend too slow - need accelerated interventions")
    
    # Create comprehensive PDF
    create_comprehensive_pdf_report(data, yearly, trends, monthly_avg, month_names)
    
    # Export to Excel
    export_to_excel(data, yearly, trends, monthly_avg)
    
    return yearly, trends


def create_comprehensive_pdf_report(data, yearly, trends, monthly_avg, month_names):
    """Create comprehensive PDF report"""
    
    print("\n" + "="*80)
    print("CREATING COMPREHENSIVE PDF REPORT")
    print("="*80)
    
    output_file = 'scriptsV2/outputs/comprehensive_trends_report.pdf'
    
    with PdfPages(output_file) as pdf:
        
        # PAGE 1: Executive Summary
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('COMPREHENSIVE TRENDS ANALYSIS\nKenya Zero-Dose Program 2018-2024', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        summary_text = f"""
EXECUTIVE SUMMARY - 7-YEAR TRENDS
{'='*80}

Period: 2018-2024 (84 months)
Report Generated: {datetime.now().strftime('%B %d, %Y')}

KEY METRICS TRENDS:

1. VACCINATION COVERAGE
"""
        for metric in ['DPT1 coverage', 'DPT2 coverage', 'DPT3 coverage']:
            t = trends[metric]
            summary_text += f"   {metric}:\n"
            summary_text += f"     2018: {t['start']:>8.1f}%    2024: {t['end']:>8.1f}%    Change: {t['change']:>+7.1f}pp    {t['trend']}\n"
        
        summary_text += f"\n2. ZERO-DOSE STATUS\n"
        t = trends['Zero-dose rate']
        summary_text += f"   Zero-dose rate:\n"
        summary_text += f"     2018: {t['start']:>8.1f}%    2024: {t['end']:>8.1f}%    Change: {t['change']:>+7.1f}pp    {t['trend']}\n"
        
        summary_text += f"\n3. DROPOUT ANALYSIS\n"
        t = trends['Dropout rate']
        summary_text += f"   Dropout rate (DPT1→DPT3):\n"
        summary_text += f"     2018: {t['start']:>8.1f}%    2024: {t['end']:>8.1f}%    Change: {t['change']:>+7.1f}pp    {t['trend']}\n"
        
        summary_text += f"\n4. DISEASE BURDEN\n"
        for metric in ['Tetanus cases', 'Diphtheria cases', 'Hepatitis B cases']:
            t = trends[metric]
            summary_text += f"   {metric}:\n"
            summary_text += f"     2018: {t['start']:>10,.0f}    2024: {t['end']:>10,.0f}    Change: {t['change']:>+11,.0f}    {t['trend']}\n"
        
        summary_text += f"\n5. PERFORMANCE vs WHO TARGETS\n"
        who_target = 90.0
        current = trends['DPT3 coverage']['end']
        gap = who_target - current
        summary_text += f"   WHO DPT3 target: {who_target}%\n"
        summary_text += f"   Current DPT3: {current:.1f}%\n"
        summary_text += f"   Gap: {gap:.1f} percentage points\n"
        summary_text += f"   Status: {'ACHIEVED ✓' if gap <= 0 else 'BELOW TARGET ⚠'}\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=8, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: Coverage Trends
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('VACCINATION COVERAGE TRENDS', fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: DPT Coverage over time
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(yearly['year'], yearly['dpt1_coverage']*100, 'o-', 
                label='DPT1', linewidth=2, markersize=6, color='#2ecc71')
        ax1.plot(yearly['year'], yearly['dpt2_coverage']*100, 's-', 
                label='DPT2', linewidth=2, markersize=6, color='#3498db')
        ax1.plot(yearly['year'], yearly['dpt3_coverage']*100, '^-', 
                label='DPT3', linewidth=2, markersize=6, color='#e74c3c')
        ax1.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='WHO target')
        ax1.set_xlabel('Year', fontweight='bold')
        ax1.set_ylabel('Coverage (%)', fontweight='bold')
        ax1.set_title('DPT Coverage Trends', fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Zero-dose trend
        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(yearly['year'], yearly['zero_dose'], 'o-', 
                linewidth=2, markersize=6, color='#e74c3c')
        ax2.fill_between(yearly['year'], 0, yearly['zero_dose'], alpha=0.3, color='#e74c3c')
        ax2.set_xlabel('Year', fontweight='bold')
        ax2.set_ylabel('Zero-Dose Children', fontweight='bold')
        ax2.set_title('Zero-Dose Children Trend', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        # Plot 3: Dropout rate
        ax3 = plt.subplot(2, 2, 3)
        ax3.plot(yearly['year'], yearly['dropout_rate']*100, 'o-', 
                linewidth=2, markersize=6, color='#f39c12')
        ax3.fill_between(yearly['year'], 0, yearly['dropout_rate']*100, 
                        alpha=0.3, color='#f39c12')
        ax3.set_xlabel('Year', fontweight='bold')
        ax3.set_ylabel('Dropout Rate (%)', fontweight='bold')
        ax3.set_title('Dropout Rate Trend (DPT1→DPT3)', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Births trend
        ax4 = plt.subplot(2, 2, 4)
        ax4.plot(yearly['year'], yearly['estimated_lb'], 'o-', 
                linewidth=2, markersize=6, color='#9b59b6')
        ax4.fill_between(yearly['year'], 0, yearly['estimated_lb'], 
                        alpha=0.3, color='#9b59b6')
        ax4.set_xlabel('Year', fontweight='bold')
        ax4.set_ylabel('Live Births', fontweight='bold')
        ax4.set_title('Birth Trends', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 3: Disease Burden Trends
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('DISEASE BURDEN TRENDS', fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: Tetanus
        ax1 = plt.subplot(2, 2, 1)
        ax1.plot(yearly['year'], yearly['tetanus'], 'o-', 
                linewidth=2, markersize=6, color='#e74c3c')
        ax1.set_xlabel('Year', fontweight='bold')
        ax1.set_ylabel('Cases', fontweight='bold')
        ax1.set_title('Tetanus Cases', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Diphtheria
        ax2 = plt.subplot(2, 2, 2)
        ax2.plot(yearly['year'], yearly['diphtheria'], 'o-', 
                linewidth=2, markersize=6, color='#3498db')
        ax2.set_xlabel('Year', fontweight='bold')
        ax2.set_ylabel('Cases', fontweight='bold')
        ax2.set_title('Diphtheria Cases', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Hepatitis B
        ax3 = plt.subplot(2, 2, 3)
        ax3.plot(yearly['year'], yearly['hepatitisb_positive'], 'o-', 
                linewidth=2, markersize=6, color='#f39c12')
        ax3.set_xlabel('Year', fontweight='bold')
        ax3.set_ylabel('Cases', fontweight='bold')
        ax3.set_title('Hepatitis B Cases', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Pneumonia
        ax4 = plt.subplot(2, 2, 4)
        ax4.plot(yearly['year'], yearly['pneumonia'], 'o-', 
                linewidth=2, markersize=6, color='#9b59b6')
        ax4.set_xlabel('Year', fontweight='bold')
        ax4.set_ylabel('Cases', fontweight='bold')
        ax4.set_title('Pneumonia Cases (Hib-related)', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 4: Monthly patterns
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('SEASONAL PATTERNS (Monthly Averages)', fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: Monthly coverage
        ax1 = plt.subplot(2, 1, 1)
        x = range(len(monthly_avg))
        ax1.plot(x, monthly_avg['dpt1_coverage']*100, 'o-', 
                label='DPT1', linewidth=2, markersize=6, color='#2ecc71')
        ax1.plot(x, monthly_avg['dpt3_coverage']*100, '^-', 
                label='DPT3', linewidth=2, markersize=6, color='#e74c3c')
        ax1.axhline(y=90, color='red', linestyle='--', alpha=0.5, label='WHO target')
        ax1.set_xlabel('Month', fontweight='bold')
        ax1.set_ylabel('Coverage (%)', fontweight='bold')
        ax1.set_title('Average Vaccination Coverage by Month', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(month_names, rotation=45)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Monthly tetanus cases
        ax2 = plt.subplot(2, 1, 2)
        ax2.bar(x, monthly_avg['tetanus'], color='#e74c3c', alpha=0.7)
        ax2.set_xlabel('Month', fontweight='bold')
        ax2.set_ylabel('Average Tetanus Cases', fontweight='bold')
        ax2.set_title('Average Tetanus Cases by Month', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(month_names, rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Comprehensive Trends Analysis - Kenya 2018-2024'
        d['Author'] = 'ScriptsV2 Analysis Suite'
        d['Subject'] = 'Zero-Dose and Vaccination Trends'
        d['Keywords'] = 'Trends, Zero-Dose, DPT, Kenya, Vaccination'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✓ Comprehensive PDF report saved to: {output_file}")
    print(f"  - 4 pages with comprehensive trend analysis")


def export_to_excel(data, yearly, trends, monthly_avg):
    """Export results to Excel"""
    
    print("\n" + "="*80)
    print("EXPORTING TO EXCEL")
    print("="*80)
    
    output_file = 'scriptsV2/outputs/comprehensive_trends.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Trend Summary
        trend_data = []
        for metric, values in trends.items():
            trend_data.append({
                'Metric': metric,
                '2018': values['start'],
                '2024': values['end'],
                'Change': values['change'],
                'Trend': values['trend'],
                'P-value': values['p_value']
            })
        trends_df = pd.DataFrame(trend_data)
        trends_df.to_excel(writer, sheet_name='Trend Summary', index=False)
        
        # Sheet 2: Yearly Data
        yearly_export = yearly[['year', 'estimated_lb', 'dpt1', 'dpt2', 'dpt3', 
                                'zero_dose', 'dropout',
                                'dpt1_coverage', 'dpt2_coverage', 'dpt3_coverage',
                                'dropout_rate', 'zero_dose_rate',
                                'tetanus', 'diphtheria', 'hepatitisb_positive', 
                                'pneumonia']].copy()
        yearly_export.columns = ['Year', 'Births', 'DPT1', 'DPT2', 'DPT3', 
                                 'Zero-Dose', 'Dropout',
                                 'DPT1 Cov', 'DPT2 Cov', 'DPT3 Cov',
                                 'Dropout Rate', 'Zero-Dose Rate',
                                 'Tetanus', 'Diphtheria', 'Hep B', 'Pneumonia']
        yearly_export.to_excel(writer, sheet_name='Yearly Data', index=False)
        
        # Sheet 3: Monthly Patterns
        monthly_avg['month_name'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_export = monthly_avg[['month_name', 'dpt1_coverage', 'dpt3_coverage', 'tetanus']].copy()
        monthly_export.columns = ['Month', 'DPT1 Coverage', 'DPT3 Coverage', 'Avg Tetanus Cases']
        monthly_export.to_excel(writer, sheet_name='Monthly Patterns', index=False)
        
        # Sheet 4: Monthly Details
        data_copy = data.copy()
        data_copy['dpt2_coverage'] = data_copy['dpt2'] / data_copy['estimated_lb']
        monthly_detail = data_copy[['year', 'month', 'estimated_lb', 
                                    'dpt1_coverage', 'dpt2_coverage', 'dpt3_coverage',
                                    'tetanus', 'diphtheria', 'hepatitisb_positive']].copy()
        monthly_detail.columns = ['Year', 'Month', 'Births', 
                                 'DPT1 Cov', 'DPT2 Cov', 'DPT3 Cov',
                                 'Tetanus', 'Diphtheria', 'Hep B']
        monthly_detail.to_excel(writer, sheet_name='Monthly Details', index=False)
    
    print(f"\n✓ Excel report saved to: {output_file}")
    print("\nExcel file contains 4 sheets:")
    print("  1. Trend Summary - All metrics with trend direction")
    print("  2. Yearly Data - Annual aggregated data")
    print("  3. Monthly Patterns - Seasonal patterns")
    print("  4. Monthly Details - Full 84-month data")


def main():
    """Main execution function"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║              COMPREHENSIVE TRENDS ANALYSIS                             ║
║                   ScriptsV2 Analysis Suite                             ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        yearly, trends = analyze_comprehensive_trends()
        
        print("\n" + "="*80)
        print("✓ ANALYSIS COMPLETE")
        print("="*80)
        print("\nOutputs created:")
        print("  1. scriptsV2/outputs/comprehensive_trends_report.pdf (4-page report)")
        print("  2. scriptsV2/outputs/comprehensive_trends.xlsx (4-sheet workbook)")
        print("\nKey insights:")
        print("  - 7-year trends for all metrics")
        print("  - Statistical trend analysis")
        print("  - Seasonal patterns identified")
        print("  - Performance vs WHO targets")
        print("\nNext steps:")
        print("  - Review trend directions")
        print("  - Identify areas needing intervention")
        print("  - Use for strategic planning")
                
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

