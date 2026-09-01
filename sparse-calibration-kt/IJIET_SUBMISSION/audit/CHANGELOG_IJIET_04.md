# IJIET-04 — Abstract revision

**Date:** 2026-08-31  
**Scope:** Abstract paragraph and IJIET Abstract character style only.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step04.docx` (copied from step03).  
**Not modified:** Results section; `ijiet/`; `paper/`; `source/main_ijiet_step03.docx`.

---

## What changed

One compact `Abstract` paragraph (style `Abstract`, 9 pt). Label **Abstract—** is bold roman; body is italic, not bold (official template mix).

The paragraph states, in order: the *p*-vs-AUC problem; diagnostic (not architectural) design with train-only KC strata; datasets ASSISTments 2012, Junyi Academy, XES3G5M and models IRT, DKT, SimpleKT; the bounded discrimination/calibration claim; the ASSISTments SimpleKT ECE result; the locked-threshold false-advance result; the simulation disclaimer; the stratum-wise validation implication.

## Claims and numbers preserved

| Requirement | How it appears |
|-------------|----------------|
| Bounded claim | “Lower KC training frequency does not universally degrade discrimination, but calibration can become less reliable in some sparse-concept regimes.” |
| SimpleKT ECE | 0.114 dense → 0.228 sparse; Limited occupancy, *N*≈415 |
| Counterexamples | Junyi learner-based sparse empty; XES3G5M SimpleKT ECE essentially flat |
| Threshold language | **false-advance rate** (incorrect-response rate among advance decisions). Not “ground-truth non-mastery.” Dense/sparse rates 0.196 / 0.268 unchanged |
| Simulation | “This is a simulated decision gate, not a classroom intervention.” |
| GKT | **Removed from the Abstract** (remains in Results as before) |
| Implication | Probability-threshold decisions should be validated by KC-frequency stratum |

No numerical results were recomputed or changed.

## Compile

| Output | Status |
|--------|--------|
| `IJIET_SUBMISSION/output/main_ijiet_step04.pdf` | OK |
| Stats | 4 pages, 3214 words, 6 tables, 1 figure |
| Results probe | “Table 2 shows learner-based AUC” still present |
