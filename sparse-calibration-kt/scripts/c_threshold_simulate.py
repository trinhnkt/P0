#!/usr/bin/env python3
"""Direction C: global-tau mastery/remediation errors by KC-frequency stratum.

Reads existing prediction CSVs. Does not train. Pre-reg:
analysis/direction_c_preregister.md
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
STRATA_PATH = ROOT / "results" / "tables" / "kc_strata.csv"
OUT = ROOT / "analysis" / "direction_c"

TAUS = (0.5, 0.6, 0.7, 0.8)
DISPLAY_TAU = 0.7
SPLIT, FOLD, SEED = "learner_based", 0, 42
BUCKETS = ["all", "dense", "medium", "sparse", "very_sparse", "strict_cold_start"]
USECOLS = ["model", "kc_id", "y_true", "p_pred"]

JOBS = [
    {
        "dataset": "assist2012",
        "models": ["dkt", "simplekt", "irt_1pl", "gkt_train_only", "cl4kt", "gkt_full_log"],
        "primary": {"dkt", "simplekt"},
        "secondary": {"gkt_train_only", "cl4kt"},
        "ablation": {"gkt_full_log"},
    },
    {
        "dataset": "junyi",
        "models": ["dkt", "simplekt"],
        "primary": {"dkt", "simplekt"},
        "secondary": set(),
        "ablation": set(),
    },
    {
        "dataset": "xes3g5m",
        "models": ["dkt", "simplekt"],
        "primary": {"dkt", "simplekt"},
        "secondary": set(),
        "ablation": set(),
    },
]


def flag(n: int) -> str:
    if n >= 1000:
        return "R"
    if n >= 100:
        return "L"
    return "I"


def kc_key(x) -> str:
    return str(x).replace(".0", "")


def role_of(job: dict, model: str) -> str:
    if model in job["ablation"]:
        return "ablation"
    if model in job["secondary"]:
        return "secondary"
    if model in job["primary"]:
        return "primary"
    return "other"


def pred_path(dataset: str, model: str) -> Path:
    for name in (
        f"{dataset}_{SPLIT}_{model}_seed{SEED}_predictions_rerun.csv",
        f"{dataset}_{SPLIT}_{model}_seed{SEED}.csv",
    ):
        p = PRED / name
        if p.exists():
            return p
    raise FileNotFoundError(f"{dataset}/{model}")


def load_strata(dataset: str) -> dict[str, int]:
    s = pd.read_csv(STRATA_PATH)
    s = s[(s["dataset"] == dataset) & (s["split"] == SPLIT) & (s["fold"] == FOLD)]
    return {kc_key(r["kc_id"]): int(r["train_freq"]) for _, r in s.iterrows()}


def rates(y: np.ndarray, p: np.ndarray, tau: float) -> dict:
    y = y.astype(int)
    p = p.astype(float)
    n = int(y.size)
    if n == 0:
        return {
            "n_events": 0,
            "mean_y": np.nan,
            "mean_p": np.nan,
            "n_advance": 0,
            "n_remediate": 0,
            "FM": np.nan,
            "Miss": np.nan,
            "UR": np.nan,
            "acc_at_tau": np.nan,
            "E_FM_calibrated": np.nan,
            "excess_FM": np.nan,
        }
    advance = p >= tau
    n_adv = int(advance.sum())
    n_rem = n - n_adv
    y0 = y == 0
    y1 = y == 1
    n_inc = int(y0.sum())
    n_cor = int(y1.sum())
    fm = float((y0 & advance).sum() / n_adv) if n_adv else np.nan
    miss = float((y0 & advance).sum() / n_inc) if n_inc else np.nan
    ur = float((y1 & ~advance).sum() / n_cor) if n_cor else np.nan
    pred_pos = advance.astype(int)
    e_fm = float((1.0 - p[advance]).mean()) if n_adv else np.nan
    return {
        "n_events": n,
        "mean_y": float(y.mean()),
        "mean_p": float(p.mean()),
        "n_advance": n_adv,
        "n_remediate": n_rem,
        "FM": fm,
        "Miss": miss,
        "UR": ur,
        "acc_at_tau": float((pred_pos == y).mean()),
        "E_FM_calibrated": e_fm,
        "excess_FM": (fm - e_fm) if n_adv else np.nan,
    }


def score_file(dataset: str, model: str, path: Path, strata: dict, role: str) -> list[dict]:
    df = pd.read_csv(path, usecols=USECOLS)
    df = df.dropna(subset=["y_true", "p_pred"])
    freqs = df["kc_id"].map(lambda k: strata.get(kc_key(k), 0))
    df = df.assign(bucket=freqs.map(get_bucket))
    rows = []
    for tau in TAUS:
        y_all = df["y_true"].to_numpy()
        p_all = df["p_pred"].to_numpy()
        rec = rates(y_all, p_all, tau)
        rec.update(
            {
                "dataset": dataset,
                "model": model,
                "role": role,
                "tau": tau,
                "bucket": "all",
                "flag": flag(rec["n_events"]),
                "n_kcs": int(df["kc_id"].nunique()),
            }
        )
        rows.append(rec)
        for b in BUCKETS[1:]:
            sub = df[df["bucket"] == b]
            rec = rates(sub["y_true"].to_numpy(), sub["p_pred"].to_numpy(), tau)
            rec.update(
                {
                    "dataset": dataset,
                    "model": model,
                    "role": role,
                    "tau": tau,
                    "bucket": b,
                    "flag": flag(rec["n_events"]),
                    "n_kcs": int(sub["kc_id"].nunique()) if rec["n_events"] else 0,
                }
            )
            rows.append(rec)
    return rows


def gaps_from(tab: pd.DataFrame) -> pd.DataFrame:
    recs = []
    keys = tab[["dataset", "model", "role", "tau"]].drop_duplicates()
    for _, k in keys.iterrows():
        sub = tab[
            (tab["dataset"] == k["dataset"])
            & (tab["model"] == k["model"])
            & (tab["tau"] == k["tau"])
        ]
        dense = sub[sub["bucket"] == "dense"]
        sparse = sub[sub["bucket"] == "sparse"]
        if dense.empty:
            continue
        d = dense.iloc[0]
        if sparse.empty or sparse.iloc[0]["n_events"] == 0:
            recs.append(
                {
                    "dataset": k["dataset"],
                    "model": k["model"],
                    "role": k["role"],
                    "tau": k["tau"],
                    "sparse_n": 0,
                    "sparse_flag": "empty",
                    "dense_n": int(d["n_events"]),
                    "dense_flag": d["flag"],
                    "FM_sparse": np.nan,
                    "FM_dense": d["FM"],
                    "dFM": np.nan,
                    "Miss_sparse": np.nan,
                    "Miss_dense": d["Miss"],
                    "dMiss": np.nan,
                    "UR_sparse": np.nan,
                    "UR_dense": d["UR"],
                    "dUR": np.nan,
                }
            )
            continue
        s = sparse.iloc[0]
        recs.append(
            {
                "dataset": k["dataset"],
                "model": k["model"],
                "role": k["role"],
                "tau": k["tau"],
                "sparse_n": int(s["n_events"]),
                "sparse_flag": s["flag"],
                "dense_n": int(d["n_events"]),
                "dense_flag": d["flag"],
                "FM_sparse": s["FM"],
                "FM_dense": d["FM"],
                "dFM": (s["FM"] - d["FM"]) if pd.notna(s["FM"]) and pd.notna(d["FM"]) else np.nan,
                "Miss_sparse": s["Miss"],
                "Miss_dense": d["Miss"],
                "dMiss": (s["Miss"] - d["Miss"]) if pd.notna(s["Miss"]) and pd.notna(d["Miss"]) else np.nan,
                "UR_sparse": s["UR"],
                "UR_dense": d["UR"],
                "dUR": (s["UR"] - d["UR"]) if pd.notna(s["UR"]) and pd.notna(d["UR"]) else np.nan,
            }
        )
    return pd.DataFrame(recs)


def cell(gaps: pd.DataFrame, dataset: str, model: str, tau: float):
    hit = gaps[
        (gaps["dataset"] == dataset)
        & (gaps["model"] == model)
        & np.isclose(gaps["tau"].astype(float), tau)
    ]
    return None if hit.empty else hit.iloc[0]


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and (np.isnan(x) or pd.isna(x))):
        return "NA"
    return f"{x:.{nd}f}"


def verdict(gaps: pd.DataFrame) -> list[str]:
    lines = []
    sk = cell(gaps, "assist2012", "simplekt", DISPLAY_TAU)
    dkt = cell(gaps, "assist2012", "dkt", DISPLAY_TAU)
    gkt = cell(gaps, "assist2012", "gkt_train_only", DISPLAY_TAU)
    cl4 = cell(gaps, "assist2012", "cl4kt", DISPLAY_TAU)
    jun = cell(gaps, "junyi", "simplekt", DISPLAY_TAU)
    xes = cell(gaps, "xes3g5m", "simplekt", DISPLAY_TAU)

    def c1_on(row, name):
        if row is None:
            lines.append(f"{name}: missing")
            return False, None
        ok_occ = row["sparse_flag"] in {"L", "R"}
        dfm, dm = row["dFM"], row["dMiss"]
        c1 = bool(ok_occ and ((pd.notna(dfm) and dfm > 0) or (pd.notna(dm) and dm > 0)))
        which = []
        if pd.notna(dfm) and dfm > 0:
            which.append("dFM")
        if pd.notna(dm) and dm > 0:
            which.append("dMiss")
        used = which[0] if which else None
        lines.append(
            f"C1 {name} tau={DISPLAY_TAU}: sparse N={int(row['sparse_n'])} flag={row['sparse_flag']} "
            f"dFM={fmt(dfm)} dMiss={fmt(dm)} -> {'PASS' if c1 else 'no'} (co-primary {used or 'none'})"
        )
        return c1, used

    c1, used = c1_on(sk, "assist2012 SimpleKT")
    if dkt is not None:
        lines.append(
            f"    DKT same tau: dFM={fmt(dkt['dFM'])} dMiss={fmt(dkt['dMiss'])} flag={dkt['sparse_flag']}"
        )

    c2 = False
    if c1 and gkt is not None and used is not None:
        col = used
        if pd.notna(sk[col]) and pd.notna(gkt[col]) and gkt["sparse_flag"] in {"L", "R"}:
            c2 = float(gkt[col]) < float(sk[col])
        lines.append(
            f"C2 GKT train-only vs SimpleKT on {col}: "
            f"GKT {fmt(gkt[col])} vs SimpleKT {fmt(sk[col])} -> {'PASS' if c2 else 'no'}"
        )
    elif gkt is not None:
        lines.append(
            f"C2 skipped (C1 failed or unused). GKT dFM={fmt(gkt['dFM'])} dMiss={fmt(gkt['dMiss'])}"
        )
    if cl4 is not None:
        lines.append(
            f"    CL4KT descriptive: dFM={fmt(cl4['dFM'])} dMiss={fmt(cl4['dMiss'])} flag={cl4['sparse_flag']}"
        )

    c3_i = False
    if jun is None:
        lines.append("C3 Junyi SimpleKT: missing file")
    elif jun["sparse_flag"] == "empty" or int(jun["sparse_n"]) == 0:
        lines.append("C3(i) Junyi SimpleKT sparse empty -> C1 not applicable (PASS emptiness)")
        c3_i = True
    else:
        lines.append(
            f"C3(i) Junyi SimpleKT unexpected sparse N={int(jun['sparse_n'])} -> check strata"
        )

    c3_ii = False
    if xes is None or sk is None:
        lines.append("C3(ii) XES SimpleKT: missing")
    elif xes["sparse_flag"] not in {"L", "R"}:
        lines.append(
            f"C3(ii) XES SimpleKT sparse flag={xes['sparse_flag']} N={int(xes['sparse_n'])} -> no |gap| test"
        )
    else:
        a_fm, a_ms = abs(sk["dFM"]) if pd.notna(sk["dFM"]) else np.nan, abs(sk["dMiss"]) if pd.notna(sk["dMiss"]) else np.nan
        x_fm, x_ms = abs(xes["dFM"]) if pd.notna(xes["dFM"]) else np.nan, abs(xes["dMiss"]) if pd.notna(xes["dMiss"]) else np.nan
        c3_ii = (
            pd.notna(a_fm)
            and pd.notna(a_ms)
            and pd.notna(x_fm)
            and pd.notna(x_ms)
            and (x_fm < a_fm)
            and (x_ms < a_ms)
        )
        lines.append(
            f"C3(ii) XES |dFM|={fmt(x_fm)} |dMiss|={fmt(x_ms)} vs ASSISTments "
            f"|dFM|={fmt(a_fm)} |dMiss|={fmt(a_ms)} -> {'PASS' if c3_ii else 'no'}"
        )
    c3 = bool(c3_i and c3_ii) if jun is not None else False
    lines.append(f"C3 overall: {'PASS' if c3 else 'no'} (need emptiness AND smaller XES gaps)")
    lines.append("C3 not retuned after seeing XES |dMiss|; ECE-flat does not imply Miss-flat.")
    lines.append(f"Direction C punchline this run: {'YES (C1)' if c1 else 'NULL / C1 failed'}")
    return lines


def tex_tau07(tab: pd.DataFrame) -> str:
    sub = tab[
        (tab["dataset"] == "assist2012")
        & np.isclose(tab["tau"].astype(float), DISPLAY_TAU)
        & (tab["bucket"].isin(["dense", "sparse"]))
        & (tab["model"].isin(["dkt", "simplekt", "gkt_train_only", "cl4kt"]))
    ].copy()
    order = ["simplekt", "dkt", "gkt_train_only", "cl4kt"]
    lines = [
        r"\begin{table}[htbp]",
        r"\caption{Simulated global-threshold decision error at $\tau=0.7$ on ASSISTments 2012, learner-based fold 0. FM $=P(y=0\mid p\ge\tau)$; $E[\mathrm{FM}]$ is $E[1-p\mid p\ge\tau]$ (calibrated advance error). Miss $=P(p\ge\tau\mid y=0)$. Sparse $N=444$ is Limited. GKT uses the train-only graph. CL4KT is a protocol adapter.}",
        r"\label{tab:c_tau07}",
        r"\centering",
        r"\footnotesize",
        r"\begin{tabular}{llrrrrrr}",
        r"\toprule",
        r"Model & Stratum & Flag & $N$ & FM & $E[\mathrm{FM}]$ & Miss & UR \\",
        r"\midrule",
    ]
    labels = {
        "simplekt": "SimpleKT",
        "dkt": "DKT",
        "gkt_train_only": "GKT (train-only)",
        "cl4kt": "CL4KT (adapter)",
    }
    for m in order:
        for b in ("dense", "sparse"):
            hit = sub[(sub["model"] == m) & (sub["bucket"] == b)]
            if hit.empty:
                continue
            r = hit.iloc[0]
            lines.append(
                f"{labels[m]} & {b} & {r['flag']} & {int(r['n_events'])} & "
                f"{fmt(r['FM'])} & {fmt(r['E_FM_calibrated'])} & {fmt(r['Miss'])} & {fmt(r['UR'])} \\\\"
            )
        lines.append(r"\midrule")
    if lines[-1] == r"\midrule":
        lines[-1] = r"\bottomrule"
    lines.extend(
        [
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for job in JOBS:
        ds = job["dataset"]
        print(f"strata {ds}", flush=True)
        strata = load_strata(ds)
        for model in job["models"]:
            try:
                path = pred_path(ds, model)
            except FileNotFoundError:
                print(f"missing {ds}/{model}", flush=True)
                continue
            print(f"score {path.name}", flush=True)
            rows.extend(score_file(ds, model, path, strata, role_of(job, model)))
    if not rows:
        raise SystemExit("no prediction files")
    tab = pd.DataFrame(rows)
    cols = [
        "dataset",
        "model",
        "role",
        "tau",
        "bucket",
        "flag",
        "n_kcs",
        "n_events",
        "mean_y",
        "mean_p",
        "n_advance",
        "n_remediate",
        "FM",
        "Miss",
        "UR",
        "acc_at_tau",
        "E_FM_calibrated",
        "excess_FM",
    ]
    tab = tab[cols]
    tab.to_csv(OUT / "threshold_rates.csv", index=False)
    g = gaps_from(tab)
    g.to_csv(OUT / "sparse_dense_gaps.csv", index=False)
    lines = verdict(g)
    # Calibration excess at display tau (not a C1–C3 criterion).
    for model in ("simplekt", "dkt", "gkt_train_only", "cl4kt"):
        for b in ("dense", "sparse"):
            hit = tab[
                (tab["dataset"] == "assist2012")
                & (tab["model"] == model)
                & np.isclose(tab["tau"].astype(float), DISPLAY_TAU)
                & (tab["bucket"] == b)
            ]
            if hit.empty:
                continue
            r = hit.iloc[0]
            lines.append(
                f"excess_FM assist2012 {model} {b}: FM={fmt(r['FM'])} "
                f"E[FM]={fmt(r['E_FM_calibrated'])} excess={fmt(r['excess_FM'])} "
                f"n_advance={int(r['n_advance'])}"
            )
    (OUT / "c1_c3_verdict.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "table_c_tau07.tex").write_text(tex_tau07(tab), encoding="utf-8")
    show = g[np.isclose(g["tau"].astype(float), DISPLAY_TAU)]
    print(show.to_string(index=False))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
