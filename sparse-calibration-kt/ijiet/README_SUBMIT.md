# IJIET submission pack

**Journal:** [International Journal of Information and Education Technology (IJIET)](https://www.ijiet.org/)  
ISSN 2010-3689 · IACSIT Press · Scopus · CiteScore 3.2 · APC **USD 500** · OJS: https://ojs.ejournal.net/index.php/ijiet/submissions

**Files for upload**

| File | Role |
|------|------|
| `Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.doc` | **Preferred IJIET upload** (official 2026 template, filled) |
| `Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx` | Same manuscript, Word 2007+ |
| `main_ijiet.pdf` | Earlier IEEE-style PDF (not the official template) |
| `main_ijiet.tex` | Earlier IEEE TeX draft (do not treat as template-compliant) |

Official template (local copy): `../IJIET_SUBMISSION/audit/IJIET_template.doc`

Compile:

```
cd ijiet
pdflatex main_ijiet.tex
bibtex main_ijiet
pdflatex main_ijiet.tex
pdflatex main_ijiet.tex
```

---

## Dual submission (do this first)

IJIET requires that the paper **not be under consideration elsewhere**. The 45-page JEDM manuscript and this IJIET short paper share the **same experiments, tables, and findings**.

- If the JEDM paper is submitted or in review: **do not** submit this IJIET version until JEDM is withdrawn or rejected.
- If you choose IJIET instead of JEDM: withdraw JEDM first, then submit this shorter applied version.
- Do not run both venues in parallel.

---

## How this version differs from the JEDM draft

| | JEDM (`paper/`) | IJIET (`ijiet/`) |
|--|-----------------|------------------|
| Length | ~45 pages | 5 two-column IEEE pages (~IJIET article length) |
| Audience | EDM / evaluation methodology | Platform designers, learning analytics |
| Punchline | Diagnostic protocol + six findings | Mastery/remediation **gate** on sparse KCs |
| Dropped | L1–L8 as a contribution, full appendices, DeLong, A9/A10 depth | Kept as “not shown” |
| Claims | Unchanged (FINDING vs HYPOTHESIS; no new model) | Same numbers, applied framing |

---

## Scope / novelty fit (honest)

**Fit: moderate — usable if framed as learning-analytics evaluation, not as a 45-page protocol paper.**

IJIET scope that matches: learning analytics, evaluation systems, impact of technology use, computer-based training. Vol. 16 No. 8 (2026) already published a student-performance prediction paper (OULAD + RNNs), so KT-style sequence models are in-scope.

**What IJIET reviewers will like**

- A product-facing question: should a global mastery threshold trust $p$ on rarely practiced skills?
- Simulated false-mastery / miss rates (Table III–IV), not only AUC.
- Dataset dependence (ASSISTments gradient vs Junyi empty vs XES flat ECE).

**What they may push back on**

- No classroom trial, no LMS A/B test, no TAM/engagement survey — IJIET’s modal paper is instructional intervention, AR/VR, ChatGPT-in-class.
- Heavy ECE/Brier language without a deployed system.
- Novelty is **diagnostic**, not a new model or pedagogy. Say that in the cover letter.
- JEDM / *Computers & Education* / EDM venues are the better scientific home for the full protocol.

**Cover-letter one-liner (if you submit here):**  
*We do not propose a new KT architecture. We show that population AUC can hide a dataset-dependent calibration failure on sparse skills, and that a locked global mastery gate then raises false-mastery rates on ASSISTments 2012 (Limited occupancy; five seeds).*

---

## Author checklist (IJIET site)

- [ ] Original, unpublished, not under review elsewhere
- [ ] IEEE two-column style (this PDF) or official Word template
- [ ] Figures/tables embedded
- [ ] Honor code / plagiarism statement
- [ ] Corresponding author: Van-Hau Nguyen, haunv@utehy.edu.vn
- [ ] APC USD 500 after acceptance
