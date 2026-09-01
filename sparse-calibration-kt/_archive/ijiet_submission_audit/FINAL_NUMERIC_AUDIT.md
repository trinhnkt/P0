# Final numeric audit (scientific integrity)

**Scope:** every numerical claim in Abstract, Introduction, Results, Discussion, and Conclusion of `IJIET_SUBMISSION/output/main_ijiet_full.pdf` (Word source `source/main_ijiet_full.docx`).

**Rule:** do not rewrite the manuscript unless an inconsistency is found. Do not leave **NOT TRACEABLE** claims in the final manuscript.

**Date:** 2026-08-31.

**Status key**

| Status | Meaning |
|--------|---------|
| **VERIFIED** | Value matches a table cell and/or analysis CSV produced from prediction exports by a named script. Rounding to 3–4 decimals is allowed where the Abstract or Table 7 uses 3 decimals of a 4-decimal Table 4 cell. |
| **NEEDS CORRECTION** | Wording or number disagrees with locked protocol / CSV. Patched before compile if listed below. |
| **NOT TRACEABLE** | No table, CSV, prediction export, or script. **None remain.** |

Locked display conventions (not treated as errors):

- Abstract / Table 7 may round four-partition SimpleKT ECE `0.1136` → `0.114` and `0.2280` → `0.228`.
- Seed-42 SimpleKT dense \(E[\mathrm{FAR}]=0.113\) is **not** four-partition dense ECE `0.114` (manuscript already distinguishes them).
- Seed-42 ΔFAR CI for SimpleKT is the **locked C2** interval `[0.006, 0.138]` from `analysis/direction_c/c2_fivefold_verdict.txt`, not the recomputed CSV `[0.0088, 0.1414]`.
- `analysis/a5_condition_verdicts.csv` still contains leftover seed-42/5-run ECE (`0.113→0.158→0.225`, sparse \(N=403\)). The manuscript uses four-partition cells (`0.114→0.228`, \(N=415\)). That analysis file is **not** a manuscript source.

---

## Traceability map

| Quantity family | Table | CSV / artifact | Prediction export | Script |
|-----------------|-------|----------------|-------------------|--------|
| Four-partition AUC/ACC | Table 3 | `analysis/four_partition/summary_4part_overall.csv` | `results/predictions/{ds}_learner_based_{model}_seed{42,2024,2025,2026,2027}_predictions_rerun.csv` | `scripts/recompute_four_partition_summaries.py` |
| Four-partition ECE, \(N\) | Table 4; Abstract 3-d.p. | `analysis/four_partition/summary_4part_bucket.csv`; `IJIET_SUBMISSION/tables/punchline_ece.csv` (**4part** rows) | same rerun CSVs | same |
| Seed-42 gate FAR / \(E[\mathrm{FAR}]\) / Excess / Miss / \(N\) | Table 5 | `IJIET_SUBMISSION/audit/ijiet08_seed42_gate_points.csv`; FAR CIs `ijiet08_seed42_kc_cluster_ci.csv` | `assist2012_learner_based_*_seed42*` (incl. GKT/CL4KT) | `scripts/c_threshold_simulate.py` |
| Five-run ΔFAR | Table 6 | `analysis/direction_c/c2_fivefold_verdict.txt`; `audit/ijiet08_fivefold_denominators.csv` | five ASSISTments learner-based reruns | `scripts/c_threshold_multifold.py` |
| Sparse mass, ρ, item medians | Table 7 (structural rows) | `analysis/dataset_sparse_diagnostic_profile.csv` (learner_based) | train-fold KC tables, not test predictions | `scripts/a5_dataset_diagnostic_profile.py` |
| Table 7 ECE arrows | Table 7 | four-partition ECE (not a5 hardcoded `EVENT_ECE`) | rerun CSVs | `recompute_four_partition_summaries.py` |
| Weighted KC regression | Results D prose | `analysis/regression_results.csv` (`weighted=True`, SimpleKT) | KC-level ECE from predictions | `scripts/a4_confounding_analysis.py` |
| Within-KC ΔECE | Table 8 | `analysis/a9/statistical_summary.csv` | `results/predictions/a9_*` | `scripts/a9_analyze.py` |

