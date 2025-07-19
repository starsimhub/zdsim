#!/usr/bin/env python3
"""
Tetanus Data Validation Script
==============================

This script validates the format of your tetanus_monthly_cases.csv file to ensure
it meets the requirements for the calibration script.

Usage:
    python scripts/validate_tetanus_data.py

The script will check:
- File existence and location
- Column headers and structure
- Date format and validity
- Case number format and validity
- Data completeness and consistency
"""

import pandas as pd
import os
import sys
from datetime import datetime

def validate_tetanus_data(filename='tetanus_monthly_cases.csv'):
    """
    Validate tetanus monthly cases data file
    
    Args:
        filename (str): Path to the CSV file to validate
        
    Returns:
        bool: True if valid, False if invalid
    """
    print("🔍 VALIDATING TETANUS DATA FILE")
    print("=" * 50)
    
    # Check 1: File existence
    print(f"📁 Checking file existence: {filename}")
    if not os.path.exists(filename):
        print(f"❌ ERROR: File '{filename}' not found!")
        print("   Please ensure the file exists in the current directory.")
        return False
    print("✅ File exists")
    
    # Check 2: File can be read as CSV
    print(f"📖 Checking CSV format...")
    try:
        df = pd.read_csv(filename)
        print("✅ File can be read as CSV")
    except Exception as e:
        print(f"❌ ERROR: Cannot read file as CSV: {e}")
        return False
    
    # Check 3: Column structure
    print(f"📊 Checking column structure...")
    expected_columns = ['date', 'cases']
    actual_columns = list(df.columns)
    
    if actual_columns != expected_columns:
        print(f"❌ ERROR: Wrong column structure!")
        print(f"   Expected: {expected_columns}")
        print(f"   Found:    {actual_columns}")
        print("   Please ensure columns are exactly 'date' and 'cases'")
        return False
    print("✅ Column structure is correct")
    
    # Check 4: Data types and format
    print(f"🔢 Checking data types and format...")
    
    # Check date column
    try:
        df['date'] = pd.to_datetime(df['date'])
        print("✅ Date column format is valid")
    except Exception as e:
        print(f"❌ ERROR: Invalid date format: {e}")
        print("   Please use YYYY-MM-DD format (e.g., 2019-01-31)")
        return False
    
    # Check cases column
    try:
        df['cases'] = pd.to_numeric(df['cases'], errors='coerce')
        print("✅ Cases column format is valid")
    except Exception as e:
        print(f"❌ ERROR: Invalid cases format: {e}")
        print("   Please use whole numbers only (no decimals)")
        return False
    
    # Check 5: Missing values
    print(f"🔍 Checking for missing values...")
    missing_dates = df['date'].isnull().sum()
    missing_cases = df['cases'].isnull().sum()
    
    if missing_dates > 0 or missing_cases > 0:
        print(f"❌ ERROR: Missing values found!")
        print(f"   Missing dates: {missing_dates}")
        print(f"   Missing cases: {missing_cases}")
        return False
    print("✅ No missing values")
    
    # Check 6: Negative case numbers
    print(f"📈 Checking case number validity...")
    negative_cases = (df['cases'] < 0).sum()
    if negative_cases > 0:
        print(f"❌ ERROR: Found {negative_cases} negative case numbers!")
        print("   Please use non-negative integers only")
        return False
    print("✅ All case numbers are non-negative")
    
    # Check 7: Date format consistency
    print(f"📅 Checking date format consistency...")
    date_strings = df['date'].dt.strftime('%Y-%m-%d')
    original_strings = df['date'].astype(str)
    
    if not all(date_strings == original_strings):
        print("❌ ERROR: Inconsistent date format!")
        print("   Please ensure all dates are in YYYY-MM-DD format")
        return False
    print("✅ Date format is consistent")
    
    # Check 8: Chronological order
    print(f"⏰ Checking chronological order...")
    if not df['date'].is_monotonic_increasing:
        print("❌ WARNING: Data is not in chronological order!")
        print("   This may cause issues with the calibration")
        print("   Consider sorting the data by date")
    else:
        print("✅ Data is in chronological order")
    
    # Check 9: Data requirements
    print(f"📋 Checking data requirements...")
    total_months = len(df)
    time_span = (df['date'].max() - df['date'].min()).days / 30.44  # Approximate months
    
    print(f"   Total observations: {total_months}")
    print(f"   Time span: {time_span:.1f} months")
    
    if total_months < 12:
        print("❌ WARNING: Less than 12 months of data!")
        print("   Calibration may not work well with limited data")
    elif total_months >= 12:
        print("✅ Sufficient data for calibration")
    
    # Check 10: Data summary
    print(f"📊 Data summary:")
    print(f"   Time period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"   Total cases: {df['cases'].sum():,}")
    print(f"   Average cases per month: {df['cases'].mean():.1f}")
    print(f"   Minimum cases per month: {df['cases'].min()}")
    print(f"   Maximum cases per month: {df['cases'].max()}")
    
    # Check for reasonable case numbers
    avg_cases = df['cases'].mean()
    if avg_cases < 1:
        print("⚠️  WARNING: Very low case numbers detected")
        print("   This may indicate data quality issues or very small population")
    elif avg_cases > 1000:
        print("⚠️  WARNING: Very high case numbers detected")
        print("   This may indicate data quality issues or very large population")
    else:
        print("✅ Case numbers appear reasonable")
    
    print("\n" + "=" * 50)
    print("✅ DATA VALIDATION COMPLETE - FILE IS READY FOR CALIBRATION!")
    print("=" * 50)
    
    return True

def main():
    """Main function to run validation"""
    # Check if filename provided as argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'data/tetanus_monthly_cases.csv'
    
    # Run validation
    is_valid = validate_tetanus_data(filename)
    
    if is_valid:
        print("\n🎉 Your data file is ready to use with the calibration script!")
        print("   Run: python scripts/run_calib_tetanus.py")
    else:
        print("\n❌ Please fix the issues above before running the calibration script.")
        print("   See docs/Tetanus_Data_Format_Specification.md for detailed requirements.")
        print("   To extract tetanus data from zerodose_data.csv, run: python scripts/extract_tetanus_data.py")
    
    return is_valid

if __name__ == "__main__":
    main() 