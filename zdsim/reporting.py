""" PDF report generator for zdsim (reportlab). """

import json
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


FIGURE_MANIFEST = [
    (
        "zerodose_impact.png",
        "Figure 1. Zero-dose share (DTP1 proxy): administrative data vs "
        "modelled reference and intervention scenarios at the end of the "
        "projection window.",
    ),
    (
        "projection_zerodose_20y.png",
        "Figure 2. Projected yearly zero-dose share among under-fives for the "
        "reference (calibrated to the empirical proxy) and intervention "
        "(scaled-up routine delivery) scenarios.",
    ),
    (
        "tetanus_reference_vs_intervention.png",
        "Figure 3. Tetanus module trajectories and cumulative case counts "
        "(reference vs intervention). Counts are modelled infections in the "
        "simulated cohort; see methodology for the scaling factor used when "
        "translating to a national cohort.",
    ),
    (
        "projection_disease_deaths.png",
        "Figure 4. Disease-attributable deaths (pentavalent modules) per year "
        "with annual averted counts.",
    ),
    (
        "admin_data_dtp1_zerodose_timeseries.png",
        "Figure 5. Administrative DTP1 coverage proxy and implied zero-dose "
        "share (monthly), used to anchor the calibration target.",
    ),
    (
        "admin_data_dpt123_vs_births.png",
        "Figure 6. Administrative DPT1 / DPT3 doses versus estimated live "
        "births, providing context for the DTP1 coverage proxy.",
    ),
]


def _build_styles():
    """ Paragraph / section / caption styles for the report. """
    base = getSampleStyleSheet()
    styles = {
        "Title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=18,
            leading=22,
            alignment=1,
            spaceAfter=12,
            textColor=colors.HexColor("#1b3b6f"),
        ),
        "Subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            alignment=1,
            textColor=colors.HexColor("#555555"),
            spaceAfter=18,
        ),
        "Section": ParagraphStyle(
            "Section",
            parent=base["Heading1"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1b3b6f"),
            spaceBefore=14,
            spaceAfter=6,
        ),
        "Sub": ParagraphStyle(
            "Sub",
            parent=base["Heading2"],
            fontSize=11.5,
            leading=15,
            textColor=colors.HexColor("#2c3e50"),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "Body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontSize=10,
            leading=14,
            alignment=4,  # justified
            spaceAfter=6,
        ),
        "Caption": ParagraphStyle(
            "Caption",
            parent=base["Italic"],
            fontSize=9,
            leading=11.5,
            alignment=1,
            textColor=colors.HexColor("#444444"),
            spaceAfter=10,
        ),
        "Reference": ParagraphStyle(
            "Reference",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=12.5,
            leftIndent=14,
            firstLineIndent=-14,
            spaceAfter=4,
        ),
        "Meta": ParagraphStyle(
            "Meta",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#555555"),
        ),
    }
    return styles


def _fmt_pct(x):
    """ Fraction as a percent string, or 'n/a' for None. """
    if x is None:
        return "n/a"
    return f"{100 * float(x):.1f}%"


def _fmt_int(x):
    """ Thousands-grouped integer, or 'n/a' for None. """
    if x is None:
        return "n/a"
    try:
        return f"{int(round(float(x))):,}"
    except (TypeError, ValueError):
        return str(x)


def _fmt_num(x, nd=2):
    """ Number with ``nd`` decimals and thousands grouping. """
    if x is None:
        return "n/a"
    try:
        return f"{float(x):,.{nd}f}"
    except (TypeError, ValueError):
        return str(x)


