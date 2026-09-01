#!/usr/bin/env python3
"""A4: cluster-aware weighted OLS for Section IV.D.

Uses IJIET_FINAL_REVISION/analysis/regression_unit_audit.csv (A3 reconstruction).
Does not treat repeated kc_id rows as independent. Primary SE: cluster-robust by kc_id.
Does not refit Huber; does not use ordinary iid-row SE as primary inference.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "analysis" / "regression_unit_audit.csv"
OUT_CLUST = HERE / "analysis" / "regression_clustered_results.csv"
OUT_FOLD = HERE / "analysis" / "regression_fold_sensitivity.csv"
OUT_TEX = HERE / "supplementary" / "Table_S_regression.tex"

PREDICTORS = [
    ("log1p_f_train", "log1p(f_train)"),
    ("difficulty_proxy", "difficulty_proxy"),
    ("item_support", "item_support"),
    ("learner_exposure", "learner_exposure"),
    ("curriculum_position_proxy", "curriculum_position_proxy"),
]
PRED_COLS = [c for c, _ in PREDICTORS]
DATASETS = ("assist2012", "junyi", "xes3g5m")
DS_LABEL = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}


def standardize(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    return (X - mu) / sd


def fit_clustered(df: pd.DataFrame, weighted: bool) -> pd.DataFrame:
    y = df["ECE"].to_numpy(dtype=float)
    X = standardize(df[PRED_COLS].to_numpy(dtype=float))
    X = sm.add_constant(X, prepend=True)
    groups = df["kc_id"].astype(str).to_numpy()
    if weighted:
        w = df["test_events"].to_numpy(dtype=float)
        model = sm.WLS(y, X, weights=w)
    else:
        model = sm.OLS(y, X)
    res = model.fit(cov_type="cluster", cov_kwds={"groups": groups}, use_t=True)
    names = ["intercept"] + [name for _, name in PREDICTORS]
    rows = []
    n_obs = int(len(df))
    n_kc = int(df["kc_id"].astype(str).nunique())
    n_fold = int(df["fold"].nunique())
    n_split = int(df["split"].nunique())
    for i, name in enumerate(names):
        if name == "intercept":
            continue
        coef = float(res.params[i])
        se = float(res.bse[i])
        ci = np.asarray(res.conf_int())
        ci_lo, ci_hi = float(ci[i, 0]), float(ci[i, 1])
        p = float(res.pvalues[i])
        rows.append(
            {
                "covariate": name,
                "coef_std": coef,
                "SE_cluster": se,
                "CI_lo": ci_lo,
                "CI_hi": ci_hi,
                "p": p,
                "n_obs": n_obs,
                "n_unique_kc": n_kc,
                "n_folds": n_fold,
                "n_splits": n_split,
                "weighted": weighted,
                "cluster": "kc_id",
                "estimator": "WLS" if weighted else "OLS",
            }
        )
    return pd.DataFrame(rows)


def fmt_coef(x: float) -> str:
    sign = "+" if x >= 0 else "\u2212"
    return f"{sign}{abs(x):.3f}"


def fmt_ci(lo: float, hi: float) -> str:
    def one(z: float) -> str:
        sign = "+" if z >= 0 else "\u2212"
        return f"{sign}{abs(z):.3f}"

    return f"[{one(lo)}, {one(hi)}]"


def write_tex(clust: pd.DataFrame) -> None:
    w = clust[clust["weighted"]].copy()
    u = clust[~clust["weighted"]].copy()
    cov_order = [name for _, name in PREDICTORS]
    cov_tex = {
        "log1p(f_train)": r"$\log(1+f_{\mathrm{train}})$",
        "difficulty_proxy": r"Difficulty proxy",
        "item_support": r"Item support",
        "learner_exposure": r"Learner exposure",
        "curriculum_position_proxy": r"Curriculum position",
    }
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Cluster-aware SimpleKT ECE regression (Section IV.D). Rows are KC-fold observations at fold 0 under learner-based and temporal splits. Predictors are standardized within dataset. Weights are test-event counts. Standard errors are cluster-robust at $\mathrm{kc\_id}$. Not a causal frequency effect.}",
        r"\label{tab:s_regression_cluster}",
        r"\centering\scriptsize",
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Dataset & Covariate & $n_{\mathrm{obs}}$ & Unique KCs & $\hat\beta$ & SE$_{\mathrm{cl}}$ & 95\% CI & $p$ \\",
        r"\midrule",
        r"\multicolumn{8}{l}{\emph{Primary: weighted WLS, cluster-robust SE}} \\",
    ]
    for ds in DATASETS:
        sub = w[w["dataset"] == ds]
        first = True
        for cov in cov_order:
            row = sub[sub["covariate"] == cov].iloc[0]
            ds_lab = DS_LABEL[ds] if first else ""
            p = row["p"]
            p_str = f"{p:.3f}" if p >= 0.001 else "$<0.001$"
            lines.append(
                f"{ds_lab} & {cov_tex[cov]} & {int(row['n_obs']):,} & {int(row['n_unique_kc']):,} & "
                f"${row['coef_std']:+.3f}$ & ${row['SE_cluster']:.3f}$ & "
                f"$[{row['CI_lo']:+.3f},{row['CI_hi']:+.3f}]$ & {p_str} \\\\"
            )
            first = False
        lines.append(r"\midrule")
    lines.append(r"\multicolumn{8}{l}{\emph{Sensitivity: unweighted OLS, same cluster-robust SE}} \\")
    for ds in DATASETS:
        sub = u[u["dataset"] == ds]
        first = True
        for cov in cov_order:
            row = sub[sub["covariate"] == cov].iloc[0]
            ds_lab = DS_LABEL[ds] if first else ""
            p = row["p"]
            p_str = f"{p:.3f}" if p >= 0.001 else "$<0.001$"
            lines.append(
                f"{ds_lab} & {cov_tex[cov]} & {int(row['n_obs']):,} & {int(row['n_unique_kc']):,} & "
                f"${row['coef_std']:+.3f}$ & ${row['SE_cluster']:.3f}$ & "
                f"$[{row['CI_lo']:+.3f},{row['CI_hi']:+.3f}]$ & {p_str} \\\\"
            )
            first = False
        lines.append(r"\midrule")
    lines[-1] = r"\bottomrule"
    lines += [
        r"\end{tabular}",
        r"\end{table}",
        "",
    ]
    OUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_TEX.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = pd.read_csv(AUDIT)
    clustered = []
    fold_rows = []
    for ds in DATASETS:
        sub = df[df["dataset"] == ds].copy()
        for weighted in (True, False):
            res = fit_clustered(sub, weighted=weighted)
            res["dataset"] = ds
            clustered.append(res)
        # Robustness: split-specific (fold is 0 in both; the repeat unit is split).
        for split, g in sub.groupby("split"):
            for weighted in (True, False):
                res = fit_clustered(g, weighted=weighted)
                res["dataset"] = ds
                res["split"] = split
                res["fold"] = int(g["fold"].iloc[0])
                fold_rows.append(res)

    clust = pd.concat(clustered, ignore_index=True)
    fold = pd.concat(fold_rows, ignore_index=True)
    cols = [
        "dataset",
        "covariate",
        "estimator",
        "weighted",
        "cluster",
        "n_obs",
        "n_unique_kc",
        "n_folds",
        "n_splits",
        "coef_std",
        "SE_cluster",
        "CI_lo",
        "CI_hi",
        "p",
    ]
    clust[cols].to_csv(OUT_CLUST, index=False)
    fold_cols = ["dataset", "split", "fold"] + [c for c in cols if c != "dataset"]
    fold[fold_cols].to_csv(OUT_FOLD, index=False)
    write_tex(clust)
    print("wrote", OUT_CLUST)
    print("wrote", OUT_FOLD)
    print("wrote", OUT_TEX)
    show = clust[(clust["weighted"]) & (clust["covariate"] == "log1p(f_train)")]
    print(show[["dataset", "n_obs", "n_unique_kc", "coef_std", "SE_cluster", "CI_lo", "CI_hi", "p"]].to_string(index=False))


if __name__ == "__main__":
    main()
