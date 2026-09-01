# IJIET-11 — Results consistency

**Date:** 2026-08-31  
**Scope:** Section IV (Result and Discussion) after Tasks 07–10.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step11.docx` (copied from step10).  
**Not modified:** table numeric cells; Fig. 1; originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`.

---

## Section IV order

| Letter | Heading | Tables |
|--------|---------|--------|
| A | Aggregate discrimination | Table 2; sparse-vs-dense AUC from four-partition CSV |
| B | Calibration across frequency strata | Table 3 |
| C | Threshold-based decision error | Tables 4–5 (SimpleKT/DKT) |
| D | Dataset-dependent explanatory analysis | Tables 6–7 |
| E | Exploratory GKT/CL4KT result | Table 4 GKT/CL4KT rows only |
| F–G | Limitations; IJIET operational implications | — |

AUC is no longer discussed as calibration. GKT/CL4KT are no longer in the main gate paragraph.

---

## Wording rules applied

1. Sparse frequency is **not** a universal AUC failure (XES3G5M sparse AUC higher; Junyi sparse **empty**).
2. Calibration does **not** universally worsen (XES3G5M SimpleKT counter-pattern; Junyi sparse empty, not zero-ECE).
3. ASSISTments sparse ECE is **Limited** (\(N=415\)).
4. SimpleKT \(\Delta\)FAR: **positive in all five training runs spanning four unique student partitions** — not “5/5 independent seeds.”
5. Gate prose reports FAR, \(E[\mathrm{FAR}]\), Excess FAR, Miss, \(N/N_{\mathrm{advance}}/N_{\mathrm{incorrect}}\), and 95% CIs.
6. GKT/CL4KT: single fold, ASSISTments only, exploratory, not SOTA; \(\Delta\)FAR CIs include 0.

Claim trace: `audit/CLAIM_TO_RESULT_MATRIX.md`.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step11.pdf` — 7 pages, 5231 words, 8 tables, 1 figure. Table 2/3 printed rates unchanged.
