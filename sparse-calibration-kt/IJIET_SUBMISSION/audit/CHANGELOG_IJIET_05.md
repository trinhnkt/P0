# IJIET-05 — Introduction and research questions

**Date:** 2026-08-31  
**Scope:** Section I (Introduction) only.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step05.docx` (copied from step04).  
**Not modified:** Abstract; Literature Review onward (including Results); originals under `ijiet/` and `paper/`.

---

## Narrative

Section I now follows:

population AUC → predicted probability *p* → calibration → threshold-based educational decisions → sparse-KC diagnostic risk.

## Terminology (this section)

- **False-Advance Rate (FAR)** introduced here; formal definition deferred to Section III as *P(y=0 | p≥τ)*.
- *y* is explained as **observed next-response correctness**, not latent mastery truth.
- Removed from Section I: “wrong dashboard,” “dirty advances,” “bake-off,” and “false-mastery error.”
- **Note:** later sections may still use older FM wording; they were not edited in this task.

## Research questions (unchanged in substance; no new RQ)

- **RQ1:** Does lower KC training frequency systematically degrade predictive discrimination?
- **RQ2:** How does calibration vary across KC-frequency strata and datasets?
- **RQ3:** When a fixed probability threshold is applied, does decision-error behavior differ between sparse and dense KCs?

## Contributions (conservative)

Kept: train-only KC-frequency protocol with strict cold-start; per-stratum ECE/Brier with occupancy flags; locked-threshold FAR/miss simulation and five-seed ASSISTments check.

Explicitly **not** claimed: new KT architecture; new calibration algorithm; new auditing theory; causal effect of frequency; classroom intervention. GKT/CL4KT remain an exploratory single-fold ASSISTments diagnostic.

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step05.pdf` — OK (4 pages, 3238 words, 6 tables, 1 figure). Results probe still present.