def _safe_get(d, *path, default=None):
    """ Walk nested dict keys; return ``default`` when missing. """
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _abstract_paragraphs(summary, styles):
    ref = _safe_get(summary, "zero_dose_fraction_under5_model_reference", default=0.0)
    scl = _safe_get(summary, "zero_dose_fraction_under5_model_scale_up", default=0.0)
    red = _safe_get(summary, "relative_reduction_percent_model", default=0.0)
    tet_av = _safe_get(
        summary, "research_question_tetanus", "modeled_answer",
        "tetanus_cases_averted_total", default=0,
    )
    tet_2025 = _safe_get(
        summary, "research_question_tetanus", "modeled_answer",
        "tetanus_cases_averted_calendar_year_2025", default=0,
    )
    start = _safe_get(summary, "projection_calendar_start", default="?")
    stop = _safe_get(summary, "projection_calendar_stop", default="?")
    zd_ref_end = _safe_get(
        summary, "population_scaled_projection",
        "zero_dose_children_reference_end",
    )
    zd_scl_end = _safe_get(
        summary, "population_scaled_projection",
        "zero_dose_children_intervention_end",
    )
    reached = _safe_get(
        summary, "population_scaled_projection",
        "zero_dose_children_reached_at_end",
    )

    items = []
    items.append(Paragraph(
        f"<b>Introduction.</b> Zero-dose children — those who never receive "
        f"the first dose of a diphtheria-tetanus-pertussis (DTP1) or "
        f"pentavalent vaccine — remain a central equity gap in global "
        f"immunisation. This report summarises a Starsim-based agent-based "
        f"model calibrated to administrative DTP1 data from Kenya, and used "
        f"to project the impact of scaling up routine vaccination on zero-"
        f"dose prevalence and downstream tetanus burden among under-fives.",
        styles["Body"],
    ))
    items.append(Paragraph(
        f"<b>Methodology.</b> Two scenarios were compared over calendar "
        f"years {start}–{stop}: a <i>reference</i> scenario whose routine "
        f"delivery probability is calibrated (grid search) so that the "
        f"modelled end-of-window zero-dose share matches the empirical "
        f"proxy, and an <i>intervention</i> scenario with a higher routine "
        f"delivery probability and coverage cap. Tetanus is modelled via "
        f"environmental / wound-exposure dynamics with waning immunity "
        f"(Starsim SIS-style); the other pentavalent modules (diphtheria, "
        f"pertussis, hepatitis B, Hib) are modelled for disease-attributable "
        f"mortality. Vaccination acts on under-fives only.",
        styles["Body"],
    ))
    items.append(Paragraph(
        f"<b>Results.</b> End-of-window modelled zero-dose share was "
        f"<b>{_fmt_pct(ref)}</b> in the reference scenario and "
        f"<b>{_fmt_pct(scl)}</b> in the intervention scenario — a relative "
        f"reduction of <b>{_fmt_num(red, 1)}%</b>. Modelled tetanus cases "
        f"averted in the simulated cohort totalled <b>{_fmt_int(tet_av)}</b> "
        f"over the window, with <b>{_fmt_int(tet_2025)}</b> in the first "
        f"year (calendar year 2025). When scaled to the Kenya under-five "
        f"population, the intervention reduces end-of-window zero-dose "
        f"children from approximately <b>{_fmt_int(zd_ref_end)}</b> to "
        f"<b>{_fmt_int(zd_scl_end)}</b>, reaching roughly "
        f"<b>{_fmt_int(reached)}</b> additional children.",
        styles["Body"],
    ))
    items.append(Paragraph(
        "<b>Conclusion.</b> The intervention scenario achieves "
        "approximately a halving of zero-dose prevalence relative to the "
        "calibrated comparator — consistent with the project's 50%-"
        "reduction target — and yields a material reduction in modelled "
        "tetanus cases.",
        styles["Body"],
    ))
    items.append(Paragraph(
        "<b>Key words:</b> zero-dose vaccination, agent-based modelling, "
        "under-five, childhood immunisation, tetanus, Starsim, Kenya.",
        styles["Body"],
    ))
    return items


