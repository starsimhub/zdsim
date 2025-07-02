import sciris as sc
import numpy as np
import starsim as ss
from zdsim import *
import pandas as pd
import matplotlib.pyplot as plt
from starsim.calibration import Calibration
from starsim.calib_components import Normal
import matplotlib.dates as mdates


def make_sim(sim_pars=None, disease_pars=None):
    """Create and configure a tetanus simulation."""
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
        coverage=0.5,
        efficacy=0.9,
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

if __name__ == '__main__':
    # --- Calibration block ---
    # Load real data
    data_df = pd.read_csv('tetanus_monthly_cases.csv')
    data_df['date'] = pd.to_datetime(data_df['date'])
    data_df = data_df.set_index('date')
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
        return sim

    # Set up the calibration component
    expected = calib_df.rename(columns={'n_infected': 'x'}).reset_index()[['t', 'x']]
    component = Normal(
        name='n_infected',
        expected=expected,
        extract_fn=lambda sim: pd.DataFrame({
            't': np.arange(len(sim.results['tetanus']['n_infected'])),
            'x': sim.results['tetanus']['n_infected'],
            'rand_seed': getattr(sim.pars, 'rand_seed', 0)
        }),
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
    sim = make_sim(disease_pars=dict(beta=best_pars['beta'], init_prev=best_pars['init_prev']))
    sim.run()
    tet : ss.Disease = sim.diseases['tetanus']
    tet.plot()

    # --- Output model results to CSV ---
    model_cases = sim.results['tetanus']['n_infected']
    model_dates = pd.date_range(start='2019-01-01', periods=len(model_cases), freq='M')
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
    plt.savefig('model_vs_data_after_calibration.png')
    plt.show()

    # --- Baseline simulation ---
    baseline_dis = Tetanus(dict(beta=5.0, init_prev=0.3))
    baseline_sim = ss.Sim(
        n_agents=10000,
        diseases=baseline_dis,
        start='2019-01-01',
        stop='2025-01-31',
        verbose=0.25
    )
    baseline_sim.run()
    baseline_cases = baseline_sim.results['tetanus']['n_infected']
    baseline_scaling = 3338 / baseline_cases[0] if baseline_cases[0] > 0 else 1
    baseline_cases_scaled = baseline_cases * baseline_scaling
    baseline_dates = pd.date_range(start='2019-01-01', periods=len(baseline_cases), freq='ME')

    # --- Intervention simulation (e.g., higher vaccine_prob) ---
    intervention_dis = Tetanus(pars=dict(beta=5.0, init_prev=0.3, vaccine_prob=0.5))  # Example: double the vaccination probability
    intervention_sim = ss.Sim(
        n_agents=10000,
        diseases=intervention_dis,
        start='2019-01-01',
        stop='2025-01-31',
        verbose=0.25
    )
    intervention_sim.run()
    intervention_cases = intervention_sim.results['tetanus']['n_infected']
    intervention_scaling = 3338 / intervention_cases[0] if intervention_cases[0] > 0 else 1
    intervention_cases_scaled = intervention_cases * intervention_scaling

    # --- Output both model results to CSV ---
    baseline_df = pd.DataFrame({'date': baseline_dates, 'baseline_cases': baseline_cases_scaled})
    intervention_df = pd.DataFrame({'date': baseline_dates, 'intervention_cases': intervention_cases_scaled})
    baseline_df.to_csv('baseline_tetanus_cases.csv', index=False)
    intervention_df.to_csv('intervention_tetanus_cases.csv', index=False)

    # --- Plot: Model before calibration ---
    plt.figure(figsize=(8,6))
    plt.plot(baseline_dates, baseline_cases_scaled, label='Model')
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model before calibration')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # --- Plot: Model after calibration/intervention ---
    plt.figure(figsize=(8,6))
    plt.plot(baseline_dates, baseline_cases_scaled, label='Baseline')
    plt.plot(baseline_dates, intervention_cases_scaled, label='Vaccine')
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model after calibration')
    plt.legend()
    plt.tight_layout()
    plt.show()




