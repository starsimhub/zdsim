"""
Pertussis (Whooping Cough) disease module.

Implemented as a standard Starsim ``ss.Infection`` with person-to-person
transmission driven by β, plus exponential waning of vaccine/natural
immunity.  The pentavalent vaccine provides protection; zero-dose
children are unprotected.
"""

import numpy as np
import starsim as ss


class Pertussis(ss.Infection):
    """
    Pertussis disease module.

    Literature R0: 5.5–17.5 (Kenya, highly transmissible). Target R0 ≈ 11.5
    with duration ≈ 0.25 yr ⇒ β = R0 / duration = 46.0 per year.
    """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            beta=ss.peryear(46.0),
            init_prev=ss.bernoulli(p=0.02),
            dur_inf=ss.lognorm_ex(mean=ss.years(0.25)),
            p_death=ss.bernoulli(p=0.01),
            p_severe=ss.bernoulli(p=0.05),
            age_susceptibility=ss.bernoulli(p=0.9),
            waning_immunity=ss.peryear(0.1),
        )
        self.define_states(
            ss.BoolState('recovered', label='Recovered'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.BoolState('severe', label='Severe disease'),
            ss.BoolState('vaccinated', default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('immunity', default=0.0, label='Immunity level'),
        )
        self.update_pars(pars, **kwargs)

    def set_prognoses(self, uids, sources=None):
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti

        p = self.pars
        self.severe[uids] = p.p_severe.rvs(uids)
        dur_inf = p.dur_inf.rvs(uids)
        will_die = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]

    def step_state(self):
        sim = self.sim
        ti = sim.ti
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered] = False
            self.recovered[recovered] = True
            self.immunity[recovered] = 0.7

        self._wane_immunity()

        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)

    def _wane_immunity(self):
        """Exponential waning of immunity; rel_sus follows 1 - immunity."""
        waning_rate = self.pars.waning_immunity.to_prob(self.sim.t.dt)
        has_immunity = (self.immunity > 0).uids
        if len(has_immunity):
            self.immunity[has_immunity] *= (1 - waning_rate)
            self.rel_sus[has_immunity] = np.maximum(0, 1 - self.immunity[has_immunity])

    def step_die(self, uids):
        self.susceptible[uids] = False
        self.infected[uids] = False
        self.recovered[uids] = False
