#!/usr/bin/env python3
"""
===========================================
DATA LOADER - UTILITY MODULE
===========================================

WHAT IT DOES:
Loads and validates the zero-dose data file.
Provides clean, standardized access to real data.

WHO SHOULD USE:
- This is a utility module used by other scripts
- You don't need to run this directly
- Other scripts import functions from here

DATA SOURCE:
- File: zdsim/data/zerodose_data.dta
- Period: 84 months (2018-2024)
- Records: Vaccination coverage and disease cases

===========================================
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA FILE PATHS
# ============================================================================

DATA_FILE = 'zdsim/data/zerodose_data.dta'
BACKUP_DATA_FILE = 'zdsim/data/zerodose_data.xlsx'

# ============================================================================
# LOAD DATA FUNCTIONS
# ============================================================================

def load_zerodose_data(verbose=True):
    """
    Load the zero-dose data file.
    
    Parameters:
    -----------
    verbose : bool
        Whether to print loading messages
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with zero-dose data
    
    Raises:
    -------
    FileNotFoundError
        If data file cannot be found
    """
    if verbose:
        print("Loading zero-dose data...")
    
    # Try primary data file
    if os.path.exists(DATA_FILE):
        try:
            data = pd.read_stata(DATA_FILE)
            if verbose:
                print(f"✓ Loaded {len(data)} records from {DATA_FILE}")
            return data
        except Exception as e:
            if verbose:
                print(f"⚠ Error loading .dta file: {e}")
    
    # Try backup Excel file
    if os.path.exists(BACKUP_DATA_FILE):
        try:
            data = pd.read_excel(BACKUP_DATA_FILE)
            if verbose:
                print(f"✓ Loaded {len(data)} records from {BACKUP_DATA_FILE}")
            return data
        except Exception as e:
            if verbose:
                print(f"⚠ Error loading .xlsx file: {e}")
    
    raise FileNotFoundError(
        f"Could not find data file. Please ensure {DATA_FILE} exists."
    )


def validate_data(data, verbose=True):
    """
    Validate that the data has expected columns.
    
    Parameters:
    -----------
    data : pd.DataFrame
        DataFrame to validate
    verbose : bool
        Whether to print validation messages
    
    Returns:
    --------
    bool
        True if data is valid
    """
    required_columns = [
        'year', 'month', 'estimated_lb',
        'dpt1', 'dpt2', 'dpt3',
        'tetanus', 'neonatal_tetanus'
    ]
    
    missing = [col for col in required_columns if col not in data.columns]
    
    if missing:
        if verbose:
            print(f"⚠ Missing required columns: {missing}")
        return False
    
    if verbose:
        print("✓ Data validation passed")
    
    return True


def get_data_summary(data):
    """
    Get summary statistics about the data.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Zero-dose data
    
    Returns:
    --------
    dict
        Dictionary with summary statistics
    """
    summary = {
        'n_records': len(data),
        'n_months': len(data),
        'years': sorted(data['year'].unique()),
        'year_range': (int(data['year'].min()), int(data['year'].max())),
        'total_births': data['estimated_lb'].sum(),
        'total_dpt1': data['dpt1'].sum(),
        'total_dpt3': data['dpt3'].sum(),
        'avg_dpt1_coverage': data['dpt1'].sum() / data['estimated_lb'].sum(),
        'avg_dpt3_coverage': data['dpt3'].sum() / data['estimated_lb'].sum(),
    }
    
    return summary


# ============================================================================
# DATA TRANSFORMATION FUNCTIONS
# ============================================================================

def calculate_zerodose(data):
    """
    Calculate zero-dose children from the data.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Zero-dose data
    
    Returns:
    --------
    pd.DataFrame
        Data with additional zero-dose columns
    """
    data = data.copy()
    
    # Calculate zero-dose (children who never got DPT1)
    data['zero_dose'] = data['estimated_lb'] - data['dpt1']
    data['zero_dose'] = data['zero_dose'].clip(lower=0)  # No negative values
    
    # Calculate dropout (started but didn't complete)
    data['dropout'] = data['dpt1'] - data['dpt3']
    data['dropout'] = data['dropout'].clip(lower=0)
    
    # Calculate coverage rates
    data['dpt1_coverage'] = data['dpt1'] / data['estimated_lb']
    data['dpt2_coverage'] = data['dpt2'] / data['estimated_lb']
    data['dpt3_coverage'] = data['dpt3'] / data['estimated_lb']
    
    # Calculate dropout rate
    data['dropout_rate'] = data['dropout'] / data['dpt1']
    data['dropout_rate'] = data['dropout_rate'].fillna(0)
    
    return data


def aggregate_by_year(data):
    """
    Aggregate data by year.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Zero-dose data
    
    Returns:
    --------
    pd.DataFrame
        Yearly aggregated data
    """
    # Calculate zero-dose first
    data = calculate_zerodose(data)
    
    # Aggregate by year
    yearly = data.groupby('year').agg({
        'estimated_lb': 'sum',
        'dpt1': 'sum',
        'dpt2': 'sum',
        'dpt3': 'sum',
        'zero_dose': 'sum',
        'dropout': 'sum',
        'tetanus': 'sum',
        'neonatal_tetanus': 'sum',
        'diphtheria': 'sum' if 'diphtheria' in data.columns else lambda x: 0,
        'hepatitisb_positive': 'sum' if 'hepatitisb_positive' in data.columns else lambda x: 0,
        'pneumonia': 'sum' if 'pneumonia' in data.columns else lambda x: 0,
    }).reset_index()
    
    # Recalculate rates
    yearly['dpt1_coverage'] = yearly['dpt1'] / yearly['estimated_lb']
    yearly['dpt2_coverage'] = yearly['dpt2'] / yearly['estimated_lb']
    yearly['dpt3_coverage'] = yearly['dpt3'] / yearly['estimated_lb']
    yearly['dropout_rate'] = yearly['dropout'] / yearly['dpt1']
    yearly['zero_dose_rate'] = yearly['zero_dose'] / yearly['estimated_lb']
    
    return yearly


def get_disease_data(data):
    """
    Extract disease-related columns.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Zero-dose data
    
    Returns:
    --------
    dict
        Dictionary with disease data
    """
    disease_data = {}
    
    # Tetanus data
    if 'tetanus' in data.columns:
        disease_data['tetanus'] = {
            'total_cases': data['tetanus'].sum(),
            'monthly_mean': data['tetanus'].mean(),
            'monthly_std': data['tetanus'].std()
        }
    
    if 'neonatal_tetanus' in data.columns:
        disease_data['neonatal_tetanus'] = {
            'total_cases': data['neonatal_tetanus'].sum(),
            'proportion': data['neonatal_tetanus'].sum() / data['tetanus'].sum()
        }
    
    # Diphtheria data
    if 'diphtheria' in data.columns:
        disease_data['diphtheria'] = {
            'total_cases': data['diphtheria'].sum(),
            'monthly_mean': data['diphtheria'].mean()
        }
    
    # Hepatitis B data
    if 'hepatitisb_positive' in data.columns:
        disease_data['hepatitis_b'] = {
            'total_cases': data['hepatitisb_positive'].sum(),
            'monthly_mean': data['hepatitisb_positive'].mean()
        }
    
    # Pneumonia (Hib proxy) data
    if 'pneumonia' in data.columns:
        disease_data['pneumonia_hib'] = {
            'total_cases': data['pneumonia'].sum(),
            'monthly_mean': data['pneumonia'].mean()
        }
    
    return disease_data


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def load_and_prepare_data(verbose=True):
    """
    Load data and prepare it with additional calculated columns.
    
    Parameters:
    -----------
    verbose : bool
        Whether to print messages
    
    Returns:
    --------
    tuple
        (data, yearly_data, summary)
    """
    # Load data
    data = load_zerodose_data(verbose=verbose)
    
    # Validate
    if not validate_data(data, verbose=verbose):
        raise ValueError("Data validation failed")
    
    # Calculate zero-dose
    data = calculate_zerodose(data)
    
    # Aggregate by year
    yearly = aggregate_by_year(data)
    
    # Get summary
    summary = get_data_summary(data)
    
    if verbose:
        print(f"\n✓ Data prepared:")
        print(f"  - {summary['n_records']} monthly records")
        print(f"  - Years: {summary['year_range'][0]}-{summary['year_range'][1]}")
        print(f"  - Total births: {summary['total_births']:,.0f}")
        print(f"  - Average DPT3 coverage: {summary['avg_dpt3_coverage']*100:.1f}%")
    
    return data, yearly, summary


def print_data_summary(data):
    """
    Print a formatted summary of the data.
    
    Parameters:
    -----------
    data : pd.DataFrame
        Zero-dose data
    """
    summary = get_data_summary(data)
    
    print("\n" + "="*70)
    print("DATA SUMMARY")
    print("="*70)
    print(f"\nRecords: {summary['n_records']} months")
    print(f"Period: {summary['year_range'][0]}-{summary['year_range'][1]}")
    print(f"\nPopulation:")
    print(f"  Total births: {summary['total_births']:>20,.0f}")
    print(f"  Total DPT1 given: {summary['total_dpt1']:>16,.0f}")
    print(f"  Total DPT3 given: {summary['total_dpt3']:>16,.0f}")
    print(f"\nCoverage:")
    print(f"  DPT1 coverage: {summary['avg_dpt1_coverage']*100:>18.1f}%")
    print(f"  DPT3 coverage: {summary['avg_dpt3_coverage']*100:>18.1f}%")
    print(f"  Dropout rate: {(1 - summary['avg_dpt3_coverage']/summary['avg_dpt1_coverage'])*100:>19.1f}%")
    
    # Disease data
    disease_data = get_disease_data(data)
    if disease_data:
        print(f"\nDisease Burden:")
        for disease, stats in disease_data.items():
            if 'total_cases' in stats:
                print(f"  {disease.replace('_', ' ').title()}: {stats['total_cases']:>10,.0f} cases")
    
    print("="*70)


# ============================================================================
# TESTING
# ============================================================================

def test_data_loader():
    """Test the data loading functions"""
    
    print("\n" + "="*70)
    print("TESTING DATA LOADER")
    print("="*70)
    
    try:
        # Load data
        data, yearly, summary = load_and_prepare_data(verbose=True)
        
        # Print summary
        print_data_summary(data)
        
        # Show yearly trends
        print("\n" + "="*70)
        print("YEARLY TRENDS")
        print("="*70)
        print(f"\n{'Year':<8} {'Births':<12} {'Zero-Dose':<12} {'DPT3 Cov.':<12}")
        print("-"*70)
        for _, row in yearly.iterrows():
            print(f"{int(row['year']):<8} {row['estimated_lb']:>10,.0f}  "
                  f"{row['zero_dose']:>10,.0f}  {row['dpt3_coverage']*100:>10.1f}%")
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


if __name__ == '__main__':
    print("""
===========================================
DATA LOADER - UTILITY MODULE
===========================================

This module provides data loading and validation
functions for all ScriptsV2 analyses.

Key Functions:
- load_zerodose_data(): Load the data file
- validate_data(): Validate data integrity
- calculate_zerodose(): Calculate zero-dose children
- aggregate_by_year(): Aggregate to yearly data
- load_and_prepare_data(): All-in-one loader

Running tests...
""")
    
    test_data_loader()

