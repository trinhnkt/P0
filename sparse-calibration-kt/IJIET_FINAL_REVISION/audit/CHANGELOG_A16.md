# CHANGELOG_A16 — IJIET double-blind manuscript

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged (`0.1136`, `0.2280`, FAR `0.196`/`0.268`, ΔFAR `0.047`, CI `[0.006, 0.138]`).

Same-day XES/A2B scientific apply is preserved in `audit/CHANGELOG_A16_XES.md`.

## Builds

| File | Role |
|------|------|
| `output/main_ijiet_full.pdf` | Named manuscript (8 pages) |
| `output/main_ijiet_blind.pdf` | Double-blind review (8 pages) |
| `manuscript/main_ijiet_full.docx` | Named Word (science unchanged) |
| `manuscript/main_ijiet_blind.docx` | Blind Word |
| `manuscript/main_ijiet_blind.doc` | Blind Word 97–2003 |

## Blind removals

Author names, affiliations, emails, corresponding-author line, CRediT initials, identifying acknowledgment. PDF `/Author` (and Creator/Producer) cleared on the blind file only.

## Retained

Public dataset names; numbered citations; `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`.

## Audit

See `audit/DOUBLE_BLIND_AUDIT.md`.

| Check | Result |
|-------|--------|
| Visible author identity | PASS |
| PDF metadata identity | PASS |
| Repository identity | FAIL |
| Acknowledgments identity | PASS |

Repository identity is **FAIL** if the live 4open snapshot still contains named JEDM `main_jedm.tex` / emails. The manuscript URL was not changed.

## Files

- `IJIET_FINAL_REVISION/build_a16_double_blind.py`
- `IJIET_FINAL_REVISION/audit/DOUBLE_BLIND_AUDIT.md`
- this changelog
