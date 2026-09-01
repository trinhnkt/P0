#!/usr/bin/env python3
"""A11: unique IRT p_pred stats on learner-based test prediction exports."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
PRED = HERE.parent / "results" / "predictions"
OUT = HERE / "analysis" / "irt_fallback_stats.csv"

DATASETS = ["assist2012", "junyi", "xes3g5m"]
SEEDS = [42, 2024, 2025, 2026, 2027]


def pred_path(ds: str, seed: int) -> Path | None:
    for name in (
        f"{ds}_learner_based_irt_1pl_seed{seed}_predictions_rerun.csv",
        f"{ds}_learner_based_irt_1pl_seed{seed}.csv",
    ):
        p = PRED / name
        if p.exists():
            return p
    return None


def main() -> None:
    rows = []
    for ds in DATASETS:
        for seed in SEEDS:
            path = pred_path(ds, seed)
            if path is None:
                rows.append(
                    {
                        "dataset": ds,
                        "seed": seed,
                        "file": "",
                        "n": 0,
                        "n_unique_p": np.nan,
                        "p_min": np.nan,
                        "p_max": np.nan,
                        "p_std": np.nan,
                        "p_mean": np.nan,
                        "auc": np.nan,
                        "constant": "",
                        "note": "MISSING",
                    }
                )
                continue
            df = pd.read_csv(path, usecols=["p_pred", "y_true"])
            p = df["p_pred"].to_numpy(dtype=np.float64)
            y = df["y_true"].to_numpy()
            n_unique = int(pd.Series(p).nunique())
            auc = float("nan")
            if len(np.unique(y)) >= 2:
                auc = float(roc_auc_score(y, p))
            rows.append(
                {
                    "dataset": ds,
                    "seed": seed,
                    "file": path.name,
                    "n": int(len(p)),
                    "n_unique_p": n_unique,
                    "p_min": float(p.min()),
                    "p_max": float(p.max()),
                    "p_std": float(p.std(ddof=0)),
                    "p_mean": float(p.mean()),
                    "auc": auc,
                    "constant": n_unique == 1,
                    "note": "",
                }
            )
            print(
                f"{ds} seed{seed}: n={len(p)} unique={n_unique} "
                f"min={p.min():.6f} max={p.max():.6f} std={p.std():.2e} auc={auc:.4f}",
                flush=True,
            )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
