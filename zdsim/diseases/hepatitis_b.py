"""
Hepatitis B disease module.

Implemented as a standard Starsim ``ss.Infection`` with person-to-person
transmission driven by β.  Chronic carriers remain infected after the
acute phase completes; the pentavalent vaccine provides protection.
"""

import numpy as np
import starsim as ss


class HepatitisB(ss.Infection):
    """
    Hepatitis B disease module.

    Literature R0: 0.5–1.5 (Kenya). Target R0 ≈ 1.0 with duration ≈ 2.0 yr
    ⇒ β = R0 / duration = 0.5 per year.
    """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            beta               = ss.peryear(0.5),
            init_prev          = ss.bernoulli(p=0.005),
            dur_inf            = ss.lognorm_ex(mean=ss.years(2.0)),
            p_death            = ss.bernoulli(p=0.02),
            p_chronic          = ss.bernoulli(p=0.05),
            p_severe           = ss.bernoulli(p=0.1),
            age_susceptibility = ss.bernoulli(p=0.7),
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
        """ Set prognoses upon hepatitis B infection (uids: infected agents). """
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
        """ Acute recovery and scheduled deaths (chronic carriers stay infected). """
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
        """ Reset state flags for agents who die. """
        self.susceptible[uids] = False
        self.infected[uids]    = False
        self.recovered[uids]   = False
        return
