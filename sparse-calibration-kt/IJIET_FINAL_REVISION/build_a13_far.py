#!/usr/bin/env python3
"""A13: partition-level ΔFAR robustness (average duplicated 2025/2026 split first)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SRC = HERE / "analysis" / "ijiet08_fivefold_denominators.csv"
OUT = HERE / "analysis" / "far_partition_robustness.csv"

MODEL = {"simplekt": "T-KT", "dkt": "DKT"}
DUP_SEEDS = (2025, 2026)


def sample_sd(vals: list[float]) -> float:
    n = len(vals)
    if n < 2:
        return float("nan")
    m = sum(vals) / n
    return (sum((x - m) ** 2 for x in vals) / (n - 1)) ** 0.5


def main() -> None:
    df = pd.read_csv(SRC)
    rows = []
    for model in ("simplekt", "dkt"):
        sub = df[(df["dataset"] == "assist2012") & (df["model"] == model)].copy()
        sub = sub.sort_values("seed")
        run = {int(s): float(v) for s, v in zip(sub["seed"], sub["dFM"])}
        seeds = [42, 2024, 2025, 2026, 2027]
        run_vals = [run[s] for s in seeds]
        n_run_pos = sum(v > 0 for v in run_vals)
        dup = (run[DUP_SEEDS[0]] + run[DUP_SEEDS[1]]) / 2.0
        part = {
            "42": run[42],
            "2024": run[2024],
            "2025_2026": dup,
            "2027": run[2027],
        }
        part_vals = list(part.values())
        n_part_pos = sum(v > 0 for v in part_vals)
        rows.append(
            {
                "dataset": "assist2012",
                "model": MODEL[model],
                "n_unique_partitions": 4,
                "n_partition_dfar_gt0": n_part_pos,
                "partition_mean_dfar": sum(part_vals) / 4.0,
                "partition_min_dfar": min(part_vals),
                "partition_max_dfar": max(part_vals),
                "n_runs": 5,
                "n_runs_dfar_gt0": n_run_pos,
                "five_run_mean_dfar": sum(run_vals) / 5.0,
                "five_run_sd_dfar": sample_sd(run_vals),
                "dup_rule": "average seeds 2025 and 2026 first",
                "dfar_seed42": run[42],
                "dfar_seed2024": run[2024],
                "dfar_seed2025": run[2025],
                "dfar_seed2026": run[2026],
                "dfar_seed2027": run[2027],
                "dfar_partition_2025_2026": dup,
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print(out.to_string(index=False))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
