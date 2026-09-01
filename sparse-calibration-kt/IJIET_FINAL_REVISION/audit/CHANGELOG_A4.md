# CHANGELOG_A4 — cluster-aware regression

**Date:** 2026-09-01  
**Prerequisite:** A3 (`REGRESSION_UNIT_AUDIT.md`): `n=478 / 2,645 / 1,263` are KC-fold (KC-split, fold 0) rows, not unique KCs.

## What this task did

- Fit test-event-weighted WLS of SimpleKT ECE on the A3 complete-case rows, with **cluster-robust SE at `kc_id`** (primary). Predictors standardized within dataset. No iid-row SE as primary inference.
- Sensitivity: unweighted OLS, same cluster-robust SE.
- Split-specific (fold 0 × learner-based / temporal) robustness in `regression_fold_sensitivity.csv`. Fold is 0 in both splits; the repeat unit is split protocol.
- Wrote Table S TeX.
- Updated Section IV.D: “n=… KCs” → verified KC-fold vs unique-KC counts; replaced Huber/bootstrap log-frequency intervals with cluster-robust WLS. Kept “associated with” / between-KC; no causal wording.

## Primary weighted cluster-robust log-frequency (obsolete Huber row in parentheses)

| Dataset | n obs | Unique KCs | \(\hat\beta\) [95% CI] | p |
|---------|------:|-----------:|------------------------|--:|
| ASSISTments 2012 | 478 | 261 | −0.068 [−0.086, −0.050] (old −0.079 [−0.097, −0.061]) | <0.001 |
| Junyi Academy | 2,645 | 1,326 | −0.014 [−0.018, −0.010] (old −0.010 [−0.014, −0.007]) | <0.001 |
| XES3G5M | 1,263 | 830 | −0.069 [−0.123, −0.015] (old −0.117 [−0.171, −0.063]) | 0.013 |

Learner exposure on ASSISTments: +0.016 [0.004, 0.027] (old +0.019 [0.010, 0.027]). Difficulty still independently associated on ASSISTments and Junyi only.

Unweighted XES log-frequency CI **includes 0** (−0.012 [−0.031, +0.007]); that is sensitivity only.

## What this task did not do

- Did not use ordinary independent-row SE as primary.
- Did not treat rows as unique KCs.
- Did not use the A2B masked XES tree (`n=829`).
- Did not change ASSISTments ECE/FAR lock cells or Junyi Table 4.
- Did not claim a causal frequency effect.

## Files

- `IJIET_FINAL_REVISION/analysis/regression_clustered_results.csv`
- `IJIET_FINAL_REVISION/analysis/regression_fold_sensitivity.csv`
- `IJIET_FINAL_REVISION/supplementary/Table_S_regression.tex`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx` (IV.D only)
- `IJIET_FINAL_REVISION/a4_cluster_regression.py`
- this changelog

## Scientific results changed?

**Yes, IV.D inference and unit wording only.** Old “n=… KCs” and Huber/bootstrap CIs are **obsolete**. Sign of weighted log-frequency remains negative on all three datasets; cluster-robust CIs still exclude 0.

Compile: `output/main_ijiet_full.pdf` (8 pages; ASSISTments ECE 0.1136 / 0.2280 unchanged).

## STOP
