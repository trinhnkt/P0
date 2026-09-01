# A3 — KC-level regression unit audit

**Date:** 2026-09-01  
**Scope:** Section IV.D weighted SimpleKT ECE regression (`n=478`, `2,645`, `1,263`).  
**Coefficients:** not refit. **Manuscript:** not edited.

## Dataset used for the reported regression

| Piece | Path | Role |
|-------|------|------|
| Row-level KC table | `analysis/kc_characteristics.csv` | Train-only covariates + per-KC SimpleKT ECE |
| Fitted `n` / coefficients | `analysis/regression_results.csv` | Weighted SimpleKT rows: `n=478 / 2645 / 1263` |
| Builder | `scripts/a4_confounding_analysis.py` | Join, `dropna`, Huber/OLS |

Reconstruction of the fitted rows: `IJIET_FINAL_REVISION/analysis/regression_unit_audit.csv` (SimpleKT only; complete cases on ECE and the five covariates; `test_events` as the weight column).

`a4_confounding_analysis.py` builds training covariates on **fold 0** for both `learner_based` and `temporal`, computes per-KC ECE from SimpleKT prediction exports, then fits **one regression per dataset** on the stacked table. It does **not** restrict to unique `kc_id`, and it does **not** average the two splits before fitting.

## Per-dataset unit counts

From `regression_unit_audit.csv` (matches `regression_results.csv` `n` exactly):

| Dataset | Total rows (`n` in IV.D) | Unique `kc_id` | Folds represented | Splits represented | Mean obs / KC | Min | Max |
|---------|--------------------------:|---------------:|------------------:|-------------------:|--------------:|----:|----:|
| ASSISTments 2012 | 478 | 261 | 1 (`fold=0`) | 2 | 1.831 | 1 | 2 |
| Junyi Academy | 2,645 | 1,326 | 1 (`fold=0`) | 2 | 1.995 | 1 | 2 |
| XES3G5M | 1,263 | 830 | 1 (`fold=0`) | 2 | 1.522 | 1 | 2 |

Row breakdown by split (complete cases):

| Dataset | `learner_based` fold 0 | `temporal` fold 0 |
|---------|----------------------:|------------------:|
| ASSISTments 2012 | 260 | 218 |
| Junyi Academy | 1,326 | 1,319 |
| XES3G5M | 830 | 433 |

Max observations per KC is **2** because a KC can appear once per split. It is not five learner-based folds stacked (`fold_0`…`fold_4`).

XES3G5M complete cases include **one** row with `kc_id=-1` (padding token from the historical flatten). That row is in the reported `n=1,263`.

## Verdict on `n=478 / 2645 / 1263`

**B — KC-fold / KC-split observations, not unique KCs.**

- **Not A.** Unique KC counts are **261 / 1,326 / 830**, not 478 / 2,645 / 1,263.
- **B, with a precise label:** each row is a `(dataset, split, fold=0, kc_id)` observation. The same `kc_id` can contribute two rows (learner-based and temporal). The fitted `n` is the number of complete KC-split rows after `dropna`.
- **Not five independent learner folds.** Only fold 0 is present; the duplicate unit is **split protocol**, not seed/`fold_1`–`fold_4`.

Therefore the manuscript phrase **“n=478, 2,645, and 1,263 KCs”** is **incorrect**. Those integers count **KC-split rows**, not distinct knowledge components.

This audit does not change coefficients, standard errors, or Word text. Clustered SEs / unique-KC refits are a later task if commissioned.

## Column map (`regression_unit_audit.csv`)

| CSV column | IV.D quantity |
|------------|----------------|
| `dataset` | ASSISTments / Junyi / XES3G5M (`assist2012`, `junyi`, `xes3g5m`) |
| `split` | `learner_based` or `temporal` (needed to distinguish the two rows per KC) |
| `fold` | 0 |
| `kc_id` | as stored in `kc_characteristics.csv` |
| `test_events` | test-event count (regression weight) |
| `ECE` | KC-level SimpleKT ECE |
| `log1p_f_train` | \(\log(1+f_{\mathrm{train}})\) |
| `difficulty_proxy` | \(1-\) mean train correctness |
| `item_support` | distinct training items per KC |
| `learner_exposure` | distinct training learners per KC |
| `curriculum_position_proxy` | median normalized sequence position (train) |

## What this task did not do

- Did not refit \(\hat\beta\).
- Did not edit the manuscript, Table 7, or Results D.
- Did not replace historical `kc_characteristics.csv`.
- Did not use `IJIET_FINAL_REVISION/a2b/` XES rows (`n=829`, learner-based only, padding dropped). Those are a later masked tree, not the IV.D source audited here.
