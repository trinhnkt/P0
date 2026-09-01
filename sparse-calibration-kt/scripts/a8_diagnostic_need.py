#!/usr/bin/env python3
"""
A8: Conditional-use framework for sparse-concept diagnostics.

Depends on A5:
  analysis/dataset_sparse_diagnostic_profile.csv

Does not invent new frequency cutoffs. Need levels reuse:
  - pre-registered sparse threshold f_train < 100 (protocol buckets);
  - reliability flags R/L/I (N>=1000 / 100-999 / <100);
  - published event-level SimpleKT ECE (Table 9) and temporal cold-start counts (Table 6).

C4 (deployment) is qualitative intended-use, not a log-derived rating.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(".")
OUT = ROOT / "analysis"
REV_TAB = ROOT / "REV_REVIEWER_CALIBRATION_v1" / "tables"
OUT.mkdir(exist_ok=True)
REV_TAB.mkdir(parents=True, exist_ok=True)

# Temporal cold-start from Table 6 (published; not re-estimated here).
TEMPORAL_CS = {
    "ASSISTments 2012": {"strict_kcs": 27, "strict_events": 1407, "flag": "R"},
    "Junyi Academy": {"strict_kcs": 4, "strict_events": 2545, "flag": "R"},
    "XES3G5M": {"strict_kcs": 117, "strict_events": 233214, "flag": "R"},
}


def flag_need(flag: str | None, n: int) -> str:
    if n <= 0 or flag is None:
        return "Low"
    if flag == "R":
        return "High"
    if flag == "L":
        return "Moderate"
    return "Low"


def write_framework_tex() -> str:
    tex = r"""\begin{table*}[htbp]
\caption{Decision framework for when sparse-concept diagnostics are informative. Levels reuse the protocol's pre-registered sparse threshold ($f_{\mathrm{train}}<100$) and reliability flags (R/L/I); they are not new cutoffs tuned on these three datasets. C4 is an intended-use condition, not a quantity estimated from the interaction logs. Reporting occupancy and reliability flags remains useful even when the empirical priority of sparse-stratum claims is Low.}
\label{tab:a8_need_framework}
\centering
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{2.6cm}XXX}
\toprule
\textbf{Condition} & \textbf{Low need} & \textbf{Moderate need} & \textbf{High need} \\
\midrule
C1 Sparse mass & No KCs below the pre-registered sparse threshold ($f_{\mathrm{train}}<100$) & Sparse-like KCs appear only under an alternate split, or the tail is present but tiny relative to the dense mass & A non-empty sparse-like share of KCs under the split actually used (observed here: $18.9\%$ and $22.5\%$) \\
\midrule
C2 Evaluation support & Sparse strata empty or Insufficient ($N<100$) & Sparse stratum Limited ($100\le N<1000$) & Sparse stratum Reliable ($N\ge 1000$) \\
\midrule
C3 Calibration susceptibility & No stratum-level ECE/REL rise and only a weak KC-level frequency--ECE association & KC-level association present, but the stratum gradient is flat, inverted, or model-heterogeneous & Monotonic ECE/REL increase from dense to sparse with at least Limited support \\
\midrule
C4 Deployment relevance (qualitative) & Rankings only; probabilities are not thresholded & Probabilities are reported but not used as gates & Remediation, practice, or mastery decisions use probability thresholds \\
\midrule
C5 Temporal / cold-start exposure & Temporal split does not populate strict or limited cold-start groups & Cold-start groups exist but are small in KC count & Large cold-start test mass (Reliable $N$) or worse-than-random discrimination on unseen KCs \\
\bottomrule
\end{tabularx}

