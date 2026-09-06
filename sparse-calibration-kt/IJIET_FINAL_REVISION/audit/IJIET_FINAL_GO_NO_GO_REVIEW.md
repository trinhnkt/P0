# IJIET final independent GO/NO-GO audit

**Date:** 6 September 2026  
**Mode:** audit only. Manuscript, numbers, models, and tables were not edited.  
**Compiled source actually inspected:** `IJIET_FINAL_REVISION/output/main_ijiet_blind.pdf` (9 pages).  
**Requested filename `main_ijiet_blind(1).pdf`:** not found in the repository, Desktop, or Downloads. The living blind PDF is treated as the corresponding compiled artifact. Twin named source: `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`.  
**Word headings** were read from the `.docx` (not from PDF text-extraction order).

Special returns used below:

- `TITLE_REPRODUCIBILITY_DEFENSIBLE = CONDITIONAL` (C03)
- `BASELINE_STATUS = ACCEPT_CURRENT` (C04)
- Fig. 1 = `MINOR_REFORMAT` (C07)
- Fig. 3 = `KEEP_ASSIST_JUNYI` (C08)
- Table 6 = `KEEP_MAIN` (C09)
- Temporal = `ADD_SUPPLEMENTARY_TEMPORAL_TABLE` (C12)
- AI statement = `AUTHOR_CONFIRMATION_REQUIRED` (C14)
- Publisher dates = `KEEP_TEMPLATE_PLACEHOLDER` (C15)

---

## C01 — Frequency-cut sensitivity count

**Status:** REQUIRED_FIX

1. **Manuscript.** Introduction empirical-answer paragraph: “Three alternative train-only frequency cuts leave that ASSISTments T-KT rise positive (Supplementary Table S7).” Results IV.D: “two alternative train-only cut grids.” Abstract does not repeat the count.
2. **Code / SI.** `supplementary/Table_S7_threecut.tex` and `analysis/si_threecut_tkt_dkt.csv`: one **primary** grid Main (20/100/500) reprinting Table 5, plus **two alternatives** Alt-1 (10/50/250) and Alt-2 (30/150/750).
3. **Impact.** Wording only. Locked ECE 0.1136 / 0.2280 unchanged.
4. **Risk if unchanged.** Reviewer can treat Intro vs Results vs S7 as sloppy counting and ask whether a third unpublished grid exists.
5. **Action.** Change the Introduction sentence to “two alternative train-only frequency cut grids.” Do not count Main as an alternative. Leave S7 and Results as they are.
6. **Files.** `manuscript/main_ijiet_full.docx` (Introduction paragraph only). Then rebuild blind PDF.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Aligns Results and S7; does not conflict with Table 5.
10. **Confidence.** HIGH

---

## C02 — Limited cold-start k5/k10

**Status:** OPTIONAL

1. **Manuscript.** Already correct: strict is `f_train=0`; very-sparse is `0<f_train<20`; “not a limited cold-start (k5/k10) group.” Table 7 is feasibility. Occupancy L/I ≠ k5/k10. XES very-sparse N=114 L.
2. **Code / artifacts.** Registered convention in `src/recalculate_diagnostics.py` and `results/tables/clean_cold_start_results_summary.csv` is **inclusive of zero**: `k5: train_freq<=5`, `k10: train_freq<=10`, `warm: train_freq>10`. That is **not** `1<=f_train<=5`. Junyi temporal k5/k10 coincide with strict (0 KCs with `1<=f<=10`; `results/reports/cold_start_group_audit_report.md`). Old JEDM Table VI used this grouping; current Roadmap/P0 changelog (phase 27) deliberately kept k5/k10 out of main Table 7.
3. **Impact.** If added: new SI numbers only. No change to Table 7 locks.
4. **Risk if unchanged.** A reviewer who remembers k5/k10 may ask for them. The paper already says they are not the Table 7 slice.
5. **Action.** Keep Table 7 as feasibility. If added, put **registered** k5/k10 (`f<=5`, `f<=10`, including strict) in Supplementary only, with the Junyi coincidence note. Do **not** redefine very-sparse as limited cold-start. Do **not** invent a `1<=f<=5` slice unless labeled as a new grouping.
6. **Files if added.** New SI table from `clean_cold_start_results_summary.csv`; one pointer sentence. Not required.
7. **Retrain.** No.
8. **CPU recompute.** Existing CSV is enough. Fresh prediction-level recompute is optional and CPU-only.
9. **Conflict.** Adding k5/k10 to **main** Table 7 would conflict with the current disclaimer. SI-only does not.
10. **Confidence.** HIGH

