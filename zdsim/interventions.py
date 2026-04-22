""" Intervention modules: zero-dose (never-vaccinated) pentavalent delivery. """

import starsim as ss


class ZeroDoseVaccination(ss.Intervention):
    """ Vaccinate zero-dose children (routine or campaign mode).

    A child is "zero-dose" iff they have not yet received any pentavalent dose
    from this intervention. Newborns inherit ``zero_dose = True`` by default
    (Starsim applies defaults to agents added by births), so the pool is
    continuously replenished as the population grows. On first vaccination,
    ``zero_dose`` flips to False and the target diseases receive an immunity
    boost; annual boosters maintain that immunity through ``booster_age_max``.
    """

    TARGET_DISEASES = ('diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib')

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            start_day              = 0,
            end_day                = 365 * 50,
            coverage               = 0.8,
            efficacy               = 0.9,
            age_min                = 0.0,  # years
            age_max                = 5.0,  # years
            year                   = None,
            routine_prob           = 0.1,
            # Optional annual booster: re-apply vaccine effect to agents in
            # [age_min, booster_age_max]. Disabled by default because real EPI
            # systems in low-coverage settings do not deliver annual adult
            # pentavalent boosters. Enable only for sensitivity analyses.
            booster_age_max        = 0.0,
            booster_interval_years = 1.0,
            # p_vx is the Bernoulli that decides whether each eligible child
            # gets vaccinated on a given step. The dynamic callable below
            # computes the right probability for routine vs campaign mode.
            p_vx                   = ss.bernoulli(p=self._compute_p_vx),
        )
        self.define_states(
            ss.BoolState('zero_dose',     default=True,  label='Zero-dose (never vaccinated)'),
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
        dt_years = sim.t.dt.years if hasattr(sim.t.dt, 'years') else sim.t.dt
        if self.pars.year is not None:
            # Campaign mode: vaccinate at the timestep closest to each target year
            self.timepoints = []
            for yr in self.pars.year:
                ti = sim.t.yearvec.searchsorted(yr)
                if ti < len(sim.t.yearvec):
                    self.timepoints.append(ti)
        else:
            # Routine mode: every timestep in the [start_day, end_day] window
            start_ti = int(self.pars.start_day / (dt_years * 365))
            end_ti   = int(self.pars.end_day   / (dt_years * 365))
            self.timepoints = list(range(start_ti, min(end_ti, len(sim.t))))

        # Booster timepoints: every booster_interval_years within the run
        self.booster_timepoints = []
        if float(self.pars.booster_age_max) > float(self.pars.age_max) and self.pars.booster_interval_years:
            interval_ti = max(1, int(round(float(self.pars.booster_interval_years) / float(dt_years))))
            # First booster lands one interval after the first routine/campaign step
            first = (self.timepoints[0] if self.timepoints else 0) + interval_ti
            self.booster_timepoints = list(range(first, len(sim.t), interval_ti))
        return


    def check_eligibility(self):
        """ UIDs of zero-dose agents whose age (in years) is in the eligible window. """
        age_years    = self.sim.people.age
        age_eligible = (age_years >= self.pars.age_min) & (age_years <= self.pars.age_max)
        return (age_eligible & self.zero_dose).uids

    def step(self):
        """ One vaccination round; returns UIDs vaccinated this step (primary + booster). """
        sim = self.sim
        if sim is None:
            return ss.uids()

        newly_vaccinated = ss.uids()
        if sim.ti in self.timepoints:
            eligible_uids = self.check_eligibility()
            if len(eligible_uids) > 0:
                # Standard "define_pars + filter" pattern: one Bernoulli draw per
                # eligible agent, with per-agent RNG keyed by UID (CRN-safe).
                vax_uids = self.pars.p_vx.filter(eligible_uids)
                if len(vax_uids) > 0:
                    self.zero_dose[vax_uids]       = False
                    self.vaccinated[vax_uids]      = True
                    self.ti_vaccinated[vax_uids]   = sim.ti
                    self.doses_received[vax_uids] += 1
                    self._apply_vaccine_effects(vax_uids)
                    newly_vaccinated = vax_uids

        if self.booster_timepoints and sim.ti in self.booster_timepoints:
            age_years = sim.people.age
            in_window = (age_years >= self.pars.age_min) & (age_years <= self.pars.booster_age_max)
            booster_uids = (self.vaccinated & in_window).uids
            if len(booster_uids) > 0:
                self.ti_vaccinated[booster_uids]   = sim.ti
                self.doses_received[booster_uids] += 1
                self._apply_vaccine_effects(booster_uids)

        return newly_vaccinated

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
