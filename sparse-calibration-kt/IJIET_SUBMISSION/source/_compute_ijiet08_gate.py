#!/usr/bin/env python3
"""IJIET-08: recover gate denominators and KC-cluster FAR CIs from prediction exports.

Does not retune tau. Display tau=0.7. Uses the C2 bootstrap (B=2000, RNG 0, KC cluster).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.kc_strata import get_bucket  # noqa: E402

PRED = ROOT / "results" / "predictions"
DATA = ROOT / "data" / "processed"
OUT = ROOT / "IJIET_SUBMISSION" / "audit"
RATES = ROOT / "analysis" / "direction_c" / "threshold_rates.csv"
GAPS = ROOT / "analysis" / "direction_c" / "fivefold_gaps.csv"
BOOT_EXISTING = ROOT / "analysis" / "direction_c" / "seed42_bootstrap_dfm.csv"

TAU = 0.7
BOOT_B = 2000
BOOT_RNG = 0
SPLIT = "learner_based"


def kc_key(x) -> str:
    return str(x).replace(".0", "")


def pred_path(model: str, seed: int) -> Path:
    aliases = {
        "simplekt": "simplekt",
        "dkt": "dkt",
        "gkt_train_only": "gkt_train_only",
        "cl4kt": "cl4kt",
    }
    m = aliases[model]
    for name in (
        f"assist2012_{SPLIT}_{m}_seed{seed}_predictions_rerun.csv",
        f"assist2012_{SPLIT}_{m}_seed{seed}.csv",
    ):
        p = PRED / name
        if p.exists():
            return p
    raise FileNotFoundError(model)


def train_freq(fold: int) -> dict[str, int]:
    train = pd.read_csv(
        DATA / "assist2012" / "splits" / SPLIT / f"fold_{fold}" / "train.csv",
        usecols=["kc_id"],
    )
    vc = train["kc_id"].map(kc_key).value_counts()
    return {k: int(v) for k, v in vc.items()}


def attach(df: pd.DataFrame, freq: dict[str, int]) -> pd.DataFrame:
    f = df["kc_id"].map(lambda k: freq.get(kc_key(k), 0))
    return df.assign(bucket=f.map(get_bucket), kc=df["kc_id"].map(kc_key))


def stratum_stats(sub: pd.DataFrame) -> dict:
    y = sub["y_true"].to_numpy(dtype=int)
    p = sub["p_pred"].to_numpy(dtype=float)
    adv = p >= TAU
    n = int(y.size)
    n_adv = int(adv.sum())
    n_inc = int((y == 0).sum())
    n_fa = int(((y == 0) & adv).sum())
    far = n_fa / n_adv if n_adv else np.nan
    e_far = float((1.0 - p[adv]).mean()) if n_adv else np.nan
    miss = n_fa / n_inc if n_inc else np.nan
    return {
        "N_total": n,
        "N_advance": n_adv,
        "N_incorrect": n_inc,
        "FAR": far,
        "E_FAR": e_far,
        "Excess_FAR": (far - e_far) if pd.notna(far) and pd.notna(e_far) else np.nan,
        "Miss": miss,
    }


def kc_adv_fail(sub: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    n_adv, n_fail = [], []
    for _, part in sub.groupby("kc", sort=False):
        y = part["y_true"].to_numpy()
        p = part["p_pred"].to_numpy()
        adv = p >= TAU
        n_adv.append(int(adv.sum()))
        n_fail.append(int(((y == 0) & adv).sum()))
    return np.asarray(n_adv, dtype=np.int64), np.asarray(n_fail, dtype=np.int64)


def boot_ratio(n_adv: np.ndarray, n_fail: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n = len(n_adv)
    out = np.empty(BOOT_B, dtype=float)
    ok = 0
    for _ in range(BOOT_B):
        idx = rng.integers(0, n, n)
        a = int(n_adv[idx].sum())
        if a == 0:
            continue
        out[ok] = int(n_fail[idx].sum()) / a
        ok += 1
    return out[:ok]


def boot_delta(
    s_adv, s_fail, d_adv, d_fail, rng: np.random.Generator
) -> np.ndarray:
    ns, nd = len(s_adv), len(d_adv)
    out = np.empty(BOOT_B, dtype=float)
    ok = 0
    for _ in range(BOOT_B):
        i_s = rng.integers(0, ns, ns)
        i_d = rng.integers(0, nd, nd)
        a_s, a_d = int(s_adv[i_s].sum()), int(d_adv[i_d].sum())
        if a_s == 0 or a_d == 0:
            continue
        out[ok] = int(s_fail[i_s].sum()) / a_s - int(d_fail[i_d].sum()) / a_d
        ok += 1
    return out[:ok]


def ci(arr: np.ndarray) -> tuple[float, float, int]:
    if arr.size == 0:
        return np.nan, np.nan, 0
    return float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975)), int(arr.size)


def main() -> None:
    rates = pd.read_csv(RATES)
    t4_src = rates[
        (rates["dataset"] == "assist2012")
        & (rates["tau"] == TAU)
        & (rates["bucket"].isin(["dense", "sparse"]))
        & (rates["model"].isin(["simplekt", "dkt", "gkt_train_only", "cl4kt"]))
    ].copy()
    t4_src["N_incorrect"] = (
        t4_src["n_events"] * (1.0 - t4_src["mean_y"])
    ).round().astype(int)
    t4_src.to_csv(OUT / "ijiet08_table4_from_threshold_rates.csv", index=False)

    models = [
        ("simplekt", "SimpleKT"),
        ("dkt", "DKT"),
        ("gkt_train_only", "GKT (train-only)"),
        ("cl4kt", "CL4KT (adapter)"),
    ]
    freq = train_freq(0)
    boot_rows = []
    point_rows = []
    for key, label in models:
        path = pred_path(key, 42)
        print(f"load {path.name}", flush=True)
        df = pd.read_csv(path, usecols=["kc_id", "y_true", "p_pred"]).dropna(
            subset=["y_true", "p_pred"]
        )
        df = attach(df, freq)
        rng = np.random.default_rng(BOOT_RNG)
        packed = {}
        for bucket in ("dense", "sparse"):
            sub = df[df["bucket"] == bucket]
            st = stratum_stats(sub)
            st.update({"model": label, "stratum": bucket})
            point_rows.append(st)
            packed[bucket] = kc_adv_fail(sub)
            arr = boot_ratio(*packed[bucket], rng)
            lo, hi, n = ci(arr)
            boot_rows.append(
                {
                    "model": label,
                    "quantity": f"FAR_{bucket}",
                    "point": st["FAR"],
                    "ci_lo": lo,
                    "ci_hi": hi,
                    "n_valid": n,
                }
            )
        d_arr = boot_delta(*packed["sparse"], *packed["dense"], rng)
        lo, hi, n = ci(d_arr)
        far_s = next(r["FAR"] for r in point_rows if r["model"] == label and r["stratum"] == "sparse")
        far_d = next(r["FAR"] for r in point_rows if r["model"] == label and r["stratum"] == "dense")
        boot_rows.append(
            {
                "model": label,
                "quantity": "Delta_FAR",
                "point": far_s - far_d,
                "ci_lo": lo,
                "ci_hi": hi,
                "n_valid": n,
            }
        )
        print(f"  {label} dFAR={far_s-far_d:.4f} CI [{lo:.4f}, {hi:.4f}]", flush=True)

    pd.DataFrame(point_rows).to_csv(OUT / "ijiet08_seed42_gate_points.csv", index=False)
    pd.DataFrame(boot_rows).to_csv(OUT / "ijiet08_seed42_kc_cluster_ci.csv", index=False)

    gaps = pd.read_csv(GAPS)
    a = gaps[gaps["dataset"] == "assist2012"].copy()
    a["N_incorrect_sparse"] = (
        a["FM_sparse"] * a["sparse_n_advance"] / a["Miss_sparse"]
    ).round()
    a.to_csv(OUT / "ijiet08_fivefold_denominators.csv", index=False)

    exist = pd.read_csv(BOOT_EXISTING)
    lines = [
        "# IJIET-08 recovered gate denominators and CIs",
        "",
        "Source: `results/predictions/*` plus `analysis/direction_c/threshold_rates.csv`.",
        "Bootstrap: KC-cluster percentile, B=2000, RNG seed 0 (same as C2).",
        "tau=0.7. Not retuned on sparse events.",
        "",
        "## Seed-42 points vs published 3-decimal table",
        str(pd.DataFrame(point_rows).to_string(index=False)),
        "",
        "## KC-cluster 95% CI",
        str(pd.DataFrame(boot_rows).to_string(index=False)),
        "",
        "## Existing C2 Delta-FM CI (should match SimpleKT Delta_FAR)",
        str(exist.to_string(index=False)),
        "",
        "## Five-seed sparse denominators (assist2012)",
        str(
            a[["model", "seed", "sparse_n", "sparse_n_advance", "N_incorrect_sparse", "dFM"]]
            .to_string(index=False)
        ),
        "",
    ]
    (OUT / "ijiet08_gate_recover.txt").write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT / "ijiet08_gate_recover.txt")


if __name__ == "__main__":
    main()
