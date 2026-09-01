# Reference audit — IJIET Related Work (Section II)

**Date:** 2026-08-31  
**Scope:** Every citation used in the rewritten Literature Review, plus two corrections in the numbered list that those citations depend on.  
**Rule:** no new numbered source was inserted. All in-text keys remain in `[1]`–`[20]`.  
**Sources checked:** ACM DL / publisher pages, NeurIPS proceedings, PMLR, AAAI OJS, Springer, JEDM, arXiv, Crossref DOIs as listed below.

Section II cites: `[1]`–`[17]`, `[20]`. It does **not** cite `[18]` or `[19]` (dataset records; they remain in Methods).

---

## Corrections applied in the Word reference list

| Key | Issue | Action |
|-----|--------|--------|
| `[5]` pyKT | Venue said “Thirty-seventh … 2022”. NeurIPS 2022 Datasets and Benchmarks is the **36th** conference. | Changed to “Thirty-sixth … 2022”. Year 2022 unchanged. |
| `[9]` CL4KT | Last author was “D. Choi”. ACM WWW ’22 lists **Sungrae Park** (with Wonsung Lee, Jaeyoon Chun, Youngmin Lee, Kyoungsoo Park). | Changed to “S. Park”. Initials otherwise retained (IEEE style). |

No other reference strings were rewritten. Numbering of `[1]`–`[20]` is unchanged so Methods/Results citations still resolve.

---

## Citations used in Section II

