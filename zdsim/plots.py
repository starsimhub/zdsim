import starsim as ss 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(12, 8))
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

# - - - - - -  TETANUS-SPECIFIC PLOTTING FUNCTIONS - - - - - -

def plot_tetanus_focus(sim, title_prefix="TETANUS FOCUS"):
    """
    Create tetanus-focused plots with enhanced visualization.
    
    Parameters:
    -----------
    sim : starsim.Sim
        Simulation object with tetanus disease
    title_prefix : str
        Prefix for plot titles
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    
    # Get tetanus disease
    if 'tetanus' not in sim.diseases:
        raise ValueError("Simulation must contain tetanus disease")
    
    tetanus = sim.diseases['tetanus']
    results = tetanus.results
    
    # Set style for better visualization
    plt.style.use('seaborn-v0_8')
    sns.set_palette("viridis")
    
    # Create figure with enhanced layout (more compact)
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    fig.suptitle(f'{title_prefix}: Comprehensive Tetanus Analysis', fontsize=16, fontweight='bold')
    
    timevec = results.timevec
    
    # 1. Prevalence over time (enhanced)
    ax1 = axes[0, 0]
    prevalence = results.prevalence
    ax1.plot(timevec, prevalence, 'r-', linewidth=3, label='Tetanus Prevalence', alpha=0.8)
    ax1.fill_between(timevec, prevalence, alpha=0.3, color='red')
    ax1.set_title('Tetanus Prevalence Over Time\n(Environmental Exposure)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time (years)')
    ax1.set_ylabel('Prevalence')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    # Add note
    ax1.text(0.02, 0.98, 'Note: Tetanus is not directly transmissible\nbut occurs through wound contamination', 
             transform=ax1.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    # 2. Cumulative cases (enhanced)
    ax2 = axes[0, 1]
    cum_infections = results.cum_infections
    ax2.plot(timevec, cum_infections, 'b-', linewidth=3, label='Cumulative Cases', alpha=0.8)
    ax2.fill_between(timevec, cum_infections, alpha=0.3, color='blue')
    ax2.set_title('Cumulative Tetanus Cases\n(Total Infections)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Cumulative Cases')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    # Add note
    ax2.text(0.02, 0.98, 'Note: Shows total tetanus cases\naccumulated over time', 
             transform=ax2.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    
    # 3. New infections over time (enhanced)
    ax3 = axes[0, 2]
    new_infections = results.new_infections
    ax3.plot(timevec, new_infections, 'k-', linewidth=3, label='New Tetanus Cases', alpha=0.8)
    ax3.fill_between(timevec, new_infections, alpha=0.3, color='black')
    ax3.set_title('New Tetanus Cases Over Time\n(Incident Cases)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Time (years)')
    ax3.set_ylabel('New Cases')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    # Add note
    ax3.text(0.02, 0.98, 'Note: Shows new tetanus cases\noccurring each time period', 
             transform=ax3.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.7))
    
    # 4. Age distribution of cases (if available)
    ax4 = axes[1, 0]
    if hasattr(tetanus, 'infected') and len(tetanus.infected.uids) > 0:
        infected_ages = sim.people.age[tetanus.infected.uids]
        ax4.hist(infected_ages, bins=20, alpha=0.7, color='red', edgecolor='black', density=True)
        ax4.set_title('Age Distribution of Tetanus Cases\n(Risk by Age Group)', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Age (years)')
        ax4.set_ylabel('Density')
        ax4.grid(True, alpha=0.3)
        # Add note
        ax4.text(0.02, 0.98, 'Note: Tetanus risk varies by age\nAdults 15-45 years at higher risk', 
                 transform=ax4.transAxes, fontsize=8, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
    else:
        ax4.text(0.5, 0.5, 'No tetanus cases observed', ha='center', va='center', 
                transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Age Distribution of Tetanus Cases\n(Risk by Age Group)', fontsize=12, fontweight='bold')
    
    # 5. Vaccination status (if available)
    ax5 = axes[1, 1]
    if hasattr(tetanus, 'vaccinated'):
        vaccinated_count = np.sum(tetanus.vaccinated)
        total_pop = len(sim.people)
        unvaccinated_count = total_pop - vaccinated_count
        
        categories = ['Vaccinated', 'Unvaccinated']
        values = [vaccinated_count, unvaccinated_count]
        colors = ['green', 'lightcoral']
        
        wedges, texts, autotexts = ax5.pie(values, labels=categories, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        ax5.set_title('Vaccination Status\n(DTP-HepB-Hib Coverage)', fontsize=12, fontweight='bold')
        
        # Enhance pie chart
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        # Add note
        ax5.text(0.02, 0.98, 'Note: DTP-HepB-Hib vaccine\nprotects against tetanus', 
                 transform=ax5.transAxes, fontsize=8, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    else:
        ax5.text(0.5, 0.5, 'No vaccination data', ha='center', va='center', 
                transform=ax5.transAxes, fontsize=12)
        ax5.set_title('Vaccination Status\n(DTP-HepB-Hib Coverage)', fontsize=12, fontweight='bold')
    
    # 6. Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Calculate summary statistics
    total_cases = cum_infections[-1] if len(cum_infections) > 0 else 0
    total_new_cases = np.sum(results.new_infections) if len(results.new_infections) > 0 else 0
    peak_prevalence = np.max(prevalence) if len(prevalence) > 0 else 0
    final_prevalence = prevalence[-1] if len(prevalence) > 0 else 0
    
    summary_text = f"""
    TETANUS SUMMARY STATISTICS
    
    Total Cases: {total_cases:.0f}
    New Cases: {total_new_cases:.0f}
    Peak Prevalence: {peak_prevalence:.4f}
    Final Prevalence: {final_prevalence:.4f}
    
    Population: {len(sim.people):,}
    Simulation: {sim.pars.start}-{sim.pars.stop}
    
    Note: Tetanus is preventable
    through vaccination
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    return fig

