/**
 * Zero-dose results viewer — loads summary JSON (see Readme).
 */
(function () {
  const $ = (sel) => document.querySelector(sel);

  /** Kenya health.go.ke–style chart colours (nav blue, grey reference, deeper blue intervention) */
  const COL = {
    data: "#5c9bd1",
    ref: "#6b7d7c",
    refFill: "rgba(107, 125, 124, 0.15)",
    int: "#0d47a1",
    intFill: "rgba(13, 71, 161, 0.12)",
    gapBar: "rgba(21, 101, 192, 0.55)",
    gapBorder: "#1565c0",
    countsRef: "rgba(107, 125, 124, 0.85)",
    countsInt: "rgba(13, 71, 161, 0.82)",
    deathsRefFill: "rgba(107, 125, 124, 0.12)",
    deathsIntFill: "rgba(13, 71, 161, 0.1)",
    avertedBar: "rgba(21, 101, 192, 0.65)",
    avertedBorder: "#0d47a1",
  };

  /** JSON field names (reference scenario = calibrated comparator); fall back for older summary files. */
  function refZdFraction(data) {
    const v = data.zero_dose_fraction_under5_model_reference;
    if (v != null) return v;
    return data.zero_dose_fraction_under5_model_status_quo;
  }
  function refCalibrationBundle(data) {
    return data.calibration_reference_bundle || data.calibration_status_quo_bundle;
  }
  function refYearlyReference(data) {
    return data.projection_yearly_reference || data.projection_yearly_status_quo;
  }
  function refRoutineProb(data) {
    const v = data.model_reference_routine_prob;
    if (v != null) return v;
    return data.model_status_quo_routine_prob;
  }
  function totalReferenceDeaths(dsum) {
    if (!dsum) return null;
    const v = dsum.total_reference_deaths;
    if (v != null) return v;
    return dsum.total_baseline_deaths;
  }

  /** Seeds: prefer top-level fields; fall back to bundles (older JSON). */
  function seedSummaryLine(data) {
    const br = refCalibrationBundle(data);
    const sr = data.seed_reference != null ? data.seed_reference : br && br.seed != null ? br.seed : null;
    const su = data.calibration_scale_up_bundle;
    const si =
      data.seed_intervention != null
        ? data.seed_intervention
        : su && su.seed != null
          ? su.seed
          : null;
    if (sr != null && si != null && Number(sr) !== Number(si)) {
      return String(sr) + " (reference) · " + String(si) + " (intervention)";
    }
    if (sr != null) return String(sr);
    return "—";
  }

  function pct(x) {
    if (x == null || Number.isNaN(x)) return "—";
    return (x * 100).toFixed(1) + "%";
  }

  function pp(x) {
    if (x == null || Number.isNaN(x)) return "—";
    return x.toFixed(2) + " pp";
  }

  function fmtEmpirical(emp) {
    if (!emp) return null;
    return {
      meanZd: emp.mean_zerodose_proxy,
      stdZd: emp.std_zerodose_proxy,
      meanCov: emp.mean_dtp1_coverage_proxy,
      nMonths: emp.n_months,
      yearsSpan: emp.years_span,
    };
  }

  /** Resolve fetch URLs for both /web/index.html and serving from /web/ only */
  function candidateDataUrls() {
    const here = window.location.href;
    const urls = [];
    try {
      urls.push(new URL("data/summary.json", here).href);
    } catch (_) {}
    try {
      urls.push(new URL("../outputs/zerodose_demo_summary.json", here).href);
    } catch (_) {}
    try {
      urls.push(new URL("/outputs/zerodose_demo_summary.json", here.origin).href);
    } catch (_) {}
    return [...new Set(urls)];
  }

  let barChart;
  let lineChart;
  let gapChart;
  let countsChart;
  let deathsLineChart;
  let deathsAvertedChart;

  function mergeYearlyRows(rowsSq, rowsSc) {
    const byY = {};
    (rowsSq || []).forEach(function (r) {
      byY[r.calendar_year] = {
        sqFrac: r.zerodose_under5_fraction,
        sqNzd: r.n_zero_dose_under5,
        nChild: r.n_children_under5,
      };
    });
    (rowsSc || []).forEach(function (r) {
      if (!byY[r.calendar_year]) {
        byY[r.calendar_year] = { nChild: r.n_children_under5 };
      }
      byY[r.calendar_year].scFrac = r.zerodose_under5_fraction;
      byY[r.calendar_year].scNzd = r.n_zero_dose_under5;
    });
    const years = Object.keys(byY)
      .map(Number)
      .sort(function (a, b) {
        return a - b;
      });
    return { byY, years };
  }

  function renderDom(data) {
    const emp = data.empirical_zerodose_proxy_dtp1;
    const e = fmtEmpirical(emp);
    const benefit = data.projection_benefit_summary || {};
    const zdSq = refZdFraction(data);
    const zdSc = data.zero_dose_fraction_under5_model_scale_up;
    const rel = data.relative_reduction_percent_model;
    const hasDeaths =
      Array.isArray(data.projection_yearly_deaths_comparison) &&
      data.projection_yearly_deaths_comparison.length > 0;

    const sub = $("#hero-sub");
    if (sub) {
      sub.textContent =
        "Simulation evidence for intervention · projection " +
        (data.projection_calendar_start || "—") +
        "–" +
        (data.projection_calendar_stop || "—") +
        " · " +
        (data.n_agents != null ? data.n_agents.toLocaleString() : "—") +
        " agents · seeds " +
        seedSummaryLine(data);
    }

    const arn = $("#alignment-run-note");
    if (arn) {
      const ma = data.methodology_alignment;
      if (ma && ma.rono_2025_window) {
        arn.hidden = false;
        arn.textContent =
          "This run used the Rono et al. (2024) policy horizon (" +
          (ma.calendar_start != null ? String(ma.calendar_start) : "—") +
          "–" +
          (ma.calendar_stop != null ? String(ma.calendar_stop) : "—") +
          "). Full methods note: section below (same article as Readme.md).";
      } else {
        arn.hidden = true;
        arn.textContent = "";
      }
    }

    const dt = $("#decision-text");
    if (dt) dt.innerHTML = buildDecisionHtml(data);
    const ml = $("#metrics-lead");
    if (ml) ml.innerHTML = buildMetricsLead(data);

    $("#exec-text").innerHTML = buildExecutiveHtml(data, e, zdSq, zdSc, rel, benefit, hasDeaths);

    const gapEndPp =
      zdSq != null && zdSc != null && !Number.isNaN(zdSq) && !Number.isNaN(zdSc)
        ? (zdSq - zdSc) * 100
        : null;
    const cg = $("#card-gap");
    if (cg) {
      cg.innerHTML =
        "<strong>" +
        (gapEndPp != null ? gapEndPp.toFixed(1) + " pp" : "—") +
        "</strong><span>Share-point gap at end (reference minus intervention)</span>";
    }

    $("#card-data").innerHTML = e
      ? "<strong>" + pct(e.meanZd) + "</strong><span>Admin. zero-dose proxy (data mean)</span>"
      : "<strong>—</strong><span>No admin. row (run with xlsx)</span>";
    $("#card-sq").innerHTML =
      "<strong>" + pct(zdSq) + "</strong><span>Reference scenario — end of window</span>";
    $("#card-su").innerHTML =
      "<strong>" + pct(zdSc) + "</strong><span>Intervention scenario — end of window</span>";

    const cb = $("#card-benefit");
    if (cb) {
      cb.innerHTML =
        "<strong>" +
        (benefit.mean_annual_reduction_zerodose_share_pp != null
          ? benefit.mean_annual_reduction_zerodose_share_pp.toFixed(2) + " pp/yr"
          : "—") +
        "</strong><span>Mean annual narrowing of zero-dose share (intervention benefit)</span>";
    }

    const dsum = data.projection_death_benefit_summary || {};
    const secDeaths = $("#metrics-deaths");
    if (secDeaths) secDeaths.hidden = !hasDeaths;
    const dblock = $("#deaths-charts-block");
    if (dblock) dblock.hidden = !hasDeaths;

    const dl = $("#deaths-lead");
    if (dl) {
      dl.textContent = hasDeaths
        ? data.disease_deaths_note ||
            "Deaths are attributed to pentavalent disease modules in the ABM (not all-cause mortality)."
        : "Re-run python run_simulation.py with an up-to-date Starsim build to populate disease death tallies.";
    }

    const cda = $("#card-deaths-averted");
    if (cda) {
      cda.innerHTML =
        "<strong>" +
        (dsum.total_deaths_averted != null ? Math.round(dsum.total_deaths_averted).toLocaleString() : "—") +
        "</strong><span>Total deaths averted vs reference (over projection, simulation)</span>";
    }
    const cdb = $("#card-deaths-reference");
    if (cdb) {
      cdb.innerHTML =
        "<strong>" +
        (totalReferenceDeaths(dsum) != null
          ? Math.round(totalReferenceDeaths(dsum)).toLocaleString()
          : "—") +
        "</strong><span>Total disease deaths — reference arm</span>";
    }
    const cdi = $("#card-deaths-intervention");
    if (cdi) {
      cdi.innerHTML =
        "<strong>" +
        (dsum.total_intervention_deaths != null
          ? Math.round(dsum.total_intervention_deaths).toLocaleString()
          : "—") +
        "</strong><span>Total disease deaths — intervention arm</span>";
    }

    const fd = $("#findings-deaths");
    if (fd) {
      fd.innerHTML = hasDeaths
        ? buildDeathsFindingsHtml(dsum, data)
        : "<p class='muted'>Disease death metrics appear after running <code>python run_simulation.py</code> (current version records pentavalent disease deaths by year).</p>";
    }

    const cnote = $("#chart-counts-note");
    if (cnote) {
      cnote.textContent =
        "Bars count modeled children under five with zero doses each year (simulation cohort). " +
        "Use for comparing scenarios and trend shape; national totals require scaling and different data.";
    }

    const cdnote = $("#chart-deaths-note");
    if (cdnote) {
      cdnote.textContent = hasDeaths
        ? (data.disease_deaths_note ||
            "") +
            " Values scale with agent count and stochastic draws — use for scenario comparison, not national estimates."
        : "";
    }

    $("#findings-admin").innerHTML = buildAdminHtml(data, e);
    $("#findings-model").innerHTML = buildModelHtml(data);
    $("#findings-benefit").innerHTML = buildBenefitHtml(benefit, data);
    $("#limitations").innerHTML = buildLimitationsHtml();

    const wl = $("#who-link");
    if (wl) {
      wl.href =
        data.who_context_url || "https://www.who.int/news-room/fact-sheets/detail/immunization-coverage";
    }

    $("#raw-json").textContent = JSON.stringify(data, null, 2);

    return { e, zdSq, zdSc, rowsSq: refYearlyReference(data), rowsSc: data.projection_yearly_scale_up };
  }

  function renderCharts(e, zdSq, zdSc, rowsSq, rowsSc, data) {
    const barCanvas = $("#chart-bar");
    const lineCanvas = $("#chart-line");
    const gapCanvas = $("#chart-gap");
    const countsCanvas = $("#chart-counts");
    const deathsLineCanvas = $("#chart-deaths-line");
    const deathsAvertedCanvas = $("#chart-deaths-averted");
    if (typeof Chart === "undefined") {
      if (barCanvas && barCanvas.parentElement) {
        barCanvas.parentElement.innerHTML =
          "<p class='banner error'>Chart.js did not load (check network / CDN). Text results above are still valid.</p>";
      }
      return;
    }

    try {
      if (barChart) barChart.destroy();
      if (lineChart) lineChart.destroy();
      if (gapChart) gapChart.destroy();
      if (countsChart) countsChart.destroy();
      if (deathsLineChart) deathsLineChart.destroy();
      if (deathsAvertedChart) deathsAvertedChart.destroy();

      const labels = e
        ? ["Data (admin. proxy)", "Reference scenario", "Intervention scenario"]
        : ["Reference scenario", "Intervention scenario"];
      const vals = e ? [e.meanZd * 100, zdSq * 100, zdSc * 100] : [zdSq * 100, zdSc * 100];
      const colors = e ? [COL.data, COL.ref, COL.int] : [COL.ref, COL.int];

      barChart = new Chart(barCanvas.getContext("2d"), {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Zero-dose share among under-fives (%)",
              data: vals,
              backgroundColor: colors,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            title: {
              display: true,
              text: "Reference vs intervention — zero-dose share at end of projection window",
            },
            tooltip: {
              callbacks: {
                afterLabel: function () {
                  return "Lower is better for zero-dose burden.";
                },
              },
            },
          },
          scales: {
            y: { beginAtZero: true, max: 100, title: { display: true, text: "% of under-fives" } },
          },
        },
      });

      const merged = mergeYearlyRows(rowsSq, rowsSc);
      const years = merged.years;
      const byY = merged.byY;

      if (rowsSq && rowsSc && years.length) {
        const dsq = years.map(function (y) {
          return byY[y].sqFrac != null ? byY[y].sqFrac * 100 : null;
        });
        const dsc = years.map(function (y) {
          return byY[y].scFrac != null ? byY[y].scFrac * 100 : null;
        });

        lineChart = new Chart(lineCanvas.getContext("2d"), {
          type: "line",
          data: {
            labels: years,
            datasets: [
              {
                label: "Reference scenario",
                data: dsq,
                borderColor: COL.ref,
                backgroundColor: COL.refFill,
                fill: true,
                tension: 0.15,
              },
              {
                label: "Intervention scenario",
                data: dsc,
                borderColor: COL.int,
                backgroundColor: COL.intFill,
                fill: true,
                tension: 0.15,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: "Trajectory of zero-dose share — room for policy is the vertical distance",
              },
            },
            scales: {
              y: { beginAtZero: true, max: 100, title: { display: true, text: "%" } },
              x: { title: { display: true, text: "Calendar year" } },
            },
          },
        });

        const gapPp = years.map(function (y) {
          const row = byY[y];
          if (row.sqFrac == null || row.scFrac == null) return null;
          return (row.sqFrac - row.scFrac) * 100;
        });

        if (gapCanvas) {
          gapChart = new Chart(gapCanvas.getContext("2d"), {
            type: "bar",
            data: {
              labels: years,
              datasets: [
                {
                  label: "Share-point gap (reference − intervention)",
                  data: gapPp,
                  backgroundColor: COL.gapBar,
                  borderColor: COL.gapBorder,
                  borderWidth: 1,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                title: {
                  display: true,
                  text: "Annual modeled benefit of intervention (larger = more share recovered per year)",
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: { display: true, text: "Percentage points" },
                },
                x: { title: { display: true, text: "Calendar year" } },
              },
            },
          });
        }

        const sqCounts = years.map(function (y) {
          return byY[y].sqNzd != null ? byY[y].sqNzd : null;
        });
        const scCounts = years.map(function (y) {
          return byY[y].scNzd != null ? byY[y].scNzd : null;
        });

        if (countsCanvas) {
          countsChart = new Chart(countsCanvas.getContext("2d"), {
            type: "bar",
            data: {
              labels: years,
              datasets: [
                {
                  label: "Reference — zero-dose children (modeled)",
                  data: sqCounts,
                  backgroundColor: COL.countsRef,
                },
                {
                  label: "Intervention — zero-dose children (modeled)",
                  data: scCounts,
                  backgroundColor: COL.countsInt,
                },
              ],
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
                  text: "Burden in children — same scenarios, absolute counts in the ABM cohort",
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: { precision: 0 },
                  title: { display: true, text: "Children (simulation)" },
                },
                x: { title: { display: true, text: "Calendar year" } },
              },
            },
          });
        }
      }

      const deathComp = data && data.projection_yearly_deaths_comparison;
      if (
        deathComp &&
        deathComp.length &&
        deathsLineCanvas &&
        deathsAvertedCanvas &&
        typeof Chart !== "undefined"
      ) {
        const yd = deathComp.map(function (r) {
          return r.calendar_year;
        });
        const baseD = deathComp.map(function (r) {
          return r.reference_deaths != null ? r.reference_deaths : r.baseline_deaths;
        });
        const intD = deathComp.map(function (r) {
          return r.intervention_deaths;
        });
        const avD = deathComp.map(function (r) {
          return r.deaths_averted;
        });

        deathsLineChart = new Chart(deathsLineCanvas.getContext("2d"), {
          type: "line",
          data: {
            labels: yd,
            datasets: [
              {
                label: "Reference — disease deaths",
                data: baseD,
                borderColor: COL.ref,
                backgroundColor: COL.deathsRefFill,
                fill: true,
                tension: 0.12,
              },
              {
                label: "Intervention — disease deaths",
                data: intD,
                borderColor: COL.int,
                backgroundColor: COL.deathsIntFill,
                fill: true,
                tension: 0.12,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: {
                display: true,
                text: "Pentavalent disease modules — annual deaths in the simulated cohort",
              },
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { precision: 0 },
                title: { display: true, text: "Deaths" },
              },
              x: { title: { display: true, text: "Calendar year" } },
            },
          },
        });

        deathsAvertedChart = new Chart(deathsAvertedCanvas.getContext("2d"), {
          type: "bar",
          data: {
            labels: yd,
            datasets: [
              {
                label: "Deaths averted (reference − intervention)",
                data: avD,
                backgroundColor: COL.avertedBar,
                borderColor: COL.avertedBorder,
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              title: {
                display: true,
                text: "Modeled averted deaths per year (positive = intervention fewer deaths)",
              },
            },
            scales: {
              y: {
                ticks: { precision: 0 },
                title: { display: true, text: "Deaths averted" },
              },
              x: { title: { display: true, text: "Calendar year" } },
            },
          },
        });
      }
    } catch (err) {
      console.error(err);
      const box = $("#chart-bar");
      if (box && box.parentElement) {
        box.parentElement.innerHTML =
          "<p class='banner error'>Could not draw charts: " + escapeHtml(String(err.message)) + "</p>";
      }
    }
  }

  function render(data) {
    const { e, zdSq, zdSc, rowsSq, rowsSc } = renderDom(data);

    $("#loading").style.display = "none";
    $("#app-main").hidden = false;

    // Charts need visible layout; wait one frame so canvas gets dimensions
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        renderCharts(e, zdSq, zdSc, rowsSq, rowsSc, data);
      });
    });
  }

  function buildDecisionHtml(data) {
    const start = data.projection_calendar_start;
    const stop = data.projection_calendar_stop;
    const span =
      start != null && stop != null ? String(start) + "–" + String(stop) : "the projection window";
    return (
      "<p class='mission'>" +
        "<strong>Zero-dose children</strong> (in WHO-aligned terms) are those who have not received " +
        "an initial DTP-containing dose—often proxied by pentavalent coverage in programs. " +
        "Reaching them is central to equity and to <strong>Immunization Agenda 2030</strong>; " +
        "barriers include geography, fragile settings, weak data, and health-system gaps. " +
        "<em>This page</em> shows a <strong>model-based</strong> contrast: calibrated reference delivery vs a strengthened " +
        "intervention—useful for direction and magnitude of effect, not a substitute for subnational maps, " +
        "survey estimates (e.g. KDHS/WUENIC), or costing of real programs.</p>" +
      "<ol class='decision-steps'>" +
        "<li><strong>Research question:</strong> Tetanus cases averted under reduced zero-dose burden by 2025 — the <strong>modeled answer</strong> (new tetanus infections, reference − intervention) is in <em>What the simulation compared</em> below and in <code>research_question_tetanus</code> in the JSON. Global headline figures from the brief are not produced by this run.</li>" +
        "<li><strong>What we show:</strong> Administrative data (when present) describe historical pressure. The model calibrates a <strong>reference scenario</strong> to that pressure, then contrasts it with an <strong>intervention scenario</strong> (stronger routine delivery and a higher coverage cap). Both arms run over <strong>" +
        escapeHtml(span) +
        "</strong>.</li>" +
        "<li><strong>Why the gap matters:</strong> The distance between reference and intervention curves is the modeled incremental benefit: fewer under-fives left without a first pentavalent dose in the simulation. Charts below show share, annual gap in percentage points, counts, and disease deaths in the modeled cohort.</li>" +
        "</ol>" +
        "<p class='muted'>Use these results for direction and magnitude of effect; pair with costing, delivery plans, and survey validation for investment decisions.</p>"
    );
  }

  function buildMetricsLead(data) {
    const y = data.years != null ? String(data.years) : "—";
    const na = data.n_agents != null ? data.n_agents.toLocaleString() : "—";
    const start = data.projection_calendar_start;
    const stop = data.projection_calendar_stop;
    const span = start != null && stop != null ? String(start) + "–" + String(stop) : "—";
    return (
      "Window <strong>" +
      escapeHtml(span) +
      "</strong> (" +
      escapeHtml(y) +
      " full years), <strong>" +
      escapeHtml(na) +
      "</strong> agents. " +
      "The highlighted card is the absolute gap in zero-dose <em>share</em> at the end of the window (reference minus intervention)."
    );
  }

  function buildExecutiveHtml(data, e, zdSq, zdSc, rel, benefit, hasDeaths) {
    const lines = [];
    const dsum = data.projection_death_benefit_summary || {};
    lines.push(
      "<p><strong>Reference scenario</strong> = delivery intensity calibrated to administrative zero-dose pressure (comparator). " +
        "<strong>Intervention scenario</strong> = deliberate strengthening (higher routine probability and coverage cap). " +
        "That contrast is the quantitative story for incremental benefit of intensified delivery.</p>"
    );
    const rqt = data.research_question_tetanus;
    if (rqt && rqt.modeled_answer) {
      const m = rqt.modeled_answer;
      const rqNote = rqt.interpretation
        ? " <span class='muted'>" + escapeHtml(rqt.interpretation) + "</span>"
        : "";
      let tp =
        "<p><strong>Research question — modeled tetanus cases averted:</strong> " +
        (m.tetanus_cases_averted_total != null
          ? "<strong>" + Math.round(m.tetanus_cases_averted_total).toLocaleString() + "</strong>"
          : "—") +
        " (new tetanus infections, reference − intervention, over the projection window). ";
      if (m.tetanus_cases_averted_calendar_year_2025 != null) {
        tp +=
          "Calendar year 2025: <strong>" +
          Math.round(m.tetanus_cases_averted_calendar_year_2025).toLocaleString() +
          "</strong> cases averted (modeled). ";
      }
      tp +=
        "Modeled zero-dose reduction vs reference (end of window): <strong>" +
        (m.modeled_zero_dose_relative_reduction_percent_end_window != null
          ? m.modeled_zero_dose_relative_reduction_percent_end_window.toFixed(1) + "%"
          : "—") +
        "</strong>." +
        rqNote +
        "</p>";
      lines.push(tp);
    }
    if (e) {
      lines.push(
        "<p>Administrative data (mean over months) imply roughly <strong>" +
          pct(e.meanCov) +
          "</strong> DTP1 proxy coverage and <strong>" +
          pct(e.meanZd) +
          "</strong> zero-dose proxy (±" +
          pct(e.stdZd) +
          " across months; " +
          e.nMonths +
          " months" +
          (e.yearsSpan ? ", " + e.yearsSpan : "") +
          "). The reference scenario is aligned to that pressure before projecting forward.</p>"
      );
    }
    lines.push(
      "<p>By the <strong>end of the projection</strong>, the model places zero-dose share at <strong>" +
        pct(zdSq) +
        "</strong> under the reference scenario vs <strong>" +
        pct(zdSc) +
        "</strong> under the intervention scenario — about a <strong>" +
        (rel != null ? rel.toFixed(1) : "—") +
        "%</strong> relative reduction in that share vs reference. " +
        "Averaged over years, the share narrows by about <strong>" +
        pp(benefit.mean_annual_reduction_zerodose_share_pp) +
        "</strong> per year under intervention vs reference (see Supporting detail).</p>"
    );
    if (hasDeaths && dsum.total_deaths_averted != null) {
      lines.push(
        "<p>Modeled <strong>disease deaths</strong> (pentavalent pathogens in the simulation, not all-cause mortality) total about <strong>" +
          Math.round(totalReferenceDeaths(dsum) || 0).toLocaleString() +
          "</strong> under the reference scenario vs <strong>" +
          Math.round(dsum.total_intervention_deaths || 0).toLocaleString() +
          "</strong> under intervention — about <strong>" +
          Math.round(dsum.total_deaths_averted || 0).toLocaleString() +
          "</strong> deaths averted over the projection window in this cohort.</p>"
      );
    }
    return lines.join("");
  }

  function buildDeathsFindingsHtml(dsum, data) {
    if (!dsum || totalReferenceDeaths(dsum) == null) {
      return (
        "<p class='muted'>No disease death summary in this JSON. Re-run <code>python run_simulation.py</code> with the current codebase.</p>"
      );
    }
    const note = data.disease_deaths_note
      ? "<p class='muted'>" + escapeHtml(data.disease_deaths_note) + "</p>"
      : "";
    const caveat =
      dsum.total_deaths_averted != null && dsum.total_deaths_averted < 0
        ? "<p class='muted'>In this draw, intervention had more modeled disease deaths than the reference scenario (stochastic noise is normal for small cohorts or short windows). Prefer longer runs, more agents, or multiple seeds for a stable ordering.</p>"
        : "";
    return (
      note +
        caveat +
        "<ul class='facts'>" +
        "<li>Total disease deaths, reference scenario: <strong>" +
        Math.round(totalReferenceDeaths(dsum)).toLocaleString() +
        "</strong></li>" +
        "<li>Total disease deaths, intervention scenario: <strong>" +
        Math.round(dsum.total_intervention_deaths).toLocaleString() +
        "</strong></li>" +
        "<li>Total averted (reference − intervention): <strong>" +
        Math.round(dsum.total_deaths_averted).toLocaleString() +
        "</strong></li>" +
        "<li>Mean averted per calendar year: <strong>" +
        (dsum.mean_annual_deaths_averted != null ? dsum.mean_annual_deaths_averted.toFixed(2) : "—") +
        "</strong></li>" +
        "</ul>"
    );
  }

  function buildAdminHtml(data, e) {
    if (!e) {
      return "<p class='muted'>No administrative summary in this JSON. Run <code>python run_simulation.py</code> with the xlsx data path.</p>";
    }
    return (
      "<p>We use monthly <strong>dpt1</strong> and <strong>estimated_lb</strong> (annual live births) to build a coverage proxy " +
        "<code>min(1, dpt1 / (estimated_lb/12))</code> and zero-dose proxy <code>1 − coverage</code>. " +
        "This is an administrative approximation, not a household survey.</p>" +
        "<p class='muted'>Data file: " +
        escapeHtml(data.data_file || "—") +
        "</p>"
    );
  }

  function buildModelHtml(data) {
    const b = refCalibrationBundle(data);
    if (!b) return "<p class='muted'>Missing calibration bundles in JSON.</p>";
    return (
      "<p>The intervention in the model is <strong>stronger routine vaccination delivery</strong> (higher probability of a successful routine contact and, in the intervention scenario, a higher coverage cap). " +
        "Parameters are fixed immediately before each run (see <code>zerodose_calibration.py</code>). " +
        "Routine delivery uses <code>routine_prob × coverage</code> per timestep.</p>" +
        "<ul class='facts'>" +
        "<li>Reference scenario: routine_prob ≈ <strong>" +
        (refRoutineProb(data) != null ? refRoutineProb(data).toFixed(4) : "—") +
        "</strong>, coverage ≈ <strong>" +
        (b.intervention_coverage != null ? b.intervention_coverage.toFixed(4) : "—") +
        "</strong></li>" +
        "<li>Intervention scenario: routine_prob ≈ <strong>" +
        (data.model_scale_up_routine_prob != null ? data.model_scale_up_routine_prob.toFixed(4) : "—") +
        "</strong>, coverage cap ≈ <strong>" +
        (data.model_scale_up_coverage != null ? data.model_scale_up_coverage.toFixed(4) : "—") +
        "</strong></li>" +
        "<li>Birth rate (model): <strong>" +
        (b.birth_rate != null ? b.birth_rate : "—") +
        "</strong> /1000/yr; death rate: <strong>" +
        (b.death_rate != null ? b.death_rate : "—") +
        "</strong> /1000/yr</li>" +
        "</ul>"
    );
  }

  function buildBenefitHtml(benefit, data) {
    if (!benefit || !Object.keys(benefit).length) {
      return "<p class='muted'>No projection benefit block in this JSON.</p>";
    }
    return (
      "<p>These metrics summarize how much the <strong>intervention scenario</strong> closes the gap versus the <strong>reference scenario</strong> over the projection years — the core incremental effect in this demo.</p>" +
        "<ul class='facts'>" +
        "<li>Mean annual reduction in zero-dose <em>share</em> (intervention vs reference): <strong>" +
        pp(benefit.mean_annual_reduction_zerodose_share_pp) +
        "</strong></li>" +
        "<li>Cumulative (percentage-point·years): <strong>" +
        (benefit.cumulative_zerodose_share_reduction_pp_years != null
          ? benefit.cumulative_zerodose_share_reduction_pp_years.toFixed(1)
          : "—") +
        "</strong> — integrated “share recovered” over time</li>" +
        "<li>Sum of annual differences in zero-dose <em>child counts</em> (modeled cohort): <strong>" +
        (benefit.sum_annual_zero_dose_children_gap != null
          ? benefit.sum_annual_zero_dose_children_gap
          : "—") +
        "</strong></li>" +
        "</ul>" +
        "<p class='muted'>Years included: " +
        (Array.isArray(benefit.projection_years) ? benefit.projection_years.join(", ") : "—") +
        "</p>"
    );
  }

  function buildLimitationsHtml() {
    return (
      "<ul class='facts'>" +
        "<li>This is <strong>scenario evidence</strong>, not a guarantee of real-world impact without program quality and reach.</li>" +
        "<li>Administrative proxies differ from survey coverage; align with WUENIC/GHO for external reporting.</li>" +
        "<li>By default both arms use the same RNG seed (fair counterfactual); override <code>--seed-intervention</code> only if you want independent draws between arms.</li>" +
        "<li>Child counts scale with the simulated cohort, not the national birth cohort unless you rescale the model.</li>" +
        "</ul>"
    );
  }

  function escapeHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  async function tryFetch(url) {
    const r = await fetch(url, { cache: "no-store" });
    if (!r.ok) throw new Error(r.status + " " + url);
    return r.json();
  }

  function showFilePicker(msg) {
    const loadEl = $("#loading");
    loadEl.className = "banner error";
    loadEl.innerHTML =
      "<p><strong>" +
      escapeHtml(msg) +
      "</strong></p>" +
      "<p>1. Run: <code>python run_simulation.py</code> (writes <code>web/data/summary.js</code> + <code>summary.json</code>).</p>" +
      "<p>2. Or: <code>python web/open_spa.py</code> to start the server and open the browser.</p>" +
      "<p>3. Or pick a <code>zerodose_demo_summary.json</code> file:</p>" +
      '<div class="file-row"><input type="file" id="file" accept="application/json,.json" /></div>';
    const inp = $("#file");
    if (inp) {
      inp.addEventListener(
        "change",
        function (ev) {
          const f = ev.target.files[0];
          if (!f) return;
          const reader = new FileReader();
          reader.onload = function () {
            try {
              render(JSON.parse(reader.result));
              const ds = $("#data-source");
              if (ds) ds.textContent = "Loaded: " + f.name;
            } catch (err) {
              alert("Invalid JSON: " + err.message);
            }
          };
          reader.readAsText(f);
        },
        { once: false }
      );
    }
  }

  function isUsableSummary(obj) {
    return (
      obj &&
      typeof obj === "object" &&
      (obj.projection_calendar_start != null || obj.n_agents != null)
    );
  }

  async function load() {
    // 1) Embedded by run_simulation.py (works with file:// and http)
    if (typeof window.ZDSIM_SUMMARY !== "undefined" && window.ZDSIM_SUMMARY !== null) {
      if (isUsableSummary(window.ZDSIM_SUMMARY)) {
        try {
          render(window.ZDSIM_SUMMARY);
          const ds = $("#data-source");
          if (ds) ds.textContent = "Loaded: embedded web/data/summary.js";
          return;
        } catch (err) {
          console.error(err);
          showFilePicker("Embedded data failed to render: " + String(err.message));
          return;
        }
      }
    }

    const urls = candidateDataUrls();
    let lastErr;
    for (const p of urls) {
      try {
        const data = await tryFetch(p);
        render(data);
        const ds = $("#data-source");
        if (ds) ds.textContent = "Loaded: " + p;
        return;
      } catch (e) {
        lastErr = e;
      }
    }
    console.error("All fetch attempts failed:", lastErr);
    const sub = $("#hero-sub");
    if (sub) sub.textContent = "Results not loaded — see instructions below";
    showFilePicker(
      "No embedded results and no fetch (run python run_simulation.py to build web/data/summary.js, or use a local server)."
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
