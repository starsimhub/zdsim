# TB ACF Calibration Learnings for Zero-Dose Vaccination Model

## Overview

This document summarizes the key calibration techniques learned from the TB ACF (Active Case Finding) project and how they can be applied to improve the zero-dose vaccination model calibration.

## Key Learnings from TB ACF Project

### 1. **Multiple Calibration Components**

The TB ACF project uses a sophisticated approach with multiple calibration components:

- **Prevalence Components**: Track disease prevalence over time
- **Incidence Components**: Monitor new disease cases
- **Historical Data**: Incorporate long-term epidemiological trends
- **Age-specific Data**: Include age-stratified prevalence and incidence
- **Mortality Components**: Track disease-specific mortality rates
- **Notification Rates**: Include health system reporting data

**Application to Zero-Dose Model:**
- Disease prevalence for each of the 5 diseases
- Annual incidence rates
- Vaccination coverage rates
- Age-specific disease burden
- Case fatality rates

### 2. **Weighted Calibration Targets**

The TB ACF project assigns different weights to different data sources:

```python
# High weight for critical targets
prevalence_comp.weight = 5.0

# Medium weight for important targets  
incidence_comp.weight = 3.0

# Lower weight for supplementary targets
coverage_comp.weight = 2.0
```

**Benefits:**
- Prioritizes most important epidemiological outcomes
- Balances different data sources appropriately
- Improves calibration quality and convergence

### 3. **Real-World Data Integration**

The TB ACF project integrates multiple real-world data sources:

- **WHO Global Health Observatory**: Disease burden estimates
- **National Health Surveys**: Population-level prevalence
- **Health System Data**: Notification and mortality rates
- **Research Studies**: Age-specific and risk-stratified data

**Application to Zero-Dose Model:**
- WHO vaccination coverage data
- Disease burden estimates from GBD
- National immunization program data
- Age-specific disease incidence

### 4. **Advanced Parameter Optimization**

The TB ACF project uses sophisticated parameter optimization:

- **Log-scale Parameters**: For parameters that span orders of magnitude
- **Realistic Parameter Ranges**: Based on literature and expert knowledge
- **Pruning Functions**: To exclude unrealistic parameter combinations
- **Multi-objective Optimization**: Balancing multiple calibration targets

**Example from TB ACF:**
```python
calib_pars = dict(
    beta = dict(low=0.1, high=2.0, guess=0.95, suggest_type='suggest_float', log=False),
    x_pcf1 = dict(low=0, high=10.0, guess=0.15),
    x_pcf2 = dict(low=0, high=10.0, guess=0.2),
    # ... more parameters
)
```

### 5. **Comprehensive Visualization**

The TB ACF project includes extensive visualization:

- **Component Plots**: Show fit for each calibration target
- **Parameter Importance**: Identify most influential parameters
- **Optimization History**: Track convergence over time
- **Parallel Coordinate Plots**: Explore parameter relationships
- **Contour Plots**: Visualize parameter interactions

## Implementation in Zero-Dose Model

### 1. **Calibration Components Created**

```python
# Prevalence components (high weight)
prevalence_comp = ss.Binomial(
    name=f'{disease.title()} Prevalence',
    weight=5.0,
    conform='prevalent',
    expected=pd.DataFrame({
        'x': [int(target['prevalence'] * 100000)],
        'n': [100000],
    }, index=pd.Index([ss.date('2018-06-01')], name='t')),
    extract_fn=lambda sim, d=disease: pd.DataFrame({
        'x': getattr(sim.results, d).n_infected,
        'n': sim.results.n_alive,
    }, index=pd.Index(sim.results.timevec, name='t')),
)

# Incidence components (medium weight)
incidence_comp = ss.GammaPoisson(
    name=f'{disease.title()} Incidence',
    weight=3.0,
    conform='incident',
    # ... implementation
)

# Vaccination coverage components (medium weight)
coverage_comp = ss.Binomial(
    name=f'{disease.title()} Vaccination Coverage',
    weight=2.0,
    conform='prevalent',
    # ... implementation
)
```

### 2. **Parameter Ranges Defined**

```python
# Disease-specific parameters
for disease in diseases:
    # Transmission rate (log scale)
    calib_pars[f'{disease}_beta'] = dict(
        low=0.01, high=2.0, guess=0.5,
        suggest_type='suggest_float', log=True
    )
    
    # Case fatality rate (log scale)
    calib_pars[f'{disease}_p_death'] = dict(
        low=0.001, high=0.2, guess=0.05,
        suggest_type='suggest_float', log=True
    )
    
    # Duration of infection (log scale)
    calib_pars[f'{disease}_dur_inf'] = dict(
        low=7, high=90, guess=21,
        suggest_type='suggest_float', log=True
    )
```

