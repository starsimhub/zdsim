# Zero-Dose Vaccination Simulation Scripts

## Overview
This directory contains the most important scripts for the zero-dose vaccination simulation model. All scripts have been clearly named to immediately indicate their purpose and functionality.

## Core Scripts

### **1. Main Simulation Scripts**

#### **`main_zero_dose_simulation.py`** - **MOST IMPORTANT**
- **Purpose**: Main simulation script for zero-dose vaccination model
- **Features**: Runs baseline vs vaccination scenarios for all 5 diseases
- **Usage**: `python scripts/main_zero_dose_simulation.py`
- **Output**: Comprehensive results and plots for all diseases

#### **`test_complete_model.py`**
- **Purpose**: Tests the complete zero-dose vaccination model
- **Features**: Full model validation and testing
- **Usage**: `python scripts/test_complete_model.py`

#### **`comprehensive_demo.py`**
- **Purpose**: Comprehensive demonstration of the model
- **Features**: Baseline vs vaccination comparison with detailed plots
- **Usage**: `python scripts/comprehensive_demo.py`

#### **`basic_usage_examples.py`**
- **Purpose**: Basic usage examples and tutorials
- **Features**: Simple examples for getting started
- **Usage**: `python scripts/basic_usage_examples.py`

### **2. Disease-Specific Analysis**

#### **`tetanus_analysis_simple.py`** - **TETANUS FOCUS**
- **Purpose**: Simple tetanus-focused analysis
- **Features**: Single tetanus simulation with enhanced plots
- **Usage**: `python scripts/tetanus_analysis_simple.py`

#### **`tetanus_analysis_comprehensive.py`**
- **Purpose**: Comprehensive tetanus analysis
- **Features**: Baseline vs vaccination tetanus comparison
- **Usage**: `python scripts/tetanus_analysis_comprehensive.py`

#### **`tetanus_parameter_validation.py`** - **VALIDATION**
- **Purpose**: Validates tetanus model against document requirements
- **Features**: Parameter validation and outcome verification
- **Usage**: `python scripts/tetanus_parameter_validation.py`

### **3. Calibration and Validation**

#### **`parameter_calibration_system.py`** - **CALIBRATION**
- **Purpose**: Calibrates disease parameters against real-world data
- **Features**: Parameter optimization and calibration
- **Usage**: `python scripts/parameter_calibration_system.py`

#### **`parameter_distribution_plots.py`** - **VIOLIN PLOTS**
- **Purpose**: Creates violin plots of calibrated parameters
- **Features**: Parameter distribution visualization
- **Usage**: `python scripts/parameter_distribution_plots.py`

#### **`scientific_parameter_validation.py`** - **SCIENTIFIC VALIDATION**
- **Purpose**: Validates parameters against scientific literature
- **Features**: Literature-based parameter validation
- **Usage**: `python scripts/scientific_parameter_validation.py`

#### **`epidemiological_analysis.py`** - **EPIDEMIOLOGICAL VALIDATION**
- **Purpose**: Validates epidemiological aspects of the model
- **Features**: Age distribution and transmission validation
- **Usage**: `python scripts/epidemiological_analysis.py`

#### **`real_world_data_validation.py`** - **REAL-WORLD VALIDATION**
- **Purpose**: Validates model against real-world data and WHO targets
- **Features**: Real-world data comparison and validation
- **Usage**: `python scripts/real_world_data_validation.py`

#### **`basic_model_validation.py`** - **BASIC VALIDATION**
- **Purpose**: Basic model validation and testing
- **Features**: Simple validation of parameters and vaccination impact
- **Usage**: `python scripts/basic_model_validation.py`

#### **`model_limitations_analysis.py`** - **LIMITATIONS ANALYSIS**
- **Purpose**: Identifies and analyzes model challenges and limitations
- **Features**: Model constraint assessment and limitation documentation
- **Usage**: `python scripts/model_limitations_analysis.py`

#### **`validation_results_summary.py`** - **VALIDATION SUMMARY**
- **Purpose**: Summarizes validation results and provides recommendations
- **Features**: Comprehensive validation summary and recommendations
- **Usage**: `python scripts/validation_results_summary.py`

### **4. Key Features Demonstration**

#### **`key_features_demonstration.py`** - **KEY FEATURES DEMO**
- **Purpose**: Comprehensive demonstration of all model key features
- **Features**: Disease-specific modeling, vaccination strategies, results analysis
- **Usage**: `python scripts/key_features_demonstration.py`

