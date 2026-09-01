# IJIET final submission checklist

**Date:** 2026-08-31  
**Inspected files (frozen; this task did not overwrite them):**

- `output/main_ijiet_full.pdf` (named / editor; 8 pages; A4)
- `output/main_ijiet_blind.pdf` (double-blind review; 8 pages; A4)

**Word sources (not recompiled):** `source/main_ijiet_full.docx`, `source/main_ijiet_blind.docx`  
**Template authority:** official `IJIET_template.doc` (https://www.ijiet.org/files/IJIET_template.doc), plus prior format/visual audits.  
**Numeric authority:** `audit/FINAL_NUMERIC_AUDIT.md` (all Abstract–Conclusion numerals VERIFIED; NOT TRACEABLE: none).

**Verdict: READY TO SUBMIT** the two PDFs above. Residuals below are author/process or optional proof edits. None required a scientific rewrite or a new compile.

Legend: **PASS** = checklist item met. **PASS\*** = met with a documented residual that is not treated as blocking. **OPEN** = author/process action outside the PDF.

---

## Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Current IJIET template followed | **PASS** | Official Word template: A4, 1-col front matter then 2-col body (243.65 pt + 14.4 pt gutter), Times New Roman, `Abstract—` / `Keywords—`, Roman H1 / letter H2, `Table n.` / `Fig. n.`, IEEE numbered refs, empty header/footer (publisher inserts running head after acceptance). Built from that template, not IEEEtran. |
| Full research paper, not extended abstract | **PASS** | 8 pages; six sections (I–VI); Methods + Results + Discussion + Conclusion; 8 tables, 1 figure, 20 references; ~6,400 words including refs. |
| Title concise | **PASS** | “Sparse-Concept Calibration of Knowledge Tracing Models for Threshold-Based Educational Decisions.” Two-line title; topic + method + decision setting. Template 20 pt TNR centered (unbold, matching `IJIET_template.doc` rather than 2026 production PDFs). |
| Abstract formatted correctly | **PASS** | Style `Abstract`; label **Abstract—** bold; body italic; 9 pt; first-line indent as template. Content is a diagnostic summary, not a new architecture. |
| Keywords formatted correctly | **PASS** | Style `IndexTerms`; **Keywords—** bold; terms italic, lowercase: knowledge tracing, calibration, sparse concepts, learning analytics, educational decision support, mastery threshold. |
| Author block correct in full version | **PASS** | Five named authors; affiliation digits 1/2; emails with initials; `*` corresponding author + `*Corresponding author` line. PDF Author metadata lists all five names. |
| Blind version anonymized | **PASS** | “Anonymous Authors”; “Affiliations omitted for double-blind review.” No names, emails, Hung Yen, Military Science, or `K.-T.N.` in extracted text or PDF bytes. Contributions use Author 1–5. Acknowledgment: “Omitted for double-blind review.” Dataset names and anonymous.4open.science URL retained. |
| Figures legible | **PASS** | One embedded figure (page 3): 2×3 KC-count + log training-volume panels; 40° x-ticks; caption below. Raster at 1.6× is readable. Placed width ~490 pt (1-col span). |
| Tables legible | **PASS** | Eight tables. Wide tables (2, 4–8) sit in 1-col sections (no column-snaking). Table 5 FAR CIs use en-dash so intervals do not wrap on the comma. 7–8 pt TNR. **Residual:** leftover 1-col section padding above Tables 5–6 (IJIET-18); last page is short in both columns. Not a snaking/overflow failure. |
| All equations defined | **PASS** | ECE as template equation **(1)** with \(M=15\) equal-width bins. Brier, UNC, REL, RES defined in III.F. FAR, Miss, \(E[\mathrm{FAR}]\), Excess FAR, ΔFAR defined in III.H. Occupancy R/L/I defined in III.E. |
| All abbreviations defined | **PASS\*** | First-use expansions: KT, KC, AUC, ECE, FAR, BKT, IRT, DKT, GKT, CL4KT, ACC, RQ1–3, R/L/I, pyKT. “95% CI” follows an earlier “confidence intervals” sentence. **Residual:** “RCT” (instructional / classroom) is not expanded. Optional proof expansion: randomized controlled trial. |
| All tables cited | **PASS\*** | Tables 1 and 3–8 are cited by number in running text (Table 1 in Methods; Table 3–8 in Results/Discussion; “Tables 5–6”). **Residual:** Table 2 is introduced by the sentence immediately above its caption (“Recovered hyperparameters follow”) but that sentence does not contain the string “Table 2”. Not patched: PDFs are frozen. |
| All figures cited | **PASS** | `Fig. 1` cited in III.D before the caption; one figure only. |
| All references cited in text | **PASS** | In-text `[1]`–`[20]` (including ranges `[1]–[3]`). Every list item appears in the body. |
| No uncited references | **PASS** | Reference list is `[1]`…`[20]` with no extras. |
| Conflict of Interest present | **PASS** | Unnumbered heading; “The authors declare no conflict of interest.” |
| Author Contributions present | **PASS** | Initials + roles (full PDF); all authors approved. Blind PDF uses Author 1–5. |
| Ethics/data statement present or author-action flag | **PASS** | Ethical Statement: public de-identified secondary analysis; no new participants; no classroom intervention; no invented IRB. No `[AUTHOR ACTION REQUIRED]` placeholder. |
| Generative-AI disclosure present | **PASS** | Generative AI Statement: ChatGPT, Claude, Google Antigravity for language/formatting/consistency/reproducibility prompts; versions not recorded; not used to fabricate results; not a co-author. |
| Data/code availability present | **PASS** | Anonymous review URL `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`; public source datasets; public repo upon acceptance. |
| No publisher-created DOI/volume/page metadata fabricated | **PASS** | Empty header/footer (no journal running head, no `10.18178/ijiet`, no Vol./No., no production pagination). Manuscript dates remain template placeholders `Month date, 2026`. Reference DOIs are for cited works only. Copyright CC BY 4.0 line matches the template. |
| No overclaim of latent mastery | **PASS** | FAR uses observed next-response \(y\), “not latent mastery truth.” Limitations: “Next-response correctness is not latent mastery.” |
| No universal sparse-AUC claim | **PASS** | Explicit counterexample: XES3G5M sparse AUC > dense AUC (DKT, SimpleKT). “Lower training frequency does not universally degrade discrimination.” |
| No universal sparse-calibration claim | **PASS** | Junyi sparse empty; XES3G5M SimpleKT ECE essentially flat; “Calibration does not universally worsen”; Table 7/8 “not universal laws.” |
| Gate described as simulation | **PASS** | Abstract, III.H, Table 5 caption, Results C, Discussion, Conclusion: simulated gate / not a classroom trial or intervention. |
| GKT/CL4KT described as exploratory | **PASS** | Introduction: exploratory single-fold diagnostic. Results E: not SOTA, not a proposed method, **not an official CL4KT checkpoint**. Table 6: seed 42 only. |
| Four unique learner partitions stated correctly | **PASS** | Abstract, Introduction (iii), Methods B, Table 3/4/6 captions, Results, Discussion: five training runs / four unique partitions; seeds 2025 and 2026 share a split; not five independent folds. |
| All numerical claims traceable | **PASS** | `audit/FINAL_NUMERIC_AUDIT.md`: every Abstract / Introduction / Results / Discussion / Conclusion numeral VERIFIED to table / CSV / prediction export / script. Dual numbering (ECE \(N=415\) vs gate \(N=444\)) not mixed. Locked C2 ΔFAR CI `[0.006, 0.138]`. |
| PDF metadata anonymized in blind version | **PASS** | Blind: `Author` / `Creator` / `Producer` / dates empty. Title retained (non-identifying). Full PDF Author field is the five-author string. |
| No compilation warnings affecting publication | **PASS\*** | Word `ExportAsFixedFormat` produced both PDFs (8 pp, 8 tables, 1 figure) with no error log. **Residual layout (not a compiler error):** extra space above Tables 5–6 from leftover 1-col section marks; last-page columns do not fill. Known from IJIET-18. Not re-flowed (PDF freeze). |

---

## Residuals (do not block this freeze)

1. **Table 2** lacks a numbered in-text “Table 2” (adjacent introducing sentence only). Optional proof sentence if the editor requires it.
2. **RCT** not expanded on first use.
3. **Manuscript received/revised/accepted** dates are still `Month date, 2026` (template placeholders; do not invent calendar dates).
4. **ORCID** not present (IDs were never on file; do not invent).
5. **Generative-AI tool versions** were not recorded (already stated).
6. **Dual submission vs JEDM** (`paper/`) is a process decision, not a PDF field. IJIET forbids parallel consideration.
7. Layout leftovers in (1) and last-page balance. Do not recompile to chase them unless the editor asks — that reflow previously snaked tables.

---

## What this task did not do

- No scientific edits.
- **Did not overwrite** `output/main_ijiet_full.pdf` or `output/main_ijiet_blind.pdf`.
- Did not add journal running heads, DOIs, volume/issue, or fake received dates.

Page rasters used for visual confirmation: `audit/final_check_pages/full_p1.png`–`full_p8.png`, `blind_p1.png`.
