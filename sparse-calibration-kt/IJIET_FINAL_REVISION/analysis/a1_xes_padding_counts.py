#!/usr/bin/env python3
"""A1: count XES3G5M -1 / selectmask rows without retraining."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REV = ROOT / "IJIET_FINAL_REVISION"
OUT_CSV = REV / "analysis" / "xes_padding_counts.csv"

INTER = ROOT / "data" / "processed" / "xes3g5m" / "interactions.csv"
RAW_FLAT = ROOT / "data" / "raw" / "xes3g5m" / "raw_data.csv"
TV = ROOT / "data" / "raw" / "xes3g5m" / "kc_level" / "train_valid_sequences.csv"
TE = ROOT / "data" / "raw" / "xes3g5m" / "kc_level" / "test.csv"
STRATA = ROOT / "results" / "tables" / "kc_strata.csv"
A9_ELIG = ROOT / "analysis" / "a9" / "kc_eligibility.csv"
A9_SEL = ROOT / "analysis" / "a9" / "selected_kcs.csv"


def is_pad(s: pd.Series) -> pd.Series:
    t = s.astype(str).str.replace(r"\.0$", "", regex=True)
    return t.isin(["-1", "nan", "None", ""])


def split_counts(split: str, fold: int) -> dict:
    d = ROOT / "data" / "processed" / "xes3g5m" / "splits" / split / f"fold_{fold}"
    out = {}
    for name in ("train", "valid", "test"):
        p = d / f"{name}.csv"
        if not p.exists():
            out[f"{split}_f{fold}_{name}_rows"] = None
            out[f"{split}_f{fold}_{name}_pad"] = None
            continue
        df = pd.read_csv(p, usecols=["kc_id", "item_id", "correct"])
        pad = is_pad(df["kc_id"])
        out[f"{split}_f{fold}_{name}_rows"] = int(len(df))
        out[f"{split}_f{fold}_{name}_pad"] = int(pad.sum())
        out[f"{split}_f{fold}_{name}_pad_all_y0"] = bool((df.loc[pad, "correct"] == 0).all()) if pad.any() else None
    return out


def pred_counts() -> dict:
    out = {}
    jobs = [
        ("learner_based", 42, "dkt"),
        ("learner_based", 42, "simplekt"),
        ("learner_based", 42, "irt_1pl"),
        ("temporal", 42, "dkt"),
        ("temporal", 42, "simplekt"),
    ]
    pred_dir = ROOT / "results" / "predictions"
    for split, seed, model in jobs:
        for name in (
            f"xes3g5m_{split}_{model}_seed{seed}_predictions_rerun.csv",
            f"xes3g5m_{split}_{model}_seed{seed}.csv",
        ):
            p = pred_dir / name
            if p.exists():
                break
        else:
            out[f"pred_{split}_{model}_seed{seed}_rows"] = None
            continue
        df = pd.read_csv(p, usecols=["kc_id", "y_true", "p_pred"])
        pad = is_pad(df["kc_id"])
        key = f"pred_{split}_{model}_seed{seed}"
        out[f"{key}_file"] = p.name
        out[f"{key}_rows"] = int(len(df))
        out[f"{key}_pad"] = int(pad.sum())
        if pad.any():
            sub = df.loc[pad]
            out[f"{key}_pad_mean_y"] = float(sub["y_true"].mean())
            out[f"{key}_pad_mean_p"] = float(sub["p_pred"].mean())
        else:
            out[f"{key}_pad_mean_y"] = None
            out[f"{key}_pad_mean_p"] = None
    return out


def expand_selectmasks() -> dict:
    out = {
        "tv_sequences": None,
        "te_sequences": None,
        "tv_tokens": None,
        "te_tokens": None,
        "concept_m1": None,
        "question_m1": None,
        "response_m1": None,
        "selectmask_ne_1": None,
        "selectmask_present": None,
        "overlap_concept_m1_and_smask_ne1": None,
        "smask_ne1_not_concept_m1": None,
        "concept_m1_not_smask_ne1": None,
        "is_repeat_nonzero": None,
    }
    if not TV.exists():
        out["raw_kc_level_present"] = False
        return out
    out["raw_kc_level_present"] = True

    def flatten(path: Path, has_sm: bool) -> pd.DataFrame:
        df = pd.read_csv(path)
        rows = []
        for _, row in df.iterrows():
            q = str(row["questions"]).split(",")
            c = str(row["concepts"]).split(",")
            r = str(row["responses"]).split(",")
            n = min(len(q), len(c), len(r))
            if has_sm and "selectmasks" in row.index and pd.notna(row["selectmasks"]):
                sm = str(row["selectmasks"]).split(",")
            else:
                sm = ["NA"] * n
            if "is_repeat" in row.index and pd.notna(row.get("is_repeat")):
                ir = str(row["is_repeat"]).split(",")
            else:
                ir = ["NA"] * n
            n = min(n, len(sm), len(ir))
            for i in range(n):
                rows.append((q[i], c[i], r[i], sm[i], ir[i]))
        return pd.DataFrame(rows, columns=["q", "c", "r", "sm", "ir"])

    tv = flatten(TV, True)
    te = flatten(TE, "selectmasks" in pd.read_csv(TE, nrows=0).columns)
    all_ = pd.concat([tv, te], ignore_index=True)
    out["tv_sequences"] = int(len(pd.read_csv(TV, usecols=[0])))
    out["te_sequences"] = int(len(pd.read_csv(TE, usecols=[0])))
    out["tv_tokens"] = int(len(tv))
    out["te_tokens"] = int(len(te))
    c_m1 = tv["c"].eq("-1") | te["c"].eq("-1") if False else all_["c"].eq("-1")
    # tv-only vs all
    out["concept_m1"] = int((all_["c"] == "-1").sum())
    out["question_m1"] = int((all_["q"] == "-1").sum())
    out["response_m1"] = int((all_["r"] == "-1").sum())
    sm_avail = all_["sm"] != "NA"
    out["selectmask_present"] = int(sm_avail.sum())
    sm_ne1 = sm_avail & (all_["sm"] != "1")
    out["selectmask_ne_1"] = int(sm_ne1.sum())
    cpad = all_["c"] == "-1"
    out["overlap_concept_m1_and_smask_ne1"] = int((cpad & sm_ne1).sum())
    out["smask_ne1_not_concept_m1"] = int((sm_ne1 & ~cpad).sum())
    out["concept_m1_not_smask_ne1"] = int((cpad & sm_avail & ~sm_ne1).sum())
    out["is_repeat_nonzero"] = int(all_["ir"].isin(["1", "1.0"]).sum())
    out["tv_concept_m1"] = int((tv["c"] == "-1").sum())
    out["te_concept_m1"] = int((te["c"] == "-1").sum())
    return out


def main() -> None:
    rows = []

    inter = pd.read_csv(INTER, usecols=["user_id", "item_id", "kc_id", "correct"])
    pad = is_pad(inter["kc_id"])
    item_pad = is_pad(inter["item_id"])
    n = len(inter)
    n_pad = int(pad.sum())
    rows.append(("processed_interactions", n, "data/processed/xes3g5m/interactions.csv"))
    rows.append(("unique_kc_including_pad", int(inter["kc_id"].nunique()), "nunique kc_id"))
    rows.append(("unique_real_kcs_excl_-1", int(inter.loc[~pad, "kc_id"].nunique()), "official 865"))
    rows.append(("unique_item_including_pad", int(inter["item_id"].nunique()), "nunique item_id"))
    rows.append(("unique_real_items_excl_-1", int(inter.loc[~item_pad, "item_id"].nunique()), "official 7652"))
    rows.append(("padding_kc_-1_rows", n_pad, "kc_id in {-1}"))
    rows.append(("padding_item_-1_rows", int(item_pad.sum()), "item_id in {-1}"))
    rows.append(("pad_kc_and_item_overlap", int((pad & item_pad).sum()), "both -1"))
    rows.append(("pad_kc_not_item", int((pad & ~item_pad).sum()), ""))
    rows.append(("pad_item_not_kc", int((~pad & item_pad).sum()), ""))
    rows.append(("valid_nonpadding_rows", n - n_pad, "kc_id not -1"))
    rows.append(("padding_pct_of_processed", round(100.0 * n_pad / n, 4), "percent"))
    rows.append(("pad_correct_mean", float(inter.loc[pad, "correct"].mean()) if n_pad else None, "after preprocess 0/1"))
    rows.append(("n_users", int(inter["user_id"].nunique()), ""))

    for split, fold in (("learner_based", 0), ("learner_based", 1), ("temporal", 0)):
        for k, v in split_counts(split, fold).items():
            rows.append((k, v, f"splits/{split}/fold_{fold}"))

    for k, v in pred_counts().items():
        rows.append((k, v, "results/predictions"))

    if STRATA.exists():
        s = pd.read_csv(STRATA)
        s = s[(s["dataset"] == "xes3g5m") & (s["kc_id"].astype(str).str.replace(r"\.0$", "", regex=True) == "-1")]
        for _, r in s.iterrows():
            rows.append(
                (
                    f"strata_{r['split']}_f{int(r['fold'])}_kc-1",
                    f"train={int(r['train_freq'])};valid={int(r['valid_freq'])};test={int(r['test_freq'])};bucket={r['bucket']}",
                    "kc_strata.csv",
                )
            )

    if A9_ELIG.exists():
        e = pd.read_csv(A9_ELIG)
        e["kc"] = e["kc_id"].astype(str).str.replace(r"\.0$", "", regex=True)
        hit = e[(e["dataset"] == "xes3g5m") & (e["kc"] == "-1")]
        rows.append(("a9_elig_-1_rows", int(len(hit)), "analysis/a9/kc_eligibility.csv"))
        if len(hit):
            rows.append(("a9_elig_-1_eligible_flag", bool(hit.iloc[0].get("eligible", False)), str(hit.iloc[0].to_dict())))
    if A9_SEL.exists():
        sel = pd.read_csv(A9_SEL)
        sel["kc"] = sel["kc_id"].astype(str).str.replace(r"\.0$", "", regex=True)
        rows.append(
            ("a9_selected_contains_-1", bool(((sel["dataset"] == "xes3g5m") & (sel["kc"] == "-1")).any()), "selected_kcs.csv")
        )

    a9_train = ROOT / "data" / "processed" / "a9" / "xes3g5m" / "t500" / "learner_based" / "fold_0" / "train.csv"
    if a9_train.exists():
        t = pd.read_csv(a9_train, usecols=["kc_id"])
        rows.append(("a9_t500_train_rows", int(len(t)), str(a9_train)))
        rows.append(("a9_t500_train_pad", int(is_pad(t["kc_id"]).sum()), "others kept in downsample"))

    sm = expand_selectmasks()
    for k, v in sm.items():
        rows.append((k, v, "kc_level sequences"))

    df = pd.DataFrame(rows, columns=["metric", "value", "note"])
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(df.to_string(index=False))
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    main()
