""" Load the included administrative immunization workbook. """

import os

import numpy as np
import pandas as pd


def default_formatted_xlsx_path():
    """ Absolute path to the formatted monthly workbook shipped in ``zdsim/data/``. """
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "data", "zerodose_data_formated.xlsx")


def load_formatted_xlsx(path=None):
    """ Load Sheet1 of the monthly workbook; uses the included default if ``path`` is None. """
    path = path or default_formatted_xlsx_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"Data file not found: {path}\n"
            "Use zerodose_data_formated.xlsx (not the Excel lock file ~$...)."
        )
    df = pd.read_excel(path, sheet_name=0, engine="openpyxl")
    return df


def empirical_zerodose_proxy_dtp1(df):
    """ Mean DTP1 zero-dose proxy (1 - dpt1/monthly_births) across all rows. """
    need    = {"dpt1", "estimated_lb"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    lb             = pd.to_numeric(df["estimated_lb"], errors="coerce").astype(float)
    d1             = pd.to_numeric(df["dpt1"],          errors="coerce").astype(float)
    monthly_births = lb / 12.0
    valid          = monthly_births > 0
    ratio          = np.where(valid, d1 / monthly_births, np.nan)
    coverage       = np.clip(ratio, 0.0, 1.0)
    zerodose       = 1.0 - coverage

    return {
        "mean_zerodose_proxy":      float(np.nanmean(zerodose)),
        "std_zerodose_proxy":       float(np.nanstd(zerodose)),
        "mean_dtp1_coverage_proxy": float(np.nanmean(coverage)),
        "n_months":                 int(len(df)),
        "years_span":               f"{df['year'].min()}-{df['year'].max()}" if "year" in df.columns else None,
    }


def monthly_dtp1_coverage_and_zerodose(df):
    """ Per-row DTP1 coverage proxy, zero-dose proxy, and ``period`` label for plotting. """
    need    = {"dpt1", "estimated_lb"}
    missing = need - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    out            = df.copy()
    lb             = pd.to_numeric(out["estimated_lb"], errors="coerce").astype(float)
    d1             = pd.to_numeric(out["dpt1"],          errors="coerce").astype(float)
    monthly_births = lb / 12.0
    ratio          = np.where(monthly_births > 0, d1 / monthly_births, np.nan)

    out["dtp1_coverage_proxy"] = np.clip(ratio, 0.0, 1.0)
    out["zerodose_proxy"]      = 1.0 - out["dtp1_coverage_proxy"]

    if "year" in out.columns and "month" in out.columns:
        out["period"] = out["year"].astype(str) + " " + out["month"].astype(str)
    else:
        out["period"] = np.arange(len(out))

    return out