Occupancy flags: R \(N\ge 1000\), L \(100\le N<1000\). Sparse \(N=415\) (four-partition mean) vs gate sparse \(N=444\) (seed 42) must not be mixed.

---

## Special checklist

| Check | Finding | Status |
|-------|---------|--------|
| ASSISTments SimpleKT dense ECE | Table 4 `0.1136±0.0066`; 4part CSV `0.113558…±0.006585…`; Abstract `0.114` | VERIFIED |
| ASSISTments SimpleKT medium ECE | Table 4 `0.1541±0.0051`; CSV `0.154118…±0.005063…` | VERIFIED |
| ASSISTments SimpleKT sparse ECE | Table 4 `0.2280±0.0197`, \(N=415\) L; CSV `0.228032…`, \(N=415.25\); Abstract `0.228`, \(N\approx 415\) | VERIFIED |
| XES3G5M SimpleKT dense / sparse ECE | Table 4 `0.1145±0.0011` / `0.1248±0.0085`; CSV `0.114472` / `0.124805`; Abstract “essentially flat” | VERIFIED |
| Gate dense FAR | Table 5 SimpleKT `0.196 [0.186–0.208]`; CSV FAR `0.196327`, CI `0.18563–0.20768` | VERIFIED |
| Gate sparse FAR | `0.268 [0.202–0.337]`; CSV `0.268085`, CI `0.20201–0.33685` | VERIFIED |
| ΔFAR (seed 42) | prose `+0.072`; CSV `0.071758` | VERIFIED |
| \(E[\mathrm{FAR}]\) dense / sparse | `0.113` / `0.050`; CSV `0.112505` / `0.049905` | VERIFIED |
| Excess FAR dense / sparse | `0.083` / `0.218`; CSV `0.083823` / `0.218180` | VERIFIED |
| Miss dense / sparse | `0.352` / `0.320`; CSV `0.351910` / `0.319797` | VERIFIED |
| Five-run statement | Abstract, Table 6, Results C, Discussion: five training runs / four unique partitions. **Introduction contributions originally said only “five-seed check.”** Patched (see Correction 1). | VERIFIED after patch |
| GKT | Table 5 + subsection E: ASSISTments fold 0 / seed 42 only | VERIFIED |
| CL4KT | “protocol adapter, not an official checkpoint” (Results E); Introduction “CL4KT-style adapter” / “single-fold” | VERIFIED |
| Temporal | Discussion D: “single corrected cutoff (seed 42), not a multi-cutoff variance estimate.” Claim B in `analysis/claim_evidence_matrix.md`. Gate numbers are learner-based, not temporal. | VERIFIED |

---

## Correction applied

**Correction 1 (wording only, no numbers).** Introduction contributions (iii) originally: “a five-seed check of the sparse–dense FAR gap on ASSISTments 2012.” That did not meet the required dual disclosure (five training runs / four unique partitions). Replaced with: “a check of the sparse–dense FAR gap on ASSISTments 2012 across five training runs / four unique learner partitions.” Abstract, Methods, Results, Discussion, and Table 6 already used the dual wording. No table cell changed.

No other inconsistency was found in the audited sections.

---

## Abstract

| ID | Claim | Source | Status |
|----|-------|--------|--------|
| A1 | SimpleKT ECE `0.114` dense → `0.228` sparse | 3-d.p. of Table 4 / `punchline_ece.csv` 4part `0.11356` / `0.22803` | VERIFIED |
| A2 | Limited occupancy, \(N\approx 415\) | Table 4 sparse \(N=415\) (mean `415.25` events) | VERIFIED |
| A3 | Junyi: no learner-based sparse stratum | Table 4 caption; `summary_4part_bucket.csv` has no Junyi sparse SimpleKT row with events | VERIFIED |
| A4 | XES3G5M SimpleKT ECE essentially flat | Table 4 `0.1145` → `0.1114` → `0.1248` | VERIFIED |
| A5 | \(\tau=0.7\) | locked display threshold; `c_threshold_simulate.py` `DISPLAY_TAU = 0.7` | VERIFIED |
| A6 | SimpleKT FAR `0.196` dense → `0.268` sparse, one ASSISTments fold | Table 5 seed 42; `ijiet08_seed42_gate_points.csv` | VERIFIED |
| A7 | Gap positive on all five training runs across four unique learner partitions (mean `0.047`) | Table 6; `c2_fivefold_verdict.txt` SimpleKT `dFM mean=0.047` `pos=5/5`; fivefold CSV mean `0.04746` | VERIFIED |
| A8 | Simulated gate, not classroom | qualitative protocol; matches Table 5 caption | VERIFIED |