---

## C03 — Reproducibility claim

**Status:** NO_CHANGE (for current wording).  
**TITLE_REPRODUCIBILITY_DEFENSIBLE = CONDITIONAL**

1. **Manuscript.** Title: “Reproducible Sparse-Concept and Calibration Diagnostics…”. Contribution (iii) and Limitations: frozen review artifact + one-command rebuild of diagnostic tables from frozen summaries (`scripts/rebuild_locked_tables.sh`). Table 2 Version/commit = NOT RECOVERED. Abstract matches (iii).
2. **Code.**  
   - **LEVEL A supported:** `scripts/rebuild_locked_tables.sh` → `scripts/p0_rebuild_locked_tables.py` verifies locked ASSISTments T-KT ECE from frozen summaries and rewrites S8/S9. Documented in `docs/how_to_reproduce.md` Track B.  
   - **LEVEL B partially supported:** S7 three-cut and Fig. 3 scripts read frozen prediction CSVs. There is no single advertised command that rebuilds every stratum/calibration table from predictions.  
   - **LEVEL C not supported as a locked claim:** `scripts/reproduce_one_dataset.sh` exists (preprocess → split → train → strata → metrics). Docs explicitly say it **does not** recreate locked ECE 0.1136/0.2280 or FAR 0.196/0.268. No `Makefile`, no `run_all.sh`, no Dockerfile, no `environment.yml`. `requirements.txt` exists. Training-container commit is NOT RECOVERED.
3. **Impact.** Current body is LEVEL A (honest). Changing the title or claiming end-to-end would be a scientific-scope change.
4. **Risk if unchanged.** A reviewer who reads “Reproducible” as LEVEL C may ask for a training image. The paper already refuses that claim.
5. **Action.** Do **not** claim end-to-end reproduction. Keep (iii) as frozen-summary rebuild. One-dataset LEVEL C regeneration is **not** required before this revision if Table 2 stays NOT RECOVERED. Optional later: pin a conda lock or regenerate one log as a supplement, without touching locked cells.
6. **Files.** None for a wording-preserving decision.
7. **Retrain.** No for the current claim. Yes only if someone later attempts LEVEL C.
8. **CPU recompute.** Track B is CPU-only. Track A is training.
9. **Conflict.** A LEVEL C claim would conflict with Table 2 and `how_to_reproduce.md`.
10. **Confidence.** HIGH

**Title verdict:** CONDITIONAL. Defensible for a **protocol / frozen-artifact** paper at LEVEL A. Not defensible if “Reproducible” is read as raw-data → trained weights → locked ECE. The body already scopes the title; do not drop “Reproducible” solely because LEVEL C is absent.

---

## C04 — Baseline deviation from P0 Roadmap

**Status:** NO_CHANGE  
**BASELINE_STATUS = ACCEPT_CURRENT**

1. **Manuscript.** Scored: IRT, DKT, T-KT on three logs; official SimpleKT [4] on ASSISTments only. BKT not scored. GKT/CL4KT/AKT not scored. Limitations and S9 state the fallback.
2. **Code / SI.** `supplementary/Table_S9_baseline_inventory.tex`: Roadmap slot is **simpleKT or AKT**; official SimpleKT is Assist-only; AKT / DKVMN / sparseKT = out of P0. Official JSON exists only at `results/reports/p0_official_simplekt_assist_ece.json`. No official SimpleKT Junyi/XES outputs. No AKT prediction exports under `results/`. BKT degeneration is documented (pyBKT 1.4.1, ASSISTments seed 42) in S9, Limitations, and `docs/how_to_reproduce.md`.
3. **Impact.** None if left as a protocol-instantiation paper.
4. **Risk if unchanged.** A methods reviewer may still want SimpleKT on three logs or a live BKT. That is a new-experiment request, not an internal inconsistency.
5. **Action.** Do **not** add training. Keep the existing deviation sentence (S9 + Limitations). Proposed one-liner if an editor asks: “P0 instantiates the protocol with two stable sequence baselines plus IRT after pyBKT degenerated; the strong pyKT-family slot is official SimpleKT on ASSISTments only.”
6. **Files.** None.
7. **Retrain.** Adding SimpleKT on Junyi/XES or AKT would require substantial new training. Not recommended for this revision.
8. **CPU recompute.** Cannot create missing official SimpleKT/AKT cells from current exports.
9. **Conflict.** Adding AKT or scoring BKT would reopen S9 and the “out of P0” Limitations sentence.
10. **Confidence.** HIGH

