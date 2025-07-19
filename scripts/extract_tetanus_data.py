#!/usr/bin/env python3
"""
Extract Tetanus Data from Zero Dose Data
========================================

This script extracts tetanus-related data from the zerodose_data.csv file
and formats it according to the calibration script requirements.

The script will:
1. Load the zerodose_data.csv file
2. Extract tetanus-related columns
3. Convert to the required format (date, cases)
4. Save as data/tetanus_monthly_cases.csv
"""

import pandas as pd
import os
from datetime import datetime
import calendar

def extract_tetanus_data():
    """
    Extract tetanus data from zerodose_data.csv and format for calibration
    """
    print("🔍 EXTRACTING TETANUS DATA FROM ZERODOSE DATA")
    print("=" * 50)
    
    # Load the zerodose data
    try:
        df = pd.read_csv('data/zerodose_data.csv')
        print("✅ Loaded zerodose_data.csv")
    except Exception as e:
        print(f"❌ ERROR: Could not load data/zerodose_data.csv: {e}")
        return False
    
    # Check for tetanus-related columns
    tetanus_columns = ['neonatal_tetanus', 'peri_neonatal_tetanus', 'tetanus', 'tetanus_inpatient']
    available_columns = [col for col in tetanus_columns if col in df.columns]
    
    print(f"📊 Found tetanus columns: {available_columns}")
    
    if not available_columns:
        print("❌ ERROR: No tetanus-related columns found in the data")
        return False
    
    # Create the output data
    output_data = []
    
    for _, row in df.iterrows():
        year = row['year']
        month = row['month']
        
        # Convert month name to number
        month_num = datetime.strptime(month, '%B').month
        
        # Calculate total tetanus cases (sum of all available tetanus columns)
        total_cases = 0
        for col in available_columns:
            if pd.notna(row[col]):
                total_cases += int(row[col])
        
        # Get the last day of the month
        last_day = calendar.monthrange(year, month_num)[1]
        
        # Create date string in YYYY-MM-DD format
        date_str = f"{year}-{month_num:02d}-{last_day:02d}"
        
        output_data.append({
            'date': date_str,
            'cases': total_cases
        })
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data)
    
    # Sort by date
    output_df['date'] = pd.to_datetime(output_df['date'])
    output_df = output_df.sort_values('date')
    output_df['date'] = output_df['date'].dt.strftime('%Y-%m-%d')
    
    # Ensure data folder exists
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_file = 'data/tetanus_monthly_cases.csv'
    output_df.to_csv(output_file, index=False)
    
    print(f"✅ Saved tetanus data to {output_file}")
    print(f"📊 Data summary:")
    print(f"   - Time period: {output_df['date'].min()} to {output_df['date'].max()}")
    print(f"   - Total months: {len(output_df)}")
    print(f"   - Total cases: {output_df['cases'].sum():,}")
    print(f"   - Average cases per month: {output_df['cases'].mean():.1f}")
    print(f"   - Minimum cases per month: {output_df['cases'].min()}")
    print(f"   - Maximum cases per month: {output_df['cases'].max()}")
    
    # Show first few rows
    print(f"\n📋 First 5 rows of extracted data:")
    print(output_df.head().to_string(index=False))
    
    # Validate the output
    print(f"\n🔍 Validating extracted data...")
    try:
        # Check if the file can be read back
        test_df = pd.read_csv(output_file)
        print("✅ Output file can be read successfully")
        
        # Check column structure
        if list(test_df.columns) == ['date', 'cases']:
            print("✅ Column structure is correct")
        else:
            print("❌ ERROR: Wrong column structure")
            return False
        
        # Check data types
        test_df['date'] = pd.to_datetime(test_df['date'])
        test_df['cases'] = pd.to_numeric(test_df['cases'])
        print("✅ Data types are correct")
        
        # Check for missing values
        if test_df.isnull().any().any():
            print("❌ ERROR: Missing values found")
            return False
        else:
            print("✅ No missing values")
        
        # Check for negative cases
        if (test_df['cases'] < 0).any():
            print("❌ ERROR: Negative case numbers found")
            return False
        else:
            print("✅ All case numbers are non-negative")
        
        print("✅ Data validation passed!")
        
    except Exception as e:
        print(f"❌ ERROR during validation: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ TETANUS DATA EXTRACTION COMPLETE!")
    print("=" * 50)
    print(f"📁 Output file: {output_file}")
    print(f"📊 Ready for calibration: python scripts/run_calib_tetanus.py")
    
    return True

def main():
    """Main function"""
    success = extract_tetanus_data()
    
    if success:
        print("\n🎉 Tetanus data extraction successful!")
        print("   The data is now ready for calibration.")
    else:
        print("\n❌ Tetanus data extraction failed!")
        print("   Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    main() 