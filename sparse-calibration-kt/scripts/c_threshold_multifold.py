#!/usr/bin/env python3
"""C2 robustness: five-fold ΔFM at τ=0.7 plus seed-42 KC-clustered bootstrap.

Addendum: analysis/direction_c_preregister.md
Does not train. Does not retune C1–C3.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.kc_strata import get_bucket  # noqa: E402

PRED = ROOT / "results" / "predictions"
DATA = ROOT / "data" / "processed"
OUT = ROOT / "analysis" / "direction_c"

SPLIT = "learner_based"
DISPLAY_TAU = 0.7
SEEDS = (42, 2024, 2025, 2026, 2027)
USECOLS = ["kc_id", "y_true", "p_pred"]
BOOT_B = 2000
BOOT_RNG = 0

DATASETS = ("assist2012", "junyi", "xes3g5m")
MODELS = ("dkt", "simplekt")


def flag(n: int) -> str:
    if n >= 1000:
        return "R"
    if n >= 100:
        return "L"
    return "I"


def kc_key(x) -> str:
    return str(x).replace(".0", "")


def pred_path(dataset: str, model: str, seed: int) -> Path:
    for name in (
        f"{dataset}_{SPLIT}_{model}_seed{seed}_predictions_rerun.csv",
        f"{dataset}_{SPLIT}_{model}_seed{seed}.csv",
    ):
        p = PRED / name
        if p.exists():
            return p
    raise FileNotFoundError(f"{dataset}/{model}/seed{seed}")


def train_freq_map(dataset: str, fold: int) -> dict[str, int]:
    train = pd.read_csv(
        DATA / dataset / "splits" / SPLIT / f"fold_{fold}" / "train.csv",
        usecols=["kc_id"],
    )
    vc = train["kc_id"].map(kc_key).value_counts()
    return {k: int(v) for k, v in vc.items()}


def fm_miss(y: np.ndarray, p: np.ndarray, tau: float) -> tuple[float, float, int, int]:
    y = y.astype(int)
    p = p.astype(float)
    adv = p >= tau
    n_adv = int(adv.sum())
    n_inc = int((y == 0).sum())
    fm = float(((y == 0) & adv).sum() / n_adv) if n_adv else np.nan
    miss = float(((y == 0) & adv).sum() / n_inc) if n_inc else np.nan
    return fm, miss, n_adv, int(y.size)


def attach_buckets(df: pd.DataFrame, freq: dict[str, int]) -> pd.DataFrame:
    f = df["kc_id"].map(lambda k: freq.get(kc_key(k), 0))
    return df.assign(bucket=f.map(get_bucket), kc=df["kc_id"].map(kc_key))


def gap_row(dataset: str, model: str, seed: int, fold: int, df: pd.DataFrame) -> dict:
    dense = df[df["bucket"] == "dense"]
    sparse = df[df["bucket"] == "sparse"]
    y_d, p_d = dense["y_true"].to_numpy(), dense["p_pred"].to_numpy()
    y_s, p_s = sparse["y_true"].to_numpy(), sparse["p_pred"].to_numpy()
    fm_d, miss_d, nadv_d, n_d = fm_miss(y_d, p_d, DISPLAY_TAU)
    fm_s, miss_s, nadv_s, n_s = fm_miss(y_s, p_s, DISPLAY_TAU)
    e_s = float((1.0 - p_s[p_s >= DISPLAY_TAU]).mean()) if nadv_s else np.nan
    e_d = float((1.0 - p_d[p_d >= DISPLAY_TAU]).mean()) if nadv_d else np.nan
    return {
        "dataset": dataset,
        "model": model,
        "seed": seed,
        "fold": fold,
        "tau": DISPLAY_TAU,
        "sparse_n": n_s,
        "sparse_flag": flag(n_s) if n_s else "empty",
        "sparse_n_advance": nadv_s,
        "dense_n": n_d,
        "FM_sparse": fm_s,
        "FM_dense": fm_d,
        "dFM": (fm_s - fm_d) if pd.notna(fm_s) and pd.notna(fm_d) else np.nan,
        "Miss_sparse": miss_s,
        "Miss_dense": miss_d,
        "dMiss": (miss_s - miss_d) if pd.notna(miss_s) and pd.notna(miss_d) else np.nan,
        "excess_FM_sparse": (fm_s - e_s) if pd.notna(fm_s) and pd.notna(e_s) else np.nan,
        "excess_FM_dense": (fm_d - e_d) if pd.notna(fm_d) and pd.notna(e_d) else np.nan,
    }


def bootstrap_dfm(df: pd.DataFrame, mode: str, rng: np.random.Generator) -> np.ndarray:
    """mode: 'event' or 'kc'."""
    sparse = df[df["bucket"] == "sparse"]
    dense = df[df["bucket"] == "dense"]
    y_s, p_s = sparse["y_true"].to_numpy(), sparse["p_pred"].to_numpy()
    y_d, p_d = dense["y_true"].to_numpy(), dense["p_pred"].to_numpy()
    out = np.empty(BOOT_B, dtype=float)
    n_ok = 0
    if mode == "event":
        n_s, n_d = len(y_s), len(y_d)
        for _ in range(BOOT_B):
            i_s = rng.integers(0, n_s, n_s)
            i_d = rng.integers(0, n_d, n_d)
            fm_s, _, _, _ = fm_miss(y_s[i_s], p_s[i_s], DISPLAY_TAU)
            fm_d, _, _, _ = fm_miss(y_d[i_d], p_d[i_d], DISPLAY_TAU)
            if pd.notna(fm_s) and pd.notna(fm_d):
                out[n_ok] = fm_s - fm_d
                n_ok += 1
        return out[:n_ok]

    def kc_counts(sub: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        n_adv, n_fail = [], []
        for _, part in sub.groupby("kc", sort=False):
            y = part["y_true"].to_numpy()
            p = part["p_pred"].to_numpy()
            adv = p >= DISPLAY_TAU
            n_adv.append(int(adv.sum()))
            n_fail.append(int(((y == 0) & adv).sum()))
        return np.asarray(n_adv, dtype=np.int64), np.asarray(n_fail, dtype=np.int64)

    s_adv, s_fail = kc_counts(sparse)
    d_adv, d_fail = kc_counts(dense)
    ns, nd = len(s_adv), len(d_adv)
    for _ in range(BOOT_B):
        i_s = rng.integers(0, ns, ns)
        i_d = rng.integers(0, nd, nd)
        a_s, f_s = int(s_adv[i_s].sum()), int(s_fail[i_s].sum())
        a_d, f_d = int(d_adv[i_d].sum()), int(d_fail[i_d].sum())
        if a_s == 0 or a_d == 0:
            continue
        out[n_ok] = f_s / a_s - f_d / a_d
        n_ok += 1
    return out[:n_ok]


def summarize_boot(arr: np.ndarray) -> dict:
    if arr.size == 0:
        return {"n_valid": 0, "mean": np.nan, "ci_lo": np.nan, "ci_hi": np.nan}
    return {
        "n_valid": int(arr.size),
        "mean": float(arr.mean()),
        "ci_lo": float(np.quantile(arr, 0.025)),
        "ci_hi": float(np.quantile(arr, 0.975)),
    }


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and (np.isnan(x) or pd.isna(x))):
        return "NA"
    return f"{x:.{nd}f}"


def tex_fivefold(g: pd.DataFrame) -> str:
    sub = g[(g["dataset"] == "assist2012") & (g["model"].isin(["dkt", "simplekt"]))]
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Five-fold robustness of the simulated gate at $\tau=0.7$ on ASSISTments 2012 (learner-based seeds 42, 2024, 2025, 2026, 2027). $\Delta\mathrm{FM}=\mathrm{FM}_{\mathrm{sparse}}-\mathrm{FM}_{\mathrm{dense}}$. GKT and the CL4KT adapter remain a single-seed instantiation (Table~\ref{tab:c_tau07}).}",
        r"\label{tab:c_fivefold}",
        r"\centering",
        r"\footnotesize",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"Model & Mean $\Delta$FM & SD & Folds $\Delta$FM$>0$ & Mean $\Delta$Miss & SD & Mean sparse $N$ \\",
        r"\midrule",
    ]
    labels = {"simplekt": "SimpleKT", "dkt": "DKT"}
    for m in ("simplekt", "dkt"):
        hit = sub[sub["model"] == m]
        npos = int((hit["dFM"] > 0).sum())
        lines.append(
            f"{labels[m]} & {fmt(hit['dFM'].mean())} & {fmt(hit['dFM'].std(ddof=1))} & "
            f"{npos}/5 & {fmt(hit['dMiss'].mean())} & {fmt(hit['dMiss'].std(ddof=1))} & "
            f"{hit['sparse_n'].mean():.0f} \\\\"
        )
    lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    boot_rows = []
    for ds in DATASETS:
        for fold, seed in enumerate(SEEDS):
            print(f"freq {ds} fold_{fold} seed={seed}", flush=True)
            freq = train_freq_map(ds, fold)
            n_sparse_kcs = sum(1 for v in freq.values() if 20 <= v < 100)
            for model in MODELS:
                if n_sparse_kcs == 0:
                    rows.append(
                        {
                            "dataset": ds,
                            "model": model,
                            "seed": seed,
                            "fold": fold,
                            "tau": DISPLAY_TAU,
                            "sparse_n": 0,
                            "sparse_flag": "empty",
                            "sparse_n_advance": 0,
                            "dense_n": 0,
                            "FM_sparse": np.nan,
                            "FM_dense": np.nan,
                            "dFM": np.nan,
                            "Miss_sparse": np.nan,
                            "Miss_dense": np.nan,
                            "dMiss": np.nan,
                            "excess_FM_sparse": np.nan,
                            "excess_FM_dense": np.nan,
                        }
                    )
                    continue
                path = pred_path(ds, model, seed)
                print(f"  score {path.name}", flush=True)
                df = pd.read_csv(path, usecols=USECOLS).dropna(subset=["y_true", "p_pred"])
                df = attach_buckets(df, freq)
                rec = gap_row(ds, model, seed, fold, df)
                rows.append(rec)
                if ds == "assist2012" and seed == 42:
                    rng = np.random.default_rng(BOOT_RNG)
                    for mode in ("kc", "event"):
                        arr = bootstrap_dfm(df, mode, rng)
                        sm = summarize_boot(arr)
                        boot_rows.append(
                            {
                                "dataset": ds,
                                "model": model,
                                "seed": seed,
                                "mode": mode,
                                "dFM_point": rec["dFM"],
                                **sm,
                            }
                        )
                        print(
                            f"  boot {model} {mode}: {fmt(sm['mean'])} "
                            f"[{fmt(sm['ci_lo'])}, {fmt(sm['ci_hi'])}] n={sm['n_valid']}",
                            flush=True,
                        )

    g = pd.DataFrame(rows)
    g.to_csv(OUT / "fivefold_gaps.csv", index=False)
    b = pd.DataFrame(boot_rows)
    b.to_csv(OUT / "seed42_bootstrap_dfm.csv", index=False)
    (OUT / "table_c_fivefold.tex").write_text(tex_fivefold(g), encoding="utf-8")

    lines = ["C2 five-fold robustness (tau=0.7); C1–C3 not retuned."]
    for ds in DATASETS:
        for model in MODELS:
            hit = g[(g["dataset"] == ds) & (g["model"] == model)]
            n_empty = int((hit["sparse_flag"] == "empty").sum())
            usable = hit[hit["sparse_flag"].isin(["L", "R"])]
            if usable.empty:
                lines.append(f"{ds} {model}: sparse empty on {n_empty}/5 folds")
                continue
            npos = int((usable["dFM"] > 0).sum())
            lines.append(
                f"{ds} {model}: dFM mean={fmt(usable['dFM'].mean())} "
                f"sd={fmt(usable['dFM'].std(ddof=1))} "
                f"pos={npos}/{len(usable)} dMiss mean={fmt(usable['dMiss'].mean())} "
                f"sparse_n mean={usable['sparse_n'].mean():.0f}"
            )
    for _, r in b.iterrows():
        covers = (
            pd.notna(r["ci_lo"])
            and pd.notna(r["ci_hi"])
            and (r["ci_lo"] > 0 or r["ci_hi"] < 0)
        )
        zero_in = pd.notna(r["ci_lo"]) and pd.notna(r["ci_hi"]) and r["ci_lo"] <= 0 <= r["ci_hi"]
        lines.append(
            f"boot seed42 {r['model']} {r['mode']}: point={fmt(r['dFM_point'])} "
            f"CI=[{fmt(r['ci_lo'])}, {fmt(r['ci_hi'])}] "
            f"{'excludes 0' if covers else ('includes 0' if zero_in else 'NA')}"
        )
    (OUT / "c2_fivefold_verdict.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