---

## C05 — Section heading “A. E. Secondary explanatory analysis”

**Status:** NO_CHANGE

1. **Manuscript (Word source).** Heading 2 at IV.E is exactly “E. Secondary explanatory analysis.” Next heading is “F. Secondary decision-error probe.” (`_p0_gng_headings.txt`)
2. **PDF extraction.** `get_text` concatenates Table 8 row label “A. Estimability” with the following heading, producing the false string “A. E. Secondary explanatory analysis.” Both “E. Secondary explanatory” and “F. Secondary decision-error” exist as real headings.
3. **Impact.** None. Not a scientific or heading error in source.
4. **Risk if unchanged.** PDF copy-paste tools may show “A. E.”; the printed heading is E.
5. **Action.** Do not retitle. Do not “fix” a PDF-order artifact.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Changing the heading to drop a nonexistent “A.” would be editing a phantom.
10. **Confidence.** HIGH

---

## C06 — “Competitive AUC”

**Status:** RECOMMENDED_FIX

1. **Manuscript.** Discussion: “The ASSISTments T-KT cell is an illustrative case: competitive AUC, Limited-but-estimable sparse occupancy…”
2. **Numbers in the same paper.** Table 4: DKT 0.6979±0.0014 vs T-KT 0.6837±0.0025 vs official SimpleKT 0.7700±0.0013. T-KT is below DKT and well below official SimpleKT.
3. **Impact.** Wording only. No numeric change.
4. **Risk if unchanged.** “Competitive” is not justified against the paper’s own baselines and invites a “why not SimpleKT?” reading.
5. **Action.** Replace with: “aggregate discrimination that does not reveal the sparse-stratum calibration pattern.”
6. **Files.** `manuscript/main_ijiet_full.docx` (Discussion sentence).
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** The replacement supports Contribution (ii). It does not contradict Table 4.
10. **Confidence.** HIGH

---

## C07 — Figure 1 pipeline quality

**Status:** RECOMMENDED_FIX  
**Figure verdict:** MINOR_REFORMAT (do not redraw the workflow)

1. **Manuscript.** Fig. 1 caption: pipeline with L1–L7 matching Table 3. Displayed bbox in the living PDF: **501.7 × 96.7 pt** (page 3).
2. **Source image.** Embedded PNG is **809 × 268** (aspect 3.02). Displayed aspect is 5.19, so the figure is **vertically crushed / horizontally stretched**. Generator `figures/generate_fig1_pipeline.py` uses ~6.4 pt type in a two-row banner; L-tags follow Table 3 IDs, not left-to-right order (L2 before L1), which the caption already explains.
3. **Impact.** Format only. Scientific workflow is correct.
4. **Risk if unchanged.** Print-size labels are hard to read; aspect distortion looks unprofessional for IJIET.
5. **Action.** Restore native aspect at full-width (~501.7 × 166 pt). Do **not** redraw boxes or change L1–L7 meaning. Only redraw later if, after aspect restore, type is still illegible.
6. **Files.** Word figure frame (height). PNG itself need not change.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** None.
10. **Confidence.** HIGH

---

## C08 — Reliability diagram dataset choice

**Status:** NO_CHANGE  
**Figure verdict:** KEEP_ASSIST_JUNYI

1. **Manuscript.** Fig. 3: ASSISTments dense vs sparse; Junyi dense vs medium because learner-based sparse is empty. Caption states that.
2. **Artifacts.** Fig. 3 is seed-42 diagrams. XES T-KT ECE counter-pattern is already in Table 5 / S1 (0.1176 / 0.1129 / 0.1254, sparse N=1,969 R). XES prediction exports exist (`a2b` and frozen reruns). Junyi is the empty-sparse estimability case.
3. **Impact.** Replacing Junyi with XES would be a figure-composition change, not a numeric lock change.
4. **Risk if unchanged.** A reviewer may ask “why not XES in Fig. 3?” Table 5 already answers the counter-pattern. Losing Junyi would hide the empty-bucket visual.
5. **Action.** Keep Assist + Junyi. Do not replace. An optional third XES row is polish, not required, and would need a taller figure.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** XES panels could be drawn from existing predictions (CPU) if later desired.
9. **Conflict.** Replacing Junyi would weaken the estimability story already in Table 8 / V.C.
10. **Confidence.** HIGH

