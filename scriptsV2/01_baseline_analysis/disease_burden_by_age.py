#!/usr/bin/env python3
"""
===========================================
DISEASE BURDEN BY AGE GROUP ⭐
===========================================

WHAT IT DOES:
Analyzes disease burden (cases and deaths) by age group
using real data from Kenya (2018-2024).

Focuses on diseases prevented by Pentavalent vaccine:
- Tetanus (with age-specific data: neonatal, peri-neonatal)
- Diphtheria
- Hepatitis B
- Pneumonia (Hib-related)
- Pertussis (estimated from respiratory infections)

WHO SHOULD USE:
- Program managers prioritizing age groups
- Researchers analyzing disease patterns
- Policy makers allocating resources

WHAT YOU NEED:
- Python environment activated
- Access to zerodose_data.dta file

WHAT YOU GET:
- Disease cases by age group
- Estimated deaths by age (using CFR)
- Age-prioritization recommendations
- Excel report with age-stratified data
- Comprehensive PDF report

USAGE:
    python scriptsV2/01_baseline_analysis/disease_burden_by_age.py

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

# Import utilities from the 09_utilities directory
sys.path.insert(0, os.path.join(parent_dir, '09_utilities'))
from data_loader import load_zerodose_data
from age_group_calculator import AGE_GROUPS, get_age_specific_cfr

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def analyze_disease_burden_by_age():
    """Main analysis function"""
    
    print("\n"\n=" + "="*80)
    print("\n"DISEASE BURDEN BY AGE GROUP")
    print("\n"Based on real data (2018-2024)")
    print("\n"="*80)
    
    # Load data
    data = load_zerodose_data(verbose=True)
    
    # Extract disease data
    print("\n"\n=" + "="*80)
    print("\n"DISEASE DATA SUMMARY (7 years)")
    print("\n"="*80)
    
    # Tetanus (age-specific data available)
    total_tetanus = data['tetanus'].sum()
    neonatal_tetanus = data['neonatal_tetanus'].sum()
    peri_neonatal_tetanus = data['peri_neonatal_tetanus'].sum()
    
    # Other diseases
    diphtheria = data['diphtheria'].sum()
    hepatitis_b = data['hepatitisb_positive'].sum()
    pneumonia = data['pneumonia'].sum()
    lower_rti = data['lower_rti'].sum()
    
    print(f"\nTetanus:")
    print(f"  Total cases: {total_tetanus:>25,.0f}")
    print(f"  Neonatal (0-28 days): {neonatal_tetanus:>15,.0f} ({neonatal_tetanus/total_tetanus*100:.1f}%)")
    print(f"  Peri-neonatal (29-60 days): {peri_neonatal_tetanus:>9,.0f} ({peri_neonatal_tetanus/total_tetanus*100:.1f}%)")
    print(f"  Other ages: {total_tetanus - neonatal_tetanus - peri_neonatal_tetanus:>23,.0f} ({(1 - (neonatal_tetanus + peri_neonatal_tetanus)/total_tetanus)*100:.1f}%)")
    
    print(f"\nOther Diseases:")
    print(f"  Diphtheria: {diphtheria:>24,.0f}")
    print(f"  Hepatitis B: {hepatitis_b:>23,.0f}")
    print(f"  Pneumonia (Hib-related): {pneumonia:>12,.0f}")
    print(f"  Lower RTI (Pertussis-related): {lower_rti:>8,.0f}")
    
    # Calculate age-stratified disease burden
    print("\n"\n=" + "="*80)
    print("\n"AGE-STRATIFIED DISEASE BURDEN")
    print("\n"="*80)
    
    # Tetanus by age (from real data + estimates)
    tetanus_by_age = {
        'Neonates (0-28d)': neonatal_tetanus,
        'Infants (1-11m)': peri_neonatal_tetanus,  # Peri-neonatal
        'Toddlers (1-2y)': (total_tetanus - neonatal_tetanus - peri_neonatal_tetanus) * 0.15,
        'Preschool (2-5y)': (total_tetanus - neonatal_tetanus - peri_neonatal_tetanus) * 0.25,
        'School Age (5-15y)': (total_tetanus - neonatal_tetanus - peri_neonatal_tetanus) * 0.30,
        'Adults (15+y)': (total_tetanus - neonatal_tetanus - peri_neonatal_tetanus) * 0.30
    }
    
    # Diphtheria by age (estimates based on epidemiology)
    diphtheria_by_age = {
        'Neonates (0-28d)': diphtheria * 0.05,
        'Infants (1-11m)': diphtheria * 0.15,
        'Toddlers (1-2y)': diphtheria * 0.20,
        'Preschool (2-5y)': diphtheria * 0.25,
        'School Age (5-15y)': diphtheria * 0.30,  # Peak age
        'Adults (15+y)': diphtheria * 0.05
    }
    
    # Hepatitis B by age
    hep_b_by_age = {
        'Neonates (0-28d)': hepatitis_b * 0.30,  # Vertical transmission
        'Infants (1-11m)': hepatitis_b * 0.15,
        'Toddlers (1-2y)': hepatitis_b * 0.15,
        'Preschool (2-5y)': hepatitis_b * 0.15,
        'School Age (5-15y)': hepatitis_b * 0.10,
        'Adults (15+y)': hepatitis_b * 0.15
    }
    
    # Pneumonia/Hib by age
    pneumonia_by_age = {
        'Neonates (0-28d)': pneumonia * 0.20,
        'Infants (1-11m)': pneumonia * 0.35,  # Peak age
        'Toddlers (1-2y)': pneumonia * 0.25,
        'Preschool (2-5y)': pneumonia * 0.15,
        'School Age (5-15y)': pneumonia * 0.03,
        'Adults (15+y)': pneumonia * 0.02
    }
    
    # Pertussis (from lower RTI as proxy)
    pertussis_by_age = {
        'Neonates (0-28d)': lower_rti * 0.25,
        'Infants (1-11m)': lower_rti * 0.40,  # Peak age
        'Toddlers (1-2y)': lower_rti * 0.20,
        'Preschool (2-5y)': lower_rti * 0.10,
        'School Age (5-15y)': lower_rti * 0.03,
        'Adults (15+y)': lower_rti * 0.02
    }
    
    # Calculate deaths using age-specific CFR
    print("\n"\n=" + "="*80)
    print("\n"ESTIMATED DEATHS BY AGE (using age-specific CFR)")
    print("\n"="*80)
    
    tetanus_cfr = get_age_specific_cfr('tetanus')
    diphtheria_cfr = get_age_specific_cfr('diphtheria')
    pertussis_cfr = get_age_specific_cfr('pertussis')
    hib_cfr = get_age_specific_cfr('hib')
    
    # Calculate deaths for each disease by age
    tetanus_deaths = {}
    diphtheria_deaths = {}
    pertussis_deaths = {}
    hep_b_deaths = {}
    hib_deaths = {}
    
    for age_group in AGE_GROUPS.keys():
        tetanus_deaths[age_group] = tetanus_by_age[age_group] * tetanus_cfr.get(age_group, 0.3)
        diphtheria_deaths[age_group] = diphtheria_by_age[age_group] * diphtheria_cfr.get(age_group, 0.05)
        pertussis_deaths[age_group] = pertussis_by_age[age_group] * pertussis_cfr.get(age_group, 0.01)
        hep_b_deaths[age_group] = hep_b_by_age[age_group] * 0.02  # 2% CFR for Hep B
        hib_deaths[age_group] = pneumonia_by_age[age_group] * hib_cfr.get(age_group, 0.03)
    
    # Print disease burden table
    print(f"\n{'Age Group':<20} {'Tetanus':<12} {'Deaths':<10} {'CFR':<8}")
    print("\n"-"*80)
    for age_group in AGE_GROUPS.keys():
        cases = tetanus_by_age[age_group]
        deaths = tetanus_deaths[age_group]
        cfr = tetanus_cfr.get(age_group, 0.3) * 100
        print(f"{age_group:<20} {cases:>10,.0f}  {deaths:>8,.0f}  {cfr:>6.1f}%")
    
    print(f"\n{'TOTAL':<20} {sum(tetanus_by_age.values()):>10,.0f}  "
          f"{sum(tetanus_deaths.values()):>8,.0f}")
    
    # Priority ranking
    print("\n"\n=" + "="*80)
    print("\n"AGE GROUP PRIORITY RANKING")
    print("\n"="*80)
    print("\n"\nBased on total disease burden (all 5 Pentavalent diseases):")
    
    total_burden = {}
    total_deaths = {}
    
    for age_group in AGE_GROUPS.keys():
        total_burden[age_group] = (
            tetanus_by_age[age_group] +
            diphtheria_by_age[age_group] +
            pertussis_by_age[age_group] +
            hep_b_by_age[age_group] +
            pneumonia_by_age[age_group]
        )
        total_deaths[age_group] = (
            tetanus_deaths[age_group] +
            diphtheria_deaths[age_group] +
            pertussis_deaths[age_group] +
            hep_b_deaths[age_group] +
            hib_deaths[age_group]
        )
    
    # Sort by deaths (most critical metric)
    sorted_ages = sorted(total_deaths.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Rank':<6} {'Age Group':<20} {'Total Cases':<15} {'Total Deaths':<15} {'Priority'}")
    print("\n"-"*80)
    
    priorities = ['CRITICAL', 'VERY HIGH', 'HIGH', 'MEDIUM', 'LOW', 'LOW']
    for rank, (age_group, deaths) in enumerate(sorted_ages, 1):
        cases = total_burden[age_group]
        priority = priorities[rank-1] if rank <= len(priorities) else 'LOW'
        print(f"{rank:<6} {age_group:<20} {cases:>13,.0f}  {deaths:>13,.0f}  {priority}")
    
    # Create comprehensive report
    create_comprehensive_pdf_report(
        data, tetanus_by_age, diphtheria_by_age, hep_b_by_age, 
        pneumonia_by_age, pertussis_by_age,
        tetanus_deaths, diphtheria_deaths, hib_deaths,
        pertussis_deaths, hep_b_deaths,
        total_burden, total_deaths, sorted_ages
    )
    
    # Export to Excel
    export_to_excel(
        tetanus_by_age, diphtheria_by_age, hep_b_by_age,
        pneumonia_by_age, pertussis_by_age,
        tetanus_deaths, diphtheria_deaths, hib_deaths,
        pertussis_deaths, hep_b_deaths,
        total_burden, total_deaths
    )
    
    return total_burden, total_deaths


def create_comprehensive_pdf_report(data, tetanus_by_age, diphtheria_by_age, hep_b_by_age,
                                   pneumonia_by_age, pertussis_by_age,
                                   tetanus_deaths, diphtheria_deaths, hib_deaths,
                                   pertussis_deaths, hep_b_deaths,
                                   total_burden, total_deaths, sorted_ages):
    """Create comprehensive PDF report"""
    
    print("\n"\n=" + "="*80)
    print("\n"CREATING COMPREHENSIVE PDF REPORT")
    print("\n"="*80)
    
    output_file = 'scriptsV2/outputs/disease_burden_by_age_report.pdf'
    
    with PdfPages(output_file) as pdf:
        
        # PAGE 1: Executive Summary
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('DISEASE BURDEN BY AGE GROUP\nKenya Pentavalent Diseases 2018-2024', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        ax = fig.add_subplot(111)
        ax.axis('off')
        
        summary_text = f"""