| Key | Authors (verified) | Title | Venue / year | DOI or durable ID | Status |
|-----|--------------------|-------|--------------|-------------------|--------|
| `[1]` | Albert T. Corbett; John R. Anderson | Knowledge tracing: Modeling the acquisition of procedural knowledge | *User Modeling and User-Adapted Interaction* 4(4):253–278, 1994 | [10.1007/BF01099821](https://doi.org/10.1007/BF01099821) | VERIFIED. Word title-cases “Tracing”; publisher uses sentence case. |
| `[2]` | Chris Piech; Jonathan Bassen; Jonathan Huang; Surya Ganguli; Mehran Sahami; Leonidas J. Guibas; Jascha Sohl-Dickstein | Deep Knowledge Tracing | NeurIPS 2015, pp. 505–513 | ACM [10.5555/2969239.2969296](https://dl.acm.org/doi/10.5555/2969239.2969296) (proceedings); no Crossref journal DOI | VERIFIED. |
| `[3]` | Ghodai Abdelrahman; Qing Wang; Bernardo Nunes | Knowledge Tracing: A Survey | *ACM Computing Surveys* 55(11):1–37, 2023 | [10.1145/3569576](https://doi.org/10.1145/3569576) | VERIFIED. Word uses “B. Nunes” (ACM listing). |
| `[4]` | Zitao Liu; Qiongqiong Liu; Jiahao Chen; Shuyan Huang; Weiqi Luo | simpleKT: A Simple But Tough-to-Beat Baseline for Knowledge Tracing | ICLR 2023 | OpenReview `9HiGqC9C-KA`; arXiv [2302.06881](https://arxiv.org/abs/2302.06881) | VERIFIED. No Crossref DOI. Word “Q. Liu” = Qiongqiong Liu (not a different Qi Liu). |
| `[5]` | Zitao Liu; Qiongqiong Liu; Jiahao Chen; Shuyan Huang; Jiliang Tang; Weiqi Luo | pyKT: A Python Library to Benchmark Deep Learning based Knowledge Tracing Models | NeurIPS 2022 Datasets and Benchmarks (36th conference) | arXiv [2206.11460](https://arxiv.org/abs/2206.11460) | VERIFIED after venue-number correction. |
| `[6]` | Georg Rasch | *Probabilistic Models for Some Intelligence and Attainment Tests* | Danish Institute for Educational Research, 1960 | none (book) | VERIFIED as the canonical 1PL/Rasch source used in the manuscript. |
| `[7]` | Aritra Ghosh; Neil Heffernan; Andrew S. Lan | Context-Aware Attentive Knowledge Tracing | KDD 2020, pp. 2330–2339 | [10.1145/3394486.3403282](https://doi.org/10.1145/3394486.3403282) | VERIFIED. |
| `[8]` | Hiromi Nakagawa; Yusuke Iwasawa; Yutaka Matsuo | Graph-based Knowledge Tracing: Modeling Student Proficiency Using Graph Neural Network | IEEE/WIC/ACM Web Intelligence 2019, pp. 156–163 | [10.1145/3350546.3352513](https://doi.org/10.1145/3350546.3352513) | VERIFIED. |
| `[9]` | Wonsung Lee; Jaeyoon Chun; Youngmin Lee; Kyoungsoo Park; Sungrae Park | Contrastive Learning for Knowledge Tracing | *Proc. ACM Web Conference* (WWW) 2022, pp. 2330–2338 | [10.1145/3485447.3512105](https://doi.org/10.1145/3485447.3512105) | VERIFIED after last-author correction. Earlier bib/Word “Woonhak / Dongmin Choi” does **not** match ACM. |
| `[10]` | Radek Pelánek | Metrics for Evaluation of Student Models | *Journal of Educational Data Mining* 7(2):1–19, 2015 | [10.5281/zenodo.3554665](https://doi.org/10.5281/zenodo.3554665) | VERIFIED (JEDM Zenodo DOI). |
| `[11]` | Chuan Guo; Geoff Pleiss; Yu Sun; Kilian Q. Weinberger | On Calibration of Modern Neural Networks | ICML 2017, PMLR 70:1321–1330 | PMLR [proceedings.mlr.press/v70/guo17a](https://proceedings.mlr.press/v70/guo17a.html) | VERIFIED. |
| `[12]` | Mahdi Pakdaman Naeini; Gregory Cooper; Milos Hauskrecht | Obtaining Well Calibrated Probabilities Using Bayesian Binning | AAAI 2015, vol. 29, no. 1 | [10.1609/aaai.v29i1.9602](https://doi.org/10.1609/aaai.v29i1.9602) | VERIFIED. ECE source. Word omits print pages (AAAI is article-id); optional pp. 2901–2907 appear in some reprints—not added. |
| `[13]` | Glenn W. Brier | Verification of Forecasts Expressed in Terms of Probability | *Monthly Weather Review* 78(1):1–3, 1950 | [10.1175/1520-0493(1950)078\<0001:VOFEIT\>2.0.CO;2](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2) | VERIFIED. |
| `[14]` | Morris H. DeGroot; Stephen E. Fienberg | The Comparison and Evaluation of Forecasters | *The Statistician* 32(1/2):12–22, 1983 | [10.2307/2987588](https://doi.org/10.2307/2987588) | VERIFIED. Reliability-diagram / refinement source. |
| `[15]` | Xiaoran Yan; Cheng Tang; Atsushi Shimada | Recovering Stranded Discrimination in Knowledge Tracing: Per-Item Bias Correction via Empirical-Bayes Shrinkage | arXiv:2606.14123, 2026 | [10.48550/arXiv.2606.14123](https://doi.org/10.48550/arXiv.2606.14123) | VERIFIED as **preprint**. A project page claims ECML PKDD 2026; that venue is **not** used in the manuscript. |
| `[16]` | Shuyan Huang; Zitao Liu; Xiangyu Zhao; Weiqi Luo; Jian Weng | Towards Robust Knowledge Tracing Models via k-Sparse Attention | SIGIR 2023, pp. 2441–2445 | [10.1145/3539618.3592073](https://doi.org/10.1145/3539618.3592073) | VERIFIED. Word “X. Zhao / J. Weng” matches Xiangyu Zhao and Jian Weng. Repo `references.bib` had “Zhao, Xia” and “Weng, Jialin”—those full names are **wrong** and were not copied into Word. |
| `[17]` | Indronil Bhattacharjee; Christabel Wayllace | Cold Start Problem: An Experimental Study of Knowledge Tracing Models with New Students | AIED 2025, LNCS 15880, pp. 425–432 | [10.1007/978-3-031-98459-4_30](https://doi.org/10.1007/978-3-031-98459-4_30) | VERIFIED. New-**student** cold start, not concept-level \(f=0\). |
| `[20]` | Zitao Liu; Qiongqiong Liu; Teng Guo; Jiahao Chen; Shuyan Huang; Xiangyu Zhao; Jiliang Tang; Weiqi Luo; Jian Weng | XES3G5M: A Knowledge Tracing Benchmark Dataset with Auxiliary Information | NeurIPS 2023 Datasets and Benchmarks (37th conference) | NeurIPS hash `67fc628f17c2ad53621fb961c6bafcaf` | VERIFIED. Cited in Section II only for the long-tail KC volume fact, not as a new experimental table. |

---

## Sources deliberately not added

The JEDM related-work file also cites DKVMN, GIKT, EdNet, DAS3H, csKT, CLST, LLM cold-start papers, Kapoor leakage, and DeLong testing. Those records exist in `source/bibliography/references.bib` but were **not** inserted into the IJIET numbered list, because they are not required for the four-group IJIET narrative and would renumber `[18]`–`[20]` or add unverified extras.

---

## How each Section II citation is used

| Group | Keys | Use (not overclaim) |
|-------|------|---------------------|
| A. Benchmark models | `[1]` BKT, `[6]` IRT/Rasch, `[2]` DKT, `[7]` AKT, `[4]` SimpleKT, `[5]` pyKT, `[3]` survey | Population-AUC evaluation lineage. |
| B. Graph / SSL | `[8]` GKT, `[9]` CL4KT | Related architectures; **not** this paper’s contribution. |
| C. Sparse / cold-start | `[16]` sparse attention; `[17]` new-student; `[20]` long-tail volume | Distinguishes four problem types. No claim that sparseKT is a low-frequency-KC method. |
| D. Calibration / decisions | `[10]` probability-level student-model metrics; `[12]` ECE; `[11]` NN miscalibration; `[13]` Brier; `[14]` reliability diagrams; `[15]` complementary per-item correction | Probability-level evaluation. `[15]` is not presented as our calibrator. |
| Gap (no extra cite) | — | Aggregate discrimination vs joint sparse-frequency / calibration / occupancy / threshold error. |