---

## Introduction

| ID | Claim | Source | Status |
|----|-------|--------|--------|
| I1 | \(\tau\), FAR \(=P(y=0\mid p\ge\tau)\) | definition, not a fitted number | VERIFIED |
| I2 | XES sparse AUC higher than dense for DKT and SimpleKT | Results A; `summary_4part_bucket.csv` DKT `0.857` vs `0.817`; SimpleKT `0.847` vs `0.755` | VERIFIED |
| I3 | SimpleKT ECE increases dense→sparse on ASSISTments; higher FAR at \(\tau=0.7\); Junyi sparse empty; XES ECE essentially absent gradient | Tables 4–5; no extra point estimates in Intro | VERIFIED |
| I4 | Contributions (iii): five-run FAR check | After Correction 1: five training runs / four unique learner partitions, matching Abstract | VERIFIED |
| I5 | GKT and CL4KT-style adapter: exploratory **single-fold** on ASSISTments | Results E; seed 42 / fold 0 only | VERIFIED |

No other numerals appear in the Introduction.

---

## Results

### A. Aggregate discrimination (Table 3)

All cells: `summary_4part_overall.csv`, \(n_{\mathrm{partitions}}=4\). Predictions: official rerun CSVs. Script: `recompute_four_partition_summaries.py`.

| ID | Claim | CSV (rounded as in table) | Status |
|----|-------|---------------------------|--------|
| R3.1 | ASSISTments IRT AUC `0.5000`, ACC `0.6973±0.0004` | `0.5`, `0.697339±0.000411` | VERIFIED |
| R3.2 | ASSISTments DKT `0.6979±0.0014` / `0.7182±0.0014` | `0.697947±0.001446` / `0.718171±0.001408` | VERIFIED |
| R3.3 | ASSISTments SimpleKT `0.6837±0.0025` / `0.6996±0.0032` | `0.683699±0.002461` / `0.699563±0.003154` | VERIFIED |
| R3.4 | Junyi IRT `0.5000` / `0.7053±0.0018` | `0.5` / `0.705317±0.001751` | VERIFIED |
| R3.5 | Junyi DKT `0.7320±0.0009` / `0.7343±0.0015` | `0.731957±0.000921` / `0.734297±0.001521` | VERIFIED |
| R3.6 | Junyi SimpleKT `0.7231±0.0030` / `0.7274±0.0015` | `0.723122±0.003049` / `0.727409±0.001462` | VERIFIED |
| R3.7 | XES IRT `0.5000` / `0.7961±0.0031` | `0.5` / `0.796051±0.003092` | VERIFIED |
| R3.8 | XES DKT `0.8171±0.0022` / `0.8327±0.0032` | `0.817121±0.002230` / `0.832679±0.003205` | VERIFIED |
| R3.9 | XES SimpleKT `0.7557±0.0013` / `0.8067±0.0037` | `0.755706±0.001325` / `0.806711±0.003660` | VERIFIED |
| R3.10 | XES sparse vs dense AUC: DKT `0.857` vs `0.817`; SimpleKT `0.847` vs `0.755` | bucket CSV `0.857065` vs `0.816947`; `0.846849` vs `0.754625` | VERIFIED |
| R3.11 | Junyi learner-based sparse empty | no Junyi sparse events under registered cuts | VERIFIED |

### B. Calibration (Table 4)

Source: `summary_4part_bucket.csv` SimpleKT (and DKT/IRT as cited). \(N\) = mean test events over four partitions.

