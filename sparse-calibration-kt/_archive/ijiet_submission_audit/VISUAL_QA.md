# Visual QA (IJIET-16)

**Date:** 2026-08-31
**Manuscript inspected:** `output/main_ijiet_full.pdf` (named camera-ready; 8 pages after fix).
**Blind sibling:** `output/main_ijiet_blind.pdf` (same layout minus identifying front/end matter).
**Comparators:** official `source/template/IJIET_template.doc`; IJIET 2026 papers [V16N1-2484](https://www.ijiet.org/vol16/IJIET-V16N1-2484.pdf) and [V16N8-2667](https://www.ijiet.org/vol16/IJIET-V16N8-2667.pdf).

Production PDFs add a journal running head, DOI, and page numbers. The official template leaves those empty; they were **not** added (IJIET-01 ID 27).

Scientific numbers, table cells, and Fig. 1 data were **not** changed. Fig. 1 tick rotation only.

## Checklist vs template / 2026 papers

| Element | Template / 2026 | This manuscript after fix |
|---------|-----------------|---------------------------|
| Page A4, 2-col 243.65 + 14.4 gutter | Yes | Yes |
| Title 20 pt TNR centered | Template unbold; 2026 PDFs bold | 20 pt TNR, unbold (template) |
| Authors 11 pt, numbered affils, email, `*Corresponding author` | Yes | Yes; `*` superscripted |
| Manuscript received/revised/accepted | Placeholder in template | Placeholder restored |
| Abstract— / Keywords— | 9 pt; label bold | Mixed label/body restored |
| Roman H1 | Template sentence case; 2026 ALL CAPS | Unified ALL CAPS `I.`–`VI.` to match 2026 papers |
| Letter H2 italic | Yes | Yes |
| Table *n*. above table, 8 pt | 2026 mixed case “Table 1.” | Captions mixed case; PDF small-caps style may still look uppercase |
| Fig. 1 caption below | Yes | Yes |
| Numbered refs `[n]`, doi: | Yes | Yes |
| Empty header/footer | Template | Empty (publisher-owned) |

## Findings

| Page | Element | Problem | Severity | Fix |
|------|---------|---------|----------|-----|
| 3 | Two-column body | Section break before Fig. 1 left the right column empty (~½ page whitespace) | HIGH | Column break before *D. Train-only frequency strata*; figure section set Continuous 1-col |
| 4 | Figure 1 | Bottom x-tick labels overlapped (`1–19` / `20–99` / `100–499`) at print size | HIGH | Regenerated PNG with 40° ticks, slightly wider embed (490 pt). **Data unchanged** |
| 5 | Table 4 FAR [95% CI] | CI wrapped mid-interval (`0.268 [0.202,` / `0.337]`) | HIGH | En-dash intervals `[0.202–0.337]`; FAR column widened to 90 pt. **Numbers unchanged** |
| 1–8 | Heading 1 | `I. Introduction` (list) vs forced `IV. RESULT` after section breaks | MEDIUM | All six headings set to 2026-style `I. INTRODUCTION` … `VI. CONCLUSION` |
| 1 | Corresponding `*` | Asterisk not superscript | MEDIUM | Superscripted |
| 1 | Manuscript dates | Template line missing | MEDIUM | Placeholder `Manuscript received Month date, 2026; …` restored |
| 1 | Abstract / Keywords | Whole-paragraph bold vs mixed label | MEDIUM | Bold `Abstract—` / `Keywords—` only; body italic |
| 6 | Table 7 caption | Style `Normal` 10 pt | MEDIUM | Restored `Table Title` 8 pt |
| 7–8 | Long URLs | Hyphenation split `school-data` / `publ-ic` / anonymous URL | MEDIUM | Zero-width space after `/`; no-proofing on URL paragraphs |
| 5 | Table 4 span | 1-col gate table still opens a gap in the right-hand text column (Word two-col + spanning table) | LOW | Left as residual; 2026 papers also span wide tables |
| 3 | Settings listing | Unnumbered (intentional; Results stay Table 2–7) | LOW | None (science/numbering contract) |
| 4 | ECE formula | Inline, not template `equation` `(1)` | LOW | Left inline; formula unchanged |
| 4 | Left column after Fig. 1 | Shorter than right (G ends early) | LOW | Improved by continuous figure section; residual OK |
| 8 | Last-page column balance | Left column shorter (end matter) | LOW | Typical of last IJIET page; not forced |
| — | Journal running head | 2026 PDFs have Vol./No. header | n/a | Do **not** add; publisher production |
| 7 | Ethical / AI placeholders | `[AUTHOR ACTION REQUIRED…]`, `[version to be confirmed]` | n/a | Author action; not a typesetting defect |

## Special checks

- **Tables 3–6:** Table 3 is a readable 1-col span; Table 4 CIs no longer split on the comma; Table 5 1-col span; Table 6 fits a single column.
- **Long equations:** ECE/Brier remain inline and inside the 243.65 pt column.
- **Long URLs/DOIs:** wrap at slashes; CC BY link intact.
- **Fig. 1:** still 2×3 KC count + log training volume; caption below.

## Compile log

```
MS_DATES_INSERTED i=7
ABSTRACT_MIXED
KEYWORDS_MIXED
STAR_SUPERSCRIPT
COL_BREAK_BEFORE='D. Train-only frequency strata' i=117
FIG_REPLACED w=489.8 h=352.5
FIG_SEC=3 start=0 cols=1
T4_CI_FIX=8 widths=[62.0, 48.0, 52.0, 58.0, 58.0, 90.0, 48.0, 52.0, 44.6]
T7_CAPTION_STYLE i=405
URL_ZWSP_PARAS=3
FULL_TABLES=8 FIGS=1
ANON_AUTHORS i=2
ANON_AFFIL1 i=3
ANON_AFFIL2 i=4
ANON_EMAIL i=5
ANON_CORR i=6
ANON_CONTRIB i=465
ANON_ACK i=473
BLIND_TABLES=8 FIGS=1
FULL_PAGES=8
BLIND_PAGES=8
KEEP={'ASSISTments': True, 'Junyi Academy': True, 'XES3G5M': True, 'https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/': True, 'Corbett': True}
```
