# CHANGELOG_A1 — XES3G5M padding and mask audit

**Date:** 2026-08-31  
**Task:** A1 inspect-only. No manuscript edits. No retraining.

## What this task did

- Traced XES3G5M from official `kc_level` sequences through flatten (`src/create_xes3g5m_full.py`), preprocess (`src/preprocess.py`), splits, `f_train` (`src/kc_strata.py`), DKT/SimpleKT training (`src/baseline_runner.py`), prediction exports, and metric / gate / A4 / A9 scripts.
- Confirmed `selectmasks` is never read; `selectmask != 1` is identical to concept `-1`.
- Counted padding without retraining (`analysis/a1_xes_padding_counts.py` → `analysis/xes_padding_counts.csv`).
- Classified **CASE B**: padding is not metadata-only.

## Decision

**ACTION = XES3G5M RERUN REQUIRED.**

Do not retabulate ASSISTments or Junyi because of this finding.

## Files modified (this folder only)

- `IJIET_FINAL_REVISION/audit/XES3G5M_PADDING_AUDIT.md`
- `IJIET_FINAL_REVISION/analysis/xes_padding_counts.csv`
- `IJIET_FINAL_REVISION/analysis/a1_xes_padding_counts.py` (count helper)
- this changelog
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (compile of the **unchanged** manuscript copy)
- `IJIET_FINAL_REVISION/audit/compile_verify.txt`

## Scientific results changed?

**No.** Manuscript table cells, Fig. 1, ECE, FAR, and references were not edited. The audit shows existing XES3G5M trained models and several eval paths **are contaminated**; that is a finding, not a new number in the paper.

## Unresolved issues

- XES3G5M rerun (flatten without `-1`, rebuild splits / `f_train` / models / predictions / metrics) is **not** started here.
- Four-partition ECE scripts already drop `kc_id == -1`; training, gate, A4, and A9 do not. A later task must list every downstream table/figure before any XES number is replaced.
- Multi-KC `is_repeat` expansion (863,807 tokens) is separate from padding; not resolved in A1.

## STOP

Do not start Task A2 automatically.