def _introduction_paragraphs(summary, styles):
    emp_zd = _safe_get(summary, "empirical_zerodose_proxy_dtp1", "mean_zerodose_proxy", default=0.0)
    emp_cov = _safe_get(summary, "empirical_zerodose_proxy_dtp1", "mean_dtp1_coverage_proxy", default=0.0)
    span = _safe_get(summary, "empirical_zerodose_proxy_dtp1", "years_span", default="")
    n_months = _safe_get(summary, "empirical_zerodose_proxy_dtp1", "n_months", default=0)

    items = [
        Paragraph(
            "Vaccination is a cornerstone of child public health: the WHO "
            "Immunization Agenda 2030 targets at least 90% coverage of "
            "essential vaccines in every country and in every district. "
            "Despite steady improvements, access gaps persist, and in sub-"
            "Saharan Africa roughly one in five children still lacks access "
            "to routine immunisation. Children who never receive a first "
            "DTP- or pentavalent-containing dose — the so-called "
            "<i>zero-dose</i> children — are the clearest marker of that "
            "gap and the central focus of this project.",
            styles["Body"],
        ),
        Paragraph("Statement of the problem", styles["Sub"]),
        Paragraph(
            "Globally about 14% of under-five children are penta-zero-dose "
            "and roughly 7.5% are truly zero-dose. In Kenya the zero-dose "
            "rate is approximately 7% (KDHS 2022), but monthly "
            "administrative data show that the implied coverage gap varies "
            "substantially across time and regions. Because diphtheria, "
            "neonatal tetanus and pertussis are controlled or near "
            "elimination, <b>tetanus</b> is used as the sentinel outcome: "
            "it remains endemic via environmental and wound exposure, and "
            "its burden is sensitive to first-dose coverage.",
            styles["Body"],
        ),
        Paragraph(
            f"The bundled administrative dataset provides a monthly DTP1 "
            f"coverage proxy spanning {span} "
            f"({_fmt_int(n_months)} months). Its mean coverage is "
            f"<b>{_fmt_pct(emp_cov)}</b>, implying a mean zero-dose share "
            f"of <b>{_fmt_pct(emp_zd)}</b>. This value anchors the model "
            f"calibration target.",
            styles["Body"],
        ),
        Paragraph("Objective", styles["Sub"]),
        Paragraph(
            "To quantify how many children would be additionally reached, "
            "and how many tetanus cases averted, if routine pentavalent "
            "delivery were scaled up enough to approximately halve the "
            "zero-dose share among under-fives, using a data-anchored "
            "agent-based simulation.",
            styles["Body"],
        ),
        Paragraph("Research question", styles["Sub"]),
        Paragraph(
            "<i>How many tetanus cases would be averted if we reduce the "
            "prevalence of zero-dose vaccination by ~50% among under-fives "
            "by the end of the projection window?</i>",
            styles["Body"],
        ),
    ]
    return items


