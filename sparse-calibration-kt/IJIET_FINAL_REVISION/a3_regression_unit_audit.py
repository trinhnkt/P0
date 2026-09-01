#!/usr/bin/env python3
"""A3: reconstruct the IV.D SimpleKT regression rows and audit the analysis unit.

Does not refit coefficients. Does not edit the manuscript.
Source: historical analysis/kc_characteristics.csv produced by scripts/a4_confounding_analysis.py.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SRC = REPO / "analysis" / "kc_characteristics.csv"
OUT_CSV = HERE / "analysis" / "regression_unit_audit.csv"

DATASETS = ("assist2012", "junyi", "xes3g5m")
COVS = [
    "ECE",
    "log_train_freq",
    "difficulty_proxy",
    "n_train_items",
    "n_train_learners",
    "median_sequence_position_train",
    "test_events",
]


def main() -> None:
    kc = pd.read_csv(SRC)
    sub = kc[(kc["model"] == "simplekt") & (kc["dataset"].isin(DATASETS))].copy()
    rows = sub.dropna(subset=COVS).copy()
    # A4 built train features with fold=0 only (learner_based and temporal).
    rows["fold"] = 0
    audit = pd.DataFrame(
        {
            "dataset": rows["dataset"].astype(str),
            "split": rows["split"].astype(str),
            "fold": rows["fold"].astype(int),
            "kc_id": rows["kc_id"].astype(str),
            "test_events": rows["test_events"].astype(int),
            "ECE": rows["ECE"].astype(float),
            "log1p_f_train": rows["log_train_freq"].astype(float),
            "difficulty_proxy": rows["difficulty_proxy"].astype(float),
            "item_support": rows["n_train_items"].astype(float),
            "learner_exposure": rows["n_train_learners"].astype(float),
            "curriculum_position_proxy": rows["median_sequence_position_train"].astype(float),
        }
    )
    audit = audit.sort_values(["dataset", "split", "fold", "kc_id"]).reset_index(drop=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_CSV, index=False)
    print("wrote", OUT_CSV, "rows", len(audit))
    for ds, g in audit.groupby("dataset", sort=True):
        n_kc = g["kc_id"].nunique()
        n_fold = g["fold"].nunique()
        n_split = g["split"].nunique()
        obs = g.groupby("kc_id").size()
        print(
            f"{ds}: rows={len(g)} unique_kc={n_kc} folds={n_fold} splits={n_split} "
            f"mean_obs/kc={obs.mean():.4f} min={int(obs.min())} max={int(obs.max())}"
        )


if __name__ == "__main__":
    main()