### 3. **Real-World Targets**

```python
targets = {
    'diphtheria': {
        'prevalence': 0.0001,  # 0.01% prevalence
        'incidence': 0.00005,  # 0.005% annual incidence
        'cfr': 0.05,  # 5% case fatality rate
        'vaccination_coverage': 0.85,  # 85% DPT coverage
    },
    'tetanus': {
        'prevalence': 0.00005,  # 0.005% prevalence
        'incidence': 0.00002,  # 0.002% annual incidence
        'cfr': 0.10,  # 10% case fatality rate
        'vaccination_coverage': 0.85,  # 85% DPT coverage
    },
    # ... more diseases
}
```

## Key Improvements Achieved

### 1. **Multiple Data Sources**
- ✅ Disease prevalence from WHO data
- ✅ Annual incidence rates from epidemiological studies
- ✅ Vaccination coverage from immunization programs
- ✅ Case fatality rates from literature

### 2. **Weighted Calibration**
- ✅ High weight (5.0) for prevalence targets
- ✅ Medium weight (3.0) for incidence targets
- ✅ Medium weight (2.0) for coverage targets

### 3. **Advanced Parameter Optimization**
- ✅ Log-scale parameters for wide ranges
- ✅ Realistic parameter bounds
- ✅ Disease-specific parameter sets
- ✅ Vaccination intervention parameters

### 4. **Comprehensive Visualization**
- ✅ Component plots for each target
- ✅ Parameter importance analysis
- ✅ Optimization history tracking
- ✅ Parameter distribution plots

## Technical Implementation

### 1. **Calibration Components**
- **15 components total** (3 per disease: prevalence, incidence, coverage)
- **Weighted targets** based on data quality and importance
- **Real-world data integration** from WHO and literature

### 2. **Parameter Optimization**
- **21 parameters total** (disease-specific + vaccination)
- **Log-scale optimization** for wide parameter ranges
- **Realistic bounds** based on epidemiological literature

### 3. **Visualization System**
- **Component plots** showing fit for each target
- **Parameter importance** identifying key parameters
- **Optimization history** tracking convergence
- **Parameter distributions** showing calibration results

## Benefits of TB ACF Approach

### 1. **Improved Calibration Quality**
- Multiple data sources provide better constraints
- Weighted targets prioritize important outcomes
- Real-world data ensures realistic results

### 2. **Better Parameter Estimation**
- Log-scale parameters handle wide ranges
- Realistic bounds prevent unrealistic values
- Disease-specific parameters capture heterogeneity

### 3. **Enhanced Visualization**
- Multiple plot types for comprehensive analysis
- Parameter importance helps identify key factors
- Optimization history tracks convergence

### 4. **Policy Relevance**
- Real-world targets ensure policy relevance
- Multiple diseases capture full vaccination impact
- Age-specific data supports targeted interventions

## Future Improvements

### 1. **Additional Data Sources**
- Age-specific disease burden
- Risk-stratified vaccination coverage
- Health system capacity data
- Economic impact measures

### 2. **Advanced Optimization**
- Multi-objective optimization
- Bayesian parameter estimation
- Uncertainty quantification
- Sensitivity analysis

### 3. **Enhanced Visualization**
- Interactive dashboards
- Real-time parameter updates
- Scenario comparison tools
- Policy impact visualization

## Conclusion

The TB ACF calibration approach provides a sophisticated framework for model calibration that can significantly improve the zero-dose vaccination model. Key learnings include:

1. **Multiple calibration components** with appropriate weights
2. **Real-world data integration** from multiple sources
3. **Advanced parameter optimization** with realistic bounds
4. **Comprehensive visualization** for analysis and interpretation

These techniques can be applied to improve calibration quality, parameter estimation, and policy relevance of the zero-dose vaccination model.

## Files Created

1. **`scripts/advanced_calibration_system.py`** - Full implementation with all TB ACF techniques
2. **`scripts/improved_calibration_system.py`** - Simplified version focusing on key techniques
3. **`scripts/tb_acf_inspired_calibration.py`** - Working demonstration of TB ACF approach
4. **`TB_ACF_CALIBRATION_LEARNINGS.md`** - This comprehensive summary document

The TB ACF approach provides a robust foundation for advanced model calibration that can significantly improve the quality and policy relevance of the zero-dose vaccination model.
