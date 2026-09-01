# Live reference audit — titles vs opened documents

**Date:** 2026-08-31  
**Source:** `output/main_ijiet_full.pdf` REFERENCES `[1]`–`[22]`  
**Method:** Crossref API for every DOI; publisher/arXiv/NeurIPS/PMLR/Springer/Zenodo/Kaggle/Google Sites landing pages and PDFs for titles.

**Verdict:** Every numbered item is a real work. No DOI or URL opens a different paper. Differences below are capitalization, IEEE style, or one dataset year.

Legend: **OK** = title on the opened document is the same work (IEEE case ignored). **NIT** = style only. **FIX?** = bibliographic detail, not a fake title.

| # | Manuscript title | Opened document title | Link opened | Title match | Notes |
|---|------------------|----------------------|-------------|-------------|-------|
| 1 | Knowledge Tracing: Modeling the acquisition of procedural knowledge | Knowledge tracing: Modeling the acquisition of procedural knowledge | https://doi.org/10.1007/BF01099821 → Springer; Crossref | **OK** | Springer issue date Dec 1994, vol. 4, pp. 253–278. Crossref year field is 1995 (ignore). Journal name on Springer: *User Modeling and User-Adapted Interaction* (manuscript matches; Crossref has British *Modelling*). |
| 2 | Deep Knowledge Tracing | Deep Knowledge Tracing (PDF first heading) | https://proceedings.neurips.cc/paper/2015/file/bac9162b47c56fc8a4d2a519803d51b3-Paper.pdf | **OK** | NIPS 2015 / Adv. Neural Inf. Process. Syst. vol. 28, pp. 505–513. No Crossref journal DOI (correctly omitted). |
| 3 | Knowledge Tracing: A survey | Knowledge Tracing: A Survey | https://doi.org/10.1145/3569576 → ACM CSUR 55(11):1–37, 2023 | **OK** | Authors Abdelrahman, Wang, Nunes. ACM lists Bernardo Pereira Nunes; IEEE initial **B. Nunes** is fine. |
| 4 | SimpleKT: A simple but tough-to-beat baseline… | simpleKT: A Simple But Tough-to-Beat Baseline for Knowledge Tracing | https://arxiv.org/abs/2302.06881 (ICLR 2023; OpenReview `9HiGqC9C-KA`) | **OK** | **NIT:** official stylization is **simpleKT**, not SimpleKT. No Crossref DOI. |
| 5 | pyKT: A python library to benchmark… | pyKT / PYKT: A Python Library to Benchmark Deep Learning based Knowledge Tracing Models | https://arxiv.org/abs/2206.11460 ; NeurIPS 2022 D&B PDF | **OK** | PDF footer: **36th** NeurIPS 2022 D&B (matches). **NIT:** official “Python”; NeurIPS PDF header often **PYKT**. |
| 6 | Probabilistic Models for Some Intelligence and Attainment Tests | same book title | Danish Institute for Educational Research, 1960 (Rasch.org / Psychometrika 1963 review) | **OK** | Book; no DOI. Publisher English name matches. |
| 7 | Context-aware attentive Knowledge Tracing | Context-Aware Attentive Knowledge Tracing | https://doi.org/10.1145/3394486.3403282 → ACM KDD 2020, pp. 2330–2339 | **OK** | Ghosh, Heffernan, Lan. |
| 8 | Graph-based Knowledge Tracing: Modeling student proficiency using graph neural network | Graph-based Knowledge Tracing: Modeling Student Proficiency Using Graph Neural Network | https://doi.org/10.1145/3350546.3352513 → WI 2019, pp. 156–163 | **OK** | Nakagawa, Iwasawa, Matsuo. |
| 9 | Contrastive learning for Knowledge Tracing | Contrastive Learning for Knowledge Tracing | https://doi.org/10.1145/3485447.3512105 → WWW 2022, pp. 2330–2338 | **OK** | Last author Sungrae Park (**S. Park**), not Choi. |
| 10 | Metrics for evaluation of student models | Metrics for Evaluation of Student Models | https://doi.org/10.5281/zenodo.3554665 → Zenodo + JEDM 7(2):1–19 | **OK** | Not in Crossref; Zenodo/JEDM DOI works. |
| 11 | On calibration of modern neural networks | On Calibration of Modern Neural Networks | https://proceedings.mlr.press/v70/guo17a.html — PMLR 70:1321–1330, 2017 | **OK** | 34th ICML. No Crossref DOI (correctly omitted). |
| 12 | Obtaining well calibrated probabilities using Bayesian binning | Obtaining Well Calibrated Probabilities Using Bayesian Binning | https://doi.org/10.1609/aaai.v29i1.9602 → AAAI OJS vol. 29, no. 1, 2015 | **OK** | Article-id venue; print pages not required. |
| 13 | Verification of forecasts expressed in terms of probability | VERIFICATION OF FORECASTS EXPRESSED IN TERMS OF PROBABILITY | https://doi.org/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2 — MWR 78(1):1–3 | **OK** | AMS heading is all caps; same title. |
| 14 | The comparison and evaluation of forecasters | The Comparison and Evaluation of Forecasters | https://doi.org/10.2307/2987588 — *The Statistician* 32(1/2), 1983 | **OK** | Crossref page field is start page 12; 12–22 is the standard span. |
| 15 | Recovering stranded discrimination in Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage | Recovering Stranded Discrimination in Knowledge Tracing: Per-Item Bias Correction via Empirical-Bayes Shrinkage | https://arxiv.org/abs/2606.14123 and https://doi.org/10.48550/arXiv.2606.14123 | **OK** | Preprint. GitHub claims ECML PKDD 2026; no LNCS volume yet — arXiv cite is the honest one. Crossref does not index this arXiv DOI; `doi.org` still opens arXiv. |
| 16 | Towards robust Knowledge Tracing models via k-sparse attention | Towards Robust Knowledge Tracing Models via k-Sparse Attention | https://doi.org/10.1145/3539618.3592073 → SIGIR 2023, pp. 2441–2445 | **OK** | Huang, Liu, Zhao, Luo, Weng. |
| 17 | Cold start problem: An experimental study of Knowledge Tracing models with new students | Cold Start Problem: An Experimental Study of Knowledge Tracing Models with New Students | https://doi.org/10.1007/978-3-031-98459-4_30 → Springer AIED 2025, LNCS 15880, pp. 425–432 | **OK** | Underscore `_30` in DOI is required. |
| 18 | ASSISTments 2012–2013 school data with affect | Page H1: **2012-13 School Data with Affect** | https://sites.google.com/site/assistmentsdata/datasets/2012-13-school-data-with-affect (live) | **OK** | Same dump. Title in the bibliography is a descriptive expansion of the site heading, not a different dataset. |
| 19 | Junyi Academy online learning activity dataset | Junyi Academy Online Learning Activity Dataset | https://www.kaggle.com/datasets/junyiacademy/learning-activity-public-dataset-by-junyi-academy (live) | **OK** | **FIX?:** Kaggle recommended citation year is **2020** (Chen/Hsieh/Tsai); manuscript uses **2019** (end of the 2018/08–2019/07 log window). Title and URL match. |
| 20 | XES3G5M: A Knowledge Tracing benchmark dataset with auxiliary information | XES3G5M: A Knowledge Tracing Benchmark Dataset with Auxiliary Information | NeurIPS 2023 D&B PDF hash `67fc628f17c2ad53621fb961c6bafcaf` | **OK** | **37th** NeurIPS 2023 D&B. Authors include T. Guo and J. Weng. No Crossref DOI. |
| 21 | Uncertainty-aware Knowledge Tracing | Uncertainty-aware Knowledge Tracing | https://doi.org/10.1609/aaai.v39i27.35007 → AAAI 39(27):27905–27913, 2025 | **OK** | PDF/OJS authors: Weihua Cheng, Hanwen Du, Chunxiao Li, Ersheng Ni, Liangdi Tan, Tianqi Xu, Yongxin Ni. Initials in the list match. |
| 22 | Knowing when to defer: Selective prediction for responsible Knowledge Tracing | Knowing When to Defer: Selective Prediction for Responsible Knowledge Tracing | https://proceedings.mlr.press/v339/mitton26a.html — PMLR 339:22–42, 2026 | **OK** | Mitton, Bhattacharyya, Abboud, Woodhead. No DOI on PMLR (correctly omitted). Optional durable URL not in the list. |

## What is not a problem

- IEEE title case vs publisher Title Case / ALL CAPS.
- Dataset records `[18]`–`[19]` using `[Online]. Available:` instead of a DOI.
- Keeping `[15]` as arXiv rather than “ECML PKDD 2026” without an LNCS volume.

## Optional one-line bibliographic tweak (not a fake paper)

- `[19]` year **2019 → 2020** if matching the Kaggle recommended citation.

No table cells, ECE/FAR numbers, or in-text keys need to change for this audit.
