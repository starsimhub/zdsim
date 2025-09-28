"""
Simple tetanus-focused analysis script.

This script provides enhanced visualization and analysis specifically for tetanus,
which is the main focus of the zero-dose vaccination paper.
"""

import sciris as sc
import numpy as np
import starsim as ss
import zdsim as zds
import matplotlib.pyplot as plt
import seaborn as sns

def create_tetanus_simulation(n_agents=10000, start=2020, stop=2030):
    """Create a simulation focused on tetanus analysis."""
    
    # Simulation parameters
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1/52,  # Weekly timesteps
        verbose=1/52
    )
    
    # Create population
    people = ss.People(n_agents=n_agents)
    
    # Create tetanus disease with enhanced parameters
    tetanus = zds.Tetanus(dict(
        beta=ss.peryear(0.02),  # Environmental exposure rate
        init_prev=ss.bernoulli(p=0.001),  # Initial prevalence
        dur_inf=ss.lognorm_ex(mean=ss.years(0.1)),  # Duration
        p_death=ss.bernoulli(p=0.1),  # Case fatality rate
        p_severe=ss.bernoulli(p=0.3),  # Severe disease probability
        wound_rate=ss.peryear(0.1),  # Annual wound exposure rate
    ))
    
    # Create networks
    networks = [
        ss.RandomNet(dict(n_contacts=5, dur=0), name='household'),
        ss.RandomNet(dict(n_contacts=15, dur=0), name='community')
    ]
    
    # Create demographics
    demographics = [
        ss.Births(dict(birth_rate=25)),
        ss.Deaths(dict(death_rate=8))
    ]
    
    # Create simulation
    sim = ss.Sim(
        people=people,
        diseases=tetanus,
        networks=networks,
        demographics=demographics,
        pars=sim_pars
    )
    
    return sim

def plot_tetanus_enhanced(sim, title_suffix=""):
    """Create enhanced tetanus-focused plots."""
    
    # Get tetanus disease
    tetanus = sim.diseases['tetanus']
    results = tetanus.results
    
    # Set style for better visualization
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create comprehensive figure (more compact)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f'TETANUS FOCUSED ANALYSIS{title_suffix}', fontsize=16, fontweight='bold')
    
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
    ax1.text(0.02, 0.98, 'Note: Tetanus is not directly\ntransmissible between people', 
             transform=ax1.transAxes, fontsize=8, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    # 2. Cumulative cases (enhanced)
    ax2 = axes[0, 1]
    cum_infections = results.cum_infections
    ax2.plot(timevec, cum_infections, 'b-', linewidth=3, label='Cumulative Cases', alpha=0.8)
    ax2.fill_between(timevec, cum_infections, alpha=0.3, color='blue')
    ax2.set_title('Cumulative Tetanus Cases', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Time (years)')
    ax2.set_ylabel('Cumulative Cases')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. New infections over time (enhanced)
    ax3 = axes[0, 2]
    new_infections = results.new_infections
    ax3.plot(timevec, new_infections, 'k-', linewidth=3, label='New Tetanus Cases', alpha=0.8)
    ax3.fill_between(timevec, new_infections, alpha=0.3, color='black')
    ax3.set_title('New Tetanus Cases Over Time', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Time (years)')
    ax3.set_ylabel('New Cases')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. Age distribution of cases (if available)
    ax4 = axes[1, 0]
    if hasattr(tetanus, 'infected') and len(tetanus.infected.uids) > 0:
        infected_ages = sim.people.age[tetanus.infected.uids]
        ax4.hist(infected_ages, bins=20, alpha=0.7, color='red', edgecolor='black', density=True)
        ax4.set_title('Age Distribution of Tetanus Cases', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Age (years)')
        ax4.set_ylabel('Density')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'No tetanus cases observed', ha='center', va='center', 
                transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Age Distribution of Tetanus Cases', fontsize=14, fontweight='bold')
    
    # 5. Wound exposure events (if available)
    ax5 = axes[1, 1]
    if hasattr(tetanus, 'ti_wound'):
        wound_times = tetanus.ti_wound[tetanus.ti_wound > 0]
        if len(wound_times) > 0:
            ax5.hist(wound_times, bins=20, alpha=0.7, color='orange', edgecolor='black')
            ax5.set_title('Wound Exposure Events', fontsize=14, fontweight='bold')
            ax5.set_xlabel('Time (years)')
            ax5.set_ylabel('Number of Wound Events')
            ax5.grid(True, alpha=0.3)
        else:
            ax5.text(0.5, 0.5, 'No wound exposures', ha='center', va='center', 
                    transform=ax5.transAxes, fontsize=12)
            ax5.set_title('Wound Exposure Events', fontsize=14, fontweight='bold')
    else:
        ax5.text(0.5, 0.5, 'No wound data', ha='center', va='center', 
                transform=ax5.transAxes, fontsize=12)
        ax5.set_title('Wound Exposure Events', fontsize=14, fontweight='bold')
    
    # 6. Summary statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Calculate summary statistics
    total_cases = cum_infections[-1] if len(cum_infections) > 0 else 0
    total_new_cases = np.sum(results.new_infections) if len(results.new_infections) > 0 else 0
    peak_prevalence = np.max(prevalence) if len(prevalence) > 0 else 0
    final_prevalence = prevalence[-1] if len(prevalence) > 0 else 0
    
    summary_text = f"""
    TETANUS SUMMARY STATISTICS{title_suffix}
    
    Total Cases: {total_cases:.0f}
    New Cases: {total_new_cases:.0f}
    Peak Prevalence: {peak_prevalence:.4f}
    Final Prevalence: {final_prevalence:.4f}
    
    Population: {len(sim.people):,}
    Simulation: {sim.pars.start}-{sim.pars.stop}
    """
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    return fig

def run_tetanus_analysis():
    """Run tetanus-focused analysis."""
    
    print("="*80)
    print("TETANUS-FOCUSED ANALYSIS")
    print("="*80)
    
    # Create tetanus simulation
    print("\n1. Creating tetanus simulation...")
    sim = create_tetanus_simulation(n_agents=15000, start=2020, stop=2030)
    
    print("2. Running simulation...")
    sim.run()
    
    print("3. Creating enhanced tetanus plots...")
    fig = plot_tetanus_enhanced(sim, " - TETANUS FOCUS")
    plt.show()
    
    # Get tetanus results
    tetanus = sim.diseases['tetanus']
    results = tetanus.results
    
    # Print detailed results
    print(f"\nTETANUS ANALYSIS RESULTS:")
    print(f"Total Cases: {results.cum_infections[-1]:.0f}")
    print(f"New Cases: {np.sum(results.new_infections):.0f}")
    print(f"Peak Prevalence: {np.max(results.prevalence):.4f}")
    print(f"Final Prevalence: {results.prevalence[-1]:.4f}")
    
    print(f"\nTetanus-focused analysis completed!")
    print(f"This analysis provides enhanced visualization specifically for tetanus,")
    print(f"which is the main focus of the zero-dose vaccination paper.")
    
    return sim

if __name__ == '__main__':
    # Run the tetanus-focused analysis
    sim = run_tetanus_analysis()
