# Results Folder Structure

## 📁 **ORGANIZED OUTPUT STRUCTURE**

All simulation outputs are now organized in a dedicated `results/` folder for better file management and clarity.

## **📂 FOLDER STRUCTURE**

```
zdsimjuly/
├── data/                           # Input data files
│   ├── zerodose_data.csv          # Original source data
│   └── tetanus_monthly_cases.csv  # Extracted tetanus data
├── scripts/                        # Python scripts
│   ├── run_calib_tetanus.py       # Main calibration script
│   ├── extract_tetanus_data.py    # Data extraction script
│   ├── validate_tetanus_data.py   # Data validation script
│   └── plots.py                   # Plotting functions
├── results/                        # 🆕 OUTPUT FOLDER
│   ├── model_tetanus_cases.csv    # Calibrated model results
│   ├── baseline_tetanus_cases.csv # Baseline scenario results
│   ├── intervention_tetanus_cases.csv # Intervention scenario results
│   ├── model_vs_data_after_calibration.png
│   ├── baseline_vs_data.png
│   └── baseline_vs_intervention.png
└── docs/                          # Documentation
```

## **📊 OUTPUT FILES IN RESULTS FOLDER**

### **CSV Data Files**
- **`model_tetanus_cases.csv`**: Model predictions after calibration
  - Columns: `date`, `model_cases`, `real_cases`
  - Shows how well the calibrated model matches real data

- **`baseline_tetanus_cases.csv`**: Baseline scenario (no intervention)
  - Columns: `date`, `baseline_cases`
  - Shows tetanus cases without additional vaccination

- **`intervention_tetanus_cases.csv`**: Intervention scenario (with vaccination)
  - Columns: `date`, `intervention_cases`
  - Shows tetanus cases with zero-dose vaccination intervention

### **PNG Plot Files**
- **`model_vs_data_after_calibration.png`**: Model fit visualization
  - Shows calibrated model predictions vs. real data
  - Demonstrates calibration quality

- **`baseline_vs_data.png`**: Baseline model performance
  - Shows baseline model vs. real data
  - Reference for calibration improvement

- **`baseline_vs_intervention.png`**: Intervention impact
  - Compares baseline vs. intervention scenarios
  - Shows vaccination intervention effectiveness

## **🔄 WORKFLOW WITH NEW STRUCTURE**

### **Step 1: Extract Data**
```bash
python scripts/extract_tetanus_data.py
# Creates: data/tetanus_monthly_cases.csv
```

### **Step 2: Validate Data**
```bash
python scripts/validate_tetanus_data.py
# Validates: data/tetanus_monthly_cases.csv
```

### **Step 3: Run Calibration**
```bash
python scripts/run_calib_tetanus.py
# Creates: results/*.csv and results/*.png
```

### **Step 4: Review Results**
- Check `results/` folder for all outputs
- Open CSV files for detailed analysis
- View PNG plots for visual assessment

## **✅ BENEFITS OF NEW STRUCTURE**

1. **Clean Organization**: All outputs in one dedicated folder
2. **Easy Access**: Clear separation of inputs (data/) and outputs (results/)
3. **Version Control**: Results folder can be easily excluded from git
4. **Reproducibility**: Clear input/output structure for reproducibility
5. **Documentation**: Self-documenting folder structure

## **🔧 TECHNICAL DETAILS**

### **Automatic Folder Creation**
The calibration script automatically creates the `results/` folder if it doesn't exist:
```python
os.makedirs('results', exist_ok=True)
```

### **File Path Updates**
All file save operations now use the `results/` prefix:
- `model_tetanus_cases.csv` → `results/model_tetanus_cases.csv`
- `baseline_tetanus_cases.csv` → `results/baseline_tetanus_cases.csv`
- `intervention_tetanus_cases.csv` → `results/intervention_tetanus_cases.csv`
- Plot files → `results/*.png`

### **Data Input Path**
The script now reads from the `data/` folder:
- `tetanus_monthly_cases.csv` → `data/tetanus_monthly_cases.csv`

## **📝 USAGE NOTES**

- The `results/` folder is created automatically when running the calibration script
- Previous output files in the root directory are no longer created
- All plotting functions now save to the results folder
- The validation script checks the correct data folder location
- The extraction script saves to the data folder as before

This structure provides a clean, organized approach to managing simulation outputs while maintaining clear separation between inputs and results. 