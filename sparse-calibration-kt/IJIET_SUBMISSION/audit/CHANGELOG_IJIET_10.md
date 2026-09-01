# IJIET-10 — Explanatory analysis

**Date:** 2026-08-31  
**Scope:** Restore a short Results subsection from already-validated analyses. No new experiments; no appendices.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step10.docx` (copied from step09).  
**Not modified:** originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`; AUC/ACC/ECE cells; gate tables; Fig. 1.

---

## Placement and length

Heading: **Explanatory Analysis of Dataset-Dependent Calibration** (Results, after Table 6).

Methods G adds one sentence defining item support, learner exposure, and the curriculum-position proxy so those symbols are named before Results.

Compile grew from 7 pages / 4,670 words to **8 pages / 5,158 words** (~0.5–1.0 IJIET page). One figure. Eight tables (unnumbered settings listing + Tables 1–7).

---

## Estimands (kept distinct)

| Estimand | Question | Source |
|----------|----------|--------|
| Between-KC association | Do KCs that already have lower \(f_{\mathrm{train}}\) also have higher ECE after training-only covariates? | Weighted SimpleKT regression (`analysis/regression_results.csv`; `paper/tables` lineage) |
| Within-KC controlled sparsification | If training rows are reduced for the *same* originally dense KC, does ECE rise? | `paper/tables/table_16_sparsification.tex` (seed 42, 30 KCs/dataset) |

No causal claims. Frequency alone is **not** treated as a universal cause.

---

## Observational descriptors (already in Table 6 or the validated discussion)

1. Sparse mass: 18.9% / 0% / 22.5% of KCs with \(f_{\mathrm{train}}<100\).
2. Test-event support: \(N=415\) (L) / empty / \(N=2{,}010\) (R).
3. Frequency–difficulty: \(\rho=-0.227\), \(-0.416\), \(+0.087\).
4. Item support: ASSISTments median 44.5 (dense 205 vs sparse 1); Junyi median 18 (IQR 5); XES3G5M median 3 (dense 9 vs sparse 1).
5. Learner exposure: distinct training learners/KC; weighted SimpleKT coefficient independently associated only on ASSISTments (\(+0.019\) \([0.010, 0.027]\)).
6. Curriculum-position coupling: \(\rho=-0.308\), \(-0.324\), \(-0.125\).

Regression (weighted, SimpleKT): \(\log(1+f_{\mathrm{train}})\) \(\hat\beta=-0.079\), \(-0.010\), \(-0.117\) with CIs excluding 0. XES3G5M unweighted frequency interval includes 0 (stated, not inverted).

---

## Table 7 (compact; five rows)

Key cells only, to show that reducing training evidence for the same KC does not universally worsen calibration:

| Dataset | Model | Reduction | \(\Delta\)ECE | 95% CI | Reading |
|---------|-------|-----------|---------------|--------|---------|
| ASSISTments 2012 | DKT | 500 | \(-0.047\) | \([-0.060,-0.033]\) | ECE lower |
| ASSISTments 2012 | SimpleKT | 50 | \(+0.002\) | \([-0.021,+0.025]\) | CI includes 0 |
| Junyi Academy | DKT | 500 | \(-0.021\) | \([-0.041,-0.001]\) | ECE lower |
| Junyi Academy | SimpleKT | 50 | \(+0.135\) | \([+0.110,+0.161]\) | ECE higher |
| XES3G5M | DKT | 500 | \(-0.008\) | \([-0.019,+0.004]\) | CI includes 0 |

The ASSISTments observational SimpleKT dense-to-sparse ECE jump (\(0.114\to 0.228\)) is **not reproduced** by sparsifying originally dense ASSISTments KCs. Junyi SimpleKT at 50 rows is retained as the counter-cell (a within-KC increase is possible, not a law). Full 18-row sparsification table and old appendices were **not** restored.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step10.pdf` — 8 pages, 5158 words, 8 tables, 1 figure. Table 2/3 rates untouched. Heading 1 remains I–V.
