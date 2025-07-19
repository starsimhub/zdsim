"""
TETANUS Agent-Based Model (ABM) Simulation Pipeline
==================================================

This script is for researchers who want to analyze tetanus transmission and intervention scenarios using real data. It uses an agent-based model (ABM), which simulates individual people and their interactions. The script is designed to be as clear and explicit as possible, so you can use it even if you are not a coding expert.

What this script does, step by step:
1. Loads your real tetanus case data from a CSV file ('tetanus_monthly_cases.csv').
2. Calibrates (fits) the model to your data, so the model's predictions match your real-world observations as closely as possible.
3. Runs the model under different scenarios: baseline (no extra intervention) and intervention (e.g., increased vaccination).
4. Saves the results as CSV files and creates plots for you to review and use in your research.

**Input data requirements:**
- The file must be named 'tetanus_monthly_cases.csv' and be in the same folder as this script.
- The file must have two columns: 'date' (YYYY-MM-DD) and 'cases' (number of cases for that month).
- Example:
    date,cases
    2018-01-31,12
    2018-02-28,10
    ...

**Outputs:**
- model_tetanus_cases.csv: Model's best estimate after calibration.
- baseline_tetanus_cases.csv: Model results with no extra intervention.
- intervention_tetanus_cases.csv: Model results with increased vaccination.
- model_vs_data_after_calibration.png: Plot comparing model and data.

If you encounter errors, the script will print clear messages about what went wrong and how to fix it. Make sure you have the required Python packages installed (see comments in the script).
"""

import sciris as sc
import numpy as np
import starsim as ss
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from zdsim.disease_models.tetanus import Tetanus
from zdsim.interventions import ZeroDoseVaccination
from plots import plot_model_vs_data, plot_baseline_vs_data, plot_baseline_vs_intervention

from starsim.calibration import Calibration
from starsim.calib_components import Normal
CALIBRATION_AVAILABLE = True


# ===============================
# Simulation Construction
# ===============================

def make_tetanus_baseline(sim_pars=None, disease_pars=None):
    """
    Create and configure a tetanus simulation WITHOUT interventions for calibration.
    """
    
    # Set up default simulation parameters
    sim_params = dict(
        start=sc.date('2018-02-01'),  # Simulation start date
        stop=sc.date('2025-01-31'),   # Simulation end date
        dt=1/12,                      # Time step: 1/12 = monthly
    )
    # If the user provides custom simulation parameters, update the defaults
    if sim_pars:
        sim_params.update(sim_pars)

    # Set up the disease (tetanus) with default or user-provided parameters
    default_disease_pars = dict(
        beta=ss.rate_prob(1.3),           # Transmission rate (Beta)
        gamma=ss.rate_prob(3/12),         # Recovery rate (Gamma) - 3 months
        waning=ss.rate_prob(0.055),       # Immunity waning rate
        p_death=ss.bernoulli(p=0.05),     # Case fatality rate
        vaccine_efficacy=0.9,             # Vaccine efficacy (90%)
        vaccine_prob=0.25,                # Vaccination probability
    )
    
    if disease_pars:
        # Update with user-provided parameters
        for key, value in disease_pars.items():
            if key == 'beta':
                default_disease_pars['beta'] = ss.rate_prob(value)
            elif key == 'gamma':
                default_disease_pars['gamma'] = ss.rate_prob(value)
            elif key == 'waning':
                default_disease_pars['waning'] = ss.rate_prob(value)
            else:
                default_disease_pars[key] = value
    
    tetanus = Tetanus(default_disease_pars)

    # Set up the simulation object WITHOUT interventions for calibration
    sim = ss.Sim(
        n_agents=10000,  # Population size
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),  # Random contact network: each person has 5 contacts
        diseases=tetanus,  # Add the tetanus disease
        demographics=[ss.Births(dict(birth_rate=250)), ss.Deaths(dict(death_rate=10))], 
        pars=sim_params,  # Simulation parameters
        verbose=0.1  # Controls how much progress information is printed
    )
    
    return sim

