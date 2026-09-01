# IJIET submission — master changelog

Working rule: inspect → smallest defensible change → compile → inspect warnings → log → **stop and report** before the next task.

Original manuscripts (`paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`) are never overwritten.

---

## Task 1 — Workspace and source inspection (2026-08-31)

**Status:** complete. Stopped before any template rewrite.

### What changed

- Created `IJIET_SUBMISSION/{source,figures,tables,supplementary,audit,output}/`.
- Frozen content snapshot: `source/snapshots/main_ijiet_ieee_draft.tex` (copy of `ijiet/main_ijiet.tex`).
- Copied numeric punchline files into `tables/` from `analysis/four_partition/`.
- Recorded venue rules, ethics/AI policy, locked scientific facts, and dual-submission constraint.

### What did not change

- No edits to JEDM or `ijiet/` sources.
- No numerical results added, dropped, or recomputed.
- No new citations.
- No official-template manuscript yet (`.doc` download failed with HTTP 500).

### Compile

Skipped (no template-based source). Prior IEEE compile remains 5 pages (`ijiet/main_ijiet.log`).

### Residual risks

- Formatting authority is still missing (`IJIET_template.doc`).
- Dual submission vs JEDM is unresolved (policy, not a TeX issue).
- Figure binary not yet copied into this package.

### Next

Task 2: acquire official template (or document a published-PDF proxy with explicit residual uncertainty). No prose rewrite until the format checklist exists.

---

## Task 2 — Official IJIET Word manuscript (2026-08-31)

