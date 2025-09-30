#!/usr/bin/env python3
"""
===========================================
AGE GROUP CALCULATOR - UTILITY MODULE
===========================================

WHAT IT DOES:
Provides standardized age grouping functions for all
ScriptsV2 analyses. Ensures consistent age ranges across
all scripts.

WHO SHOULD USE:
- This is a utility module used by other scripts
- You don't need to run this directly
- Other scripts import functions from here

AGE GROUPS DEFINED:
- Neonates: 0-28 days (0-0.077 years)
- Infants: 1-11 months (0.077-1 years)
- Toddlers: 1-2 years
- Preschool: 2-5 years
- School Age: 5-15 years
- Adults: 15+ years

===========================================
"""

import numpy as np
import pandas as pd

# ============================================================================
# STANDARD AGE GROUP DEFINITIONS
# ============================================================================

# Age groups in years
AGE_GROUPS = {
    'Neonates (0-28d)': (0, 28/365),         # 0-28 days
    'Infants (1-11m)': (28/365, 1),          # 1-11 months
    'Toddlers (1-2y)': (1, 2),               # 1-2 years
    'Preschool (2-5y)': (2, 5),              # 2-5 years
    'School Age (5-15y)': (5, 15),           # 5-15 years
    'Adults (15+y)': (15, 120)               # 15+ years
}

# Age groups for children under 5 (primary target)
UNDER5_AGE_GROUPS = {
    'Neonates (0-28d)': (0, 28/365),
    'Infants (1-11m)': (28/365, 1),
    'Toddlers (1-2y)': (1, 2),
    'Preschool (2-5y)': (2, 5),
}

# Simplified age groups (fewer categories)
SIMPLE_AGE_GROUPS = {
    'Infants (<1y)': (0, 1),
    'Children (1-5y)': (1, 5),
    'Older Children (5-15y)': (5, 15),
    'Adults (15+y)': (15, 120)
}

# ============================================================================
# AGE GROUPING FUNCTIONS
# ============================================================================

def assign_age_group(age, age_group_dict=None):
    """
    Assign an age to an age group.
    
    Parameters:
    -----------
    age : float
        Age in years
    age_group_dict : dict, optional
        Dictionary of age groups. Default is AGE_GROUPS
    
    Returns:
    --------
    str
        Name of the age group
    
    Examples:
    ---------
    >>> assign_age_group(0.05)  # ~18 days old
    'Neonates (0-28d)'
    
    >>> assign_age_group(0.5)   # 6 months old
    'Infants (1-11m)'
    
    >>> assign_age_group(3)     # 3 years old
    'Preschool (2-5y)'
    """
    if age_group_dict is None:
        age_group_dict = AGE_GROUPS
    
    for group_name, (min_age, max_age) in age_group_dict.items():
        if min_age <= age < max_age:
            return group_name
    
    # Return last group for anyone older than max
    return list(age_group_dict.keys())[-1]


def get_age_mask(ages, age_min, age_max):
    """
    Create a boolean mask for ages within a range.
    
    Parameters:
    -----------
    ages : array-like
        Array of ages
    age_min : float
        Minimum age (inclusive)
    age_max : float
        Maximum age (exclusive)
    
    Returns:
    --------
    np.ndarray
        Boolean mask
    
    Examples:
    ---------
    >>> ages = np.array([0.05, 0.5, 2, 10, 20])
    >>> mask = get_age_mask(ages, 0, 1)
    >>> ages[mask]  # Get all infants
    array([0.05, 0.5])
    """
    ages = np.asarray(ages)
    return (ages >= age_min) & (ages < age_max)


