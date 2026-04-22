#!/usr/bin/env python3
"""
Demonstrate how scaling up pentavalent-style vaccination reduces zero-dose
children, with empirical context from ``zerodose_data_formated.xlsx``.

Global context (WHO, not from this file):
  https://www.who.int/news-room/fact-sheets/detail/immunization-coverage
"""

import argparse
import json
import os
import sys
from dataclasses import replace

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import starsim as ss

import zdsim as zds
from zdsim.zerodose_calibration import (
    SimulationParameterBundle,
    build_calibration_bundle,
    empirical_summary_from_dataframe,
    with_intervention_delivery,
)
from zdsim.zerodose_data import (
    default_formatted_xlsx_path,
    load_formatted_xlsx,
    monthly_dtp1_coverage_and_zerodose,
)

CALIBRATION_SCHEMA_VERSION = "1"

WHO_IMMUNIZATION_COVERAGE_FS = (
    "https://www.who.int/news-room/fact-sheets/detail/immunization-coverage"
)

# Cohort size for full projection (rounded up from 15k to align with presentation-style runs)
DEFAULT_N_AGENTS = 20_000

# Default calibration file: auto-used when present so re-runs skip the grid-search.
# Override with --calibration-file or clear with --no-calibration-file.
DEFAULT_CALIBRATION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration.json")

# -------------------------------------------------------------------------
# Kenya national anchors (2024) used to scale model fractions to real counts.
# Exposed as module-level constants so downstream scripts can override them
# (e.g. to scale to a different country) without editing function bodies.
#
# Under-5 population  : UN World Population Prospects 2024
#                        https://population.un.org/wpp/
# Annual live births  : WHO/UNICEF WUENIC 2024 revision (released July 2025)
#                        https://www.who.int/teams/immunization-vaccines-and-biologicals/
#                        immunization-analysis-and-insights/global-monitoring/
#                        immunization-coverage/who-unicef-estimates-of-national-
#                        immunization-coverage
# -------------------------------------------------------------------------
KENYA_UNDER5_POPULATION = 7_200_000
KENYA_ANNUAL_LIVE_BIRTHS = 1_270_000
KENYA_ANCHOR_SOURCE = (
    "UN World Population Prospects 2024; "
    "WHO/UNICEF WUENIC 2024 revision (released July 2025)"
)


def _new_disease_deaths_this_step(sim, ti):
    """
    Count infection-module deaths that occur on this timestep index.

    Args:
        sim (ss.Sim): running simulation
        ti  (int):    timestep index; counts deaths with ti_dead in (ti-1, ti]

    Returns:
        total (int): number of disease-module deaths this step. Excludes
        demographic background mortality from ``ss.Deaths``.
    """
    prev = -np.inf if ti <= 0 else float(ti - 1)
    total = 0
    for dis in sim.diseases.values():
        if not hasattr(dis, "ti_dead"):
            continue
        td = dis.ti_dead
        try:
            mask = (td > prev) & (td <= float(ti))
        except Exception:
            continue
        if hasattr(mask, "uids"):
            total += len(mask.uids)
        else:
            total += int(np.count_nonzero(np.asarray(mask)))
    return int(total)


class YearlyZeroDoseRecorder(ss.Analyzer):
    """
    At each calendar year boundary (weekly dt), record zero-dose share among
    under-fives and approximate counts for projection / benefit summaries.
    """

    def __init__(self):
        super().__init__(name="zerodose_yearly")
        self.rows = []
        self._deaths_by_year = {}
        return

    def step(self):
        """ Record zero-dose share once per calendar year and per-step death tally. """
        sim   = self.sim
        ti    = sim.ti
        y     = int(np.floor(sim.t.yearvec[ti]))
        n_die = _new_disease_deaths_this_step(sim, ti)
        self._deaths_by_year[y] = self._deaths_by_year.get(y, 0) + n_die

        if ti > 0:
            y_prev = int(np.floor(sim.t.yearvec[ti - 1]))
            if y == y_prev:
                return

        zd_frac  = zerodose_fraction_under5(sim)
        children = _child_uids(sim.people)
        n_ch     = int(len(children))
        n_zd     = int(np.round(zd_frac * n_ch)) if n_ch else 0

        self.rows.append({
            "calendar_year":            y,
            "zerodose_under5_fraction": zd_frac,
            "n_children_under5":        n_ch,
            "n_zero_dose_under5":       n_zd,
        })
        return


def _child_uids(people, age_max_months=60.0):
    """ UIDs of agents under ``age_max_months`` months old. """
    age_months = people.age * 12.0
    mask       = age_months < age_max_months
    return mask.uids


def zerodose_fraction_under5(sim):
    """Share of under-fives with no modeled pentavalent dose."""
    children = _child_uids(sim.people)
    if len(children) == 0:
        return float("nan")

    invs = getattr(sim, "interventions", None)
    if not invs:
        return 1.0

    vacc = None
    for inv in invs.values():
        if isinstance(inv, zds.ZeroDoseVaccination):
            vacc = inv
            break
    if vacc is None:
        return 1.0

    unvacc = ~vacc.vaccinated[children]
    return float(np.mean(unvacc))


