# Double-blind check (IJIET-15)

**Date:** 2026-08-31  
**Policy:** IJIET ethics page (list-77-1) uses **double-blind** peer review; FAQ Q1/Q6 say blind review. The official template is named; this task therefore ships **two** PDFs.

| Build | Path | Pages |
|-------|------|------:|
| Named (camera-ready / editor) | `output/main_ijiet_full.pdf` | 8 |
| Double-blind review | `output/main_ijiet_blind.pdf` | 8 |

## What was anonymized (blind only)

- Author names, numbered affiliations, emails, `*Corresponding author`.
- Author-contribution initials (`K.-T.N.` …) replaced with Author 1–5.
- Acknowledgment naming “respective institutions” replaced with “Omitted for double-blind review.”
- Word/PDF `Author` and related document properties cleared.
- No ORCID was present in the Word source; ORCID strings were still scanned.

## What was **not** anonymized

- Public dataset names: ASSISTments 2012, Junyi Academy, XES3G5M.
- Numbered literature `[1]`–`[20]`.
- Train-only strata, seeds, occupancy flags, FAR/ECE tables.
- Artifact URL (already anonymous): `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/` (PDF line wrapping is ignored when checking this URL).

## Repository

The review artifact is already on anonymous.4open.science. It does not contain `github.com/trinhnkt` or other owner logins. The same URL is used in both PDFs.

## PDF metadata

| Field | Full | Blind |
|-------|------|-------|
| Author | `Khanh-Trinh Nguyen, Tuan Dao Minh, Duong Nguyen Tien, Chi Thanh Nguyen, Van-Hau Nguyen` | `(blank)` |
| Creator | `` | `(blank)` |
| Producer | `` | `(blank)` |

## Identifying-string scan

- Full PDF must contain author/affiliation strings. Hits: Khanh-Trinh, Tuan Dao Minh, Duong Nguyen Tien, Chi Thanh Nguyen, Van-Hau, Hung Yen, utehy.edu.vn, trinhnk, tuanymc, duongnt@, thanhnc, haunv@, ioit.ai.vn, Military Science, K.-T.N., T.D.M., D.N.T., C.T.N., V.-H.N.
- Blind PDF must contain **none** of those strings. Hits: (none)
- Blind PDF raw-byte scan for names/emails/GitHub: (none)

## Kept scientific tokens in the blind PDF

- `ASSISTments`: present
- `Junyi Academy`: present
- `XES3G5M`: present
- `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`: present
- `Corbett`: present

## Verdict

PASS: named PDF identifies authors; blind PDF does not; metadata Author is blank.
