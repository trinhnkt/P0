# IJIET-12 — Discussion and Conclusion

**Date:** 2026-08-31  
**Scope:** Rewrite Sections V and VI. Section IV remains Results A–E.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step12.docx` (copied from step11).  
**Not modified:** table numeric cells; Fig. 1; originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`.

---

## Section map

| Number | Heading | Content |
|--------|---------|---------|
| IV | RESULT | Unchanged A–E from IJIET-11 |
| V | DISCUSSION | A–D (new) |
| VI | CONCLUSION | Short closing paragraph |

Old IV.F/G headings (“What this paper does not show”; “Implications for information and education technology”) were removed. Their substance moved into V.B and V.D.

---

## Discussion (V)

**A. Main empirical findings.** Frequency is not a universal predictor of AUC failure (XES3G5M sparse AUC higher; Junyi sparse empty). Calibration vulnerability is dataset-dependent (ASSISTments Limited \(N=415\); XES3G5M counter-pattern). Threshold behavior can differ by frequency stratum (FAR vs Miss; five training runs spanning four unique student partitions).

**B. Practical implications.** Restrained, pre-threshold checks: occupancy, per-stratum calibration, threshold-error metrics (FAR, \(E[\mathrm{FAR}]\), Excess FAR, Miss), sufficient sample support.

**C. Why datasets differ.** Measured Table 6/7 descriptors only. Curriculum hierarchy, tagging granularity, ceiling effects, and item semantics are labeled **hypotheses**, not facts.

**D. Limitations.** Next-response \(\neq\) latent mastery; simulated gate; no classroom RCT; GKT/CL4KT exploratory single fold; temporal evaluation is a single corrected cutoff (seed 42); four unique learner partitions; R/L/I descriptive; ECE depends on binning; three datasets cannot establish a universal diagnostic law.

---

## Conclusion (VI)

Short. Uses “under the evaluated conditions”, “association”, “can”, “in some dataset-model settings”. Avoids “proves”, “causes”, “always”, “universally”.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step12.pdf` — 8 pages, 5507 words, 8 tables, 1 figure. Table 2/3 printed rates unchanged (`0.6979±0.0014`, `0.1136±0.0066`).
