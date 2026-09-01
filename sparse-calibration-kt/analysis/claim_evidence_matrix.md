# Claim–evidence matrix (A10)

Wording strength: **DESCRIPTIVE** | **ASSOCIATIONAL** | **CONTROLLED_EXPERIMENT** | **CAUSAL**.
CAUSAL is unused: no claim in this manuscript meets causal identification.

---

## Finding 1 — Lower KC frequency does not imply universal AUC degradation

| Field | Content |
|--------|---------|
| **Claim** | Predictive AUC does not fall monotonically with lower train-only KC frequency on every dataset. |
| **Source** | Table 5 (`tab:strata_learner`); Figure 2; RQ1 in `04_experiments.tex` |
| **Statistical support** | Learner-based DKT/SimpleKT: ASSISTments non-monotonic; Junyi sparse/very-sparse empty; XES3G5M sparse AUC *higher* than dense (DKT 0.8547 vs 0.8168; SimpleKT 0.8455 vs 0.7548). DeLong tests (Table 4) compare *overall* DKT vs SimpleKT, not sparse-vs-dense AUC. |
| **Limitation** | Sparse/very-sparse cells carry L/I flags; XES explanations (hierarchy, item features, multi-skill) are hypotheses, not tested. |
| **Strength** | DESCRIPTIVE |

---

## Finding 2 — Calibration can be more sensitive than aggregate discrimination in some sparse-concept regimes

| Field | Content |
|--------|---------|
| **Claim** | On ASSISTments 2012, SimpleKT ECE rises from dense to sparse while aggregate AUC remains competitive. |
| **Source** | Table 9 (`tab:calibration_learner`); Table 3 overall AUC; reliability diagrams (Junyi temporal, Figure `fig:reliability_junyi_temporal`) |
| **Statistical support** | SimpleKT ECE $0.1136\pm0.0066$ (dense) → $0.1541$ (medium) → $0.2280\pm0.0197$ (sparse, Limited, $N=415$), four unique partitions. DKT REL $0.0053\to0.0301\to0.0624$. Overall DKT AUC $0.6979\pm0.0014$. |
| **Limitation** | Sparse ECE is Limited-flag; very-sparse is Insufficient. Pattern is dataset-specific (see Finding 3). |
| **Strength** | DESCRIPTIVE (stratum ECE); not a test that calibration *always* fails first. |

---

## Finding 3 — The calibration–frequency relationship is dataset-dependent

| Field | Content |
|--------|---------|
| **Claim** | A sparse-stratum ECE rise is visible on some datasets and absent on others. |
| **Source** | Table 9; Table 12 (`tab:a5` / dataset conditions); Section `sec:a5_dataset_dependent` |
| **Statistical support** | ASSISTments SimpleKT monotonic ECE rise. Junyi learner-based sparse buckets empty. XES3G5M SimpleKT ECE flat; IRT inverted; DKT ECE increases. Spearman $\bar\rho(\log(1+f_{\mathrm{train}}),\mathrm{ECE})$: −0.60 / −0.43 / −0.23 (all $p<0.001$). |
| **Limitation** | Three datasets, protocol thresholds pre-registered; occupancy depends on split and preprocessing. |
| **Strength** | ASSOCIATIONAL (KC-level correlations); DESCRIPTIVE (stratum tables). |

---

## Finding 4 — Observable factors explain part of the heterogeneity; frequency is not a universal dose–response

| Field | Content |
|--------|---------|
| **Claim A** | After training-only covariates, $\log(1+f_{\mathrm{train}})$ remains associated with SimpleKT ECE in all three datasets, with varying magnitude; difficulty is an additional associate. |
| **Source** | Section `sec:a4_confounding`; CHANGELOG_A4 |
| **Statistical support** | Weighted regression $\hat\beta$ on $\log(1+f_{\mathrm{train}})$: ASSISTments −0.079; Junyi −0.010; XES −0.117 (all $p<0.001$ weighted). Unweighted XES $p=0.18$. Matched difficulty tertiles: 8/9 comparisons. |
| **Limitation** | Observational; residual confounding possible; difficulty proxy is $1-\bar c_{\mathrm{train}}$, not IRT $\theta$. |
| **Strength** | ASSOCIATIONAL |

| Field | Content |
|--------|---------|
| **Claim B** | Reducing training rows for the *same* originally dense KCs increases within-KC ECE only in some dataset–model cells. |
| **Source** | Table 16 (`tab:a9_sparsification`); Figure `fig:a9_sparsify`; Appendix `app:a9_sparsify` |
| **Statistical support** | Bootstrap over 30 KCs, seed 42. ASSISTments DKT t500 $\Delta$ECE −0.047 [−0.060, −0.033]. Junyi SimpleKT t500/t100/t50 $+0.101$ / $+0.132$ / $+0.135$ (CIs exclude 0). XES SimpleKT t50 $+0.032$ [0.021, 0.043]. |
| **Limitation** | One seed; 100% control is the published export; early stopping on reduced trains; 30 KCs per dataset; does not identify a causal law for naturally sparse KCs. |
| **Strength** | CONTROLLED_EXPERIMENT (within-KC downsampling). Not CAUSAL for real-world sparsity. |