---

## C09 — Brier table size

**Status:** NO_CHANGE  
**Table verdict:** KEEP_MAIN

1. **Manuscript.** Table 6 is already an extract: DKT/T-KT dense/sparse (and Junyi/XES rows) with ECE, Brier, UNC, REL, RES. Caption points to full S1.
2. **SI.** `Table_S1_calibration_full.tex` is the complete four-partition grid including IRT and medium.
3. **Impact.** Moving Junyi/XES out of main would shrink pages but cut dataset-dependence evidence for Contribution (ii).
4. **Risk if unchanged.** Table 6 is dense; still readable as a contrast table.
5. **Action.** Keep the main extract. Do not move all Brier evidence to SI. A further-compact Assist-only main table is optional polish only.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Removing Junyi/XES from main would weaken Contribution (ii).
10. **Confidence.** HIGH

---

## C10 — Terminology “sparse mass”

**Status:** RECOMMENDED_FIX

1. **Manuscript.** Discussion: “plenty of sparse mass and Reliable occupancy.” Table 8 defines sparse mass as the share of KCs with `f_train<100`.
2. **Protocol.** Registered sparse **bucket** is `20<=f_train<100`. Tail `f_train<100` also includes very-sparse and (if present) strict.
3. **Impact.** Wording only. No numeric change.
4. **Risk if unchanged.** A careful reader can equate “sparse mass” with the sparse bucket and misread XES occupancy.
5. **Action.** Replace with “low-frequency tail mass (`f_train<100`)” in the table row, caption, and the Discussion sentence. Keep the numeric share.
6. **Files.** `manuscript/main_ijiet_full.docx` (Table 8 + Discussion). SI only if it repeats the phrase.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** None if the `<100` definition is preserved.
10. **Confidence.** HIGH

---

## C11 — Regression inclusion / exclusion

**Status:** OPTIONAL

### Audit-only summary (code-traced)

| dataset | total_KCs | included_KCs | excluded_KCs | reason_counts |
|---|---:|---:|---:|---|
| ASSISTments 2012 | 265 (`kc_strata` unique) | 261 | 4 | **4 no evaluable test predictions** (`test_freq=0` on learner-based and temporal fold 0; kc_id 38, 178, 209, 291). They never enter `analysis/kc_characteristics.csv`. |
| Junyi Academy | 1326 | 1326 | 0 | — |
| XES3G5M | 865 real KCs (padding excluded) | 829 | 36 | **25 no evaluable test predictions** (`test_freq=0`, very-sparse, present in train features). **11 missing train covariates** (strict cold-start `train_freq=0`; of these, 8 also have `test_freq=0`; 3 have 1–2 test events but `inner` join to train features drops them). Padding `kc_id=-1` is not in the a2b fold-0 strata (0 padding rows). |

1. **Manuscript.** IV.E already reports 261 / 1,326 / 829 unique KCs. It does not list exclusion reasons.
2. **Code.** Assist/Junyi: `scripts/a4_confounding_analysis.py` builds ECE from prediction files then `dropna` on covariates. XES: `a2b/evaluate.py` `regression_xes()` does `met.merge(feat, how="inner")` then `dropna` on ECE and five covariates; writes `a2b/analysis/regression_input.csv` (829 rows, 829 unique KCs, no NA).
3. **Impact.** Explanation only. Coefficients unchanged.
4. **Risk if unchanged.** A reviewer may ask why 261/265 and 829/865. The reasons are ordinary complete-case rules, not a silent KC-padding error.
5. **Action.** Preferred: one Supplementary sentence or a 3-row reason table. A main Methods sentence is optional. No manuscript change is scientifically acceptable.
6. **Files if added.** SI only (`Table_S_regression.tex` note or a tiny S-table).
7. **Retrain.** No.
8. **CPU recompute.** No (counts already recovered).
9. **Conflict.** None. Do not revert XES to 830/866.
10. **Confidence.** HIGH

---

## C12 — Temporal evidence

**Status:** RECOMMENDED_FIX  
**Temporal verdict:** ADD_SUPPLEMENTARY_TEMPORAL_TABLE

