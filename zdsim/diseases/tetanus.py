"""
Tetanus disease module with age-specific wound-exposure dynamics.

Tetanus (*Clostridium tetani*) is **not** person-to-person transmissible; β
is 0 and the Starsim network transmission step is effectively inert.
Infection occurs through wound contamination, and each age group has its
own calibrated annual wound-exposure rate.

Four age-specific segments
--------------------------
- **Neonatal** (0–28 days): high CFR; partial protection from maternal vaccination.
- **Peri-neonatal** (29–60 days): moderate CFR.
- **Childhood** (2 months – 15 years): reduced CFR, vaccine-derived immunity.
- **Adult** (15+ years): Kenya has achieved MNT elimination; rarely reached in
  the pediatric projection window but retained for completeness.

Vaccine-induced immunity wanes exponentially (``waning=0.055``/yr per the
Rono et al. 2024 brief). Once an agent's immunity falls below 0.1 it is
reset to 0.0 and the agent re-enters the susceptible pool — completing the
SIS cycle.

Port notes (Starsim 3.3.3)
--------------------------
All stochastic draws use registered Starsim distributions
(``ss.random()`` / ``ss.bernoulli``) so that RNG is managed per-module by
the framework (supports CRN, MultiSim, and reproducible seeding).
"""

import numpy as np
import starsim as ss


