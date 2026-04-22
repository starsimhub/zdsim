#!/usr/bin/env python3
""" Run reference vs scale-up scenarios and write zdsim outputs. """

import json
import os
import sys
from dataclasses import replace
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import starsim as ss

import zdsim as zds
from zdsim.reporting import generate_report_pdf
from zdsim.zerodose_calibration import SimulationParameterBundle, build_calibration_bundle, empirical_summary_from_dataframe, with_intervention_delivery
from zdsim.zerodose_data import default_formatted_xlsx_path, load_formatted_xlsx, monthly_dtp1_coverage_and_zerodose

CALIBRATION_SCHEMA_VERSION = "1"
DEFAULT_N_AGENTS = 20_000
DEFAULT_CALIBRATION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")
CALIB_YEARS = 8
CALIB_N_AGENTS = 10_000

KENYA_UNDER5_POPULATION = 7_200_000
KENYA_ANNUAL_LIVE_BIRTHS = 1_270_000
KENYA_ANCHOR_SOURCE = "UN WPP 2024; WHO/UNICEF WUENIC 2024 revision"


def zerodose_fraction_under5(sim):
    """ Prevalence of zero-dose (never-vaccinated) children under age 5.

    Uses the explicit ``zero_dose`` state on the ``ZeroDoseVaccination``
    module. When that module is not attached (true no-intervention baseline),
    every under-5 is zero-dose by definition.
    """
    # Exclude unborn fetuses (negative age) inserted by ss.Pregnancy.
    age = sim.people.age
    children = ((age >= 0.0) & (age < 5.0)).uids
    if len(children) == 0:
        return float("nan")
    for inv in sim.interventions.values():
        if isinstance(inv, zds.ZeroDoseVaccination):
            return float(np.mean(inv.zero_dose[children]))
    return 1.0


DISEASE_NAMES = ("diphtheria", "tetanus", "pertussis", "hepatitis_b", "hib")


def _deaths_this_step_by_disease(sim, ti):
    """ Count per-disease deaths on this timestep, de-duplicating agents across modules. """
    prev = -np.inf if ti <= 0 else float(ti - 1)
    per_disease = {name: 0 for name in DISEASE_NAMES}
    seen = set()
    for name in DISEASE_NAMES:
        dis = sim.diseases.get(name) if hasattr(sim.diseases, "get") else getattr(sim.diseases, name, None)
        if dis is None or not hasattr(dis, "ti_dead"):
            continue
        try:
            mask = (dis.ti_dead > prev) & (dis.ti_dead <= float(ti))
        except Exception:
            continue
        uids = np.asarray(mask.uids if hasattr(mask, "uids") else np.where(np.asarray(mask))[0])
        if uids.size == 0:
            continue
        novel = [int(u) for u in uids if int(u) not in seen]
        seen.update(novel)
        per_disease[name] += len(novel)
    return per_disease


class YearlyRecorder(ss.Analyzer):
    """ Record yearly zero-dose share and per-disease attributable deaths. """

    def __init__(self):
        super().__init__(name="zerodose_yearly")
        self.rows = []
        self.deaths_by_year = {}
        self.deaths_by_year_by_disease = {}
        return

    def step(self):
        """ Record one row at each year boundary. """
        ti = self.sim.ti
        year = int(np.floor(self.sim.t.yearvec[ti]))
        per_dis = _deaths_this_step_by_disease(self.sim, ti)
        step_total = sum(per_dis.values())
        self.deaths_by_year[year] = self.deaths_by_year.get(year, 0) + step_total
        ydict = self.deaths_by_year_by_disease.setdefault(year, {name: 0 for name in DISEASE_NAMES})
        for name, n in per_dis.items():
            ydict[name] += n
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


def _default_age_pyramid(max_age=80, growth_rate=0.022):
    """ Declining-pyramid age distribution typical of a growing LMIC population.

    Weight at age ``a`` is ``exp(-growth_rate * a)``; ``growth_rate`` ~0.022 gives
    a pyramid consistent with birth_rate ~25/1000 and death_rate ~8/1000.
    """
    ages = np.arange(0, max_age + 1)
    weights = np.exp(-growth_rate * ages)
    return pd.DataFrame({"age": ages, "value": weights})


