"""
Base classes and utilities for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np
import sciris as sc

class ZeroDoseSim(ss.Sim):
    """
    Base simulation class for zero-dose vaccination studies.
    """
    
    def __init__(self, pars=None, **kwargs):
        super().__init__(pars, **kwargs)
        return
    
    def make_people(self, n_agents=10000, age_dist=None):
        """Create a population with appropriate age distribution"""
        if age_dist is None:
            # Default age distribution weighted towards children
            age_dist = ss.uniform(low=0, high=80)
        
        people = ss.People(n_agents=n_agents, age_dist=age_dist)
        return people
    
    def make_networks(self):
        """Create contact networks for disease transmission"""
        # Household contacts
        household_net = ss.RandomNet(dict(n_contacts=3, dur=0))
        
        # Community contacts
        community_net = ss.RandomNet(dict(n_contacts=10, dur=0))
        
        return [household_net, community_net]
    
    def make_demographics(self):
        """Create demographic modules"""
        births = ss.Births(dict(birth_rate=25))  # 25 births per 1000 population per year
        deaths = ss.Deaths(dict(death_rate=8))    # 8 deaths per 1000 population per year
        
        return [births, deaths]
