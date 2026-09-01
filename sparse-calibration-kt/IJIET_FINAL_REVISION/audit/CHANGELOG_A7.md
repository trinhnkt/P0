# CHANGELOG_A7 — Table 7 estimability vs observed pattern

**Date:** 2026-09-01  
**Retrain:** no. **Numeric cells:** unchanged.

## Problem

Section IV.D treated three conditions as jointly determining whether a sparse-calibration contrast is “estimable”: sparse mass, test support, and frequency–difficulty coupling. That conflated **whether a contrast can be estimated** with **whether an adverse gradient is observed**.

## Logic now used

| Question | What it is | Table 7 block |
|----------|------------|---------------|
| **A** — Is sparse-vs-dense calibration estimable? | C1 non-empty sparse tail; C2 sufficient evaluation support | A. Estimability |
| **B** — Is an adverse sparse-calibration gradient observed? | May be associated with C3 (frequency–difficulty coupling) plus other structural descriptors | B. Observed pattern/context |

C3 is **not** claimed necessary or sufficient. ASSISTments and XES3G5M both meet C1–C2; only ASSISTments shows a dense-to-sparse T-KT ECE rise.

## Manuscript edits

- **IV.D intro (before Table 7):** replaced “three empirical conditions… ASSISTments 2012 meets all three” with the C1–C2 / C3 split, including: *C1–C2 determine whether a sparse contrast can be estimated under the registered thresholds; C3 and other structural descriptors help characterize the direction of the observed pattern.*
- **Table 7 title:** “Empirical conditions associated with the availability and direction of sparse-calibration contrasts on the three evaluated datasets.” Caption keeps the sparse-mass definition and states that C3 is not necessary or sufficient.
- **Table 7 body:** two blocks. A: sparse mass (C1), sparse test support (C2). B: difficulty coupling (C3), item support, curriculum-position coupling, observed T-KT ECE (A6 name; not published SimpleKT).
- **After Table 7:** removed “three observational pre-conditions…” and the paragraph that restated table numbers. Item-support and curriculum ρ now live in the table; learner exposure is identified as a regression covariate, not a C1–C2 criterion.
- **Discussion V.C:** C1–C2 estimability vs structural context; C3/item/curriculum reported as context, not as necessary or sufficient conditions.

Row values that moved into the table are the same numerals as the deleted prose: mass 18.9% / 0% / 22.5%; N 415 (L) / empty / 2,010 (R); ρ −0.227 / −0.416 / +0.087; item medians 44.5 / 18 / 3 (dense 205 vs sparse 1; IQR 5; dense 9 vs sparse 1); curriculum ρ −0.308 / −0.324 / −0.125; T-KT ECE 0.114→0.228 / dense→medium only / flat 0.114→0.125.

## What this task did not do

- Did not rerun models or change any locked ECE/FAR cell.
- Did not apply A2B XES numbers.
- Did not treat C3 as a requirement for estimability or for an adverse gradient.

## Files

- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (8 pages; compile checks true)
- `IJIET_FINAL_REVISION/apply_a7_word.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a7`.

## STOP
