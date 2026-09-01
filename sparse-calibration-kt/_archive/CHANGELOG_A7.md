# CHANGELOG A7

**Loại nhiệm vụ:** CPU + manuscript revision. Không GPU.

**Mục tiêu:** Biến L8 từ một case study bắt bug thành một cơ chế predictive-sanity được đánh giá bằng fault injection có kiểm soát.

**Ràng buộc đã giữ:**
- Không ghi đè prediction CSV gốc. Fault chỉ trên bản sao trong bộ nhớ.
- Threshold không được chọn hậu nghiệm để làm đẹp detection rate.
- Không viết “L8 phát hiện mọi bug.”

---

## File mới

- `scripts/a7_l8_fault_injection.py` — fault injection + signals + table/figure
- `analysis/l8_fault_injection_results.csv` — hàng kết quả theo file × fault
- `analysis/l8_fault_injection_summary.csv` — detection rate tổng
- `analysis/table_a7_l8_fault_injection.tex`
- `analysis/l8_fault_injection_detection_curve.pdf`
- `analysis/a7_manuscript_subsection.tex`
- `REV_REVIEWER_CALIBRATION_v1/tables/table_13_l8_fault_injection.tex`
- `REV_REVIEWER_CALIBRATION_v1/figures/l8_fault_injection_detection_curve.pdf`
- `CHANGELOG_A7.md` (file này)

## File sửa (REV_REVIEWER_CALIBRATION_v1)

- `sections/01_introduction.tex` — Contribution 3 + fault injection
- `sections/03_protocol.tex` — L8 trỏ tới Appendix fault injection
- `sections/04_experiments.tex` — đoạn Results sau case L8
- `sections/05_discussion_limitations.tex` — reviewing community + Temporal Alignment Validity
- `sections/06_conclusion.tex` — L8 = case + validation, không phải detector phổ quát
- `tables/table1_leakage_audit.tex` — cột Empirical demonstration
- `appendix/appendix_a_sensitivity.tex` — subsection “Controlled Fault Injection…”

Chạy lại: `python scripts/a7_l8_fault_injection.py`  
Chỉ relabel detection từ CSV đã có: `python scripts/a7_l8_fault_injection.py --relabel-only`

---

## Detection rule (validation experiment)

Không pre-register cho phân tích chính. Dùng:

- warm AUC < 0.55; **hoặc**
- warm AUC + 0.05 < IRT warm AUC (pipeline sạch); **hoặc**
- corr(p, y) ≤ 0; **hoặc**
- E[p | y=1] − E[p | y=0] ≤ 0; **hoặc**
- identity_mismatch_rate > clean_identity + 0.01

Mệnh đề identity dùng *reference từ đúng file sạch* (Junyi có ~0.9% va chạm ID tự nhiên). Không tinh chỉnh trên F1–F6.

---

## Detection rate

| Điều kiện | Detected |
|-----------|----------|
| Clean (false-positive) | 0/6 |
| F1 label shift +1 | 6/6 (identity) |
| F2 label shift −1 | 6/6 (identity) |
| F3 prediction shift | 0/6 |
| F4 within-learner shuffle | 2/6 (chỉ XES, collapse vs IRT) |
| F5 row-index mismatch | 6/6 (AUC ~0.50) |
| F6 1 / 5 / 10 / 25% | 0/6 |
| F6 50% | 3/6 |
| **Tất cả fault đã inject** | **23/60 (38.3%)** |

F1/F2 không làm sụp AUC vì chuỗi learner tự tương quan (SimpleKT ASSISTments F2 thậm chí AUC 0.81). F3 giữ y và ID nên identity không cháy. Đây là giới hạn đã báo, không phải failure bị giấu.

---

## Câu cho reviewer

Contribution 3 không còn chỉ một anecdotal catch. L8 được đánh giá trên sáu lớp fault có kiểm soát. Bài báo nói rõ: L8 *nhạy với một số fault class đã kiểm tra* (label-identity shift; global row-index mismatch) và *không nhạy* với adjacent-timestep prediction shift. Không claim L8 bắt mọi bug.
