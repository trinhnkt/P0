# IJIET-14 — Reference audit

**Date:** 2026-08-31  
**Scope:** All 20 numbered references; IJIET (IEEE-like) punctuation; verified DOIs as `doi: …`; dataset URLs only where required.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step14.docx` (copied from step13).  
**Audit table:** `IJIET_SUBMISSION/audit/REFERENCE_AUDIT_FULL.csv`  
**Not modified:** in-text `[1]`–`[20]` keys; table cells; Fig. 1; scientific body; originals under `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `ijiet/`.

---

## Specific checks

| Item | Finding | Action |
|------|---------|--------|
| **[5] pyKT** | NeurIPS 2022 Datasets and Benchmarks is the **36th** conference (paper footer). Not the 37th. No Crossref DOI. Book-series vol. 35 not used (would collide with “36th”). | `in Proc. 36th Conference … Track, 2022.` |
| **[20] XES3G5M** | NeurIPS 2023 D&B is the **37th** conference (paper footer; hash `67fc628f…`). No Crossref DOI. Book-series vol. 36 not used. | `in Proc. 37th Conference … Track, 2023.` |
| **[17] Bhattacharjee & Wayllace** | Springer chapter DOI is `10.1007/978-3-031-98459-4_30` (underscore, not hyphen). LNCS **15880**, pp. **425–432**. | DOI added in that form. |
| **[15] Yan et al.** | GitHub/project pages claim ECML PKDD 2026 acceptance. No Springer LNCS volume, pages, or conference DOI. | **Retained** `arXiv:2606.14123` plus arXiv DOI `10.48550/arXiv.2606.14123`. |
| **[18] ASSISTments** | Official dump page (live): `https://sites.google.com/site/assistmentsdata/datasets/2012-13-school-data-with-affect`. Feng et al. 2009 is the site’s recommended *paper* cite for non-affect use; not substituted. | Kept dataset record + `[Online]. Available:` URL. |
| **[19] Junyi** | Official Kaggle dump, 2019. | Kept dataset record + `[Online]. Available:` URL. |

---

## Style

2026 IJIET articles use numbered IEEE punctuation and `doi: 10.…` (not a bare URL) when a DOI exists. Journal/book titles are italic. Electronic dataset records keep `[Online]. Available:`. Missing months, print pages, and Crossref DOIs were **not** invented (e.g. AAAI `[12]` stays article-id; SimpleKT `[4]` has no Crossref DOI).

Other updates: `[2]` vol. 28; `[11]` 34th ICML / PMLR vol. 70; DOIs added on `[1]`, `[3]`, `[7]`–`[10]`, `[12]`–`[14]`, `[16]`. `[9]` last author remains **S. Park**.

---

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step14.pdf` — 8 pages, 5674 words, 8 tables, 1 figure. Table 2/3 rates unchanged.
