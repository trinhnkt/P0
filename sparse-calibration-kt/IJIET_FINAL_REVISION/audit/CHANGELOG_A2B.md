# CHANGELOG_A2B — rebuild XES3G5M with valid masking

**Date:** 2026-08-31  
**Prerequisite:** CASE B (A1).

## What this task did

- Flattened official `kc_level` files dropping `selectmask != 1`, KC `-1`, question `-1`, and non-{0,1} labels into `IJIET_FINAL_REVISION/a2b/` only.
- Rebuilt learner-based folds using **historical user sets** (same students) with padding rows removed; copied fold_2 → fold_3.
- Re-cut temporal 70/10/20 on the masked table.
- Recomputed train-only KC strata (0 rows with `kc_id=-1`).
- Retrained IRT, DKT, local SimpleKT (seeds 42, 2024, 2025, 2026, 2027; learner-based + temporal).
- Recomputed AUC/ACC, ECE, Brier/REL/RES, XES gate, KC covariates, regression, and XES A9.
- Listed obsolete manuscript XES numbers in `analysis/XES3G5M_RERUN_MANIFEST.md`.

## What this task did not do

- Did not overwrite `data/processed/xes3g5m/` or historical `results/predictions/`.
- Did not edit the manuscript, Table 1–8, or Figure 1 (a later task applies the manifest).
- Did not change ASSISTments or Junyi artifacts.

## Scientific results changed?

**Yes, XES3G5M only**, in the new tree. Accepted manuscript copy still shows obsolete XES cells until a text-apply task.

Largest XES deltas (old → new):

- Table 1: 866 KCs / 7.95M rows / 1,589,145 test events → **865 / 6,413,353 / 1,282,422**.
- Table 3 AUC/ACC: DKT 0.8171→**0.8180**, SimpleKT 0.7557→**0.7536**; IRT ACC unchanged at 0.7961.
- Table 4 SimpleKT ECE still roughly flat: 0.1176 / 0.1129 / 0.1254 (N=1,969).
- Gate ΔMiss **flips sign** (old +0.112 → new **−0.183**); ΔFAR stays negative 5/5.
- Regression log-freq: −0.117 → **−0.028** (n=829).
- A9 ΔECE large: DKT t500 −0.008 → **+0.142**; SimpleKT t50 +0.032 → **+0.110**.

## Files

- `IJIET_FINAL_REVISION/analysis/XES3G5M_RERUN_MANIFEST.md`
- `IJIET_FINAL_REVISION/a2b/` (processed data, splits, predictions, eval)
- Historical `data/processed/xes3g5m/` and `results/predictions/` untouched
- Compile of the **unchanged** manuscript: `output/main_ijiet_full.pdf` (8 pages; locked ASSISTments cells still present)

## STOP

Do not start the next manuscript-edit task automatically.
