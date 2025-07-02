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
        self.define_pars(
            init_prev = ss.bernoulli(0.1),  # 10% initially infected for testing
            beta = 1.3,                    # Infection rate (per month)
            gamma = 0.25,                  # Recovery rate (per month, 3 months infectious period)
            waning = 0.055,                # Immunity waning rate (per month)
            vaccine_prob = 0.25,           # Probability of vaccination per month
            vaccine_efficacy = 0.9,        # Probability vaccine produces immunity
        )
        
        self.update_pars(pars, **kwargs)
        self.pars.beta = ss.beta_per_step(self.pars.beta)
        self.define_states(
            ss.FloatArr('state', default=TST.SUSCEPTIBLE),
            ss.BoolArr('immune', default=False),
            ss.BoolArr('vaccinated', default=False),
            ss.FloatArr('time_infected'),
            ss.FloatArr('time_recovered'),
            ss.FloatArr('time_vaccinated'),
        )

    def step(self):
        p = self.pars
        ti = self.ti
        # Vaccination step for susceptibles
        sus = (self.state == TST.SUSCEPTIBLE) & (~self.vaccinated)
        n_sus = np.sum(sus)
        if n_sus > 0:
            to_vacc = np.random.rand(n_sus) < p.vaccine_prob
            vacc_uids = np.where(sus)[0][to_vacc]
            if len(vacc_uids) > 0:
                eff = np.random.rand(len(vacc_uids)) < p.vaccine_efficacy
                immune_uids = np.array(vacc_uids)[eff]
                self.vaccinated[ss.uids(vacc_uids)] = True
                self.time_vaccinated[ss.uids(vacc_uids)] = ti
                self.immune[ss.uids(immune_uids)] = True
        # Waning immunity
        waning = (self.immune == True)
        n_waning = np.sum(waning)
        if n_waning > 0:
            lose_imm = np.random.rand(n_waning) < p.waning
            lose_imm_uids = np.where(waning)[0][lose_imm]
            if len(lose_imm_uids) > 0:
                self.immune[ss.uids(lose_imm_uids)] = False
                self.vaccinated[ss.uids(lose_imm_uids)] = False
        # Environmental exposure for susceptibles (not immune)
        sus = (self.state == TST.SUSCEPTIBLE) & (~self.immune)
        n_sus = np.sum(sus)
        if n_sus > 0:
            new_inf = np.random.rand(n_sus) < (p.beta / 1000)  # Adjust for population size
            new_inf_uids = np.where(sus)[0][new_inf]
            if len(new_inf_uids) > 0:
                self.set_prognoses(ss.uids(new_inf_uids))
        # Recovery
        inf = (self.state == TST.INFECTED)
        n_inf = np.sum(inf)
        if n_inf > 0:
            recover = np.random.rand(n_inf) < p.gamma
            rec_uids = np.where(inf)[0][recover]
            if len(rec_uids) > 0:
                self.state[ss.uids(rec_uids)] = TST.SUSCEPTIBLE
                self.immune[ss.uids(rec_uids)] = False  # SIS: return to susceptible, not immune
        return

    def set_prognoses(self, uids, from_uids=None):
        super().set_prognoses(uids, from_uids)
        self.state[uids] = TST.INFECTED
        self.time_infected[uids] = self.ti
        return

    def init_results(self):
        super().init_results()
        self.define_results(
            # ss.Result('n_infected', dtype=int, label='Number infected'),  # Already defined by parent
            # ss.Result('n_susceptible', dtype=int, label='Number susceptible'),  # Already defined by parent
            ss.Result('n_immune', dtype=int, label='Number immune'),
            ss.Result('n_vaccinated', dtype=int, label='Number vaccinated'),
        )
        return

    def update_results(self):
        super().update_results()
        self.results['n_infected'][self.ti] = np.sum(self.state == TST.INFECTED)
        self.results['n_susceptible'][self.ti] = np.sum(self.state == TST.SUSCEPTIBLE)
        self.results['n_immune'][self.ti] = np.sum(self.immune)
        self.results['n_vaccinated'][self.ti] = np.sum(self.vaccinated)
        return
