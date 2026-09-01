# CHANGELOG A5

**Loại nhiệm vụ:** CPU + interpretation (chạy sau A4)

**Phụ thuộc đã thỏa:** A4 outputs (`kc_characteristics.csv`, `spearman_correlations.csv`, `matched_analysis.csv`, `calibration_gradient_summary.csv`) tồn tại và được tái sử dụng. Không train lại model.

**File mới:**
- `scripts/a5_dataset_diagnostic_profile.py` — script tái lập được
- `analysis/dataset_sparse_diagnostic_profile.csv` — hồ sơ chẩn đoán 3 dataset
- `analysis/a5_condition_verdicts.csv` — 6 điều kiện × 3 dataset
- `analysis/table_a5_dataset_conditions.tex` — bảng nguồn
- `analysis/a5_manuscript_subsection.tex` — bản thảo subsection
- `REV_REVIEWER_CALIBRATION_v1/tables/table_12_dataset_conditions.tex`
- `CHANGELOG_A5.md` (file này)

**File sửa:**
- `REV_REVIEWER_CALIBRATION_v1/sections/05_discussion_limitations.tex` — thêm subsection “Why Sparse-Concept Calibration Vulnerability Is Dataset-Dependent”; cập nhật External Validity
- `REV_REVIEWER_CALIBRATION_v1/sections/06_conclusion.tex` — heterogeneity gắn với điều kiện đo được
- `REV_REVIEWER_CALIBRATION_v1/appendix/appendix_a_sensitivity.tex` — nạp Table 12 (tránh đẩy số bảng chính)

---

## Cột hồ sơ chẩn đoán (CSV)

`total_kcs`; `proportion_*` (strict / very sparse / sparse / medium / dense); `interaction_concentration` (top-1, top-10%, Herfindahl); `median_train_frequency`; `frequency_iqr`; `kc_difficulty_*`; `items_per_kc_*`; `learners_per_kc_*`; `curriculum_position_*`; `strict_cold_start_*` (KC share + test-event mass); `test_events_*` theo stratum; `calibration_frequency_association_strength`.

Thêm coupling: `freq_difficulty_rho`, `freq_curriculum_rho`, `freq_items_rho`.

---

## FINDING đã kiểm chứng (không suy diễn)

| Dataset | Sparse mass | Test support | Freq–difficulty | Curriculum-pos. | SimpleKT ECE gradient |
|---------|-------------|--------------|-----------------|-----------------|------------------------|
| ASSISTments 2012 | 18.9% | Partial (N=403 L) | ρ=−0.227 (sparse harder) | ρ=−0.308 | 0.113 → 0.158 → 0.225 |
| Junyi Academy | 0.0% | Absent | ρ=−0.416 | ρ=−0.324 | chỉ dense→medium (+0.031) |
| XES3G5M | 22.5% | Present (N=2,002 R) | ρ=+0.087 (yếu, ngược dấu) | ρ=−0.125 (yếu) | phẳng 0.115 → 0.112 → 0.124 |

Điểm then chốt cho reviewer:
- Junyi không “an toàn hơn”: median $f_{\mathrm{train}}=7074$ đẩy 97.5% KC vào dense. Temporal split vẫn tạo 10 KC sparse-like (ECE 0.1624 vs dense 0.0889).
- XES3G5M không thiếu sparse mass hay N: pattern phẳng/inverted **không** phải do bucket rỗng. IRT inverted, DKT tăng — gradient phụ thuộc model.
- ρ=+0.087 **không** được viết thành “sparse KCs are easier” (bản A5 cũ mắc lỗi này).

Item-support dense vs sparse (205 vs 1) được ghi là **một phần cơ học** (KC $f<100$ không thể có hàng trăm item). Contrast không cơ học: median items/KC 44.5 / 18 / 3; freq–item ρ = 0.92 / 0.03 / 0.83.

---

## HYPOTHESIS (không nâng thành FINDING)

- Ontology KC thô / skill hiếm trên ASSISTments
- Đổi ngưỡng dense (ví dụ $f\ge 2000$) trên Junyi
- Cây KC phân cấp, multi-skill expansion, ceiling, item features trên XES3G5M

---

## Bảng mới

**Table 12.** Dataset conditions associated with observable sparse-KC calibration vulnerability

Hàng: meaningful sparse mass; sufficient test support; frequency–difficulty coupling; curriculum-position coupling; item-support imbalance; observed calibration gradient.

---

## Kết luận điều kiện (không universal)

Gradient SimpleKT quan sát được khi đồng thời: (1) sparse mass khác không; (2) đủ test events (≥ Limited); (3) coupling tần suất–độ khó không đảo chiều.

- ASSISTments: đủ cả ba → gradient đơn điệu
- Junyi learner-based: thiếu (1) và (2) → protocol để trống, không suy ra ổn định
- XES3G5M: đủ (1)(2), thiếu (3) → SimpleKT phẳng; IRT đảo; DKT tăng

Không claim frequency *gây* miscalibration.

---

## Sửa so với bản A5 nháp trước

- ECE dùng **event-level Table 9**, không dùng median KC-level (tránh “inverted” giả tạo ở XES very-sparse 0.0436 vs 0.1951 event-level)
- Sửa diễn giải ρ XES3G5M: +0.087 là yếu/ngược dấu, không phải “negative correlation”
- Bảng 6 hàng đúng spec reviewer, không phải dump mọi số
