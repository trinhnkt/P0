#!/usr/bin/env python3
"""B1: occupancy vs mixed-τ policies on frozen T-KT p (ASSISTments seed 42).

Source: analysis/direction_c/threshold_rates.csv (same cells as Table 5 / S3).
No retraining. CSV model name simplekt is T-KT in the manuscript.
"""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SRC = ROOT.parent / "analysis" / "direction_c" / "threshold_rates.csv"
OUT_CSV = HERE / "b1_occupancy_gate_policies.csv"
OUT_TXT = HERE / "b1_occupancy_gate_policies.txt"
OUT_TEX = ROOT / "supplementary" / "Table_S4_occupancy_policies.tex"


def load() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with SRC.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["dataset"] == "assist2012" and r["model"] == "simplekt":
                rows.append(r)
    return rows


def get(rows: list[dict[str, str]], tau: float, bucket: str) -> dict[str, str]:
    for r in rows:
        if abs(float(r["tau"]) - tau) < 1e-9 and r["bucket"] == bucket:
            return r
    raise KeyError((tau, bucket))


def stats(r: dict[str, str]) -> dict[str, float]:
    n = float(r["n_events"] or 0)
    na = float(r["n_advance"] or 0)
    my = float(r["mean_y"]) if r["mean_y"] else 0.0
    ninc = n * (1.0 - my) if n else 0.0
    fm = float(r["FM"]) if r["FM"] else None
    err = (fm * na) if fm is not None else 0.0
    return {"n": n, "na": na, "ninc": ninc, "err": err, "fm": fm or float("nan")}


def fmt_far(x: float | None) -> str:
    if x is None:
        return "—"
    return f"{x:.3f}"


def main() -> None:
    rows = load()
    d07 = stats(get(rows, 0.7, "dense"))
    m07 = stats(get(rows, 0.7, "medium"))
    s07 = stats(get(rows, 0.7, "sparse"))
    v07 = stats(get(rows, 0.7, "very_sparse"))
    s08 = stats(get(rows, 0.8, "sparse"))
    all07 = stats(get(rows, 0.7, "all"))
    ninc_all = all07["ninc"]

    a_na, a_err = all07["na"], all07["err"]
    a_far, a_miss = a_err / a_na, a_err / ninc_all

    b_na = d07["na"] + m07["na"]
    b_err = d07["err"] + m07["err"]
    b_far, b_miss = b_err / b_na, b_err / ninc_all

    c_na = d07["na"] + m07["na"] + s08["na"] + v07["na"]
    c_err = d07["err"] + m07["err"] + s08["err"] + v07["err"]
    c_far, c_miss = c_err / c_na, c_err / ninc_all

    if round(d07["fm"], 3) != 0.196 or round(s07["fm"], 3) != 0.268:
        raise SystemExit(f"lock FAR {d07['fm']} {s07['fm']}")
    if int(s07["na"]) != 235:
        raise SystemExit(f"lock Nadvance sparse {s07['na']}")

    recs = [
        {
            "policy": "A_global_tau07",
            "pop_Nadvance": int(a_na),
            "pop_FAR": a_far,
            "pop_Miss": a_miss,
            "sparse_Nadvance": int(s07["na"]),
            "sparse_FAR": s07["fm"],
            "sparse_Miss": s07["err"] / s07["ninc"],
        },
        {
            "policy": "B_Reliable_only",
            "pop_Nadvance": int(b_na),
            "pop_FAR": b_far,
            "pop_Miss": b_miss,
            "sparse_Nadvance": 0,
            "sparse_FAR": "",
            "sparse_Miss": 0.0,
        },
        {
            "policy": "C_sparse_tau08",
            "pop_Nadvance": int(c_na),
            "pop_FAR": c_far,
            "pop_Miss": c_miss,
            "sparse_Nadvance": int(s08["na"]),
            "sparse_FAR": s08["fm"],
            "sparse_Miss": s08["err"] / s08["ninc"],
        },
    ]
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)

    report = (
        "B1 occupancy/mixed-τ policies (T-KT=simplekt CSV; ASSISTments fold 0 seed 42)\n"
        f"A global τ=0.7: pop Nadv={int(a_na)} FAR={a_far:.5f} Miss={a_miss:.5f}; "
        f"sparse Nadv={int(s07['na'])} FAR={s07['fm']:.5f}\n"
        f"B Reliable-only: pop Nadv={int(b_na)} FAR={b_far:.5f} Miss={b_miss:.5f}; "
        f"sparse Nadv=0 FAR=NA Miss=0\n"
        f"C sparse τ=0.8 else 0.7: pop Nadv={int(c_na)} FAR={c_far:.5f} Miss={c_miss:.5f}; "
        f"sparse Nadv={int(s08['na'])} FAR={s08['fm']:.5f}\n"
        "Source: analysis/direction_c/threshold_rates.csv. No retrain.\n"
    )
    OUT_TXT.write_text(report, encoding="utf-8")

    OUT_TEX.write_text(
        r"""\begin{table}[htbp]
\caption{Simulated practice-gate policies on frozen T-KT probabilities, ASSISTments 2012 learner-based fold 0 (seed 42). Same $p$ as Table 5 / Table S3; CSV model name \texttt{simplekt} is the local T-KT baseline, not published SimpleKT. Policy A: global $\tau=0.7$. Policy B: advance only if occupancy is Reliable (dense+medium). Policy C: $\tau=0.8$ on the sparse stratum and $\tau=0.7$ elsewhere. Population FAR/Miss use all test events ($N=534{,}150$). Sparse FAR is undefined when $N_{\mathrm{advance}}=0$. Not a classroom trial.}
\label{tab:s4_occupancy_policies}
\centering
\small
\begin{tabular}{lcccccc}
\toprule
Policy & Pop. $N_{\mathrm{advance}}$ & Pop. FAR & Pop. Miss & Sparse $N_{\mathrm{advance}}$ & Sparse FAR & Sparse Miss \\
\midrule
A global $\tau=0.7$ & 287{,}164 & 0.197 & 0.350 & 235 & 0.268 & 0.320 \\
B Reliable-only & 286{,}921 & 0.197 & 0.350 & 0 & --- & 0 \\
C sparse $\tau=0.8$ & 287{,}147 & 0.197 & 0.350 & 218 & 0.261 & 0.289 \\
\bottomrule
\end{tabular}
\end{table}
""",
        encoding="utf-8",
    )
    print(report)


if __name__ == "__main__":
    main()
