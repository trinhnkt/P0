# IJIET-07 — Methods completeness

**Date:** 2026-08-31  
**Scope:** Section III (Materials and Methods) only.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step07.docx` (copied from step06).  
**Not modified:** Abstract; Introduction; Literature Review; Result and Discussion tables/figure numbers; originals under `ijiet/` and `paper/`.

---

## Structure (IJIET Heading 2 A.–H.)

- **A. Datasets** — post-processing counts; provenance; XES3G5M kc_level expansion vs official paper.
- **B. Splits and seeds** — learner-based primary; temporal complementary; 70/10/20 construction; learner-disjointness; train-only KC buckets; five runs / four unique partitions.
- **C. Model settings** — recovered hyperparameters table; GKT/CL4KT exploratory settings in prose; NOT RECOVERED cells not imputed.
- **D. Train-only frequency strata** — cuts unchanged; Fig. 1 re-inserted.
- **E. Reliability flags** — R/L/I named **descriptive sample-support flags**, not inferential guarantees.
- **F. Calibration** — ECE retained; Brier and UNC/REL/RES defined.
- **G. Difficulty coupling** — `difficulty(c) = 1 − mean_train_correctness(c)`; Spearman ρ(log(1+f_train), difficulty).
- **H. Simulated decision gate** — FAR defined; Result tables still label the same quantity as FM.

---

## A. Datasets / XES3G5M counts

Table 1 **numeric cells were not changed**:

| Dataset | Learners | KCs | Interactions | Test events |
|---------|----------|-----|--------------|-------------|
| ASSISTments 2012 | 27,806 | 265 | 2.66M | 534,150 |
| Junyi Academy | 71,014 | 1,326 | 16.2M | 3,269,022 |
| XES3G5M | 18,066 | 866 | 7.95M | 1,589,145 |

Caption now states that these are **post-processing** counts. Prose gives exact processed interactions: 2,657,490 / 16,215,567 / 7,953,709.

XES3G5M vs Liu et al. `[20]` (18,066 students, 7,652 questions, 865 KCs, 5,549,635 interactions): **verified**, not unresolved. 866 includes padding token `skill_id=-1`; 7.95M is flattened kc_level rows (multi-KC expansion + 1,540,356 padding rows). Full trail: `audit/XES3G5M_COUNT_AUDIT.md`.

---

## B–C. Splits, seeds, settings

- Learner-based: 20% test learners, 10% valid, remainder train; disjoint within a fold.
- Temporal: earliest 70% / next 10% / latest 20% by timestamp; not the source of gate numbers.
- Seeds **42, 2024, 2025, 2026, 2027**; **2025 and 2026 share fold_2 = fold_3** (verified on disk for all three datasets). Never called five independent folds.
- Training snapshot git commit: **NOT RECOVERED**. Local SimpleKT is not byte-identical to official SimpleKT `[4]`.
- Settings table is **unnumbered** so Results captions remain Table 2–6. Machine-readable copy: `supplementary/TABLE_S1_MODEL_SETTINGS.md`.

---

## E–H. Flags, calibration, difficulty, gate

- R/L/I: descriptive sample-support flags; not CIs or tests.
- ECE formula unchanged (M=15 equal-width).
- Brier = (1/N) Σ (p_i − y_i)²; Brier = UNC − RES + REL with the binned definitions; components need not sum exactly to Brier.
- Difficulty proxy is train-only and **not** latent IRT β. Spearman association defined, not re-reported as a new result.
- FAR = P(y=0 | p≥τ); y = next-response correctness. Result tables still say FM.

Frequency-stratum cuts are unchanged.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step07.pdf` — 5 pages, 4392 words, 7 tables (Table 1 + unnumbered settings table + Results Tables 2–6), 1 figure. Results probe still present.