def build_sim_from_bundle(bundle, *, n_agents, start, stop, record_yearly=False, with_intervention=True):
    """ Build one simulation from a parameter bundle. When with_intervention is False, no ZeroDoseVaccination module is added (true baseline). """
    people = ss.People(n_agents=n_agents, age_data=_default_age_pyramid())
    b = bundle
    interventions = None
    if with_intervention:
        interventions = [
            zds.ZeroDoseVaccination(
                dict(
                    start_day=0,
                    end_day=365 * int(stop - start),
                    coverage=b.intervention_coverage,
                    efficacy=b.intervention_efficacy,
                    age_min=b.intervention_age_min,
                    age_max=b.intervention_age_max,
                    routine_prob=b.intervention_routine_prob,
                    booster_age_max=b.intervention_booster_age_max,
                    booster_interval_years=b.intervention_booster_interval_years,
                )
            )
        ]
    sim = ss.Sim(
        people=people,
        diseases=[
            zds.Diphtheria(dict(beta=ss.peryear(b.diphtheria_beta), init_prev=ss.bernoulli(p=b.diphtheria_init_p))),
            zds.Tetanus(dict(init_prev=ss.bernoulli(p=b.tetanus_init_p))),
            zds.Pertussis(dict(beta=ss.peryear(b.pertussis_beta), init_prev=ss.bernoulli(p=b.pertussis_init_p))),
            zds.HepatitisB(dict(beta=ss.peryear(b.hepatitis_b_beta), init_prev=ss.bernoulli(p=b.hepatitis_b_init_p))),
            zds.Hib(dict(beta=ss.peryear(b.hib_beta), init_prev=ss.bernoulli(p=b.hib_init_p))),
        ],
        networks=[
            ss.RandomNet(dict(n_contacts=b.household_contacts, dur=0), name="household"),
            ss.RandomNet(dict(n_contacts=b.community_contacts, dur=0), name="community"),
        ],
        demographics=[ss.Pregnancy(fertility_rate=b.fertility_rate), ss.Deaths(dict(death_rate=b.death_rate))],
        interventions=interventions,
        analyzers=[YearlyRecorder()] if record_yearly else None,
        pars=dict(start=start, stop=stop, dt=1 / 52, verbose=0, rand_seed=int(b.seed)),
    )
    return sim


def grid_search_reference_routine(empirical_zd, base_bundle, *, n_agents, calib_years, start):
    """ Pick routine_prob that best matches empirical zero-dose target. """
    stop_short = int(start + calib_years)
    best_rp, best_zd, best_err = 0.03, float("nan"), np.inf
    for rp in np.linspace(0.018, 0.090, 14):
        sim = build_sim_from_bundle(
            with_intervention_delivery(base_bundle, routine_prob=float(rp)),
            n_agents=n_agents,
            start=start,
            stop=stop_short,
        )
        sim.run()
        zd = float(zerodose_fraction_under5(sim))
        err = abs(zd - empirical_zd)
        if err < best_err:
            best_rp, best_zd, best_err = float(rp), zd, err
    return best_rp, best_zd


def _align_rows(rows_ref, rows_int):
    """ Return shared years and per-year dicts for both scenarios. """
    ref = {int(r["calendar_year"]): r for r in rows_ref}
    intr = {int(r["calendar_year"]): r for r in rows_int}
    years = sorted(set(ref) & set(intr))
    return years, ref, intr


def _get_rows(sim):
    """ Yearly rows with disease-attributable deaths (total and per-disease) included. """
    rec = [a for a in sim.analyzers.values() if isinstance(a, YearlyRecorder)]
    if not rec:
        return []
    rec = rec[0]
    rows = [dict(r) for r in rec.rows]
    for row in rows:
        y = int(row["calendar_year"])
        row["disease_attributable_deaths"] = int(rec.deaths_by_year.get(y, 0))
        per = rec.deaths_by_year_by_disease.get(y, {})
        row["deaths_by_disease"] = {name: int(per.get(name, 0)) for name in DISEASE_NAMES}
    return rows


def _tetanus_metrics(sim):
    """ Total and yearly tetanus new infections. """
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


_MONTH_ORDER = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}


