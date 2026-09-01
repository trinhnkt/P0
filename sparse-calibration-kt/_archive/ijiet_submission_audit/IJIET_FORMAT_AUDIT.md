# IJIET-01 — Format audit (no manuscript edits)

**Date:** 2026-08-31  
**Current manuscript (audited):**  
`ijiet/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx`  
(same content as the `.doc` sibling)

**Formatting authority (not IEEE conference class):**  
- Official template: `IJIET_SUBMISSION/audit/IJIET_template.doc`  
  downloaded from https://www.ijiet.org/files/IJIET_template.doc  
- Author guide: https://www.ijiet.org/list-14-1.html  
- FAQ (template is mandatory before submission): https://www.ijiet.org/list-22-1.html  
- Ethics / generative-AI: https://www.ijiet.org/list-77-1.html  

**Out of scope for this audit as “current IJIET manuscript”:**  
`ijiet/main_ijiet.tex` uses `IEEEtran` journal two-column. That file is **not** the official IJIET template and was not scored here.

**Measurement method:** Microsoft Word 16 COM read-only dump of page setup, styles, fonts, indents, headers/footers, table widths, and inline picture size (`audit/format_measure.txt`, `audit/format_measure2.txt`). Units below are Word points unless noted (1 in = 72 pt).

---

## Header and page numbers — authors vs publisher

The official template has **empty headers and empty footers** in all four sections (`HEADER: []`, `FOOTER: []`). It does **not** contain:

- `INTERNATIONAL JOURNAL OF INFORMATION AND EDUCATION TECHNOLOGY`
- volume / issue / year running head
- production page numbers (e.g. 2068)
- DOI `10.18178/ijiet.…`

Those elements appear on **already published** PDFs (production). They are **not** author-generated in the current official template.

**Required action: do not add that journal header or production page numbers.** Leave header/footer empty as in `IJIET_template.doc`. The publisher inserts them after acceptance.

Placeholders that **are** in the template (authors may leave them generic):

- `Manuscript received …; revised …; accepted …`
- Copyright / CC BY line (template year 2026)

Placeholders that **must not** be invented by authors:

- final received/revised/accepted/published calendar dates assigned by the journal
- volume, issue, article number, page range
- DOI

---

## Double-blind vs named template

Ethics (list-77-1) states a **double-blind** review process. FAQ says **blind peer review**. The **official template includes full names, numbered affiliations, emails, and `*Corresponding author`**.

The current manuscript follows the **template** (named). This audit does **not** treat named authors as a format failure. Do not strip names unless OJS later asks for a separate anonymized file.

---

## Audit table