def build_sim_from_bundle(bundle, *, n_agents, start, stop, record_yearly=False):
    """
    Construct a Sim using only ``bundle`` fields. Resets RNG to ``bundle.seed``
    immediately before building so each run matches the calibrated draw.

    The initial population is restricted to children aged 0–5 years (uniform
    distribution across single-year age groups 0–4) so the simulation focuses
    on the pediatric cohort that is the target of the DTP/pentavalent programme.
    Births continuously replenish the under-5 population; the zero-dose share
    metric always measures the fraction of current under-5 agents unvaccinated.
    """
    sim_pars = dict(
        start=start,
        stop=stop,
        dt=1 / 52,
        verbose=0,
        rand_seed=int(bundle.seed),
    )

    # Uniform under-5 age distribution: equal weight for each single-year group 0–4.
    # ss.People uses this to sample initial ages; within each bin Starsim draws
    # uniformly so agents start between 0 and 5 years.
    under5_age_data = pd.DataFrame({"age": [0, 1, 2, 3, 4], "value": [1, 1, 1, 1, 1]})
    people = ss.People(n_agents=n_agents, age_data=under5_age_data)

    b = bundle
    diseases = [
        zds.Diphtheria(
            dict(beta=ss.peryear(b.diphtheria_beta), init_prev=ss.bernoulli(p=b.diphtheria_init_p))
        ),
        zds.Tetanus(
            dict(init_prev=ss.bernoulli(p=b.tetanus_init_p))
        ),
        zds.Pertussis(
            dict(beta=ss.peryear(b.pertussis_beta), init_prev=ss.bernoulli(p=b.pertussis_init_p))
        ),
        zds.HepatitisB(
            dict(
                beta=ss.peryear(b.hepatitis_b_beta),
                init_prev=ss.bernoulli(p=b.hepatitis_b_init_p),
            )
        ),
        zds.Hib(dict(beta=ss.peryear(b.hib_beta), init_prev=ss.bernoulli(p=b.hib_init_p))),
    ]

    networks = [
        ss.RandomNet(dict(n_contacts=b.household_contacts, dur=0), name="household"),
        ss.RandomNet(dict(n_contacts=b.community_contacts, dur=0), name="community"),
    ]

    demographics = [
        ss.Births(dict(birth_rate=b.birth_rate)),
        ss.Deaths(dict(death_rate=b.death_rate)),
    ]

    years = stop - start
    interventions = [
        zds.ZeroDoseVaccination(
            dict(
                start_day=0,
                end_day=365 * years,
                coverage=b.intervention_coverage,
                efficacy=b.intervention_efficacy,
                age_min=b.intervention_age_min,
                age_max=b.intervention_age_max,
                routine_prob=b.intervention_routine_prob,
            )
        )
    ]

    analyzers = [YearlyZeroDoseRecorder()] if record_yearly else None

    return ss.Sim(
        people=people,
        diseases=diseases,
        networks=networks,
        demographics=demographics,
        interventions=interventions,
        analyzers=analyzers,
        pars=sim_pars,
    )


