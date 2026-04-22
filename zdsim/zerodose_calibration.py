"""
Calibrate zero-dose simulation parameters from administrative data (xlsx).

Parameter bundles are built immediately before each :class:`starsim.Sim` is
constructed so values match the latest data read and calibration step.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any

import numpy as np
import pandas as pd

from zdsim.zerodose_data import empirical_zerodose_proxy_dtp1


@dataclass(frozen=True)
class SimulationParameterBundle:
    """
    Complete inputs for one Starsim scenario (one line per field used in build).
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
    data_derived: dict[str, Any] = field(default_factory=dict)

    def as_log_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SimulationParameterBundle":
        """Reconstruct a bundle from a plain dict (e.g. loaded from JSON)."""
        import dataclasses
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in d.items() if k in known})


def _clip_cov(x: float) -> float:
    return float(np.clip(x, 0.45, 0.98))


def demographics_from_live_births(
    df: pd.DataFrame | None,
    *,
    population: float | None,
    default_birth_rate: float = 25.0,
    default_death_rate: float = 8.0,
) -> tuple[float, float, dict[str, Any]]:
    """
    Crude birth/death rates (per 1000 per year) for Starsim demographics.

    If ``population`` is given, birth_rate ≈ 1000 * mean(annual live births) / population.
    """
    meta: dict[str, Any] = {"population_used": population}
    if df is None or "estimated_lb" not in df.columns:
        meta["birth_rate_source"] = "default"
        return default_birth_rate, default_death_rate, meta

    lb = pd.to_numeric(df["estimated_lb"], errors="coerce").astype(float)
    mean_annual_lb = float(np.nanmean(lb))
    meta["mean_annual_live_births_estimated"] = mean_annual_lb

    if population is not None and population > 0:
        br = 1000.0 * mean_annual_lb / float(population)
        br = float(np.clip(br, 10.0, 55.0))
        meta["birth_rate_source"] = "estimated_lb / population"
        return br, default_death_rate, meta

    meta["birth_rate_source"] = "default (set --population to calibrate birth_rate from estimated_lb)"
    return default_birth_rate, default_death_rate, meta


def disease_init_from_reported_cases(
    df: pd.DataFrame | None,
    *,
    reference_population: float | None,
) -> dict[str, float]:
    """Scale initial Bernoulli prevalence from mean monthly cases if population is known."""
    defaults = {
        "diphtheria_init_p": 0.01,
        "tetanus_init_p": 0.001,
        "pertussis_init_p": 0.02,
        "hepatitis_b_init_p": 0.005,
        "hib_init_p": 0.01,
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


def build_calibration_bundle(
    *,
    seed: int,
    df: pd.DataFrame | None,
    population: float | None,
    empirical: dict[str, Any] | None,
) -> SimulationParameterBundle:
    """
    Build a base bundle: demographics + disease inits + data-derived intervention coverage.

    ``intervention_routine_prob`` is set to a neutral mid-range; grid search overwrites it
    for the reference arm before the main run.
    """
    br, dr, demo_meta = demographics_from_live_births(df, population=population)
    init_p = disease_init_from_reported_cases(df, reference_population=population)

    if empirical:
        cov = _clip_cov(float(empirical["mean_dtp1_coverage_proxy"]))
        emp_tag = True
    else:
        cov = 0.65
        emp_tag = False

    return SimulationParameterBundle(
        seed=seed,
        birth_rate=br,
        death_rate=dr,
        household_contacts=5,
        community_contacts=15,
        diphtheria_beta=0.15,
        pertussis_beta=0.25,
        hepatitis_b_beta=0.08,
        hib_beta=0.12,
        diphtheria_init_p=init_p["diphtheria_init_p"],
        tetanus_init_p=init_p["tetanus_init_p"],
        pertussis_init_p=init_p["pertussis_init_p"],
        hepatitis_b_init_p=init_p["hepatitis_b_init_p"],
        hib_init_p=init_p["hib_init_p"],
        intervention_routine_prob=0.03,
        intervention_coverage=cov,
        intervention_efficacy=0.9,
        intervention_age_min=0.0,
        intervention_age_max=60.0,
        data_derived={
            "demographics": demo_meta,
            "intervention_coverage_from_mean_dtp1_proxy": emp_tag,
        },
    )


def with_intervention_delivery(
    base: SimulationParameterBundle,
    *,
    routine_prob: float,
    coverage: float | None = None,
) -> SimulationParameterBundle:
    """Copy bundle with updated intervention delivery parameters (immutable)."""
    cov = base.intervention_coverage if coverage is None else coverage
    return replace(
        base,
        intervention_routine_prob=float(routine_prob),
        intervention_coverage=float(cov),
    )


def empirical_summary_from_dataframe(df: pd.DataFrame | None) -> dict[str, Any] | None:
    if df is None:
        return None
    return empirical_zerodose_proxy_dtp1(df)