def _monthly_tetanus_data(df_data):
    """ Return (fractional_years, cases) sorted chronologically from the empirical table. """
    if df_data is None or "tetanus" not in df_data.columns:
        return np.array([]), np.array([])
    df = df_data.copy()
    if "month" in df.columns:
        df["_m"] = df["month"].map(_MONTH_ORDER).fillna(0).astype(int)
    else:
        df["_m"] = 1
    df = df.sort_values(["year", "_m"]).reset_index(drop=True)
    years = pd.to_numeric(df["year"], errors="coerce").astype(float).values
    months = df["_m"].astype(float).values
    cases = pd.to_numeric(df["tetanus"], errors="coerce").astype(float).values
    t = years + (months - 0.5) / 12.0
    ok = np.isfinite(t) & np.isfinite(cases)
    return t[ok], cases[ok]


def _model_monthly_tetanus(sim):
    """ Return (month_centers, monthly_cases_in_model_agents) for tetanus in ``sim``. """
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


def _build_uncalibrated_sim(bundle, *, n_agents, start, stop):
    """ Build a sim with inflated tetanus wound rates to mimic an uncalibrated (over-predicting) fit. """
    people = ss.People(n_agents=n_agents, age_data=_default_age_pyramid())
    b = bundle
    tetanus = zds.Tetanus(
        dict(
            init_prev=ss.bernoulli(p=min(0.05, max(b.tetanus_init_p * 8.0, 0.01))),
            neonatal_wound_rate=ss.peryear(0.028),
            peri_neonatal_wound_rate=ss.peryear(0.053),
            childhood_wound_rate=ss.peryear(0.170),
            adult_wound_rate=ss.peryear(1.700),
        )
    )
    sim = ss.Sim(
        people=people,
        diseases=[
            zds.Diphtheria(dict(beta=ss.peryear(b.diphtheria_beta), init_prev=ss.bernoulli(p=b.diphtheria_init_p))),
            tetanus,
            zds.Pertussis(dict(beta=ss.peryear(b.pertussis_beta), init_prev=ss.bernoulli(p=b.pertussis_init_p))),
            zds.HepatitisB(dict(beta=ss.peryear(b.hepatitis_b_beta), init_prev=ss.bernoulli(p=b.hepatitis_b_init_p))),
            zds.Hib(dict(beta=ss.peryear(b.hib_beta), init_prev=ss.bernoulli(p=b.hib_init_p))),
        ],
        networks=[
            ss.RandomNet(dict(n_contacts=b.household_contacts, dur=0), name="household"),
            ss.RandomNet(dict(n_contacts=b.community_contacts, dur=0), name="community"),
        ],
        demographics=[ss.Pregnancy(fertility_rate=b.fertility_rate), ss.Deaths(dict(death_rate=b.death_rate))],
        interventions=None,
        pars=dict(start=start, stop=stop, dt=1 / 52, verbose=0, rand_seed=int(b.seed)),
    )
    return sim


def _run_historical(bundle, *, n_agents, start_year, stop_year, with_intervention):
    """ Run a historical (calibration-window) sim and return (centers, monthly_cases). """
    sim = build_sim_from_bundle(
        bundle, n_agents=n_agents, start=start_year, stop=stop_year, with_intervention=with_intervention
    )
    sim.run()
    return _model_monthly_tetanus(sim)


def _run_historical_uncalibrated(bundle, *, n_agents, start_year, stop_year):
    """ Run an uncalibrated historical sim (inflated wound rates) and return (centers, monthly_cases). """
    sim = _build_uncalibrated_sim(bundle, n_agents=n_agents, start=start_year, stop=stop_year)
    sim.run()
    return _model_monthly_tetanus(sim)