def plot_tetanus_comparison(baseline_sim, vaccination_sim, title_prefix="TETANUS COMPARISON"):
    """
    Create comparison plots between baseline and vaccination scenarios for tetanus.
    
    Parameters:
    -----------
    baseline_sim : starsim.Sim
        Baseline simulation (no vaccination)
    vaccination_sim : starsim.Sim
        Vaccination simulation
    title_prefix : str
        Prefix for plot titles
        
    Returns:
    --------
    matplotlib.figure.Figure
        The created figure
    """
    
    # Get tetanus diseases
    baseline_tetanus = baseline_sim.diseases['tetanus']
    vaccination_tetanus = vaccination_sim.diseases['tetanus']
    
    baseline_results = baseline_tetanus.results
    vaccination_results = vaccination_tetanus.results
    
    # Set style
    plt.style.use('seaborn-v0_8')
    
    # Create figure (more compact)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f'{title_prefix}: Baseline vs Vaccination', fontsize=16, fontweight='bold')
    
    timevec = baseline_results.timevec
    
    # 1. Prevalence comparison
    ax1 = axes[0, 0]
    ax1.plot(timevec, baseline_results.prevalence, 'r-', linewidth=3, 
             label='Baseline (No Vaccination)', alpha=0.8)
    ax1.plot(timevec, vaccination_results.prevalence, 'b-', linewidth=3, 
             label='With Vaccination', alpha=0.8)
    ax1.fill_between(timevec, baseline_results.prevalence, alpha=0.2, color='red')
    ax1.fill_between(timevec, vaccination_results.prevalence, alpha=0.2, color='blue')
    ax1.set_title('Tetanus Prevalence Comparison\n(Vaccination Impact)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time (years)')
    ax1.set_ylabel('Prevalence')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    # Add note
    ax1.text(0.02, 0.98, 'Note: Vaccination reduces\ntetanus prevalence', 
             transform=ax1.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    # 2. Cumulative cases comparison
    ax2 = axes[0, 1]
    ax2.plot(timevec, baseline_results.cum_infections, 'r-', linewidth=3, 
             label='Baseline', alpha=0.8)
    ax2.plot(timevec, vaccination_results.cum_infections, 'b-', linewidth=3, 
             label='With Vaccination', alpha=0.8)
    ax2.set_title('Cumulative Tetanus Cases\n(Total Infections)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Cumulative Cases')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    # Add note
    ax2.text(0.02, 0.98, 'Note: Shows total cases\naccumulated over time', 
             transform=ax2.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))
    
    # 3. Impact summary
    ax3 = axes[1, 0]
    baseline_cases = baseline_results.cum_infections[-1]
    vaccination_cases = vaccination_results.cum_infections[-1]
    cases_averted = baseline_cases - vaccination_cases
    
    # Use new cases instead of deaths since deaths not available
    baseline_new = np.sum(baseline_results.new_infections)
    vaccination_new = np.sum(vaccination_results.new_infections)
    new_cases_averted = baseline_new - vaccination_new
    
    categories = ['Cases Averted', 'New Cases Averted']
    values = [cases_averted, new_cases_averted]
    colors = ['lightblue', 'lightcoral']
    
    bars = ax3.bar(categories, values, color=colors, alpha=0.8, edgecolor='black')
    ax3.set_title('Vaccination Impact\n(Cases Prevented)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Number Averted')
    
    # Add value labels
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    # Add note
    ax3.text(0.02, 0.98, 'Note: Shows cases prevented\nby vaccination', 
             transform=ax3.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    # 4. Reduction percentages
    ax4 = axes[1, 1]
    case_reduction = (cases_averted / baseline_cases * 100) if baseline_cases > 0 else 0
    new_case_reduction = (new_cases_averted / baseline_new * 100) if baseline_new > 0 else 0
    
    reduction_categories = ['Case Reduction', 'New Case Reduction']
    reduction_values = [case_reduction, new_case_reduction]
    colors = ['lightgreen', 'lightcoral']
    
    bars = ax4.bar(reduction_categories, reduction_values, color=colors, alpha=0.8, edgecolor='black')
    ax4.set_title('Reduction Percentages\n(Vaccination Effectiveness)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Reduction (%)')
    ax4.set_ylim(0, 100)
    
    # Add value labels
    for bar, value in zip(bars, reduction_values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
    # Add note
    ax4.text(0.02, 0.98, 'Note: Percentage reduction\nachieved by vaccination', 
             transform=ax4.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    plt.tight_layout()
    return fig