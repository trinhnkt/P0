# IJIET-09 — Figures and tables

**Date:** 2026-08-31  
**Scope:** Fig. 1 and Tables 1–6 captions/layout. Verified AUC/ACC/ECE cells not edited.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step09.docx` (copied from step08).  
**Not modified:** originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`; stratum cuts; Table 1 cohort cells; Table 2/3 rates.

---

## Fig. 1

The previous graphic was **number of KCs per train-only frequency stratum**, not interaction volume. The old caption (“Dense concepts dominate interactions…”) is removed.

A second row was added from **verified** fold-0 `train_freq` sums in `results/tables/kc_strata.csv` (not inferred from KC counts). Shared legend (Learner-based / Temporal); tick labels `=0`, `1–19`, `20–99`, `100–499`, `≥500`; footer names the strata. Labels enlarged; no per-subplot legends.

The figure sits in a one-column section (width 470 pt, aspect ratio preserved) so it spans the IJIET text width. Caption is **below** the plot:

> Fig. 1. Distribution of KCs across train-only frequency strata under learner-based and temporal splits. Bottom: verified training-interaction counts (sum of train-only f_train on fold 0); volume is not inferred from KC counts. Bottom y-axis is logarithmic.

Generator: `source/generate_ijiet_fig1.py` → `figures/fig1_kc_and_train_volume.png`.

---

## Tables

| Table | Change |
|-------|--------|
| **1** | Caption states post-processing cohort statistics, not raw public-dump counts. Cells unchanged (ASSISTments 27,806 / 265 / 2.66M / 534,150; Junyi 71,014 / 1,326 / 16.2M / 3,269,022; XES3G5M 18,066 / 866 / 7.95M / 1,589,145). |
| **2** | Caption expands AUC and ACC. Verified rates untouched (e.g. ASSISTments DKT AUC 0.6979±0.0014). |
| **3** | Caption states **N is the mean test-event count across four unique learner partitions**, not a single-partition count. ECE cells untouched (e.g. SimpleKT ASSISTments dense 0.1136±0.0066, sparse 0.2280±0.0197, N=415 L). |
| **4** | FAR terminology; columns N, N_advance, N_incorrect, FAR [95% CI], E[FAR], Excess FAR, Miss. Point estimates remain published 3-decimal FAR/Miss; CIs from IJIET-08 KC-cluster bootstrap. |
| **5** | Replaces implied-independent “5/5 seeds”. Caption: five training runs (seeds 42, 2024, 2025, 2026, 2027) across four unique learner partitions. SimpleKT ΔFAR>0 on 5/5 runs **and all four unique partitions**; DKT 3/5 runs (shared partition mixed in sign). Mean sparse N / N_advance / N_incorrect unchanged. |
| **6** | Caption: empirical observations on these three datasets; **not universal laws**. |

List autonumber leaking into table cells (Roman/letter prefixes) is stripped. Tables 3–5 are wrapped in one-column sections so nine-column gate tables remain readable. Table titles remain above tables.

Symbols used in captions: FAR = P(y=0 \| p≥τ); Excess FAR = FAR−E[FAR]; N_advance / N_incorrect = advance and incorrect-response denominators; R/L occupancy flags as in Methods.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step09.pdf` — 7 pages, 4670 words, 7 tables (Table 1 + unnumbered settings listing + Tables 2–6), 1 figure. Heading 1 restored to I–V after section breaks. No remaining “5/5 seeds” or volume-from-KC-count caption.

### Residual

- Table 4 FAR CIs still wrap inside the FAR column at print size.
- Results H2 letters can still restart after a one-column table section (IJIET-07 residual).
- Dual submission vs JEDM, generative-AI disclosure, and typical 8–12 page length are unchanged.
