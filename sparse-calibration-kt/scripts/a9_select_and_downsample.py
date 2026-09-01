#!/usr/bin/env python3
"""
A9: Select KCs (pre-registered rule) and write downsample manifests + train copies.

Never overwrites official processed splits.
Does not use ECE/REL/AUC to select KCs.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".")
OUT = ROOT / "analysis" / "a9"
MAN = OUT / "manifests"
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)

DATASETS = ["assist2012", "junyi", "xes3g5m"]
DS_LABEL = {
    "assist2012": "ASSISTments 2012",
    "junyi": "Junyi Academy",
    "xes3g5m": "XES3G5M",
}
SPLIT = "learner_based"
FOLD = 0
TARGETS = (500, 100, 50)
MAX_PER_TERTILE = 10
MAX_SELECTED = 30
PRED_MODELS = ("dkt", "simplekt")


def kc_key(s) -> str:
    return str(s).replace(".0", "")


def split_dir(ds: str) -> Path:
    return ROOT / "data" / "processed" / ds / "splits" / SPLIT / f"fold_{FOLD}"


def pred_path(ds: str, model: str) -> Path:
    p = ROOT / "results" / "predictions" / f"{ds}_{SPLIT}_{model}_seed42_predictions_rerun.csv"
    if p.exists():
        return p
    return ROOT / "results" / "predictions" / f"{ds}_{SPLIT}_{model}_seed42.csv"


def salt(dataset: str, kc: str, k: int) -> int:
    h = hashlib.sha256(f"{dataset}|{kc}|{k}|a9".encode()).hexdigest()
    return int(h[:8], 16) % (2**31)


def load_pred_kcs(ds: str) -> set[str]:
    sets = []
    for m in PRED_MODELS:
        p = pred_path(ds, m)
        if not p.exists():
            raise FileNotFoundError(p)
        kcs = pd.read_csv(p, usecols=["kc_id"])["kc_id"].map(kc_key)
        sets.append(set(kcs))
    return sets[0] & sets[1]


def select_dataset(ds: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = split_dir(ds)
    train = pd.read_csv(d / "train.csv", usecols=["kc_id", "correct"])
    test = pd.read_csv(d / "test.csv", usecols=["kc_id", "correct"])
    train["kc_id"] = train["kc_id"].map(kc_key)
    test["kc_id"] = test["kc_id"].map(kc_key)
    pred_kcs = load_pred_kcs(ds)

    tr = train.groupby("kc_id").agg(
        train_freq=("correct", "size"),
        train_correct_rate=("correct", "mean"),
    )
    te = test.groupby("kc_id").agg(
        test_n=("correct", "size"),
        test_pos=("correct", "sum"),
    )
    te["test_neg"] = te["test_n"] - te["test_pos"]
    tab = tr.join(te, how="inner").reset_index()
    tab["difficulty_proxy"] = 1.0 - tab["train_correct_rate"]
    tab["in_official_preds"] = tab["kc_id"].isin(pred_kcs)

    eligible = tab[
        (tab["train_freq"] >= 500)
        & (tab["test_n"] >= 100)
        & (tab["test_pos"] >= 20)
        & (tab["test_neg"] >= 20)
        & (tab["in_official_preds"])
    ].copy()
    eligible["eligible"] = True
    tab["eligible"] = tab["kc_id"].isin(eligible["kc_id"])

    if len(eligible) <= MAX_SELECTED:
        selected = eligible.sort_values("kc_id")
        rule = "all_eligible"
    else:
        eligible = eligible.copy()
        eligible["tert"] = pd.qcut(
            eligible["difficulty_proxy"], 3, labels=["T1_easier", "T2", "T3_harder"], duplicates="drop"
        )
        parts = []
        for _, g in eligible.groupby("tert", observed=True):
            g = g.sort_values("kc_id").head(MAX_PER_TERTILE)
            parts.append(g)
        selected = pd.concat(parts, ignore_index=True).sort_values("kc_id")
        rule = f"difficulty_tertiles_top{MAX_PER_TERTILE}_by_kc_id"

    selected = selected.copy()
    selected["selection_rule"] = rule
    selected["dataset"] = ds
    tab["dataset"] = ds
    return tab, selected


def downsample_train(ds: str, selected: pd.DataFrame) -> pd.DataFrame:
    d = split_dir(ds)
    train = pd.read_csv(d / "train.csv")
    train["_kc"] = train["kc_id"].map(kc_key)
    selected_ids = set(selected["kc_id"])
    freq = selected.set_index("kc_id")["train_freq"].to_dict()

    plans = []
    dest_root = ROOT / "data" / "processed" / "a9" / ds
    # Copy val/test only for reduced levels. full uses the official fold_0 files.
    for split_name in ("valid.csv", "test.csv"):
        src = d / split_name
        for k in TARGETS:
            dest = dest_root / f"t{k}" / SPLIT / f"fold_{FOLD}"
            dest.mkdir(parents=True, exist_ok=True)
            if not (dest / split_name).exists():
                (dest / split_name).write_bytes(src.read_bytes())

    for _, row in selected.iterrows():
        plans.append(
            {
                "dataset": ds,
                "kc_id": row["kc_id"],
                "level": "full",
                "n_full": int(row["train_freq"]),
                "n_keep": int(row["train_freq"]),
                "n_drop": 0,
                "feasible": True,
                "rng_salt": None,
            }
        )

    others = train[~train["_kc"].isin(selected_ids)]
    for k in TARGETS:
        keep_parts = [others]
        for kc in sorted(selected_ids):
            n_full = int(freq[kc])
            feasible = n_full > k
            n_keep = k if feasible else n_full
            sub = train[train["_kc"] == kc]
            if feasible:
                s = salt(ds, kc, k)
                rng = np.random.default_rng(s)
                pick = rng.choice(len(sub), size=n_keep, replace=False)
                pick.sort()
                keep_parts.append(sub.iloc[pick])
            else:
                keep_parts.append(sub)
            plans.append(
                {
                    "dataset": ds,
                    "kc_id": kc,
                    "level": f"t{k}",
                    "n_full": n_full,
                    "n_keep": n_keep,
                    "n_drop": n_full - n_keep,
                    "feasible": bool(feasible),
                    "rng_salt": salt(ds, kc, k) if feasible else None,
                }
            )
        out = pd.concat(keep_parts, axis=0)
        out = out.sort_index()
        out = out.drop(columns=["_kc"])
        dest = dest_root / f"t{k}" / SPLIT / f"fold_{FOLD}"
        dest.mkdir(parents=True, exist_ok=True)
        out.to_csv(dest / "train.csv", index=False)
        print(f"  {ds} t{k}: train rows {len(out)} (original {len(train)})")

    return pd.DataFrame(plans)


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--dataset", nargs="*", default=DATASETS, choices=DATASETS)
    args = p.parse_args()

    all_cand = []
    all_sel = []
    all_plan = []
    for ds in args.dataset:
        print(f"Selecting {ds}")
        cand, sel = select_dataset(ds)
        print(f"  eligible {int(cand['eligible'].sum())} selected {len(sel)} rule={sel['selection_rule'].iloc[0]}")
        all_cand.append(cand)
        all_sel.append(sel)
        print(f"Downsampling {ds}")
        all_plan.append(downsample_train(ds, sel))

    # Merge with any existing tables if running a subset
    def write_or_merge(path, new_df, keys):
        if path.exists() and set(new_df["dataset"].unique()) != set(DATASETS):
            old = pd.read_csv(path)
            old = old[~old["dataset"].isin(new_df["dataset"].unique())]
            new_df = pd.concat([old, new_df], ignore_index=True)
        new_df.to_csv(path, index=False)

    write_or_merge(OUT / "kc_eligibility.csv", pd.concat(all_cand, ignore_index=True), ["dataset", "kc_id"])
    write_or_merge(OUT / "selected_kcs.csv", pd.concat(all_sel, ignore_index=True), ["dataset", "kc_id"])
    write_or_merge(MAN / "downsample_plan.csv", pd.concat(all_plan, ignore_index=True), ["dataset", "kc_id", "level"])
    print("A9 selection + downsample complete. Official train.csv files were not modified.")


if __name__ == "__main__":
    main()