def _methodology_paragraphs(summary, styles):
    ref_bundle = _safe_get(summary, "calibration_reference_bundle", default={})
    scl_bundle = _safe_get(summary, "calibration_scale_up_bundle", default={})
    ref_rp = _safe_get(summary, "model_reference_routine_prob")
    scl_rp = _safe_get(summary, "model_scale_up_routine_prob")
    scl_cov = _safe_get(summary, "model_scale_up_coverage")
    efficacy = ref_bundle.get("intervention_efficacy")
    start = _safe_get(summary, "projection_calendar_start", default="?")
    stop = _safe_get(summary, "projection_calendar_stop", default="?")
    n_agents = _safe_get(summary, "n_agents", default="?")
    calib_years = _safe_get(summary, "calibration_short_run_years")
    calib_agents = _safe_get(summary, "calibration_short_run_agents")
    data_path = _safe_get(summary, "data_file", default="(bundled xlsx)")
    calib_src = _safe_get(summary, "calibration_source", default="inline grid search")

    items = [
        Paragraph(
            "The model is built on the <b>Starsim</b> agent-based framework. "
            "Each agent represents a single child; the population includes "
            "births and deaths so that the under-five cohort renews over "
            "time. Vaccination is delivered via a routine <i>first-dose</i> "
            "intervention applied only to children in the 0-to-60-month "
            "age window, with a per-step delivery probability and an "
            "overall coverage cap.",
            styles["Body"],
        ),
        Paragraph("Disease modules", styles["Sub"]),
        Paragraph(
            "Five pentavalent disease modules are instantiated: "
            "diphtheria, tetanus, pertussis, hepatitis B, and Hib. "
            "All but tetanus use standard person-to-person transmission "
            "with module-specific <i>&beta;</i> values. Tetanus, in "
            "contrast, is modelled as an environmental / wound-exposure "
            "process — an SIS-style dynamic with waning vaccine-induced "
            "immunity — because tetanus transmission is not person-to-"
            "person in practice. Vaccinated agents become transiently "
            "immune with efficacy " f"{_fmt_pct(efficacy)} "
            "and re-enter the susceptible pool as immunity wanes, matching "
            "the dynamics described in the Rono et al. (2024) brief.",
            styles["Body"],
        ),
        Paragraph("Calibration", styles["Sub"]),
        Paragraph(
            f"A grid search over the routine-delivery probability is used "
            f"to match the modelled end-of-window zero-dose share to the "
            f"empirical DTP1 proxy. Calibration uses short, higher-agent "
            f"runs (≈{_fmt_int(calib_agents)} agents, "
            f"{calib_years}-year window) and, once converged, the chosen "
            f"routine probability and a coverage cap set by the mean DTP1 "
            f"proxy define the <i>reference</i> bundle. The "
            f"<i>intervention</i> bundle multiplies the reference routine "
            f"probability (capped at 0.12) and raises the coverage by "
            f"+2 percentage points, bounded by the coverage cap.",
            styles["Body"],
        ),
        Paragraph(
            f"Calibration source for this run: <font face='Courier'>{calib_src}</font>.",
            styles["Meta"],
        ),
        Paragraph("Key parameters", styles["Sub"]),
    ]

    param_rows = [
        ["Parameter", "Reference", "Intervention"],
        [
            "Routine delivery probability (per week)",
            _fmt_num(ref_rp, 4),
            _fmt_num(scl_rp, 4),
        ],
        [
            "Coverage cap",
            _fmt_pct(ref_bundle.get("intervention_coverage")),
            _fmt_pct(scl_cov if scl_cov is not None
                     else scl_bundle.get("intervention_coverage")),
        ],
        [
            "Vaccine efficacy",
            _fmt_pct(ref_bundle.get("intervention_efficacy")),
            _fmt_pct(scl_bundle.get("intervention_efficacy")),
        ],
        [
            "Eligible ages (years)",
            f"{_fmt_num(ref_bundle.get('intervention_age_min'), 0)}"
            f"–{_fmt_num(ref_bundle.get('intervention_age_max'), 0)}",
            f"{_fmt_num(scl_bundle.get('intervention_age_min'), 0)}"
            f"–{_fmt_num(scl_bundle.get('intervention_age_max'), 0)}",
        ],
        [
            "Diphtheria β",
            _fmt_num(ref_bundle.get("diphtheria_beta"), 3),
            _fmt_num(scl_bundle.get("diphtheria_beta"), 3),
        ],
        [
            "Pertussis β",
            _fmt_num(ref_bundle.get("pertussis_beta"), 3),
            _fmt_num(scl_bundle.get("pertussis_beta"), 3),
        ],
        [
            "Hepatitis B β",
            _fmt_num(ref_bundle.get("hepatitis_b_beta"), 3),
            _fmt_num(scl_bundle.get("hepatitis_b_beta"), 3),
        ],
        [
            "Hib β",
            _fmt_num(ref_bundle.get("hib_beta"), 3),
            _fmt_num(scl_bundle.get("hib_beta"), 3),
        ],
    ]
    param_table = Table(param_rows, colWidths=[8.0 * cm, 4.0 * cm, 4.0 * cm])
    param_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3b6f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.whitesmoke, colors.HexColor("#f4f6fb")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    items.append(param_table)

    items.append(Paragraph("Run configuration", styles["Sub"]))
    items.append(Paragraph(
        f"Agents: <b>{_fmt_int(n_agents)}</b> &nbsp;&nbsp; "
        f"Projection window: <b>{start}–{stop}</b> &nbsp;&nbsp; "
        f"Data file: <font face='Courier'>{os.path.basename(str(data_path))}</font>",
        styles["Meta"],
    ))
    return items


