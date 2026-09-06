# IJIET_FINAL_REVISION

Living IJIET manuscript (named + blind, 9 pages; allowed 8–10). Edit Word in `manuscript/`, then pack `output/OJS_UPLOAD/`.

Official template: `../IJIET_SUBMISSION/source/template/IJIET_template.doc`.  
Do not upload `_archive/`.

| Path | Role |
|------|------|
| `manuscript/` | Named and blind Word |
| `output/OJS_UPLOAD/` | Files to upload to IJIET OJS |
| `analysis/` | Locked numeric artifacts |
| `audit/` | Changelogs and scientific locks |
| `supplementary/` | Tables S1–S10 sources |
| `figures/` | Fig. 1–3 |
| `tables/` | Numeric table copies |
| `a2b/` | Masked XES3G5M series (source of truth for XES ECE) |

Target: named `main_ijiet_full` and double-blind `main_ijiet_blind`. Rebuild both with `build_a16_double_blind.py` after named edits.

## Submit here

OJS files: `output/OJS_UPLOAD/` (see `README_SUBMIT.md` there).

Current PDFs/Word are the P0 protocol pack (9 pages). Copies also sit in `IJIET_SUBMISSION/`. Do not upload `_archive/`.

## Integrity

See `audit/SCIENTIFIC_LOCKS.md`. Every task writes `audit/CHANGELOG_<TASK>.md`, compiles, then **stops**.
