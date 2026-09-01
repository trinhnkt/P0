#!/usr/bin/env python3
"""
A7: Controlled fault injection for L8 predictive-sanity validation.

Reads existing temporal prediction CSVs. Never overwrites them.
Faults are applied to in-memory copies only.

This is a VALIDATION experiment, not a pre-registered primary analysis.
Detection thresholds are those already used by L8 in Appendix F
(near-random warm AUC; collapse vs IRT; non-positive association).
They are not tuned on the injected-fault outcomes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(".")
PRED_DIR = ROOT / "results" / "predictions"
STRATA_CSV = ROOT / "results" / "tables" / "kc_strata.csv"
OUT_DIR = ROOT / "analysis"
FIG_DIR = ROOT / "REV_REVIEWER_CALIBRATION_v1" / "figures"
OUT_DIR.mkdir(exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = ["assist2012", "junyi", "xes3g5m"]
DS_LABEL = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}
MODELS = ["dkt", "simplekt"]
SEED = 42
PARTIAL_RATES = (0.01, 0.05, 0.10, 0.25, 0.50)

# ---------------------------------------------------------------------------
# Pre-specified L8 detection rule (Appendix F). Not tuned on F1–F6.
# ---------------------------------------------------------------------------
NEAR_RANDOM_AUC = 0.55
IRT_MARGIN = 0.05
# Any material disagreement between exported y and official test-split y
# on the same stable_id. Pre-specified in the L8 signal list; not tuned on F1–F6.
# Elevation over the same file's clean-pipeline identity mismatch.
# Uses the correct pipeline as the reference distribution (not tuned on F1–F6).
IDENTITY_ELEVATION = 0.01
DETECTION_RULE = (
    "warm_AUC < 0.55 OR warm_AUC + 0.05 < IRT_warm_AUC "
    "OR pearson(p,y) <= 0 OR (E[p|y=1]-E[p|y=0]) <= 0 "
    "OR identity_mismatch_rate > clean_identity_mismatch + 0.01"
)


def find_pred_path(dataset: str, model: str) -> Path | None:
    for name in (
        f"{dataset}_temporal_{model}_seed{SEED}_predictions_rerun.csv",
        f"{dataset}_temporal_{model}_seed{SEED}.csv",
    ):
        p = PRED_DIR / name
        if p.exists():
            return p
    return None


def stable_id(df: pd.DataFrame) -> pd.Series:
    return (
        df["user_id"].astype(str)
        + "|"
        + df["item_id"].astype(str)
        + "|"
        + df["kc_id"].astype(str)
        + "|"
        + df["timestamp"].astype(str)
    )


def load_pred(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        usecols=["user_id", "item_id", "kc_id", "timestamp", "y_true", "p_pred"],
    )
    df["kc_id"] = df["kc_id"].astype(str)
    df["y_true"] = pd.to_numeric(df["y_true"], errors="coerce")
    df["p_pred"] = pd.to_numeric(df["p_pred"], errors="coerce")
    df = df.dropna(subset=["y_true", "p_pred"]).copy()
    df["stable_id"] = stable_id(df)
    return df


def warm_kc_set(strata: pd.DataFrame, dataset: str) -> set[str]:
    sub = strata[
        (strata["dataset"] == dataset)
        & (strata["split"] == "temporal")
        & (strata["fold"] == 0)
    ]
    return set(sub.loc[sub["train_freq"] > 10, "kc_id"].astype(str))


def auc_safe(y, p) -> float:
    y = np.asarray(y)
    p = np.asarray(p)
    if y.size < 20 or len(np.unique(y)) < 2:
        return float("nan")
    try:
        return float(roc_auc_score(y, p))
    except Exception:
        return float("nan")


def load_test_labels(dataset: str) -> pd.Series:
    path = ROOT / "data" / "processed" / dataset / "splits" / "temporal" / "fold_0" / "test.csv"
    test = pd.read_csv(
        path, usecols=["user_id", "item_id", "kc_id", "timestamp", "correct"]
    )
    test["kc_id"] = test["kc_id"].astype(str)
    test["sid"] = stable_id(test)
    return test.drop_duplicates("sid").set_index("sid")["correct"]


def signals(df: pd.DataFrame, warm_kcs: set[str], test_y: pd.Series | None = None) -> dict:
    warm = df[df["kc_id"].isin(warm_kcs)]
    y = warm["y_true"].to_numpy()
    p = np.clip(warm["p_pred"].to_numpy(), 1e-7, 1 - 1e-7)
    auc = auc_safe(y, p)
    if y.size and y.std() > 0 and p.std() > 0:
        corr = float(np.corrcoef(p, y)[0, 1])
    else:
        corr = float("nan")
    pos = p[y == 1]
    neg = p[y == 0]
    gap = (
        float(pos.mean() - neg.mean())
        if len(pos) and len(neg)
        else float("nan")
    )
    missing = float(
        df[["user_id", "item_id", "kc_id", "timestamp"]].isna().any(axis=1).mean()
    )
    dup = float(df["stable_id"].duplicated().mean()) if len(df) else 1.0
    if test_y is not None and len(df):
        mapped = df["stable_id"].map(test_y)
        matched = mapped.notna()
        unmatched = float((~matched).mean())
        if matched.any():
            mismatch = float((mapped[matched].to_numpy() != df.loc[matched, "y_true"].to_numpy()).mean())
        else:
            mismatch = 1.0
    else:
        unmatched = float("nan")
        mismatch = float("nan")
    return {
        "n_warm": int(len(warm)),
        "AUC": auc,
        "correlation": corr,
        "conditional_mean_gap": gap,
        "frac_missing_ids": missing,
        "frac_duplicate_ids": dup,
        "frac_unmatched_ids": unmatched,
        "identity_mismatch_rate": mismatch,
    }


def detected(sig: dict, irt_warm_auc: float, clean_identity: float = 0.0) -> bool:
    auc = sig["AUC"]
    corr = sig["correlation"]
    gap = sig["conditional_mean_gap"]
    ident = sig.get("identity_mismatch_rate", float("nan"))
    flags = []
    if pd.notna(auc) and auc < NEAR_RANDOM_AUC:
        flags.append("near_random_auc")
    if pd.notna(auc) and pd.notna(irt_warm_auc) and (auc + IRT_MARGIN) < irt_warm_auc:
        flags.append("collapse_vs_irt")
    if pd.notna(corr) and corr <= 0:
        flags.append("nonpositive_corr")
    if pd.notna(gap) and gap <= 0:
        flags.append("nonpositive_gap")
    if pd.notna(ident) and pd.notna(clean_identity) and (ident > clean_identity + IDENTITY_ELEVATION):
        flags.append("identity_mismatch")
    return bool(flags), "|".join(flags) if flags else "none"


def sort_seq(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(
        ["user_id", "timestamp", "item_id", "kc_id"], kind="mergesort"
    ).reset_index(drop=True)


def apply_fault(df: pd.DataFrame, fault: str, rate: float, rng: np.random.Generator) -> pd.DataFrame:
    """Return an in-memory copy. Original df is never modified."""
    out = df.copy()
    if fault == "clean":
        return out

    if fault in {"F1_label_shift_plus1", "F2_label_shift_minus1", "F3_pred_shift"}:
        out = sort_seq(out)
        g = out.groupby("user_id", sort=False)
        if fault == "F1_label_shift_plus1":
            out["y_true"] = g["y_true"].shift(-1)
        elif fault == "F2_label_shift_minus1":
            out["y_true"] = g["y_true"].shift(1)
        else:
            out["p_pred"] = g["p_pred"].shift(-1)
        out = out.dropna(subset=["y_true", "p_pred"]).reset_index(drop=True)
        return out

    if fault == "F4_within_learner_shuffle":
        out = sort_seq(out)
        out["p_pred"] = out.groupby("user_id", sort=False)["p_pred"].transform(
            lambda s: rng.permutation(s.to_numpy())
        )
        return out

    if fault == "F5_row_index_mismatch":
        alt = out.sort_values(
            ["kc_id", "item_id", "user_id"], kind="mergesort"
        ).reset_index(drop=True)
        out = out.reset_index(drop=True)
        out["p_pred"] = alt["p_pred"].to_numpy()
        return out

    if fault == "F6_partial_mismatch":
        n = len(out)
        k = int(round(rate * n))
        if k <= 0:
            return out
        idx = rng.choice(n, size=k, replace=False)
        src = rng.choice(n, size=k, replace=True)
        vals = out["p_pred"].to_numpy()
        vals = vals.copy()
        vals[idx] = out["p_pred"].to_numpy()[src]
        out = out.copy()
        out["p_pred"] = vals
        return out

    raise ValueError(fault)


def row_record(dataset, model, fault, rate, sig, is_det, fired, irt_auc):
    return {
        "dataset": DS_LABEL[dataset],
        "model": model,
        "fault_type": fault,
        "corruption_rate": rate,
        "n_warm": sig["n_warm"],
        "AUC": None if pd.isna(sig["AUC"]) else round(sig["AUC"], 6),
        "correlation": None if pd.isna(sig["correlation"]) else round(sig["correlation"], 6),
        "conditional_mean_gap": None if pd.isna(sig["conditional_mean_gap"]) else round(sig["conditional_mean_gap"], 6),
        "frac_missing_ids": round(sig["frac_missing_ids"], 6),
        "frac_duplicate_ids": round(sig["frac_duplicate_ids"], 6),
        "frac_unmatched_ids": None if pd.isna(sig["frac_unmatched_ids"]) else round(sig["frac_unmatched_ids"], 6),
        "identity_mismatch_rate": None if pd.isna(sig["identity_mismatch_rate"]) else round(sig["identity_mismatch_rate"], 6),
        "irt_warm_auc": None if pd.isna(irt_auc) else round(irt_auc, 6),
        "detected": bool(is_det),
        "fired_signals": fired,
        "detection_rule": DETECTION_RULE,
    }


def write_latex(results: pd.DataFrame):
    inj = results[results["fault_type"] != "clean"]
    clean = results[results["fault_type"] == "clean"]
    n_fp = int(clean["detected"].sum())
    n_clean = len(clean)
    n_det = int(inj["detected"].sum())
    n_inj = len(inj)
    rate = n_det / n_inj if n_inj else float("nan")

    full = inj[inj["fault_type"] != "F6_partial_mismatch"]
    partial = inj[inj["fault_type"] == "F6_partial_mismatch"]

    def det_rate(df):
        if df.empty:
            return "—"
        return f"{100 * df['detected'].mean():.0f}\\% ({int(df['detected'].sum())}/{len(df)})"

    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Controlled fault-injection validation of channel L8 (temporal warm cohort). "
        r"This is a validation experiment, not a pre-registered primary analysis. "
        r"Detection uses the Appendix~\ref{app:alignment} signals plus identity consistency "
        r"against official test-split labels on a stable instance id: warm AUC $< 0.55$, "
        r"or warm AUC more than $0.05$ below the clean IRT warm-cohort reference, "
        r"or non-positive $\mathrm{corr}(p,y)$ / conditional-mean gap, "
        r"or exported $y$ elevated more than $1$ percentage point above the same file's "
        r"clean-pipeline identity-mismatch rate. "
        r"Thresholds were not tuned on the injected faults. "
        r"L8 is sensitive to some of the tested alignment-fault classes; it is not claimed to detect all bugs.}"
        r"\label{tab:l8_fault_injection}",
        r"\centering",
        r"\small",
        r"\begin{tabular}{lc}",
        r"\toprule",
        r"\textbf{Condition} & \textbf{Detection rate} \\",
        r"\midrule",
        rf"Clean pipeline (false-positive check) & {n_fp}/{n_clean} \\",
        rf"F1 label shift $+1$ & {det_rate(full[full['fault_type']=='F1_label_shift_plus1'])} \\",
        rf"F2 label shift $-1$ & {det_rate(full[full['fault_type']=='F2_label_shift_minus1'])} \\",
        rf"F3 prediction shift & {det_rate(full[full['fault_type']=='F3_pred_shift'])} \\",
        rf"F4 within-learner shuffle & {det_rate(full[full['fault_type']=='F4_within_learner_shuffle'])} \\",
        rf"F5 row-index mismatch & {det_rate(full[full['fault_type']=='F5_row_index_mismatch'])} \\",
        r"\midrule",
        rf"F6 partial mismatch $1\%$ & {det_rate(partial[partial['corruption_rate']==0.01])} \\",
        rf"F6 partial mismatch $5\%$ & {det_rate(partial[partial['corruption_rate']==0.05])} \\",
        rf"F6 partial mismatch $10\%$ & {det_rate(partial[partial['corruption_rate']==0.10])} \\",
        rf"F6 partial mismatch $25\%$ & {det_rate(partial[partial['corruption_rate']==0.25])} \\",
        rf"F6 partial mismatch $50\%$ & {det_rate(partial[partial['corruption_rate']==0.50])} \\",
        r"\midrule",
        rf"All injected faults & {n_det}/{n_inj} ({100*rate:.1f}\%) \\",
        r"\bottomrule",
        r"\end{tabular}",
        r"",
        r"\vspace{1ex}",
        r"{\scriptsize \textbf{Note:} Counts pool DKT and SimpleKT $\times$ three datasets "
        r"(six files). Original prediction CSVs are not modified. Adjacent-timestep "
        r"prediction shifts (F3) often retain warm AUC because learner sequences are "
        r"autocorrelated; L8 as specified does not treat that residual association as a failure.\par}",
        r"\end{table}",
        r"",
    ]
    tex = "\n".join(lines)
    (OUT_DIR / "table_a7_l8_fault_injection.tex").write_text(tex, encoding="utf-8")
    rev = ROOT / "REV_REVIEWER_CALIBRATION_v1" / "tables" / "table_13_l8_fault_injection.tex"
    rev.write_text(tex, encoding="utf-8")
    print(f"Saved {rev}")
    return rate, n_det, n_inj, n_fp, n_clean


def write_figure(results: pd.DataFrame):
    import matplotlib.pyplot as plt

    partial = results[results["fault_type"] == "F6_partial_mismatch"]
    if partial.empty:
        return
    curve = (
        partial.groupby("corruption_rate")["detected"]
        .mean()
        .reset_index()
        .sort_values("corruption_rate")
    )
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    ax.plot(
        100 * curve["corruption_rate"],
        100 * curve["detected"],
        marker="o",
        color="#1f4e79",
        linewidth=1.6,
    )
    ax.set_xlabel("F6 corruption rate (% of rows)")
    ax.set_ylabel("L8 detection rate (%)")
    ax.set_title("L8 detection vs partial mismatch (F6)")
    ax.set_ylim(-5, 105)
    ax.set_xlim(0, 52)
    ax.grid(True, linewidth=0.4, alpha=0.6)
    fig.tight_layout()
    for dest in (
        OUT_DIR / "l8_fault_injection_detection_curve.pdf",
        FIG_DIR / "l8_fault_injection_detection_curve.pdf",
    ):
        fig.savefig(dest, bbox_inches="tight")
        print(f"Saved {dest}")
    plt.close(fig)


def write_summary(results: pd.DataFrame):
    inj = results[results["fault_type"] != "clean"]
    summary = {
        "n_injected": int(len(inj)),
        "n_detected": int(inj["detected"].sum()),
        "detection_rate": float(inj["detected"].mean()) if len(inj) else float("nan"),
        "clean_false_positives": int(results.loc[results["fault_type"] == "clean", "detected"].sum()),
        "n_clean": int((results["fault_type"] == "clean").sum()),
        "detection_rule": DETECTION_RULE,
        "note": "validation experiment; thresholds not tuned on injected faults",
    }
    pd.DataFrame([summary]).to_csv(OUT_DIR / "l8_fault_injection_summary.csv", index=False)
    print(summary)
    return summary


def relabel_from_csv(path: Path) -> pd.DataFrame:
    """Recompute detected/fired_signals from stored signals using the current rule."""
    results = pd.read_csv(path)
    clean_id = (
        results[results["fault_type"] == "clean"]
        .set_index(["dataset", "model"])["identity_mismatch_rate"]
    )

    fired_list = []
    det_list = []
    for _, row in results.iterrows():
        key = (row["dataset"], row["model"])
        base = float(clean_id.loc[key]) if key in clean_id.index else 0.0
        sig = {
            "AUC": row["AUC"],
            "correlation": row["correlation"],
            "conditional_mean_gap": row["conditional_mean_gap"],
            "identity_mismatch_rate": row["identity_mismatch_rate"],
        }
        is_det, fired = detected(sig, row["irt_warm_auc"], base)
        fired_list.append(fired)
        det_list.append(is_det)
    results["fired_signals"] = fired_list
    results["detected"] = det_list
    results["detection_rule"] = DETECTION_RULE
    results.to_csv(path, index=False)
    print(f"Relabeled {path}")
    return results


def main():
    strata = pd.read_csv(STRATA_CSV)
    strata = strata[strata["dataset"].isin(DATASETS)]
    records = []

    for ds in DATASETS:
        warm = warm_kc_set(strata, ds)
        irt_path = find_pred_path(ds, "irt_1pl")
        if irt_path is None:
            print(f"SKIP IRT missing: {ds}")
            irt_auc = float("nan")
        else:
            print(f"Loading IRT reference: {irt_path}")
            irt_df = load_pred(irt_path)
            irt_auc = signals(irt_df, warm, None)["AUC"]
            print(f"  IRT warm AUC = {irt_auc:.4f}")
            del irt_df

        print(f"Loading official test labels: {ds}")
        test_y = load_test_labels(ds)

        for model in MODELS:
            path = find_pred_path(ds, model)
            if path is None:
                print(f"SKIP missing {ds} {model}")
                continue
            print(f"Loading {path} (read-only)")
            clean = load_pred(path)
            rng = np.random.default_rng(2026)

            jobs = [("clean", 0.0)]
            for f in (
                "F1_label_shift_plus1",
                "F2_label_shift_minus1",
                "F3_pred_shift",
                "F4_within_learner_shuffle",
                "F5_row_index_mismatch",
            ):
                jobs.append((f, 1.0))
            for r in PARTIAL_RATES:
                jobs.append(("F6_partial_mismatch", r))

            clean_identity = 0.0
            for fault, rate in jobs:
                inj = apply_fault(clean, fault, rate, rng)
                sig = signals(inj, warm, test_y)
                if fault == "clean":
                    clean_identity = float(sig.get("identity_mismatch_rate") or 0.0)
                is_det, fired = detected(sig, irt_auc, clean_identity)
                rec = row_record(ds, model, fault, rate, sig, is_det, fired, irt_auc)
                records.append(rec)
                print(
                    f"  {fault} r={rate:.2f} AUC={sig['AUC']:.4f} "
                    f"corr={sig['correlation']:.4f} det={is_det} [{fired}]"
                )
                del inj

            del clean
        del test_y

    results = pd.DataFrame(records)
    out_csv = OUT_DIR / "l8_fault_injection_results.csv"
    results.to_csv(out_csv, index=False)
    print(f"\nSaved {out_csv}")

    write_summary(results)
    write_latex(results)
    write_figure(results)
    print("A7 complete. Original prediction CSVs were not modified.")


if __name__ == "__main__":
    import sys

    if "--relabel-only" in sys.argv:
        out_csv = OUT_DIR / "l8_fault_injection_results.csv"
        results = relabel_from_csv(out_csv)
        write_summary(results)
        write_latex(results)
        write_figure(results)
    else:
        main()