| ID | Claim | CSV | Status |
|----|-------|-----|--------|
| R4.1 | ASSISTments SimpleKT dense `0.1136±0.0066`, \(N=523{,}971\) R | ECE `0.113559±0.006585`, \(N=523971.25\) | VERIFIED |
| R4.2 | medium `0.1541±0.0051`, \(N=5{,}963\) R | `0.154118±0.005063`, \(N=5963.0\) | VERIFIED |
| R4.3 | sparse `0.2280±0.0197`, \(N=415\) L | `0.228032±0.019728`, \(N=415.25\) | VERIFIED |
| R4.4 | DKT dense `0.0602±0.0022` vs sparse `0.2333±0.0084` | `0.060239±0.002210` / `0.233289±0.008377` | VERIFIED |
| R4.5 | IRT dense ECE `0.0031±0.0006` | `0.003117±0.000628` | VERIFIED |
| R4.6 | Junyi SimpleKT dense `0.0792±0.0051`, \(N=3{,}232{,}614\); medium `0.1073±0.0156`, \(N=3{,}836\) | `0.079222±0.0051` band, \(N=3232614.25\); `0.107318`, \(N=3836.25\) | VERIFIED |
| R4.7 | XES SimpleKT `0.1145`, `0.1114`, `0.1248`; sparse \(N=2{,}010\) R | `0.114472±0.001085`, `0.111446±0.007626`, `0.124805±0.008461`; \(N=2009.875\) | VERIFIED |

### C. Threshold gate (Tables 5–6)

Seed-42 points: `ijiet08_seed42_gate_points.csv`. FAR CIs: `ijiet08_seed42_kc_cluster_ci.csv` (percentile, \(B=2000\)). ΔFAR SimpleKT CI in prose: **locked C2** `c2_fivefold_verdict.txt`. Five-run: `ijiet08_fivefold_denominators.csv` + verdict file.

| ID | Claim | Trace | Status |
|----|-------|-------|--------|
| R5.1 | SimpleKT dense: \(N=528{,}018\), \(N_{\mathrm{adv}}=284{,}326\), \(N_{\mathrm{inc}}=158{,}623\); FAR `0.196 [0.186, 0.208]`; \(E[\mathrm{FAR}]=0.113\); Excess `0.083`; Miss `0.352` | gate CSV + CI CSV | VERIFIED |
| R5.2 | SimpleKT sparse: \(N=444\), \(N_{\mathrm{adv}}=235\), \(N_{\mathrm{inc}}=197\); FAR `0.268 [0.202, 0.337]`; \(E=0.050\); Excess `0.218`; Miss `0.320`; \(\Delta\mathrm{FAR}=+0.072\) | same | VERIFIED |
| R5.3 | DKT FAR `0.200 [0.190, 0.211]` / `0.296 [0.221, 0.383]`; \(E\) `0.147`/`0.057`; Excess `0.053`/`0.239`; Miss `0.398`/`0.365`; \(N_{\mathrm{adv}}\) `315{,}650`/`243` | same | VERIFIED |
| R5.4 | GKT (train-only) FAR `0.205 [0.194, 0.217]` / `0.220 [0.149, 0.295]`; \(E\) `0.163`/`0.157`; Excess `0.042`/`0.063`; Miss `0.455`/`0.234`; \(N_{\mathrm{adv}}\) `351{,}503`/`209` | same; seed 42 only | VERIFIED |
| R5.5 | CL4KT (adapter) FAR `0.185 [0.176, 0.194]` / `0.240 [0.159, 0.330]`; \(E\) `0.175`/`0.116`; Excess `0.010`/`0.124`; Miss `0.359`/`0.244`; \(N_{\mathrm{adv}}\) `307{,}479`/`200` | same; adapter, not official checkpoint | VERIFIED |
| R5.6 | Seed-42 ΔFAR CI: SimpleKT `[0.006, 0.138]` (locked C2); DKT `[0.019, 0.175]`; GKT `[−0.054, 0.092]`; CL4KT `[−0.018, 0.142]` | C2 verdict for SK/DKT; CI CSV for GKT/CL4KT (and FAR bounds) | VERIFIED |
| R6.1 | SimpleKT mean ΔFAR `0.047`, sd `0.033`, `5/5` runs (4 partitions) | verdict `mean=0.047 sd=0.033 pos=5/5`; CSV mean `0.04746`, sample sd `0.03275` | VERIFIED |
| R6.2 | Mean sparse \(N=413\), \(N_{\mathrm{adv}}=227\), \(N_{\mathrm{inc}}=155\) | fivefold CSV means `412.6`, `227.4`, `155.4` | VERIFIED |
| R6.3 | DKT mean ΔFAR `0.033`, sd `0.048`, `3/5` runs; \(N_{\mathrm{adv}}=226\) | verdict + CSV `0.03318`, `0.04772`, `226.4` | VERIFIED |
| R6.4 | XES SimpleKT ΔFAR negative `5/5`; ΔMiss mean `+0.112` `5/5` | `c2_fivefold_verdict.txt` | VERIFIED |
| R6.5 | Digit coincidence: seed-42 \(E[\mathrm{FAR}]=0.113\) vs four-partition ECE `0.114` | Table 5 vs Table 4; distinguished in prose | VERIFIED |