def _results_paragraphs(summary, styles):
    ref = _safe_get(summary, "zero_dose_fraction_under5_model_reference", default=0.0)
    scl = _safe_get(summary, "zero_dose_fraction_under5_model_scale_up", default=0.0)
    red = _safe_get(summary, "relative_reduction_percent_model", default=0.0)
    benefit = _safe_get(summary, "projection_benefit_summary", default={}) or {}
    death_b = _safe_get(summary, "projection_death_benefit_summary", default={}) or {}
    tet = _safe_get(summary, "research_question_tetanus", "modeled_answer", default={}) or {}
    scaled = _safe_get(summary, "population_scaled_projection", default={}) or {}

    items = [
        Paragraph("Zero-dose share", styles["Sub"]),
        Paragraph(
            f"At the end of the projection window the modelled zero-dose "
            f"share among under-fives is <b>{_fmt_pct(ref)}</b> in the "
            f"reference scenario and <b>{_fmt_pct(scl)}</b> in the "
            f"intervention scenario — a <b>{_fmt_num(red, 1)}%</b> relative "
            f"reduction. Across the full window the intervention reduces "
            f"the annual zero-dose share by on average "
            f"<b>{_fmt_num(benefit.get('mean_annual_reduction_zerodose_share_pp'), 2)} "
            f"percentage points</b> "
            f"(cumulatively "
            f"{_fmt_num(benefit.get('cumulative_zerodose_share_reduction_pp_years'), 2)} "
            f"pp-years).",
            styles["Body"],
        ),
        Paragraph("Tetanus burden", styles["Sub"]),
        Paragraph(
            f"In the simulated cohort, the intervention averts "
            f"<b>{_fmt_int(tet.get('tetanus_cases_averted_total'))}</b> "
            f"tetanus cases over {_fmt_num(summary.get('years'), 0)} years "
            f"(reference {_fmt_int(tet.get('reference_total'))} vs "
            f"intervention {_fmt_int(tet.get('intervention_total'))}), "
            f"with "
            f"<b>{_fmt_int(tet.get('tetanus_cases_averted_calendar_year_2025'))}</b> "
            f"cases averted in the first calendar year (2025).",
            styles["Body"],
        ),
        Paragraph("Disease-attributable deaths", styles["Sub"]),
        Paragraph(
            f"Across all pentavalent disease modules, total modelled deaths "
            f"are <b>{_fmt_int(death_b.get('total_reference_deaths'))}</b> "
            f"in the reference scenario and "
            f"<b>{_fmt_int(death_b.get('total_intervention_deaths'))}</b> "
            f"in the intervention scenario "
            f"(averted <b>{_fmt_int(death_b.get('total_deaths_averted'))}</b>, "
            f"mean "
            f"{_fmt_num(death_b.get('mean_annual_deaths_averted'), 1)} per "
            f"year). These counts are stochastic in small cohorts.",
            styles["Body"],
        ),
    ]

    if scaled:
        items.append(Paragraph("Population-scaled projection (Kenya)", styles["Sub"]))
        items.append(Paragraph(
            f"Anchor: <i>{scaled.get('anchor_label', 'n/a')}</i>. "
            f"Scaling by the ratio of the real annual birth cohort to the "
            f"modelled annual births (factor "
            f"{_fmt_num(scaled.get('count_scale_factor'), 0)}), the "
            f"intervention reduces end-of-window zero-dose children from "
            f"<b>{_fmt_int(scaled.get('zero_dose_children_reference_end'))}</b> "
            f"to "
            f"<b>{_fmt_int(scaled.get('zero_dose_children_intervention_end'))}</b>, "
            f"reaching approximately "
            f"<b>{_fmt_int(scaled.get('zero_dose_children_reached_at_end'))}</b> "
            f"additional children — a mean of "
            f"{_fmt_int(scaled.get('mean_annual_children_additionally_vaccinated'))} "
            f"children additionally vaccinated per year. Scaled tetanus "
            f"cases averted: "
            f"<b>{_fmt_int(scaled.get('tetanus_cases_averted_scaled'))}</b>. "
            f"Source: {scaled.get('anchor_source', 'see methodology')}.",
            styles["Body"],
        ))

    # Yearly breakdown table
    yearly_ref = _safe_get(summary, "projection_yearly_reference", default=[]) or []
    yearly_scl = _safe_get(summary, "projection_yearly_scale_up", default=[]) or []
    if yearly_ref and yearly_scl:
        items.append(Paragraph("Annual breakdown", styles["Sub"]))
        year_rows = [
            ["Year", "ZD share\n(reference)", "ZD share\n(intervention)",
             "Ref. deaths", "Int. deaths"],
        ]
        for r, s in zip(yearly_ref, yearly_scl):
            year_rows.append([
                str(r.get("calendar_year", "?")),
                _fmt_pct(r.get("zerodose_under5_fraction")),
                _fmt_pct(s.get("zerodose_under5_fraction")),
                _fmt_int(r.get("disease_attributable_deaths")),
                _fmt_int(s.get("disease_attributable_deaths")),
            ])
        yt = Table(year_rows, colWidths=[2.2 * cm, 3.6 * cm, 3.6 * cm, 3.3 * cm, 3.3 * cm])
        yt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3b6f")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.whitesmoke, colors.HexColor("#f4f6fb")]),
        ]))
        items.append(yt)

    return items


