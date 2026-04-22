"""
Intervention modules for zero-dose vaccination simulation.

Port notes (Starsim 3.3.3)
--------------------------
Stochastic agent selection uses a registered ``ss.random()`` distribution
so RNG is handled by the Starsim framework (supports seeding, CRN, and
MultiSim parallelism). No direct ``np.random`` calls remain.
"""

import numpy as np
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
    """

    TARGET_DISEASES = ('diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib')

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            start_day     = 0,
            end_day       = 365 * 50,
            coverage      = 0.8,
            efficacy      = 0.9,
            age_min       = 0,    # months
            age_max       = 60,   # months
            year          = None,
            routine_prob  = 0.1,
            selection_rng = ss.random(),
        )
        self.define_states(
            ss.BoolState('vaccinated',    default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated',  label='Time of vaccination'),
            ss.FloatArr('doses_received', default=0, label='Number of doses received'),
        )
        self.update_pars(pars, **kwargs)
        return

    def init_pre(self, sim):
        """ Resolve campaign years (or routine window) to sim timesteps. """
        super().init_pre(sim)
        if self.pars.year is not None:
            # Campaign mode: vaccinate at the timestep closest to each target year
            self.timepoints = []
            for year in self.pars.year:
                ti = sim.t.yearvec.searchsorted(year)
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
        age_months    = self.sim.people.age * 12
        age_eligible  = (age_months >= self.pars.age_min) & (age_months <= self.pars.age_max)
        return (age_eligible & ~self.vaccinated).uids

    def step(self):
        """
        One vaccination round (routine or campaign).

        Returns the UIDs of agents vaccinated on this timestep.
        """
        sim = self.sim
        if sim is None or sim.ti not in self.timepoints:
            return ss.uids()

        eligible_uids = self.check_eligibility()
        if len(eligible_uids) == 0:
            return ss.uids()

        if self.pars.year is not None:
            prob = float(self.pars.coverage)
        else:
            prob = float(self.pars.routine_prob) * float(self.pars.coverage)
            prob = min(1.0, max(0.0, prob))

        if prob <= 0:
            return ss.uids()

        # Per-agent Bernoulli selection via managed RNG stream
        selection_draws = self.pars.selection_rng.rvs(eligible_uids)
        selected_mask   = selection_draws < prob
        if not np.any(selected_mask):
            return ss.uids()
        vaccinated_uids = eligible_uids[selected_mask]

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
