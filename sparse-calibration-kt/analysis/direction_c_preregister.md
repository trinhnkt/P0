# Direction C — pre-registration (locked before τ-curves are inspected)

**Goal.** Turn Finding 2 (dataset-dependent sparse ECE) and the qualitative C4 row (probabilities as remediation/mastery gates) into a **simulated decision error**: the same global threshold \(\tau\) applied to \(p\) produces different false-mastery / false-remediation rates on sparse vs dense KCs.

This is **not** an instructional RCT, **not** a new calibrator, and **not** a claim that sparse KCs universally fail. It asks whether the protocol **changes a thresholded decision** relative to looking only at aggregate AUC.

**Locked:** 2026-08-26, after Direction A scored A1–A3 NULL on ASSISTments and before this script’s per-\(\tau\) rates are read.

---

## Scope

| Item | Locked choice |
|------|----------------|
| Primary dataset | ASSISTments 2012, learner-based `fold_0` ≡ seed 42 |
| Negative controls | Junyi Academy and XES3G5M, same split/fold/seed, DKT + SimpleKT only |
| Primary models | DKT, SimpleKT (existing rerun CSVs) |
| Secondary models (ASSISTments only) | GKT **train-only** graph; CL4KT protocol adapter |
| Not primary | GKT **full-log** graph (G-L9 ablation only); GIKT; sparseKT; new GPU runs |
| Strata | `results/tables/kc_strata.csv` train-only \(f_{\mathrm{train}}\); buckets unchanged |
| Occupancy | R \(N\ge 1000\), L \(100\le N<1000\), I \(N<100\). Success claims require sparse flag L or R. Very-sparse (\(N=11\) on ASSISTments) is I — report, do not test. |
| Prediction files | Prefer `*_seed42_predictions_rerun.csv`, else `*_seed42.csv` |

Junyi learner-based sparse/very-sparse buckets are expected **empty** under pre-registered frequency cuts. That emptiness is a protocol outcome (no C1 claim), not a missing table cell to impute.

---

## Decision rule (one gate)

For each test event with predicted probability \(p\) and label \(y\in\{0,1\}\):

- \(p \ge \tau\): **advance / skip remediation** (treat as mastery-like)
- \(p < \tau\): **trigger remediation**

\(\tau\) is a **global** scalar. Sparse events never get their own tuned \(\tau\).

### Locked \(\tau\) grid

\[
\tau \in \{0.5,\ 0.6,\ 0.7,\ 0.8\}
\]

**Display threshold** (manuscript table, if numbers exist): \(\tau=0.7\). The other three values are robustness, not a search.

No \(\tau\) is selected by sparse ECE, sparse AUC, or sparse decision error.

---

## Outcomes (all reported; two co-primary)

Let \(A = \{p \ge \tau\}\) (advance).

| Name | Definition | Educational reading |
|------|------------|---------------------|
| **FM** (co-primary) | \(P(y=0 \mid A)\) | When the system skips remediation, how often was the answer wrong? |
| **Miss** (co-primary) | \(P(A \mid y=0)\) | Among actual incorrect answers, how often did the system still skip help? |
| UR (secondary) | \(P(\neg A \mid y=1)\) | Unnecessary remediation among correct answers |
| Acc@\(\tau\) (secondary) | \(P((p\ge\tau) = (y=1))\) | Thresholded accuracy |
| E[FM] if calibrated | \(E[1-p \mid A]\) | Reliability of the advance decision; compare to FM |

Empty advance set \(\Rightarrow\) FM is undefined (NaN), not zero.

**Sparse–dense gap** (model \(m\), threshold \(\tau\)):

\[
\Delta_{\mathrm{FM}}(m,\tau)=\mathrm{FM}_{\mathrm{sparse}}-\mathrm{FM}_{\mathrm{dense}},\qquad
\Delta_{\mathrm{Miss}}(m,\tau)=\mathrm{Miss}_{\mathrm{sparse}}-\mathrm{Miss}_{\mathrm{dense}}.
\]

Positive \(\Delta_{\mathrm{FM}}\) = sparse advances are dirtier than dense advances. Positive \(\Delta_{\mathrm{Miss}}\) = sparse failures are skipped more often.

