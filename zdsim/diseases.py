import numpy as np
import starsim as ss
import matplotlib.pyplot as plt
import pandas as pd
from enum import IntEnum

__all__ = ['Tetanus', 'TST']

class TST(IntEnum):
    NONE          = -1  # No state
    SUSCEPTIBLE   = 0  # Agent is alive
    INFECTED      = 1  # Agent is infected with tetanus
    RECOVERED     = 2

class VxST(IntEnum):
    NONE = 0
    ONE_DOSE_IMMUNIZED = 1
    TWO_DOSE_IMMUNIZED = 2
    FULLY_IMMUNIZED = 3

class Tetanus(ss.Infection):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        
        # 1. Define parameters
        # 2. Update parameters
        # 3. Define states:
        #    a. state
        #    b. time recorders
        """
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        # DISEASE PARAMETERS: All this data will be stored in the Tetanus.pars dictionary
        # -------------------------------------------------------------------------------------      
        """
        self.define_pars(
            init_prev = ss.bernoulli(0.01),  # Initial infection probability
            beta = ss.beta(1.3),             # Transmission rate per contact
            gamma = ss.peryear(3),           # Recovery rate (3-month infectious period)
            waning = ss.peryear(0.055),      # Immunity waning rate (loss of protection)
            # vaccine_prob = 0.25,             # Probability of receiving a vaccine
            # vaccine_efficacy = 0.9,          # Vaccine effectiveness in preventing infection
            immunity_boost = 1.0,            # Boost in immunity after infection
        )
        self.update_pars(pars, **kwargs)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        """
        #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        # AGENT HEALTH STATUS AND DISEASE-LINKED DATA
        # --------------------------------------------
        
            Each agent has the following disease-related parameters, forming a virtual table like this:

            | Agent ID | Infection Status | Disease Stage  | Time Since Infection  | Vaccine Status | Treatment Status | Mortality Risk |
            |----------|------------------|----------------|-----------------------|----------------|------------------|----------------|
            | 1        | Infected         | Latent         | 10 days               | Vaccinated     | Not on treatment | Low            |
            | 2        | Susceptible      | N/A            | N/A                   | Not vaccinated | N/A              | Moderate       |
            | 3        | Infected         | Active         | 45 days               | Vaccinated     | On treatment     | High           |
            | ...      | ...              | ...            | ...                   | ...            | ...              | ...            |

            > ⚠️ Note: This data is stored internally for each agent. While conceptually it forms a table, under the hood it is not managed 
            as a single table, but rather as a collection of vectors. The data is stored in specialized data structures that combine 
            disease -and- agent specific information. For this reason, it must be defined using Starsim array types (e.g., `ss.FloatArr`, `ss.BoolArr`, etc.)
            as shown below and as numbers (e.g., 0, 1, 2, etc.) instead of strings (e.g., "Infected", "Susceptible", etc.) to ensure efficient storage and processing.
            e.g. If you want to store a Yes or No value, use ss.BoolArr, in this way: ss.BoolArr('vaccinated', default=False) will be initialized and stored
            as a "column" for the agent defauted to Zeroes
        """

        self.define_states(
            ss.FloatArr('state', default=TST.SUSCEPTIBLE),  #<--- This will be an array under Tetanus.state with Float values -- so tetanus.rel_sus[12] will return the state of agent 12 
            ss.FloatArr('vx_state', default=VxST.NONE),     #<--- Optional: Keeps track of the vaccination status  
            ss.FloatArr('time_infected'),                   #<--- This will be an array under Tetanus.ti_infected  
            ss.FloatArr('time_last_vx'),                    #<--- Optional: Could be used to store the time of the last vaccination.
            ss.FloatArr('rel_sus', default=1.0),            #<--- This will be an array under Tetanus.rel_sus
            ss.FloatArr('minerva_column', default=0),       #<--- This will be an array under Tetanus.minerva_column
        )    
        # INDEX: each row is an agent, the row index is the agent ID  (ss.UID or ss.AUID)
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    """ Determines if an agent is infectious and can transmit tetanus. """
    @property
    def zero_dose_prospect(self):   
        # this is a filter that returns the uids of the agents that are infected
        return (self.state == TST.SUSCEPTIBLE) | (self.vx_state == VxST.ONE_DOSE_IMMUNIZED) | (self.vx_state == VxST.TWO_DOSE_IMMUNIZED)

    @property
    def protected(self):
        # this is a filter that returns the uids of the agents that are immunized
        return self.state == VxST.FULLY_IMMUNIZED

    def set_prognoses(self, uids, from_uids=None):
        """ Handles new infections and vaccination effects. """
        super().set_prognoses(uids, from_uids)
        # Convert numpy indices to ss.uids if needed
        if not hasattr(uids, 'uids') and not isinstance(uids, ss.uids().__class__):
            uids = ss.uids(uids)
        self.state[uids] = TST.INFECTED
        self.time_infected[uids] = self.ti
        return

    def step(self):
        """ Simulate the disease dynamics for one time step. """
        p = self.pars
        ti = self.ti
        # Susceptible to infected
        sus = (self.state == TST.SUSCEPTIBLE)
        n_sus = np.sum(sus)
        if n_sus > 0:
            # Example: random infection based on beta
            new_inf = np.random.rand(n_sus) < p.beta
            new_inf_uids = np.where(sus)[0][new_inf]
            if len(new_inf_uids) > 0:
                # Convert to ss.uids for Arr indexing
                new_inf_uids = ss.uids(new_inf_uids)
                self.set_prognoses(new_inf_uids)
        # Infected to recovered
        inf = (self.state == TST.INFECTED)
        n_inf = np.sum(inf)
        if n_inf > 0:
            recover = np.random.rand(n_inf) < p.gamma
            rec_uids = np.where(inf)[0][recover]
            if len(rec_uids) > 0:
                # Convert to ss.uids for Arr indexing
                rec_uids = ss.uids(rec_uids)
                self.state[rec_uids] = TST.RECOVERED
        return

    def init_results(self):
        """ Initialize results """
        super().init_results()
        self.define_results(
            ss.Result('rel_sus', dtype=float, label='Relative susceptibility'),
            ss.Result('ever_infected', dtype=bool, label='Ever infected'),
            ss.Result('vaccinated', dtype=bool, label='Vaccinated'),
        )
        return

    def update_results(self):
        """ Store the population immunity (susceptibility) """
        super().update_results()
        self.results['rel_sus'][self.ti] = self.rel_sus.mean()
        return
    
    
    def finalize_result(self):
        super().finalize_results()
        res = self.results
        res['cum_deaths']     = np.cumsum(res['new_deaths'])

        return
    
    def plot(self):
        fig = plt.figure()
        for rkey in self.results.keys(): 
            if rkey == 'timevec':
                continue
            plt.plot(self.results['timevec'], self.results[rkey], label=rkey.title())
        plt.legend()
        plt.show()
        return fig