1. **Manuscript.** Contribution (i) / Intro: protocol “combines learner-based and temporal views.” Main Tables 4–8 and Fig. 3 are learner-based. Limitations: single corrected temporal cutoff, seed 42. S10 includes temporal L1–L7 PASS.
2. **Artifacts (already exist; not in SI as a performance table).**  
   - `results/tables/clean_calibration_by_bucket_temporal.csv` — temporal ECE/Brier/UNC/REL/RES by dataset × model × bucket.  
   - `results/tables/clean_cold_start_results_summary.csv` and `temporal_cold_start_group_counts.csv` — temporal strict/k5/k10/warm.  
   - `IJIET_FINAL_REVISION/a2b/analysis/temporal_seed42.csv` — XES seed-42 temporal AUC/ECE/Brier including cold-start.  
   - `results/reports/temporal_prediction_alignment_audit.md` — **historical** near-0.5 AUC on old Assist/Junyi temporal files; later T11/fix reports exist. Any new SI table must use the **corrected** series only.
3. **Impact.** Adding SI is reporting, not a new experiment. Reducing the “temporal views” clause would be wording only.
4. **Risk if unchanged.** Reviewer: “you promised temporal views; Results are learner-based.” S10 + Methods + Limitations may be enough for some readers, not all.
5. **Action.** Add one Supplementary temporal table from **verified-aligned** existing exports: overall AUC (if present), stratum occupancy, ECE, Brier, strict/k5/k10, warm, alignment status. Do **not** start new temporal training. Alternative if alignment of Assist/Junyi temporal predictions cannot be certified: shorten Contribution (i) to “learner-based primary results plus a temporal split used for leakage/regression.”
6. **Files.** New SI tex + one pointer in Methods or IV. Not the main Results tables.
7. **Retrain.** No.
8. **CPU recompute.** Yes, from frozen predictions / existing CSVs. Do not use pre-alignment files.
9. **Conflict.** Do not present temporal ECE as a second main finding that rivals Table 5. Keep learner-based as primary.
10. **Confidence.** MEDIUM (table is assemblable; which CSV is the post-alignment source must be checked before numbers are copied)

---

## C13 — Wording “Success claims”

**Status:** RECOMMENDED_FIX

1. **Manuscript.** Methods, reliability flags: “Success claims require Limited or Reliable occupancy. Insufficient cells are descriptive only.”
2. **Code.** Occupancy is a descriptive N flag (`N<100` I; `100<=N<1000` L; `N>=1000` R), not a hypothesis test.
3. **Impact.** Wording / scientific register only.
4. **Risk if unchanged.** “Success claims” sounds like a performance guarantee in a diagnostic paper.
5. **Action.** Replace with: “Substantive stratum-level interpretations require at least Limited support; Insufficient cells are descriptive only.”
6. **Files.** `manuscript/main_ijiet_full.docx` (III.E).
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** None; the next sentence already says Insufficient cells are descriptive.
10. **Confidence.** HIGH

---

## C14 — Generative AI disclosure

**Status:** AUTHOR_DECISION_REQUIRED  
**AI verdict:** AUTHOR_CONFIRMATION_REQUIRED

1. **Manuscript (living).** “During manuscript preparation, the authors used Cursor Grok 4.6 for language polishing, formatting, consistency checking, and reproducibility-prompt preparation.” ChatGPT / Claude / Antigravity are absent (0 hits in the living blind PDF).
2. **Project records.** Older drafts and `audit/AI_TOOL_VERSION_AUDIT.md` / CHANGELOG A15–A20 named ChatGPT, Claude, and Google Antigravity. **No session log retains build IDs.** Versions GPT-5.6 / Sonnet 5 / Antigravity 2.11.0 were later filled from public pages and then stripped (phase 31) because they were not log-verified. This revision cycle’s documented tool is Cursor Grok 4.6.
3. **Impact.** Disclosure wording only. No results change.
4. **Risk if unchanged.** If other tools **were** used on this manuscript version, IJIET §6.3 is incomplete. If they were not, re-adding them would over-disclose and re-introduce unverifiable versions.
5. **Action.** Author must confirm, for **this** IJIET manuscript version, whether ChatGPT / Claude / Antigravity were used for manuscript preparation.  
   - If **no**: keep the living Grok-only statement (`AI_STATEMENT_COMPLETE`).  
   - If **yes**: name the product and **only** a version that is actually known; do not invent GPT-5.6 / Sonnet 5 / 2.11.0.  
   Do not add tools used only for non-manuscript research work.
