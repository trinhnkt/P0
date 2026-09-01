#!/usr/bin/env python3
"""
A5: Dataset diagnostic profile for sparse-KC calibration vulnerability.

Depends on A4 outputs:
  analysis/kc_characteristics.csv
  analysis/spearman_correlations.csv
  analysis/matched_analysis.csv
  analysis/calibration_gradient_summary.csv
  results/tables/kc_strata.csv

Produces:
  analysis/dataset_sparse_diagnostic_profile.csv
  analysis/table_a5_dataset_conditions.tex
  analysis/a5_condition_verdicts.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(".")
OUT_DIR = ROOT / "analysis"
OUT_DIR.mkdir(exist_ok=True)

DATASETS = ["assist2012", "junyi", "xes3g5m"]
LABELS = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}
SPLIT = "learner_based"
FOLD = 0
BUCKETS = ["strict_cold_start", "very_sparse", "sparse", "medium", "dense"]

# Event-level ECE from Table 9 (SimpleKT, learner-based) — official paper metric.
# Used for the "observed calibration gradient" row so the table matches the manuscript.
EVENT_ECE_SIMPLEKT = {
    "assist2012": {
        "dense": 0.1131, "medium": 0.1578, "sparse": 0.2254, "very_sparse": 0.2464,
        "events": {"dense": 523395, "medium": 6211, "sparse": 403, "very_sparse": 19, "strict_cold_start": 4},
        "flags": {"dense": "R", "medium": "R", "sparse": "L", "very_sparse": "I"},
    },
    "junyi": {
        "dense": 0.0788, "medium": 0.1100, "sparse": np.nan, "very_sparse": np.nan,
        "events": {"dense": 3235313, "medium": 2689, "sparse": 0, "very_sparse": 0, "strict_cold_start": 0},
        "flags": {"dense": "R", "medium": "R", "sparse": None, "very_sparse": None},
    },
    "xes3g5m": {
        "dense": 0.1146, "medium": 0.1117, "sparse": 0.1244, "very_sparse": 0.1951,
        "events": {"dense": 1268748, "medium": 13082, "sparse": 2002, "very_sparse": 109, "strict_cold_start": 2},
        "flags": {"dense": "R", "medium": "R", "sparse": "R", "very_sparse": "L"},
    },
}


def iqr(s):
    s = s.dropna()
    if s.empty:
        return np.nan
    return float(s.quantile(0.75) - s.quantile(0.25))


def spearman_safe(x, y, min_n=10):
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    if len(x) < min_n:
        return np.nan, np.nan, len(x)
    rho, p = stats.spearmanr(x, y)
    return float(rho), float(p), int(len(x))


def prop_bucket(counts, name, total):
    if total == 0:
        return 0.0
    return float(counts.get(name, 0)) / total


def main():
    strata = pd.read_csv(ROOT / "results" / "tables" / "kc_strata.csv")
    strata = strata[strata["dataset"].isin(DATASETS)]
    kc = pd.read_csv(OUT_DIR / "kc_characteristics.csv")
    spearman = pd.read_csv(OUT_DIR / "spearman_correlations.csv")
    matched = pd.read_csv(OUT_DIR / "matched_analysis.csv")
    cal = pd.read_csv(OUT_DIR / "calibration_gradient_summary.csv")

    rows = []
    verdicts = []

    for ds in DATASETS:
        lb = strata[
            (strata["dataset"] == ds)
            & (strata["split"] == SPLIT)
            & (strata["fold"] == FOLD)
        ].copy()
        total_kcs = int(len(lb))
        counts = lb["bucket"].value_counts()

        p_strict = prop_bucket(counts, "strict_cold_start", total_kcs)
        p_vs = prop_bucket(counts, "very_sparse", total_kcs)
        p_sp = prop_bucket(counts, "sparse", total_kcs)
        p_med = prop_bucket(counts, "medium", total_kcs)
        p_den = prop_bucket(counts, "dense", total_kcs)
        sparse_mass = p_strict + p_vs + p_sp

        freq = lb["train_freq"].astype(float)
        freq_pos = freq[freq > 0]
        median_freq = float(freq_pos.median()) if len(freq_pos) else np.nan
        freq_iqr = iqr(freq_pos)
        train_sum = float(freq.sum())
        interaction_concentration_top1 = (
            float(freq.max() / train_sum) if train_sum > 0 else np.nan
        )
        n_top10 = max(1, int(np.ceil(0.10 * total_kcs)))
        interaction_concentration_top10pct = (
            float(freq.nlargest(n_top10).sum() / train_sum) if train_sum > 0 else np.nan
        )
        shares = (freq / train_sum) if train_sum > 0 else freq * 0
        herfindahl = float((shares ** 2).sum()) if train_sum > 0 else np.nan

        kc_sub = kc[
            (kc["dataset"] == ds)
            & (kc["split"] == SPLIT)
            & (kc["model"] == "simplekt")
        ].copy()

        med_diff = float(kc_sub["difficulty_proxy"].median())
        iqr_diff = iqr(kc_sub["difficulty_proxy"])
        med_items = float(kc_sub["n_train_items"].median())
        iqr_items = iqr(kc_sub["n_train_items"])
        med_learners = float(kc_sub["n_train_learners"].median())
        iqr_learners = iqr(kc_sub["n_train_learners"])
        med_pos = float(kc_sub["median_sequence_position_train"].median())
        iqr_pos = iqr(kc_sub["median_sequence_position_train"])

        rho_fd, p_fd, n_fd = spearman_safe(
            kc_sub["log_train_freq"], kc_sub["difficulty_proxy"]
        )
        rho_fp, p_fp, n_fp = spearman_safe(
            kc_sub["log_train_freq"], kc_sub["median_sequence_position_train"]
        )
        rho_fi, p_fi, n_fi = spearman_safe(
            kc_sub["log_train_freq"], kc_sub["n_train_items"]
        )

        # Items/KC imbalance: dense median vs sparse+very-sparse median.
        items_dense = kc_sub.loc[kc_sub["bucket"] == "dense", "n_train_items"]
        items_sparse = kc_sub.loc[
            kc_sub["bucket"].isin(["sparse", "very_sparse"]), "n_train_items"
        ]
        med_items_dense = float(items_dense.median()) if len(items_dense) else np.nan
        med_items_sparse = float(items_sparse.median()) if len(items_sparse) else np.nan
        item_imbalance_ratio = (
            med_items_dense / med_items_sparse
            if (pd.notna(med_items_dense) and pd.notna(med_items_sparse) and med_items_sparse > 0)
            else np.nan
        )

        # Test-event support from official Table-9 event counts (SimpleKT).
        ev = EVENT_ECE_SIMPLEKT[ds]["events"]
        ev_strict = ev.get("strict_cold_start", 0)
        ev_vs = ev.get("very_sparse", 0)
        ev_sp = ev.get("sparse", 0)
        ev_med = ev.get("medium", 0)
        ev_den = ev.get("dense", 0)
        ev_total = ev_strict + ev_vs + ev_sp + ev_med + ev_den
        ev_sparse_like = ev_strict + ev_vs + ev_sp
        pct_sparse_events = ev_sparse_like / ev_total if ev_total else 0.0

        # Temporal sparse activation (Junyi contrast).
        temp_sparse = strata[
            (strata["dataset"] == ds)
            & (strata["split"] == "temporal")
            & (strata["fold"] == FOLD)
            & (strata["bucket"].isin(["sparse", "very_sparse", "strict_cold_start"]))
        ]
        temporal_sparse_kcs = int(len(temp_sparse))

        ece_ev = EVENT_ECE_SIMPLEKT[ds]
        ece_d, ece_m, ece_s, ece_v = (
            ece_ev["dense"], ece_ev["medium"], ece_ev["sparse"], ece_ev["very_sparse"]
        )
        grad_dm = (ece_m - ece_d) if pd.notna(ece_m) and pd.notna(ece_d) else np.nan
        grad_ms = (ece_s - ece_m) if pd.notna(ece_s) and pd.notna(ece_m) else np.nan

        freq_ece = spearman[
            (spearman["dataset"] == ds)
            & (spearman["x"] == "log_train_freq")
            & (spearman["y"] == "ECE")
        ]
        assoc_rho = float(freq_ece["rho"].mean()) if len(freq_ece) else np.nan
        assoc_n_sig = int((freq_ece["sig"] != "").sum()) if len(freq_ece) else 0

        match_sub = matched[matched["dataset"] == ds]
        n_sig_m = int((match_sub["p_value"] < 0.05).sum()) if len(match_sub) else 0
        n_m = int(len(match_sub))

        # IRT event-level gradient (for model-heterogeneity note; Table 9).
        irt_cal = cal[
            (cal["Dataset"] == LABELS[ds])
            & (cal["Model"] == "IRT")
            & (cal["Split"] == "learner")
        ]
        irt_ece = {r["Stratum"]: r["ECE"] for _, r in irt_cal.iterrows()}

        rows.append({
            "dataset": LABELS[ds],
            "split": SPLIT,
            "total_kcs": total_kcs,
            "proportion_strict": round(p_strict, 4),
            "proportion_very_sparse": round(p_vs, 4),
            "proportion_sparse": round(p_sp, 4),
            "proportion_medium": round(p_med, 4),
            "proportion_dense": round(p_den, 4),
            "sparse_mass_prop": round(sparse_mass, 4),
            "interaction_concentration_top1": round(interaction_concentration_top1, 4),
            "interaction_concentration_top10pct": round(interaction_concentration_top10pct, 4),
            "interaction_herfindahl": round(herfindahl, 4),
            "median_train_frequency": round(median_freq, 1),
            "frequency_iqr": round(freq_iqr, 1),
            "kc_difficulty_median": round(med_diff, 4),
            "kc_difficulty_iqr": round(iqr_diff, 4),
            "items_per_kc_median": round(med_items, 2),
            "items_per_kc_iqr": round(iqr_items, 2),
            "items_per_kc_dense_median": None if pd.isna(med_items_dense) else round(med_items_dense, 2),
            "items_per_kc_sparse_median": None if pd.isna(med_items_sparse) else round(med_items_sparse, 2),
            "item_support_imbalance_ratio": None if pd.isna(item_imbalance_ratio) else round(item_imbalance_ratio, 2),
            "learners_per_kc_median": round(med_learners, 1),
            "learners_per_kc_iqr": round(iqr_learners, 1),
            "curriculum_position_median": round(med_pos, 4),
            "curriculum_position_iqr": round(iqr_pos, 4),
            "freq_difficulty_rho": None if pd.isna(rho_fd) else round(rho_fd, 4),
            "freq_difficulty_p": None if pd.isna(p_fd) else float(f"{p_fd:.4g}"),
            "freq_curriculum_rho": None if pd.isna(rho_fp) else round(rho_fp, 4),
            "freq_curriculum_p": None if pd.isna(p_fp) else float(f"{p_fp:.4g}"),
            "freq_items_rho": None if pd.isna(rho_fi) else round(rho_fi, 4),
            "freq_items_p": None if pd.isna(p_fi) else float(f"{p_fi:.4g}"),
            "strict_cold_start_kc_prop": round(p_strict, 4),
            "strict_cold_start_test_events": int(ev_strict),
            "strict_cold_start_event_share": round(ev_strict / ev_total, 6) if ev_total else 0.0,
            "test_events_strict": int(ev_strict),
            "test_events_very_sparse": int(ev_vs),
            "test_events_sparse": int(ev_sp),
            "test_events_medium": int(ev_med),
            "test_events_dense": int(ev_den),
            "test_events_sparse_like_total": int(ev_sparse_like),
            "test_event_share_sparse_like": round(pct_sparse_events, 6),
            "temporal_sparse_like_kcs": temporal_sparse_kcs,
            "ece_event_dense_simplekt": ece_d,
            "ece_event_medium_simplekt": ece_m,
            "ece_event_sparse_simplekt": None if pd.isna(ece_s) else ece_s,
            "ece_event_very_sparse_simplekt": None if pd.isna(ece_v) else ece_v,
            "ece_gradient_dense_to_medium": None if pd.isna(grad_dm) else round(grad_dm, 4),
            "ece_gradient_medium_to_sparse": None if pd.isna(grad_ms) else round(grad_ms, 4),
            "calibration_frequency_association_strength": round(assoc_rho, 4),
            "calibration_frequency_n_models_sig": f"{assoc_n_sig}/{len(freq_ece)}",
            "matched_sig_strata": f"{n_sig_m}/{n_m}",
            "irt_ece_dense": irt_ece.get("dense", np.nan),
            "irt_ece_sparse": irt_ece.get("sparse", np.nan),
            "coupling_n_kcs": n_fd,
        })

        # --- Condition verdicts (FINDING only; hypotheses stay in the manuscript) ---
        if sparse_mass >= 0.10:
            mass_v = f"Present ({sparse_mass:.1%} of KCs)"
        elif sparse_mass >= 0.02:
            mass_v = f"Limited ({sparse_mass:.1%} of KCs)"
        else:
            mass_v = f"Absent ({sparse_mass:.1%} of KCs)"

        flags = ece_ev["flags"]
        if ev_sp + ev_vs == 0:
            support_v = "Absent (0 sparse/very-sparse test events)"
        elif flags.get("sparse") == "R" or ev_sp >= 1000:
            support_v = (
                f"Present (sparse $N={ev_sp:,}$ {flags.get('sparse')}; "
                f"very-sparse $N={ev_vs:,}$ {flags.get('very_sparse')})"
            )
        elif flags.get("sparse") == "L" or ev_sp >= 100:
            support_v = (
                f"Partial (sparse $N={ev_sp:,}$ {flags.get('sparse')}; "
                f"very-sparse $N={ev_vs:,}$ {flags.get('very_sparse')})"
            )
        else:
            support_v = f"Insufficient (sparse $N={ev_sp:,}$; very-sparse $N={ev_vs:,}$)"

        if pd.isna(rho_fd):
            fd_v = "Not estimable"
        elif abs(rho_fd) < 0.15:
            direction = "opposite-signed" if rho_fd > 0 else "expected-signed"
            fd_v = f"Weak, {direction} ($\\rho={rho_fd:+.3f}$)"
        elif rho_fd < 0:
            fd_v = f"Present, expected dir.\\ ($\\rho={rho_fd:+.3f}$; sparse harder)"
        else:
            fd_v = f"Present, opposite dir.\\ ($\\rho={rho_fd:+.3f}$; sparse easier)"

        if pd.isna(rho_fp):
            cp_v = "Not estimable"
        elif abs(rho_fp) < 0.15:
            cp_v = f"Weak ($\\rho={rho_fp:+.3f}$)"
        else:
            cp_v = f"Present ($\\rho={rho_fp:+.3f}$)"

        if pd.isna(item_imbalance_ratio):
            if pd.notna(med_items) and med_items <= 5:
                item_v = f"Low item support (median {med_items:.1f} items/KC)"
            else:
                item_v = f"Median {med_items:.1f} items/KC (no sparse contrast)"
        elif item_imbalance_ratio >= 5:
            item_v = (
                f"High (dense {med_items_dense:.1f} vs sparse {med_items_sparse:.1f} items/KC)"
            )
        elif item_imbalance_ratio >= 2:
            item_v = (
                f"Moderate (dense {med_items_dense:.1f} vs sparse {med_items_sparse:.1f})"
            )
        else:
            item_v = (
                f"Low (dense {med_items_dense:.1f} vs sparse {med_items_sparse:.1f})"
            )

        if pd.isna(ece_s):
            grad_v = (
                f"Dense$\\to$medium only ($\\Delta$ECE$={grad_dm:+.3f}$); sparse empty"
            )
        elif grad_dm > 0.02 and (pd.isna(grad_ms) or grad_ms > 0.02):
            grad_v = (
                f"Monotonic increase ({ece_d:.3f}$\\to${ece_m:.3f}$\\to${ece_s:.3f})"
            )
        elif abs(grad_dm) <= 0.02 and abs(grad_ms) <= 0.02:
            grad_v = (
                f"Flat dense$\\to$sparse ({ece_d:.3f}$\\to${ece_m:.3f}$\\to${ece_s:.3f})"
            )
        else:
            grad_v = (
                f"Non-monotonic ({ece_d:.3f}$\\to${ece_m:.3f}$\\to${ece_s:.3f})"
            )

        verdicts.append({
            "dataset": LABELS[ds],
            "meaningful_sparse_mass": mass_v,
            "sufficient_test_support": support_v,
            "frequency_difficulty_coupling": fd_v,
            "curriculum_position_coupling": cp_v,
            "item_support_imbalance": item_v,
            "observed_calibration_gradient": grad_v,
        })

    profile = pd.DataFrame(rows)
    verdict_df = pd.DataFrame(verdicts)
    profile.to_csv(OUT_DIR / "dataset_sparse_diagnostic_profile.csv", index=False)
    verdict_df.to_csv(OUT_DIR / "a5_condition_verdicts.csv", index=False)
    print("Saved analysis/dataset_sparse_diagnostic_profile.csv")
    print(profile.T.to_string())
    print("\nVerdicts:")
    print(verdict_df.T.to_string())

    write_latex_table(verdict_df, profile)
    return profile, verdict_df


def write_latex_table(verdict_df, profile):
    def cell(ds, col):
        return verdict_df.loc[verdict_df["dataset"] == ds, col].iloc[0]

    a, j, x = "ASSISTments 2012", "Junyi Academy", "XES3G5M"
    lines = [
        r"\begin{table*}[htbp]",
        r"\caption{Dataset conditions associated with observable sparse-KC calibration vulnerability. "
        r"All six rows are structural or metric observations computed from training-fold frequencies "
        r"and published event-level SimpleKT ECE (Table~\ref{tab:calibration_learner}); they are FINDINGS, "
        r"not causal claims. Hierarchical curriculum, ceiling effects, item-feature richness, and tagging "
        r"granularity are \emph{not} listed here because they are untested (HYPOTHESIS; see text). "
        r"Sparse mass $= $ share of KCs with $f_{\mathrm{train}}<100$ (sparse + very sparse + strict). "
        r"Test support uses the protocol reliability flags (R/L/I). Coupling is Spearman $\rho$ between "
        r"$\log(1+f_{\mathrm{train}})$ and the named training-only covariate.}",
        r"\label{tab:a5_dataset_conditions}",
        r"\centering",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}p{3.3cm}XXX}",
        r"\toprule",
        r"\textbf{Condition} & \textbf{ASSISTments 2012} & \textbf{Junyi Academy} & \textbf{XES3G5M} \\",
        r"\midrule",
        rf"Meaningful sparse mass & {cell(a,'meaningful_sparse_mass')} & {cell(j,'meaningful_sparse_mass')} & {cell(x,'meaningful_sparse_mass')} \\",
        r"\midrule",
        rf"Sufficient test support & {cell(a,'sufficient_test_support')} & {cell(j,'sufficient_test_support')} & {cell(x,'sufficient_test_support')} \\",
        r"\midrule",
        rf"Frequency--difficulty coupling & {cell(a,'frequency_difficulty_coupling')} & {cell(j,'frequency_difficulty_coupling')} & {cell(x,'frequency_difficulty_coupling')} \\",
        r"\midrule",
        rf"Curriculum-position coupling & {cell(a,'curriculum_position_coupling')} & {cell(j,'curriculum_position_coupling')} & {cell(x,'curriculum_position_coupling')} \\",
        r"\midrule",
        rf"Item-support imbalance & {cell(a,'item_support_imbalance')} & {cell(j,'item_support_imbalance')} & {cell(x,'item_support_imbalance')} \\",
        r"\midrule",
        rf"Observed calibration gradient (SimpleKT, event-level) & {cell(a,'observed_calibration_gradient')} & {cell(j,'observed_calibration_gradient')} & {cell(x,'observed_calibration_gradient')} \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"",
        r"\vspace{1ex}",
        r"{\scriptsize \textbf{Note:} Event-level ECE matches Table~\ref{tab:calibration_learner}. "
        r"XES3G5M IRT ECE \emph{decreases} from dense to sparse (inverted), whereas DKT increases; "
        r"the SimpleKT row is therefore not a dataset-universal gradient. "
        r"Junyi temporal splits do populate sparse strata (see Table~\ref{tab:temporal_strata}), "
        r"so the learner-based empty-sparse pattern is threshold- and volume-dependent.\par}",
        r"\end{table*}",
        r"",
    ]
    tex = "\n".join(lines)
    path = OUT_DIR / "table_a5_dataset_conditions.tex"
    path.write_text(tex, encoding="utf-8")
    print(f"\nSaved {path}")


if __name__ == "__main__":
    main()