---

## Finding 5 — Sparse-concept diagnostics are conditionally important

| Field | Content |
|--------|---------|
| **Claim** | Sparse-stratum calibration *claims* are high-priority when sparse mass, evaluation support, and either a calibration association or cold-start exposure are present; occupancy reporting remains useful when those claims are not supported. |
| **Source** | Tables 14–15; Section `sec:a8_when_needed` |
| **Statistical support** | Framework C1–C5 reuses pre-registered $f_{\mathrm{train}}<100$ and R/L/I flags. ASSISTments: High; Junyi learner-based: Low (empty sparse); XES: High reporting, Moderate SimpleKT gradient. |
| **Limitation** | C4 (deployment) is qualitative and not estimated from the logs. Framework is a reporting aid, not a fitted predictor of ECE. |
| **Strength** | DESCRIPTIVE (framework application). |

---

## Finding 6 — L1–L8 is a reproducible audit workflow; L8 has empirical value

| Field | Content |
|--------|---------|
| **Claim A** | L1–L7 operationalize standard split/train-only/validation-only safeguards as named checks with artifacts. |
| **Source** | Table 1; Section `sec:audit`; P4 |
| **Statistical support** | PASS/FAIL logs in the artifact; no detection experiment for L1–L7. |
| **Limitation** | Not a new auditing methodology. |
| **Strength** | DESCRIPTIVE |

| Field | Content |
|--------|---------|
| **Claim B** | L8 flagged a temporal prediction–label misalignment; after correction, warm-cohort AUC recovered. |
| **Source** | Appendix `app:alignment`; RQ4; Table 6 |
| **Statistical support** | Pre-correction: near-random deep-KT AUC on *warm* temporal cohorts; IRT remained informative. Post-correction warm AUC: Junyi DKT/SimpleKT 0.6949 / 0.7167; XES 0.6626 / 0.6615; ASSISTments 0.6606 / 0.6734. |
| **Limitation** | One caught defect in this codebase; single temporal cutoff. |
| **Strength** | DESCRIPTIVE (audit case). |

| Field | Content |
|--------|---------|
| **Claim C** | On six injected alignment-fault classes, L8 detected 23/60 faults (0/6 false positives on clean copies); missed adjacent-timestep prediction shifts (F3). |
| **Source** | Table 13; Appendix `app:l8_fault` |
| **Statistical support** | 23/60 = 38.3% detection; F1/F2/F5 caught; F3 none. Thresholds not retuned on injected faults. |
| **Limitation** | Faults injected into existing CSVs, not a full training-pipeline attack surface. Not a general bug detector. |
| **Strength** | CONTROLLED_EXPERIMENT (fault injection). |

---

## Simulated global-threshold decision error (Direction C)

| Field | Content |
|--------|---------|
| **Claim** | On ASSISTments 2012 fold 0, a global $\tau=0.7$ yields higher SimpleKT FM among advances on sparse than dense KCs; train-only GKT shrinks $\Delta$FM. Not a classroom policy. C4 remains qualitative. |
| **Source** | `sec:threshold_simulation`; Tables `tab:gkt_cl4kt_fold0`, `tab:c_tau07` |
| **Statistical support** | SimpleKT seed-42 $\Delta$FM $=+0.072$ (0.268 vs 0.196), Limited $N=444$. Five-fold mean $\Delta$FM $=0.047$ (sd $0.033$, $5/5$ positive). Seed-42 KC-cluster bootstrap 95% CI $[0.006, 0.138]$. GKT $\Delta$FM $=+0.015$ (seed 42 only). XES SimpleKT $\Delta$Miss mean $+0.112$ on $5/5$ folds despite flat ECE. |
| **Limitation** | Single seed; CL4KT adapter; sparse Limited; simulated gate; GKT train-only graph. |
| **Strength** | DESCRIPTIVE (thresholded rates); not CAUSAL. |

---

## Other major claims

| Claim | Source | Support | Limitation | Strength |
|--------|--------|---------|------------|----------|
| Aggregate DKT vs SimpleKT AUC differs on learner-based splits | Table 4 | DeLong, Bonferroni | Not a sparse-KC test | ASSOCIATIONAL |
| IRT learner-based AUC = 0.50 is a base-rate fallback, not a calibrated success | Table 3, 9 | RES = 0 | Implementation-specific | DESCRIPTIVE |
| Deep KT AUC is near-random or worse on strict/limited temporal cold-start | Table 6 | e.g. XES DKT 0.4642, $N=233{,}214$ (R) | Difficulty confound untested | DESCRIPTIVE |
| Protocol does not propose a new KT model | Intro, scope | Design | — | DESCRIPTIVE |

---

## Words not used as overclaim

The revised narrative avoids: proves; demonstrates universally; causes (except “we do not claim … causes”); always (except negations); robust across datasets; establishes a novel audit methodology.
