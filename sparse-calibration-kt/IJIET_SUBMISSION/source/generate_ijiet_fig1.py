#!/usr/bin/env python3
"""Regenerate IJIET Fig. 1: KC counts (top) and verified training-event volume (bottom).

Does not overwrite paper/figures. Fold 0 only, matching the published figure.
Training volume = sum of train-only f_train per stratum (kc_strata.csv), not inferred from n_kcs.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "IJIET_SUBMISSION" / "figures"
DIST = ROOT / "results" / "tables" / "bucket_distribution.csv"
STRATA = ROOT / "results" / "tables" / "kc_strata.csv"

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


def count_table(dist: pd.DataFrame, col: str) -> dict[tuple[str, str, str], float]:
    out = {}
    for ds in DATASETS:
        for split in SPLITS:
            for b in BUCKETS:
                hit = dist[
                    (dist["dataset"] == ds)
                    & (dist["split"] == split)
                    & (dist["bucket"] == b)
                    & (dist["fold"] == 0)
                ]
                out[(ds, split, b)] = float(hit[col].sum()) if not hit.empty else 0.0
    return out


def main() -> None:
    dist = pd.read_csv(DIST)
    dist = dist[dist["dataset"].isin(DATASETS)].copy()
    strata = pd.read_csv(STRATA)
    strata = strata[(strata["dataset"].isin(DATASETS)) & (strata["fold"] == 0)].copy()
    n_kcs = count_table(dist, "n_kcs")
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
            kvals = [n_kcs.get((ds, split, b), 0.0) for b in BUCKETS]
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
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / "fig1_kc_and_train_volume.png"
    fig.savefig(png, bbox_inches="tight")
    plt.close(fig)
    print("wrote", png, png.stat().st_size)


if __name__ == "__main__":
    main()