6. **Files.** Generative AI Statement in the named Word file, only after author confirmation.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Re-adding unverifiable versions would conflict with the phase-31 honesty rule already applied.
10. **Confidence.** MEDIUM (Grok-4.6 use is HIGH; historical other-tool use on **this** version is not independently certifiable)

Verified listing (this audit):

| Tool | Version | Role | Evidence |
|---|---|---|---|
| Cursor Grok 4.6 | 4.6 (as printed) | Language polish, formatting, consistency, reproducibility-prompt preparation | Living PDF Generative AI Statement; this revision log |
| ChatGPT | **not verified for this version** | Historical draft disclosure only | `AI_TOOL_VERSION_AUDIT.md`; stripped from living PDF |
| Claude | **not verified for this version** | Historical draft disclosure only | same |
| Google Antigravity | **not verified for this version** | Historical draft disclosure only | same |

---

## C15 — Publisher metadata

**Status:** NO_CHANGE  
**Metadata verdict:** KEEP_TEMPLATE_PLACEHOLDER

1. **Manuscript.** “Manuscript received Month date, 2026; revised Month date, 2026; accepted Month date, 2026.” Copyright / CC BY 4.0 closing block is present.
2. **Template evidence (repository, not a published article).** `_archive/ijiet_submission_audit/IJIET_TEMPLATE_REVIEW.md` records that `IJIET_template.doc` uses the same received/revised/accepted placeholder and that the draft correctly keeps `Month date, 2026`.
3. **Impact.** Format / publisher fields only.
4. **Risk if unchanged.** None for submission. Inventing dates/DOI/volume would be worse.
5. **Action.** Keep placeholders. Do not invent received/revised/accepted dates, DOI, volume, issue, or page numbers. Leave CC BY template text.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Filling real dates now would conflict with the template-review rule already on file.
10. **Confidence.** HIGH

---

## C16 — XES occupancy flag

**Status:** NO_CHANGE

1. **Manuscript.** Table 7: “XES3G5M very-sparse 114 L 0.184 0.173.” Prose N≈114. I = N<100; L = 100≤N<1000.
2. **Locks / changelog.** Phase 19 set the printed flag from I to L at mean N=114. `SCIENTIFIC_LOCKS.md` matches.
3. **Impact.** None.
4. **Risk if unchanged.** None; already L.
5. **Action.** No change. Do not reopen.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Changing L→I would contradict N=114.
10. **Confidence.** HIGH

---

## C17 — Junyi terminology

**Status:** NO_CHANGE

1. **Manuscript.** V.C: “the operational field is ucid (an exercise-level identifier, not a skill tag)… Junyi is therefore interpreted primarily as a granularity-and-estimability case rather than direct evidence about pedagogical KC sparsity.” Intro/Discussion use “exercise-level operational identifier (ucid).” Table 7: “learner-based operational identifier (ucid).”
2. **Code.** Junyi KC field in the pipeline is `ucid`. The shared KC-stratum machinery is used, but the paper states the semantic caveat (phase 20).
3. **Impact.** Already consistent. No scientific change needed.
4. **Risk if unchanged.** Residual generic “KC” in shared table headers is acceptable given V.C.
5. **Action.** No change.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Relabeling Junyi as a pedagogical skill log would conflict with V.C.
10. **Confidence.** HIGH

---

## C18 — FAR role

**Status:** NO_CHANGE

1. **Manuscript.** FAR is IV.F “Secondary decision-error probe,” “not RQ3,” Supplementary S3–S6. Contribution (ii) is ECE/Brier/reliability. Limitations: simulated probe, not classroom policy, not latent mastery.
2. **SI captions.** S3–S6: “Not a classroom trial.”
3. **Impact.** None.
4. **Risk if unchanged.** None if FAR stays demoted. Promoting it would recreate the old C2 problem.
5. **Action.** Do not promote FAR. No change.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Promoting FAR to RQ3 or Contribution (ii) would conflict with IV.F and the Intro “not RQ3” sentence.
10. **Confidence.** HIGH

---

## C19 — P1/P2/P3 boundary

**Status:** NO_CHANGE

