# Zero-Dose Vaccination Simulation Model

This repository contains a comprehensive agent-based model (ABM) for simulating zero-dose vaccination interventions targeting five vaccine-preventable diseases.

## Overview

The zero-dose vaccination model simulates the impact of vaccinating children who have received zero doses of routine vaccines. The model targets five diseases commonly prevented by the DTP-HepB-Hib vaccine:

1. **Diphtheria** - Bacterial infection causing severe respiratory illness
2. **Tetanus** - Bacterial infection from wound contamination
3. **Pertussis** - Highly contagious respiratory disease (whooping cough)
4. **Hepatitis B** - Viral infection causing chronic liver disease
5. **Hib** - Bacterial infection causing meningitis and pneumonia

## Model Structure

### Disease Modules
Each disease is implemented as a separate module with disease-specific parameters:
- Transmission rates (beta)
- Initial prevalence
- Duration of infection
- Case fatality rates
- Disease-specific outcomes (severe disease, chronic infection, etc.)

### Vaccination Intervention
The `ZeroDoseVaccination` intervention class implements:
- Age-targeted vaccination (typically 0-60 months)
- Coverage rates and vaccine efficacy
- Routine and campaign delivery modes
- Immunity tracking and waning

### Population Dynamics
- Birth and death rates
- Age-structured population
- Contact networks (household and community)
- Disease transmission dynamics

## Usage

### Basic Simulation

```python
import zdsim as zds
import starsim as ss

# Create diseases
diseases = [
    zds.Diphtheria(),
    zds.Tetanus(),
    zds.Pertussis(),
    zds.HepatitisB(),
    zds.Hib()
]

# Create vaccination intervention
vaccination = zds.ZeroDoseVaccination(dict(
    coverage=0.8,      # 80% coverage
    efficacy=0.9,      # 90% efficacy
    age_min=0,         # 0 months
    age_max=60         # 60 months
))

# Create simulation
sim = ss.Sim(
    people=ss.People(n_agents=10000),
    diseases=diseases,
    networks=[ss.RandomNet(dict(n_contacts=10, dur=0))],
    demographics=[ss.Births(dict(birth_rate=25)), ss.Deaths(dict(death_rate=8))],
    interventions=[vaccination],
    pars=dict(start=2020, stop=2030, dt=1/52)
)

# Run simulation
sim.run()
```

### Running Baseline vs Vaccination Comparison

```python
# Run the full comparison script
python scripts/run_zerodose_simulation.py
```

### Testing the Implementation

```python
# Run tests
python scripts/test_zerodose.py
```

## Key Features

### Disease-Specific Modeling
- **Diphtheria**: High transmission, moderate severity
- **Tetanus**: Environmental exposure, high case fatality
- **Pertussis**: High transmission, immunity waning
- **Hepatitis B**: Chronic infection, age-dependent susceptibility
- **Hib**: High severity in children, meningitis outcomes

### Vaccination Strategies
- **Routine vaccination**: Continuous vaccination of eligible children
- **Campaign vaccination**: Targeted vaccination campaigns
- **Age targeting**: Focus on children 0-60 months
- **Coverage tracking**: Monitor vaccination coverage over time

### Results and Analysis
- Disease prevalence over time
- Cumulative infections and deaths
- Vaccination coverage and impact
- Cases averted by vaccination
- Age-specific outcomes

## Model Parameters

### Disease Parameters
Each disease has configurable parameters:
- `beta`: Transmission rate per year
- `init_prev`: Initial prevalence
- `dur_inf`: Duration of infection
- `p_death`: Case fatality rate
- `p_severe`: Probability of severe disease

### Vaccination Parameters
- `coverage`: Vaccination coverage rate
- `efficacy`: Vaccine efficacy
- `age_min/max`: Age range for vaccination
- `routine_prob`: Annual routine vaccination probability

### Population Parameters
- `n_agents`: Population size
- `birth_rate`: Births per 1000 population per year
- `death_rate`: Deaths per 1000 population per year
- Contact network parameters

## Output and Visualization

The model generates comprehensive outputs:
- Disease prevalence over time
- Cumulative infections and deaths
- Vaccination coverage rates
- Impact metrics (cases averted, percentage reduction)
- Comparative plots between baseline and vaccination scenarios

## File Structure

```
zdsim/
├── diseases/
│   ├── __init__.py
│   ├── diphtheria.py
│   ├── tetanus.py
│   ├── pertussis.py
│   ├── hepatitis_b.py
│   └── hib.py
├── interventions.py
├── base.py
├── plots.py
└── __init__.py

scripts/
├── run_zerodose_simulation.py
└── test_zerodose.py
```

## Dependencies

- starsim (agent-based modeling framework)
- numpy
- matplotlib
- sciris
- pandas

## Example Results

The model can demonstrate significant impact of zero-dose vaccination:
- 60-80% reduction in disease cases
- Prevention of severe outcomes
- Improved population immunity
- Age-specific protection benefits

## Future Enhancements

- Integration with real epidemiological data
- Spatial modeling capabilities
- Cost-effectiveness analysis
- Sensitivity analysis tools
- Multi-country comparisons

## Citation

If you use this model in your research, please cite:
```
Zero-Dose Vaccination ABM Model
Institute for Disease Modeling
2025
```
