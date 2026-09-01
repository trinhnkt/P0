#!/usr/bin/env python3
"""Score GKT vs DKT/SimpleKT on locked ASSISTments fold_0 strata (A1–A3)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.kc_strata import get_bucket  # noqa: E402
from src.recalculate_diagnostics import (  # noqa: E402
    calculate_metrics,
    compute_brier_decomposition,
    compute_ece,
)

DS, SPLIT, FOLD, SEED = "assist2012", "learner_based", 0, 42
PRED = ROOT / "results" / "predictions"
OUT = ROOT / "analysis" / "direction_a"
BUCKETS = ["dense", "medium", "sparse", "very_sparse", "strict_cold_start"]


def flag(n: int) -> str:
    if n >= 1000:
        return "R"
    if n >= 100:
        return "L"
    return "I"


def kc_key(x) -> str:
    return str(x).replace(".0", "")


def load_strata() -> dict:
    s = pd.read_csv(ROOT / "results" / "tables" / "kc_strata.csv")
    s = s[(s["dataset"] == DS) & (s["split"] == SPLIT) & (s["fold"] == FOLD)]
    m = {}
    for _, r in s.iterrows():
        m[kc_key(r["kc_id"])] = int(r["train_freq"])
    return m


def pred_path(model: str) -> Path:
    for name in (
        f"{DS}_{SPLIT}_{model}_seed{SEED}_predictions_rerun.csv",
        f"{DS}_{SPLIT}_{model}_seed{SEED}.csv",
    ):
        p = PRED / name
        if p.exists():
            return p
    raise FileNotFoundError(model)


def score(path: Path, strata: dict) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.dropna(subset=["y_true", "p_pred"])
    freqs = df["kc_id"].map(lambda k: strata.get(kc_key(k), 0))
    df["bucket"] = freqs.map(get_bucket)
    rows = []
    y_all, p_all = df["y_true"].astype(int).values, df["p_pred"].astype(float).values
    auc, acc, nll, rmse = calculate_metrics(y_all, p_all)
    ece = compute_ece(y_all, p_all)
    brier, _, rel, res = compute_brier_decomposition(y_all, p_all)
    rows.append(
        {
            "model": df["model"].iloc[0],
            "bucket": "all",
            "flag": flag(len(df)),
            "n_kcs": df["kc_id"].nunique(),
            "n_events": len(df),
            "AUC": auc,
            "ECE": ece,
            "REL": rel,
            "RES": res,
            "ACC": acc,
            "NLL": nll,
            "RMSE": rmse,
            "Brier": brier,
        }
    )
    for b in BUCKETS:
        sub = df[df["bucket"] == b]
        if sub.empty:
            continue
        y, p = sub["y_true"].astype(int).values, sub["p_pred"].astype(float).values
        auc, acc, nll, rmse = calculate_metrics(y, p)
        ece = compute_ece(y, p)
        brier, _, rel, res = compute_brier_decomposition(y, p)
        rows.append(
            {
                "model": df["model"].iloc[0],
                "bucket": b,
                "flag": flag(len(sub)),
                "n_kcs": sub["kc_id"].nunique(),
                "n_events": len(sub),
                "AUC": auc,
                "ECE": ece,
                "REL": rel,
                "RES": res,
                "ACC": acc,
                "NLL": nll,
                "RMSE": rmse,
                "Brier": brier,
            }
        )
    return pd.DataFrame(rows)


def verdict(tab: pd.DataFrame) -> list[str]:
    def cell(model, bucket, col):
        hit = tab[(tab["model"] == model) & (tab["bucket"] == bucket)]
        if hit.empty:
            return None
        return hit.iloc[0][col]

    lines = []
    dkt_s = cell("dkt", "sparse", "AUC")
    dkt_e = cell("dkt", "sparse", "ECE")
    any_pass = False
    for name in ["gkt_train_only", "gkt_full_log", "cl4kt"]:
        sparse_n = cell(name, "sparse", "n_events")
        if sparse_n is None:
            continue
        sparse_flag = cell(name, "sparse", "flag")
        m_s = cell(name, "sparse", "AUC")
        m_e = cell(name, "sparse", "ECE")
        m_strict = cell(name, "strict_cold_start", "n_events")
        a1 = sparse_flag == "I" or (
            m_strict is not None and sparse_n is not None and m_strict >= 0.5 * sparse_n
        )
        a2 = m_s is not None and dkt_s is not None and (m_s - dkt_s) <= 0
        a3 = (
            m_s is not None
            and dkt_s is not None
            and m_e is not None
            and dkt_e is not None
            and (m_s >= dkt_s)
            and (m_e > dkt_e)
            and sparse_flag in {"L", "R"}
        )
        lines.append(
            f"{name} A1 occupancy: sparse N={sparse_n} flag={sparse_flag} strict_n={m_strict} -> {'PASS' if a1 else 'no'}"
        )
        if m_s is not None and dkt_s is not None:
            lines.append(
                f"{name} A2 discrimination: sparse AUC {m_s:.4f} vs DKT {dkt_s:.4f} delta={m_s-dkt_s:+.4f} -> {'PASS (no/negative gain)' if a2 else 'still higher AUC'}"
            )
        if m_e is not None and dkt_e is not None:
            lines.append(
                f"{name} A3 calibration: sparse ECE {m_e:.4f} vs DKT {dkt_e:.4f} "
                f"(AUC>=DKT and ECE worse, L/R) -> {'PASS' if a3 else 'no'}"
            )
        any_pass = any_pass or bool(a1 or a2 or a3)
    lines.append(f"Direction A punchline this run: {'YES' if any_pass else 'NULL / not yet'}")
    return lines


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    strata = load_strata()
    models = ["dkt", "simplekt", "gkt_train_only", "gkt_full_log", "cl4kt"]
    frames = []
    for m in models:
        try:
            path = pred_path(m)
        except FileNotFoundError:
            print(f"missing {m}", flush=True)
            continue
        print(f"score {path.name}", flush=True)
        frames.append(score(path, strata))
    if not frames:
        raise SystemExit("no prediction files")
    tab = pd.concat(frames, ignore_index=True)
    tab.to_csv(OUT / "assist2012_learner_gkt_vs_baselines.csv", index=False)
    lines = verdict(tab)
    (OUT / "a1_a3_verdict.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(tab.to_string(index=False))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
