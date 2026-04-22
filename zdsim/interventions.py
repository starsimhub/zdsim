"""
Intervention modules for zero-dose vaccination simulation.
"""

import starsim as ss
import numpy as np


class ZeroDoseVaccination(ss.Intervention):
    """
    Zero-dose vaccination intervention.

    Targets children who have received zero doses of routine vaccines and
    provides the DTP-HepB-Hib (pentavalent) vaccine.

    Delivery modes
    --------------
    Routine (default): every timestep within [start_day, end_day], each
        eligible unvaccinated child is vaccinated with probability
        ``routine_prob * coverage``.
    Campaign: if ``year`` is set, vaccination occurs only on the timestep
        closest to each listed calendar year, with probability ``coverage``.

    Protection is applied to all five pentavalent disease modules by setting
    ``disease.immunity = efficacy`` and ``disease.rel_sus = 1 - efficacy``.
    Immunity waning is handled inside each disease module (see tetanus.py).
    """

    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            start_day=0,
            end_day=365 * 50,
            coverage=0.8,
            efficacy=0.9,
            age_min=0,    # months
            age_max=60,   # months
            year=None,
            routine_prob=0.1,
        )
        self.define_states(
            ss.BoolState('vaccinated', default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('doses_received', default=0, label='Number of doses received'),
        )
        self.update_pars(pars, **kwargs)
        return

    def init_pre(self, sim):
        super().init_pre(sim)
        if self.pars.year is not None:
            self.timepoints = []
            for year in self.pars.year:
                ti = sim.t.yearvec.searchsorted(year)
                if ti < len(sim.t.yearvec):
                    self.timepoints.append(ti)
        else:
            dt_years = sim.t.dt.years if hasattr(sim.t.dt, 'years') else sim.t.dt
            start_ti = int(self.pars.start_day / (dt_years * 365))
            end_ti = int(self.pars.end_day / (dt_years * 365))
            self.timepoints = list(range(start_ti, min(end_ti, len(sim.t))))
        return

    def check_eligibility(self):
        age_months = self.sim.people.age * 12
        age_eligible = (age_months >= self.pars.age_min) & (age_months <= self.pars.age_max)
        return (age_eligible & ~self.vaccinated).uids

    def step(self):
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

        n_vaccinate = int(len(eligible_uids) * prob)
        if n_vaccinate <= 0:
            return ss.uids()

        selected = np.random.choice(len(eligible_uids), size=n_vaccinate, replace=False)
        vaccinated_uids = eligible_uids[selected]

        self.vaccinated[vaccinated_uids] = True
        self.ti_vaccinated[vaccinated_uids] = sim.ti
        self.doses_received[vaccinated_uids] += 1
        self._apply_vaccine_effects(vaccinated_uids)

        return vaccinated_uids

    def _apply_vaccine_effects(self, uids):
        sim = self.sim
        for name in ('diphtheria', 'tetanus', 'pertussis', 'hepatitis_b', 'hib'):
            if name not in sim.diseases:
                continue
            dis = sim.diseases[name]
            dis.vaccinated[uids] = True
            dis.ti_vaccinated[uids] = sim.ti
            dis.immunity[uids] = self.pars.efficacy
            dis.rel_sus[uids] = 1.0 - self.pars.efficacy

    def init_results(self):
        super().init_results()

    def update_results(self):
        super().update_results()