1. **Manuscript.** “We do not train graph, contrastive, or self-supervised KT models.” “Graph and contrastive KT, and any path or distillation module, are left to later studies.” GKT and CL4KT: **0 hits** in the living blind PDF (literature-only citations may appear as numbered refs without those tokens). No scored GNN/SSL/GKT/CL4KT/path/distillation results.
2. **Code / changelog.** Phase 1/6/28: those models out of scope and not scored.
3. **Impact.** None.
4. **Risk if unchanged.** None.
5. **Action.** Do not add those models. No change.
6. **Files.** None.
7. **Retrain.** No — and must not be started for this revision.
8. **CPU recompute.** No.
9. **Conflict.** Scoring them would violate the P0 boundary the paper already states.
10. **Confidence.** HIGH

---

## C20 — XES3G5M padding fix

**Status:** NO_CHANGE

1. **Manuscript.** Table 1: 865 KCs; 6,413,353 valid KC-level rows; test 1,282,422. T-KT ECE series 0.1176 / 0.1129 / 0.1254. Regression n=829 unique KCs, masked weighted fit.
2. **Code.** `a2b/build_dataset.py` asserts `n_kcs==865` and `n_kc_minus1==0`. a2b learner-based fold-0 strata: 865 KCs, 0 padding. Historical 866 is documented as padding `kc_id=-1` and is not the living paper.
3. **Impact.** None. Do not reopen.
4. **Risk if unchanged.** None.
5. **Action.** No change. Do not rerun XES because older drafts said 866.
6. **Files.** None.
7. **Retrain.** No.
8. **CPU recompute.** No.
9. **Conflict.** Reverting to 866 would conflict with Table 1 and a2b.
10. **Confidence.** HIGH

---

## Summary table

| ID | Issue | Status | Evidence | Scientific impact | Rerun needed? | Recommended action | Confidence |
|---|---|---|---|---|---|---|---|
| C01 | Frequency-cut count (3 vs 2) | REQUIRED_FIX | Intro “Three alternative…”; Results “two alternative…”; S7 = Main + Alt-1 + Alt-2 | Wording only | No | Say “two alternative train-only frequency cut grids” | HIGH |
| C02 | Report k5/k10 limited cold-start | OPTIONAL | Table 7 already correct; CSV has registered `f<=5`/`f<=10` | None unless SI added | No | Keep Table 7; optional SI only; do not redefine very-sparse | HIGH |
| C03 | Reproducibility scope / title | NO_CHANGE | LEVEL A script + NOT RECOVERED; Track A does not lock ECE | Claim already scoped | No | Keep LEVEL A wording; title CONDITIONAL | HIGH |
| C04 | Baseline vs Roadmap | NO_CHANGE | S9: simpleKT **or** AKT; official SimpleKT Assist only; BKT fail documented | None | No | ACCEPT_CURRENT; no new models | HIGH |
| C05 | Heading “A. E. Secondary…” | NO_CHANGE | Word heading is “E. Secondary…”; PDF “A. E.” is Table 8+heading concat | None | No | Do not retitle | HIGH |
| C06 | “Competitive AUC” | RECOMMENDED_FIX | T-KT 0.6837 < DKT 0.6979 < official SimpleKT 0.7700 | Wording | No | Replace with sparse-pattern sentence | HIGH |
| C07 | Fig. 1 print quality | RECOMMENDED_FIX | Display 501.7×96.7 vs PNG 809×268 (aspect crush) | Format | No | MINOR_REFORMAT: restore aspect; no redraw | HIGH |
| C08 | Fig. 3 Junyi vs XES | NO_CHANGE | Caption: Assist sparse vs Junyi medium (empty sparse); XES in Table 5 | None | No | KEEP_ASSIST_JUNYI | HIGH |
| C09 | Table 6 Brier size | NO_CHANGE | Main extract + full S1; Junyi/XES needed for (ii) | None | No | KEEP_MAIN | HIGH |
| C10 | “Sparse mass” vs sparse bucket | RECOMMENDED_FIX | Table 8: share with `f<100`; bucket is `20<=f<100` | Wording | No | “low-frequency tail mass (`f_train<100`)” | HIGH |
| C11 | Regression 261/1326/829 | OPTIONAL | 4 Assist + 36 XES excluded; reasons traced | None | No | Optional SI reason table | HIGH |
| C12 | Temporal evidence vs claim | RECOMMENDED_FIX | Protocol claims both views; main Results learner-based; temporal CSVs exist | Reporting | No | ADD_SUPPLEMENTARY_TEMPORAL_TABLE from aligned exports | MEDIUM |
| C13 | “Success claims require…” | RECOMMENDED_FIX | III.E occupancy flags are descriptive | Wording | No | Use “substantive stratum-level interpretations…” | HIGH |
| C14 | AI disclosure completeness | AUTHOR_DECISION_REQUIRED | Living: Grok 4.6 only; older tools unversioned | Disclosure | No | Author confirms whether other tools were used on this version | MEDIUM |
| C15 | Received/revised/accepted dates | NO_CHANGE | Template placeholder `Month date, 2026`; CC BY present | None | No | KEEP_TEMPLATE_PLACEHOLDER | HIGH |
| C16 | XES very-sparse flag | NO_CHANGE | Table 7: N=114 **L** | None | No | Already correct | HIGH |
| C17 | Junyi ucid / KC wording | NO_CHANGE | V.C granularity-and-estimability; ucid ≠ skill tag | None | No | Already consistent | HIGH |
| C18 | FAR demotion | NO_CHANGE | IV.F / S3–S6; not RQ3; not (ii) | None | No | Do not promote | HIGH |
| C19 | P1/P2/P3 model boundary | NO_CHANGE | Graph/contrastive/SSL/path/distillation out of scope; not scored | None | No | Do not add models | HIGH |
| C20 | XES 865 / padding | NO_CHANGE | Table 1 865 / 6,413,353; a2b assert; 829 regression | None | No | Do not reopen 866 | HIGH |