def count_by_age_group(ages, age_group_dict=None):
    """
    Count how many individuals are in each age group.
    
    Parameters:
    -----------
    ages : array-like
        Array of ages
    age_group_dict : dict, optional
        Dictionary of age groups
    
    Returns:
    --------
    dict
        Dictionary with age group names as keys and counts as values
    
    Examples:
    ---------
    >>> ages = np.array([0.05, 0.5, 1.5, 3, 8, 20])
    >>> count_by_age_group(ages)
    {'Neonates (0-28d)': 1, 'Infants (1-11m)': 1, ...}
    """
    if age_group_dict is None:
        age_group_dict = AGE_GROUPS
    
    counts = {}
    ages = np.asarray(ages)
    
    for group_name, (min_age, max_age) in age_group_dict.items():
        mask = get_age_mask(ages, min_age, max_age)
        counts[group_name] = np.sum(mask)
    
    return counts


def summarize_by_age_group(ages, values, age_group_dict=None, agg_func='sum'):
    """
    Summarize values by age group.
    
    Parameters:
    -----------
    ages : array-like
        Array of ages
    values : array-like
        Array of values to summarize (e.g., cases, deaths)
    age_group_dict : dict, optional
        Dictionary of age groups
    agg_func : str or callable
        Aggregation function: 'sum', 'mean', 'max', etc.
    
    Returns:
    --------
    dict
        Dictionary with age group names as keys and aggregated values
    
    Examples:
    ---------
    >>> ages = np.array([0.05, 0.5, 1.5, 3, 8, 20])
    >>> cases = np.array([10, 20, 15, 25, 5, 8])
    >>> summarize_by_age_group(ages, cases)
    {'Neonates (0-28d)': 10, 'Infants (1-11m)': 20, ...}
    """
    if age_group_dict is None:
        age_group_dict = AGE_GROUPS
    
    ages = np.asarray(ages)
    values = np.asarray(values)
    
    summary = {}
    
    for group_name, (min_age, max_age) in age_group_dict.items():
        mask = get_age_mask(ages, min_age, max_age)
        group_values = values[mask]
        
        if len(group_values) == 0:
            summary[group_name] = 0
        elif agg_func == 'sum':
            summary[group_name] = np.sum(group_values)
        elif agg_func == 'mean':
            summary[group_name] = np.mean(group_values)
        elif agg_func == 'max':
            summary[group_name] = np.max(group_values)
        elif agg_func == 'min':
            summary[group_name] = np.min(group_values)
        elif callable(agg_func):
            summary[group_name] = agg_func(group_values)
        else:
            raise ValueError(f"Unknown aggregation function: {agg_func}")
    
    return summary


def create_age_group_dataframe(ages, age_group_dict=None):
    """
    Create a DataFrame with age group assignments.
    
    Parameters:
    -----------
    ages : array-like
        Array of ages
    age_group_dict : dict, optional
        Dictionary of age groups
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with 'age' and 'age_group' columns
    """
    if age_group_dict is None:
        age_group_dict = AGE_GROUPS
    
    ages = np.asarray(ages)
    age_groups = [assign_age_group(age, age_group_dict) for age in ages]
    
    return pd.DataFrame({
        'age': ages,
        'age_group': age_groups
    })


def print_age_group_summary(age_summary_dict):
    """
    Pretty print age group summary.
    
    Parameters:
    -----------
    age_summary_dict : dict
        Dictionary with age group names as keys
    """
    print("\n" + "="*70)
    print("AGE GROUP SUMMARY")
    print("="*70)
    print(f"\n{'Age Group':<25} {'Count/Value':>15}")
    print("-"*70)
    
    total = 0
    for group_name, value in age_summary_dict.items():
        print(f"{group_name:<25} {value:>15,.0f}")
        total += value
    
    print("-"*70)
    print(f"{'TOTAL':<25} {total:>15,.0f}")
    print("="*70)


# ============================================================================
# AGE-SPECIFIC PARAMETERS
# ============================================================================

