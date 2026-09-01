#!/usr/bin/env python3
"""A8: write the complete controlled-sparsification grid (historical A9, not A2B)."""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "analysis" / "a9_statistical_summary.csv"
OUT_CSV = HERE / "analysis" / "controlled_sparsification_full.csv"
OUT_TEX = HERE / "supplementary" / "Table_S2_controlled_sparsification.tex"

DS_NAME = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}
MODEL_CSV = {"dkt": "dkt", "simplekt": "simplekt"}
MODEL_TEX = {"dkt": "DKT", "simplekt": "T-KT"}
LEVEL_ROWS = {"t500": 500, "t100": 100, "t50": 50}
DS_ORDER = ["assist2012", "junyi", "xes3g5m"]
MODEL_ORDER = ["dkt", "simplekt"]
LEVEL_ORDER = ["t500", "t100", "t50"]


def fmt_signed(x: float, digits: int = 3) -> str:
    v = round(x, digits)
    if abs(v) < 0.5 * 10 ** (-digits):
        return f"$0.{'0' * digits}$"
    if v > 0:
        return f"$+{v:.{digits}f}$"
    return f"$-{abs(v):.{digits}f}$"


def fmt_ci(lo: float, hi: float, digits: int = 3) -> str:
    return f"[{fmt_signed(lo, digits)}, {fmt_signed(hi, digits)}]"


def share_pct(frac: float) -> str:
    return f"{int(round(frac * 100))}\\%"


def load_rows() -> list[dict]:
    with SRC.open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    by = {(r["dataset"], r["model"], r["level"]): r for r in raw}
    rows = []
    for ds in DS_ORDER:
        for model in MODEL_ORDER:
            for level in LEVEL_ORDER:
                r = by[(ds, model, level)]
                rows.append(
                    {
                        "dataset": DS_NAME[ds],
                        "model": MODEL_CSV[model],
                        "rows_kept": LEVEL_ROWS[level],
                        "delta_ECE": float(r["delta_ECE_mean"]),
                        "CI_low": float(r["delta_ECE_ci95_lo"]),
                        "CI_high": float(r["delta_ECE_ci95_hi"]),
                        "delta_REL": float(r["delta_REL_mean"]),
                        "REL_CI_low": float(r["delta_REL_ci95_lo"]),
                        "REL_CI_high": float(r["delta_REL_ci95_hi"]),
                        "share_ECE_increase": float(r["frac_kcs_ece_worse"]),
                        "n_KCs": int(r["n_kcs"]),
                        "_tex_model": MODEL_TEX[model],
                    }
                )
    if len(rows) != 18:
        raise SystemExit(f"expected 18 cells, got {len(rows)}")
    return rows


def write_csv(rows: list[dict]) -> None:
    fields = [
        "dataset",
        "model",
        "rows_kept",
        "delta_ECE",
        "CI_low",
        "CI_high",
        "delta_REL",
        "REL_CI_low",
        "REL_CI_high",
        "share_ECE_increase",
        "n_KCs",
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})


def write_tex(rows: list[dict]) -> None:
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Complete within-KC controlled sparsification (seed 42; 30 originally dense KCs per dataset; learner-based fold 0). $\Delta=$ reduced$-$full. Positive $\Delta$ECE means worse calibration after reducing training rows for the same KC. 95\% CIs are bootstrap over KCs. T-KT is the local Transformer KT baseline, not published SimpleKT. This table reports every dataset $\times$ model $\times$ $\{500,100,50\}$ cell; none is omitted. Not a causal law for real-world sparsity.}",
        r"\label{tab:s2_controlled_sparsification}",
        r"\centering\scriptsize",
        r"\begin{tabular}{llrcccc}",
        r"\toprule",
        r"Dataset & Model & Rows & $\Delta$ECE [95\% CI] & $\Delta$REL [95\% CI] & Share ECE$\uparrow$ & $n_{\mathrm{KC}}$ \\",
        r"\midrule",
    ]
    last_ds = None
    for r in rows:
        if last_ds is not None and r["dataset"] != last_ds:
            lines.append(r"\midrule")
        last_ds = r["dataset"]
        ece = f"{fmt_signed(r['delta_ECE'])} {fmt_ci(r['CI_low'], r['CI_high'])}"
        rel = f"{fmt_signed(r['delta_REL'])} {fmt_ci(r['REL_CI_low'], r['REL_CI_high'])}"
        lines.append(
            f"{r['dataset']} & {r['_tex_model']} & {r['rows_kept']} & "
            f"{ece} & {rel} & {share_pct(r['share_ECE_increase'])} & {r['n_KCs']} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing source {SRC}")
    rows = load_rows()
    write_csv(rows)
    write_tex(rows)
    xes_sk = [r for r in rows if r["dataset"] == "XES3G5M" and r["model"] == "simplekt"]
    print(f"wrote {OUT_CSV} n={len(rows)}")
    print(f"wrote {OUT_TEX}")
    for r in xes_sk:
        print(
            f"XES simplekt {r['rows_kept']}: "
            f"dECE={r['delta_ECE']:+.4f} [{r['CI_low']:+.4f}, {r['CI_high']:+.4f}]"
        )


if __name__ == "__main__":
    main()
