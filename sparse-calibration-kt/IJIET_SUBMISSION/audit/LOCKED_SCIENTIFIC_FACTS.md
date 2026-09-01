# Locked scientific facts

Do not change these unless an audit of experimental artifacts proves them wrong.
Do not invent p-values, CIs, sample sizes, model results, or seeds.

## Datasets and models

- Three datasets: ASSISTments 2012, Junyi Academy, XES3G5M.
- Main baselines: IRT, DKT, SimpleKT.
- GKT and CL4KT-style results are exploratory, single-fold ASSISTments analyses (seed 42 / fold 0). CL4KT is a protocol adapter, not an official checkpoint.

## Train-only KC strata

Frequency is counted on the **training fold only**.

- Strict: \(f_{\mathrm{train}}=0\)
- Very sparse: \(0<f_{\mathrm{train}}<20\)
- Sparse: \(20\le f_{\mathrm{train}}<100\)
- Medium: \(100\le f_{\mathrm{train}}<500\)
- Dense: \(f_{\mathrm{train}}\ge 500\)

## Occupancy flags (test-event count \(N\))

- R: \(N\ge 1000\)
- L: \(100\le N<1000\)
- I: \(N<100\)

Success claims require L or R. Insufficient cells are descriptive only.

## Split / seed disclosure

- Seeds 2025 and 2026 currently share the same learner partition (`fold_2` = `fold_3`) on all three datasets.
- Never describe them as five independent partitions.
- Tables that report mean±sd over learner-based performance use **four unique partitions** (the two initializations on the duplicated split are averaged first).
- Gate-robustness tables may still list all five **training seeds** with that disclosure.

## Findings that must not be inverted

- Sparse training frequency does **not** universally imply lower AUC.
- ASSISTments SimpleKT shows the clearest calibration gradient.
- Junyi learner-based sparse bucket is empty under the registered thresholds.
- XES3G5M SimpleKT does not show the same monotonic ECE gradient.
- Threshold / mastery-gate results are **simulations**, not classroom trials.
- Do not claim causal effects from observational stratum analysis.
- Do not claim classroom effectiveness from the simulated gate.

## Canonical four-partition SimpleKT ECE (learner-based)

From `analysis/four_partition/` (copied to `tables/punchline_ece.csv`):

| Dataset | Stratum | \(N\) | Flag | ECE |
|---------|---------|-------|------|-----|
| ASSISTments 2012 | dense | 523,971 | R | \(0.1136\pm0.0066\) |
| ASSISTments 2012 | medium | 5,963 | R | \(0.1541\pm0.0051\) |
| ASSISTments 2012 | sparse | 415 | L | \(0.2280\pm0.0197\) |
| Junyi | dense | 3,232,614 | R | \(0.0792\pm0.0051\) |
| Junyi | medium | 3,836 | R | \(0.1073\pm0.0156\) |
| Junyi | sparse | empty | — | — |
| XES3G5M | dense | 1,268,696 | R | \(0.1145\pm0.0011\) |
| XES3G5M | medium | 12,980 | R | \(0.1114\pm0.0076\) |
| XES3G5M | sparse | 2,010 | R | \(0.1248\pm0.0085\) |

## Dual numbering (do not mix)

| Quantity | Source | Notes |
|----------|--------|--------|
| ECE / AUC / sparse \(N=415\) | Four unique partitions | Tables 3/5/9 lineage |
| Gate / GKT / ECE-adjacent 0.210-style cells | Seed 42 only | Sparse \(N=444\); dense events 528,018 |
| SimpleKT dense \(E[\mathrm{FM}]\) at \(\tau=0.7\) seed 42 = 0.113 | Gate table | **Not** the four-partition dense ECE 0.114 |

## Gate facts (seed 42 unless noted)

- Display \(\tau=0.7\); grid {0.5, 0.6, 0.7, 0.8} is recorded, not a sparse-error search.
- SimpleKT FM: 0.196 dense → 0.268 sparse (\(\Delta\mathrm{FM}=+0.072\)).
- Five-seed SimpleKT \(\Delta\mathrm{FM}\) all positive, mean 0.047, sd 0.033.
- Seed-42 KC-cluster bootstrap CI \([0.006, 0.138]\).
- DKT \(\Delta\mathrm{FM}\) positive on only 3/5 seeds — not a five-run finding.
