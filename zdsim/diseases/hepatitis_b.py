""" Hepatitis B module: person-to-person SIR with chronic carrier fraction. """

import numpy as np
import starsim as ss


class HepatitisB(ss.Infection):
    """ Hepatitis B (R0 ~ 1, β = 0.5/yr) with chronic carriers. """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            beta      = ss.peryear(0.5),
            init_prev = ss.bernoulli(p=0.005),
            dur_inf   = ss.lognorm_ex(mean=ss.years(2.0)),
            p_death   = ss.bernoulli(p=0.02),
            p_chronic = ss.bernoulli(p=0.05),
            p_severe  = ss.bernoulli(p=0.1),
        )
        self.define_states(
            ss.BoolState('recovered',    label='Recovered'),
            ss.FloatArr('ti_recovered',  label='Time of recovery'),
            ss.FloatArr('ti_dead',       label='Time of death'),
            ss.BoolState('severe',       label='Severe disease'),
            ss.BoolState('chronic',      label='Chronic infection'),
            ss.BoolState('vaccinated',   default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('immunity',      default=0.0, label='Immunity level'),
            ss.FloatArr('ti_chronic',    label='Time of chronic infection'),
        )
        self.update_pars(pars, **kwargs)
        return

    def set_prognoses(self, uids, sources=None):
        """ Set prognoses on infection (flags chronic carriers). """
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids]    = True
        self.ti_infected[uids] = ti

        p = self.pars
        self.severe[uids]  = p.p_severe.rvs(uids)
        chronic            = p.p_chronic.rvs(uids)
        self.chronic[uids] = chronic
        if np.any(chronic):
            self.ti_chronic[uids[chronic]] = ti

        dur_inf   = p.dur_inf.rvs(uids)
        will_die  = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids  = uids[~will_die]
        self.ti_dead[dead_uids]     = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        return

    def step_state(self):
        """ Acute recovery + scheduled deaths; chronic carriers stay infected. """
        sim = self.sim
        ti  = sim.ti
        acute_recovered = (self.infected & ~self.chronic & (self.ti_recovered <= ti)).uids
        if len(acute_recovered):
            self.infected[acute_recovered]  = False
            self.recovered[acute_recovered] = True
            self.immunity[acute_recovered]  = 0.9

        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)
        return

    def step_die(self, uids):
        """ Clear state flags on death. """
        self.susceptible[uids] = False
        self.infected[uids]    = False
        self.recovered[uids]   = False
        return
