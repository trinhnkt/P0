#!/usr/bin/env python3
"""A9 metrics, paired ΔECE/ΔREL, bootstrap CI, figure, LaTeX."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(".")
sys.path.append(str(ROOT.resolve()))
from src.recalculate_diagnostics import (  # noqa: E402
    calculate_metrics,
    compute_brier_decomposition,
    compute_ece,
)

OUT = ROOT / "analysis" / "a9"
FIG = ROOT / "REV_REVIEWER_CALIBRATION_v1" / "figures"
TAB = ROOT / "REV_REVIEWER_CALIBRATION_v1" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

SPLIT = "learner_based"
LEVELS = ["full", "t500", "t100", "t50"]
MODELS = ["dkt", "simplekt"]
SEEDS_REDUCED = [42]
N_BOOT = 10000
BOOT_SEED = 2029
DS_LABEL = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}


def kc_key(s) -> str:
    return str(s).replace(".0", "")


def official_pred(ds: str, model: str, seed: int) -> Path:
    p = ROOT / "results" / "predictions" / f"{ds}_{SPLIT}_{model}_seed{seed}_predictions_rerun.csv"
    if p.exists():
        return p
    return ROOT / "results" / "predictions" / f"{ds}_{SPLIT}_{model}_seed{seed}.csv"


def a9_pred(ds: str, model: str, level: str, seed: int) -> Path:
    return ROOT / "results" / "predictions" / f"a9_{ds}_{SPLIT}_{model}_{level}_seed{seed}.csv"


def metrics_block(y, p) -> dict:
    y = np.asarray(y).astype(int)
    p = np.clip(np.asarray(p).astype(float), 1e-15, 1 - 1e-15)
    auc, acc, nll, rmse = calculate_metrics(y, p)
    ece = compute_ece(y, p)
    brier, unc, rel, res = compute_brier_decomposition(y, p)
    return {
        "AUC": auc,
        "ACC": acc,
        "NLL": nll,
        "RMSE": rmse,
        "ECE": ece,
        "Brier": brier,
        "REL": rel,
        "RES": res,
        "n_events": int(len(y)),
        "n_pos": int((y == 1).sum()),
        "n_neg": int((y == 0).sum()),
    }


def load_selected() -> pd.DataFrame:
    return pd.read_csv(OUT / "selected_kcs.csv")


def eval_file(path: Path, selected: set[str]) -> tuple[dict, pd.DataFrame]:
    df = pd.read_csv(path, usecols=["kc_id", "y_true", "p_pred"])
    df["kc_id"] = df["kc_id"].map(kc_key)
    df = df[df["kc_id"].isin(selected)].dropna(subset=["y_true", "p_pred"])
    pooled = metrics_block(df["y_true"], df["p_pred"])
    rows = []
    for kc, g in df.groupby("kc_id"):
        m = metrics_block(g["y_true"], g["p_pred"])
        m["kc_id"] = kc
        rows.append(m)
    return pooled, pd.DataFrame(rows)


def bootstrap_mean_ci(vals: np.ndarray, rng: np.random.Generator):
    vals = np.asarray(vals, dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return np.nan, np.nan, np.nan
    means = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(N_BOOT)]
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(vals.mean()), float(lo), float(hi)


def main():
    sel_all = load_selected()
    pooled_rows = []
    kc_rows = []

    datasets = sorted(sel_all["dataset"].unique())
    for ds in datasets:
        selected = set(sel_all.loc[sel_all["dataset"] == ds, "kc_id"].map(kc_key))
        for model in MODELS:
            # full = official seed 42 (and extra seeds if present)
            for seed in [42, 2024, 2025]:
                pfull = official_pred(ds, model, seed)
                if not pfull.exists():
                    continue
                pooled, per_kc = eval_file(pfull, selected)
                pooled.update(dataset=ds, model=model, level="full", seed=seed, source="official")
                pooled_rows.append(pooled)
                per_kc["dataset"] = ds
                per_kc["model"] = model
                per_kc["level"] = "full"
                per_kc["seed"] = seed
                kc_rows.append(per_kc)

            for level in ("t500", "t100", "t50"):
                for seed in SEEDS_REDUCED:
                    p = a9_pred(ds, model, level, seed)
                    if not p.exists():
                        continue
                    pooled, per_kc = eval_file(p, selected)
                    pooled.update(dataset=ds, model=model, level=level, seed=seed, source="a9")
                    pooled_rows.append(pooled)
                    per_kc["dataset"] = ds
                    per_kc["model"] = model
                    per_kc["level"] = level
                    per_kc["seed"] = seed
                    kc_rows.append(per_kc)

    if not pooled_rows:
        print("No A9 or official files to score.")
        return

    pooled = pd.DataFrame(pooled_rows)
    kc_m = pd.concat(kc_rows, ignore_index=True)
    pooled.to_csv(OUT / "pooled_selected_kc_metrics.csv", index=False)
    kc_m.to_csv(OUT / "kc_metrics.csv", index=False)

    rng = np.random.default_rng(BOOT_SEED)
    stats = []
    for (ds, model, level), g in kc_m.groupby(["dataset", "model", "level"]):
        if level == "full":
            continue
        full = kc_m[
            (kc_m["dataset"] == ds)
            & (kc_m["model"] == model)
            & (kc_m["level"] == "full")
            & (kc_m["seed"] == 42)
        ]
        merged = g.merge(full, on="kc_id", suffixes=("_red", "_full"))
        if merged.empty:
            continue
        d_ece = merged["ECE_red"] - merged["ECE_full"]
        d_rel = merged["REL_red"] - merged["REL_full"]
        ece_m, ece_lo, ece_hi = bootstrap_mean_ci(d_ece.to_numpy(), rng)
        rel_m, rel_lo, rel_hi = bootstrap_mean_ci(d_rel.to_numpy(), rng)
        stats.append(
            {
                "dataset": ds,
                "model": model,
                "level": level,
                "n_kcs": int(len(merged)),
                "delta_ECE_mean": ece_m,
                "delta_ECE_ci95_lo": ece_lo,
                "delta_ECE_ci95_hi": ece_hi,
                "delta_REL_mean": rel_m,
                "delta_REL_ci95_lo": rel_lo,
                "delta_REL_ci95_hi": rel_hi,
                "frac_kcs_ece_worse": float((d_ece > 0).mean()),
                "note": "positive Delta = worse calibration after reducing evidence; bootstrap over KCs",
            }
        )
    stats_df = pd.DataFrame(stats)
    stats_df.to_csv(OUT / "statistical_summary.csv", index=False)
    pooled.to_csv(ROOT / "analysis" / "a9_sparsification_results.csv", index=False)
    stats_df.to_csv(ROOT / "analysis" / "a9_statistical_summary.csv", index=False)
    kc_m.to_csv(ROOT / "analysis" / "a9_kc_metrics.csv", index=False)

    # Figure: pooled ECE vs level for datasets that have at least one reduced run
    plot_df = pooled[pooled["seed"] == 42].copy()
    has_red = set(plot_df.loc[plot_df["level"] != "full", "dataset"])
    plot_df = plot_df[plot_df["dataset"].isin(has_red)]
    if not plot_df.empty:
        fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.6), sharex=True)
        xmap = {lv: i for i, lv in enumerate(LEVELS)}
        for ax, metric in zip(axes, ("ECE", "REL")):
            for ds in sorted(plot_df["dataset"].unique()):
                for model, ls in (("dkt", "-"), ("simplekt", "--")):
                    sub = plot_df[(plot_df["dataset"] == ds) & (plot_df["model"] == model)]
                    sub = sub.sort_values("level", key=lambda s: s.map(xmap))
                    if sub.empty:
                        continue
                    ax.plot(
                        [xmap[lv] for lv in sub["level"]],
                        sub[metric],
                        marker="o",
                        linestyle=ls,
                        label=f"{DS_LABEL[ds]} {model}",
                    )
            ax.set_xticks(range(len(LEVELS)))
            ax.set_xticklabels(["full", "500", "100", "50"])
            ax.set_xlabel("Training rows kept per selected KC")
            ax.set_ylabel(metric)
            ax.grid(True, alpha=0.4, linewidth=0.4)
        axes[0].legend(fontsize=7, loc="best")
        fig.suptitle("Selected-KC test calibration vs controlled training evidence", fontsize=10)
        fig.tight_layout()
        for dest in (OUT / "ece_rel_vs_evidence.pdf", FIG / "a9_ece_rel_vs_evidence.pdf"):
            fig.savefig(dest, bbox_inches="tight")
            print("saved", dest)
        plt.close(fig)

    # LaTeX summary (only rows we have)
    if not stats_df.empty:
        lines = [
            r"\begin{table}[htbp]",
            r"\caption{Controlled sparsification: within-KC change in primary calibration outcomes on the held-out test events of selected originally-dense KCs. $\Delta = $ reduced $-$ full. Positive values mean worse calibration after reducing training rows for the same KC. 95\% CIs are bootstrap over KCs. This is a validation experiment; it does not claim that real-world sparsity always causes miscalibration.}",
            r"\label{tab:a9_sparsification}",
            r"\centering",
            r"\small",
            r"\begin{tabular}{llcccc}",
            r"\toprule",
            r"Dataset & Model & Level & $\Delta$ECE [95\% CI] & $\Delta$REL [95\% CI] & Share ECE$\uparrow$ \\",
            r"\midrule",
        ]
        for _, r in stats_df.iterrows():
            lines.append(
                f"{DS_LABEL[r['dataset']]} & {r['model']} & {r['level']} & "
                f"{r['delta_ECE_mean']:.4f} [{r['delta_ECE_ci95_lo']:.4f}, {r['delta_ECE_ci95_hi']:.4f}] & "
                f"{r['delta_REL_mean']:.4f} [{r['delta_REL_ci95_lo']:.4f}, {r['delta_REL_ci95_hi']:.4f}] & "
                f"{100*r['frac_kcs_ece_worse']:.0f}\\% \\\\"
            )
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", r""]
        tex = "\n".join(lines)
        (OUT / "table_a9_sparsification.tex").write_text(tex, encoding="utf-8")
        TAB.mkdir(parents=True, exist_ok=True)
        (TAB / "table_16_sparsification.tex").write_text(tex, encoding="utf-8")
        print(stats_df.to_string(index=False))
    print("A9 analysis complete")


if __name__ == "__main__":
    main()
