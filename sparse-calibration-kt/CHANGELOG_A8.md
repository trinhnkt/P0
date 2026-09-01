# CHANGELOG A8

**Loại nhiệm vụ:** CPU + synthesis + manuscript revision (chạy sau A4/A5)

**Mục tiêu:** Conditional-use framework — không nói mọi KT dataset đều cần sparse-concept diagnostics với cùng cường độ.

---

## File mới

- `scripts/a8_diagnostic_need.py`
- `analysis/a8_diagnostic_need_matrix.csv` — C1–C5 × Low / Moderate / High
- `analysis/a8_dataset_need_ratings.csv` — áp vào 3 dataset
- `analysis/table_a8_need_framework.tex`
- `analysis/table_a8_dataset_need.tex`
- `analysis/a8_manuscript_subsection.tex`
- `REV_REVIEWER_CALIBRATION_v1/tables/table_14_need_framework.tex`
- `REV_REVIEWER_CALIBRATION_v1/tables/table_15_dataset_need.tex`
- `CHANGELOG_A8.md` (file này)

## File sửa (REV_REVIEWER_CALIBRATION_v1)

- `sections/01_introduction.tex` — RQ3 mới; cold-start thành RQ4
- `sections/04_experiments.tex` — RQ3 Explanatory Conditions; RQ4 cold-start
- `sections/05_discussion_limitations.tex` — subsection “When Are Sparse-Concept Diagnostics Necessary?”
- `sections/06_conclusion.tex` — câu điều kiện
- `main_jedm.tex` / `main_jedm_anonymous.tex` — abstract
- `appendix/appendix_a_sensitivity.tex` — nạp Table 14–15

Chạy: `python scripts/a8_diagnostic_need.py`

---

## Framework (không bịa cutoff mới)

| Condition | Nguồn mức Low/Mod/High |
|-----------|------------------------|
| C1 Sparse mass | Ngưỡng protocol đã đăng ký $f_{\mathrm{train}}<100$ |
| C2 Evaluation support | Cờ R/L/I sẵn có ($N\ge 1000$ / $100$–$999$ / $<100$) |
| C3 Calibration susceptibility | Định tính trên ECE Table 9 + $\bar\rho$ A4 |
| C4 Deployment relevance | Intended use; **không** ước lượng từ log |
| C5 Temporal / cold-start | Occupancy Table 6; không cutoff KC-count mới |

---

## Áp vào ba dataset

| | C1 | C2 | C3 | C4 | C5 | Overall |
|--|----|----|----|----|----|---------|
| ASSISTments | High (18.9%) | Moderate ($N=403$ L) | High (ECE $0.113\to0.225$) | Use-dependent | Moderate (27 strict KCs) | **High** |
| Junyi | Low (0%) | Low (empty) | Moderate (dense→medium only) | Use-dependent | Moderate (4 strict KCs; 10 temporal sparse-like) | **Low (learner-based); Moderate (temporal)** |
| XES3G5M | High (22.5%) | High ($N=2002$ R) | Moderate (SimpleKT flat; model-heterogeneous) | Use-dependent | High (117 KCs / 233k events) | **High reporting; Moderate SimpleKT gradient** |

Need ≠ vulnerability: XES vẫn *cần* chạy diagnostics để thấy pattern phẳng/đảo, không phải để khẳng định ECE tăng như ASSISTments.

---

## Câu trả lời reviewer

> Sparse diagnostics are most informative when a dataset contains a meaningful low-frequency tail, those strata have sufficient evaluation support, and calibration reliability varies systematically with training evidence or deployment involves concept cold-start.

Hai lớp:
- **Universally useful reporting hygiene:** occupancy, empty buckets, R/L/I.
- **Empirically high-priority sparse diagnostics:** khi C1+C2 và (C3 hoặc C5), cộng C4 nếu xác suất bị threshold.

---

## RQ

- RQ1, RQ2 giữ nguyên
- **RQ3 (Explanatory Conditions):** Under what dataset and concept conditions is lower training frequency associated with meaningful calibration degradation?
- RQ3 cũ → **RQ4** Limited Cold-start Concept Diagnostics