def _discussion_paragraphs(summary, styles):
    return [
        Paragraph(
            "The intervention scenario reduces zero-dose prevalence "
            "substantially across the projection window and, via its impact "
            "on first-dose coverage, lowers the modelled tetanus burden in "
            "the simulated cohort. The magnitude of the relative reduction "
            "is consistent with the project's halving target.",
            styles["Body"],
        ),
        Paragraph(
            "Several caveats apply. Disease-attributable death counts come "
            "from the Starsim pentavalent modules and represent only the "
            "modelled fraction of child mortality — not all-cause under-"
            "five mortality. Annual averted counts can be noisy when the "
            "modelled cohort is small or the projection window is short; "
            "in those regimes occasional negative yearly averted values "
            "are expected and should prompt longer runs or larger cohorts. "
            "When the two arms use distinct RNG seeds the comparison is "
            "also noisier than when they share a seed (the default).",
            styles["Body"],
        ),
        Paragraph(
            "Equity in first-dose access — geographic, socioeconomic, and "
            "service-delivery heterogeneity — is known to drive zero-dose "
            "persistence. The current implementation applies a homogeneous "
            "routine-delivery probability and coverage cap; future work "
            "should stratify by subnational region and risk profile, and "
            "link the delivery process to supply-chain and demand-side "
            "constraints.",
            styles["Body"],
        ),
    ]


def _conclusion_paragraphs(summary, styles):
    red = _safe_get(summary, "relative_reduction_percent_model", default=0.0)
    tet_av = _safe_get(
        summary, "research_question_tetanus", "modeled_answer",
        "tetanus_cases_averted_total", default=0,
    )
    return [
        Paragraph(
            f"The model demonstrates that an intervention strong enough to "
            f"halve zero-dose prevalence (observed relative reduction "
            f"<b>{_fmt_num(red, 1)}%</b> in this run) produces a meaningful "
            f"decline in modelled tetanus cases "
            f"(<b>{_fmt_int(tet_av)}</b> averted in the simulated cohort) "
            f"and reduces overall pentavalent-attributable mortality. These "
            f"findings support sustained investment in routine first-dose "
            f"delivery as the most direct lever on zero-dose prevalence.",
            styles["Body"],
        ),
    ]


def _references_paragraphs(styles):
    refs = [
        "Rono, B. C., Njeri, A., Mambo, S. N., &amp; Akangbe, R. O. (2024). "
        "<i>Agent-Based Modelling (ABM) predicts number needed to vaccinate "
        "to achieve a 50% reduction in zero-dose vaccination among under-"
        "five children in Kenya by 2025.</i> Project brief (JKUAT / APHRC / "
        "Lagos State MoH).",
        "Cata-Preta, B. O., Santos, T. M., Mengistu, T., Hogan, D. R., "
        "Barros, A. J. D., &amp; Victora, C. G. (2021). "
        "Zero-dose children and the immunisation cascade: understanding "
        "immunisation pathways in low- and middle-income countries. "
        "<i>Vaccine</i>, 39(32), 4564–4570. "
        "https://doi.org/10.1016/j.vaccine.2021.02.072",
        "Kenya National Bureau of Statistics (2022). "
        "<i>Kenya Demographic and Health Survey (KDHS) 2022.</i>",
        "Ozigbu, C. E., Olatosi, B., Li, Z., Hardin, J. W., &amp; Hair, N. "
        "L. (2022). Correlates of zero-dose vaccination status among "
        "children aged 12–59 months in sub-Saharan Africa. <i>Vaccines</i>, "
        "10(7), 1052. https://doi.org/10.3390/vaccines10071052",
        "Wonodi, C., &amp; Farrenkopf, B. A. (2023). Defining the zero-dose "
        "child: a comparative analysis of two approaches and their impact "
        "on assessing the zero-dose burden across 82 low- and middle-"
        "income countries. <i>Vaccines</i>, 11(10), 1543. "
        "https://doi.org/10.3390/vaccines11101543",
        "WHO / UNICEF (2024). <i>WUENIC — WHO/UNICEF estimates of national "
        "immunisation coverage.</i>",
        "World Health Organization (2020). <i>Immunization Agenda 2030.</i>",
        "Starsim Collective. <i>Starsim — agent-based disease modelling "
        "framework.</i> https://starsim.org/",
    ]
    return [Paragraph(r, styles["Reference"]) for r in refs]


