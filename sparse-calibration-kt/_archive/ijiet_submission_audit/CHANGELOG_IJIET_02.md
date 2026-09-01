# IJIET-02 — Clean submission branch

**Date:** 2026-08-31  
**Scope:** copy sources into `IJIET_SUBMISSION/source/`, strip publisher-owned metadata on the **copy only**, compile PDF.  
**Not in scope:** IJIET-01 MINOR/MAJOR typesetting fixes (table width, AI disclosure, title bold, equation style, etc.).

Originals **not modified:** `ijiet/*`, `paper/*`, `REV_REVIEWER_CALIBRATION_v1/*`.

---

## Source files copied

| From | To |
|------|-----|
| `ijiet/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx` | `source/main_ijiet_step02.docx` (then cleaned) |
| same `.doc` | `source/main_ijiet_step02.doc` (saved after clean) |
| `audit/IJIET_template.doc` | `source/template/IJIET_template.doc` |
| `paper/references.bib` | `source/bibliography/references.bib` (350 lines) |
| `IJIET_SUBMISSION/figures/figure2_bucket_distribution.png` | `source/figures/figure2_bucket_distribution.png` |
| `paper/figures/figure2_bucket_distribution.pdf` | `source/figures/figure2_bucket_distribution.pdf` |

Working manuscript (edit this file, not `ijiet/`):  
`IJIET_SUBMISSION/source/main_ijiet_step02.docx`

Frozen IEEE snapshot from Task 1 remains at `source/snapshots/` and was **not** used as the IJIET layout.

---

## Style / template files used

- **Authority:** official IJIET Word template (`IJIET_template.doc`, A4, 1-col front matter + 2-col body, Heading 1 = I./II./III., styles `Abstract`, `IndexTerms`, `Text`, `Affiliation`, `Table Title`, `figure caption`, `Reference Head`, `References`).
- The working `.docx` already inherits those styles (filled from the template in the previous Word pass).
- **Not used:** `IEEEtran.cls`, `ijiet/main_ijiet.tex`.

---

## Publisher metadata removed or confirmed absent

Removed from the **working copy** (one Affiliation paragraph):

- `Manuscript received Month date, 2026; revised Month date, 2026; accepted Month date, 2026`

Confirmed absent (all four sections; also after clean):

- Journal running header (`INTERNATIONAL JOURNAL…` / `International Journal of Information…`)
- IJIET article DOI (`10.18178`)
- Volume/issue imitation (`Vol. 16`)
- Header/footer page numbers (headers and footers empty; PAGE fields cleared)

**Left in place (manuscript content, not production metadata):**

- Title, authors, affiliations, corresponding-author line
- Abstract, keywords, I.–V. body, tables, Fig. 1, references `[1]`–`[20]`
- Template copyright / CC BY line
- Bibliographic `vol.` / `no.` inside cited works (not IJIET issue metadata)

---

## Compile status

| Output | Result |
|--------|--------|
| `IJIET_SUBMISSION/output/main_ijiet_step02.pdf` | **OK** — Word `ExportAsFixedFormat` print-quality PDF, 347 879 bytes |
| Word stats after clean | **4 pages**, **3229 words** (was 3242; drop is the removed date line), 6 tables, 1 figure |
| Verify | Title, authors, Conflict of Interest, Fig. 1, Table 3, `*Corresponding author` present; `Manuscript received` / `10.18178` / journal header absent |

---

## Warnings still unresolved (from IJIET-01; not fixed in this step)

1. **MAJOR** — No generative-AI disclosure (ethics §6.3).  
2. **MAJOR** — Tables ~283 pt wide vs 243.65 pt column (overflow).  
3. **MINOR** — Title is 20 pt **bold**; template title is 20 pt roman.  
4. **MINOR** — Abstract/Keywords whole-paragraph bold+italic vs mixed label/body.  
5. **MINOR** — ECE is inline, not template `equation` `(1)`.  
6. **MINOR** — Corresponding-author `*` not superscripted.  
7. **MINOR** — No dedicated public-dataset / no-new-human-subjects ethics sentence.  
8. **MINOR** — Table header cells styled `Figure Caption`; journal/book titles in refs likely not italic.  
9. Leftover empty 1-column section break from the template sample.  
10. Dual-submission vs JEDM (policy, not typesetting).
