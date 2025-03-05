import numpy as np
import starsim as ss
import matplotlib.pyplot as plt
import pandas as pd
from enum import IntEnum

__all__ = ['Tetanus', 'TetanusStates']

class TetanusStates(IntEnum):
    NONE   = 0  # Agent is alive
    IMMUNIZED     = 2  # Received vaccination
    SUSCEPTIBLE   = 2  # Agent is susceptible to tetanus
    INFECTED      = 3  # Agent is infected with tetanus

class VaccineTypes(IntEnum):
    NONE = 0  # No vaccine received
    DPT1 = 1  # first (1st) dose of diphtheria-tetanus-pertussis containing vaccine (DTP1)
    DPT2 = 2  # Second dose of vaccine
    DPT3 = 3  # Third dose of vaccine
    PENTA_DOSE = 4 # DPT1 + HepB + HiB

class Tetanus(ss.Infection):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        """
        # 1. Define parameters
        # 2. Update parameters
        # 3. Define states:
            a. state
            b. time recorders
        """

        self.define_pars(
            init_prev = ss.bernoulli(0.01),  # Initial infection probability
            beta = ss.beta(1.3),             # Transmission rate per contact
            gamma = ss.peryear(3),           # Recovery rate (3-month infectious period)
            waning = ss.peryear(0.055),      # Immunity waning rate (loss of protection)
            vaccine_prob = 0.25,             # Probability of receiving a vaccine
            vaccine_efficacy = 0.9,          # Vaccine effectiveness in preventing infection
            immunity_boost = 1.0,            # Boost in immunity after infection
        )
        self.update_pars(pars, **kwargs)

        self.define_states(
            ss.FloatArr('state', default=TetanusStates.NONE),
            ss.FloatArr('ti_infected'),
            ss.FloatArr('rel_sus', default=1.0),
        )


        
    """ Determines if an agent is infectious and can transmit tetanus. """
    @property
    def infectious(self):   
        return self.state == TetanusStates.INFECTED

    @property
    def immnunized(self):
        return self.state == TetanusStates.IMMUNIZED

    def set_prognoses(self, uids, from_uids=None):
        """ Handles new infections and vaccination effects. """
        super().set_prognoses(uids, from_uids)

        return


    def step(self):
        """ Executes transitions at each time step (infection, recovery, waning immunity). """
        super().step()
        p = self.pars
        ti = self.ti


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
    
    def start_vaccination(self, uids):
        """ Administers vaccination to selected individuals. """
        if len(uids) == 0:
            return 0  # No one to vaccinate

        vaccinated_uids = self.pars.vaccine_prob.filter(uids)
        self.vaccinated[vaccinated_uids] = True
        self.state[vaccinated_uids] = TetanusStates.IMMUNIZED

        return len(vaccinated_uids)

    def plot(self):
        """ Generates a plot of disease progression over time. """
        fig = plt.figure()
        for rkey in self.results.keys():
            if rkey == 'timevec':
                continue
            plt.plot(self.results['timevec'], self.results[rkey], label=rkey.title())
        plt.legend()
        plt.show()
        return fig