### **5. Data-Driven Analysis Scripts**

#### **`real_data_loader.py`** - **REAL DATA ANALYSIS**
- **Purpose**: Loads and analyzes real-world epidemiological data
- **Features**: Real data loading, disease burden analysis, policy insights
- **Usage**: `python scripts/real_data_loader.py`

#### **`data_driven_calibration.py`** - **DATA-DRIVEN CALIBRATION**
- **Purpose**: Calibrates model parameters against real-world data
- **Features**: Parameter calibration, model validation, policy recommendations
- **Usage**: `python scripts/data_driven_calibration.py`

#### **`policy_decision_support.py`** - **POLICY DECISION SUPPORT**
- **Purpose**: Comprehensive policy analysis and decision support
- **Features**: Scenario analysis, cost-effectiveness, decision dashboard
- **Usage**: `python scripts/policy_decision_support.py`

#### **`policy_implementation_guide.py`** - **POLICY IMPLEMENTATION GUIDE**
- **Purpose**: Comprehensive guide for implementing zero-dose vaccination policies
- **Features**: Implementation roadmap, resource requirements, risk mitigation
- **Usage**: `python scripts/policy_implementation_guide.py`

### **6. Generic Scripts**

#### **`generic/run_generic_simulation.py`** - **GENERIC RUNNER**
- **Purpose**: Generic script for running zero-dose vaccination simulations
- **Features**: Flexible parameter setting and basic simulation execution
- **Usage**: `python scripts/generic/run_generic_simulation.py`

## Script Categories

### **Main Simulation Scripts (4 scripts)**
- Core simulation functionality
- Baseline vs vaccination scenarios
- Comprehensive results and analysis

### **Disease-Specific Analysis (3 scripts)**
- Tetanus-focused analysis
- Parameter validation
- Disease-specific insights

### **Calibration and Validation (8 scripts)**
- Parameter calibration system
- Scientific validation
- Real-world data validation
- Model limitations analysis

### **Key Features Demonstration (1 script)**
- Comprehensive feature demonstration
- All model capabilities shown

### **Data-Driven Analysis Scripts (4 scripts)**
- Real-world data integration
- Evidence-based parameter calibration
- Policy decision support
- Implementation guidance

### **Generic Scripts (1 script)**
- Flexible simulation running

## Usage Recommendations

### **For Basic Usage:**
1. Start with `main_zero_dose_simulation.py` for complete simulation
2. Use `basic_usage_examples.py` for basic examples
3. Use `tetanus_analysis_simple.py` for tetanus-specific analysis

### **For Advanced Analysis:**
1. Use `tetanus_analysis_comprehensive.py` for comprehensive tetanus analysis
2. Use `parameter_calibration_system.py` for parameter calibration
3. Use validation scripts for model validation

### **For Model Validation:**
1. Run all validation scripts to ensure model accuracy
2. Use `validation_results_summary.py` for comprehensive validation
3. Check `model_limitations_analysis.py` for model limitations

### **For Key Features Demonstration:**
1. Use `key_features_demonstration.py` to see all model capabilities
2. Demonstrates disease-specific modeling, vaccination strategies, and results analysis

### **For Data-Driven Policy Analysis:**
1. Use `real_data_loader.py` to analyze real-world epidemiological data
2. Use `data_driven_calibration.py` to calibrate model against real data
3. Use `policy_decision_support.py` for comprehensive policy analysis
4. Use `policy_implementation_guide.py` for implementation guidance

## Key Features Demonstrated

All scripts demonstrate the key features of the zero-dose vaccination model:

1. **Disease-Specific Modeling** - Each disease has unique characteristics
2. **Vaccination Strategies** - Multiple vaccination approaches
3. **Results and Analysis** - Comprehensive metrics and outputs
4. **Model Validation** - Scientific and real-world validation
5. **Parameter Calibration** - Calibrated against real-world data

## Clear Naming Convention

All scripts now have clear, descriptive names that immediately indicate their purpose:

- **`main_`** - Main/core functionality
- **`test_`** - Testing and validation
- **`comprehensive_`** - Full-featured analysis
- **`basic_`** - Simple/basic functionality
- **`tetanus_`** - Tetanus-specific analysis
- **`parameter_`** - Parameter-related functionality
- **`validation_`** - Validation and testing
- **`analysis_`** - Analysis and insights
- **`demonstration_`** - Feature demonstration

The scripts are now clearly named and organized for easy understanding and use. Each script name immediately indicates its purpose and functionality.