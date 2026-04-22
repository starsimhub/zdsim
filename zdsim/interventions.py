""" Intervention modules: zero-dose (never-vaccinated) pentavalent delivery. """

import starsim as ss


class ZeroDoseVaccination(ss.Intervention):
    """ Vaccinate unvaccinated under-fives (routine or campaign mode). """

    TARGET_DISEASES = ('diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib')

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            start_day    = 0,
            end_day      = 365 * 50,
            coverage     = 0.8,
            efficacy     = 0.9,
            age_min      = 0.0,  # years
            age_max      = 5.0,  # years
            year         = None,
            routine_prob = 0.1,
            # p_vx is the Bernoulli that decides whether each eligible child
            # gets vaccinated on a given step. The dynamic callable below
            # computes the right probability for routine vs campaign mode.
            p_vx         = ss.bernoulli(p=self._compute_p_vx),
        )
        self.define_states(
            ss.BoolState('vaccinated',    default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated',  label='Time of vaccination'),
            ss.FloatArr('doses_received', default=0,     label='Number of doses received'),
        )
        self.update_pars(pars, **kwargs)
        return

    @staticmethod
    def _compute_p_vx(module, sim, uids):
        """ Per-step vaccination probability (campaign or ``routine_prob*coverage``). """
        p = module.pars
        if p.year is not None:
            prob = float(p.coverage)
        else:
            prob = float(p.routine_prob) * float(p.coverage)
        return min(1.0, max(0.0, prob))

    def init_pre(self, sim):
        """ Resolve campaign years (or routine window) to sim timesteps. """
        super().init_pre(sim)
        if self.pars.year is not None:
            # Campaign mode: vaccinate at the timestep closest to each target year
            self.timepoints = []
            for yr in self.pars.year:
                ti = sim.t.yearvec.searchsorted(yr)
                if ti < len(sim.t.yearvec):
                    self.timepoints.append(ti)
        else:
            # Routine mode: every timestep in the [start_day, end_day] window
            dt_years = sim.t.dt.years if hasattr(sim.t.dt, 'years') else sim.t.dt
            start_ti = int(self.pars.start_day / (dt_years * 365))
            end_ti   = int(self.pars.end_day   / (dt_years * 365))
            self.timepoints = list(range(start_ti, min(end_ti, len(sim.t))))
        return

    def check_eligibility(self):
        """ UIDs of unvaccinated agents whose age (in years) is in the eligible window. """
        age_years    = self.sim.people.age
        age_eligible = (age_years >= self.pars.age_min) & (age_years <= self.pars.age_max)
        return (age_eligible & ~self.vaccinated).uids

    def step(self):
        """ One vaccination round; returns UIDs vaccinated this step. """
        sim = self.sim
        if sim is None or sim.ti not in self.timepoints:
            return ss.uids()

        eligible_uids = self.check_eligibility()
        if len(eligible_uids) == 0:
            return ss.uids()

        # Standard "define_pars + filter" pattern: one Bernoulli draw per eligible
        # agent, with per-agent RNG keyed by UID (CRN-safe).
        vaccinated_uids = self.pars.p_vx.filter(eligible_uids)
        if len(vaccinated_uids) == 0:
            return ss.uids()

        self.vaccinated[vaccinated_uids]      = True
        self.ti_vaccinated[vaccinated_uids]   = sim.ti
        self.doses_received[vaccinated_uids] += 1
        self._apply_vaccine_effects(vaccinated_uids)
        return vaccinated_uids

    def _apply_vaccine_effects(self, uids):
        """ Set ``immunity`` and reduce ``rel_sus`` on each pentavalent module. """
        sim      = self.sim
        efficacy = float(self.pars.efficacy)
        for name in self.TARGET_DISEASES:
            dis = sim.diseases.get(name) if hasattr(sim.diseases, 'get') else getattr(sim.diseases, name, None)
            if dis is None:
                continue
            dis.vaccinated[uids]    = True
            dis.ti_vaccinated[uids] = sim.ti
            dis.immunity[uids]      = efficacy
            dis.rel_sus[uids]       = 1.0 - efficacy
        return
