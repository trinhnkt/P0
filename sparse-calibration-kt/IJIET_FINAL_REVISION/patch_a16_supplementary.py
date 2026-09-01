#!/usr/bin/env python3
"""Patch supplementary XES rows from A2B CSVs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
A2B_BUCKET = HERE / "a2b" / "analysis" / "summary_4part_bucket.csv"
A2B_A9 = HERE / "a2b" / "analysis" / "a9" / "statistical_summary.csv"
S1 = HERE / "supplementary" / "Table_S1_calibration_full.tex"
S2 = HERE / "supplementary" / "Table_S2_controlled_sparsification.tex"
SREG = HERE / "supplementary" / "Table_S_regression.tex"


def pm(mean: float, std: float, d: int = 4) -> str:
    if pd.isna(mean):
        return "---"
    m = f"{mean:.{d}f}"
    if pd.isna(std) or float(std) == 0.0:
        return f"${m}$"
    return f"${m}\\pm{std:.{d}f}$"


def flag(n: int) -> str:
    if n >= 1000:
        return "R"
    if n >= 100:
        return "L"
    return "I"


def patch_s1() -> None:
    df = pd.read_csv(A2B_BUCKET)
    model_name = {"irt_1pl": "IRT", "dkt": "DKT", "simplekt": "T-KT"}
    lines = []
    for model in ("irt_1pl", "dkt", "simplekt"):
        for stratum in ("dense", "medium", "sparse"):
            r = df[(df["model"] == model) & (df["bucket"] == stratum) & (df["n_partitions"] == 4)].iloc[0]
            n = int(round(float(r["n_events_mean"])))
            lines.append(
                f"XES3G5M & {model_name[model]} & {stratum} & {n:,} & {flag(n)} & "
                f"{pm(r['ece_mean'], r['ece_std'])} & "
                f"{pm(r['brier_mean'], r['brier_std'])} & "
                f"{pm(r['uncertainty_mean'], r['uncertainty_std'])} & "
                f"{pm(r['reliability_mean'], r['reliability_std'])} & "
                f"{pm(r['resolution_mean'], r['resolution_std'])} \\\\"
            )
    text = S1.read_text(encoding="utf-8")
    start = text.index("XES3G5M & IRT & dense")
    end = text.index("\\bottomrule", start)
    new = text[:start] + "\n".join(lines) + "\n" + text[end:]
    S1.write_text(new, encoding="utf-8")
    print("patched S1 XES", len(lines), "rows")


def fmt_ci(mean, lo, hi) -> str:
    sign = "+" if mean >= 0 else "-"
    def one(x):
        s = "+" if x >= 0 else "-"
        return f"{s}{abs(x):.3f}"
    return f"{sign}{abs(mean):.3f} [{one(lo)}, {one(hi)}]"


def patch_s2() -> None:
    df = pd.read_csv(A2B_A9)
    rows = {
        ("dkt", "t500"): "XES3G5M & DKT & 500",
        ("dkt", "t100"): "XES3G5M & DKT & 100",
        ("dkt", "t50"): "XES3G5M & DKT & 50",
        ("simplekt", "t500"): "XES3G5M & T-KT & 500",
        ("simplekt", "t100"): "XES3G5M & T-KT & 100",
        ("simplekt", "t50"): "XES3G5M & T-KT & 50",
    }
    text = S2.read_text(encoding="utf-8")
    for (model, level), prefix in rows.items():
        r = df[(df["model"] == model) & (df["level"] == level)].iloc[0]
        ece = fmt_ci(r["delta_ECE_mean"], r["delta_ECE_ci95_lo"], r["delta_ECE_ci95_hi"])
        rel = fmt_ci(r["delta_REL_mean"], r["delta_REL_ci95_lo"], r["delta_REL_ci95_hi"])
        share = f"{int(round(100 * r['frac_kcs_ece_worse']))}\\%"
        new_line = (
            f"{prefix} & ${ece.replace('[', '[$').replace(', ', '$, $').replace(']', '$]')}$ "
            f"& ${rel.replace('[', '[$').replace(', ', '$, $').replace(']', '$]')}$ "
            f"& {share} & 30 \\\\"
        )
        # simpler: match original S2 style
        # $+0.014$ [$-0.002$, $+0.032$]
        def tex_pm(x: float) -> str:
            return f"{'+' if x >= 0 else '-'}{abs(x):.3f}"
        ece_tex = (
            f"${tex_pm(r['delta_ECE_mean'])}$ "
            f"[${tex_pm(r['delta_ECE_ci95_lo'])}$, ${tex_pm(r['delta_ECE_ci95_hi'])}$]"
        )
        rel_tex = (
            f"${tex_pm(r['delta_REL_mean'])}$ "
            f"[${tex_pm(r['delta_REL_ci95_lo'])}$, ${tex_pm(r['delta_REL_ci95_hi'])}$]"
        )
        new_line = f"{prefix} & {ece_tex} & {rel_tex} & {share} & 30 \\\\"
        old_start = text.index(prefix)
        old_end = text.index("\\\\", old_start) + 2
        text = text[:old_start] + new_line + text[old_end:]
    S2.write_text(text, encoding="utf-8")
    print("patched S2 XES")


def patch_sreg() -> None:
    # Weighted XES block from A2B Huber (manifest). n=829.
    old = """XES3G5M & $\\log(1+f_{\\mathrm{train}})$ & 1,263 & 830 & $-0.069$ & $0.028$ & $[-0.123,-0.015]$ & 0.013 \\\\
 & Difficulty proxy & 1,263 & 830 & $+0.010$ & $0.011$ & $[-0.011,+0.031]$ & 0.347 \\\\
 & Item support & 1,263 & 830 & $+0.008$ & $0.005$ & $[-0.001,+0.017]$ & 0.092 \\\\
 & Learner exposure & 1,263 & 830 & $-0.001$ & $0.012$ & $[-0.024,+0.022]$ & 0.926 \\\\
 & Curriculum position & 1,263 & 830 & $-0.000$ & $0.007$ & $[-0.015,+0.014]$ & 0.969 \\\\"""
    new = """XES3G5M & $\\log(1+f_{\\mathrm{train}})$ & 829 & 829 & $-0.028$ & $0.007$ & $[-0.042,-0.014]$ & $<0.001$ \\\\
 & Difficulty proxy & 829 & 829 & $+0.080$ & $0.004$ & $[+0.072,+0.088]$ & $<0.001$ \\\\
 & Item support & 829 & 829 & $-0.007$ & $0.001$ & $[-0.010,-0.005]$ & $<0.001$ \\\\
 & Learner exposure & 829 & 829 & $+0.013$ & $0.004$ & $[+0.005,+0.021]$ & 0.001 \\\\
 & Curriculum position & 829 & 829 & $-0.014$ & $0.002$ & $[-0.019,-0.009]$ & $<0.001$ \\\\"""
    text = SREG.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit("S regression weighted XES block not found")
    text = text.replace(old, new, 1)
    old_u = """XES3G5M & $\\log(1+f_{\\mathrm{train}})$ & 1,263 & 830 & $-0.012$ & $0.010$ & $[-0.031,+0.007]$ & 0.209 \\\\
 & Difficulty proxy & 1,263 & 830 & $+0.044$ & $0.007$ & $[+0.031,+0.057]$ & $<0.001$ \\\\
 & Item support & 1,263 & 830 & $-0.010$ & $0.005$ & $[-0.021,+0.001]$ & 0.064 \\\\
 & Learner exposure & 1,263 & 830 & $+0.019$ & $0.008$ & $[+0.003,+0.035]$ & 0.022 \\\\
 & Curriculum position & 1,263 & 830 & $-0.004$ & $0.004$ & $[-0.013,+0.005]$ & 0.350 \\\\"""
    new_u = """XES3G5M & $\\log(1+f_{\\mathrm{train}})$ & 829 & 829 & $-0.008$ & $0.012$ & $[-0.031,+0.015]$ & 0.488 \\\\
 & Difficulty proxy & 829 & 829 & $+0.070$ & $0.006$ & $[+0.057,+0.083]$ & $<0.001$ \\\\
 & Item support & 829 & 829 & $-0.009$ & $0.002$ & $[-0.014,-0.004]$ & $<0.001$ \\\\
 & Learner exposure & 829 & 829 & $+0.007$ & $0.008$ & $[-0.009,+0.023]$ & 0.396 \\\\
 & Curriculum position & 829 & 829 & $-0.017$ & $0.004$ & $[-0.025,-0.009]$ & $<0.001$ \\\\"""
    if old_u not in text:
        raise SystemExit("S regression unweighted XES block not found")
    text = text.replace(old_u, new_u, 1)
    SREG.write_text(text, encoding="utf-8")
    print("patched S regression XES")


def main() -> None:
    patch_s1()
    patch_s2()
    patch_sreg()


if __name__ == "__main__":
    main()
