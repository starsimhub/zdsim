""" Calibrate zero-dose simulation parameters from administrative data. """

import dataclasses
from dataclasses import asdict, dataclass, field, replace

import numpy as np
import pandas as pd

from zdsim.zerodose_data import empirical_zerodose_proxy_dtp1

__all__ = ['SimulationParameters', 'build_calibration_parameters', 'empirical_summary_from_dataframe', 'with_intervention_delivery']

@dataclass(frozen=True)
class SimulationParameters:
    """ Immutable set of model inputs used to build one Starsim scenario.

    Only tetanus is modelled as a disease (per Rono et al. 2024 — the other
    DTP-bracket diseases are eliminated or near-elimination in Kenya). The
    ``household_contacts`` / ``community_contacts`` networks are retained
    because the vaccination intervention is still delivered through them.
    """
    seed: int
    birth_rate: float  # crude CBR per 1000/yr, kept for reporting and back-compat
    death_rate: float
    household_contacts: int
    community_contacts: int
    tetanus_init_p: float  # initial prevalence seeded from reported monthly cases
    intervention_routine_prob: float
    intervention_coverage: float
    intervention_efficacy: float
    intervention_age_min: float
    intervention_age_max: float
    intervention_booster_age_max: float = 0.0  # 0 disables boosters (default, realistic for low-coverage EPI)
    intervention_booster_interval_years: float = 1.0
    fertility_rate: float = 130.0  # births per 1000 women aged 15-49 per year (Kenya-like default)
    data_derived: dict = field(default_factory=dict)

    def as_log_dict(self):
        """ Return the parameter set as a plain dict (for JSON logging). """
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        """ Rebuild a parameter set from ``d``; extra keys are ignored. """
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


def _clip_cov(x):
    """ Clip coverage to the plausible 45–98% range. """
    return float(np.clip(x, 0.45, 0.98))


def demographics_from_live_births(df, *, population, default_birth_rate=25.0, default_death_rate=8.0):
    """ Return (birth_rate, death_rate, meta) per 1000/yr, from data if available. """
    meta = {"population_used": population}
    if df is None or "estimated_lb" not in df.columns:
        meta["birth_rate_source"] = "default"
        return default_birth_rate, default_death_rate, meta

    lb             = pd.to_numeric(df["estimated_lb"], errors="coerce").astype(float)
    mean_annual_lb = float(np.nanmean(lb))
    meta["mean_annual_live_births_estimated"] = mean_annual_lb

    if population is not None and population > 0:
        br = 1000.0 * mean_annual_lb / float(population)
        br = float(np.clip(br, 10.0, 55.0))
        meta["birth_rate_source"] = "estimated_lb / population"
        return br, default_death_rate, meta

    meta["birth_rate_source"] = "default (set --population to calibrate birth_rate from estimated_lb)"
    return default_birth_rate, default_death_rate, meta


def tetanus_init_from_reported_cases(df, *, reference_population):
    """ Initial tetanus Bernoulli prevalence, scaled from reported cases when available. """
    default = 0.001
    if df is None or reference_population is None or reference_population <= 0:
        return default
    if "tetanus" not in df.columns:
        return default
    m = float(np.nanmean(pd.to_numeric(df["tetanus"], errors="coerce")))
    return float(min(0.05, max(1e-4, (m * 12.0) / reference_population)))


def build_calibration_parameters(*, seed, df, population, empirical):
    """ Build a base parameter set with demographics, tetanus init, and data-derived coverage. """
    br, dr, demo_meta = demographics_from_live_births(df, population=population)
    tetanus_init_p    = tetanus_init_from_reported_cases(df, reference_population=population)

    if empirical:
        cov     = _clip_cov(float(empirical["mean_dtp1_coverage_proxy"]))
        emp_tag = True
    else:
        cov     = 0.65
        emp_tag = False

    # Convert CBR (births per 1000 total population) to ASFR proxy (births per
    # 1000 women aged 15-49 per year). With an exp(-0.022*a) age pyramid,
    # women aged 15-49 are ~22.9% of total population, so fertility_rate
    # = birth_rate / 0.229 ~= birth_rate * 4.37.
    fertility_rate = float(br * 4.37)

    return SimulationParameters(
        seed                      = seed,
        birth_rate                = br,
        death_rate                = dr,
        fertility_rate            = fertility_rate,
        household_contacts        = 5,
        community_contacts        = 15,
        tetanus_init_p            = tetanus_init_p,
        intervention_routine_prob        = 0.03,
        intervention_coverage            = cov,
        intervention_efficacy            = 0.9,
        intervention_age_min             = 0.0,
        intervention_age_max             = 5.0,
        intervention_booster_age_max     = 0.0,  # boosters disabled: primary series only
        intervention_booster_interval_years = 1.0,
        data_derived = {
            "demographics": demo_meta,
            "intervention_coverage_from_mean_dtp1_proxy": emp_tag,
        },
    )


def with_intervention_delivery(base, *, routine_prob, coverage=None):
    """ Return a copy of ``base`` with updated routine_prob and (optionally) coverage. """
    cov = base.intervention_coverage if coverage is None else coverage
    return replace(
        base,
        intervention_routine_prob = float(routine_prob),
        intervention_coverage     = float(cov),
    )


def empirical_summary_from_dataframe(df):
    """ Return the empirical zero-dose summary, or None if ``df`` is None. """
    if df is None:
        return None
    return empirical_zerodose_proxy_dtp1(df)
