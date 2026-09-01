# IJIET-08 — Threshold decision metrics (FAR)

**Date:** 2026-08-31  
**Scope:** Gate method (Section III.H) and corresponding Results/Discussion/Conclusion/Abstract terminology.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step08.docx` (copied from step07).  
**Not modified:** ECE/AUC tables; train-only stratum cuts; Table 1 counts; τ grid; originals under `paper/` and `ijiet/`.

---

## Terminology

Primary gate error renamed **False Mastery (FM) → False-Advance Rate (FAR)**.

| Quantity | Definition |
|----------|------------|
| FAR | \(P(y=0 \mid p\ge\tau)\) |
| Interpretation | Among responses for which the simulated system would advance the learner, the proportion whose observed next response is incorrect |
| Not | latent mastery |
| What it is | a next-response decision-error proxy under a simulated threshold gate |
| Miss | \(P(p\ge\tau \mid y=0)\) (unchanged) |
| Expected FAR | \(E[1-p \mid p\ge\tau]\) |
| Excess FAR | \(\mathrm{FAR} - E[1-p \mid p\ge\tau]\) |
| \(\Delta\)FAR | \(\mathrm{FAR}_{\mathrm{sparse}} - \mathrm{FAR}_{\mathrm{dense}}\) |

Display \(\tau=0.7\). Locked grid \(\{0.5,0.6,0.7,0.8\}\). \(\tau\) is not tuned on sparse test events.

---

## Denominators (recovered, not invented)

Prediction exports exist under `results/predictions/`. Integer denominators were recovered from `analysis/direction_c/threshold_rates.csv` (seed 42) and `fivefold_gaps.csv`, then checked against the prediction files.

**Table 4 (ASSISTments fold 0, \(\tau=0.7\))**

| Model | Stratum | \(N\) (\(N_{\mathrm{total}}\)) | \(N_{\mathrm{adv}}\) | \(N_{\mathrm{inc}}\) |
|-------|---------|--------------------------------|----------------------|----------------------|
| all listed | dense | 528,018 | SimpleKT 284,326; DKT 315,650; GKT 351,503; CL4KT 307,479 | 158,623 |
| all listed | sparse | 444 | SimpleKT 235; DKT 243; GKT 209; CL4KT 200 | 197 |

FAR/Miss/E[FAR] **3-decimal point estimates are the published values** (not re-rounded). Excess FAR is those 3-decimal values subtracted (e.g. SimpleKT sparse \(0.268-0.050=0.218\)).

**Table 5** adds mean sparse denominators across five seeds: \(N=413\), SimpleKT \(N_{\mathrm{adv}}=227\), \(N_{\mathrm{inc}}=155\); DKT \(N_{\mathrm{adv}}=226\), \(N_{\mathrm{inc}}=155\). Mean \(\Delta\)FAR 0.047 / 0.033 and seed counts **unchanged**.

Prose states that FAR precision is governed by \(N_{\mathrm{advance}}\), not by \(N_{\mathrm{total}}\).

---

## Confidence intervals

KC-cluster percentile bootstrap, \(B=2000\), RNG seed 0 (C2 protocol).

| Quantity | Source | 95% CI |
|----------|--------|--------|
| SimpleKT \(\Delta\)FAR seed 42 | locked C2 `seed42_bootstrap_dfm.csv` (not replaced) | \([0.006, 0.138]\) |
| DKT \(\Delta\)FAR seed 42 | same C2 file | \([0.019, 0.175]\) |
| Per-stratum FAR (all four models) | recomputed from prediction exports | Table 4 note |
| GKT / CL4KT \(\Delta\)FAR | newly computed, same protocol (not in C2) | GKT \([-0.054, 0.092]\); CL4KT \([-0.018, 0.142]\) (both include 0) |

Script: `source/_compute_ijiet08_gate.py`. Trails: `audit/ijiet08_seed42_kc_cluster_ci.csv`, `audit/ijiet08_gate_recover.txt`.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step08.pdf` — 6 pages, 4593 words, 7 tables, 1 figure. ECE table numbers untouched. No remaining “false mastery” / \(\Delta\)FM / E[FM] wording.
