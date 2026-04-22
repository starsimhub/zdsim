"""
Calibrate zero-dose simulation parameters from administrative data (xlsx).

Parameter bundles are built immediately before each :class:`starsim.Sim` is
constructed so values match the latest data read and calibration step.
"""

import dataclasses
from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np
import pandas as pd

from zdsim.zerodose_data import empirical_zerodose_proxy_dtp1


@dataclass(frozen=True)
class SimulationParameterBundle:
    """
    Complete inputs for one Starsim scenario (one line per field used in build).

    Note: dataclass field annotations are required by @dataclass; they are *not*
    Python type hints in the general sense (Starsim style §2.21 forbids hints on
    function signatures, not on dataclass fields).
    """
    seed: int
    birth_rate: float
    death_rate: float
    household_contacts: int
    community_contacts: int
    diphtheria_beta: float
    pertussis_beta: float
    hepatitis_b_beta: float
    hib_beta: float
    diphtheria_init_p: float
    tetanus_init_p: float  # initial prevalence seeded from reported monthly cases
    pertussis_init_p: float
    hepatitis_b_init_p: float
    hib_init_p: float
    intervention_routine_prob: float
    intervention_coverage: float
    intervention_efficacy: float
    intervention_age_min: float
    intervention_age_max: float
    data_derived: dict = field(default_factory=dict)

    def as_log_dict(self):
        """ Return the bundle as a plain dict (for JSON logging). """
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        """
        Reconstruct a bundle from a plain dict (e.g. loaded from JSON).

        Args:
            d (dict): mapping of field name → value. Extra keys are dropped.

        Returns:
            bundle (SimulationParameterBundle)
        """
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


def _clip_cov(x):
    """ Clip coverage to the plausible 45–98% range. """
    return float(np.clip(x, 0.45, 0.98))


def demographics_from_live_births(df, *, population, default_birth_rate=25.0, default_death_rate=8.0):
    """
    Crude birth/death rates (per 1000 per year) for Starsim demographics.

    Args:
        df                 (DataFrame/None):  monthly administrative data, or None for fallback
        population         (float/None):      total population used to back-calculate birth_rate
        default_birth_rate (float):           fallback CBR (per 1000) when no data
        default_death_rate (float):           fallback CDR (per 1000) when no data

    Returns:
        birth_rate (float), death_rate (float), meta (dict)

    If ``population`` is given, birth_rate ≈ 1000 * mean(annual live births) / population.
    """
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


def disease_init_from_reported_cases(df, *, reference_population):
    """
    Scale initial Bernoulli prevalence from mean monthly cases if population is known.

    Args:
        df                   (DataFrame/None):  monthly administrative data, or None for defaults
        reference_population (float/None):      denominator for per-capita scaling

    Returns:
        init_p (dict): per-disease ``init_prev`` probabilities keyed by
                       ``<disease>_init_p``.
    """
    defaults = {
        "diphtheria_init_p":  0.01,
        "tetanus_init_p":     0.001,
        "pertussis_init_p":   0.02,
        "hepatitis_b_init_p": 0.005,
        "hib_init_p":         0.01,
    }
    if df is None or reference_population is None or reference_population <= 0:
        return defaults

    out = dict(defaults)
    if "tetanus" in df.columns:
        m = float(np.nanmean(pd.to_numeric(df["tetanus"], errors="coerce")))
        p = min(0.05, max(1e-4, (m * 12.0) / reference_population))
        out["tetanus_init_p"] = float(p)
    if "diphtheria" in df.columns:
        m = float(np.nanmean(pd.to_numeric(df["diphtheria"], errors="coerce")))
        p = min(0.05, max(1e-4, (m * 12.0) / reference_population))
        out["diphtheria_init_p"] = float(p)
    return out


def build_calibration_bundle(*, seed, df, population, empirical):
    """
    Build a base bundle: demographics + disease inits + data-derived intervention coverage.

    Args:
        seed       (int):            RNG seed stored in the bundle
        df         (DataFrame/None): monthly administrative data (or None)
        population (float/None):     total population for per-capita scaling
        empirical  (dict/None):      summary from ``empirical_zerodose_proxy_dtp1``

    Returns:
        bundle (SimulationParameterBundle)

    ``intervention_routine_prob`` is set to a neutral mid-range; grid search
    overwrites it for the reference arm before the main run.
    """
    br, dr, demo_meta = demographics_from_live_births(df, population=population)
    init_p            = disease_init_from_reported_cases(df, reference_population=population)

    if empirical:
        cov     = _clip_cov(float(empirical["mean_dtp1_coverage_proxy"]))
        emp_tag = True
    else:
        cov     = 0.65
        emp_tag = False

    return SimulationParameterBundle(
        seed                      = seed,
        birth_rate                = br,
        death_rate                = dr,
        household_contacts        = 5,
        community_contacts        = 15,
        diphtheria_beta           = 0.15,
        pertussis_beta            = 0.25,
        hepatitis_b_beta          = 0.08,
        hib_beta                  = 0.12,
        diphtheria_init_p         = init_p["diphtheria_init_p"],
        tetanus_init_p            = init_p["tetanus_init_p"],
        pertussis_init_p          = init_p["pertussis_init_p"],
        hepatitis_b_init_p        = init_p["hepatitis_b_init_p"],
        hib_init_p                = init_p["hib_init_p"],
        intervention_routine_prob = 0.03,
        intervention_coverage     = cov,
        intervention_efficacy     = 0.9,
        intervention_age_min      = 0.0,
        intervention_age_max      = 60.0,
        data_derived = {
            "demographics": demo_meta,
            "intervention_coverage_from_mean_dtp1_proxy": emp_tag,
        },
    )


def with_intervention_delivery(base, *, routine_prob, coverage=None):
    """
    Copy bundle with updated intervention delivery parameters (immutable).

    Args:
        base         (SimulationParameterBundle): the bundle to copy
        routine_prob (float):                     new per-step routine delivery probability
        coverage     (float/None):                new coverage (None keeps the existing value)

    Returns:
        bundle (SimulationParameterBundle)
    """
    cov = base.intervention_coverage if coverage is None else coverage
    return replace(
        base,
        intervention_routine_prob = float(routine_prob),
        intervention_coverage     = float(cov),
    )


def empirical_summary_from_dataframe(df):
    """ Wrap ``empirical_zerodose_proxy_dtp1`` so runners need not import data code. """
    if df is None:
        return None
    return empirical_zerodose_proxy_dtp1(df)
