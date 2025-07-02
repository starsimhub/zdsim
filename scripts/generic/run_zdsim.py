import sciris as sc
import numpy as np
import starsim as ss
from zdsim import *
import pandas as pd
import matplotlib.pyplot as plt
from starsim.calibration import Calibration
from starsim.calib_components import Normal
import matplotlib.dates as mdates

"""
run_zdsim.py

This script provides a full pipeline for simulating, calibrating, and analyzing tetanus disease dynamics using the Starsim agent-based modeling framework. It includes:
    - Construction of a simulation with configurable parameters and interventions
    - Calibration of model parameters to real-world data
    - Output of model results and comparison to observed data
    - Visualization and CSV export of baseline and intervention scenarios

Usage:
    Run this script directly to perform calibration and generate outputs:
        python run_zdsim.py

Requirements:
    - starsim
    - sciris
    - numpy
    - pandas
    - matplotlib
    - tetanus_monthly_cases.csv (input data)

Outputs:
    - model_tetanus_cases.csv
    - baseline_tetanus_cases.csv
    - intervention_tetanus_cases.csv
    - model_vs_data_after_calibration.png

"""

def plot_model_vs_data(model_dates, model_cases, data_dates, data_cases, filename=None):
    """
    Plot model-predicted cases vs. real data after calibration.

    Args:
        model_dates (array-like): Dates for model predictions.
        model_cases (array-like): Model-predicted case counts.
        data_dates (array-like): Dates for observed data.
        data_cases (array-like): Observed case counts.
        filename (str, optional): If provided, save the plot to this file.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(model_dates, model_cases, label='Model')
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model after calibration')
    plt.legend()
    plt.tight_layout()
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()
    if filename:
        plt.savefig(filename)
    plt.show()

def plot_baseline_vs_data(baseline_dates, baseline_cases, data_dates, data_cases):
    """
    Plot baseline model-predicted cases vs. real data before calibration.

    Args:
        baseline_dates (array-like): Dates for baseline model predictions.
        baseline_cases (array-like): Baseline model-predicted case counts.
        data_dates (array-like): Dates for observed data.
        data_cases (array-like): Observed case counts.
    """
    plt.figure(figsize=(8,6))
    plt.plot(baseline_dates, baseline_cases, label='Model')
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model before calibration')
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_baseline_vs_intervention(baseline_dates, baseline_cases, intervention_dates, intervention_cases, data_dates, data_cases):
    """
    Plot baseline and intervention model-predicted cases vs. real data after calibration/intervention.

    Args:
        baseline_dates (array-like): Dates for baseline model predictions.
        baseline_cases (array-like): Baseline model-predicted case counts.
        intervention_dates (array-like): Dates for intervention model predictions.
        intervention_cases (array-like): Intervention model-predicted case counts.
        data_dates (array-like): Dates for observed data.
        data_cases (array-like): Observed case counts.
    """
    plt.figure(figsize=(8,6))
    plt.plot(baseline_dates, baseline_cases, label='Baseline')
    plt.plot(intervention_dates, intervention_cases, label='Vaccine')
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model after calibration')
    plt.legend()
    plt.tight_layout()
    plt.show()


def make_sim(sim_pars=None, disease_pars=None):
    """
    Create and configure a tetanus simulation using Starsim.

    Args:
        sim_pars (dict, optional): Simulation-level parameters (e.g., start/stop dates, time step). If provided, these override defaults.
        disease_pars (dict, optional): Parameters for the Tetanus disease model (e.g., beta, init_prev). If provided, these override defaults.

    Returns:
        starsim.Sim: A configured simulation object ready to run.

    The simulation includes:
        - A population of 10,000 agents
        - A random contact network
        - A ZeroDoseVaccination intervention
        - Tetanus disease dynamics
        - Births and deaths
    """
    sim_params = dict(
        start=sc.date('2019-01-01'),
        stop=sc.date('2025-01-31'),
        dt=1/12,  # monthly time step
    )
    if sim_pars:
        sim_params.update(sim_pars)

    # Create the product - a vaccine with 50% efficacy
    inv = ZeroDoseVaccination(dict(
        start_day=0,
        end_day=365*50,
        coverage=0.7,
        efficacy=0.95,
        year=[2020, 2021, 2022, 2023, 2024, 2025],
    ))

    pop = ss.People(n_agents=10000)
    tt = Tetanus(disease_pars or dict(
        beta=5.0,
        init_prev=0.3,
    ))

    sim = ss.Sim(
        people=pop,
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),
        interventions=[inv],
        diseases=tt,
        demographics=[ss.Births(dict(birth_rate=5)), ss.Deaths(dict(death_rate=5))],
        pars=sim_params,
    )
    sim.pars.verbose = sim.pars.dt / 365
    return sim

    
def run_calib():  
    """
    Run the calibration pipeline for the Tetanus model.

    This function:
        - Loads real-world monthly tetanus case data from CSV
        - Sets up calibration parameters (beta, init_prev)
        - Defines a build function to update the simulation with calibration parameters
        - Uses Starsim's Calibration framework to fit the model to data
        - Runs the best-fit simulation and outputs results to CSV
        - Plots model vs. data before and after calibration
        - Runs and outputs baseline and intervention scenarios

    Outputs:
        - model_tetanus_cases.csv: Model-predicted cases after calibration
        - baseline_tetanus_cases.csv: Cases with baseline scenario
        - intervention_tetanus_cases.csv: Cases with intervention scenario
        - model_vs_data_after_calibration.png: Plot comparing model and data

    Raises:
        Exception: If the input data file cannot be loaded
    """
        
    # --- Calibration block ---
    # Load real data
    data_df = pd.read_csv('tetanus_monthly_cases.csv')
    data_df['date'] = pd.to_datetime(data_df['date'])
    # Do NOT sort the data; preserve the order as in the CSV to match the year/month sequence
    data_df = data_df.set_index('date')  # This does not sort, just sets the index
    # Prepare calibration data: index must match model output (monthly)
    calib_data = data_df['cases'].values
    calib_dates = data_df.index
    calib_df = pd.DataFrame({'t': np.arange(len(calib_data)), 'n_infected': calib_data})
    calib_df = calib_df.set_index('t')

    # Define calibration parameters
    calib_pars = dict(
        beta=dict(low=0.1, high=10, guess=5.0),
        init_prev=dict(low=0.01, high=0.5, guess=0.3),
    )

    # Define the build function
    def build_fn(sim, calib_pars=None, **kwargs):
        if sim is None:
            raise ValueError('build_fn received sim=None. Cannot proceed.')
        tetanus = None
        if hasattr(sim, 'diseases'):
            if isinstance(sim.diseases, dict):
                tetanus = sim.diseases.get('tetanus', None)
            elif isinstance(sim.diseases, list):
                for d in sim.diseases:
                    if d.__class__.__name__.lower() == 'tetanus':
                        tetanus = d
                        break
        if tetanus is not None and calib_pars is not None:
            for k, v in calib_pars.items():
                if hasattr(tetanus.pars, k):
                    setattr(tetanus.pars, k, v['value'] if isinstance(v, dict) and 'value' in v else v)
        if sim is None:
            raise ValueError('build_fn is returning sim=None!')
        return sim

    # Set up the calibration component
    expected = calib_df.rename(columns={'n_infected': 'x'}).reset_index()[['t', 'x']]
    def safe_extract_fn(sim):
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

    # Create the base sim
    base_sim = make_sim()

    # Set up and run calibration
    calib = Calibration(
        sim=base_sim,
        calib_pars=calib_pars,
        build_fn=build_fn,
        components=[component],
        total_trials=30,  # You can increase for better fit
        n_workers=1,
        verbose=True
    )
    calib.calibrate()
    # calib.check_fit(do_plot=True)
    calib.check_fit()

    # --- Main simulation code follows ---
    # Use best-fit parameters from calibration
    best_pars = calib.best_pars
    # Convert beta from per-year to per-step (monthly) rate
    beta_per_year = best_pars['beta']
    beta_per_step = 1 - np.exp(-beta_per_year * (1/12))
    sim = make_sim(disease_pars=dict(beta=beta_per_step, init_prev=best_pars['init_prev']))
    sim.run()
    tet : ss.Disease = sim.diseases['tetanus']
    tet.plot()

    # --- Output model results to CSV ---
    model_cases = sim.results['tetanus']['n_infected']
    model_dates = pd.date_range(start='2019-01-01', periods=len(model_cases), freq='ME')
    model_df = pd.DataFrame({'date': model_dates, 'model_cases': model_cases})
    model_df.to_csv('model_tetanus_cases.csv', index=False)

    # --- Load real data from CSV ---
    # The file 'tetanus_monthly_cases.csv' should have columns: 'date', 'cases'
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
    plot_model_vs_data(model_dates, model_cases, data_dates, data_cases, filename='model_vs_data_after_calibration.png')

    # --- Baseline simulation ---
    baseline_dis = Tetanus(dict(beta=beta_per_step, init_prev=best_pars['init_prev']))
    baseline_sim = ss.Sim(
        n_agents=10000,
        diseases=baseline_dis,
        start='2019-01-01',
        stop='2025-01-31',
        dt=1/12,
        verbose=0.25
    )
    baseline_sim.run()
    baseline_cases = baseline_sim.results['tetanus']['n_infected']
    baseline_dates = pd.date_range(start='2019-01-01', periods=len(baseline_cases), freq='ME')

    # --- Intervention simulation (e.g., higher vaccine_prob) ---
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

    # --- Output both model results to CSV ---
    baseline_df = pd.DataFrame({'date': baseline_dates, 'baseline_cases': baseline_cases})
    intervention_df = pd.DataFrame({'date': intervention_dates, 'intervention_cases': intervention_cases})
    baseline_df.to_csv('baseline_tetanus_cases.csv', index=False)
    intervention_df.to_csv('intervention_tetanus_cases.csv', index=False)

    # --- Plot: Model before calibration ---
    plot_baseline_vs_data(baseline_dates, baseline_cases, data_dates, data_cases)

    # --- Plot: Model after calibration/intervention ---
    plot_baseline_vs_intervention(baseline_dates, baseline_cases, intervention_dates, intervention_cases, data_dates, data_cases)





if __name__ == '__main__':
    
    run_calib()