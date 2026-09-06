# CHANGELOG_P0 — Align main text with GS Hậu roadmap v3.0

**Date:** 2026-09-03  
**Pages:** 8–10 allowed. **Retrain:** no. **Locks:** ASSISTments ECE `0.1136`/`0.2280`; FAR `0.196`/`0.268` remain as a simulated probe.

| Phase | Change |
|---|---|
| 1 | Removed TSCDA name; GKT/CL4KT not scored; II.B → evaluation rigor/leakage |
| 2 | Contributions C1 protocol+L1–L7, C2 ECE/Brier/reliability, C3 artefact |
| 3 | Table 9 leakage; Table 10 Brier U-R-R; Table 11 cold-start feasibility; Fig. 2 reliability |
| 4 | `analysis/leakage_audit_log.csv`; `docs/how_to_reproduce.md` |
| 5 | Named+blind PDF 9/9 pages; OJS pack synced 2026-09-03 |
| 6 | Editorial 2026-09-04: drop leftover “locked C2”; Table 7 estimability labels E1–E3; cite GKT/CL4KT [8][9] as related literature only; keywords protocol/leakage; L6 = final checkpoint |
| 7 | Grammar/caption: “an E1–E2”; Table 9 PASS includes fixed schedule (L6 final checkpoint) |
| 8 | FAR Tables 5–6 → SI S5–S6; main tables renumbered 1–9; Table 9 cold-start Autofit |

| 9 | SI Table S7 three-cut (20/100/500 lock; Alt-1 10/50/250; Alt-2 30/150/750) on frozen T-KT CSVs; `how_to_reproduce.md` points to `reproduce_one_dataset.sh` and states it does not recreate locked ECE/FAR |

| 10 | Official SimpleKT [4] on ASSISTments 4 partitions: AUC `0.7700±0.0013`, ACC `0.7522±0.0014`; ECE dense `0.0203±0.0035` / medium `0.0262±0.0025` / sparse `0.0884±0.0187` (N=415 L). ΔECE +0.068; added Table 4 row + Table 5 three rows. T-KT ECE `0.1136`/`0.2280` unchanged. BKT still not scored. Junyi/XES official ECE not added. |

| 11 | IV.B pointer to SI Table S7 (3-cut does not flip T-KT dense→sparse ECE). IV.C: seed-42 ΔFAR CI `[0.006, 0.138]` called wide; sparse ECE Limited N=415. Table 9 Small Caps off. T-KT ECE/FAR locks unchanged. |

