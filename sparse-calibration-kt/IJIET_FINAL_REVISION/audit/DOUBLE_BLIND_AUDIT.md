# DOUBLE_BLIND_AUDIT — IJIET named vs review PDF

**Date:** 2026-09-01  
**Policy:** IJIET ethics (list-77-1) uses double-blind peer review. The official template is named; this task ships **two** PDFs. Isolation: `IJIET_FINAL_REVISION/` only.

| Build | Path | Pages |
|-------|------|------:|
| Named (editor / camera-ready) | `output/main_ijiet_full.pdf` | 8 |
| Double-blind review | `output/main_ijiet_blind.pdf` | 8 |

Word sources: `manuscript/main_ijiet_full.docx` (unchanged science) and `manuscript/main_ijiet_blind.docx`.

## PASS / FAIL

| Check | Result |
|-------|--------|
| Visible author identity (blind PDF) | **PASS** |
| PDF metadata identity (blind `/Author`) | **PASS** |
| Repository identity | **FAIL** |
| Acknowledgments identity (blind PDF) | **PASS** |

## Visible author identity

Blind PDF must contain none of the author names, emails, affiliation strings, or CRediT initials. Named PDF must still contain them.

- Named PDF hits: Khanh-Trinh, Tuan Dao Minh, Duong Nguyen Tien, Chi Thanh Nguyen, Van-Hau, Hung Yen, utehy.edu.vn, trinhnk, tuanymc, duongnt@, thanhnc, haunv@, ioit.ai.vn, Military Science, Academy of Military, K.-T.N., T.D.M., D.N.T., C.T.N., V.-H.N.
- Blind PDF text hits: (none)
- Blind PDF raw-byte hits: (none)
- Blind PDF contains `Anonymous Authors`: yes

Removed in the blind Word/PDF only: names; numbered affiliations; emails; `*Corresponding author`; Author-contribution initials (`K.-T.N.` … → Author 1–5).

## PDF metadata identity

| Field | Full | Blind |
|-------|------|-------|
| Author | `Khanh-Trinh Nguyen, Tuan Dao Minh, Duong Nguyen Tien, Chi Thanh Nguyen, Van-Hau Nguyen` | `(blank)` |
| Creator | `(blank)` | `(blank)` |
| Producer | `(blank)` | `(blank)` |

## Repository identity

Review URL (retained in both PDFs): `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`

Live listing via `anonymous.4open.science` API (2026-09-01):

- Reachable: True
- Root entries: .gitignore, setup_EXPERIMENT_P0.md, sparse-calibration-kt
- README clone line: `git clone https://github.com/anonymous-researcher-2026/sparse-calibration-kt.git`
- `github.com/trinhnkt` in README: False
- Fetch error: HTTP 429 on a later file after the named JEDM tex files were already retrieved. The FAIL below is from those files, not from the rate limit.

Identity-bearing files inside that snapshot:

- `sparse-calibration-kt/paper/main_jedm.tex`: utehy.edu.vn, Hung Yen, haunv@, Khanh-Trinh, Van-Hau, ioit.ai.vn, thanhnc@, 0009-0004
- `sparse-calibration-kt/jedm_upload_folder/main_jedm.tex`: utehy.edu.vn, Hung Yen, haunv@, Khanh-Trinh, Van-Hau, ioit.ai.vn, thanhnc@, 0009-0004

The URL host is anonymous and does not contain a GitHub login. README clones `github.com/anonymous-researcher-2026/sparse-calibration-kt.git` (placeholder owner). The **named** JEDM sources `paper/main_jedm.tex` and `jedm_upload_folder/main_jedm.tex` in the same snapshot still list author names, `utehy.edu.vn` / `ioit.ai.vn` emails, Hung Yen / Military Science affiliations, and ORCID in the named tex. `paper/main_jedm.pdf` is the named compiled JEDM PDF. That is a repository-identity leak for IJIET reviewers who open those paths. `paper/main_jedm_anonymous.tex` uses Anonymous Authors / `anonymous@example.com` and was not counted as a leak.

This task does **not** rewrite the 4open.science snapshot. The IJIET manuscripts keep the existing anonymous URL.

## Acknowledgments identity

Blind acknowledgment body is `Omitted for double-blind review.` Institutional “respective institutions” wording is removed. Dataset names in the ethics statement are public benchmarks and are retained.

## Scientifically retained in the blind PDF

- `ASSISTments`: present
- `Junyi Academy`: present
- `XES3G5M`: present
- `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`: present
- `Corbett`: present

Public dataset names, numbered model citations, and the anonymous.4open.science URL are retained.

## Scientific locks (both PDFs)

Both PDFs: 8 pages; ECE `0.1136` / `0.2280`; FAR `0.196` / `0.268`; Fig. 1; refs [21]–[22]. All lock checks true.

ASSISTments cells were not edited. Tables/figure counts must match the named source.

## Anonymize log

```
A16 double-blind build
REPO={"url": "https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/", "reachable": true, "readme_github_owner": "git clone https://github.com/anonymous-researcher-2026/sparse-calibration-kt.git", "named_jedm_hits": ["utehy.edu.vn", "Hung Yen", "haunv@", "Khanh-Trinh", "Van-Hau", "ioit.ai.vn", "thanhnc@", "0009-0004"], "github_trinhnkt": false, "files_with_identity": [{"path": "sparse-calibration-kt/paper/main_jedm.tex", "hits": ["utehy.edu.vn", "Hung Yen", "haunv@", "Khanh-Trinh", "Van-Hau", "ioit.ai.vn", "thanhnc@", "0009-0004"]}, {"path": "sparse-calibration-kt/jedm_upload_folder/main_jedm.tex", "hits": ["utehy.edu.vn", "Hung Yen", "haunv@", "Khanh-Trinh", "Van-Hau", "ioit.ai.vn", "thanhnc@", "0009-0004"]}], "error": "HTTPError: HTTP Error 429: Too Many Requests", "root_names": [".gitignore", "setup_EXPERIMENT_P0.md", "sparse-calibration-kt"]}
FULL_TABLES=8 FIGS=1
ANON_AUTHORS i=2
ANON_AFFIL i=3
DEL_AFFIL2 i=4
DEL_EMAIL i=5
DEL_CORR i=6
ANON_CONTRIB i=533
ANON_ACK i=541
BLIND_TABLES=8 FIGS=1
FULL_PAGES=8
BLIND_PAGES=8
FULL_META_AUTHOR='Khanh-Trinh Nguyen, Tuan Dao Minh, Duong Nguyen Tien, Chi Thanh Nguyen, Van-Hau Nguyen'
BLIND_META_AUTHOR=''
FULL_HITS=['Khanh-Trinh', 'Tuan Dao Minh', 'Duong Nguyen Tien', 'Chi Thanh Nguyen', 'Van-Hau', 'Hung Yen', 'utehy.edu.vn', 'trinhnk', 'tuanymc', 'duongnt@', 'thanhnc', 'haunv@', 'ioit.ai.vn', 'Military Science', 'Academy of Military', 'K.-T.N.', 'T.D.M.', 'D.N.T.', 'C.T.N.', 'V.-H.N.']
BLIND_HITS=[]
BLIND_BYTE_HITS=[]
KEEP={'ASSISTments': True, 'Junyi Academy': True, 'XES3G5M': True, 'https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/': True, 'Corbett': True}
FULL_LOCKS={'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}
BLIND_LOCKS={'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}
```