**Status:** complete. Word files written; originals `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, and `ijiet/*.tex` not overwritten.

### What changed

- Downloaded the live official template `IJIET_template.doc` (OLE compound file, A4, Title 20 pt, Heading 1 = I./II./III.). Stored at `IJIET_SUBMISSION/audit/IJIET_template.doc`.
- Filled that template (not an IEEE reconstruction) via Word COM: `IJIET_SUBMISSION/source/fill_ijiet_from_template.py`.
- Wrote:
  - `ijiet/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx`
  - `ijiet/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.doc`
  - copy in `IJIET_SUBMISSION/output/`
- Embedded Fig. 1 from `paper/figures/figure2_bucket_distribution.pdf` (rasterized PNG).
- Numbers copied from the validated IJIET draft / four-partition tables. No recomputation.

### Compile / inspect

Word statistics: 4 pages, 3242 words, 6 tables, 1 figure, 20 references. Heading list I–V matches the official template (Introduction; Literature Review; Materials and Methods; Result and Discussion; Conclusion). Sample template text is gone. Unicode ± and τ are present (U+00B1, U+03C4).

### Residual risks

- Dual submission vs JEDM is still unresolved.
- Length is short vs typical IJIET articles (8–12 pages); content was not padded.
- Manuscript received/revised/accepted dates remain placeholders.
- Official site sometimes returns HTTP 500 for the template URL; a local copy is now in `audit/`.

---

## Task IJIET-01 — Format audit only (2026-08-31)

**Status:** complete. **No manuscript source edited.**

### What changed

- Wrote `IJIET_SUBMISSION/audit/IJIET_FORMAT_AUDIT.md`.
- Measured official `IJIET_template.doc` vs the filled Word manuscript with Word COM (`format_measure.txt`, `format_measure2.txt`).

### Result

- PASS 18 / MINOR FIX 8 / MAJOR FIX 2 / NOT VERIFIABLE 0.
- Journal running header and production page numbers are **publisher-owned** (empty in the official template). Do not add them.
- Next format pass should start with AI disclosure and table column-width overflow.

---

## Task IJIET-02 — Clean IJIET branch (2026-08-31)

**Status:** complete. Originals under `ijiet/` and `paper/` not modified.

### What changed

- Copied manuscript, official template, figure, and bibliography into `IJIET_SUBMISSION/source/`.
- On the copy only: removed received/revised/accepted dates; kept headers/footers empty (no journal running head, DOI, production pages).
- Compiled `IJIET_SUBMISSION/output/main_ijiet_step02.pdf` (4 pages, 3229 words).
- Log: `audit/CHANGELOG_IJIET_02.md`.

### Unresolved

IJIET-01 MAJOR/MINOR typesetting items (AI disclosure, table overflow, title bold, etc.) were not applied in this step.

---

## Task IJIET-03 — Front matter (2026-08-31)

**Status:** complete. Originals and step02 snapshot not modified.

### What changed (working copy only)

- Title set to *Sparse-Concept Calibration of Knowledge Tracing Models for Threshold-Based Educational Decisions* (20 pt TNR, not bold). “Mastery and Remediation Gates” dropped because the gate is next-response correctness, not latent mastery.
- Authors/affiliations/emails/`*Corresponding author` formatted to the official IJIET template (superscripts including `*`).
- Keywords label is `Keywords—` (not IEEE Index Terms); six terms as specified.
- Compiled `output/main_ijiet_step03.pdf`. Master file not anonymized.

### Unresolved

IJIET-01 MAJOR items (AI disclosure, table width) and remaining MINOR body/typesetting items.

---

## Task IJIET-04 — Abstract (2026-08-31)

**Status:** complete. Results section not edited.

### What changed

- One-paragraph IJIET Abstract with bounded claim, SimpleKT ECE 0.114→0.228 (Limited, N≈415), false-advance language, simulation disclaimer; GKT dropped from the Abstract only.
- Compiled `output/main_ijiet_step04.pdf`.

---

## Task IJIET-05 — Introduction (2026-08-31)

**Status:** complete. Results not edited.

### What changed

- Section I rewritten for IJIET: AUC → *p* → calibration → threshold decisions → sparse-KC risk.
- FAR named; *y* = next-response correctness, not latent mastery. RQ1–RQ3 retained. Conservative contributions.
- Compiled `output/main_ijiet_step05.pdf`.

---

## Task IJIET-06 — Literature Review (2026-08-31)

**Status:** complete. Results not edited. No new citations.

### What changed

- Section II restructured into IJIET Heading 2 A–D: benchmark KT; graph/self-supervised KT; sparse-data vs cold-start; calibration and decision support, ending in an explicit research gap.
- Reference audit in `audit/REFERENCE_AUDIT_RELATED_WORK.md`. Corrected pyKT conference number (`[5]`) and CL4KT last author (`[9]`).
- Compiled `output/main_ijiet_step06.pdf`.

---

## Task IJIET-07 — Methods completeness (2026-08-31)

**Status:** complete. Results tables/numbers not edited. Table 1 cells not changed.

### What changed

- Section III rewritten as Heading 2 A–H: datasets (post-processing + XES3G5M kc_level audit); splits and seeds; model settings; train-only strata; reliability flags; calibration; difficulty coupling; simulated gate.
- XES3G5M 866 KCs / 7.95M rows **verified** as kc_level flattening plus retained `-1` padding; not silently retabulated. See `audit/XES3G5M_COUNT_AUDIT.md`.
- Recovered hyperparameters in an unnumbered Methods table; missing commit marked NOT RECOVERED. Copy: `supplementary/TABLE_S1_MODEL_SETTINGS.md`.
- Compiled `output/main_ijiet_step07.pdf`.

---

## Task IJIET-08 — Threshold decision metrics (2026-08-31)

**Status:** complete. ECE/AUC numbers not edited. Gate point estimates kept at published 3 decimals; denominators and FAR CIs recovered from prediction exports.

### What changed

- FM renamed FAR throughout. Methods now define FAR, Miss, E[FAR], Excess FAR, and ΔFAR, and state that FAR is not latent mastery.
- Table 4 and Table 5 include \(N\), \(N_{\mathrm{adv}}\), \(N_{\mathrm{inc}}\). Seed-42 ΔFAR CI remains [0.006, 0.138].
- Compiled `output/main_ijiet_step08.pdf`.

---

## Task IJIET-09 — Figures and tables (2026-08-31)

**Status:** complete. Table 2 AUC/ACC and Table 3 ECE cells not edited.

### What changed

- Fig. 1 caption no longer claims interaction volume from KC counts. A second panel uses verified fold-0 `train_freq` sums. Figure spans the IJIET text width; caption is below the plot.
- Table 1: post-processing cohort note. Table 3: N = four-partition mean. Table 4: N_advance, N_incorrect, Excess FAR, FAR 95% CIs. Table 5: 5/5 training runs across four unique partitions (not independent seeds). Table 6: empirical on these three datasets, not universal laws.
- Compiled `output/main_ijiet_step09.pdf` (7 pages).

---

## Task IJIET-10 — Explanatory analysis (2026-08-31)

**Status:** complete. No new experiments; Table 2/3 rates untouched; old appendices not restored.

### What changed

- Results subsection “Explanatory Analysis of Dataset-Dependent Calibration” (~0.5–1 IJIET page): sparse mass, test support, frequency–difficulty, item support, learner exposure, curriculum-position proxy; between-KC regression vs within-KC sparsification.
- Compact Table 7 (five rows). ASSISTments observational ECE gradient is not reproduced by reducing training rows for the same originally dense KC.
- Compiled `output/main_ijiet_step10.pdf` (8 pages).

---

## Task IJIET-11 — Results consistency (2026-08-31)

**Status:** complete. Table cells not edited. Claim trace in `CLAIM_TO_RESULT_MATRIX.md`.

### What changed

- Section IV reordered to A discrimination, B calibration, C threshold error, D explanatory analysis, E exploratory GKT/CL4KT.
- Sparse AUC ≠ calibration; Junyi sparse = empty; XES3G5M = counter-pattern; SimpleKT five-run wording uses four unique partitions.
- Compiled `output/main_ijiet_step11.pdf`.

---

## Task IJIET-12 — Discussion and Conclusion (2026-08-31)

**Status:** complete. Table cells and Fig. 1 not edited.

### What changed

- Section IV retitled **RESULT** (A–E unchanged). New **V. DISCUSSION** (A findings, B practical implications, C measured dataset differences with labeled hypotheses, D limitations). **VI. CONCLUSION** is short and avoids “proves/causes/always/universally”.
- Compiled `output/main_ijiet_step12.pdf` (8 pages).

---

## Task IJIET-13 — Required end matter (2026-08-31)

**Status:** complete. No invented IRB; AI versions left as placeholders.

### What changed

- Added Ethical Statement, Data and Code Availability, and Generative AI Statement. Author Contributions mapped to evidenced CRediT-like roles. Acknowledgment is institutional support only.
- Compiled `output/main_ijiet_step13.pdf` (8 pages).

---

## Task IJIET-14 — Reference audit (2026-08-31)

**Status:** complete. In-text `[1]`–`[20]` unchanged. Yan et al. kept as arXiv.

### What changed

- Every numbered reference audited (authors, venue, year, pages/DOI). pyKT = 36th NeurIPS (2022); XES3G5M = 37th (2023). Bhattacharjee DOI uses `_30`. Dataset URLs retained. IJIET `doi:` punctuation applied where verified.
- Audit table: `audit/REFERENCE_AUDIT_FULL.csv`. Compiled `output/main_ijiet_step14.pdf` (8 pages).

---

## Task IJIET-15 — Double-blind review version (2026-08-31)

**Status:** complete. Two PDFs; scientific body, tables, and Fig. 1 unchanged except anonymized front/end matter.

### What changed

- Named build: `output/main_ijiet_full.pdf` (authors, affiliations, emails, corresponding author).
- Blind build: `output/main_ijiet_blind.pdf` (Anonymous Authors; affiliations/emails/corresponding author removed; Author 1–5 contributions; acknowledgment omitted).
- Artifact URL remains `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/` in both (already anonymous; owner GitHub not used).
- Blind PDF `/Author` is null; Creator/Producer cleared. Dataset names and `[1]`–`[20]` retained.
- Audit: `audit/DOUBLE_BLIND_CHECK.md`.

---

## Task IJIET-16 — Visual template QA (2026-08-31)

**Status:** complete. HIGH/MEDIUM layout issues fixed; scientific cells unchanged.

### What changed

- Compared `main_ijiet_full.pdf` to `IJIET_template.doc` and 2026 papers V16N1-2484 and V16N8-2667.
- Fixed empty right column on p.3, overlapping Fig. 1 ticks, Table 4 CI wrapping, heading consistency, `*` superscript, manuscript-date placeholder, Abstract/Keywords mixed style, Table 7 caption, URL hyphenation.
- Recompiled `output/main_ijiet_full.pdf` and `output/main_ijiet_blind.pdf` (8 pages).
- Audit: `audit/VISUAL_QA.md`.

---

## Task IJIET-17 — Fix remaining QA items (2026-08-31)

**Status:** complete. No invented ORCID, IRB number, calendar dates, or experimental cells.

### What changed

- Settings listing numbered **Table 2**; former Tables 2–7 became **Tables 3–8** in captions and in-text.
- ECE moved to template `equation` style as **(1)**; formula unchanged.
- Table 5/6 captions shortened (FAR definitions already in III.H).
- Ethical Statement: public de-identified secondary analysis; placeholder removed; **no** invented “IRB not required”.
- Generative AI: tool names kept; `[version to be confirmed]` removed (“versions were not recorded”).
- Blind PDF: empty affiliation/email/corresponding-author/date lines deleted.
- Recompiled named and blind PDFs (9 pages).

**Not changed (need author/process, not typesetting):** ORCID (none on file); manuscript received dates; dual-submission vs JEDM.

---

## Task IJIET-18 — Close empty space before spanning tables (2026-08-31)

**Status:** complete for blank-page / snaking-table failures. Residual 1-col padding before Tables 5–6 is leftover Word section spacing.

### What changed

- Wide tables (2, 4–8) and Fig. 1 sit in 1-col blocks that include the heading/intro, so Word no longer leaves a nearly empty 2-col page before the table.
- Tables no longer snake across newspaper columns. Table 8 is one full-width block.
- Restored **D. Train-only frequency strata** (section breaks had produced `A. D.`).
- Table 4 starts complete on the next page (no orphan header).
- Recompiled named and blind PDFs (8 pages). ECE 0.1136 / 0.2280 and FAR 0.196 / 0.268 unchanged.

Audit: `audit/CHANGELOG_IJIET_18.md`.

---

## Task IJIET-19 — Final scientific integrity audit (2026-08-31)

**Status:** complete. Prompt labeled IJIET-17 (numeric); format IJIET-17 already closed.

### What changed

- `audit/FINAL_NUMERIC_AUDIT.md`: every numeral in Abstract, Introduction, Results, Discussion, Conclusion traced to table / CSV / prediction export / analysis script.
- Introduction (iii): “five-seed check” aligned to **five training runs / four unique learner partitions**. No table cells changed.
- Recompiled `output/main_ijiet_full.pdf` and `output/main_ijiet_blind.pdf`.

### Verdict

All audited claims **VERIFIED** after that wording patch. **NOT TRACEABLE: none.** Locked C2 ΔFAR CI `[0.006, 0.138]` retained. Dual numbering (ECE \(N=415\) vs gate \(N=444\)) consistent.

---

## Task IJIET-20 — Final submission check (2026-08-31)

**Status:** complete. User prompt labeled IJIET-18 (final check); layout IJIET-18 already closed.

### What changed

- Wrote `audit/IJIET_FINAL_CHECKLIST.md` and `audit/IJIET_SUBMISSION_SUMMARY.md`.
- Inspected frozen `output/main_ijiet_full.pdf` and `output/main_ijiet_blind.pdf` (8 pages each). **PDFs were not overwritten.**

### Verdict

**READY TO SUBMIT.** Checklist items PASS (two PASS\* residuals: Table 2 numbered in-text pointer; “RCT” expansion). Process leftovers: JEDM dual-submission, placeholder manuscript dates, no ORCID.

---

## Task IJIET-21 — Update manuscript vs latest KT (2026-08-31)

**Status:** complete. User asked to update the paper after the contribution-vs-latest review.

### What changed (no experimental cells)

- §II.A: UKT (AAAI 2025) as architecture / population-ranking, not a frequency-stratum audit. New **[21]**.
- §II.D: Mitton et al. (PMLR 339, 2026) selective prediction as complementary to a locked-τ FAR. New **[22]**.
- Methods C: numbered in-text “Table 2 reports recovered training settings”.
- Methods H: expand RCT on first use.
- Recompiled named and blind PDFs (still 8 pages). ECE 0.1136 / 0.2280 and FAR 0.196 / 0.268 unchanged.

### What did not change

- Table numeric cells, Fig. 1, locked C2 CI, GKT/CL4KT protocol.

---