| 12 | V.B: EdTech skip/advance gates consume *p*, not AUC; protocol is evaluation, not a production threshold. T-KT ECE/FAR locks unchanged. |
| 13 | Restore justify + Text style on 9 leftover Normal paragraphs (IV.D, IV.E, V.A–D, VI). No numeric edits. |
| 14 | Close GS v3.0 items 6/7/10 without BKT or lock edits: SI S8 bucket AUC/ACC; SI S9 baseline inventory (IRT fallback; no 2–3% pyKT Assist2012 claim); `scripts/rebuild_locked_tables.sh` verifies ECE 0.1136/0.2280 from frozen CSVs. IV.A / Limitations pointers. |
| 15 | Table 9 XES very-sparse → masked a2b: N 112→114, T-KT ECE 0.183→0.184, DKT ECE 0.184→0.173; prose N≈112→N≈114. Assist 0.245/0.178 unchanged. T-KT ECE/FAR locks unchanged. |
| 16 | Table 9 caption: XES very-sparse = same masked series as Table 5 (N=114). Locks file records 0.184/0.173. |
| 17 | RQ3 → estimability + train-only-cut robustness; empirical-answer para no longer treats FAR as RQ3. Gate τ=0.7 remains S5–S6 probe. No numeric lock edits. |
| 18 | IV.E + Table 9 caption: 0<f<20 is the protocol very-sparse bucket, not limited-k5/k10 cold-start. Occupancy L/I ≠ k5/k10. No Table 9 cell edits. |
| 19 | Table 9 XES very-sparse flag I/L → L (printed mean N=114). ECE 0.184/0.173 and N=114 unchanged. |
| 20 | Junyi terminology: Abstract/IV.E/V.A/V.C use exercise-level operational identifier (ucid), not pedagogical KC tagging. V.C: granularity-and-estimability case. No numeric edits. |
| 21 | IV.B: ASSISTments calibration ordering unchanged under two alt cut grids (S7). S7 adds DKT rows from frozen CSVs; T-KT 0.1136/0.2280 and grids 20/100/500, 10/50/250, 30/150/750 unchanged. Official SimpleKT not regrouped. |
| 22 | New Fig. 1 pipeline (L1–L7 = Table 3). Old Fig. 1→Fig. 2 (KC distribution, PNG unchanged). Old Fig. 2→Fig. 3 (reliability 2×2). No numeric lock edits. |
| 23 | Table 3 kept fold-0. SI Table S10 = L1–L7 on 4 unique learner partitions + temporal seed 42 from frozen split files. One pointer sentence. No ECE/FAR edits. |
| 24 | IV.D secondary: keep Table 7 + short regression; drop 12-row Table 8 to SI S2; one sparsification sentence; add three-estimands paragraph (stratum ECE vs between-KC regression vs within-KC sparsification). Cold-start Table 9→8. Locks unchanged. |
| 25 | Reviewer zip/README: drop JEDM token; 8-page → 9-page; SI S1–S10; pack date 6 Sep 2026. Cover letter still records withdrawal (editor only). Locks unchanged. |
| 26 | IV.C FAR → one secondary-probe paragraph (0.196/0.268, ΔFAR=+0.072, 4/4, XES negative, S3–S6). Drop main-text denominator/CI dump and E[FAR] vs ECE sentence. RQ3 unchanged. Locks unchanged. |
| 27 | Results reorder: A AUC, B ECE/Brier/Fig.3, C cold-start (Table 7), D conditions+S7 (Table 8), E regression/sparsification, F FAR probe. No k5/k10. Locks unchanged. |
| 28 | Contributions → (i) protocol+occupancy+L1–L7; (ii) per-stratum ECE/Brier/reliability, dataset-dependent; (iii) frozen artefact + one-command table rebuild. FAR/regression/sparsification stay supporting. No C1–C3 tokens. Abstract untouched. Locks unchanged. |
| 29 | Limitations cleaned: keep mastery/3 datasets/ECE binning/R-L-I/temporal cutoff/shared split/BKT fail/local T-KT. Drop NOT RECOVERED from Limitations (Table 2 methods cells unchanged). Reproduction = frozen zip + table rebuild. No AKT swap. Abstract untouched. Locks unchanged. |
| 30 | FINAL_CLAIM_EVIDENCE.csv: 7 primary claims all VERIFIED from S8/Table 5/bucket CSV/S7/cold-start export/rebuild log. No NOT TRACEABLE or MANUAL ONLY. Locks unchanged. |
| 31 | Uplift 1–5: drop exclusive-submission from Ethical Statement; AI = Cursor Grok 4.6 only; Fig. 1 → 501.8 pt; Abstract 5-block + artefact; Intro Table 8 → Section IV.D. Cover letter keeps exclusive, AI matches. Locks unchanged. |
| 32 | Fig. 3 width 480 → 501.8 pt (aspect locked). Table 8 section rows A/B compacted to one spanning cell. No numeric edits. |
| 33 | Pack date: cover letter → 6 September 2026; editor summary matches C1–C3 (occupancy, L1–L7, one-command rebuild). Article placeholders remain Month date, 2026. Locks unchanged. |
| 34 | GO/NO-GO necessary wording/format only: C01 two alternative cut grids; C06 drop competitive AUC; C07 Fig. 1 501.8×166.5 (PNG aspect); C10 low-frequency tail mass; C12 learner-based primary + complementary temporal split (no new SI table); C13 occupancy-interpretation sentence. No numeric lock edits. Pages 9/9. |
| 35 | Generative AI Statement + cover letter: ChatGPT GPT-6 Astra, Claude Sonnet 5, Google Antigravity 2.12.0, Cursor Grok 4.6 (public versions as of 6 Sep 2026). No numeric lock edits. |

Official `pykt.models.simplekt.simpleKT` ASSISTments AUC/ECE is now in the manuscript. BKT remains un-scored (pyBKT 1.4.1 degenerate on ASSISTments fold 0 seed 42).
