# CHANGELOG_A3 — KC-level regression unit audit

**Date:** 2026-09-01  
**Manuscript:** not edited. **Coefficients:** not refit.

## What this task did

- Located the IV.D regression source: `analysis/kc_characteristics.csv` via `scripts/a4_confounding_analysis.py`, with fitted `n` in `analysis/regression_results.csv`.
- Reconstructed every complete SimpleKT regression row into `IJIET_FINAL_REVISION/analysis/regression_unit_audit.csv`.
- Counted rows vs unique `kc_id` vs folds vs splits.
- Wrote `IJIET_FINAL_REVISION/audit/REGRESSION_UNIT_AUDIT.md`.

## Verdict

`n=478 / 2645 / 1263` is **B** (KC-split observations at fold 0), **not** unique KCs (261 / 1,326 / 830). The phrase “n=… KCs” in Section IV.D is incorrect. No Word change in this task.

## Scientific results changed?

**No numbers were recomputed.** The unit interpretation of the existing `n` is now documented. Downstream prose that calls those counts “KCs” is marked incorrect in the audit, not patched.

## Files

- `IJIET_FINAL_REVISION/analysis/regression_unit_audit.csv`
- `IJIET_FINAL_REVISION/audit/REGRESSION_UNIT_AUDIT.md`
- `IJIET_FINAL_REVISION/a3_regression_unit_audit.py`
- this changelog

## Compile

Unchanged manuscript: `output/main_ijiet_full.pdf` (8 pages; locked ASSISTments cells still present).

## STOP

Do not auto-start a coefficient refit or a manuscript wording patch.
