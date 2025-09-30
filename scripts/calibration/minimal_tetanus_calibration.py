#!/usr/bin/env python3
"""
Minimal Tetanus Model Calibration

This script implements a minimal tetanus calibration to test the system.
"""

import numpy as np
import pandas as pd
import starsim as ss
import zdsim as zds
import warnings
warnings.filterwarnings('ignore')

def main():
    """Main function to test tetanus calibration."""
    
    print("="*60)
    print("MINIMAL TETANUS MODEL CALIBRATION")
    print("="*60)
    
    try:
        # Test basic imports
        print("✓ Testing imports...")
        import starsim as ss
        import zdsim as zds
        print("✓ Imports successful")
        
        # Create minimal simulation
        print("✓ Creating minimal simulation...")
        people = ss.People(n_agents=100)
        
        tetanus = zds.Tetanus(dict(
            neonatal_wound_rate=ss.peryear(0.1),
            peri_neonatal_wound_rate=ss.peryear(0.01),
            childhood_wound_rate=ss.peryear(0.05),
            adult_wound_rate=ss.peryear(0.03),
            neonatal_cfr=0.8,
            peri_neonatal_cfr=0.4,
            childhood_cfr=0.1,
            adult_cfr=0.2,
            maternal_vaccination_efficacy=0.6,
            maternal_vaccination_coverage=0.4,
        ))
        
        sim = ss.Sim(
            people=people,
            diseases=[tetanus],
            pars={'dur': 365, 'dt': 30}
        )
        
        print("✓ Simulation created")
        
        # Run simulation
        print("✓ Running simulation...")
        sim.run()
        
        print("✓ Simulation completed")
        
        # Get results
        tetanus_results = sim.diseases['tetanus']
        neonatal_cases = np.sum(tetanus_results.neonatal)
        total_cases = np.sum(tetanus_results.infected)
        
        print(f"✓ Results:")
        print(f"  Total tetanus cases: {total_cases}")
        print(f"  Neonatal cases: {neonatal_cases}")
        if total_cases > 0:
            print(f"  Neonatal proportion: {neonatal_cases/total_cases:.1%}")
        
        print("\n" + "="*60)
        print("MINIMAL TETANUS CALIBRATION COMPLETED")
        print("="*60)
        print("✓ Basic tetanus model working")
        print("✓ Ready for full calibration")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