def grid_search_reference_routine(empirical_zd, base_bundle, *, n_agents, calib_years, start):
    """
    Pick ``intervention_routine_prob`` so model ZD matches empirical target; holds
    all other bundle fields (including data-derived coverage) fixed.

    Reproducibility is handled by Starsim: the trial bundle propagates
    ``seed`` → ``ss.Sim(rand_seed=...)`` inside ``build_sim_from_bundle``.
    """
    stop_short = start + calib_years
    # routine_prob × coverage (coverage from data); search a bit wider on routine
    grid = np.linspace(0.018, 0.090, 14)
    best_rp = float(grid[len(grid) // 2])
    best_err = 1.0
    best_zd = 0.0

    for rp in grid:
        trial = with_intervention_delivery(base_bundle, routine_prob=float(rp))
        sim = build_sim_from_bundle(
            trial,
            n_agents=n_agents,
            start=start,
            stop=stop_short,
            record_yearly=False,
        )
        sim.run()
        zd = zerodose_fraction_under5(sim)
        err = abs(zd - empirical_zd)
        if err < best_err:
            best_err = err
            best_rp = float(rp)
            best_zd = zd

    return best_rp, best_zd


def _print_bundle(label, bundle):
    """ Pretty-print the key fields of ``bundle`` with a header label. """
    print(f"--- {label} (applied now) ---")
    print(
        f"  demographics: birth_rate={bundle.birth_rate:.4f}/1000/yr, "
        f"death_rate={bundle.death_rate:.4f}/1000/yr"
    )
    print(
        f"  intervention: routine_prob={bundle.intervention_routine_prob:.6f}, "
        f"coverage={bundle.intervention_coverage:.4f}, efficacy={bundle.intervention_efficacy:.4f}"
    )
    print(
        f"  networks: household={bundle.household_contacts}, "
        f"community={bundle.community_contacts}"
    )
    if bundle.data_derived:
        print(f"  data_derived: {bundle.data_derived}")
    print()
    return


def _save_administrative_timeseries_plots(df_monthly, out_dir):
    """ Monthly DTP1 coverage and zero-dose proxies from the xlsx (2-panel figure). """
    s     = monthly_dtp1_coverage_and_zerodose(df_monthly)
    paths = []

    x         = np.arange(len(s))
    labels    = s["period"].astype(str).tolist() if "period" in s.columns else [str(i) for i in x]
    tick_step = max(1, len(x) // 12)
    xticks    = x[::tick_step]

    fig, (ax_cov, ax_zd) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    cov_pct = s["dtp1_coverage_proxy"].to_numpy() * 100
    ax_cov.fill_between(x, 0, cov_pct, color="#aed6f1", alpha=0.6)
    ax_cov.plot(x, cov_pct, color="#2874a6", linewidth=1.2)
    ax_cov.axhline(
        float(np.nanmean(cov_pct)),
        color="#1b4f72",
        linestyle="--",
        linewidth=1,
        label=f"Mean {np.nanmean(cov_pct):.1f}%",
    )
    ax_cov.set_ylabel("DTP1 coverage proxy (%)")
    ax_cov.set_title("Administrative data: DTP1 vs monthly births (see zdsim/zerodose_data.py)")
    ax_cov.legend(loc="upper right", fontsize=8)
    ax_cov.set_ylim(0, min(105, max(50, np.nanmax(cov_pct) * 1.1)))

    zd_pct = s["zerodose_proxy"].to_numpy() * 100
    roll = (
        s["zerodose_proxy"]
        .rolling(window=12, min_periods=1)
        .mean()
        .to_numpy()
        * 100
    )
    ax_zd.plot(x, zd_pct, color="#95a5a6", linewidth=0.8, alpha=0.9, label="Monthly")
    ax_zd.plot(x, roll, color="#c0392b", linewidth=1.5, label="12-month rolling mean")
    ax_zd.axhline(
        float(np.nanmean(zd_pct)),
        color="#641e16",
        linestyle="--",
        linewidth=1,
        label=f"Mean {np.nanmean(zd_pct):.1f}%",
    )
    ax_zd.set_ylabel("Zero-dose proxy (%)")
    ax_zd.set_xlabel("Month (from data file)")
    ax_zd.legend(loc="upper right", fontsize=8)
    ax_zd.set_ylim(0, min(100, max(30, np.nanmax(zd_pct) * 1.15)))

    ax_zd.set_xticks(xticks)
    ax_zd.set_xticklabels([labels[i] for i in xticks], rotation=45, ha="right", fontsize=7)

    fig.tight_layout()
    p1 = os.path.join(out_dir, "admin_data_dtp1_zerodose_timeseries.png")
    fig.savefig(p1, dpi=150)
    plt.close(fig)
    paths.append(p1)

    # DPT1–3 dropout-style view (same monthly birth denominator)
    need = {"dpt1", "dpt2", "dpt3", "estimated_lb"}
    if need <= set(s.columns):
        lb = pd.to_numeric(s["estimated_lb"], errors="coerce").astype(float)
        mb = lb / 12.0
        fig2, ax = plt.subplots(figsize=(11, 4))
        for col, clr, lab in (
            ("dpt1", "#2874a6", "DPT1"),
            ("dpt2", "#1e8449", "DPT2"),
            ("dpt3", "#117a65", "DPT3"),
        ):
            d = pd.to_numeric(s[col], errors="coerce").astype(float)
            r = np.where(mb > 0, np.clip(d / mb, 0, 1.5), np.nan) * 100
            ax.plot(x, r, label=lab, color=clr, linewidth=1.0, alpha=0.85)
        ax.set_ylabel("Doses / monthly births (%) [capped display 150%]")
        ax.set_title("Administrative data: DPT doses relative to estimated monthly births")
        ax.set_ylim(0, 150)
        ax.legend(loc="upper right", fontsize=8)
        ax.set_xticks(xticks)
        ax.set_xticklabels([labels[i] for i in xticks], rotation=45, ha="right", fontsize=7)
        fig2.tight_layout()
        p2 = os.path.join(out_dir, "admin_data_dpt123_vs_births.png")
        fig2.savefig(p2, dpi=150)
        plt.close(fig2)
        paths.append(p2)

    return paths


def _align_yearly_rows(rows_sq, rows_sc):
    """ Align reference / intervention yearly rows by calendar_year. """
    d_sq  = {r["calendar_year"]: r for r in rows_sq}
    d_sc  = {r["calendar_year"]: r for r in rows_sc}
    years = sorted(set(d_sq) & set(d_sc))
    return years, d_sq, d_sc


def _attach_deaths_to_yearly_rows(sim):
    """ Mutate zerodose_yearly rows with disease_attributable_deaths tallies. """
    an = sim.analyzers.get("zerodose_yearly")
    if not an:
        return
    dby = getattr(an, "_deaths_by_year", {}) or {}
    for row in an.rows:
        cy = int(row["calendar_year"])
        row["disease_attributable_deaths"] = int(dby.get(cy, 0))
    return


def _tetanus_new_infection_metrics(sim):
    """
    Sum ``new_infections`` over the run from the tetanus disease module.

    Returns:
        metrics (dict): ``total`` and per-``by_calendar_year`` counts.
    """
    dis = sim.diseases.get("tetanus")
    if dis is None:
        return {"total": 0.0, "by_calendar_year": {}}
    ni = np.asarray(dis.results.new_infections, dtype=float).ravel()
    if ni.size == 0:
        return {"total": 0.0, "by_calendar_year": {}}
    yv = np.asarray(sim.t.yearvec, dtype=float).ravel()
    if yv.size != ni.size:
        return {
            "total":            float(np.sum(ni)),
            "by_calendar_year": {},
            "note":             "yearvec_length_mismatch",
        }
    cy      = np.floor(yv).astype(int)
    by_year = {}
    for y in np.unique(cy):
        by_year[int(y)] = float(ni[cy == y].sum())
    return {"total": float(np.sum(ni)), "by_calendar_year": by_year}


def _research_question_tetanus_json(ref, intv, *, modeled_zd_relative_reduction_percent):
    """ Package the Project 2-2A-7 tetanus / zero-dose research question answer from two runs. """
    rq = (
        "How many tetanus cases will be averted if we reduce prevalence of zero-dose "
        "vaccination by 50% among under-fives by the year 2025?"
    )
    per_year = []
    years = sorted(set(ref["by_calendar_year"]) | set(intv["by_calendar_year"]))
    for y in years:
        r = float(ref["by_calendar_year"].get(y, 0.0))
        i = float(intv["by_calendar_year"].get(y, 0.0))
        per_year.append(
            {
                "calendar_year": y,
                "reference_tetanus_cases": r,
                "intervention_tetanus_cases": i,
                "tetanus_cases_averted": r - i,
            }
        )
    modeled = {
        "metric": "new_tetanus_infections_in_simulated_cohort",
        "reference_total": ref["total"],
        "intervention_total": intv["total"],
        "tetanus_cases_averted_total": ref["total"] - intv["total"],
        "by_calendar_year": per_year,
        "modeled_zero_dose_relative_reduction_percent_end_window": modeled_zd_relative_reduction_percent,
    }
    if 2025 in years or 2025 in ref["by_calendar_year"] or 2025 in intv["by_calendar_year"]:
        r25 = float(ref["by_calendar_year"].get(2025, 0.0))
        i25 = float(intv["by_calendar_year"].get(2025, 0.0))
        modeled["tetanus_cases_averted_calendar_year_2025"] = r25 - i25
        modeled["reference_tetanus_cases_calendar_year_2025"] = r25
        modeled["intervention_tetanus_cases_calendar_year_2025"] = i25
    return {
        "question": rq,
        "modeled_answer": modeled,
        "interpretation": (
            "New tetanus infections are from the Starsim tetanus module (not national statistics). "
            "They depend on n_agents. By default both arms use the same RNG seed (fair counterfactual); "
            "if you pass --seed-intervention with a different value, arms are independent and averted counts "
            "can be noisy or negative. Modeled ZD reduction is in "
            "modeled_zero_dose_relative_reduction_percent_end_window (not fixed at 50%)."
        ),
    }


def _death_benefit_from_rows(rows_sq, rows_sc):
    """ Reference vs intervention disease-attributable deaths from pentavalent modules. """
    years, d_sq, d_sc = _align_yearly_rows(rows_sq, rows_sc)
    if not years:
        return {}

    b       = np.array([float(d_sq[y].get("disease_attributable_deaths", 0)) for y in years])
    i       = np.array([float(d_sc[y].get("disease_attributable_deaths", 0)) for y in years])
    averted = b - i

    return {
        "projection_years":           years,
        "total_reference_deaths":     float(np.sum(b)),
        "total_intervention_deaths":  float(np.sum(i)),
        "total_deaths_averted":       float(np.sum(averted)),
        "mean_annual_deaths_averted": float(np.mean(averted)) if len(years) else 0.0,
    }


def _yearly_deaths_comparison_list(rows_sq, rows_sc):
    """ Per-year reference/intervention deaths + averted counts. """
    years, d_sq, d_sc = _align_yearly_rows(rows_sq, rows_sc)
    out = []
    for y in years:
        b = int(d_sq[y].get("disease_attributable_deaths", 0))
        inv = int(d_sc[y].get("disease_attributable_deaths", 0))
        out.append(
            {
                "calendar_year": y,
                "reference_deaths": b,
                "intervention_deaths": inv,
                "deaths_averted": b - inv,
            }
        )
    return out


def _save_tetanus_comparison_figure(sim_ref, sim_int, out_path, *, n_agents):
    """
    Reference vs intervention tetanus panels.

    Panels: prevalence, cumulative cases, new cases over time, total new / averted bars.
    """
    try:
        tr = sim_ref.diseases["tetanus"].results
        ti = sim_int.diseases["tetanus"].results
    except (KeyError, AttributeError):
        return
    tv = tr.timevec
    if tv is None or len(tv) < 2:
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"Tetanus: reference vs intervention (N = {n_agents:,} agents)",
        fontsize=14,
        fontweight="bold",
    )

    ax = axes[0, 0]
    ax.plot(tv, tr.prevalence, color="#7f8c8d", linewidth=2, label="Reference scenario")
    ax.plot(tv, ti.prevalence, color="#27ae60", linewidth=2, label="Intervention scenario")
    ax.set_title("Tetanus prevalence")
    ax.set_xlabel("Time")
    ax.set_ylabel("Prevalence")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    ax.plot(tv, tr.cum_infections, color="#7f8c8d", linewidth=2, label="Reference scenario")
    ax.plot(tv, ti.cum_infections, color="#27ae60", linewidth=2, label="Intervention scenario")
    ax.set_title("Cumulative tetanus cases")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative cases")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    ax.plot(
        tv,
        tr.new_infections,
        color="#7f8c8d",
        linewidth=1.2,
        alpha=0.9,
        label="Reference scenario",
    )
    ax.plot(
        tv,
        ti.new_infections,
        color="#27ae60",
        linewidth=1.2,
        alpha=0.9,
        label="Intervention scenario",
    )
    ax.set_title("New tetanus cases (per timestep)")
    ax.set_xlabel("Time")
    ax.set_ylabel("New cases")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    ref_new = float(np.sum(tr.new_infections))
    int_new = float(np.sum(ti.new_infections))
    averted = ref_new - int_new
    ax = axes[1, 1]
    bars = ax.bar(
        ["Reference\n(total new)",
         "Intervention\n(total new)",
         "Cases\naverted (ref − int)"],
        [ref_new, int_new, averted],
        color=["#7f8c8d", "#27ae60", "#1e8449"],
        edgecolor="black",
        linewidth=0.5,
    )
    ax.set_title("Tetanus case counts (full run)")
    ax.set_ylabel("Cases")
    ymax = max(ref_new, int_new, abs(averted), 1.0)
    for b in bars:
        h = b.get_height()
        ax.text(
            b.get_x() + b.get_width() / 2.0,
            h + 0.02 * ymax,
            f"{h:.0f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    ax.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return


def _save_deaths_projection_figure(rows_sq, rows_sc, out_path, *, projection_start, projection_stop):
    """ Write the modelled-deaths + averted 2-panel projection figure. """
    comp = _yearly_deaths_comparison_list(rows_sq, rows_sc)
    if len(comp) < 1:
        return
    years = [r["calendar_year"]       for r in comp]
    b     = [r["reference_deaths"]    for r in comp]
    inv   = [r["intervention_deaths"] for r in comp]
    av    = [r["deaths_averted"]      for r in comp]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
    ax1.plot(years, b, "o-", color="#7f8c8d", linewidth=2, label="Reference scenario")
    ax1.plot(years, inv, "s-", color="#27ae60", linewidth=2, label="Intervention scenario")
    ax1.set_ylabel("Disease-attributable deaths (sim)")
    ax1.set_title(
        f"Modeled deaths — pentavalent disease modules ({projection_start}–{projection_stop})"
    )
    ax1.legend(loc="upper right", fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2.bar(years, av, color="#1e8449", alpha=0.85, label="Averted vs reference")
    ax2.set_ylabel("Deaths averted (reference − intervention)")
    ax2.set_xlabel("Calendar year")
    ax2.axhline(0, color="#999", linewidth=0.8)
    ax2.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return


def _benefit_from_trajectories(rows_sq, rows_sc):
    """ Aggregate zero-dose share benefit from per-year reference/intervention rows. """
    years, d_sq, d_sc = _align_yearly_rows(rows_sq, rows_sc)
    if not years:
        return {}

    z_sq = np.array([d_sq[y]["zerodose_under5_fraction"] for y in years])
    z_sc = np.array([d_sc[y]["zerodose_under5_fraction"] for y in years])
    gap  = z_sq - z_sc

    # Approximate child-level gap (same model size; different runs share seed but trajectories differ)
    nzd_sq = np.array([d_sq[y]["n_zero_dose_under5"] for y in years], dtype=float)
    nzd_sc = np.array([d_sc[y]["n_zero_dose_under5"] for y in years], dtype=float)

    return {
        "projection_years":                              years,
        "mean_annual_reduction_zerodose_share_pp":       float(np.mean(gap) * 100),
        "cumulative_zerodose_share_reduction_pp_years": float(np.sum(gap) * 100),
        "sum_annual_zero_dose_children_gap":             float(np.sum(nzd_sq - nzd_sc)),
    }


def _population_scaled_projection(*, zd_reference, zd_intervention, benefit, death_benefit,
                                  tetanus_cases_averted, n_agents, birth_rate):
    """
    Scale modeled fractions to real-world child population counts.

    Anchors are Kenya national figures from official sources (verified April 2026):
      - Under-5 population:  7 200 000  (UN World Population Prospects 2024)
      - Annual live births:  1 270 000  (WHO/UNICEF WUENIC 2024 revision)

    Zero-dose share metrics scale exactly (fractions × real population).
    Disease counts (deaths, tetanus cases) are scaled by the ratio of real
    annual births to the model's implied annual births
    (n_agents × birth_rate / 1000).  This produces estimates that are
    order-of-magnitude correct; uncertainty from model stochasticity and
    population heterogeneity should be communicated alongside these numbers.
    """
    # Official Kenya population anchors live at module scope so researchers
    # can swap them for another country without editing this function.
    kenya_under5   = KENYA_UNDER5_POPULATION
    kenya_births   = KENYA_ANNUAL_LIVE_BIRTHS
    anchor_source  = KENYA_ANCHOR_SOURCE

    # Model implied annual births
    model_annual_births = n_agents * (birth_rate / 1000.0)
    count_scale = kenya_births / model_annual_births if model_annual_births > 0 else 1.0

    mean_pp = benefit.get("mean_annual_reduction_zerodose_share_pp", 0.0)
    n_proj_years = len(benefit.get("projection_years", [])) or 1

    total_deaths_averted = death_benefit.get("total_deaths_averted", 0.0)
    mean_annual_averted = death_benefit.get("mean_annual_deaths_averted", 0.0)

    return {
        "anchor_label": "Kenya national (official sources, 2024)",
        "anchor_under5_population": kenya_under5,
        "anchor_annual_live_births": kenya_births,
        "anchor_source": anchor_source,
        "count_scale_factor": round(count_scale, 1),
        "count_scale_note": (
            f"Disease counts scaled by real_annual_births / model_annual_births "
            f"({kenya_births:,} / {model_annual_births:,.0f}). "
            "Zero-dose shares apply to any population without rescaling."
        ),
        # Zero-dose absolute counts (fractions × real under-5 population)
        "zero_dose_children_reference_end":    int(round(kenya_under5 * zd_reference)),
        "zero_dose_children_intervention_end": int(round(kenya_under5 * zd_intervention)),
        "zero_dose_children_reached_at_end":   int(round(kenya_under5 * (zd_reference - zd_intervention))),
        # Annual vaccination gain (fraction reduction × annual births)
        "mean_annual_children_additionally_vaccinated": int(
            round(kenya_births * mean_pp / 100.0)
        ),
        # Cumulative child-years of zero-dose gap closed over projection window
        "cumulative_child_years_zd_gap_closed": int(
            round(kenya_births * n_proj_years * mean_pp / 100.0)
        ),
        # Disease deaths scaled by count_scale
        "total_disease_deaths_averted_scaled": int(round(total_deaths_averted * count_scale)),
        "mean_annual_disease_deaths_averted_scaled": int(round(mean_annual_averted * count_scale)),
        "tetanus_cases_averted_scaled": int(round(tetanus_cases_averted * count_scale)),
        "interpretation": (
            "Scaled estimates show the real-world order of magnitude for Kenya. "
            "Zero-dose fractions are model outputs; absolute counts apply those fractions "
            "to the Kenya under-5 population or annual birth cohort. "
            "Disease death estimates carry additional uncertainty from model structure "
            "and should be treated as illustrative, not as epidemiological projections."
        ),
    }


def _save_projection_figure(rows_sq, rows_sc, out_path, *, projection_start, projection_stop):
    """ Write the zero-dose share projection figure (reference vs intervention). """
    years, d_sq, d_sc = _align_yearly_rows(rows_sq, rows_sc)
    if len(years) < 2:
        return

    z_sq = np.array([d_sq[y]["zerodose_under5_fraction"] for y in years]) * 100
    z_sc = np.array([d_sc[y]["zerodose_under5_fraction"] for y in years]) * 100

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(years, z_sq, "o-", color="#7f8c8d", linewidth=2, label="Model: reference scenario")
    ax.plot(years, z_sc, "s-", color="#27ae60", linewidth=2, label="Model: intervention scenario")
    ax.fill_between(
        years, z_sc, z_sq, color="#27ae60", alpha=0.2, label="Gap (modeled benefit)"
    )
    ax.set_ylabel("Zero-dose share among under-fives (%)")
    ax.set_xlabel("Calendar year")
    ax.set_title(
        f"Projected zero-dose under-fives ({projection_start}–{projection_stop})"
    )
    ax.legend(loc="upper right", fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return


def run_demo(*, n_agents, start, stop, seed, seed_intervention, out_dir, data_path,
             scale_routine_factor, scale_coverage_cap, population,
             alignment_meta=None, calibration_file=None, save_calibration=None):
    """ End-to-end demo: (optionally calibrate), run reference + intervention, write outputs. """
    os.makedirs(out_dir, exist_ok=True)

    empirical      = None
    empirical_zd   = 0.165  # fallback when --no-data
    data_file_used = None
    df_data        = None

    print("WHO reference:", WHO_IMMUNIZATION_COVERAGE_FS)

    # ------------------------------------------------------------------
    # Branch A: load pre-computed calibration from file
    # ------------------------------------------------------------------
    if calibration_file and os.path.isfile(calibration_file):
        with open(calibration_file, encoding="utf-8") as _f:
            _cal = json.load(_f)
        reference_bundle = SimulationParameterBundle.from_dict(_cal["reference_bundle"])
        scale_up_bundle  = SimulationParameterBundle.from_dict(_cal["scale_up_bundle"])
        empirical        = _cal.get("empirical")
        _meta            = _cal.get("calibration_metadata", {})
        empirical_zd     = _meta.get("empirical_zerodose_proxy", 0.165)
        reference_rp     = _meta.get("calibrated_routine_prob", reference_bundle.intervention_routine_prob)
        calib_zd         = _meta.get("calibrated_model_zd", float("nan"))
        calib_years      = _meta.get("calib_years", 8)
        calib_agents     = _meta.get("n_agents_calib", 10_000)
        data_file_used   = _meta.get("data_file")
        print(f"Loaded calibration from {os.path.abspath(calibration_file)}")
        print(f"  routine_prob={reference_rp:.6f}, model ZD={calib_zd:.1%}, target={empirical_zd:.1%}")
        if empirical:
            print(
                f"  (original data: {data_file_used}, "
                f"mean ZD proxy={empirical_zd:.1%} ±{empirical.get('std_zerodose_proxy',0):.1%})"
            )
        print()
        # Load df_data for the admin timeseries plots if the data file is still reachable
        _src = data_path or data_file_used
        if _src and os.path.isfile(_src):
            df_data = load_formatted_xlsx(_src)

    # ------------------------------------------------------------------
    # Branch B: run calibration from scratch
    # ------------------------------------------------------------------
    else:
        if calibration_file:
            print(f"Note: calibration file not found ({calibration_file}), running calibration.\n")

        if data_path is not None:
            df_data = load_formatted_xlsx(data_path)
            empirical = empirical_summary_from_dataframe(df_data)
            empirical_zd = empirical["mean_zerodose_proxy"]
            data_file_used = os.path.abspath(data_path)
            print(
                f"Data ({data_file_used}): mean zero-dose proxy (DTP1) = "
                f"{empirical_zd:.1%} (±{empirical['std_zerodose_proxy']:.1%} across months)"
            )
        print()

        base_bundle = build_calibration_bundle(
            seed=seed,
            df=df_data,
            population=population,
            empirical=empirical,
        )

        calib_years  = min(8, stop - start)
        calib_agents = min(10_000, n_agents)

        print(
            f"Calibrating routine_prob to empirical target (short run ~{calib_years} y, "
            f"{calib_agents} agents; coverage from data = {base_bundle.intervention_coverage:.4f})..."
        )
        reference_rp, calib_zd = grid_search_reference_routine(
            empirical_zd,
            base_bundle,
            n_agents=calib_agents,
            calib_years=calib_years,
            start=start,
        )
        print(
            f"  Grid best routine_prob={reference_rp:.6f} "
            f"(short-run model ZD={calib_zd:.1%}, target={empirical_zd:.1%})\n"
        )

        reference_bundle = with_intervention_delivery(base_bundle, routine_prob=reference_rp)

        scale_rp = min(0.12, reference_rp * scale_routine_factor)
        scale_cov = float(
            min(scale_coverage_cap, max(reference_bundle.intervention_coverage + 0.02, 0.85))
        )
        scale_up_bundle = with_intervention_delivery(
            base_bundle, routine_prob=scale_rp, coverage=scale_cov
        )

        if save_calibration:
            _cal_out = {
                "schema_version": CALIBRATION_SCHEMA_VERSION,
                "created_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                "calibration_metadata": {
                    "data_file": data_file_used,
                    "n_agents_calib": calib_agents,
                    "calib_years": calib_years,
                    "projection_start": start,
                    "seed": seed,
                    "scale_routine_factor": scale_routine_factor,
                    "scale_coverage_cap": scale_coverage_cap,
                    "empirical_zerodose_proxy": empirical_zd,
                    "calibrated_routine_prob": reference_rp,
                    "calibrated_model_zd": calib_zd,
                    "scale_up_routine_prob": scale_rp,
                    "scale_up_coverage": scale_cov,
                },
                "empirical": empirical,
                "reference_bundle": reference_bundle.as_log_dict(),
                "scale_up_bundle":  scale_up_bundle.as_log_dict(),
            }
            os.makedirs(os.path.dirname(os.path.abspath(save_calibration)) or ".", exist_ok=True)
            with open(save_calibration, "w", encoding="utf-8") as _f:
                json.dump(_cal_out, _f, indent=2)
            print(f"Saved calibration to {save_calibration}\n")

    # Apply intervention seed (may differ from calibration seed)
    intervention_seed = int(seed_intervention) if seed_intervention is not None else int(seed)
    scale_up_bundle = replace(scale_up_bundle, seed=intervention_seed)

    print(
        f"Forward projection window: {start}–{stop} "
        f"({stop - start} years). Yearly trajectories: reference vs intervention scenarios.\n"
    )
    print(
        f"RNG seeds: reference={seed}, intervention={intervention_seed} "
        f"(matched by default for a fair counterfactual; use --seed-intervention K for independent draws).\n"
    )

    print("Running model — reference scenario (calibrated comparator)...")
    _print_bundle("Reference scenario bundle", reference_bundle)
    sim_status = build_sim_from_bundle(
        reference_bundle,
        n_agents=n_agents,
        start=start,
        stop=stop,
        record_yearly=True,
    )
    sim_status.run()
    _attach_deaths_to_yearly_rows(sim_status)
    zd_status = zerodose_fraction_under5(sim_status)
    rows_status = list(sim_status.analyzers["zerodose_yearly"].rows)

    print("Running model — vaccination scale-up (intervention)...")
    _print_bundle("Scale-up bundle", scale_up_bundle)
    sim_scale = build_sim_from_bundle(
        scale_up_bundle,
        n_agents=n_agents,
        start=start,
        stop=stop,
        record_yearly=True,
    )
    sim_scale.run()
    _attach_deaths_to_yearly_rows(sim_scale)
    zd_scale = zerodose_fraction_under5(sim_scale)
    rows_scale = list(sim_scale.analyzers["zerodose_yearly"].rows)

    reduction = (
        (zd_status - zd_scale) / zd_status * 100 if zd_status > 0 else 0.0
    )

    ref_tetanus = _tetanus_new_infection_metrics(sim_status)
    int_tetanus = _tetanus_new_infection_metrics(sim_scale)
    research_question_tetanus = _research_question_tetanus_json(
        ref_tetanus,
        int_tetanus,
        modeled_zd_relative_reduction_percent=reduction,
    )

    benefit = _benefit_from_trajectories(rows_status, rows_scale)
    death_benefit = _death_benefit_from_rows(rows_status, rows_scale)
    deaths_yearly = _yearly_deaths_comparison_list(rows_status, rows_scale)

    _ma = research_question_tetanus["modeled_answer"]
    print(
        "Research question — modeled tetanus cases averted (reference − intervention): "
        f"{_ma['tetanus_cases_averted_total']:.0f} "
        f"(new infections: reference {_ma['reference_total']:.0f}, "
        f"intervention {_ma['intervention_total']:.0f})"
    )
    if "tetanus_cases_averted_calendar_year_2025" in _ma:
        print(
            f"  Modeled tetanus cases averted in calendar year 2025: "
            f"{_ma['tetanus_cases_averted_calendar_year_2025']:.0f}"
        )
    print()

    scaled = _population_scaled_projection(
        zd_reference=zd_status,
        zd_intervention=zd_scale,
        benefit=benefit,
        death_benefit=death_benefit,
        tetanus_cases_averted=float(_ma.get("tetanus_cases_averted_total", 0)),
        n_agents=n_agents,
        birth_rate=reference_bundle.birth_rate,
    )
    print(
        "Population-scaled projection (Kenya national, official anchors):\n"
        f"  Zero-dose children in reference scenario (end):    {scaled['zero_dose_children_reference_end']:>10,}\n"
        f"  Zero-dose children in intervention (end):         {scaled['zero_dose_children_intervention_end']:>10,}\n"
        f"  Children reached (ZD gap at end of window):       {scaled['zero_dose_children_reached_at_end']:>10,}\n"
        f"  Mean annual children additionally vaccinated:     {scaled['mean_annual_children_additionally_vaccinated']:>10,}\n"
        f"  Cumulative child-years ZD gap closed ({stop-start} yr): {scaled['cumulative_child_years_zd_gap_closed']:>10,}\n"
        f"  Disease deaths averted (scaled, {stop-start} yr total): {scaled['total_disease_deaths_averted_scaled']:>10,}\n"
        f"  Mean annual disease deaths averted (scaled):      {scaled['mean_annual_disease_deaths_averted_scaled']:>10,}\n"
        f"  Tetanus cases averted (scaled, {stop-start} yr total):  {scaled['tetanus_cases_averted_scaled']:>10,}\n"
    )
    print()

    summary = {
        "data_file": data_file_used,
        "population_assumption": population,
        "calibration_source": os.path.abspath(calibration_file) if calibration_file and os.path.isfile(calibration_file) else "inline",
        "seed_reference": seed,
        "seed_intervention": intervention_seed,
        "empirical_zerodose_proxy_dtp1": empirical,
        "calibration_reference_bundle": reference_bundle.as_log_dict(),
        "calibration_scale_up_bundle": scale_up_bundle.as_log_dict(),
        "model_reference_routine_prob": reference_bundle.intervention_routine_prob,
        "model_scale_up_routine_prob": scale_up_bundle.intervention_routine_prob,
        "model_scale_up_coverage": scale_up_bundle.intervention_coverage,
        "zero_dose_fraction_under5_model_reference": zd_status,
        "zero_dose_fraction_under5_model_scale_up": zd_scale,
        "relative_reduction_percent_model": reduction,
        "projection_calendar_start": start,
        "projection_calendar_stop": stop,
        "projection_yearly_reference": rows_status,
        "projection_yearly_scale_up": rows_scale,
        "projection_benefit_summary": benefit,
        "projection_death_benefit_summary": death_benefit,
        "projection_yearly_deaths_comparison": deaths_yearly,
        "disease_deaths_note": (
            "Counts are deaths attributed to pentavalent disease modules in the simulation "
            "(diphtheria, tetanus, pertussis, hepatitis B, Hib), not all-cause mortality. "
            "Yearly totals are stochastic; with few agents or short runs, cumulative “averted” deaths "
            "can occasionally be negative—in that case prefer longer projections, larger n_agents, or multiple seeds."
        ),
        "n_agents": n_agents,
        "years": stop - start,
        "who_context_url": WHO_IMMUNIZATION_COVERAGE_FS,
        "calibration_short_run_years": calib_years,
        "calibration_short_run_agents": calib_agents,
        "research_question_tetanus": research_question_tetanus,
        "population_scaled_projection": scaled,
    }
    if alignment_meta:
        summary["methodology_alignment"] = alignment_meta

    out_json = os.path.join(out_dir, "zerodose_demo_summary.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Wrote {out_json}")

    fig, ax = plt.subplots(figsize=(7, 4))
    labels = [
        "Data\n(admin. proxy)",
        "Model\n(reference)",
        "Model\n(intervention)",
    ]
    vals = [empirical_zd * 100, zd_status * 100, zd_scale * 100]
    colors = ["#2980b9", "#7f8c8d", "#27ae60"]
    ax.bar(labels, vals, color=colors)
    ax.set_ylabel("Zero-dose share among under-fives (%)")
    ax.set_title("Zero-dose (DTP1 proxy): data vs modeled scenarios")
    ax.set_ylim(0, max(100, max(vals) * 1.15))
    fig.tight_layout()
    plot_path = os.path.join(out_dir, "zerodose_impact.png")
    fig.savefig(plot_path, dpi=150)
    plt.close(fig)
    print(f"Wrote {plot_path}")

    proj_png = os.path.join(out_dir, "projection_zerodose_20y.png")
    _save_projection_figure(
        rows_status,
        rows_scale,
        proj_png,
        projection_start=start,
        projection_stop=stop,
    )
    print(f"Wrote {proj_png}")

    deaths_png = os.path.join(out_dir, "projection_disease_deaths.png")
    _save_deaths_projection_figure(
        rows_status,
        rows_scale,
        deaths_png,
        projection_start=start,
        projection_stop=stop,
    )
    print(f"Wrote {deaths_png}")

    tetanus_png = os.path.join(out_dir, "tetanus_reference_vs_intervention.png")
    _save_tetanus_comparison_figure(
        sim_status,
        sim_scale,
        tetanus_png,
        n_agents=n_agents,
    )
    print(f"Wrote {tetanus_png}")

    if df_data is not None:
        extra = _save_administrative_timeseries_plots(df_data, out_dir)
        for p in extra:
            print(f"Wrote {p}")

    try:
        from zdsim.reporting import generate_report_pdf

        pdf_path = generate_report_pdf(summary, out_dir)
        print(f"Wrote {pdf_path}")
    except Exception as exc:
        print(
            f"Note: could not generate PDF report ({exc}). "
            "Install reportlab to enable: pip install reportlab",
            file=sys.stderr,
        )

    print("\n--- Summary ---")
    print(
        f"Model (end of window): reference ZD={zd_status:.1%} → intervention ZD={zd_scale:.1%} "
        f"({reduction:.1f}% relative reduction vs reference scenario)"
    )
    if benefit:
        print(
            f"Projected benefit over {start}–{stop}: mean annual gap "
            f"{benefit.get('mean_annual_reduction_zerodose_share_pp', 0):.2f} "
            "percentage points (zero-dose share, intervention vs reference)"
        )
    if death_benefit:
        print(
            f"Disease deaths (pentavalent modules, full run): reference "
            f"{death_benefit.get('total_reference_deaths', 0):.0f} vs intervention "
            f"{death_benefit.get('total_intervention_deaths', 0):.0f} "
            f"(averted {death_benefit.get('total_deaths_averted', 0):.0f})"
        )
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Zero-dose demonstration using bundled administrative xlsx"
    )
    p.add_argument(
        "--n-agents",
        type=int,
        default=DEFAULT_N_AGENTS,
        help=f"Population size (default: {DEFAULT_N_AGENTS} for both reference and intervention runs)",
    )
    p.add_argument(
        "--start",
        type=int,
        default=2025,
        help="First calendar year of projection (default: 2025, year after data in xlsx through 2024)",
    )
    p.add_argument(
        "--stop",
        type=int,
        default=2055,
        help="Last calendar year of projection (default: 2055 ≈ 30 years from 2025)",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for calibration grid search and reference scenario simulation",
    )
    p.add_argument(
        "--seed-intervention",
        type=int,
        default=None,
        help="Random seed for intervention scenario (default: same as --seed for matched comparison)",
    )
    p.add_argument(
        "--data",
        default=default_formatted_xlsx_path(),
        help="Path to zerodose_data_formated.xlsx (not the ~$ Excel lock file)",
    )
    p.add_argument(
        "--no-data",
        action="store_true",
        help="Do not load xlsx; use a default empirical target (~16.5%%)",
    )
    p.add_argument(
        "--scale-routine-factor",
        type=float,
        default=2.3,
        help="Intervention routine_prob = min(0.12, reference routine_prob × factor)",
    )
    p.add_argument(
        "--scale-coverage-cap",
        type=float,
        default=0.88,
        help="Coverage cap for scale-up scenario",
    )
    p.add_argument(
        "--population",
        type=float,
        default=None,
        help="Optional total population (with data: calibrates birth_rate from estimated_lb)",
    )
    p.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(__file__), "outputs"),
        help="Output directory",
    )
    p.add_argument(
        "--rono-2025-window",
        action="store_true",
        help="Use calendar years 2024–2025 for projection (Rono et al. 2024 brief policy horizon).",
    )
    p.add_argument(
        "--calibration-file",
        default=None,
        metavar="PATH",
        help=(
            f"Path to a calibration JSON produced by calibrate.py. "
            "When supplied (or when calibration.json exists in the repo root), "
            "skips the grid-search and loads pre-computed bundles. "
            "Falls back to inline calibration if the file is not found."
        ),
    )
    p.add_argument(
        "--no-calibration-file",
        action="store_true",
        help=(
            "Force inline re-calibration even when calibration.json is present. "
            "Use after changing the data file or calibration parameters."
        ),
    )
    p.add_argument(
        "--save-calibration",
        default=None,
        metavar="PATH",
        help=(
            "After running inline calibration, save the calibrated bundles to this JSON path "
            "(e.g. calibration.json). Ignored when --calibration-file is used."
        ),
    )
    args = p.parse_args(argv)

    # Auto-detect the default calibration file when --calibration-file is not given.
    # Use --no-calibration-file to force a fresh grid-search even when the file exists.
    calibration_file = args.calibration_file
    if not args.no_calibration_file and calibration_file is None:
        if os.path.isfile(DEFAULT_CALIBRATION_FILE):
            calibration_file = DEFAULT_CALIBRATION_FILE
            print(
                f"Found {DEFAULT_CALIBRATION_FILE} — skipping grid-search calibration.\n"
                "  To force re-calibration, run:  python run_simulation.py --no-calibration-file\n"
                "  To regenerate the file, run:   python calibrate.py\n"
            )

    data_path = None if args.no_data else args.data
    if data_path and not os.path.isfile(data_path):
        print(
            f"Warning: data file not found: {data_path}\n"
            f"Use --no-data or place zerodose_data_formated.xlsx in zdsim/data/.",
            file=sys.stderr,
        )
        return 1

    proj_start = int(args.start)
    proj_stop = int(args.stop)
    alignment_meta = None
    if args.rono_2025_window:
        proj_start, proj_stop = 2024, 2025
        alignment_meta = {
            "brief": "Rono et al. (2024), Project 2-2A-7 — zero-dose vaccination",
            "rono_2025_window": True,
            "calendar_start": proj_start,
            "calendar_stop": proj_stop,
            "full_documentation": "Readme.md — Mapping the Rono et al. (2024) brief to zdsim",
        }

    run_demo(
        n_agents=args.n_agents,
        start=proj_start,
        stop=proj_stop,
        seed=args.seed,
        seed_intervention=args.seed_intervention,
        out_dir=args.out,
        data_path=data_path,
        scale_routine_factor=args.scale_routine_factor,
        scale_coverage_cap=args.scale_coverage_cap,
        population=args.population,
        alignment_meta=alignment_meta,
        calibration_file=calibration_file,
        save_calibration=args.save_calibration,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
