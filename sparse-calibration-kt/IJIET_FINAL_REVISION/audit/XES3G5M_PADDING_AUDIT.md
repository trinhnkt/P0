# XES3G5M padding and mask audit (Task A1)

**Date:** 2026-08-31  
**Scope:** inspect preprocessing and evaluation only. No manuscript edits. No retraining.  
**Counts:** `IJIET_FINAL_REVISION/analysis/xes_padding_counts.csv`  
**Helper (not a result table):** `IJIET_FINAL_REVISION/analysis/a1_xes_padding_counts.py`

This audit asks whether sequence-padding / history-only tokens coded as `-1` in the official XES3G5M `kc_level` files entered statistics, frequencies, splits, training, exports, metrics, strata, sparsification, or regression.

---

## Decision

**CASE B.** Padding is not confined to metadata counts.

**ACTION = XES3G5M RERUN REQUIRED.**

Do not change ASSISTments or Junyi numbers because of this finding. Do not edit the manuscript in A1.

Four-partition ECE/AUC scripts later drop `kc_id == -1` at *metric time*. That does **not** make this CASE A: models were trained with padding as a real KC (`correct = 0`), `f_train` assigned it to **dense**, learner-based test/prediction files contain ~307k padding rows, and gate / A4 / A9 paths do not drop them.

---

## Pipeline (code, not a new experiment)

```
data/raw/xes3g5m/kc_level/train_valid_sequences.csv
data/raw/xes3g5m/kc_level/test.csv
        │  src/create_xes3g5m_full.py
        │  expands questions, concepts, responses, timestamps
        │  does NOT read selectmasks / is_repeat
        │  does NOT drop -1
        ▼
data/raw/xes3g5m/raw_data.csv
        │  src/preprocess.py
        │  dropna only (does not treat -1 as missing)
        │  correct: 1 if x > 0 else 0  →  response -1 becomes label 0
        │  n_kcs = nunique(kc_id) including -1
        ▼
data/processed/xes3g5m/interactions.csv
        │  src/three_split_constructor.py
        │  learner_based: split by user  → padding follows the user into train/valid/test
        │  temporal: sort by timestamp → all padding timestamps are early → all pad in train
        ▼
splits/{learner_based,temporal}/fold_*/{train,valid,test}.csv
        │  src/kc_strata.py  value_counts() on train, including -1
        ▼
results/tables/kc_strata.csv     f_train for kc_id=-1 → bucket dense
        │  src/baseline_runner.py / full_baseline_runner.py
        │  kc_map from all unique KCs including -1
        │  DKT/SimpleKT loss mask is labels != -1 (PyTorch batch pad)
        │  XES padding rows have correct=0, so they ARE in the loss
        │  predict_sequential writes a p_pred for every test row
        ▼
results/predictions/*xes3g5m*_predictions_rerun.csv
        │  metric scripts (inconsistent; see Q6–Q8)
        ▼
ECE / AUC / Brier / gate FAR–Miss / A4 regression / A9 downsample
```

`selectmasks` exists on `train_valid_sequences.csv` only. Official `test.csv` has **0** concept `-1` tokens and no `selectmasks` column.

PyTorch `collate_fn` padding (`labels_pad = -1`) is a *batch* pad. It is not the XES skill `-1`. The two must not be confused.

---

## Counts (no retraining)

| Quantity | Value |
|----------|------:|
| Processed rows | 7,953,709 |
| Unique KCs including `-1` | 866 |
| Unique real KCs excluding `-1` | **865** |
| Unique items including `-1` | 7,653 |
| Unique real items excluding `-1` | **7,652** |
| Padding rows (`kc_id = -1` and `item_id = -1`) | **1,540,356** |
| Valid non-padding flattened rows | **6,413,353** |
| Padding as % of processed | **19.3665%** |
| Padding `correct` after preprocess | **0.0** (all labeled incorrect) |
| Learners | 18,066 |
| Rows with `selectmask != 1` (train_valid tokens) | **1,540,356** |
| Overlap `concept == -1` ∩ `selectmask != 1` | **1,540,356** (exact) |
| `selectmask != 1` but not concept `-1` | **0** |
| Concept `-1` but not `selectmask != 1` | **0** |
| Official `kc_level` test concept `-1` | **0** |
| `is_repeat` nonzero (multi-KC expansion, not padding) | 863,807 |

Learner-based fold 0:

| Split | Rows | Padding | All padding y=0? |
|-------|-----:|--------:|:-----------------|
| Train | 5,572,247 | 1,078,981 | True |
| Valid | 792,317 | 154,652 | True |
| Test | 1,589,145 | 306,723 | True |

Temporal fold 0: **all 1,540,356 padding rows in train**; valid pad = 0; test pad = 0.

Seed-42 prediction files (learner-based): 306,723 padding rows exported. Mean predicted probability on those rows: DKT/SimpleKT ≈ **0.00464**; IRT 1PL ≈ **0.641**. Temporal prediction files: 0 padding rows.

`kc_strata.csv`: `xes3g5m` `kc_id=-1` is **dense** on every inspected fold (learner-based train ≈ 1.08M; temporal train = 1,540,356).

A9: `kc_id=-1` is in eligibility (`eligible=False`, `test_pos=0`); not in `selected_kcs.csv`. A9 `t500` train still contains **1,078,981** padding rows because downsample keeps `others`.

---

## YES / NO answers

### 1. Is `-1` counted as a KC in descriptive Table 1?

**YES.**