### D. Dataset conditions, regression, sparsification (Tables 7–8)

Structural rows: `dataset_sparse_diagnostic_profile.csv` (learner_based). ECE arrows: four-partition Table 4. Regression: `regression_results.csv`. Table 8: `analysis/a9/statistical_summary.csv`.

| ID | Claim | Trace | Status |
|----|-------|-------|--------|
| R7.1 | Sparse mass `18.9%` / `0%` / `22.5%` | profile `0.1887` / `0.0000` / `0.2252` | VERIFIED |
| R7.2 | Sparse \(N\) `415` (L) / empty / `2{,}010` (R) | Table 4 four-partition \(N\) | VERIFIED |
| R7.3 | Difficulty ρ `−0.227`, `−0.416`, `+0.087` | `freq_difficulty_rho` `−0.2274`, `−0.4164`, `+0.0871` | VERIFIED |
| R7.4 | SimpleKT ECE `0.114→0.228`; Junyi dense→medium only; XES `0.114→0.125` | 3-d.p. of Table 4 `0.1136→0.2280`; `0.1145→0.1248` | VERIFIED |
| R7.5 | “About 19% of KCs” below sparse threshold on fold 0 | `18.9%` rounded | VERIFIED |
| R7.6 | Item support: median `44.5` (dense `205` vs sparse `1`); Junyi median `18`, IQR `5`; XES median `3` (dense `9` vs sparse `1`) | profile medians / IQR | VERIFIED |
| R7.7 | Curriculum ρ `−0.308`, `−0.324`, `−0.125` | `freq_curriculum_rho` `−0.3075`, `−0.3244`, `−0.1249` | VERIFIED |
| R7.8 | Regression \(n=478\), `2{,}645`, `1{,}263` KCs | `regression_results.csv` weighted SimpleKT `n` | VERIFIED |
| R7.9 | log-freq coef `−0.079 [−0.097, −0.061]`, `−0.010 [−0.014, −0.007]`, `−0.117 [−0.171, −0.063]` | weighted `log_train_freq` rows | VERIFIED |
| R7.10 | Learner exposure ASSISTments `+0.019 [0.010, 0.027]` | weighted `n_train_learners` `0.01857 [0.00979, 0.02736]` | VERIFIED |
| R8.1 | 30 originally dense KCs, seed 42, fold 0 | `a9/selected_kcs.csv`; `a9_analyze.py` | VERIFIED |
| R8.2 | ASSISTments DKT 500: `−0.047 [−0.060, −0.033]` | `statistical_summary.csv` `−0.04652`, CI `−0.06031, −0.03254` | VERIFIED |
| R8.3 | ASSISTments SimpleKT 50: `+0.002 [−0.021, +0.025]` | `+0.00217`, CI `−0.02130, +0.02534` | VERIFIED |
| R8.4 | Junyi DKT 500: `−0.021 [−0.041, −0.001]` | `−0.02080`, CI `−0.04135, −0.00122` | VERIFIED |
| R8.5 | Junyi SimpleKT 50: `+0.135 [+0.110, +0.161]` | `+0.13503`, CI `+0.11030, +0.16114` | VERIFIED |
| R8.6 | XES DKT 500: `−0.008 [−0.019, +0.004]` | `−0.00800`, CI `−0.01860, +0.00379` | VERIFIED |
| R8.7 | Observational gradient `0.114→0.228` not reproduced by sparsification | Table 4 vs R8.3 | VERIFIED |

### E. Exploratory GKT / CL4KT