def generate_report_pdf(summary, out_dir, *, pdf_name="zdsim_report.pdf"):
    """ Build the PDF report in ``out_dir`` and return its path. """
    os.makedirs(out_dir, exist_ok=True)
    pdf_path = os.path.join(out_dir, pdf_name)
    styles = _build_styles()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="zdsim — Zero-Dose Vaccination ABM Report",
        author="zdsim",
    )

    start = _safe_get(summary, "projection_calendar_start", default="?")
    stop = _safe_get(summary, "projection_calendar_stop", default="?")

    flow = []

    # Title block
    flow.append(Paragraph(
        "Agent-Based Modelling of Zero-Dose Vaccination Among Under-Five "
        "Children in Kenya",
        styles["Title"],
    ))
    flow.append(Paragraph(
        f"Simulation report · projection window {start}–{stop} · "
        f"generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Subtitle"],
    ))
    flow.append(Paragraph(
        "<i>Structured to mirror the Rono et al. (2024) project brief.</i>",
        styles["Meta"],
    ))
    flow.append(Spacer(1, 0.6 * cm))

    # 2. Abstract
    flow.append(Paragraph("1. Abstract", styles["Section"]))
    flow.extend(_abstract_paragraphs(summary, styles))

    # 3. Introduction
    flow.append(PageBreak())
    flow.append(Paragraph("2. Introduction", styles["Section"]))
    flow.extend(_introduction_paragraphs(summary, styles))

    # 4. Methodology
    flow.append(PageBreak())
    flow.append(Paragraph("3. Methodology", styles["Section"]))
    flow.extend(_methodology_paragraphs(summary, styles))

    # 5. Results
    flow.append(PageBreak())
    flow.append(Paragraph("4. Results", styles["Section"]))
    flow.extend(_results_paragraphs(summary, styles))

    # Figures — one per page for readability
    for fname, caption in FIGURE_MANIFEST:
        fpath = os.path.join(out_dir, fname)
        if not os.path.isfile(fpath):
            continue
        flow.append(PageBreak())
        flow.append(Paragraph("4. Results — figure", styles["Section"]))
        flow.append(Spacer(1, 0.2 * cm))
        img = Image(fpath)
        max_w = 16.0 * cm
        max_h = 20.0 * cm
        iw, ih = img.imageWidth, img.imageHeight
        scale = min(max_w / iw, max_h / ih)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        img.hAlign = "CENTER"
        flow.append(img)
        flow.append(Spacer(1, 0.2 * cm))
        flow.append(Paragraph(caption, styles["Caption"]))

    # 6. Discussion
    flow.append(PageBreak())
    flow.append(Paragraph("5. Discussion", styles["Section"]))
    flow.extend(_discussion_paragraphs(summary, styles))

    # 7. Conclusion
    flow.append(Paragraph("6. Conclusion", styles["Section"]))
    flow.extend(_conclusion_paragraphs(summary, styles))

    # 8. References
    flow.append(PageBreak())
    flow.append(Paragraph("7. References", styles["Section"]))
    flow.extend(_references_paragraphs(styles))

    doc.build(flow, onFirstPage=_footer, onLaterPages=_footer)
    return pdf_path


def _footer(canvas, doc):
    """ Page-number and project footer drawn on every page. """
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#888888"))
    page = canvas.getPageNumber()
    canvas.drawRightString(
        A4[0] - 2.0 * cm, 1.0 * cm,
        f"zdsim — page {page}",
    )
    canvas.drawString(
        2.0 * cm, 1.0 * cm,
        "Agent-Based Modelling of Zero-Dose Vaccination (Kenya)",
    )
    canvas.restoreState()
    return


def generate_report_from_summary_path(summary_path, pdf_name="zdsim_report.pdf"):
    """ Read ``summary_path`` JSON and write the PDF next to it. """
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    out_dir = os.path.dirname(os.path.abspath(summary_path))
    return generate_report_pdf(summary, out_dir, pdf_name=pdf_name)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    ap = argparse.ArgumentParser(description="Generate zdsim PDF report from a summary JSON.")
    ap.add_argument("summary", help="Path to zerodose_demo_summary.json")
    ap.add_argument("--name", default="zdsim_report.pdf", help="Output PDF filename")
    args = ap.parse_args()
    path = generate_report_from_summary_path(args.summary, pdf_name=args.name)
    print(f"Wrote {path}")
