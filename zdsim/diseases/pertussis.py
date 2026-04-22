""" Pertussis module: person-to-person SIRS with exponential immunity waning. """

import numpy as np
import starsim as ss


class Pertussis(ss.Infection):
    """ Pertussis (R0 ~ 11.5, β = 46/yr) with exponential waning. """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            beta            = ss.peryear(46.0),
            init_prev       = ss.bernoulli(p=0.02),
            dur_inf         = ss.lognorm_ex(mean=ss.years(0.25)),
            p_death         = ss.bernoulli(p=0.01),
            p_severe        = ss.bernoulli(p=0.05),
            waning_immunity = ss.peryear(0.1),
        )
        self.define_states(
            ss.BoolState('recovered',    label='Recovered'),
            ss.FloatArr('ti_recovered',  label='Time of recovery'),
            ss.FloatArr('ti_dead',       label='Time of death'),
            ss.BoolState('severe',       label='Severe disease'),
            ss.BoolState('vaccinated',   default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('immunity',      default=0.0, label='Immunity level'),
        )
        self.update_pars(pars, **kwargs)
        return

    def set_prognoses(self, uids, sources=None):
        """ Set prognoses on infection. """
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids]    = True
        self.ti_infected[uids] = ti

        p = self.pars
        self.severe[uids] = p.p_severe.rvs(uids)
        dur_inf   = p.dur_inf.rvs(uids)
        will_die  = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids  = uids[~will_die]
        self.ti_dead[dead_uids]     = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        return

    def step_state(self):
        """ Recover, wane immunity, and kill as scheduled. """
        sim = self.sim
        ti  = sim.ti
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered]  = False
            self.recovered[recovered] = True
            self.immunity[recovered]  = 0.7

        self._wane_immunity()

        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)
        return

    def _wane_immunity(self):
        """ Exponentially wane ``immunity`` and update ``rel_sus``. """
        waning_rate  = self.pars.waning_immunity.to_prob(self.sim.t.dt)
        has_immunity = (self.immunity > 0).uids
        if len(has_immunity):
            self.immunity[has_immunity] *= (1 - waning_rate)
            self.rel_sus[has_immunity]   = np.maximum(0, 1 - self.immunity[has_immunity])
        return

    def step_die(self, uids):
        """ Clear state flags on death. """
        self.susceptible[uids] = False
        self.infected[uids]    = False
        self.recovered[uids]   = False
        return
