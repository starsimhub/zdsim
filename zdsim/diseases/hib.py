""" Haemophilus influenzae type b (Hib) module: person-to-person SIR. """

import starsim as ss


class Hib(ss.Infection):
    """ Hib (R0 ~ 1.75, β = 17.5/yr) with meningitis comorbidity. """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            beta         = ss.peryear(17.5),
            init_prev    = ss.bernoulli(p=0.01),
            dur_inf      = ss.lognorm_ex(mean=ss.years(0.1)),
            p_death      = ss.bernoulli(p=0.03),
            p_severe     = ss.bernoulli(p=0.15),
            p_meningitis = ss.bernoulli(p=0.1),
        )
        self.define_states(
            ss.BoolState('recovered',    label='Recovered'),
            ss.FloatArr('ti_recovered',  label='Time of recovery'),
            ss.FloatArr('ti_dead',       label='Time of death'),
            ss.BoolState('severe',       label='Severe disease'),
            ss.BoolState('meningitis',   label='Meningitis'),
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
        self.severe[uids]     = p.p_severe.rvs(uids)
        self.meningitis[uids] = p.p_meningitis.rvs(uids)
        dur_inf   = p.dur_inf.rvs(uids)
        will_die  = p.p_death.rvs(uids)
        dead_uids = uids[will_die]
        rec_uids  = uids[~will_die]
        self.ti_dead[dead_uids]     = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        return

    def step_state(self):
        """ Recover and kill as scheduled. """
        sim = self.sim
        ti  = sim.ti
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered]  = False
            self.recovered[recovered] = True
            self.immunity[recovered]  = 0.8

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
