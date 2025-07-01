import starsim as ss 
import numpy as np
import matplotlib.pyplot as plt

# - - - - - -  PLOT RESULTS SUITE - - - - - -
def plot_results(flat_results, keywords=None, exclude=['15']):
    """
    Plots the results of multiple scenarios based on specified metrics.
    Parameters:
    -----------
    flat_results : dict
        A dictionary where keys are scenario names and values are dictionaries
        containing metric data. Each metric data dictionary should have keys
        representing metric names and values containing objects with `timevec`
        (time points) and `values` (corresponding metric values).
    keywords : list of str, optional
        A list of keywords to filter the metrics to be plotted. Only metrics
        containing any of these keywords in their names will be included. If
        None, all metrics will be considered.
    exclude : list of str, optional
        A list of substrings to exclude from the metric names. Metrics
        containing any of these substrings will be ignored. Default is ['15'].
    Returns:
    --------
    None
        The function generates a plot for the selected metrics and displays it.
    Notes:
    ------
    - If there are more than 5 metrics, the plots are arranged in a grid with
      5 columns.
    - The y-axis is adjusted based on the maximum value of the metric:
        - If the maximum value is less than 1, the y-axis is scaled between 0
          and the greater of 0.5 or the maximum value.
        - Otherwise, the y-axis is labeled as 'Value'.
    - A legend is added to each plot, with transparency applied to its frame.
    - The function uses the 'tab10' colormap to differentiate scenarios.
    Example:
    --------
    >>> flat_results = {
    ...     "Scenario 1": {"metric1": result1, "metric2": result2},
    ...     "Scenario 2": {"metric1": result3, "metric2": result4},
    ... }
    >>> plot_results(flat_results, keywords=["metric"], exclude=["15"])
    """
    # Automatically identify all unique metrics across all scenarios
    metrics = []
    if keywords is None:
        metrics = sorted({key for flat in flat_results.values() for key in flat.keys()}, reverse=True)
        
    else:
        metrics = sorted({
            k for flat in flat_results.values() for k in flat
            if any(kw in k for kw in keywords) 
        })
        # Exclude specified metrics
    
    metrics = [m for m in metrics if not any(excl in m for excl in exclude)]
        
    n_metrics = len(metrics)
    if n_metrics > 0:
        # If there are more than 5 metrics, use a grid of 5 columns
        n_cols = 5
        n_rows = int(np.ceil(n_metrics / n_cols))
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(20, n_rows*2))
        axs = axs.flatten()
        
    cmap = plt.cm.get_cmap('tab10', len(flat_results))

    for i, metric in enumerate(metrics):
        ax = axs[i] if n_metrics > 1 else axs
        for j, (scenario, flat) in enumerate(flat_results.items()):
            if metric in flat:
                result = flat[metric]
                ax.plot(result.timevec, result.values, label=scenario, color=cmap(j))
        ax.set_title(metric)
        if max(result.values) < 1:
            # identify the max value of result.values
            v = max(result.values)
            ax.set_ylim(0, max(0.5, v)) 
            ax.set_ylabel('%')
        else:
            ax.set_ylabel('Value')
        ax.set_xlabel('Time')
        
        ax.grid(True)
        ax.legend()
        
        leg = ax.legend(loc='upper right', fontsize=(6 if len(flat_results) <= 5 else 5))
        
        if leg:
            leg.get_frame().set_alpha(0.5)
        # Make the x-axis labels smaller
        plt.setp(ax.get_xticklabels(), fontsize=8)
        
    # Hide any unused subplots
    for j in range(i + 1, len(axs)):
        axs[j].axis('off')
    plt.tight_layout()
    plt.show()


    """
    Sample usage:
    
    SINGLE SCENARIO EXAMPLE:
    
    >>> import matplotlib.pyplot as plt 
    >>> sim = make_sim()
    >>> sim.run()
    >>> results = {}
    >>> results[0] = sim.results.flatten()
    >>> zds.plots.plot_results(results)
    >>> plt.show()
    
    """