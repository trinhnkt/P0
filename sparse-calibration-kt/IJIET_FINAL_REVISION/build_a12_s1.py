#!/usr/bin/env python3
"""A12: Supplementary Table S1 from existing four-partition bucket summary (no rebin)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "analysis" / "summary_4part_bucket.csv"
OUT = HERE / "supplementary" / "Table_S1_calibration_full.tex"

DS = {"assist2012": "ASSISTments 2012", "junyi": "Junyi Academy", "xes3g5m": "XES3G5M"}
MODEL = {"irt_1pl": "IRT", "dkt": "DKT", "simplekt": "T-KT"}
STRATA = ["dense", "medium", "sparse"]
MODELS = ["irt_1pl", "dkt", "simplekt"]
DATASETS = ["assist2012", "junyi", "xes3g5m"]


def flag(n: int) -> str:
    if n >= 1000:
        return "R"
    if n >= 100:
        return "L"
    return "I"


def pm(mean: float, std: float, d: int = 4) -> str:
    if pd.isna(mean):
        return "---"
    m = f"{mean:.{d}f}"
    if pd.isna(std) or float(std) == 0.0:
        return f"${m}$"
    return f"${m}\\pm{std:.{d}f}$"


def main() -> None:
    df = pd.read_csv(SRC)
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Four-unique-partition event-level calibration by train-only frequency stratum (same aggregation and $M=15$ equal-width bins as Table 4). $N$ is the mean test-event count across four unique learner partitions. Flags: Reliable (R) $N\ge 1000$; Limited (L) $100\le N<1000$. Junyi sparse is empty. T-KT is the local Transformer KT baseline. Brier $=$ UNC $-$ RES $+$ REL is the binned decomposition already used in the manuscript; components need not sum exactly to Brier. IRT RES $=0$ on these learner-based strata.}",
        r"\label{tab:s1_calibration_full}",
        r"\centering\scriptsize",
        r"\begin{tabular}{lllrlccccc}",
        r"\toprule",
        r"Dataset & Model & Stratum & $N$ & Flag & ECE & Brier & UNC & REL & RES \\",
        r"\midrule",
    ]
    last_ds = None
    n_rows = 0
    for ds in DATASETS:
        for model in MODELS:
            for stratum in STRATA:
                sub = df[
                    (df["dataset"] == ds)
                    & (df["model"] == model)
                    & (df["bucket"] == stratum)
                    & (df["n_partitions"] == 4)
                ]
                if sub.empty:
                    continue
                r = sub.iloc[0]
                n = int(round(float(r["n_events_mean"])))
                if last_ds is not None and DS[ds] != last_ds:
                    lines.append(r"\midrule")
                last_ds = DS[ds]
                lines.append(
                    f"{DS[ds]} & {MODEL[model]} & {stratum} & {n:,} & {flag(n)} & "
                    f"{pm(r['ece_mean'], r['ece_std'])} & "
                    f"{pm(r['brier_mean'], r['brier_std'])} & "
                    f"{pm(r['uncertainty_mean'], r['uncertainty_std'])} & "
                    f"{pm(r['reliability_mean'], r['reliability_std'])} & "
                    f"{pm(r['resolution_mean'], r['resolution_std'])} \\\\"
                )
                n_rows += 1
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} rows={n_rows}")


if __name__ == "__main__":
    main()
