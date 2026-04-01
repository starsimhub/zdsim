"""
Load regional administrative immunization extracts bundled with zdsim.

Note: Microsoft Excel creates temporary lock files named ``~$*.xlsx`` while a
workbook is open. Those are not data files — use ``zerodose_data_formated.xlsx``.
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np
import pandas as pd


def default_formatted_xlsx_path() -> str:
    """Absolute path to the formatted monthly workbook shipped in ``zdsim/data/``."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "data", "zerodose_data_formated.xlsx")


def load_formatted_xlsx(path: str | None = None) -> pd.DataFrame:
    """Load the monthly Sheet1 table (vaccine doses, births, cases, etc.)."""
    path = path or default_formatted_xlsx_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Data file not found: {path}\n"
            "Use zerodose_data_formated.xlsx (not the Excel lock file ~$...)."
        )
    df = pd.read_excel(path, sheet_name=0, engine="openpyxl")
    return df


def empirical_zerodose_proxy_dtp1(df: pd.DataFrame) -> dict[str, Any]:
    """
    Administrative proxy for the share of infants with **no DTP1** (zero-dose for
    DTP-containing vaccine), aligned with WHO/WUENIC *first-dose* monitoring.

    For each month, approximate first-dose coverage as
    ``min(1, dpt1 / monthly_live_births)``, with
    ``monthly_live_births = estimated_lb / 12`` when ``estimated_lb`` is
    interpreted as annual live births in the sheet (constant or slow-varying).

    Zero-dose proxy = ``1 - coverage_proxy`` (clipped to [0, 1]).

    This is a **proxy from reported counts**, not individual-level survey
    coverage; interpret alongside official WUENIC/GHO estimates when publishing.
    """
    need = {"dpt1", "estimated_lb"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    lb = pd.to_numeric(df["estimated_lb"], errors="coerce").astype(float)
    d1 = pd.to_numeric(df["dpt1"], errors="coerce").astype(float)
    monthly_births = lb / 12.0
    valid = monthly_births > 0
    ratio = np.where(valid, d1 / monthly_births, np.nan)
    coverage = np.clip(ratio, 0.0, 1.0)
    zerodose = 1.0 - coverage

    return {
        "mean_zerodose_proxy": float(np.nanmean(zerodose)),
        "std_zerodose_proxy": float(np.nanstd(zerodose)),
        "mean_dtp1_coverage_proxy": float(np.nanmean(coverage)),
        "n_months": int(len(df)),
        "years_span": f"{df['year'].min()}-{df['year'].max()}"
        if "year" in df.columns
        else None,
    }


def monthly_dtp1_coverage_and_zerodose(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-row DTP1 coverage proxy and zero-dose proxy (same definitions as
    :func:`empirical_zerodose_proxy_dtp1`), plus a simple period label for plotting.
    """
    need = {"dpt1", "estimated_lb"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out = df.copy()
    lb = pd.to_numeric(out["estimated_lb"], errors="coerce").astype(float)
    d1 = pd.to_numeric(out["dpt1"], errors="coerce").astype(float)
    monthly_births = lb / 12.0
    ratio = np.where(monthly_births > 0, d1 / monthly_births, np.nan)
    out["dtp1_coverage_proxy"] = np.clip(ratio, 0.0, 1.0)
    out["zerodose_proxy"] = 1.0 - out["dtp1_coverage_proxy"]

    if "year" in out.columns and "month" in out.columns:
        out["period"] = out["year"].astype(str) + " " + out["month"].astype(str)
    else:
        out["period"] = np.arange(len(out))

    return out
