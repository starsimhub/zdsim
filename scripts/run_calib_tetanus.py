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
    2019-01-31,12
    2019-02-28,10
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
from zdsim import *
import pandas as pd
import matplotlib.pyplot as plt
from starsim.calibration import Calibration
from starsim.calib_components import Normal
import matplotlib.dates as mdates
from plots import plot_model_vs_data, plot_baseline_vs_data, plot_baseline_vs_intervention
from sim_tetanus import make_tetanus


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
    print("\n=== Tetanus Model Calibration Pipeline ===\n")
    # --- Calibration block ---
    # Load real data from CSV
    try:
        # Read the CSV file with your real tetanus case data
        data_df = pd.read_csv('tetanus_monthly_cases.csv')
        print("Loaded input data from tetanus_monthly_cases.csv")
    except Exception as e:
        # If the file is missing or not formatted correctly, print a clear error and stop
        print("ERROR: Could not load 'tetanus_monthly_cases.csv'. Please ensure the file exists and is formatted correctly.")
        print("Expected columns: 'date', 'cases'. Example row: 2019-01-31,12")
        raise e
    # Convert the 'date' column to datetime objects for easier handling
    data_df['date'] = pd.to_datetime(data_df['date'])
    # Do NOT sort the data; keep the order as in the CSV to match the model's timeline
    data_df = data_df.set_index('date')  # Set the date as the index (does not sort)
    # Prepare calibration data: index must match model output (monthly)
    # This ensures the model and data are compared on the same timeline
    calib_data = data_df['cases'].values
    calib_dates = data_df.index
    calib_df = pd.DataFrame({'t': np.arange(len(calib_data)), 'n_infected': calib_data})
    calib_df = calib_df.set_index('t')

    # Define which parameters to calibrate (fit to data)
    # beta: how easily tetanus spreads; init_prev: how many people are infected at the start
    calib_pars = dict(
        beta=dict(low=0.1, high=10, guess=5.0),         # Try values between 0.1 and 10
        init_prev=dict(low=0.01, high=0.5, guess=0.3),  # Try values between 0.01 and 0.5
    )

    # Define the build function for calibration
    # This function updates the simulation with the current set of parameters being tested
    def build_fn(sim, calib_pars=None, **kwargs):
        if sim is None:
            raise ValueError('build_fn received sim=None. Cannot proceed.')
        tetanus = None
        # Find the tetanus disease object in the simulation
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
                if hasattr(tetanus.pars, k):
                    setattr(tetanus.pars, k, v['value'] if isinstance(v, dict) and 'value' in v else v)
        if sim is None:
            raise ValueError('build_fn is returning sim=None!')
        return sim

    # Set up the calibration component
    # This tells the calibration process how to compare the model's output to your real data
    expected = calib_df.rename(columns={'n_infected': 'x'}).reset_index()[['t', 'x']]
    def safe_extract_fn(sim):
        # This function extracts the number of infected people from the simulation results
        if sim is None:
            raise ValueError('extract_fn received sim=None. This usually means build_fn failed to return a valid simulation object.')
        if not hasattr(sim, 'results') or sim.results is None:
            raise ValueError('extract_fn: sim.results is None. Simulation may have failed to run.')
        if 'tetanus' not in sim.results or 'n_infected' not in sim.results['tetanus']:
            raise ValueError('extract_fn: sim.results does not contain tetanus/n_infected.')
        return pd.DataFrame({
            't': np.arange(len(sim.results['tetanus']['n_infected'])),
            'x': sim.results['tetanus']['n_infected'],
            'rand_seed': getattr(sim.pars, 'rand_seed', 0)
        })
    component = Normal(
        name='n_infected',
        expected=expected,
        extract_fn=safe_extract_fn,
        conform='none',
        weight=1.0
    )

    # Create the base simulation with default parameters
    print("Building base simulation...")
    base_sim = make_tetanus()

    # Set up and run the calibration
    print("Starting calibration (this may take a few minutes)...")
    calib = Calibration(
        sim=base_sim,
        calib_pars=calib_pars,
        build_fn=build_fn,
        components=[component],
        total_trials=30,  # Number of different parameter sets to try; increase for better fit
        n_workers=1,      # Number of parallel workers; increase if you have a powerful computer
        verbose=True      # Print progress information
    )
    calib.calibrate()
    print("Calibration complete.")
    # Check the fit visually (shows a plot)
    calib.check_fit()

    # --- Main simulation code follows ---
    # Use the best-fit parameters found during calibration
    best_pars = calib.best_pars
    print(f"Best-fit parameters: {best_pars}")
    # Convert beta from per-year to per-step (monthly) rate
    # This is necessary because the model runs in monthly steps
    beta_per_year = best_pars['beta']
    beta_per_step = 1 - np.exp(-beta_per_year * (1/12))
    print(f"Converted beta (per-step): {beta_per_step:.4f}")
    # Create a new simulation with the best-fit parameters
    print("Running best-fit simulation...")
    sim = make_tetanus(disease_pars=dict(beta=beta_per_step, init_prev=best_pars['init_prev']))
    sim.run()
    
    # # Plot the results for visual inspection
    # tet : ss.Disease = sim.diseases['tetanus']
    # tet.plot()

    # --- Output model results to CSV ---
    # Save the model's predictions to a CSV file for further analysis
    model_cases = sim.results['tetanus']['n_infected']
    model_dates = pd.date_range(start='2019-01-01', periods=len(model_cases), freq='ME')
    model_df = pd.DataFrame({'date': model_dates, 'model_cases': model_cases})
    model_df.to_csv('model_tetanus_cases.csv', index=False)
    print("Model results saved to model_tetanus_cases.csv")

    # --- Load real data from CSV again for plotting ---
    # This ensures the plot uses the original data
    try:
        data_df = pd.read_csv('tetanus_monthly_cases.csv')
        data_df['date'] = pd.to_datetime(data_df['date'])
        data_dates = data_df['date']
        data_cases = data_df['cases']
    except Exception as e:
        print('Could not load real data:', e)
        data_dates = []
        data_cases = []

    # --- Plot model vs. data ---
    print("Plotting model vs. data after calibration...")
    plot_model_vs_data(model_dates, model_cases, data_dates, data_cases, filename='model_vs_data_after_calibration.png')

    # --- Baseline simulation (no intervention) ---
    print("Running baseline simulation (no intervention)...")
    baseline_dis = Tetanus(dict(beta=beta_per_step, init_prev=best_pars['init_prev']))
    baseline_sim = ss.Sim(
        n_agents=10000,
        diseases=baseline_dis,
        start='2019-01-01',
        stop='2025-01-31',
        dt=1/12,
        verbose=0.25  # Controls how much progress info is printed
    )
    baseline_sim.run()
    baseline_cases = baseline_sim.results['tetanus']['n_infected']
    baseline_dates = pd.date_range(start='2019-01-01', periods=len(baseline_cases), freq='ME')

    # --- Intervention simulation (e.g., higher vaccine_prob) ---
    print("Running intervention simulation (increased vaccine_prob)...")
    
    # Here, vaccine_prob is set to 0.5 (50% chance of being vaccinated)
    intervention_dis = Tetanus(pars=dict(beta=beta_per_step, init_prev=best_pars['init_prev'], vaccine_prob=0.5))
    
    intervention_sim = ss.Sim(
        n_agents=10000,
        diseases=intervention_dis,
        start='2019-01-01',
        stop='2025-01-31',
        dt=1/12,
        verbose=0.25
    )
    intervention_sim.run()
    intervention_cases = intervention_sim.results['tetanus']['n_infected']
    intervention_dates = pd.date_range(start='2019-01-01', periods=len(intervention_cases), freq='ME')

    # -------------------------- Output both model results to CSV -------------
    
    # Save baseline and intervention results for comparison
    baseline_df = pd.DataFrame({'date': baseline_dates, 'baseline_cases': baseline_cases})
    intervention_df = pd.DataFrame({'date': intervention_dates, 'intervention_cases': intervention_cases})
    baseline_df.to_csv('baseline_tetanus_cases.csv', index=False)
    intervention_df.to_csv('intervention_tetanus_cases.csv', index=False)
    print("Baseline results saved to baseline_tetanus_cases.csv")
    print("Intervention results saved to intervention_tetanus_cases.csv")

    # --------------------------- Plot: Model before calibration ---
    print("Plotting baseline model vs. data (before calibration)...")
    plot_baseline_vs_data(baseline_dates, baseline_cases, data_dates, data_cases)

    # --------------------------- Plot: Model after calibration/intervention ---
    print("Plotting baseline vs. intervention vs. data (after calibration/intervention)...")
    plot_baseline_vs_intervention(baseline_dates, baseline_cases, intervention_dates, intervention_cases, data_dates, data_cases)
    print("\n=== Pipeline complete. See output CSVs and plots for results. ===\n")


# ===============================
# Main Entry Point
# ===============================

if __name__ == '__main__':
    # Entry point for running the full pipeline
    # You can run this script directly: python run_zdsim.py
    run_calib()