def make_tetanus(sim_pars=None, disease_pars=None):
    """
    Create and configure a tetanus simulation using Starsim WITH interventions.
    """
    
    # Set up default simulation parameters
    sim_params = dict(
        start=sc.date('2018-02-01'),  # Simulation start date
        stop=sc.date('2025-01-31'),   # Simulation end date
        dt=1/12,                      # Time step: 1/12 = monthly
    )
    # If the user provides custom simulation parameters, update the defaults
    if sim_pars:
        sim_params.update(sim_pars)

    # Set up the vaccination intervention with real data parameters
    intervention = ZeroDoseVaccination(
        start_year=2018,
        end_year=2025,
        target_age_min=0,
        target_age_max=5,
        coverage_rate=0.22,  # Based on real data: current 7% + 15% improvement target
        vaccine_efficacy=0.9,  # Updated to match specifications
        campaign_frequency=2,
        seasonal_timing=True
    )

    # Set up the disease (tetanus) with default or user-provided parameters
    default_disease_pars = dict(
        beta=ss.rate_prob(1.3),           # Transmission rate (Beta)
        gamma=ss.rate_prob(3/12),         # Recovery rate (Gamma) - 3 months
        waning=ss.rate_prob(0.055),       # Immunity waning rate
        p_death=ss.bernoulli(p=0.05),     # Case fatality rate
        vaccine_efficacy=0.9,             # Vaccine efficacy (90%)
        vaccine_prob=0.25,                # Vaccination probability
    )
    
    if disease_pars:
        # Update with user-provided parameters
        for key, value in disease_pars.items():
            if key == 'beta':
                default_disease_pars['beta'] = ss.rate_prob(value)
            elif key == 'gamma':
                default_disease_pars['gamma'] = ss.rate_prob(value)
            elif key == 'waning':
                default_disease_pars['waning'] = ss.rate_prob(value)
            else:
                default_disease_pars[key] = value
    
    tetanus = Tetanus(default_disease_pars)

    # Set up the simulation object
    sim = ss.Sim(
        n_agents=10000,  # Population size
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),  # Random contact network: each person has 5 contacts
        diseases=tetanus,  # Add the tetanus disease
        interventions=intervention,  # Add the vaccination intervention
        demographics=[ss.Births(dict(birth_rate=250)), ss.Deaths(dict(death_rate=10))], 
        pars=sim_params,  # Simulation parameters
        verbose=0.1  # Controls how much progress information is printed
    )
    
    return sim


# ===============================
# Calibration and Analysis Pipeline
# ===============================

