# Task 1 — Source inspection and workspace (stop here)

Date: 2026-08-31

## Inspected (not modified)

| Artifact | Path / URL | Notes |
|----------|------------|--------|
| JEDM manuscript | `paper/main_jedm.tex` | Canonical long paper; `jedm` class; author-year citations |
| Prior IJIET IEEE draft | `ijiet/main_ijiet.tex` | IEEEtran two-column; 5-page compile in `ijiet/main_ijiet.log` (31 Aug 2026 11:03) |
| Four-partition numbers | `analysis/four_partition/` | Source of Tables 3/5/9 lineage |
| Author guidelines | https://www.ijiet.org/list-14-1.html | `.doc`/`.pdf`; embed figures; no dual submission |
| Scope | https://www.ijiet.org/list-15-1.html | Learning analytics / evaluation systems |
| Ethics / AI | https://www.ijiet.org/list-77-1.html | Disclose AI; no AI co-author; no fabrication |
| Official template | https://www.ijiet.org/files/IJIET_template.doc | **HTTP 500** — not obtained |
| Published layout proxy | https://www.ijiet.org/vol16/IJIET-V16N8-2667.pdf | Used only until `.doc` is available |

## Smallest change

Created `IJIET_SUBMISSION/` with copies and audit notes. **Did not edit** `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, or `ijiet/` working files (the snapshot under `source/snapshots/` is a copy).

## Compile

Not run for this task: there is no official-template working source yet. Recompiling the IEEEtran snapshot would only reproduce a non-authoritative layout.

Existing baseline (untouched): `ijiet/main_ijiet.log` reports `Output written on main_ijiet.pdf (5 pages)` with overfull hboxes on tables and underfull hboxes in Table `tab:cond`.

## Warnings / blockers for Task 2

1. Official Word template still unavailable (HTTP 500).
2. Dual submission: same experiments as JEDM — do not upload until that is resolved.
3. `paper/figures/figure2_bucket_distribution.pdf` is referenced by the IEEE draft but is not visible to workspace search (likely ignored); copy into `IJIET_SUBMISSION/figures/` in a later task with filesystem access.
4. IJIET requires AI-use disclosure; add only after deciding what (if anything) to declare, without inventing a methods story.

## Next task (do not start until this report is accepted)

**Task 2:** Obtain `IJIET_template.doc` (retry download; if still 500, extract styles from a second published PDF and document residual uncertainty). Produce a field-level format checklist. Still no manuscript rewrite.
