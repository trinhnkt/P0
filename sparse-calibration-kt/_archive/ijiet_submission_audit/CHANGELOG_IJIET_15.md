# IJIET-15 — Double-blind review version

**Date:** 2026-08-31  
**Scope:** Two compiled PDFs from `source/main_ijiet_step14.docx`. Named vs anonymized front/end matter only.  
**Audit:** `IJIET_SUBMISSION/audit/DOUBLE_BLIND_CHECK.md`  
**Not modified:** table numeric cells; Fig. 1; public dataset names; numbered literature; originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`.

---

## Builds

| File | Role |
|------|------|
| `output/main_ijiet_full.pdf` | Camera-ready / editor: authors, affiliations, emails, `*Corresponding author`. PDF Author metadata lists the five authors. |
| `output/main_ijiet_blind.pdf` | Double-blind review: `Anonymous Authors`; affiliations omitted; emails and corresponding-author line removed; Author 1–5 CRediT mapping; acknowledgment omitted. PDF `/Author` is null. |

Both PDFs are 8 pages. Word COM page statistics can under-count the two-column blind file; the audit uses the PDF page count.

---

## Anonymization (blind only)

- Names, Hung Yen / Academy of Military Science affiliations, institutional emails, ORCID (none in source; still scanned).
- Contribution initials `K.-T.N.` … `V.-H.N.` → Author 1–5 (same role mapping).
- “supported by the authors’ respective institutions” → “Omitted for double-blind review.”
- Owner GitHub (`github.com/trinhnkt`) is not in either manuscript.

## Not anonymized

- ASSISTments 2012, Junyi Academy, XES3G5M.
- References `[1]`–`[20]`.
- Train-only strata, seeds, occupancy flags, FAR/ECE numbers.
- Review artifact URL: `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/` (already anonymous).

---

## Compile

`python IJIET_SUBMISSION/source/prepare_step15.py` — PASS (text scan, byte scan, metadata, kept scientific tokens).