class Tetanus(ss.Infection):
    """Age-stratified tetanus with wound-exposure transmission and waning."""

    def __init__(self, pars=None, **kwargs):
        super().__init__()

        self.define_pars(
            # Core infection pars -------------------------------------------------
            beta=ss.peryear(0.0),                       # Not person-to-person
            init_prev=ss.bernoulli(p=0.001),
            dur_inf=ss.lognorm_ex(mean=ss.years(3/12)), # gamma = 3/12 (brief)
            p_death=ss.bernoulli(p=0.1),                # Fallback CFR
            p_severe=ss.bernoulli(p=0.3),
            wound_rate=ss.peryear(0.1),                 # Fallback wound rate
            waning=ss.peryear(0.055),                   # Brief: waning = 0.055

            # Age-specific CFR (calibrated) --------------------------------------
            neonatal_cfr=0.718,
            peri_neonatal_cfr=0.521,
            childhood_cfr=0.480,
            adult_cfr=0.327,

            # Age-specific wound rates (calibrated) ------------------------------
            neonatal_wound_rate=ss.peryear(0.0111),
            peri_neonatal_wound_rate=ss.peryear(0.0213),
            childhood_wound_rate=ss.peryear(0.0637),
            adult_wound_rate=ss.peryear(0.6346),

            # Maternal protection for neonates (calibrated) ----------------------
            maternal_vaccination_efficacy=0.743,
            maternal_vaccination_coverage=0.365,

            # RNG streams (one per event type for CRN stability) ----------------
            wound_rng=ss.random(),
            infection_rng=ss.random(),
            waning_rng=ss.random(),
            death_rng=ss.random(),
        )

        self.define_states(
            ss.BoolState('recovered', label='Recovered'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.BoolState('severe', label='Severe disease'),
            ss.BoolState('vaccinated', default=False, label='Vaccinated'),
            ss.FloatArr('ti_vaccinated', label='Time of vaccination'),
            ss.FloatArr('immunity', default=0.0, label='Immunity level'),
            ss.FloatArr('ti_wound', label='Time of wound exposure'),
            ss.BoolState('neonatal', default=False, label='Neonatal tetanus (0-28 days)'),
            ss.BoolState('peri_neonatal', default=False, label='Peri-neonatal tetanus (29-60 days)'),
            ss.BoolState('childhood', default=False, label='Childhood tetanus (2 months-15 years)'),
            ss.BoolState('adult', default=False, label='Adult tetanus (15+ years)'),
            ss.BoolState('maternal_vaccinated', default=False, label='Maternal vaccination'),
            ss.FloatArr('maternal_immunity', default=0.0, label='Maternal immunity level'),
        )

        self.update_pars(pars, **kwargs)

    # ------------------------------------------------------------------
    # Per-timestep dynamics
    # ------------------------------------------------------------------
    def step(self):
        """Wound-exposure transmission with four age-specific segments.

        Vaccinated agents are *not* excluded here: protection is applied via
        per-agent ``immunity``. Once immunity wanes to zero (see
        ``step_state``) the agent is fully re-exposed, completing the SIS
        cycle described in the brief (waning = 0.055).
        """
        sim = self.sim
        ti = sim.ti
        age_days = sim.people.age * 365

        susceptible = self.susceptible
        if not len(susceptible):
            return ss.uids()
        susceptible_uids = susceptible.uids
        age_s = age_days[susceptible_uids]

        # Age-group masks
        segments = [
            ('neonatal',      age_s <= 28),
            ('peri_neonatal', (age_s > 28)  & (age_s <= 60)),
            ('childhood',     (age_s > 60)  & (age_s <= 15 * 365)),
            ('adult',          age_s >  15 * 365),
        ]
        for age_group, mask in segments:
            if np.any(mask):
                self._handle_age_specific_wounds(susceptible_uids[mask], age_group, ti)

        return ss.uids()

    def _handle_age_specific_wounds(self, uids, age_group, ti):
        """Draw per-agent wound events and possible tetanus infections."""
        if len(uids) == 0:
            return

        rate_par = {
            'neonatal':      self.pars.neonatal_wound_rate,
            'peri_neonatal': self.pars.peri_neonatal_wound_rate,
            'childhood':     self.pars.childhood_wound_rate,
            'adult':         self.pars.adult_wound_rate,
        }.get(age_group, self.pars.wound_rate)
        wound_prob = rate_par.to_prob(self.sim.t.dt)

        # Wound draw via managed RNG stream (one call per agent, independent of outcome count)
        wound_draws = self.pars.wound_rng.rvs(uids)
        wound_mask = wound_draws < wound_prob
        if not np.any(wound_mask):
            return
        wound_exposure = uids[wound_mask]
        self.ti_wound[wound_exposure] = ti

        # Per-agent protection from immunity (vaccine/natural) + maternal for neonates
        immunity = self.immunity[wound_exposure]
        if age_group == 'neonatal':
            protection = np.maximum(immunity, self.maternal_immunity[wound_exposure])
        else:
            protection = immunity
        tetanus_risk = 1.0 - protection

        # Per-agent infection draw via its own RNG stream
        infection_draws = self.pars.infection_rng.rvs(wound_exposure)
        tetanus_mask = infection_draws < tetanus_risk
        tetanus_cases = wound_exposure[tetanus_mask]
        if len(tetanus_cases) > 0:
            self.set_prognoses(tetanus_cases, sources=None, age_group=age_group)

    def set_prognoses(self, uids, sources=None, age_group=None):
        """Set prognoses upon tetanus infection (age-specific CFR)."""
        super().set_prognoses(uids, sources)
        ti = self.t.ti
        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti

        if age_group == 'neonatal':
            self.neonatal[uids] = True
            cfr = self.pars.neonatal_cfr
        elif age_group == 'peri_neonatal':
            self.peri_neonatal[uids] = True
            cfr = self.pars.peri_neonatal_cfr
        elif age_group == 'childhood':
            self.childhood[uids] = True
            cfr = self.pars.childhood_cfr
        elif age_group == 'adult':
            self.adult[uids] = True
            cfr = self.pars.adult_cfr
        else:
            cfr = self.pars.p_death.pars.p if hasattr(self.pars.p_death, 'pars') else 0.1

        self.severe[uids] = self.pars.p_severe.rvs(uids)
        dur_inf = self.pars.dur_inf.rvs(uids)

        # Age-specific CFR applied via managed RNG stream
        will_die = self.pars.death_rng.rvs(uids) < cfr
        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]
        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]

    def step_state(self):
        """Recovery, waning immunity, and scheduled deaths."""
        sim = self.sim
        ti = sim.ti

        # Recovery
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        if len(recovered):
            self.infected[recovered] = False
            self.recovered[recovered] = True
            self.immunity[recovered] = 0.9

        # Waning immunity (brief: waning = 0.055/yr).  On a waning event we
        # halve immunity; if it drops below 0.1, reset to 0 and re-enter the
        # susceptible pool (complete SIS cycle).
        waning_prob = self.pars.waning.to_prob(sim.t.dt)
        immune_agents = (self.immunity > 0).uids
        if len(immune_agents):
            waning_draws = self.pars.waning_rng.rvs(immune_agents)
            waned_uids = immune_agents[waning_draws < waning_prob]
            if len(waned_uids):
                self.immunity[waned_uids] *= 0.5
                low_immunity = self.immunity[waned_uids] < 0.1
                if np.any(low_immunity):
                    susceptible_again = waned_uids[low_immunity]
                    self.immunity[susceptible_again] = 0.0
                    self.susceptible[susceptible_again] = True
                    self.recovered[susceptible_again] = False
                    self.vaccinated[susceptible_again] = False

        # Scheduled deaths
        deaths = (self.ti_dead <= ti).uids
        if len(deaths):
            sim.people.request_death(deaths)

    def step_die(self, uids):
        self.susceptible[uids] = False
        self.infected[uids] = False
        self.recovered[uids] = False
