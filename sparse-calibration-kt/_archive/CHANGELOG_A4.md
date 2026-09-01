# CHANGELOG A4

**Loại nhiệm vụ:** CPU / statistical analysis / manuscript revision

**File sửa:**
- `REV_REVIEWER_CALIBRATION_v1/sections/05_discussion_limitations.tex`

**File mới tạo:**
- `scripts/a4_confounding_analysis.py` — script phân tích confounding (tái lập được)
- `analysis/kc_characteristics.csv` — KC-level characteristics table (training-only covariates + test metrics)
- `analysis/spearman_correlations.csv` — Univariate Spearman correlations với bootstrap 95% CI
- `analysis/regression_results.csv` — Multivariable regression coefficients (weighted + unweighted)
- `analysis/matched_analysis.csv` — Matched analysis within difficulty tertiles
- `analysis/table_a4_regression.tex` — LaTeX regression table (optional appendix)
- `analysis/a4_manuscript_subsection.tex` — Auto-generated manuscript subsection

---

**Kết quả phân tích thực tế:**

### Univariate Spearman (log_train_freq ↔ ECE)
| Dataset | mean ρ | Strength | Significant |
|---------|--------|----------|-------------|
| ASSISTments 2012 | -0.60 | Strong | 3/3 models |
| Junyi Academy | -0.43 | Moderate | 3/3 models |
| XES3G5M | -0.23 | Weak | 3/3 models |

Difficulty proxy cũng có tương quan dương với ECE (rho ∈ [0.19, 0.48]).

### Multivariable Regression (SimpleKT, weighted by test events)
Sau khi kiểm soát difficulty, curriculum position, n_items, n_learners:
- **ASSISTments 2012**: log_train_freq còn **độc lập** (β = -0.079, p < 0.001)
- **Junyi Academy**: log_train_freq còn **độc lập** (β = -0.010, p < 0.001)
- **XES3G5M**: log_train_freq còn **độc lập trong mô hình weighted** (β = -0.117, p < 0.001), nhưng attenuation trong unweighted (p = 0.18) → hiệu ứng phụ thuộc vào high-event KCs

### Matched Analysis (trong cùng difficulty tertile)
- 8/9 stratum comparisons có ECE(low-freq) > ECE(high-freq) ở mức p < 0.05
- Xác nhận association không phải artifact của difficulty

**Tóm tắt:**
- Reviewer concern về confounding đã được trả lời: frequency retains independent association sau adjustment
- Tuy nhiên difficulty cũng là factor độc lập → multi-factorial
- Wording trong manuscript: "independently associated with calibration degradation after adjustment" (KHÔNG dùng "causes")
- XES3G5M cho thấy sự phụ thuộc vào high-event KCs → reinforces "dataset-dependent" narrative

**Nguyên tắc không leakage:**
- Tất cả covariates đều từ training split
- Test labels chỉ dùng để tính ECE/Brier outcome (không phải explanatory variable)
- Bucket assignment cũng từ train_freq

**Đề xuất bước tiếp theo:**
- Nếu có yêu cầu, bảng `analysis/table_a4_regression.tex` có thể thêm vào Appendix bản thảo
- Chờ task tiếp theo (A5 hoặc yêu cầu khác)
