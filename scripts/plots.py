"""
plots.py
========

This module contains all plotting functions used in the tetanus ABM pipeline. Each function is designed to help visualize model results and compare them to real data. The functions are written to be explicit and practical, with detailed docstrings and comments to guide users.

Functions:
- plot_model_vs_data: Plot model-predicted cases vs. real data after calibration.
- plot_baseline_vs_data: Plot baseline model-predicted cases vs. real data before calibration.
- plot_baseline_vs_intervention: Plot baseline and intervention model-predicted cases vs. real data after calibration/intervention.

All functions require matplotlib and pandas.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ================================================
#    MODEL .VS. DATA
# ================================================
def plot_model_vs_data(model_dates, model_cases, data_dates, data_cases, filename=None, title=''):
    """
    Plot model-predicted cases vs. real data after calibration.

    This function creates a line plot to visually compare the model's predictions to your real data, after the model has been calibrated (fitted) to your data.

    Why this is important:
    - This plot lets you see, at a glance, how well the model matches reality after calibration.
    - The model's predictions are shown as a line, and your real data as points. If the lines are close, the model is a good fit.
    - If you provide a filename, the plot is saved as an image file (e.g., for use in presentations or reports).

    What to check:
    - The dates on the x-axis should match your data and the simulation period.
    - The y-axis shows the number of tetanus cases per month.
    - If the model and data lines are far apart, calibration may need to be improved or the data checked.

    Parameters
    ----------
    model_dates : array-like
        Dates for the model's predictions (should match the simulation period).
    model_cases : array-like
        Number of cases predicted by the model for each date.
    data_dates : array-like
        Dates from your real data.
    data_cases : array-like
        Real number of cases for each date.
    filename : str, optional
        If provided, the plot will be saved to this file (e.g., 'output.png').
    
    Notes
    -----
    - The model's predictions are shown as a line, and your real data as points. If the lines are close, the model is a good fit.
    - If you provide a filename, the plot is saved as an image file (e.g., for use in presentations or reports).
    - The dates on the x-axis should match your data and the simulation period.
    - The y-axis shows the number of tetanus cases per month.
    - If the model and data lines are far apart, calibration may need to be improved or the data checked.    
        
    """
    # Create a new figure for the plot
    plt.figure(figsize=(12, 6))
    # Plot the model's predicted cases as a line
    plt.plot(model_dates, model_cases, label='Model')
    # If real data is available, plot it as black circles with lines
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    # Label the axes for clarity
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    # Add a title to explain what the plot shows
    plt.title('Model after calibration ' + title) 
    # Add a legend so users know which line is which
    plt.legend()
    plt.tight_layout()
    # Format the x-axis to show years clearly
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()
    # If a filename is provided, save the plot as an image file
    if filename:
        plt.savefig(filename)
        print(f"Plot saved to {filename}")
    # Show the plot on screen
    plt.show()


# ================================================
#    BASELINE .VS. DATA
# ================================================
def plot_baseline_vs_data(baseline_dates, baseline_cases, data_dates, data_cases, filename=None, title=''):
    """
    Plot baseline model-predicted cases vs. real data before calibration.

    This function shows how the model performs before it is fitted to your data. This is a useful reference to see how much calibration improves the model.

    Why this is important:
    - The baseline model uses default parameters, not tuned to your data. This is a "starting point" for the model.
    - Comparing this plot to the calibrated plot shows how much the model improves after fitting.

    What to check:
    - If the baseline model is very different from your data, that's normal. Calibration is meant to fix this.
    - If the baseline model is already a good fit, calibration may not change much.


    Parameters
    ----------
    baseline_dates : array-like
        Dates for the model's baseline predictions.
    baseline_cases : array-like
        Number of cases predicted by the model before calibration.
    data_dates : array-like
        Dates from your real data.
    data_cases : array-like
        Real number of cases for each date.

    Returns
    -------
    None
        The function displays the plot.

    Notes
    -----
    - The baseline model uses default parameters, not tuned to your data. This is a "starting point" for the model.
    - Comparing this plot to the calibrated plot shows how much the model improves after fitting.
    - If the baseline model is very different from your data, that's normal. Calibration is meant to fix this.
    - If the baseline model is already a good fit, calibration may not change much.
    """
    plt.figure(figsize=(8,6))
    # Plot the baseline model's predictions
    plt.plot(baseline_dates, baseline_cases, label='Model')
    # Plot the real data if available
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model before calibration '+title)
    plt.legend()
    plt.tight_layout()
    # Format the x-axis to show years clearly
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()
    # If a filename is provided, save the plot as an image file
    if filename:
        plt.savefig(filename)
        print(f"Plot saved to {filename}")
    # Show the plot on screen
    plt.show()

# ================================================
#    BASELINE .VS. INTERVENTION
# ================================================
def plot_baseline_vs_intervention(baseline_dates, baseline_cases, intervention_dates, intervention_cases, data_dates, data_cases, filename=None, title=''):
    """
    Plot baseline and intervention model-predicted cases vs. real data after calibration/intervention.

    This function compares what happens in the model with and without an intervention (such as increased vaccination), after the model has been calibrated to your data.

    Why this is important:
    - This plot helps you see the potential impact of interventions in your setting.
    - The plot shows three lines: baseline (no intervention), intervention (e.g., more vaccination), and your real data.
    - You can use this to communicate the value of interventions to stakeholders.

    What to check:
    - The intervention line should show fewer cases if the intervention is effective.
    - If the intervention has little effect, check the intervention parameters or consult with a modeling expert.

    Parameters
    ----------
    baseline_dates : array-like
        Dates for the baseline scenario.
    baseline_cases : array-like
        Model-predicted cases with no intervention.
    intervention_dates : array-like
        Dates for the intervention scenario.
    intervention_cases : array-like
        Model-predicted cases with intervention.
    data_dates : array-like
        Dates from your real data.
    data_cases : array-like
        Real number of cases for each date.

    Returns
    -------
    None
        The function displays the plot.

    Notes
    -----
    - This plot helps you see the potential impact of interventions in your setting.
    - The plot shows three lines: baseline (no intervention), intervention (e.g., more vaccination), and your real data.
    - You can use this to communicate the value of interventions to stakeholders.
    - The intervention line should show fewer cases if the intervention is effective.
    - If the intervention has little effect, check the intervention parameters or consult with a modeling expert.
    """
    plt.figure(figsize=(8,6))
    # Plot baseline scenario
    plt.plot(baseline_dates, baseline_cases, label='Baseline')
    # Plot intervention scenario
    plt.plot(intervention_dates, intervention_cases, label='Vaccine')
    # Plot real data if available
    if len(data_dates) > 0:
        plt.plot(data_dates, data_cases, 'ko-', label='Data')
    plt.xlabel('Date')
    plt.ylabel('Monthly Tetanus Cases')
    plt.title('Model after calibration '+title)
    plt.legend()
    plt.tight_layout()
    # Format the x-axis to show years clearly
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.gcf().autofmt_xdate()
    # If a filename is provided, save the plot as an image file
    if filename:
        plt.savefig(filename)
        print(f"Plot saved to {filename}")
    # Show the plot on screen
    plt.show() 