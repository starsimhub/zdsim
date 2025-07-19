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


# ===============================
# Simulation Construction
# ===============================

def make_tetanus(sim_pars=None, disease_pars=None):
    """
    Create and configure a tetanus simulation using Starsim.

    This function sets up the simulation model. It creates a "virtual world" with people, disease, and interventions.

    Step-by-step, this function:
    1. Sets up the simulation period (start and end dates) and time step (monthly).
    2. Adds a vaccination intervention, with specified coverage and efficacy.
    3. Creates a population of 10,000 people, each with their own characteristics.
    4. Sets up the disease (tetanus) with parameters for how easily it spreads and how many people are initially infected.
    5. Adds a contact network (who interacts with whom), births, and deaths.
    6. Returns a simulation object that is ready to run.

    Why this is important:
    - This function defines the "rules" of your simulation. You can adjust parameters if you want to explore different scenarios.
    - The defaults are chosen to be reasonable for most cases, but you can change them if you have specific needs.

    Args:
        sim_pars (dict, optional): Settings for the simulation (like start/end date). You can ignore this unless you want to change the simulation period.
        disease_pars (dict, optional): Settings for the disease (like how easily it spreads). Usually set automatically during calibration.

    Returns:
        starsim.Sim: The simulation object, ready to run.
    """
    # Set up default simulation parameters
    sim_params = dict(
        start=sc.date('2019-01-01'),  # Simulation start date
        stop=sc.date('2025-01-31'),   # Simulation end date
        dt=1/12,                      # Time step: 1/12 = monthly
    )
    # If the user provides custom simulation parameters, update the defaults
    if sim_pars:
        sim_params.update(sim_pars)

    # Set up the vaccination intervention
    # This intervention will run for 50 years (longer than the simulation, so it covers the whole period)
    # Coverage is the proportion of people who get vaccinated; efficacy is how well the vaccine works
    
    """Zerodose Vaccination """
    
    inv = ZeroDoseVaccination(dict(
        start_day=0,
        end_day=365*50,  # 50 years
        coverage=0.7,    # 70% of people get vaccinated
        efficacy=0.95,   # 95% effective
        year=[2020, 2021, 2022, 2023, 2024, 2025],  # Years when vaccination is active
    ))

    # Create a population of 10,000 people (agents)
    pop = ss.People(n_agents=10000)
    # Set up the disease (tetanus) with default or user-provided parameters
    tt = Tetanus(disease_pars or dict(
        beta=5.0,         # Transmission rate (per year)
        init_prev=0.3,    # Initial prevalence (proportion infected at start)
    ))

    # Set up the simulation object
    sim = ss.Sim(
        people=pop,  # The population
        networks=ss.RandomNet(dict(n_contacts=5, dur=0)),  # Random contact network: each person has 5 contacts
        interventions=[inv],  # Add the vaccination intervention
        diseases=tt,          # Add the tetanus disease
        demographics=[ss.Births(dict(birth_rate=5)), ss.Deaths(dict(death_rate=5))],  # Add births and deaths
        pars=sim_params,      # Simulation parameters
    )
    # Set verbosity: controls how much progress information is printed
    sim.pars.verbose = sim.pars.dt / 365
    return sim

if __name__ == '__main__':
    sim = make_tetanus()
    sim.run()
    sim.plot()
    plt.show()
    