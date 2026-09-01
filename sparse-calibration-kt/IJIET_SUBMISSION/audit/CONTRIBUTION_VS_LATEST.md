# Contribution vs latest KT research (2023–2026)

**Date:** 2026-08-31  
**Manuscript:** IJIET submission (updated IJIET-21: refs [21]–[22]).  
**Question:** Do the three stated contributions still hold against work published through mid-2026?

## Verdict

**Yes.** The paper’s contribution is a **diagnostic evaluation protocol**, not a new KT model. No 2024–2026 paper jointly does: (i) train-only KC-frequency strata with explicit \(f=0\), (ii) per-stratum ECE/Brier with occupancy flags, (iii) a locked-\(\tau\) simulated gate reporting FAR/Miss on sparse vs dense KCs.

## Stated contributions (Introduction)

| # | Claim | Still distinctive? |
|---|--------|-------------------|
| (i) | Train-only KC-frequency protocol + strict cold-start | Yes. Distinct from sparse attention, new-student cold start, and student/question splits. |
| (ii) | Per-stratum ECE/Brier on three public logs, R/L/I flags | Yes. Recent models add population ECE; they do not cut on \(f_{\mathrm{train}}\). Dataset-dependence (Junyi empty; XES flat) is itself a finding. |
| (iii) | Locked \(\tau=0.7\) FAR/Miss; five runs / four partitions | Yes. Closest operational neighbor (Mitton 2026) defers on uncertainty; it does not measure \(P(y=0\mid p\ge\tau)\) by train-only KC stratum. |

The manuscript correctly refuses: new architecture, new calibrator, new auditing theory, classroom intervention.

## Latest neighbors

| Paper | Year | What it does | Why it does not subsume this work | In IJIET refs? |
|-------|------|----------------|-----------------------------------|----------------|
| Yan, Tang, Shimada — SLC, arXiv:2606.14123 (ECML PKDD 2026 claim) | 2026 | Post-hoc per-item logit correction; AUC/NLL gain on sparse **items** | Method to **fix** scores after a frozen backbone. This paper **audits** frequency strata and a threshold gate. Complementary, as §II.D already says. | **[15]** |
| Huang et al. — sparseKT, SIGIR | 2023 | \(k\)-sparse **attention** | Different sense of “sparse”. Distinguished in §II.C. | **[16]** |
| Bhattacharjee & Wayllace — AIED | 2025 | New-**student** cold start | Not concept-level \(f_{\mathrm{train}}=0\). Distinguished in §II.C. | **[17]** |
| Cheng et al. — UKT, AAAI | 2025 | Gaussian/Wasserstein KT architecture; mainly AUC | New model. No train-only KC strata, no FAR. | **[21]** |
| Adaptive G-UKT, *Scientific Reports* | 2026 | Graph + uncertainty; adds NLL/ECE vs AKT/UKT | Population ECE as a model-quality score, not a frequency-stratum protocol. | No |
| Mitton et al. — selective prediction, PMLR 339 | 2026 | MC-Dropout abstention on Eedi (DKT/SAKT/AKT) | Defer uncertain predictions to a teacher. Not a locked mastery \(\tau\); not KC-frequency FAR. Closest **operational** neighbor. | **[22]** |
| EDM 2025 — “How much mastery is enough” | 2025 | BKT \(P(L_n)\) bins vs next-lesson performance | Latent BKT mastery, not next-response \(p\) calibration by KC frequency. | No |
| Purwadi et al. — IJOML | 2026 | Student-wise vs question-wise splits + ECE (MathE, logistic) | Entity cold-start + calibration, not KC-frequency strata or FAR; not pyKT-scale logs. | No |
| pyKT / SimpleKT | 2022–2023 | Standardized **population AUC** | The gap this paper names: ranking ≠ threshold decision. | **[4],[5]** |

## What this paper shows that those papers do not

1. **Joint dashboard:** AUC (Table 3) can look competitive while ECE rises on sparse KCs (Table 4) and FAR rises at \(\tau=0.7\) (Tables 5–6).
2. **Non-universal pattern:** Junyi has no learner-based sparse bucket; XES3G5M SimpleKT ECE is essentially flat (\(0.1145\)–\(0.1248\)) with Reliable \(N=2{,}010\), yet \(\Delta\)Miss can still be positive. Latest architecture papers typically do not report this counter-pattern.
3. **Within-KC control (Table 8):** sparsifying originally dense KCs does not reproduce the observational ASSISTments SimpleKT ECE gradient — so frequency is not a universal cause.
4. **Occupancy honesty:** sparse ASSISTments ECE is Limited (\(N=415\)), not a high-\(N\) law.

## Reviewer risk (optional, not required to keep the contribution)

UKT and Mitton are now **[21]** and **[22]** (IJIET-21). They are positioned as complementary (architecture / abstention), not as missing baselines. Experimental tables were not changed.

JEDM related work already named csKT, CLST, and LLM cold-start methods; IJIET still omits those to keep the list short. That thinning does **not** erase the diagnostic gap.

## Do not overclaim in cover letters

- Not “first calibration paper in KT” (Pelánek 2015; Guo 2017; Yan 2026).
- Not “first mastery-threshold paper” (BKT 0.95 literature; Rollinson & Beck 2013).
- Accurate claim: **first joint, train-only KC-frequency audit of calibration + simulated false-advance on standard deep KT backbones across three public logs, with occupancy flags and an explicit empty-bucket outcome.**
