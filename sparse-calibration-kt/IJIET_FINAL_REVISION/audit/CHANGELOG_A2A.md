# CHANGELOG_A2A — not executed

**Date:** 2026-08-31  
**Task issued:** A2A (correct XES3G5M descriptive counts only).  
**Prerequisite:** `XES3G5M_PADDING_AUDIT.md` concludes **CASE A**.

## Prerequisite check

**Failed.** A1 concludes **CASE B**, not CASE A.

`IJIET_FINAL_REVISION/audit/XES3G5M_PADDING_AUDIT.md`:

- Padding is not confined to metadata counts.
- **ACTION = XES3G5M RERUN REQUIRED.**

Verified contamination (not a Table 1-only error):

- `f_train` counts `kc_id = -1` (~1.08M train rows, fold 0).
- Stratum assignment puts `-1` in **dense**.
- DKT / SimpleKT / IRT trained with padding as a real KC (`correct = 0`).
- Learner-based test and prediction files include ~307k padding labels.
- Gate FAR/Miss, A4 KC regression, and A9 residual train include those rows.
- Four-partition ECE/AUC scripts drop `-1` at metric time only; that does not undo training contamination.

## What this task did **not** do

- Did **not** edit Table 1, Figure 1, Methods, or any dataset-count claim.
- Did **not** insert the A2A preferred provenance sentence. That sentence would state padding is excluded from stratum assignment and evaluation. The audit shows the opposite.
- Did **not** retrain.
- Did **not** change AUC / ECE / FAR.
- Did **not** change ASSISTments or Junyi numbers.
- Did **not** start A2B automatically.

## Why a count-only rewrite would be false

A2A’s preferred wording:

> “these positions are excluded from KC counts, stratum assignment, and evaluation.”

After CASE B that sentence is not true of the current pipeline. Updating Table 1 (866 → 865; 7.95M → 6.41M) while leaving trained models and gate/regression/A9 artifacts unchanged would describe a protocol the paper did not run.

## Files modified

- this changelog only

## Scientific results changed?

**No.** Manuscript copy untouched.

## STOP

Next allowed XES task is **A2B** (rebuild with valid masking), not A2A. Do not start it from this changelog.