| ID | Claim | Trace | Status |
|----|-------|-------|--------|
| RE1 | Scored only on ASSISTments 2012 fold 0 (seed 42) | `c_threshold_simulate.py` `FOLD, SEED = 0, 42`; Table 6 note “GKT/CL4KT remain seed 42 only” | VERIFIED |
| RE2 | CL4KT is a protocol adapter, not an official checkpoint | Results E wording; Table 5 row “CL4KT (adapter)” | VERIFIED |
| RE3 | GKT FAR `0.205` vs `0.220`; \(\Delta\mathrm{FAR}=+0.015\); CI `[−0.054, 0.092]` includes 0 | gate CSV Δ `0.01475`; CI CSV | VERIFIED |
| RE4 | CL4KT adapter FAR `0.185` vs `0.240`; ΔFAR CI `[−0.018, 0.142]` includes 0 | CI CSV `−0.01770, 0.14224` | VERIFIED |

---

## Discussion

| ID | Claim | Source | Status |
|----|-------|--------|--------|
| D1 | XES sparse AUC > dense (DKT, SimpleKT), Reliable occupancy | same as R3.10 | VERIFIED |
| D2 | ASSISTments SimpleKT ECE rise, Table 4 \(N=415\) Limited | Table 4 | VERIFIED |
| D3 | XES SimpleKT ECE essentially flat, Reliable sparse occupancy | Table 4 \(N=2{,}010\) | VERIFIED |
| D4 | Tables 5–6: ΔFAR positive in all five training runs spanning four unique student partitions | Table 6; fivefold CSV / C2 | VERIFIED |
| D5 | Sparse mass `18.9%`, `0%`, `22.5%`; \(N=415\) / empty / `2{,}010`; ρ `−0.227`, `−0.416`, `+0.087`; item medians `44.5`, `18`, `3`; curriculum ρ `−0.308`, `−0.324`, `−0.125` | Table 7 + profile CSV | VERIFIED |
| D6 | Table 8 does not reproduce observational ASSISTments SimpleKT ECE gradient | Table 8 vs Table 4 | VERIFIED |
| D7 | GKT and CL4KT adapter: exploratory, single-fold, ASSISTments-only | Results E | VERIFIED |
| D8 | Temporal evaluation: **single corrected cutoff (seed 42)**, not a multi-cutoff variance estimate | `analysis/claim_evidence_matrix.md` Claim B; Methods: gate numbers not from temporal split | VERIFIED |
| D9 | Main multi-run summaries use only four unique learner partitions (2025 and 2026 share a split) | Methods + four-partition script `DUP_A, DUP_B = 2025, 2026` | VERIFIED |

---

## Conclusion

| ID | Claim | Source | Status |
|----|-------|--------|--------|
| C1 | ASSISTments SimpleKT association under Limited sparse support | Table 4 sparse L \(N=415\) | VERIFIED |
| C2 | Junyi learner-based sparse bucket empty | Table 4 | VERIFIED |
| C3 | XES3G5M SimpleKT ECE essentially flat | Table 4 | VERIFIED |
| C4 | Simulated decision-error check, not a new KT model, not a classroom intervention | protocol; no extra numerals | VERIFIED |

Conclusion contains no additional point estimates.

---

## Claims that must not be “corrected” toward stale files

| Stale / alternate artifact | Why not the manuscript |
|----------------------------|------------------------|
| `punchline_ece.csv` **5run** rows (`0.1131`, `0.2250`, \(N=412.6\)) | Tables use **4part** |
| `a5_condition_verdicts.csv` sparse \(N=403\), ECE `0.113→0.158→0.225` | hardcoded seed-42/5-run block in `a5_dataset_diagnostic_profile.py` |
| `ijiet08_seed42_kc_cluster_ci.csv` SimpleKT ΔFAR `[0.009, 0.141]` | display locked C2 `[0.006, 0.138]` |
| Gate sparse \(N=444\) vs ECE sparse \(N=415\) | dual numbering: seed 42 vs four-partition mean |

---

## Verdict

- **NOT TRACEABLE claims in the audited sections: none.**
- **NEEDS CORRECTION:** one wording item (Introduction five-seed phrase) → patched; numbers unchanged.
- All listed numerals in Abstract, Introduction, Results, Discussion, and Conclusion are **VERIFIED** after that patch.
- Compile: named and blind PDFs after Correction 1 (`source/prepare_step19.py`).