def get_age_specific_cfr(disease='tetanus'):
    """
    Get age-specific case fatality rates for different diseases.
    
    Parameters:
    -----------
    disease : str
        Disease name: 'tetanus', 'pertussis', 'diphtheria', etc.
    
    Returns:
    --------
    dict
        Dictionary with age groups and their CFRs
    """
    cfr_by_disease = {
        'tetanus': {
            'Neonates (0-28d)': 0.718,    # 71.8% (calibrated)
            'Infants (1-11m)': 0.521,     # 52.1% (peri-neonatal)
            'Toddlers (1-2y)': 0.480,     # 48.0%
            'Preschool (2-5y)': 0.480,    # 48.0%
            'School Age (5-15y)': 0.327,  # 32.7%
            'Adults (15+y)': 0.327        # 32.7%
        },
        'pertussis': {
            'Neonates (0-28d)': 0.04,     # 4% in neonates
            'Infants (1-11m)': 0.02,      # 2% in infants
            'Toddlers (1-2y)': 0.01,      # 1% in toddlers
            'Preschool (2-5y)': 0.005,    # 0.5%
            'School Age (5-15y)': 0.001,  # 0.1%
            'Adults (15+y)': 0.001        # 0.1%
        },
        'diphtheria': {
            'Neonates (0-28d)': 0.10,     # 10%
            'Infants (1-11m)': 0.08,      # 8%
            'Toddlers (1-2y)': 0.06,      # 6%
            'Preschool (2-5y)': 0.05,     # 5%
            'School Age (5-15y)': 0.05,   # 5%
            'Adults (15+y)': 0.03         # 3%
        },
        'hib': {
            'Neonates (0-28d)': 0.05,     # 5%
            'Infants (1-11m)': 0.04,      # 4%
            'Toddlers (1-2y)': 0.03,      # 3%
            'Preschool (2-5y)': 0.03,     # 3%
            'School Age (5-15y)': 0.01,   # 1%
            'Adults (15+y)': 0.01         # 1%
        }
    }
    
    return cfr_by_disease.get(disease, {})


# ============================================================================
# TESTING AND DEMONSTRATION
# ============================================================================

def test_age_grouping():
    """Test the age grouping functions"""
    
    print("\n" + "="*70)
    print("TESTING AGE GROUPING FUNCTIONS")
    print("="*70)
    
    # Test ages
    test_ages = np.array([
        0.02,   # ~7 days (neonate)
        0.5,    # 6 months (infant)
        1.5,    # 18 months (toddler)
        3,      # 3 years (preschool)
        8,      # 8 years (school age)
        25      # 25 years (adult)
    ])
    
    print("\nTest Ages and Their Groups:")
    print("-"*70)
    for age in test_ages:
        group = assign_age_group(age)
        print(f"Age: {age:6.2f} years → {group}")
    
    # Test counting
    print("\n" + "="*70)
    counts = count_by_age_group(test_ages)
    print_age_group_summary(counts)
    
    # Test summarization with values
    test_cases = np.array([100, 200, 150, 250, 80, 120])
    print("\n" + "="*70)
    print("TEST CASE SUMMARIZATION")
    print("="*70)
    case_summary = summarize_by_age_group(test_ages, test_cases)
    print_age_group_summary(case_summary)
    
    print("\n✓ All tests passed!")


if __name__ == '__main__':
    print("""
===========================================
AGE GROUP CALCULATOR - UTILITY MODULE
===========================================

This module provides age grouping utilities for
all ScriptsV2 analyses.

Key Functions:
- assign_age_group(): Assign age to group
- get_age_mask(): Create boolean mask for age range
- count_by_age_group(): Count individuals per group
- summarize_by_age_group(): Aggregate values by group
- get_age_specific_cfr(): Get disease-specific CFRs

Age Groups Used:
- Neonates (0-28 days)
- Infants (1-11 months)
- Toddlers (1-2 years)
- Preschool (2-5 years)
- School Age (5-15 years)
- Adults (15+ years)

Running tests...
""")
    
    test_age_grouping()