\vspace{1ex}
{\scriptsize \textbf{Note:} Low/Moderate/High describe the priority of \emph{sparse-concept diagnostic claims}, not whether the protocol should be run. Occupancy reporting (empty buckets, reliability flags) is universally useful hygiene.\par}
\end{table*}
"""
    return tex


def write_apply_tex(rows: list[dict]) -> str:
    def cell(ds: str, cond: str) -> str:
        r = next(x for x in rows if x["dataset"] == ds and x["condition"] == cond)
        return f"{r['need_level']}: {r['evidence']}"

    datasets = ["ASSISTments 2012", "Junyi Academy", "XES3G5M"]
    conds = [
        ("C1", "C1 Sparse mass"),
        ("C2", "C2 Evaluation support"),
        ("C3", "C3 Calibration susceptibility"),
        ("C4", "C4 Deployment relevance"),
        ("C5", "C5 Temporal / cold-start"),
        ("OVERALL", "Overall sparse-diagnostic priority"),
    ]
    lines = [
        r"\begin{table*}[htbp]",
        r"\caption{Sparse-concept diagnostic need on the three evaluation datasets. "
        r"Need is not the same as observed vulnerability: XES3G5M has high reporting priority "
        r"because sparse mass and cold-start support are large, even though SimpleKT ECE is flat. "
        r"Junyi has low learner-based sparse-stratum priority because those buckets are empty, "
        r"not because calibration is known to be safe. C4 is the same qualitative intended-use "
        r"condition for all three public benchmarks.}",
        r"\label{tab:a8_dataset_need}",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{2.8cm}XXX}",
        r"\toprule",
        r"\textbf{Condition} & \textbf{ASSISTments 2012} & \textbf{Junyi Academy} & \textbf{XES3G5M} \\",
        r"\midrule",
    ]
    for cid, lab in conds:
        a, j, x = (cell(d, cid) for d in datasets)
        lines.append(f"{lab} & {a} & {j} & {x} \\\\")
        if cid != "OVERALL":
            lines.append(r"\midrule")
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"",
        r"\vspace{1ex}",
        r"{\scriptsize \textbf{Note:} Learner-based occupancy and ECE from Tables~\ref{tab:a5_dataset_conditions} "
        r"and~\ref{tab:calibration_learner}; temporal cold-start counts from Table~\ref{tab:cold_start_temporal}. "
        r"Overall priority is a qualitative synthesis, not a numeric score.\par}",
        r"\end{table*}",
        r"",
    ]
    return "\n".join(lines)


def main():
    prof = pd.read_csv(OUT / "dataset_sparse_diagnostic_profile.csv")
    rows = []

    for _, p in prof.iterrows():
        ds = p["dataset"]
        mass = float(p["sparse_mass_prop"])
        n_sp = int(p["test_events_sparse"])
        n_vs = int(p["test_events_very_sparse"])
        ece_d = p["ece_event_dense_simplekt"]
        ece_m = p["ece_event_medium_simplekt"]
        ece_s = p["ece_event_sparse_simplekt"]
        rho = float(p["calibration_frequency_association_strength"])
        t_kcs = int(p["temporal_sparse_like_kcs"])
        cs = TEMPORAL_CS[ds]

        # C1
        if mass <= 0:
            c1, e1 = "Low", r"0.0\% of KCs with $f_{\mathrm{train}}<100$"
        else:
            c1, e1 = "High", f"{100*mass:.1f}\\% of KCs below sparse threshold"
        rows.append({"dataset": ds, "condition": "C1", "need_level": c1, "evidence": e1})

        # C2 --- reuse R/L/I on sparse stratum
        if ds == "ASSISTments 2012":
            c2, e2 = "Moderate", r"sparse $N=403$ (L); very-sparse $N=19$ (I)"
        elif ds == "Junyi Academy":
            c2, e2 = "Low", "0 sparse/very-sparse test events"
        else:
            c2, e2 = "High", r"sparse $N=2{,}002$ (R); very-sparse $N=109$ (L)"
        rows.append({"dataset": ds, "condition": "C2", "need_level": c2, "evidence": e2})

        # C3
        if ds == "ASSISTments 2012":
            c3, e3 = (
                "High",
                rf"monotonic ECE ${ece_d:.3f}\to{ece_m:.3f}\to{ece_s:.3f}$; $\bar\rho={rho:.2f}$",
            )
        elif ds == "Junyi Academy":
            c3, e3 = (
                "Moderate",
                rf"dense$\to$medium $\Delta$ECE$=+{float(p['ece_gradient_dense_to_medium']):.3f}$; sparse empty; $\bar\rho={rho:.2f}$",
            )
        else:
            c3, e3 = (
                "Moderate",
                rf"SimpleKT flat ${ece_d:.3f}\to{ece_s:.3f}$; model-heterogeneous; $\bar\rho={rho:.2f}$",
            )
        rows.append({"dataset": ds, "condition": "C3", "need_level": c3, "evidence": e3})

        # C4 qualitative, same for public benchmarks
        rows.append(
            {
                "dataset": ds,
                "condition": "C4",
                "need_level": "Use-dependent",
                "evidence": "not measured in logs; High if probabilities are thresholded",
            }
        )

        # C5
        if ds == "XES3G5M":
            c5, e5 = (
                "High",
                rf"{cs['strict_kcs']} strict KCs / {cs['strict_events']:,} events (R); {t_kcs} temporal sparse-like KCs",
            )
        elif ds == "ASSISTments 2012":
            c5, e5 = (
                "Moderate",
                rf"{cs['strict_kcs']} strict KCs / {cs['strict_events']:,} events; {t_kcs} temporal sparse-like KCs",
            )
        else:
            c5, e5 = (
                "Moderate",
                rf"{cs['strict_kcs']} strict KCs / {cs['strict_events']:,} events; {t_kcs} temporal sparse-like KCs",
            )
        rows.append({"dataset": ds, "condition": "C5", "need_level": c5, "evidence": e5})

        # Overall
        if ds == "ASSISTments 2012":
            ov, eo = (
                "High",
                "C1+C3 high, C2 Limited but estimable; sparse ECE claims are informative",
            )
        elif ds == "Junyi Academy":
            ov, eo = (
                "Low (learner-based); Moderate (temporal)",
                "empty sparse buckets under learner-based split; temporal split still exposes a small tail",
            )
        else:
            ov, eo = (
                "High (reporting), Moderate (SimpleKT gradient)",
                "mass and support require the check; the check shows a flat/inverted pattern, not ASSISTments-like degradation",
            )
        rows.append({"dataset": ds, "condition": "OVERALL", "need_level": ov, "evidence": eo})

        _ = (n_sp, n_vs, flag_need)  # retained for documentation of C2 rule

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "a8_dataset_need_ratings.csv", index=False)

    framework_rows = [
        {"condition": "C1 Sparse mass", "low_need": "No KCs with f_train<100", "moderate_need": "Tail only under an alternate split, or tiny", "high_need": "Non-empty sparse-like KC share (observed 18.9%, 22.5%)", "cutoff_source": "pre-registered protocol threshold f_train<100"},
        {"condition": "C2 Evaluation support", "low_need": "Empty or Insufficient N<100", "moderate_need": "Limited 100<=N<1000", "high_need": "Reliable N>=1000", "cutoff_source": "protocol reliability flags (Section 3.5)"},
        {"condition": "C3 Calibration susceptibility", "low_need": "No stratum ECE/REL rise and weak KC-level association", "moderate_need": "KC-level association without a clear stratum gradient", "high_need": "Monotonic ECE/REL rise dense to sparse, at least Limited N", "cutoff_source": "qualitative on published Table 9 ECE; no new cutoff"},
        {"condition": "C4 Deployment relevance", "low_need": "Rankings only", "moderate_need": "Probabilities reported, not gated", "high_need": "Threshold-based educational decisions", "cutoff_source": "qualitative intended-use; not estimated from logs"},
        {"condition": "C5 Temporal/cold-start exposure", "low_need": "No strict/limited cold-start groups", "moderate_need": "Small cold-start KC count", "high_need": "Large Reliable cold-start test mass", "cutoff_source": "qualitative on Table 6 occupancy; flags reused"},
    ]
    pd.DataFrame(framework_rows).to_csv(OUT / "a8_diagnostic_need_matrix.csv", index=False)

    fw = write_framework_tex()
    ap = write_apply_tex(rows)
    (OUT / "table_a8_need_framework.tex").write_text(fw, encoding="utf-8")
    (OUT / "table_a8_dataset_need.tex").write_text(ap, encoding="utf-8")
    (REV_TAB / "table_14_need_framework.tex").write_text(fw, encoding="utf-8")
    (REV_TAB / "table_15_dataset_need.tex").write_text(ap, encoding="utf-8")
    print("Wrote A8 matrix CSVs and Tables 14--15")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