`preprocess.py` sets `n_kcs = df['kc_id'].nunique()`. That is **866**, not the official **865**. Table 1 interaction count **7.95M** (7,953,709) includes the 1,540,356 padding rows. Extra item **7,653 vs 7,652** is the same token.

### 2. Is `-1` counted in training KC frequency?

**YES.**

`src/kc_strata.py` uses `train['kc_id'].value_counts()` with no `-1` filter. Fold 0 learner-based `f_train(-1) = 1,078,981`.

### 3. Can `-1` enter any sparse/dense bucket?

**YES — dense.**

With `f_train ≈ 1.08M` (learner-based) or `1,540,356` (temporal), the fake KC is assigned `bucket=dense` (`f ≥ 500`). It does **not** land in sparse. It **does** inflate the dense stratum’s train mass and, on learner-based splits, dense test mass (~307k events, all `y=0`).

### 4. Can `-1` enter DKT/SimpleKT training?

**YES.**

`kc_map` is built from `sorted(unique(train ∪ valid ∪ test kc_id))`, which includes `-1` (`n_kcs = 866`). `KTDataset` encodes every row, including padding, as `kc_index * 2 + correct`. After preprocess, padding `correct = 0`, so the loss mask `labels_flat != -1` **keeps** those positions. The model therefore sees a high-frequency always-incorrect “skill.”

### 5. Can `-1` enter test labels?

**YES** on learner-based splits; **NO** on temporal test.

Learner-based fold 0 test: **306,723** padding labels, all 0 (~19.3% of that test file). Temporal fold 0 test: **0**. Prediction CSVs match the test files.

### 6. Can `-1` enter AUC/ECE/Brier computation?

**YES** (unfiltered paths). **Dropped** in the four-partition recompute used for the IJIET ECE tables.

| Script | Drops `kc_id == -1`? |
|--------|----------------------|
| `src/metrics.py` | **No** |
| `src/calibration_eval.py` | **No** |
| `src/recalculate_diagnostics.py` | **Yes** |
| `scripts/recompute_four_partition_summaries.py` | **Yes** |
| `scripts/recalc_temporal_calibration.py` | **Yes** |
| `scripts/make_updated_latex_tables.py` | **Yes** |
| `scripts/make_updated_figures.py` | **Yes** |
| `scripts/run_reruns.py` | **Yes** |

Because padding test rows are all `y=0` with DKT/SimpleKT `p ≈ 0.005`, an unfiltered learner-based AUC is **inflated** by a large easy-negative set. That is consistent with historically high overall XES DKT AUC versus the lower four-partition figure. Filtering at eval does **not** undo training contamination (Q4).

### 7. Can `selectmask != 1` rows enter evaluation?

**YES.**

Flattening never reads `selectmasks`. Empirically, `selectmask != 1` **is identical** to `concept == -1` (1,540,356 rows; both set-differences are 0). Those rows enter processed data, learner-based test, and prediction exports. Official `test.csv` has no mask column and 0 padding; our learner-based test is a **user re-split**, so padding **does** appear in evaluation files.

### 8. Can `-1` enter gate FAR/Miss metrics?

**YES.**

`scripts/c_threshold_simulate.py` and `scripts/c_threshold_multifold.py` do **not** filter `kc_id == -1`. Learner-based dense cells therefore include ~307k always-incorrect padding events. At `τ = 0.7`, DKT/SimpleKT padding `p ≈ 0.005` so those rows do not enter the advance set; they **do** enlarge the dense event count and the Miss denominator (`n_inc`). IRT padding `p ≈ 0.641` is still below 0.7, so the same pattern holds at the locked gate threshold. Temporal gate test files have 0 padding.

### 9. Can `-1` enter KC-level regression?

**YES.**

`scripts/a4_confounding_analysis.py` groups predictions by `kc_id` with no `-1` filter. Padding is a dense “KC” with `test_n ≈ 306,723`, `test_pos = 0`, `train_correct_rate = 0`. That is a fake point in any KC-level ECE/frequency scatter.

### 10. Can `-1` enter controlled sparsification?

**YES** (residual train), **NO** as a selected target KC.

A9 eligibility lists `-1` with `eligible=False` (no positive test labels). `selected_kcs.csv` does not contain `-1`. `scripts/a9_select_and_downsample.py` keeps `others = train[~train["_kc"].isin(selected_ids)]`, so the **1,078,981** padding train rows remain in A9 train copies (confirmed on `t500`).

---

## Why this is CASE B, not CASE A

CASE A would require padding to affect **metadata counts only**. Observed contamination:

- `f_train` and dense-stratum assignment
- DKT / SimpleKT / IRT training inputs
- learner-based test labels and prediction exports
- unfiltered AUC/ECE/Brier and gate FAR/Miss
- A4 KC-level regression
- A9 residual training data

A manuscript-only recount of Table 1 (866 → 865; 7.95M → 6.41M non-padding) would **not** repair trained models or gate/regression/sparsification artifacts.

ASSISTments and Junyi are out of scope for this rerun.

---

## Related, not padding

`is_repeat` nonzero = **863,807** tokens. That is multi-KC expansion of real questions, not `-1`. It explains why non-padding rows (6,413,353) still exceed the official question-level 5,549,635. A1 does not reclassify that expansion.

---

## What A1 did **not** do

- Did not modify the manuscript or IJIET_SUBMISSION originals.
- Did not retrain.
- Did not start Task A2.
- Did not change ASSISTments or Junyi artifacts.

---

**STOP.** Next scientific task must be issued explicitly.
