""" Post-run analysis helpers: metrics, analyzers, and result extraction.

Everything in this module is simulation-agnostic apart from using Starsim types.
It is imported by both :mod:`run_simulation` (to attach ``YearlyRecorder`` at
sim-build time and to compute summary metrics) and :mod:`zdsim.plots` (to pull
rows/series out of finished sims for plotting).

Only tetanus is modelled; all per-disease metrics therefore refer to tetanus.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import starsim as ss

import zdsim as zds
from zdsim.zerodose_calibration import SimulationParameters


MONTH_ORDER = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}

# Descriptive context diseases from the Rono et al. (2024) Results section.
# These are NOT modelled — they only provide empirical monthly burden context,
# mirroring the brief's "The tables below demonstrate the pneumonia, measles
# and tetanus cases from 2021-2024" paragraph.
CONTEXT_DISEASES = ("pneumonia", "measles", "tetanus")


def context_monthly_means(df):
    """ Mean / min / max / n_months per descriptive context disease column. """
    out = {}
    if df is None:
        return out
    for name in CONTEXT_DISEASES:
        if name not in df.columns:
            continue
        series = pd.to_numeric(df[name], errors="coerce").astype(float)
        series = series[np.isfinite(series)]
        if series.empty:
            continue
        out[name] = dict(
            mean_monthly_cases=float(series.mean()),
            min_monthly_cases=float(series.min()),
            max_monthly_cases=float(series.max()),
            n_months=int(series.size),
        )
    return out


def zerodose_fraction_under5(sim):
    """ Prevalence of zero-dose (never-vaccinated) children under age 5.

    Uses the explicit ``zero_dose`` state on the ``ZeroDoseVaccination`` module.
    When that module is not attached (true no-intervention baseline), every
    under-5 is zero-dose by definition. Fetuses inserted by ``ss.Pregnancy``
    (negative age) are excluded from the denominator.
    """
    age = sim.people.age
    children = ((age >= 0.0) & (age < 5.0)).uids
    if len(children) == 0:
        return float("nan")
    for inv in sim.interventions.values():
        if isinstance(inv, zds.ZeroDoseVaccination):
            return float(np.mean(inv.zero_dose[children]))
    return 1.0


def tetanus_deaths_at_step(sim, ti):
    """ Number of tetanus deaths on timestep ``ti``. """
    tet = sim.diseases.get("tetanus") if hasattr(sim.diseases, "get") else getattr(sim.diseases, "tetanus", None)
    if tet is None or not hasattr(tet, "ti_dead"):
        return 0
    prev = -np.inf if ti <= 0 else float(ti - 1)
    try:
        mask = (tet.ti_dead > prev) & (tet.ti_dead <= float(ti))
    except Exception:
        return 0
    uids = np.asarray(mask.uids if hasattr(mask, "uids") else np.where(np.asarray(mask))[0])
    return int(uids.size)


class YearlyRecorder(ss.Analyzer):
    """ Record yearly zero-dose share and tetanus deaths. """

    def __init__(self):
        super().__init__(name="zerodose_yearly")
        self.rows = []
        self.tetanus_deaths_by_year = {}
        return

    def step(self):
        """ Accumulate tetanus deaths every step; append a row at each year boundary. """
        ti = self.sim.ti
        year = int(np.floor(self.sim.t.yearvec[ti]))
        step_deaths = tetanus_deaths_at_step(self.sim, ti)
        self.tetanus_deaths_by_year[year] = self.tetanus_deaths_by_year.get(year, 0) + step_deaths
        if ti > 0 and int(np.floor(self.sim.t.yearvec[ti - 1])) == year:
            return
        age = self.sim.people.age
        n_children = int(len(((age >= 0.0) & (age < 5.0)).uids))
        zd = zerodose_fraction_under5(self.sim)
        self.rows.append(
            dict(
                calendar_year=year,
                zerodose_under5_fraction=float(zd),
                n_children_under5=n_children,
                n_zero_dose_under5=int(np.round(zd * n_children)) if n_children else 0,
            )
        )
        return


def align_rows(rows_ref, rows_int):
    """ Return shared calendar years and per-year dicts for both scenarios. """
    ref = {int(r["calendar_year"]): r for r in rows_ref}
    intr = {int(r["calendar_year"]): r for r in rows_int}
    years = sorted(set(ref) & set(intr))
    return years, ref, intr


def get_rows(sim):
    """ Yearly rows enriched with tetanus deaths. """
    rec = [a for a in sim.analyzers.values() if isinstance(a, YearlyRecorder)]
    if not rec:
        return []
    rec = rec[0]
    rows = [dict(r) for r in rec.rows]
    for row in rows:
        y = int(row["calendar_year"])
        row["tetanus_deaths"] = int(rec.tetanus_deaths_by_year.get(y, 0))
    return rows


def tetanus_metrics(sim):
    """ Total and per-calendar-year new tetanus infections from a finished sim. """
    tet = sim.diseases.get("tetanus")
    if tet is None:
        return dict(total=0.0, by_calendar_year={})
    new = np.asarray(tet.results.new_infections, dtype=float).ravel()
    yv = np.asarray(sim.t.yearvec, dtype=float).ravel()
    out = dict(total=float(np.sum(new)) if new.size else 0.0, by_calendar_year={})
    if new.size and new.size == yv.size:
        years = np.floor(yv).astype(int)
        for y in np.unique(years):
            out["by_calendar_year"][int(y)] = float(np.sum(new[years == y]))
    return out


def monthly_tetanus_data(df_data):
    """ Chronological (fractional_year, cases) arrays from the empirical table. """
    if df_data is None or "tetanus" not in df_data.columns:
        return np.array([]), np.array([])
    df = df_data.copy()
    if "month" in df.columns:
        df["_m"] = df["month"].map(MONTH_ORDER).fillna(0).astype(int)
    else:
        df["_m"] = 1
    df = df.sort_values(["year", "_m"]).reset_index(drop=True)
    years = pd.to_numeric(df["year"], errors="coerce").astype(float).values
    months = df["_m"].astype(float).values
    cases = pd.to_numeric(df["tetanus"], errors="coerce").astype(float).values
    t = years + (months - 0.5) / 12.0
    ok = np.isfinite(t) & np.isfinite(cases)
    return t[ok], cases[ok]


def model_monthly_tetanus(sim):
    """ Monthly tetanus new-infection counts from a finished sim. """
    tet = sim.diseases.get("tetanus")
    if tet is None:
        return np.array([]), np.array([])
    new_inf = np.asarray(tet.results.new_infections, dtype=float).ravel()
    yv = np.asarray(sim.t.yearvec, dtype=float).ravel()
    if not new_inf.size or new_inf.size != yv.size:
        return np.array([]), np.array([])
    start = float(np.floor(yv.min()))
    stop = float(np.ceil(yv.max()))
    edges = np.arange(start, stop + 1e-6, 1.0 / 12.0)
    if edges.size < 2:
        return np.array([]), np.array([])
    counts, _ = np.histogram(yv, bins=edges, weights=new_inf)
    centers = (edges[:-1] + edges[1:]) / 2.0
    return centers, counts


def load_calibration(path):
    """ Load calibrated parameter sets and metadata from JSON. """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return (
        data.get("calibration_metadata", {}),
        SimulationParameters.from_dict(data["reference_parameters"]),
        SimulationParameters.from_dict(data["scale_up_parameters"]),
    )
