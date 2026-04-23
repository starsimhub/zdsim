""" Figure generation for zdsim runs.

This module is strictly presentation: it takes finished simulations and
pre-computed result rows as inputs and writes PNGs to disk. The only
simulations it runs itself are the short historical scenarios needed for the
calibration before/after figures, which are tightly coupled to that plot and
therefore live here rather than in the main simulation pipeline.
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import starsim as ss

import zdsim as zds
from zdsim.analysis import (
    CONTEXT_DISEASES,
    MONTH_ORDER,
    align_rows,
    model_monthly_tetanus,
    monthly_tetanus_data,
)
from zdsim.zerodose_data import monthly_dtp1_coverage_and_zerodose


def _build_uncalibrated_sim(pars, *, n_agents, start, stop, age_pyramid):
    """ Historical tetanus-only sim with inflated wound rates (over-predicting fit). """
    b = pars
    people = ss.People(n_agents=n_agents, age_data=age_pyramid)
    tetanus = zds.Tetanus(
        dict(
            init_prev=ss.bernoulli(p=min(0.05, max(b.tetanus_init_p * 8.0, 0.01))),
            neonatal_wound_rate=ss.peryear(0.028),
            peri_neonatal_wound_rate=ss.peryear(0.053),
            childhood_wound_rate=ss.peryear(0.170),
            adult_wound_rate=ss.peryear(1.700),
        )
    )
    return ss.Sim(
        people=people,
        diseases=[tetanus],
        networks=[
            ss.RandomNet(dict(n_contacts=b.household_contacts, dur=0), name="household"),
            ss.RandomNet(dict(n_contacts=b.community_contacts, dur=0), name="community"),
        ],
        demographics=[ss.Pregnancy(fertility_rate=b.fertility_rate), ss.Deaths(dict(death_rate=b.death_rate))],
        interventions=None,
        pars=dict(start=start, stop=stop, dt=1 / 52, verbose=0, rand_seed=int(b.seed)),
    )


def _chronological_index(df):
    """ Integer month index sorted chronologically (year, month-name). """
    if "month" in df.columns:
        m = df["month"].map(MONTH_ORDER).fillna(0).astype(int)
    else:
        m = pd.Series(np.ones(len(df), dtype=int))
    years = pd.to_numeric(df["year"], errors="coerce").astype(float)
    tag = years * 100 + m.astype(float)
    return np.argsort(tag.values, kind="stable")


def _save_context_plot(df, out_dir):
    """ Monthly pneumonia / measles / tetanus case counts — descriptive only.

    Mirrors the "tables" in the Rono et al. (2024) Results section. Columns
    missing from the xlsx are skipped; the figure is skipped entirely if none
    of the context diseases are present.
    """
    available = [name for name in CONTEXT_DISEASES if name in df.columns]
    if not available:
        return None
    order = _chronological_index(df)
    years = pd.to_numeric(df["year"], errors="coerce").astype(float).values[order]
    path = os.path.join(out_dir, "admin_data_disease_context.png")
    fig, axes = plt.subplots(len(available), 1, figsize=(9, 2.4 * len(available)), sharex=True)
    if len(available) == 1:
        axes = [axes]
    colors = {"pneumonia": "#2980b9", "measles": "#8e44ad", "tetanus": "#c0392b"}
    for ax, name in zip(axes, available):
        y = pd.to_numeric(df[name], errors="coerce").astype(float).values[order]
        ax.plot(years, y, marker="o", markersize=3, linewidth=1.2, color=colors.get(name, "#333"))
        finite = y[np.isfinite(y)]
        if finite.size:
            ax.axhline(float(np.mean(finite)), color="k", linewidth=0.8, linestyle="--", alpha=0.5,
                       label=f"mean ≈ {np.mean(finite):,.0f}/month")
            ax.legend(loc="upper right", fontsize=8)
        ax.set_ylabel(f"{name.capitalize()}\ncases / month")
        ax.grid(alpha=0.3)
    axes[-1].set_xlabel("Calendar year")
    fig.suptitle("Monthly reported cases (Kenya HMIS) — descriptive context, not modelled",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def save_projection_plots(df_data, rows_base, rows_ref, rows_int, empirical_zd,
                          base_zd, ref_zd, int_zd, sim_base, sim_ref, sim_int, out_dir):
    """ Context + outcome plots for the reference/intervention projection. """
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

        # Descriptive context (Rono et al. 2024, Results): monthly pneumonia,
        # measles, and tetanus cases — observed, not modelled.
        p_ctx = _save_context_plot(df_data, out_dir)
        if p_ctx is not None:
            paths.append(p_ctx)

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

    years, ref, intr = align_rows(rows_ref, rows_int)
    base_by_year = {int(r["calendar_year"]): r for r in (rows_base or [])}
    if years:
        p4 = os.path.join(out_dir, "projection_zerodose_20y.png")
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(years, [ref[y]["zerodose_under5_fraction"] * 100 for y in years], "o-", label="baseline")
        ax.plot(years, [intr[y]["zerodose_under5_fraction"] * 100 for y in years], "s-", label="intervention")
        ax.set_ylabel("Zero-dose share (%)"); ax.set_xlabel("Calendar year"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p4, dpi=150); plt.close(fig); paths.append(p4)

        p5 = os.path.join(out_dir, "projection_tetanus_deaths.png")
        fig, ax = plt.subplots(figsize=(9, 4))
        if base_by_year:
            ax.plot(years, [base_by_year.get(y, {}).get("tetanus_deaths", np.nan) for y in years], "d--", color="#c0392b", label="no intervention")
        ax.plot(years, [ref[y]["tetanus_deaths"] for y in years], "o-", color="#7f8c8d", label="current program")
        ax.plot(years, [intr[y]["tetanus_deaths"] for y in years], "s-", color="#27ae60", label="intervention")
        ax.set_ylabel("Tetanus deaths"); ax.set_xlabel("Calendar year"); ax.legend(); ax.grid(alpha=0.3)
        fig.tight_layout(); fig.savefig(p5, dpi=150); plt.close(fig); paths.append(p5)

        if base_by_year:
            p5c = os.path.join(out_dir, "projection_cumulative_deaths_averted.png")
            base_yearly = np.array([base_by_year.get(y, {}).get("tetanus_deaths", 0) for y in years], dtype=float)
            ref_yearly = np.array([ref[y]["tetanus_deaths"] for y in years], dtype=float)
            int_yearly = np.array([intr[y]["tetanus_deaths"] for y in years], dtype=float)
            cum_ref = np.cumsum(base_yearly - ref_yearly)
            cum_int = np.cumsum(base_yearly - int_yearly)
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot(years, cum_ref, "o-", color="#7f8c8d", label="baseline")
            ax.plot(years, cum_int, "s-", color="#27ae60", label="intervention")
            ax.axhline(0, color="k", linewidth=0.6, alpha=0.5)
            ax.set_ylabel("Cumulative tetanus deaths averted"); ax.set_xlabel("Calendar year")
            ax.set_title("Cumulative tetanus deaths averted vs no intervention")
            ax.legend(); ax.grid(alpha=0.3)
            note = "Averted deaths (year t) = cumulative sum of [no intervention - scenario] from 2025 to t."
            fig.subplots_adjust(bottom=0.18)
            fig.text(
                0.01, 0.01, note,
                ha="left", va="bottom", fontsize=8, wrap=True,
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#f9f9f9", edgecolor="#cccccc", alpha=0.9),
            )
            fig.savefig(p5c, dpi=150); plt.close(fig); paths.append(p5c)

    p6 = os.path.join(out_dir, "tetanus_reference_vs_intervention.png")
    tb = np.asarray(sim_base.diseases["tetanus"].results.new_infections, dtype=float).ravel()
    tr = np.asarray(sim_ref.diseases["tetanus"].results.new_infections, dtype=float).ravel()
    ti = np.asarray(sim_int.diseases["tetanus"].results.new_infections, dtype=float).ravel()
    tv = np.asarray(sim_ref.t.yearvec, dtype=float).ravel()
    if tb.size and tb.size == tr.size == ti.size == tv.size:
        years_rt, base_year, ref_year = align_rows(rows_base, rows_ref)
        years_it, _, int_year = align_rows(rows_base, rows_int)
        years_u5 = [y for y in years_rt if y in years_it]
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=False)
        ax1.plot(tv, tb, label="baseline (no intervention)", color="#c0392b", alpha=0.85)
        ax1.plot(tv, tr, label="baseline", color="#7f8c8d", alpha=0.85)
        ax1.plot(tv, ti, label="intervention", color="#27ae60", alpha=0.85)
        ax1.set_ylabel("New tetanus infections (all ages)")
        ax1.set_title("Tetanus trajectories by scenario")
        ax1.legend()
        ax1.grid(alpha=0.3)

        if years_u5:
            ax2.plot(years_u5, [base_year[y]["zerodose_under5_fraction"] * 100 for y in years_u5],
                     "o-", color="#c0392b", label="baseline")
            ax2.plot(years_u5, [ref_year[y]["zerodose_under5_fraction"] * 100 for y in years_u5],
                     "o-", color="#7f8c8d", label="baseline")
            ax2.plot(years_u5, [int_year[y]["zerodose_under5_fraction"] * 100 for y in years_u5],
                     "o-", color="#27ae60", label="intervention")
            ax2.axhline(empirical_zd * 100, linestyle="--", linewidth=1, color="#2c3e50",
                        label="empirical proxy")
            ax2.set_ylabel("Zero-dose under-5 (%)")
            ax2.set_xlabel("Calendar year")
            ax2.set_title("Under-5 target metric (intervention signal)")
            ax2.legend()
            ax2.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(p6, dpi=150)
        plt.close(fig)
        paths.append(p6)
    return paths


def save_calibration_plots(df_data, ref_pars, base_pars, *, n_agents,
                           out_dir, build_simulation, age_pyramid):
    """ Tetanus fit before and after calibration, both on a common y-axis.

    Uses the provided ``build_simulation`` callable to run a calibrated
    baseline (no intervention) and a calibrated vaccine run; ``age_pyramid`` is
    reused for the uncalibrated (over-predicting) companion sim.
    """
    paths = []
    data_t, data_y = monthly_tetanus_data(df_data)
    if not data_t.size:
        return paths
    start_year = int(np.floor(data_t.min()))
    stop_year = int(np.ceil(data_t.max()))
    hist_n = max(4000, min(n_agents, 8000))

    pre_sim = _build_uncalibrated_sim(base_pars, n_agents=hist_n, start=start_year,
                                      stop=stop_year, age_pyramid=age_pyramid)
    base_sim = build_simulation(base_pars, n_agents=hist_n, start=start_year,
                                stop=stop_year, with_intervention=False)
    vac_sim = build_simulation(ref_pars, n_agents=hist_n, start=start_year,
                               stop=stop_year, with_intervention=True)
    pre_sim, base_sim, vac_sim = ss.multi_run([pre_sim, base_sim, vac_sim])
    t_pre, y_pre = model_monthly_tetanus(pre_sim)
    t_base, y_base = model_monthly_tetanus(base_sim)
    t_vac, y_vac = model_monthly_tetanus(vac_sim)

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
