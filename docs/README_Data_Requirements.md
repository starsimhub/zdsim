# Data Requirements for Tetanus Calibration

## 📋 **QUICK START - DATA REQUIREMENTS**

Before running the tetanus calibration script, you need to prepare your data file in the correct format.

### **Required File**
- **Filename**: `tetanus_monthly_cases.csv`
- **Location**: Same directory as the script
- **Format**: CSV (Comma-Separated Values)

### **Required Format**
```csv
date,cases
2019-01-31,15
2019-02-28,12
2019-03-31,18
...
```

### **Quick Validation**
Run this command to check if your data is formatted correctly:
```bash
python scripts/validate_tetanus_data.py
```

## **📊 DETAILED DATA SPECIFICATIONS**

### **Column Requirements**

| Column | Type | Format | Example | Description |
|--------|------|--------|---------|-------------|
| `date` | Date | YYYY-MM-DD | `2019-01-31` | Last day of each month |
| `cases` | Integer | Whole number | `15` | Number of tetanus cases |

### **Data Rules**
1. **Dates**: Use last day of each month (e.g., `2019-01-31`, `2019-02-28`)
2. **Cases**: Non-negative integers only (no decimals, no negative numbers)
3. **Order**: Chronological order (earliest to latest)
4. **Completeness**: No missing values or empty rows
5. **Minimum**: At least 12 months of data (recommended: 24-72 months)

### **Example Data**
```csv
date,cases
2019-01-31,15
2019-02-28,12
2019-03-31,18
2019-04-30,14
2019-05-31,22
2019-06-30,19
2019-07-31,25
2019-08-31,21
2019-09-30,17
2019-10-31,20
2019-11-30,16
2019-12-31,23
```

## **🔧 DATA PREPARATION TOOLS**

### **1. Validation Script**
Check if your data is formatted correctly:
```bash
python scripts/validate_tetanus_data.py
```

### **2. Example Data File**
Use the provided example file as a template:
- **File**: `tetanus_monthly_cases.csv` (included in the project)
- **Contains**: 72 months of sample data (2019-2024)

### **3. Detailed Specification**
For complete format requirements:
- **Document**: `docs/Tetanus_Data_Format_Specification.md`
- **Contains**: Complete validation rules, error solutions, and examples

## **🚨 COMMON ISSUES AND SOLUTIONS**

### **File Not Found**
```
ERROR: Could not load 'tetanus_monthly_cases.csv'
```
**Solution**: 
- Check file name is exactly `tetanus_monthly_cases.csv`
- Ensure file is in the same directory as the script

### **Wrong Column Names**
```
KeyError: 'date' or KeyError: 'cases'
```
**Solution**:
- Ensure column headers are exactly `date,cases`
- Check for extra spaces or special characters

### **Invalid Date Format**
```
ValueError: time data '2019/01/31' does not match format '%Y-%m-%d'
```
**Solution**:
- Use `YYYY-MM-DD` format (e.g., `2019-01-31`)
- Use last day of each month

### **Invalid Case Numbers**
```
ValueError: invalid literal for int() with base 10: '15.5'
```
**Solution**:
- Use whole numbers only (no decimals)
- No negative numbers

## **📝 STEP-BY-STEP DATA PREPARATION**

### **Option 1: Using the Example File**
1. Copy the provided `tetanus_monthly_cases.csv` file
2. Replace the sample data with your real data
3. Keep the same format and structure
4. Run validation: `python scripts/validate_tetanus_data.py`

### **Option 2: Creating from Scratch**
1. Open a text editor (Notepad, TextEdit, VS Code)
2. Add header: `date,cases`
3. Add your data rows (one per month)
4. Save as `tetanus_monthly_cases.csv`
5. Run validation: `python scripts/validate_tetanus_data.py`

### **Option 3: Using Excel/Google Sheets**
1. Create two columns: `date` and `cases`
2. Format dates as `YYYY-MM-DD`
3. Format cases as whole numbers
4. Export as CSV
5. Run validation: `python scripts/validate_tetanus_data.py`

## **📈 DATA QUALITY RECOMMENDATIONS**

### **Optimal Data Characteristics**
- **Time Period**: 2-6 years of monthly data
- **Consistency**: Regular monthly reporting
- **Completeness**: No missing months
- **Quality**: Realistic case numbers for population size
- **Variability**: Some seasonal or temporal variation

### **Data Quality Checks**
- **Reasonable Case Numbers**: 1-1000 cases per month (typical range)
- **Chronological Order**: Dates in ascending order
- **No Gaps**: Continuous monthly data
- **Consistent Format**: All dates and numbers in same format

## **✅ VALIDATION CHECKLIST**

Before running the calibration script, ensure:

- [ ] File named exactly `tetanus_monthly_cases.csv`
- [ ] File located in same directory as script
- [ ] Column headers: `date,cases`
- [ ] Date format: `YYYY-MM-DD`
- [ ] Case numbers: integers (no decimals)
- [ ] No missing values
- [ ] Chronological order
- [ ] At least 12 months of data
- [ ] Validation script passes: `python scripts/validate_tetanus_data.py`

## **📞 GETTING HELP**

### **If You Encounter Issues**

1. **Run the validation script**:
   ```bash
   python scripts/validate_tetanus_data.py
   ```

2. **Check the detailed specification**:
   - Read: `docs/Tetanus_Data_Format_Specification.md`

3. **Use the example file**:
   - Copy: `tetanus_monthly_cases.csv`
   - Replace data with your own

4. **Common solutions**:
   - Ensure no extra spaces in column headers
   - Use correct date format (YYYY-MM-DD)
   - Use whole numbers for cases
   - Check file is saved as CSV format

### **Example Validation Output**
```
🔍 VALIDATING TETANUS DATA FILE
==================================================
📁 Checking file existence: tetanus_monthly_cases.csv
✅ File exists
📖 Checking CSV format...
✅ File can be read as CSV
📊 Checking column structure...
✅ Column structure is correct
🔢 Checking data types and format...
✅ Date column format is valid
✅ Cases column format is valid
🔍 Checking for missing values...
✅ No missing values
📈 Checking case number validity...
✅ All case numbers are non-negative
📅 Checking date format consistency...
✅ Date format is consistent
⏰ Checking chronological order...
✅ Data is in chronological order
📋 Checking data requirements...
   Total observations: 72
   Time span: 71.0 months
✅ Sufficient data for calibration
📊 Data summary:
   Time period: 2019-01-31 to 2024-12-31
   Total cases: 1,829
   Average cases per month: 25.4
   Minimum cases per month: 12
   Maximum cases per month: 37
✅ Case numbers appear reasonable

==================================================
✅ DATA VALIDATION COMPLETE - FILE IS READY FOR CALIBRATION!
==================================================

🎉 Your data file is ready to use with the calibration script!
   Run: python scripts/run_calib_tetanus.py
```

## **🎯 NEXT STEPS**

Once your data is validated:

1. **Run the calibration script**:
   ```bash
   python scripts/run_calib_tetanus.py
   ```

2. **Review the results**:
   - Check generated CSV files
   - Examine the plots
   - Review calibration parameters

3. **Analyze the output**:
   - Model predictions vs real data
   - Baseline vs intervention scenarios
   - Calibration quality metrics

**Status**: **DATA REQUIREMENTS DOCUMENTATION COMPLETE** 📋 