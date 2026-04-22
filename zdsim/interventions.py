"""
Intervention modules for zero-dose vaccination simulation.

Starsim idioms (3.3.3)
----------------------
Selection is driven by ``ss.bernoulli`` + ``.filter(uids)`` -- the "define_pars
+ filter" workhorse pattern documented in the Starsim distributions guide. A
dynamic callable computes the per-agent probability each step (routine vs
campaign mode, ``routine_prob * coverage``), so users can override ``p_vx``
with their own Bernoulli without modifying the module. No direct ``np.random``
usage -- RNG is managed by Starsim (supports seeding, CRN, and MultiSim).
"""

import starsim as ss


class ZeroDoseVaccination(ss.Intervention):
    """
    Zero-dose vaccination intervention.

    Targets children who have never been vaccinated and delivers the
    pentavalent (DTP-HepB-Hib) dose.

    Delivery modes
    --------------
    - **Routine** (default): every timestep in ``[start_day, end_day]`` each
      eligible unvaccinated child is vaccinated with probability
      ``routine_prob * coverage``.
    - **Campaign**: if ``year`` is supplied, vaccination occurs only on the
      timesteps closest to those calendar years, with probability ``coverage``.

    Protection is applied to all five pentavalent disease modules by setting
    ``disease.immunity = efficacy`` and ``disease.rel_sus = 1 - efficacy``.
    Immunity waning is handled inside each disease module (see ``tetanus.py``).

    **Example**::

        import starsim as ss
        import zdsim as zds

        sim = ss.Sim(
            diseases=[zds.Diphtheria(), zds.Tetanus()],
            interventions=zds.ZeroDoseVaccination(coverage=0.85, efficacy=0.9),
            networks='random',
        )
        sim.run()
    """

    TARGET_DISEASES = ('diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib')

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            start_day    = 0,
            end_day      = 365 * 50,
            coverage     = 0.8,
            efficacy     = 0.9,
            age_min      = 0,    # months
            age_max      = 60,   # months
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
        """
        Dynamic Bernoulli probability: ``coverage`` in campaign mode,
        ``routine_prob * coverage`` in routine mode (clipped to [0, 1]).

        Args:
            module (ZeroDoseVaccination): the intervention instance
            sim    (ss.Sim):               the running simulation
            uids   (UIDs):                  agents eligible this step

        Returns:
            p (float): per-step vaccination probability (same for all uids).
        """
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
        """ UIDs of unvaccinated agents whose age (in months) is in the eligible window. """
        age_months   = self.sim.people.age * 12
        age_eligible = (age_months >= self.pars.age_min) & (age_months <= self.pars.age_max)
        return (age_eligible & ~self.vaccinated).uids

    def step(self):
        """
        One vaccination round (routine or campaign).

        Returns:
            vaccinated_uids (UIDs): agents vaccinated on this timestep.
        """
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