def _save_calibration_plots(df_data, ref_bundle, base_bundle, *, n_agents, out_dir):
    """ Write before/after calibration tetanus figures that overlay data and model lines.

    Model counts are rescaled by a single factor chosen so the calibrated baseline
    matches the empirical monthly mean: this puts data, baseline, vaccine, and
    uncalibrated curves on a common axis and isolates the calibration effect.
    """
    paths = []
    data_t, data_y = _monthly_tetanus_data(df_data)
    if not data_t.size:
        return paths
    start_year = int(np.floor(data_t.min()))
    stop_year = int(np.ceil(data_t.max()))
    hist_n = max(4000, min(n_agents, 8000))

    t_pre, y_pre = _run_historical_uncalibrated(base_bundle, n_agents=hist_n, start_year=start_year, stop_year=stop_year)
    t_base, y_base = _run_historical(base_bundle, n_agents=hist_n, start_year=start_year, stop_year=stop_year, with_intervention=False)
    t_vac, y_vac = _run_historical(ref_bundle, n_agents=hist_n, start_year=start_year, stop_year=stop_year, with_intervention=True)

    data_mean = float(np.nanmean(data_y)) if data_y.size else 0.0
    base_mean = float(np.nanmean(y_base)) if y_base.size else 0.0
    scale = (data_mean / base_mean) if (data_mean > 0 and base_mean > 0) else 1.0
    y_pre = y_pre * scale
    y_base = y_base * scale
    y_vac = y_vac * scale

    y_top = float(max(np.nanmax(data_y) if data_y.size else 0.0,
                      np.nanmax(y_pre) if y_pre.size else 0.0,
                      np.nanmax(y_base) if y_base.size else 0.0,
                      np.nanmax(y_vac) if y_vac.size else 0.0))
    y_top = y_top * 1.08 if y_top > 0 else 1.0

    p_before = os.path.join(out_dir, "calibration_before.png")
    fig, ax = plt.subplots(figsize=(9, 4))
    if t_pre.size: ax.plot(t_pre, y_pre, color="#2980b9", label="Model", linewidth=1.5)
    ax.plot(data_t, data_y, "o-", color="black", markersize=3, linewidth=1.2, label="Data")
    ax.set_title("Model before calibration", fontweight="bold", loc="left")
    ax.set_ylabel("Monthly tetanus cases"); ax.set_xlabel("Year")
    ax.grid(alpha=0.3); ax.legend()
    ax.set_ylim(0, y_top)
    fig.tight_layout(); fig.savefig(p_before, dpi=150); plt.close(fig); paths.append(p_before)

    p_after = os.path.join(out_dir, "calibration_after.png")
    fig, ax = plt.subplots(figsize=(9, 4))
    if t_base.size: ax.plot(t_base, y_base, color="#2980b9", label="Baseline", linewidth=1.5)
    if t_vac.size: ax.plot(t_vac, y_vac, color="#e67e22", label="Vaccine", linewidth=1.5)
    ax.plot(data_t, data_y, "o-", color="black", markersize=3, linewidth=1.2, label="Data")
    ax.set_title("Model after calibration", fontweight="bold", loc="left")
    ax.set_ylabel("Monthly tetanus cases"); ax.set_xlabel("Year")
    ax.grid(alpha=0.3); ax.legend()
    ax.set_ylim(0, y_top)
    fig.tight_layout(); fig.savefig(p_after, dpi=150); plt.close(fig); paths.append(p_after)
    return paths


