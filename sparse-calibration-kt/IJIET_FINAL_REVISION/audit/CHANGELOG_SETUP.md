# CHANGELOG_SETUP — initialize IJIET_FINAL_REVISION

**Date:** 2026-08-31  
**Task:** workspace only. No scientific edits.

## What this task did

- Created `IJIET_FINAL_REVISION/` with `manuscript/`, `analysis/`, `audit/`, `supplementary/`, `figures/`, `tables/`, `output/`.
- Copied the accepted named manuscript (`main_ijiet_full.docx` / `.doc`) and locked numeric artifacts **into this folder**.
- Did **not** write to `IJIET_SUBMISSION/source/` or `IJIET_SUBMISSION/output/`. Original SHA-256 hashes unchanged (`audit/SETUP_HASHES.txt`).
- Compiled from the copy: `output/main_ijiet_full.pdf` (8 pages). Kept `output/baseline_from_ijiet_submission.pdf` as the frozen IJIET-21 PDF.

Git branch `IJIET_FINAL_REVISION` was **not** created: repo `main` already has unrelated uncommitted JEDM/`paper/` files. Isolation is the folder, not a git checkout.

## Files modified (this folder only)

- `IJIET_FINAL_REVISION/README.md`
- `IJIET_FINAL_REVISION/audit/SCIENTIFIC_LOCKS.md`
- `IJIET_FINAL_REVISION/setup_copy.py`
- `IJIET_FINAL_REVISION/compile_manuscript.py`
- `IJIET_FINAL_REVISION/manuscript/*` (copies)
- `IJIET_FINAL_REVISION/analysis/*` (copies)
- `IJIET_FINAL_REVISION/tables/*` (copies)
- `IJIET_FINAL_REVISION/supplementary/TABLE_S1_MODEL_SETTINGS.md` (copy)
- `IJIET_FINAL_REVISION/figures/generate_ijiet_fig1.py` (copy)
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (compile from copy)
- `IJIET_FINAL_REVISION/output/baseline_from_ijiet_submission.pdf` (copy of accepted PDF)
- `IJIET_FINAL_REVISION/audit/SETUP_HASHES.txt`
- `IJIET_FINAL_REVISION/audit/compile_verify.txt`
- this changelog

## Scientific results changed?

**No.** Table cells, Fig. 1, ECE 0.1136/0.2280, FAR 0.196/0.268, refs `[21]`–`[22]` unchanged.

## Unresolved issues

- No next scientific task issued yet.
- Blind Word/PDF were not copied (named `main_ijiet_full` only, per target).
- Fig. 1 PNG/PDF are embedded in Word; not extracted as standalone files under `figures/`.
- Dual-submission vs JEDM `paper/` remains an author process issue, not a file issue.

## STOP

Waiting for the next numbered task. Do not start it automatically.