def run_calib():  
    """
    Run the calibration pipeline for the TETANUS model.

    This is the main function that does all the work. It is designed to be as explicit as possible, so you always know what is happening and why.

    Step-by-step, this function:
    1. Loads your real tetanus data from CSV. If the file is missing or not formatted correctly, the script will stop and tell you what to fix.
    2. Sets up the model and the parameters to be fitted (like how easily tetanus spreads and how many people are initially infected).
    3. Fits the model to your data by trying many parameter values and picking the best. This is called "calibration" and ensures the model matches your data as closely as possible.
    4. Runs the model with the best-fit parameters.
    5. Runs two scenarios: baseline (no extra intervention) and intervention (e.g., more vaccination).
    6. Saves the results as CSV files and creates plots for you to review and use in your research.

    Why this is important:
    - Calibration is essential for making sure the model's predictions are realistic for your setting.
    - Running different scenarios lets you see the potential impact of interventions.
    - The outputs (CSVs and plots) are designed to be easy to use in further analysis or presentations.

    What to check:
    - The script prints progress messages so you know what it's doing.
    - If you get an error about the CSV file, check that it's named correctly and formatted as described above.
    - The output files (CSVs and plots) are saved in the same folder as the script.
    - You can open the CSVs in Excel or R for further analysis.
    - The plots show how well the model matches your data, and what happens with interventions.

    You do not need to change anything in this function to use the script. If you want to adjust parameters or try different interventions, you can do so by editing the relevant parts of the script (ask for help if needed).
    """
    # Define output directory and date suffix for filenames
    from datetime import datetime
    date_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
    resdr = 'results'
    try:
        data_df = pd.read_csv('data/tetanus_monthly_cases.csv')
    except Exception as e:
        print("ERROR: Could not load 'data/tetanus_monthly_cases.csv'. Please ensure the file exists and is formatted correctly.")
        print("Expected columns: 'date', 'cases'. Example row: 2018-01-31,12")
        print("To validate your data file, run: python scripts/validate_tetanus_data.py")
        print("To extract tetanus data from zerodose_data.csv, run: python scripts/extract_tetanus_data.py")
        raise e
    
    # Convert the 'date' column to datetime objects for easier handling
    data_df['date'] = pd.to_datetime(data_df['date'])
    
    # Do NOT sort the data; keep the order as in the CSV to match the model's timeline
    data_df = data_df.set_index('date')  # Set the date as the index (does not sort)
    
    # Prepare calibration data: index must match model output (monthly)
    # This ensures the model and data are compared on the same timeline
    calib_data = data_df['cases'].values
    # calib_dates = data_df.index
    calib_df = pd.DataFrame({'t': np.arange(len(calib_data)), 'x': calib_data})
    calib_df = calib_df.set_index('t')

    # Define which parameters to calibrate (fit to data)
    # Using the specified model parameters from the specifications
    calib_pars = dict(
        beta=dict(low=1.0, high=2.0, guess=1.3),           # Transmission rate (Beta)
        gamma=dict(low=0.2, high=0.4, guess=0.25),         # Recovery rate (Gamma) - 3 months = 0.25
        waning=dict(low=0.01, high=0.1, guess=0.055),      # Immunity waning rate
    )

    # Define the build function for calibration
    # This function updates the simulation with the current set of parameters being tested
    def build_fn(sim, calib_pars=None, **kwargs):
        # Create a deep copy of the simulation to avoid modifying the original
        sim = sc.dcp(sim)
        
        # Find the tetanus disease object in the simulation
        tetanus = None
        if hasattr(sim, 'diseases'):
            if isinstance(sim.diseases, dict):
                tetanus = sim.diseases.get('tetanus', None)
            elif isinstance(sim.diseases, list):
                for d in sim.diseases:
                    if d.__class__.__name__.lower() == 'tetanus':
                        tetanus = d
                        break
        
        # Update the disease parameters with the current calibration values
        if tetanus is not None and calib_pars is not None:
            for k, v in calib_pars.items():
                if k == 'rand_seed':
                    continue  # Skip random seed
                value = v['value'] if isinstance(v, dict) and 'value' in v else v
                if k == 'beta':
                    # Update transmission rate (Beta)
                    tetanus.pars.beta = ss.rate_prob(value)
                elif k == 'gamma':
                    # Update recovery rate (Gamma)
                    tetanus.pars.gamma = ss.rate_prob(value)
                elif k == 'waning':
                    # Update immunity waning rate
                    tetanus.pars.waning = ss.rate_prob(value)
        
        # Ensure all parameters are properly initialized as rate_prob objects
        if tetanus is not None:
            if not hasattr(tetanus.pars.beta, 'rvs'):
                tetanus.pars.beta = ss.rate_prob(tetanus.pars.beta)
            if not hasattr(tetanus.pars.gamma, 'rvs'):
                tetanus.pars.gamma = ss.rate_prob(tetanus.pars.gamma)
            if not hasattr(tetanus.pars.waning, 'rvs'):
                tetanus.pars.waning = ss.rate_prob(tetanus.pars.waning)
        
        # Set initial infections manually (1% of population)
        if tetanus is not None:
            n_agents = len(tetanus.susceptible)
            n_init_inf = int(n_agents * 0.01)  # 1% initial prevalence
            if n_init_inf > 0:
                init_inf_uids = np.random.choice(n_agents, size=n_init_inf, replace=False)
                tetanus.set_prognoses(init_inf_uids)
        
        return sim

    # Set up the calibration component
    # This tells the calibration process how to compare the model's output to your real data
    expected = calib_df.reset_index()[['t', 'x']]
    
    def safe_extract_fn(sim):
        # This function extracts the number of infected people from the simulation results
        # Try different ways to access the results
        tetanus_results = None
        if hasattr(sim, 'results') and sim.results and 'tetanus' in sim.results:
            tetanus_results = sim.results['tetanus']
        elif hasattr(sim, 'diseases') and len(sim.diseases) > 0:
            # Try to get results from the first disease
            first_disease = list(sim.diseases.values())[0] if isinstance(sim.diseases, dict) else sim.diseases[0]
            if hasattr(first_disease, 'results'):
                tetanus_results = first_disease.results
        
        if tetanus_results is None or 'n_infected' not in tetanus_results:
            # Fallback: count infected individuals directly
            infected_count = []
            for disease in sim.diseases.values() if isinstance(sim.diseases, dict) else sim.diseases:
                if hasattr(disease, 'infected'):
                    infected_count.append(np.sum(disease.infected))
                else:
                    infected_count.append(0)
            infected_data = np.array(infected_count)
        else:
            infected_data = tetanus_results['n_infected']
        
        return pd.DataFrame({
            't': np.arange(len(infected_data)),
            'x': infected_data,
            'rand_seed': getattr(sim.pars, 'rand_seed', 0)
        })
    
    # Use calibration components if available
    if CALIBRATION_AVAILABLE:
        component = Normal(
            name='n_infected',
            expected=expected,
            extract_fn=safe_extract_fn,
            conform='none',
            weight=1.0
        )

        # Create the base simulation with default parameters (no interventions for calibration)
        base_sim = make_tetanus_baseline()

        # Set up and run the calibration
        calib = Calibration(
            sim=base_sim,
            calib_pars=calib_pars,
            build_fn=build_fn,
            components=[component],
            total_trials=200,  # Number of different parameter sets to try; increase for better fit
            n_workers=1,      # Number of parallel workers; increase if you have a powerful computer
            verbose=True      # Print progress information
        )
        calib.calibrate()
        # Check the fit visually (shows a plot)
        calib.check_fit(do_plot=False)

        # Use the best-fit parameters found during calibration
        best_pars = calib.best_pars
        
    else:
        print("Warning: Starsim calibration not available. Using default parameters.")
        best_pars = {'exposure_risk': 0.001, 'init_prev': 0.3}
    
    # Create a new simulation with the best-fit parameters
    # Filter out rand_seed from disease parameters
    disease_pars = {k: v for k, v in best_pars.items() if k != 'rand_seed'}
    sim = make_tetanus(disease_pars=disease_pars)
    sim.run()
    
    # --- Output model results to CSV ---
    # Save the model's predictions to a CSV file for further analysis
    # Extract results from the simulation
    model_cases = []
    if hasattr(sim, 'results') and sim.results and 'tetanus' in sim.results and 'n_infected' in sim.results['tetanus']:
        model_cases = sim.results['tetanus']['n_infected']
    else:
        # Fallback: count infected individuals
        for disease in sim.diseases.values() if isinstance(sim.diseases, dict) else sim.diseases:
            if hasattr(disease, 'infected'):
                model_cases.append(np.sum(disease.infected))
            else:
                model_cases.append(0)
    
    # Ensure results folder exists
    os.makedirs(resdr, exist_ok=True)
    
    model_dates = pd.date_range(start='2018-02-01', periods=len(model_cases), freq='ME')
    model_df = pd.DataFrame({'date': model_dates, 'model_cases': model_cases})
    model_df.to_csv(f'{resdr}/model_tetanus_cases_{date_suffix}.csv', index=False)

    # --- Load real data from CSV again for plotting ---
    # This ensures the plot uses the original data
    try:
        data_df = pd.read_csv('data/tetanus_monthly_cases.csv')
        data_df['date'] = pd.to_datetime(data_df['date'])
        data_dates = data_df['date']
        data_cases = data_df['cases']
    except Exception as e:
        print('Could not load real data:', e)
        data_dates = []
        data_cases = []

    # --- Plot model vs. data ---
    plot_model_vs_data(model_dates, model_cases, data_dates, data_cases, filename=f'{resdr}/model_vs_data_after_calibration_{date_suffix}.png')

    # --- Baseline simulation (no intervention) ---
    baseline_dis = Tetanus(dict(
        beta=ss.rate_prob(best_pars.get('beta', 1.3)),
        gamma=ss.rate_prob(best_pars.get('gamma', 3/12)),
        waning=ss.rate_prob(best_pars.get('waning', 0.055)),
        p_death=ss.bernoulli(p=0.05),
        vaccine_efficacy=0.9,
        vaccine_prob=0.25,
    ))
    baseline_sim = ss.Sim(
        n_agents=10000,
        diseases=baseline_dis,
        start='2018-02-01',
        stop='2025-01-31',
        dt=1/12,
        verbose=0.25  # Controls how much progress info is printed
    )
    baseline_sim.run()
    
    # Extract baseline results
    baseline_cases = []
    if hasattr(baseline_sim, 'results') and baseline_sim.results and 'tetanus' in baseline_sim.results and 'n_infected' in baseline_sim.results['tetanus']:
        baseline_cases = baseline_sim.results['tetanus']['n_infected']
    else:
        for disease in baseline_sim.diseases.values() if isinstance(baseline_sim.diseases, dict) else baseline_sim.diseases:
            if hasattr(disease, 'infected'):
                baseline_cases.append(np.sum(disease.infected))
            else:
                baseline_cases.append(0)
    
    baseline_dates = pd.date_range(start='2018-02-01', periods=len(baseline_cases), freq='ME')

    # --- Intervention simulation (with vaccination) ---
    # Create intervention simulation with vaccination
    intervention_sim = make_tetanus(disease_pars=disease_pars)
    intervention_sim.run()
    
    # Extract intervention results
    intervention_cases = []
    if hasattr(intervention_sim, 'results') and intervention_sim.results and 'tetanus' in intervention_sim.results and 'n_infected' in intervention_sim.results['tetanus']:
        intervention_cases = intervention_sim.results['tetanus']['n_infected']
    else:
        for disease in intervention_sim.diseases.values() if isinstance(intervention_sim.diseases, dict) else intervention_sim.diseases:
            if hasattr(disease, 'infected'):
                intervention_cases.append(np.sum(disease.infected))
            else:
                intervention_cases.append(0)
    
    intervention_dates = pd.date_range(
                                    start='2018-02-01', 
                                    periods=len(intervention_cases), 
                                    freq='ME'
                                    )

    # -------------------------- Output both model results to CSV -------------
    # Save baseline and intervention results for comparison
    baseline_df = pd.DataFrame({'date': baseline_dates, 'baseline_cases': baseline_cases})
    intervention_df = pd.DataFrame({'date': intervention_dates, 'intervention_cases': intervention_cases})

    baseline_df.to_csv(f'{resdr}/baseline_tetanus_cases_{date_suffix}.csv', index=False)
    intervention_df.to_csv(f'{resdr}/intervention_tetanus_cases_{date_suffix}.csv', index=False)
    plot_baseline_vs_data(baseline_dates, baseline_cases, data_dates, data_cases, filename=f'{resdr}/baseline_vs_data_{date_suffix}.png')   #Plot: Model before calibration
    plot_baseline_vs_intervention(baseline_dates, baseline_cases, intervention_dates, intervention_cases, data_dates, data_cases, filename=f'{resdr}/baseline_vs_intervention_{date_suffix}.png')  # Plot: Model after calibration/intervention


# ===============================
# Main Entry Point
# ===============================

if __name__ == '__main__':
    # Entry point for running the full pipeline
    run_calib()