---

## Success (need C1; C2/C3 are interpretation, not vetoes)

Scored **only** at \(\tau=0.7\) on occupancy-valid cells. Grid is then described, not re-used to cherry-pick a passing \(\tau\).

- **C1 Distortion (ASSISTments, SimpleKT, sparse flag L/R):** \(\Delta_{\mathrm{FM}}>0\) **or** \(\Delta_{\mathrm{Miss}}>0\). One co-primary may be null; both signs reported. Null of both = no decision-error story from Finding 2 at the display threshold.
- **C2 Model dependence (same dataset/split/τ):** GKT train-only has a **smaller** \(\Delta_{\mathrm{FM}}\) than SimpleKT **or** a smaller \(\Delta_{\mathrm{Miss}}\) than SimpleKT (whichever co-primary C1 used). CL4KT is descriptive. This does **not** claim GKT is SOTA; it asks whether the architecture that closed sparse ECE also shrinks the gate error.
- **C3 Dataset dependence:** (i) Junyi sparse empty → C1 **not applicable**. (ii) XES3G5M SimpleKT: \(|\Delta_{\mathrm{FM}}|\) and \(|\Delta_{\mathrm{Miss}}|\) both **strictly smaller** than ASSISTments SimpleKT at \(\tau=0.7\) (aligned with a flat SimpleKT ECE). If XES gaps are as large as ASSISTments, C3 fails — ECE-flat does not automatically mean gate-flat.

Direction C punchline this run = **C1 holds**. C2/C3 qualify the story. Failure is reported as NULL, not as “sparse always fails.”

---

## What this is not

- Not a real mastery policy (no spaced practice, no teacher override, no KC-level aggregation of \(p\)).
- Not post-hoc calibration (Direction B).
- Not evidence that GKT/CL4KT should replace SimpleKT in production.
- GKT full-log must not be cited as the C2 model.

---

## Outputs

- `analysis/direction_c/threshold_rates.csv` — every dataset × model × \(\tau\) × bucket
- `analysis/direction_c/sparse_dense_gaps.csv` — \(\Delta_{\mathrm{FM}}\), \(\Delta_{\mathrm{Miss}}\)
- `analysis/direction_c/c1_c3_verdict.txt`
- `analysis/direction_c/table_c_tau07.tex` — display table at \(\tau=0.7\)

---

## Addendum — C2 robustness (locked 2026-08-26, after C1 on seed 42, before other-fold \(\Delta\)FM is read)

**Does not replace C1–C3.** Those remain seed-42 tests. This addendum asks whether ASSISTments SimpleKT \(\Delta_{\mathrm{FM}}\) at \(\tau=0.7\) is a one-fold accident.

| Item | Locked |
|------|--------|
| Seeds / folds | \(42,2024,2025,2026,2027\) \(\equiv\) `fold_0`…`fold_4` (same mapping as the five-fold AUC/ECE tables) |
| \(f_{\mathrm{train}}\) | Counted from that fold’s `train.csv` (train-only); `kc_strata.csv` is incomplete for folds 3–4 |
| Models | DKT, SimpleKT only. GKT/CL4KT stay single-seed. |
| \(\tau\) | Display \(0.7\) only (grid already locked on fold 0) |
| Across-fold report | Mean \(\pm\) sd of \(\Delta_{\mathrm{FM}}\) and \(\Delta_{\mathrm{Miss}}\); count of folds with \(\Delta_{\mathrm{FM}}>0\) and sparse flag L or R |
| Within-fold CI (seed 42) | Percentile bootstrap, \(B=2000\), RNG seed 0. **Primary:** resample KCs within the sparse bucket and within the dense bucket (cluster). **Sensitivity:** resample events. |
| Not a new pass/fail | If one fold flips sign, report it; do not drop seed-42 C1. If mean \(\Delta_{\mathrm{FM}}\) is \(\le 0\), the five-fold reading of the gate is NULL and the manuscript must say so. |
| XES/Junyi five-fold | Descriptive only. C3 is not retuned. |