def _save_plots(df_data, rows_base, rows_ref, rows_int, empirical_zd, base_zd, ref_zd, int_zd, sim_ref, sim_int, out_dir):
    """ Write simple context + outcome plots. """
    paths = []
    if df_data is not None:
        d = monthly_dtp1_coverage_and_zerodose(df_data)
        x = np.arange(len(d))
        p1 = os.path.join(out_dir, "admin_data_dtp1_zerodose_timeseries.png")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
        ax1.plot(x, d["dtp1_coverage_proxy"]); ax1.set_ylabel("DTP1 proxy"); ax1.grid(alpha=0.3)
        ax2.plot(x, d["zerodose_proxy"], color="#c0392b"); ax2.set_ylabel("Zero-dose proxy"); ax2.set_xlabel("Month index"); ax2.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p1, dpi=150); plt.close(fig); paths.append(p1)

        p2 = os.path.join(out_dir, "admin_data_dpt123_vs_births.png")
        fig, ax = plt.subplots(figsize=(9, 4))
        for col in ["dpt1", "dpt3", "estimated_lb"]:
            if col in df_data.columns:
                ax.plot(x, pd.to_numeric(df_data[col], errors="coerce").astype(float).values, label=col)
        ax.set_xlabel("Month index"); ax.set_ylabel("Counts"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p2, dpi=150); plt.close(fig); paths.append(p2)

    p3 = os.path.join(out_dir, "zerodose_impact.png")
    labels = ["empirical\n(DTP1 proxy)", "baseline\n(no intervention)", "reference\n(calibrated)", "scale-up\n(intervention)"]
    values = [empirical_zd * 100, base_zd * 100, ref_zd * 100, int_zd * 100]
    colors = ["#2c3e50", "#c0392b", "#7f8c8d", "#27ae60"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(labels, values, color=colors)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.0, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Zero-dose share among under-fives (%)")
    ax.set_title("Model validation: data vs baseline vs intervention")
    ax.set_ylim(0, max(values) * 1.15 + 2)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout(); fig.savefig(p3, dpi=150); plt.close(fig); paths.append(p3)

    years, ref, intr = _align_rows(rows_ref, rows_int)
    base_by_year = {int(r["calendar_year"]): r for r in (rows_base or [])}
    if years:
        p4 = os.path.join(out_dir, "projection_zerodose_20y.png")
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(years, [ref[y]["zerodose_under5_fraction"] * 100 for y in years], "o-", label="reference")
        ax.plot(years, [intr[y]["zerodose_under5_fraction"] * 100 for y in years], "s-", label="intervention")
        ax.set_ylabel("Zero-dose share (%)"); ax.set_xlabel("Calendar year"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p4, dpi=150); plt.close(fig); paths.append(p4)

        p5 = os.path.join(out_dir, "projection_disease_deaths.png")
        fig, ax = plt.subplots(figsize=(9, 4))
        if base_by_year:
            ax.plot(years, [base_by_year.get(y, {}).get("disease_attributable_deaths", np.nan) for y in years], "d--", color="#c0392b", label="no intervention")
        ax.plot(years, [ref[y]["disease_attributable_deaths"] for y in years], "o-", color="#7f8c8d", label="reference")
        ax.plot(years, [intr[y]["disease_attributable_deaths"] for y in years], "s-", color="#27ae60", label="intervention")
        ax.set_ylabel("Disease-attributable deaths"); ax.set_xlabel("Calendar year"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p5, dpi=150); plt.close(fig); paths.append(p5)

        if base_by_year:
            p5c = os.path.join(out_dir, "projection_cumulative_deaths_averted.png")
            base_yearly = np.array([base_by_year.get(y, {}).get("disease_attributable_deaths", 0) for y in years], dtype=float)
            ref_yearly = np.array([ref[y]["disease_attributable_deaths"] for y in years], dtype=float)
            int_yearly = np.array([intr[y]["disease_attributable_deaths"] for y in years], dtype=float)
            cum_ref = np.cumsum(base_yearly - ref_yearly)
            cum_int = np.cumsum(base_yearly - int_yearly)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot(years, cum_ref, "o-", color="#7f8c8d", label="reference vs no intervention")
            ax.plot(years, cum_int, "s-", color="#27ae60", label="intervention vs no intervention")
            ax.axhline(0, color="k", linewidth=0.6, alpha=0.5)
            ax.set_ylabel("Cumulative deaths averted"); ax.set_xlabel("Calendar year")
            ax.set_title("Cumulative disease-attributable deaths averted vs no intervention")
            ax.legend(); ax.grid(alpha=0.3)
            fig.tight_layout(); fig.savefig(p5c, dpi=150); plt.close(fig); paths.append(p5c)

        p5b = os.path.join(out_dir, "projection_deaths_by_disease.png")
        fig, axes = plt.subplots(2, 3, figsize=(13, 6.5), sharex=True)
        axes = axes.ravel()
        for i, name in enumerate(DISEASE_NAMES):
            ax = axes[i]
            if base_by_year:
                ax.plot(years, [base_by_year.get(y, {}).get("deaths_by_disease", {}).get(name, np.nan) for y in years], "d--", color="#c0392b", label="no intervention", alpha=0.9)
            ax.plot(years, [ref[y].get("deaths_by_disease", {}).get(name, 0) for y in years], "o-", color="#7f8c8d", label="reference", alpha=0.9)
            ax.plot(years, [intr[y].get("deaths_by_disease", {}).get(name, 0) for y in years], "s-", color="#27ae60", label="intervention", alpha=0.9)
            ax.set_title(name.replace("_", " "), fontweight="bold")
            ax.grid(alpha=0.3)
            if i % 3 == 0:
                ax.set_ylabel("Deaths")
            if i >= 3:
                ax.set_xlabel("Calendar year")
        axes[-1].axis("off")
        axes[0].legend(loc="upper right", fontsize=8)
        fig.suptitle("Deaths per disease: no intervention vs reference vs intervention", fontsize=11)
        fig.tight_layout(); fig.savefig(p5b, dpi=150); plt.close(fig); paths.append(p5b)

    p6 = os.path.join(out_dir, "tetanus_reference_vs_intervention.png")
    tr = np.asarray(sim_ref.diseases["tetanus"].results.new_infections, dtype=float).ravel()
    ti = np.asarray(sim_int.diseases["tetanus"].results.new_infections, dtype=float).ravel()
    tv = np.asarray(sim_ref.t.yearvec, dtype=float).ravel()
    if tr.size and tr.size == ti.size and tr.size == tv.size:
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(tv, tr, label="reference", alpha=0.8)
        ax.plot(tv, ti, label="intervention", alpha=0.8)
        ax.set_ylabel("New tetanus infections"); ax.set_xlabel("Calendar year"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p6, dpi=150); plt.close(fig); paths.append(p6)
    return paths


def _load_calibration(path):
    """ Load calibration bundles and metadata from JSON. """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return (
        data.get("calibration_metadata", {}),
        SimulationParameterBundle.from_dict(data["reference_bundle"]),
        SimulationParameterBundle.from_dict(data["scale_up_bundle"]),
    )


def run_demo(*, n_agents, start, stop, seed, seed_intervention, out_dir, data_path,
             scale_routine_factor, scale_coverage_cap, population, calibration_file=None,
             save_calibration=None):
    """ Run the full workflow and return the summary dict. """
    os.makedirs(out_dir, exist_ok=True)
    empirical = None
    empirical_zd = 0.165
    data_file = None
    df = None
    if data_path is not None:
        df = load_formatted_xlsx(data_path)
        empirical = empirical_summary_from_dataframe(df)
        empirical_zd = float(empirical["mean_zerodose_proxy"])
        data_file = os.path.abspath(data_path)
        print(f"Data {data_file}: mean zero-dose proxy {empirical_zd:.1%}.")
    else:
        print(f"No data file; using fallback zero-dose target {empirical_zd:.1%}.")

    base = build_calibration_bundle(seed=seed, df=df, population=population, empirical=empirical)
    calibration_source = "inline grid search"
    if calibration_file and os.path.isfile(calibration_file):
        meta, ref_bundle, int_bundle = _load_calibration(calibration_file)
        calibration_source = f"loaded: {os.path.abspath(calibration_file)}"
        print(f"Loaded calibration from {calibration_file}.")
    else:
        print(f"Grid search: {CALIB_YEARS}y, {CALIB_N_AGENTS} agents, coverage={base.intervention_coverage:.4f}...")
        rp, zd_model = grid_search_reference_routine(
            empirical_zd,
            base,
            n_agents=CALIB_N_AGENTS,
            calib_years=CALIB_YEARS,
            start=start,
        )
        ref_bundle = with_intervention_delivery(base, routine_prob=rp)
        int_rp = min(0.12, rp * float(scale_routine_factor))
        int_cov = float(min(scale_coverage_cap, max(ref_bundle.intervention_coverage + 0.02, 0.85)))
        int_bundle = with_intervention_delivery(base, routine_prob=int_rp, coverage=int_cov)
        meta = dict(
            data_file=data_file,
            n_agents_calib=CALIB_N_AGENTS,
            calib_years=CALIB_YEARS,
            projection_start=int(start),
            seed=int(seed),
            scale_routine_factor=float(scale_routine_factor),
            scale_coverage_cap=float(scale_coverage_cap),
            empirical_zerodose_proxy=float(empirical_zd),
            calibrated_routine_prob=float(rp),
            calibrated_model_zd=float(zd_model),
            scale_up_routine_prob=float(int_rp),
            scale_up_coverage=float(int_cov),
        )
        print(f"Calibrated routine_prob={rp:.6f} (model ZD={zd_model:.1%}, target={empirical_zd:.1%}).")
        if save_calibration:
            payload = dict(
                schema_version=CALIBRATION_SCHEMA_VERSION,
                created_at=datetime.now(timezone.utc).isoformat(),
                calibration_metadata=meta,
                empirical=empirical,
                reference_bundle=ref_bundle.as_log_dict(),
                scale_up_bundle=int_bundle.as_log_dict(),
            )
            with open(save_calibration, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Saved calibration to {os.path.abspath(save_calibration)}.")

    int_seed = int(seed) if seed_intervention is None else int(seed_intervention)
    ref_bundle = replace(ref_bundle, seed=int(seed))
    int_bundle = replace(int_bundle, seed=int_seed)

    print(f"Projection window {start}-{stop}, seeds reference={seed} intervention={int_seed}.")
    sim_base = build_sim_from_bundle(ref_bundle, n_agents=n_agents, start=start, stop=stop, record_yearly=True, with_intervention=False); sim_base.run()
    sim_ref = build_sim_from_bundle(ref_bundle, n_agents=n_agents, start=start, stop=stop, record_yearly=True); sim_ref.run()
    sim_int = build_sim_from_bundle(int_bundle, n_agents=n_agents, start=start, stop=stop, record_yearly=True); sim_int.run()

    rows_base = _get_rows(sim_base)
    rows_ref, rows_int = _get_rows(sim_ref), _get_rows(sim_int)
    base_zd = float(zerodose_fraction_under5(sim_base))
    ref_zd, int_zd = float(zerodose_fraction_under5(sim_ref)), float(zerodose_fraction_under5(sim_int))
    rel = 100.0 * (ref_zd - int_zd) / ref_zd if ref_zd > 0 else float("nan")
    tet_ref, tet_int = _tetanus_metrics(sim_ref), _tetanus_metrics(sim_int)
    tet_av = float(tet_ref["total"] - tet_int["total"])

    years, ref_year, int_year = _align_rows(rows_ref, rows_int)
    if years:
        zd_gap = np.array([ref_year[y]["zerodose_under5_fraction"] - int_year[y]["zerodose_under5_fraction"] for y in years], dtype=float)
        d_ref = np.array([ref_year[y]["disease_attributable_deaths"] for y in years], dtype=float)
        d_int = np.array([int_year[y]["disease_attributable_deaths"] for y in years], dtype=float)
    else:
        zd_gap, d_ref, d_int = np.array([]), np.array([]), np.array([])
    death_av = float(np.sum(d_ref - d_int)) if years else 0.0
    model_births = n_agents * (float(ref_bundle.birth_rate) / 1000.0)
    scale = KENYA_ANNUAL_LIVE_BIRTHS / model_births if model_births > 0 else 1.0

    rq = []
    for y in sorted(set(tet_ref["by_calendar_year"]) | set(tet_int["by_calendar_year"])):
        r = float(tet_ref["by_calendar_year"].get(y, 0.0)); i = float(tet_int["by_calendar_year"].get(y, 0.0))
        rq.append(dict(calendar_year=int(y), reference_tetanus_cases=r, intervention_tetanus_cases=i, tetanus_cases_averted=r - i))

    summary = dict(
        schema_version=CALIBRATION_SCHEMA_VERSION,
        data_file=data_file,
        calibration_source=calibration_source,
        projection_calendar_start=int(start),
        projection_calendar_stop=int(stop),
        years=int(stop - start),
        n_agents=int(n_agents),
        calibration_short_run_years=meta.get("calib_years", CALIB_YEARS),
        calibration_short_run_agents=meta.get("n_agents_calib", CALIB_N_AGENTS),
        empirical_zerodose_proxy_dtp1=empirical,
        zero_dose_fraction_under5_empirical_proxy=float(empirical_zd),
        zero_dose_fraction_under5_model_baseline_no_intervention=base_zd,
        zero_dose_fraction_under5_model_reference=ref_zd,
        zero_dose_fraction_under5_model_scale_up=int_zd,
        relative_reduction_percent_model=float(rel),
        model_reference_routine_prob=float(ref_bundle.intervention_routine_prob),
        model_scale_up_routine_prob=float(int_bundle.intervention_routine_prob),
        model_scale_up_coverage=float(int_bundle.intervention_coverage),
        calibration_reference_bundle=ref_bundle.as_log_dict(),
        calibration_scale_up_bundle=int_bundle.as_log_dict(),
        projection_yearly_reference=rows_ref,
        projection_yearly_scale_up=rows_int,
        projection_benefit_summary=dict(
            projection_years=years,
            mean_annual_reduction_zerodose_share_pp=float(np.mean(zd_gap) * 100.0) if years else 0.0,
            cumulative_zerodose_share_reduction_pp_years=float(np.sum(zd_gap) * 100.0) if years else 0.0,
            sum_annual_zero_dose_children_gap=float(
                np.sum([ref_year[y]["n_zero_dose_under5"] - int_year[y]["n_zero_dose_under5"] for y in years])
            ) if years else 0.0,
        ),
        projection_death_benefit_summary=dict(
            projection_years=years,
            total_reference_deaths=float(np.sum(d_ref)) if years else 0.0,
            total_intervention_deaths=float(np.sum(d_int)) if years else 0.0,
            total_deaths_averted=death_av,
            mean_annual_deaths_averted=float(np.mean(d_ref - d_int)) if years else 0.0,
        ),
        research_question_tetanus=dict(
            question="How many tetanus cases will be averted if we reduce prevalence of zero-dose vaccination by 50% among under-fives by the year 2025?",
            modeled_answer=dict(
                metric="new_tetanus_infections_in_simulated_cohort",
                reference_total=float(tet_ref["total"]),
                intervention_total=float(tet_int["total"]),
                tetanus_cases_averted_total=tet_av,
                by_calendar_year=rq,
                modeled_zero_dose_relative_reduction_percent_end_window=float(rel),
            ),
        ),
        population_scaled_projection=dict(
            anchor_label="Kenya national 2024 anchors",
            anchor_source=KENYA_ANCHOR_SOURCE,
            count_scale_factor=float(scale),
            zero_dose_children_reference_end=int(round(ref_zd * KENYA_UNDER5_POPULATION)),
            zero_dose_children_intervention_end=int(round(int_zd * KENYA_UNDER5_POPULATION)),
            zero_dose_children_reached_at_end=int(round((ref_zd - int_zd) * KENYA_UNDER5_POPULATION)),
            mean_annual_children_additionally_vaccinated=int(round(((ref_zd - int_zd) * KENYA_UNDER5_POPULATION) / (len(years) or 1))),
            cumulative_child_years_zd_gap_closed=int(round(((ref_zd - int_zd) * KENYA_UNDER5_POPULATION) * (len(years) or 1))),
            total_disease_deaths_averted_scaled=int(round(death_av * scale)),
            mean_annual_disease_deaths_averted_scaled=int(round((death_av * scale) / (len(years) or 1))),
            tetanus_cases_averted_scaled=int(round(tet_av * scale)),
        ),
    )

    out_path = os.path.join(out_dir, "zerodose_demo_summary.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote {out_path}")
    for p in _save_plots(df, rows_base, rows_ref, rows_int, empirical_zd, base_zd, ref_zd, int_zd, sim_ref, sim_int, out_dir):
        print(f"Wrote {p}")
    try:
        for p in _save_calibration_plots(df, ref_bundle, base, n_agents=n_agents, out_dir=out_dir):
            print(f"Wrote {p}")
    except Exception as e:
        print(f"Calibration plots skipped: {e}")
    try:
        pdf = generate_report_pdf(summary, out_dir, pdf_name="zdsim_report.pdf")
        print(f"Wrote {pdf}")
    except Exception as e:
        print(f"PDF generation skipped: {e}")
    print(f"Tetanus cases: reference={tet_ref['total']:.0f}, intervention={tet_int['total']:.0f}, averted={tet_av:.0f}")
    print(f"Zero-dose under-5: empirical={empirical_zd:.1%}, baseline={base_zd:.1%}, reference={ref_zd:.1%}, intervention={int_zd:.1%} ({rel:.1f}% relative reduction).")
    return summary


def main():
    """ Set all run values here and execute. """
    n_agents = DEFAULT_N_AGENTS
    start = 2025
    stop = 2055
    seed = 42
    seed_intervention = None

    data_path = default_formatted_xlsx_path()
    use_data = True

    scale_routine_factor = 2.3
    scale_coverage_cap = 0.88
    population = None

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    calibration_file = DEFAULT_CALIBRATION_FILE if os.path.isfile(DEFAULT_CALIBRATION_FILE) else None
    save_calibration = None

    if not use_data:
        data_path = None
    elif data_path and not os.path.isfile(data_path):
        print(f"Data file not found: {data_path}.", file=sys.stderr)
        return 1

    if calibration_file:
        print(f"Using calibration file {calibration_file}.")

    run_demo(
        n_agents=int(n_agents),
        start=int(start),
        stop=int(stop),
        seed=int(seed),
        seed_intervention=seed_intervention,
        out_dir=out_dir,
        data_path=data_path,
        scale_routine_factor=float(scale_routine_factor),
        scale_coverage_cap=float(scale_coverage_cap),
        population=population,
        calibration_file=calibration_file,
        save_calibration=save_calibration,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