| ID | Element | Current manuscript | Current IJIET requirement | Status | Required action |
|----|---------|--------------------|---------------------------|--------|-----------------|
| 1 | Page size | A4 (`PaperSize=7`), 595.35 × 841.95 pt (210 × 297 mm) | Official template: A4, 595.35 × 841.95 pt. Not US Letter / IEEE `IEEEtran` letter. | PASS | None. |
| 2 | Margins | T/B 50.45 pt (17.8 mm); L/R 46.8 pt (16.5 mm); gutter 0; header/footer distance 21.55 pt | Identical values on all template sections. | PASS | None. |
| 3 | Column number and width | Sec. 1: 1 col, 501.75 pt. Sec. 2 & 4: 2 cols, **243.65 + 243.65 pt**, spacing **14.4 pt**. Sec. 3: leftover 1-col 501.75 pt (empty template break). | Template: 1-col front matter, then 2-col body with 243.65 pt columns and 14.4 pt gutter. Wide tables use a 1-col section. | PASS | Keep this geometry. Do not convert to IEEE letter two-column. Unused sec. 3 is a later cleanup, not a column-spec failure. |
| 4 | Font families | Body, title, headings, captions, refs measured as Times New Roman | Template paragraphs use Times New Roman (title 20 pt, authors 11 pt, affiliation 9 pt, body 10 pt, abstract/keywords 9 pt, captions/refs 8 pt). | PASS | None. Do not switch to Calibri/Cambria/IEEE default mix. |
| 5 | Title formatting | Style `Text`; 20 pt TNR; **bold**; centered; line 12.6 / rule Multiple; space-after 20 pt | Template “Paper Title”: style `Text`; **20 pt TNR; not bold** (`bold=0`); centered; same spacing. Production PDFs may look heavier; template is authority. | MINOR FIX | Remove title bold so it matches the official 20 pt roman title. Keep 20 pt, centered, TNR. |
| 6 | Author formatting | Style `Style Author + (Asian) MS Mincho`; 11 pt TNR; centered; names + affiliation digits; digits 1,1,1,2,1 are superscript; **`*` is not superscript** | Template: same style/size/alignment; affiliation numbers **and** `*` as superscripts (`Firstname A. Lastname¹,*`). | MINOR FIX | Superscript both corresponding-author asterisks (after Nguyen and in `1,*`). |
| 7 | Affiliation formatting | Two numbered lines, 9 pt TNR, centered, style `Affiliation`; then Email line with initials in parentheses | Template: `1 Department, Faculty, University, City, Country`; Email: `name@host (F.A.L.); …` | PASS | Format matches. Optional later content polish (Department/Faculty) is not a style miss. |
| 8 | Corresponding-author formatting | Name marked `1,*`; separate line `*Corresponding author` (9 pt, Affiliation style) | Template: `*` on the author name (superscript) **and** a following line `*Corresponding author`. | MINOR FIX | Same as ID 6: superscript `*`. Keep the dedicated line. |
| 9 | Abstract style | Style `Abstract`; 9 pt; **entire paragraph bold and italic**; first-line indent 10.1 pt; justified; label `Abstract—` | Template: style `Abstract`; 9 pt; **mixed** (`bold=-1`, `italic=9999999` = label bold, body italic); indent 10.1 pt; `Abstract—` + summary. | MINOR FIX | Restore template character style: bold `Abstract—` only; remainder italic, not bold. |
| 10 | Keywords style | Style `IndexTerms`; 9 pt; entire paragraph bold+italic; indent 10.1 pt; `Keywords—` + lowercase terms | Template: style `IndexTerms`; 9 pt; mixed bold label + italic terms; `Keywords—`. | MINOR FIX | Same as abstract: bold `Keywords—` only; terms italic, not bold. |
| 11 | Section numbering | Heading 1 auto-list **I. II. III. IV. V.**; text sentence case (`Introduction`, `Literature Review`, `Materials and Methods`, `Result and Discussion`, `Conclusion`); 10 pt TNR; **not bold**; centered; space-before 12 / after 4 | Template Heading 1: list `I.` …; sentence case (not IEEE `I. INTRODUCTION` all-caps); 10 pt; bold=0; centered. | PASS | Do not restyle as IEEE all-caps headings. |
| 12 | Subsection numbering | Heading 2 auto-list **A. B. C.**; 10 pt TNR italic; justified; space-before 6 / after 3 | Template Heading 2: `A.` italic 10 pt, alignment 3 (justified). | PASS | None. |
| 13 | Paragraph indentation | Body style `Text`: first-line indent **10.1 pt**; left indent 0 | Template body: first-line indent 10.1 pt. | PASS | None. |
| 14 | Line spacing | Body: LineSpacing **12.6**, rule **5 (Multiple)** ≈ 1.05 line; space before/after 0 | Template body: identical 12.6 / Multiple. | PASS | Do not switch to IEEE single-spaced 10 pt Exact or Word 1.15 default. |
| 15 | Equation formatting and numbering | ECE written **inline** in a `Text` paragraph: `ECE = Σ_m (n_m / N) \|acc_m − conf_m\|`. No `equation` style, no right-tab `(1)`. | Template uses style `equation`, centered content, numbered `(1)` at the right of the column. | MINOR FIX | Move the ECE (and ΔFM if displayed) into the template `equation` style with sequential `(1)`, `(2)`. Do not invent new numerical results. |
| 16 | Table titles | Captions: `Table 1.` … `Table 6.`; style `Table Title`; 8 pt TNR; centered. **Table 1 total width ≈ 283 pt vs column 243.65 pt (overflow).** Header cells inherited style `Figure Caption`. | Captions: `Table n. Title` above the table; 8 pt; centered. Tables in two-column flow must fit **243.65 pt**, or sit in a 1-col section (template sec. 3). | MAJOR FIX | Shrink or wrap tables to ≤ 243.65 pt, **or** place oversized tables in a 1-column section like the template. Reset header cells to table styles (`table col head` / `table copy`), not Figure Caption. |
| 17 | Figure captions | `Fig. 1. Train-only KC-frequency strata. …`; style `figure caption`; 8 pt; centered (`align=1`) | Template: `Fig. 1. …`; style `figure caption`; 8 pt; centered. | PASS | None. |
| 18 | Figure width / resolution | One inline picture: **240 pt × 72 pt** (fits 243.65 pt column). Source PNG 2146×638 px → ≈ **644 ppi** at 240 pt width. File metadata 96 dpi (Windows default). | Figures embedded in the file (author guide). Stay inside the column unless a 1-col span is used. Print-quality typically ≥ 300 ppi at placed size. | PASS | None required for size/ppi. Optional: embed with 300 dpi metadata; do not upscale pixels. |
| 19 | Citation style | Numbered in-text `[1]`, `[4], [5]`, `[1]–[3]` | Template / published articles: IEEE numbered `[n]`. | PASS | None. Do not convert to APA/author–year (JEDM). |
| 20 | Reference style | Style `References`; 8 pt TNR; list `[1]`…`[20]`; hanging indent −18 pt; IEEE-like punctuation | Template: style `References`; `[n]`; 8 pt; hanging −18 pt; journal/book titles typically italic in the sample. | MINOR FIX | Italicize journal and book titles as in the template samples. Do not add uncited sources. |
| 21 | Conflict of Interest | Unnumbered `Reference Head`, centered 10 pt: “The authors declare no conflict of interest.” | Template back-matter heading `Conflict of Interest` (not Heading 1). | PASS | None. |
| 22 | Author Contributions | Present; initials + roles; all authors approved | Template heading `Author Contributions`; ICMJE-style contribution text (ethics). | PASS | None. |
| 23 | Acknowledgment | Present (code availability; public logs; not a classroom trial). No Funding heading (no grant). | Template has `Acknowledgment` and optional `Funding`. Omit Funding if none. | PASS | None. |
| 24 | Ethics / data statement | Acknowledgment notes de-identified **public** logs (ASSISTments 2012, Junyi, XES3G5M) and “not a classroom trial.” No IRB / GDPR / FERPA sentence. | Ethics page: human-participant studies need consent/IRB; EdTech logs must be anonymized or permissioned; state data-protection compliance when applicable. Public de-identified benchmarks are not a new classroom trial. | MINOR FIX | Add a short dedicated sentence: public de-identified datasets; no new human-subjects protocol; not an interventional classroom study. Do not invent an IRB number. |
| 25 | Generative-AI disclosure | **Absent** (no ChatGPT/Grammarly/tool/version/use). | Ethics §6.3: **mandatory** disclosure in methods or acknowledgments if AI was used (tool, version, how). AI cannot be a co-author. Undisclosed LLM manuscript text is banned. | MAJOR FIX | Add a factual disclosure matching actual use (e.g. language/formatting assistance vs none). Do not claim a tool that was not used. Do not list AI as an author. |
| 26 | Anonymous / double-blind | Named authors, emails, affiliations (visible) | Official **template is named**. Ethics/FAQ describe blind/double-blind review (likely implemented by the journal). | PASS | Keep names as in the template unless OJS requests a separate anonymized PDF. |
| 27 | Journal header / page numbering | Headers and footers **empty** (no journal title, no page numbers) | Official template: empty header/footer. Published PDFs add running head + page numbers **in production**. | PASS | **Do not** insert `INTERNATIONAL JOURNAL OF INFORMATION AND EDUCATION TECHNOLOGY` or production page numbers. Publisher-owned. |
| 28 | Metadata authors must not generate | No DOI, no volume/issue, no article ID, no production pages. Received/revised/accepted still `Month date, 2026` placeholders. | Authors must not invent DOI `10.18178/ijiet.…`, Vol./No., or final pagination. Template allows placeholder manuscript dates. | PASS | Leave DOI/volume/pages to the publisher. Do not fill fake calendar dates. |