---

## A. MUST FIX BEFORE SUBMISSION

- **C01.** Introduction: “Three alternative train-only frequency cuts” → “two alternative train-only frequency cut grids.”

## B. SHOULD FIX

- **C06.** Drop “competitive AUC.”
- **C07.** Restore Fig. 1 native aspect (do not redraw L1–L7 workflow).
- **C10.** Rename “sparse mass” → “low-frequency tail mass (`f_train<100`).”
- **C12.** Add a Supplementary temporal performance table from **alignment-verified** existing CSVs, or slightly narrow the “temporal views” clause if those files cannot be certified.
- **C13.** Replace “Success claims require…” with the occupancy-interpretation sentence.
- **C14.** Author confirmation on AI tools for this manuscript version (keep Grok 4.6; do not invent versions).

## C. OPTIONAL POLISH

- **C02.** SI-only registered k5/k10 (`f<=5` / `f<=10`), keeping Table 7 as feasibility.
- **C11.** Three-row exclusion-reason note in the regression supplement.
- **C03 (optional later).** Conda/Docker pin or one-log Track A demo — not required to keep the current LEVEL A claim.
- **C08 optional later.** Extra XES reliability row; not instead of Junyi.
- **C09 optional later.** Further-compact Table 6 only if page pressure appears; do not drop Junyi/XES evidence.

## D. DO NOT CHANGE

- **C03** current LEVEL A / frozen-artifact wording (do not claim LEVEL C).
- **C04** baseline set (ACCEPT_CURRENT).
- **C05** IV.E / IV.F headings.
- **C08** Fig. 3 Assist+Junyi pairing.
- **C09** main Brier extract (KEEP_MAIN).
- **C15** `Month date, 2026` placeholders and CC BY template text.
- **C16** XES very-sparse flag L at N=114.
- **C17** Junyi ucid / granularity wording.
- **C18** FAR as secondary probe.
- **C19** no GKT / CL4KT / GNN / SSL / path / distillation scoring.
- **C20** 865 KCs / padding-excluded series.
- Locked numbers: ASSISTments T-KT ECE 0.1136 / 0.2280; FAR 0.196 / 0.268; XES T-KT ECE 0.1176 / 0.1129 / 0.1254; official SimpleKT Assist AUC 0.7700±0.0013.
- Do not retrain, do not add models, do not redefine very-sparse as k5/k10.

---

## SUBMISSION_RECOMMENDATION

**READY_AFTER_REQUIRED_FIXES**

One internal inconsistency is real and should be corrected before the file is treated as final: C01 (three vs two alternative cut grids). After that wording fix, plus the Fig. 1 aspect restore if the camera-ready pass is being done now, the packet is otherwise a protocol-honest P0 revision: locks match the living PDF, FAR stays demoted, XES padding is closed, baselines are an accepted Roadmap instantiation, and reproducibility is LEVEL A rather than end-to-end.

Not `READY_TO_SUBMIT` until C01 is applied.  
Not `NOT_READY`: no lock error, no heading error, no occupancy-flag error, and no missing XES-padding repair.

---

*End of audit. Manuscript was not modified.*
