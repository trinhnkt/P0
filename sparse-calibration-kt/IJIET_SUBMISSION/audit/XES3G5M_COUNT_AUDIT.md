# XES3G5M count audit (IJIET-07)

**Date:** 2026-08-31  
**Rule:** do not silently change manuscript Table 1 (866 KCs; 7.95M / 7,953,709 interactions).  
**Manuscript file audited:** `IJIET_SUBMISSION/source/main_ijiet_step06.docx` Table 1 (carried into step07 unchanged).

---

## Official dataset documentation (Liu et al., NeurIPS 2023 Datasets and Benchmarks; manuscript `[20]`)

The XES3G5M paper reports:

| Quantity | Official |
|----------|----------|
| Students | 18,066 |
| Questions | 7,652 |
| Knowledge components | 865 |
| Interactions | 5,549,635 (question-level) |

---

## Manuscript Table 1 (unchanged)

| Quantity | Table 1 |
|----------|---------|
| Learners | 18,066 |
| KCs | **866** |
| Interactions | **7.95M** (exact processed rows **7,953,709**) |
| Learner-based test events | 1,589,145 |

Processed items in the local cohort table (not shown in IJIET Table 1): **7,653**.

---

## Local verification (2026-08-31)

Sources: `data/raw/xes3g5m/metadata/questions.json`; authors’ `kc_level/train_valid_sequences.csv` and `kc_level/test.csv`; flattened `data/raw/xes3g5m/raw_data.csv`; processed `data/processed/xes3g5m/interactions.csv`; loader `src/create_xes3g5m_full.py`; filters `src/preprocess.py`. Raw diagnostic dump: `audit/xes3g5m_count_raw.txt`.

| Check | Result |
|-------|--------|
| `questions.json` keys | **7,652** (matches official questions) |
| Processed unique `item_id` | **7,653** |
| Processed unique `item_id` excluding `-1` | **7,652** (matches official) |
| Processed unique `kc_id` | **866** |
| Processed unique `kc_id` excluding `-1` | **865** (matches official) |
| Rows with `kc_id == -1` (and `item_id == -1`) | **1,540,356** |
| Non-padding processed rows | **6,413,353** |
| Flattened raw rows | **7,953,709** |
| Processed rows after `preprocess.py` | **7,953,709** (dropped **0**) |
| `kc_level` train_valid sequences | 33,397; unique concepts **865**; padding concept tokens **1,540,356** |
| `kc_level` test sequences | 3,613; unique concepts 828; padding concept tokens **0** |
| Learners | **18,066** (matches official) |

`create_xes3g5m_full.py` concatenates the two `kc_level` sequence files and expands comma-separated `questions` / `concepts` / `responses` / `timestamps` to one row per sequence position. It does **not** drop tokens coded `-1`. `preprocess.py` dropna on identifiers does **not** treat `-1` as missing, so padding rows remain.

`cid2content_emb.json` (1,175 keys) and `kc_routes_map.json` are route/content maps, **not** the 865-KC inventory. Unique `kc_routes` strings inside `questions.json` (1,240) are also not the paper’s KC count.

---

## Why Table 1 differs from the official paper

### 866 vs 865 KCs — **verified**

The extra “KC” is the sequence-padding token **`skill_id = -1`**, counted by `nunique()` on the flattened table. Excluding `-1` recovers the official **865**.

### 7,653 vs 7,652 items — **verified**

The extra item is **`question_id = -1`** on the same padding rows. Excluding `-1` recovers the official **7,652**.

### 7,953,709 vs 5,549,635 interactions — **verified as kc_level expansion, not a silent recount**

Two additive mechanisms, both from flattening the authors’ **kc_level** sequences:

1. **Padding rows retained:** 1,540,356 rows with concept/question `-1` (all from `train_valid_sequences.csv`).  
   7,953,709 − 1,540,356 = **6,413,353** non-padding KC-level rows.
2. **Multi-KC expansion:** a question tagged with several concepts becomes several sequence positions (one row per listed concept).  
   6,413,353 / 5,549,635 ≈ **1.156** KC-level rows per official question-level interaction (863,718 extra non-padding rows).

`preprocess.py` did not add or drop interactions after flattening (`raw_interactions = processed_interactions = 7,953,709` in `results/reports/p0_diagnostic_report.md`).

---

## Unresolved

None for the two manuscript figures (866 KCs; ~7.95M rows). Both are explained by kc_level flattening plus retained `-1` padding, not by an unexplained recount.

Residual (not required to keep Table 1): we did not re-derive the official **5,549,635** question-level total from `questions.json` plus a question-level log, because this pipeline never built a question-level table. That official total is cited from `[20]`, not recomputed here.

---

## Action for the IJIET manuscript

- **Do not change** Table 1 cells 866 or 7.95M.
- **Do state** that Table 1 is post-processing, and that XES3G5M counts are kc_level-expanded rows including padding token `-1`.