---

## Totals

| Status | Count | IDs |
|--------|------:|-----|
| **PASS** | **18** | 1, 2, 3, 4, 7, 11, 12, 13, 14, 17, 18, 19, 21, 22, 23, 26, 27, 28 |
| **MINOR FIX** | **8** | 5, 6, 8, 9, 10, 15, 20, 24 |
| **MAJOR FIX** | **2** | 16, 25 |
| **NOT VERIFIABLE** | **0** | — |

---

## First 10 corrections (priority order)

Do **not** apply these in this task. Listed for the next format-fix pass.

1. **(MAJOR, ID 25)** Add a generative-AI disclosure in Acknowledgment or Methods: tool, version, and role — or an explicit “no generative AI” statement if that is true of the scientific text.  
2. **(MAJOR, ID 16)** Fit all tables to the **243.65 pt** column, or move wide tables into a 1-column section as in the official template.  
3. **(MINOR, ID 9–10)** Restore Abstract/Keywords mixed formatting (bold label `Abstract—` / `Keywords—`; italic body; not whole-paragraph bold).  
4. **(MINOR, ID 5)** Un-bold the 20 pt title to match `IJIET_template.doc`.  
5. **(MINOR, ID 15)** Place ECE (and ΔFM if displayed) in template `equation` style with `(1)`, `(2)`.  
6. **(MINOR, ID 6 / 8)** Superscript corresponding-author asterisks.  
7. **(MINOR, ID 24)** Add a dedicated public-dataset / no-new-human-subjects sentence (no invented IRB).  
8. **(MINOR, ID 16 follow-on)** Restyle table header cells away from `Figure Caption`.  
9. **(MINOR, ID 20)** Italicize journal and book titles in References, matching template samples.  
10. **(MINOR, ID 3 leftover)** Remove the empty trailing paragraph and unused 1-column section break inherited from the template sample.

**Do not “fix” ID 27 by adding a journal running header.** That would be a regression.

---

## Notes (not scored as extra IDs)

- Length (~4 pages, ~3242 words) is a **content/venue** issue (FAQ: insufficient content may be rejected), not a template field in the 28-item list.  
- Dual submission vs the JEDM manuscript is an **ethics** issue, already logged; it is not a typesetting miss.  
- Scientific numbers were not re-checked in this format-only task.
