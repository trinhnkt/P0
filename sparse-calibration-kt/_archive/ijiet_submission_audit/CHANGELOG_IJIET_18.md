# IJIET-18 — Close empty space before spanning tables

**Date:** 2026-08-31  
**Working files:** `source/main_ijiet_full.docx`, `source/main_ijiet_blind.docx`  
**PDFs:** `output/main_ijiet_full.pdf`, `output/main_ijiet_blind.pdf` (8 pages)  
**Script:** `source/prepare_step18.py`  
**Not modified:** table numeric cells; Fig. 1 data; originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`.

## Cause

Word two-column → one-column Continuous breaks started the table on a **new page** when the wrap began at the caption, leaving a short leftover 2-col stub. Unwrapping tables back into 2-col made them **snake** across columns (`AllowBreakAcrossPages` does not stop column wrap).

## Fix

Wrap heading/intro + caption + table in one 1-col range:

| Block | Starts at | Ends at |
|-------|-----------|---------|
| T2 + Fig. 1 | Table 2 caption | Fig. 1 caption |
| T4 | *B. Calibration across frequency strata* | Table 4 |
| T5–T6 | *C. Threshold-based decision error* | Table 6 |
| T7–T8 | *D. Dataset-dependent explanatory analysis* | Table 8 |

Tables 1 and 3 stay in a single 2-col column. Heading 2 letters restored after section breaks. Snapshot of the pre-fix binary: `source/snapshots/main_ijiet_pre18_snake.doc`.

## Verify

- `0.1136` / `0.2280` ECE and `0.196` / `0.268` FAR present.
- Blind PDF has no identifying author strings.
- Table 8 is intact (not split across columns); no blank page immediately before it.

## Residual

Extra vertical space can still appear above Tables 5 and 6 (leftover 1-col section marks). Merging those marks deleted captions, so they were left in place.
