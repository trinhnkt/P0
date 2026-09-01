#!/usr/bin/env python3
"""Fig. 1 for the A2B-masked manuscript copy.

ASSISTments / Junyi: historical fold-0 strata (unchanged).
XES3G5M: IJIET_FINAL_REVISION/a2b strata (padding excluded).
Writes only under IJIET_FINAL_REVISION/figures/. Does not touch IJIET_SUBMISSION/.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
REV = HERE.parent
ROOT = REV.parent
HIST = ROOT / "results" / "tables" / "kc_strata.csv"
A2B = REV / "a2b" / "results" / "tables" / "kc_strata.csv"
OUT = HERE / "fig1_kc_and_train_volume.png"

DATASETS = ["assist2012", "junyi", "xes3g5m"]
TITLES = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}
BUCKETS = ["strict_cold_start", "very_sparse", "sparse", "medium", "dense"]
XTICKS = ["=0", "1–19", "20–99", "100–499", "≥500"]
COLORS = {"learner_based": "#2171B5", "temporal": "#D94801"}
SPLITS = ["learner_based", "temporal"]
SPLIT_LABELS = ["Learner-based", "Temporal"]


def fold0(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    hit = df[(df["dataset"] == dataset) & (df["fold"] == 0)].copy()
    if hit.empty:
        raise SystemExit(f"empty fold-0 strata for {dataset}")
    return hit


def main() -> None:
    hist = pd.read_csv(HIST)
    a2b = pd.read_csv(A2B)
    if "dataset" not in a2b.columns:
        a2b = a2b.copy()
        a2b["dataset"] = "xes3g5m"
    parts = [
        fold0(hist, "assist2012"),
        fold0(hist, "junyi"),
        fold0(a2b, "xes3g5m"),
    ]
    strata = pd.concat(parts, ignore_index=True)
    if ((strata["dataset"] == "xes3g5m") & (strata["kc_id"].astype(str) == "-1")).any():
        raise SystemExit("XES strata still contain kc_id=-1")

    n_kcs = (
        strata.groupby(["dataset", "split", "bucket"], dropna=False)
        .size()
        .to_dict()
    )
    vol = (
        strata.groupby(["dataset", "split", "bucket"], dropna=False)["train_freq"]
        .sum()
        .to_dict()
    )

    plt.rcParams.update(
        {
            "font.family": "Times New Roman",
            "axes.titlesize": 13,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 12,
        }
    )
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.9), dpi=300)

    for col, ds in enumerate(DATASETS):
        ax_k = axes[0, col]
        ax_v = axes[1, col]
        x = range(len(BUCKETS))
        width = 0.38
        for j, split in enumerate(SPLITS):
            offset = -width / 2 if j == 0 else width / 2
            kvals = [float(n_kcs.get((ds, split, b), 0.0)) for b in BUCKETS]
            vvals = [float(vol.get((ds, split, b), 0.0)) for b in BUCKETS]
            ax_k.bar(
                [i + offset for i in x],
                kvals,
                width=width,
                color=COLORS[split],
                label=SPLIT_LABELS[j] if col == 0 else None,
            )
            ax_v.bar(
                [i + offset for i in x],
                vvals,
                width=width,
                color=COLORS[split],
            )
        ax_k.set_title(TITLES[ds], pad=6)
        ax_k.set_xticks(list(x))
        ax_k.set_xticklabels([])
        ax_v.set_xticks(list(x))
        ax_v.set_xticklabels(XTICKS, rotation=40, ha="right", rotation_mode="anchor", fontsize=8)
        ax_v.tick_params(axis="x", pad=2)
        ax_k.set_ylabel("Number of KCs" if col == 0 else "")
        ax_v.set_ylabel("Training interactions" if col == 0 else "")
        ax_v.set_yscale("log")
        ax_v.set_ylim(bottom=1)
        ax_k.yaxis.grid(True, linestyle="--", alpha=0.45)
        ax_v.yaxis.grid(True, linestyle="--", alpha=0.45)
        ax_k.set_axisbelow(True)
        ax_v.set_axisbelow(True)
        for ax in (ax_k, ax_v):
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=COLORS["learner_based"], label="Learner-based"),
        plt.Rectangle((0, 0), 1, 1, color=COLORS["temporal"], label="Temporal"),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
        fontsize=11,
    )
    fig.text(
        0.5,
        0.01,
        "Train-only frequency: strict (=0), very sparse (1–19), sparse (20–99), medium (100–499), dense (≥500)",
        ha="center",
        fontsize=10,
    )
    fig.tight_layout(rect=[0.0, 0.06, 1.0, 0.96])
    fig.subplots_adjust(wspace=0.28, hspace=0.22)
    fig.savefig(OUT, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