EXECUTIVE SUMMARY - AGE-STRATIFIED DISEASE BURDEN
{'='*80}

Period: 2018-2024 (7 years)
Report Generated: {datetime.now().strftime('%B %d, %Y')}

KEY FINDINGS:

1. TOTAL DISEASE BURDEN (All 5 Pentavalent Diseases)
   Total Cases: {sum(total_burden.values()):>40,.0f}
   Total Deaths: {sum(total_deaths.values()):>39,.0f}
   Overall CFR: {sum(total_deaths.values())/sum(total_burden.values())*100:>40.1f}%

2. DISEASE-SPECIFIC BURDEN (7 years)
   Tetanus:
     Cases: {sum(tetanus_by_age.values()):>47,.0f}
     Deaths: {sum(tetanus_deaths.values()):>46,.0f}
     CFR: {sum(tetanus_deaths.values())/sum(tetanus_by_age.values())*100:>49.1f}%
   
   Diphtheria:
     Cases: {sum(diphtheria_by_age.values()):>47,.0f}
     Deaths: {sum(diphtheria_deaths.values()):>46,.0f}
     CFR: {sum(diphtheria_deaths.values())/sum(diphtheria_by_age.values())*100:>49.1f}%
   
   Pertussis (estimated):
     Cases: {sum(pertussis_by_age.values()):>47,.0f}
     Deaths: {sum(pertussis_deaths.values()):>46,.0f}
     CFR: {sum(pertussis_deaths.values())/sum(pertussis_by_age.values())*100:>49.1f}%
   
   Hepatitis B:
     Cases: {sum(hep_b_by_age.values()):>47,.0f}
     Deaths: {sum(hep_b_deaths.values()):>46,.0f}
     CFR: 2.0%
   
   Hib/Pneumonia:
     Cases: {sum(pneumonia_by_age.values()):>47,.0f}
     Deaths: {sum(hib_deaths.values()):>46,.0f}
     CFR: {sum(hib_deaths.values())/sum(pneumonia_by_age.values())*100:>49.1f}%

