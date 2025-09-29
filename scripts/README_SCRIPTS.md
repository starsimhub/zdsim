# Zero-Dose Vaccination Simulation Scripts

## Overview
This directory contains the most important scripts for the zero-dose vaccination simulation model. Redundant and less essential scripts have been removed to keep only the core functionality.

## Core Scripts

### **1. Main Simulation Scripts**

#### **`run_zerodose_simulation.py`** - **MOST IMPORTANT**
- **Purpose**: Main simulation script for zero-dose vaccination model
- **Features**: Runs baseline vs vaccination scenarios for all 5 diseases
- **Usage**: `python scripts/run_zerodose_simulation.py`
- **Output**: Comprehensive results and plots for all diseases

#### **`test_full_model.py`**
- **Purpose**: Tests the complete zero-dose vaccination model
- **Features**: Full model validation and testing
- **Usage**: `python scripts/test_full_model.py`

#### **`final_demo.py`**
- **Purpose**: Comprehensive demonstration of the model
- **Features**: Baseline vs vaccination comparison with detailed plots
- **Usage**: `python scripts/final_demo.py`

### **2. Disease-Specific Analysis**

#### **`simple_tetanus_analysis.py`** - **TETANUS FOCUS**
- **Purpose**: Enhanced tetanus-focused analysis
- **Features**: Detailed tetanus simulation with enhanced plots
- **Usage**: `python scripts/simple_tetanus_analysis.py`

#### **`tetanus_focused_analysis.py`**
- **Purpose**: Comprehensive tetanus analysis
- **Features**: Baseline vs vaccination tetanus comparison
- **Usage**: `python scripts/tetanus_focused_analysis.py`

#### **`tetanus_parameter_check.py`** - **VALIDATION**
- **Purpose**: Validates tetanus model against document requirements
- **Features**: Parameter validation and outcome verification
- **Usage**: `python scripts/tetanus_parameter_check.py`

### **3. Calibration and Validation**

#### **`calibration_system.py`** - **CALIBRATION**
- **Purpose**: Calibrates disease parameters against real-world data
- **Features**: Parameter optimization and calibration
- **Usage**: `python scripts/calibration_system.py`

#### **`calibrated_parameters_violin.py`** - **VIOLIN PLOTS**
- **Purpose**: Creates violin plots for calibrated parameters
- **Features**: Parameter distribution visualization
- **Usage**: `python scripts/calibrated_parameters_violin.py`

### **4. Validation Scripts**

#### **`scientific_validation.py`**
- **Purpose**: Scientific validation of model parameters
- **Features**: Validates against literature values
- **Usage**: `python scripts/scientific_validation.py`

#### **`epidemiological_validation.py`**
- **Purpose**: Epidemiological validation of model
- **Features**: Age distribution and disease pattern validation
- **Usage**: `python scripts/epidemiological_validation.py`

#### **`real_world_validation.py`**
- **Purpose**: Real-world data validation
- **Features**: Validates against WHO targets and real data
- **Usage**: `python scripts/real_world_validation.py`

#### **`simple_validation.py`**
- **Purpose**: Simple model validation
- **Features**: Basic parameter and outcome validation
- **Usage**: `python scripts/simple_validation.py`

### **5. Analysis and Reporting**

#### **`model_challenges.py`**
- **Purpose**: Identifies model challenges and limitations
- **Features**: Scientific fact checking and challenge identification
- **Usage**: `python scripts/model_challenges.py`

#### **`final_validation_summary.py`**
- **Purpose**: Comprehensive validation summary
- **Features**: Summarizes all validation results
- **Usage**: `python scripts/final_validation_summary.py`

### **6. Examples and Utilities**

#### **`example_usage.py`**
- **Purpose**: Example usage of the simulation
- **Features**: Basic usage examples and plotting
- **Usage**: `python scripts/example_usage.py`

#### **`generic/run_zdsim.py`**
- **Purpose**: Generic simulation runner
- **Features**: Flexible simulation execution
- **Usage**: `python scripts/generic/run_zdsim.py`

## Script Categories

### **Essential Scripts (Must Keep)**
1. **`run_zerodose_simulation.py`** - Main simulation
2. **`tetanus_parameter_check.py`** - Document validation
3. **`calibration_system.py`** - Parameter calibration
4. **`calibrated_parameters_violin.py`** - Parameter visualization

### **Important Scripts (Recommended)**
1. **`simple_tetanus_analysis.py`** - Tetanus focus
2. **`test_full_model.py`** - Model testing
3. **`final_demo.py`** - Comprehensive demo
4. **`scientific_validation.py`** - Scientific validation

### **Supporting Scripts (Optional)**
1. **`epidemiological_validation.py`** - Epidemiological validation
2. **`real_world_validation.py`** - Real-world validation
3. **`model_challenges.py`** - Challenge identification
4. **`example_usage.py`** - Usage examples

## Usage Recommendations

### **For Basic Usage**:
```bash
# Run main simulation
python scripts/run_zerodose_simulation.py

# Validate tetanus parameters
python scripts/tetanus_parameter_check.py

# Run tetanus-focused analysis
python scripts/simple_tetanus_analysis.py
```

### **For Calibration**:
```bash
# Calibrate parameters
python scripts/calibration_system.py

# View calibrated parameter distributions
python scripts/calibrated_parameters_violin.py
```

### **For Validation**:
```bash
# Scientific validation
python scripts/scientific_validation.py

# Full model testing
python scripts/test_full_model.py
```

## Removed Scripts

The following scripts were removed as they were redundant or less essential:

- `simple_tetanus_validation.py` (redundant with tetanus_parameter_check.py)
- `tetanus_document_validation.py` (redundant with tetanus_parameter_check.py)
- `simple_violin_plots.py` (redundant with calibrated_parameters_violin.py)
- `violin_plots_comparison.py` (redundant with calibrated_parameters_violin.py)
- `enhanced_calibrated_violin.py` (redundant with calibrated_parameters_violin.py)
- `demo_violin_plots.py` (redundant with calibrated_parameters_violin.py)
- `simple_test.py` (redundant with test_full_model.py)
- `debug_disease.py` (debugging script, not needed for production)
- `run_pneumonia.py` (pneumonia not implemented)
- `test_zerodose.py` (redundant with test_full_model.py)

## Summary

The scripts directory now contains only the most important and essential scripts for the zero-dose vaccination simulation model. This provides a clean, organized structure with clear purposes for each script while removing redundancy and less essential functionality.