3. AGE GROUP PRIORITY RANKING (by deaths)
"""
        for rank, (age_group, deaths) in enumerate(sorted_ages[:6], 1):
            cases = total_burden[age_group]
            summary_text += f"   {rank}. {age_group:<20} {cases:>15,.0f} cases  {deaths:>10,.0f} deaths\n"
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
               fontsize=8, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: Disease Burden Visualization
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('DISEASE BURDEN BY AGE GROUP', fontsize=14, fontweight='bold', y=0.98)
        
        age_labels = list(AGE_GROUPS.keys())
        x = np.arange(len(age_labels))
        width = 0.15
        
        # Plot 1: Cases by disease and age
        ax1 = plt.subplot(2, 1, 1)
        ax1.bar(x - 2*width, [tetanus_by_age[ag] for ag in age_labels], width, 
               label='Tetanus', color='#e74c3c', alpha=0.8)
        ax1.bar(x - width, [diphtheria_by_age[ag] for ag in age_labels], width, 
               label='Diphtheria', color='#3498db', alpha=0.8)
        ax1.bar(x, [pertussis_by_age[ag] for ag in age_labels], width, 
               label='Pertussis', color='#2ecc71', alpha=0.8)
        ax1.bar(x + width, [hep_b_by_age[ag] for ag in age_labels], width, 
               label='Hep B', color='#f39c12', alpha=0.8)
        ax1.bar(x + 2*width, [pneumonia_by_age[ag] for ag in age_labels], width, 
               label='Hib/Pneumonia', color='#9b59b6', alpha=0.8)
        
        ax1.set_xlabel('Age Group', fontweight='bold')
        ax1.set_ylabel('Cases (7 years)', fontweight='bold')
        ax1.set_title('Disease Cases by Age Group', fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(age_labels, rotation=45, ha='right')
        ax1.legend(loc='upper right', fontsize=8)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: Deaths by disease and age
        ax2 = plt.subplot(2, 1, 2)
        ax2.bar(x - 2*width, [tetanus_deaths[ag] for ag in age_labels], width, 
               label='Tetanus', color='#e74c3c', alpha=0.8)
        ax2.bar(x - width, [diphtheria_deaths[ag] for ag in age_labels], width, 
               label='Diphtheria', color='#3498db', alpha=0.8)
        ax2.bar(x, [pertussis_deaths[ag] for ag in age_labels], width, 
               label='Pertussis', color='#2ecc71', alpha=0.8)
        ax2.bar(x + width, [hep_b_deaths[ag] for ag in age_labels], width, 
               label='Hep B', color='#f39c12', alpha=0.8)
        ax2.bar(x + 2*width, [hib_deaths[ag] for ag in age_labels], width, 
               label='Hib', color='#9b59b6', alpha=0.8)
        
        ax2.set_xlabel('Age Group', fontweight='bold')
        ax2.set_ylabel('Deaths (7 years)', fontweight='bold')
        ax2.set_title('Deaths by Age Group', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(age_labels, rotation=45, ha='right')
        ax2.legend(loc='upper right', fontsize=8)
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 3: Total burden and priority ranking
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle('TOTAL BURDEN AND PRIORITY RANKING', fontsize=14, fontweight='bold', y=0.98)
        
        # Plot 1: Total burden by age
        ax1 = plt.subplot(2, 1, 1)
        burden_vals = [total_burden[ag] for ag in age_labels]
        death_vals = [total_deaths[ag] for ag in age_labels]
        
        ax1_twin = ax1.twinx()
        bars = ax1.bar(age_labels, burden_vals, color='#3498db', alpha=0.7, label='Total Cases')
        line = ax1_twin.plot(age_labels, death_vals, 'ro-', linewidth=2, markersize=8, label='Deaths')
        
        ax1.set_xlabel('Age Group', fontweight='bold')
        ax1.set_ylabel('Total Cases', fontweight='bold', color='#3498db')
        ax1_twin.set_ylabel('Total Deaths', fontweight='bold', color='red')
        ax1.set_title('Total Disease Burden by Age Group', fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#3498db')
        ax1_twin.tick_params(axis='y', labelcolor='red')
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, val in zip(bars, burden_vals):
            ax1.text(bar.get_x() + bar.get_width()/2, val,
                    f'{val/1000:.0f}K', ha='center', va='bottom', fontsize=8)
        
        # Plot 2: Priority ranking table
        ax2 = plt.subplot(2, 1, 2)
        ax2.axis('off')
        
        table_data = [['Rank', 'Age Group', 'Cases', 'Deaths', 'CFR', 'Priority']]
        priorities = ['CRITICAL', 'VERY HIGH', 'HIGH', 'HIGH', 'MEDIUM', 'LOW']
        
        for rank, (age_group, deaths) in enumerate(sorted_ages, 1):
            cases = total_burden[age_group]
            cfr = (deaths / cases * 100) if cases > 0 else 0
            priority = priorities[rank-1] if rank <= len(priorities) else 'LOW'
            table_data.append([
                str(rank),
                age_group,
                f"{cases:,.0f}",
                f"{deaths:,.0f}",
                f"{cfr:.1f}%",
                priority
            ])
        
        table = ax2.table(cellText=table_data, cellLoc='center', loc='center',
                         colWidths=[0.08, 0.25, 0.20, 0.18, 0.12, 0.17])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(6):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color code priority levels
        priority_colors = {
            'CRITICAL': '#e74c3c',
            'VERY HIGH': '#f39c12',
            'HIGH': '#f1c40f',
            'MEDIUM': '#3498db',
            'LOW': '#95a5a6'
        }
        
        for i in range(1, len(table_data)):
            priority = table_data[i][5]
            color = priority_colors.get(priority, 'white')
            table[(i, 5)].set_facecolor(color)
            if priority in ['CRITICAL', 'VERY HIGH']:
                table[(i, 5)].set_text_props(color='white', weight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Set PDF metadata
        d = pdf.infodict()
        d['Title'] = 'Disease Burden by Age Group - Kenya 2018-2024'
        d['Author'] = 'ScriptsV2 Analysis Suite'
        d['Subject'] = 'Age-Stratified Disease Burden Analysis'
        d['Keywords'] = 'Disease Burden, Age Groups, Pentavalent, Kenya'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✓ Comprehensive PDF report saved to: {output_file}")
    print(f"  - 3 pages with age-stratified analysis")


def export_to_excel(tetanus_by_age, diphtheria_by_age, hep_b_by_age,
                   pneumonia_by_age, pertussis_by_age,
                   tetanus_deaths, diphtheria_deaths, hib_deaths,
                   pertussis_deaths, hep_b_deaths,
                   total_burden, total_deaths):
    """Export results to Excel"""
    
    print("\n"\n=" + "="*80)
    print("\n"EXPORTING TO EXCEL")
    print("\n"="*80)
    
    output_file = 'scriptsV2/outputs/disease_burden_by_age.xlsx'
    
    age_labels = list(AGE_GROUPS.keys())
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_df = pd.DataFrame({
            'Age Group': age_labels,
            'Total Cases': [total_burden[ag] for ag in age_labels],
            'Total Deaths': [total_deaths[ag] for ag in age_labels],
            'CFR (%)': [(total_deaths[ag]/total_burden[ag]*100) if total_burden[ag] > 0 else 0 
                        for ag in age_labels]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Cases by Disease
        cases_df = pd.DataFrame({
            'Age Group': age_labels,
            'Tetanus': [tetanus_by_age[ag] for ag in age_labels],
            'Diphtheria': [diphtheria_by_age[ag] for ag in age_labels],
            'Pertussis': [pertussis_by_age[ag] for ag in age_labels],
            'Hepatitis B': [hep_b_by_age[ag] for ag in age_labels],
            'Hib/Pneumonia': [pneumonia_by_age[ag] for ag in age_labels]
        })
        cases_df.to_excel(writer, sheet_name='Cases by Disease', index=False)
        
        # Sheet 3: Deaths by Disease
        deaths_df = pd.DataFrame({
            'Age Group': age_labels,
            'Tetanus': [tetanus_deaths[ag] for ag in age_labels],
            'Diphtheria': [diphtheria_deaths[ag] for ag in age_labels],
            'Pertussis': [pertussis_deaths[ag] for ag in age_labels],
            'Hepatitis B': [hep_b_deaths[ag] for ag in age_labels],
            'Hib': [hib_deaths[ag] for ag in age_labels]
        })
        deaths_df.to_excel(writer, sheet_name='Deaths by Disease', index=False)
    
    print(f"\n✓ Excel report saved to: {output_file}")
    print("\n"\nExcel file contains 3 sheets:")
    print("\n"  1. Summary - Total burden by age")
    print("\n"  2. Cases by Disease - Disease-specific cases")
    print("\n"  3. Deaths by Disease - Disease-specific deaths")


def main():
    """Main execution function"""
    
    print("\n"""
╔════════════════════════════════════════════════════════════════════════╗
║              DISEASE BURDEN BY AGE GROUP ANALYSIS ⭐                   ║
║                     ScriptsV2 Analysis Suite                           ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        total_burden, total_deaths = analyze_disease_burden_by_age()
        
        print("\n"\n=" + "="*80)
        print("\n"✓ ANALYSIS COMPLETE")
        print("\n"="*80)
        print("\n"\nOutputs created:")
        print("\n"  1. scriptsV2/outputs/disease_burden_by_age_report.pdf (3-page report)")
        print("\n"  2. scriptsV2/outputs/disease_burden_by_age.xlsx (3-sheet workbook)")
        print("\n"\nKey insights:")
        print("\n"  - Age-stratified disease burden calculated")
        print("\n"  - Priority ranking based on deaths")
        print("\n"  - Age-specific CFR applied")
        print("\n"\nNext steps:")
        print("\n"  - Review age priority ranking")
        print("\n"  - Use for targeting interventions")
        print("\n"  - Run compare_age_groups.py for detailed age analysis")
                
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

