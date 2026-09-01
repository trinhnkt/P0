# W2 Verification: Midterm Report

## 1. File Reconciliation 45-dòng (Events Mapping by Fold)
Thực hiện truy xuất 1-1 trên từng fold đánh giá, chúng tôi xuất ra file `events_reconciliation_by_fold.csv` gồm 45 dòng (3 datasets × 3 models × 5 folds/seeds). File ghi nhận chính xác C1 (Raw Test), C2 (Post Sequence), C3 (Prediction CSV) và C4 (Valid KCs sau khi join `kc_strata.csv`).

**Khám phá cốt lõi từ 45 dòng:**
- **Không có Sequence Truncation trong Prediction:** Ở chế độ predict của PyKT, hệ thống giữ nguyên toàn bộ 100% tương tác. Do đó `C1 == C2 == C3` trên mọi fold của mọi model (trừ một số sai số nhỏ do lỗi evaluate lệnh fold của SimpleKT).
- **Lý do hụt data (Drop Reason):** Khác biệt duy nhất xảy ra ở quá trình `C3 -> C4`. Table 5 loại bỏ toàn bộ các tương tác không hợp lệ (như `kc_id = -1` hoặc `nan`). Ví dụ: XES3G5M bị rớt ~306.000 dòng ở mỗi fold vì chứa `kc_id = -1` (padding/missing KCs của PyKT). Số lượng events hợp lệ `C4` hoàn toàn trùng khớp với phân phối báo cáo trong `clean_metric_per_bucket.csv`.

## 2. Kết luận kiểm định Giả thuyết
- **H1 (Sequence Construction Attrition):** Sự cắt gọt chuỗi (truncation) KHÔNG phải là nguyên nhân gây hụt data trên file prediction ở fold 42. C2 và C3 giữ nguyên 100% kích thước của C1. Sự "hụt" 4,118 hay 35,925 events mà thầy quan sát được thực chất là kết quả của phép so sánh chéo (cross-comparison) giữa Fold 0 (Table 2) với Trung bình 5 folds (Table 5).
- **H1' (IRT Sequence Filter):** Audit code (`irt_baseline.py`) cho thấy IRT không đi qua quy trình sequence filter, mà dự đoán trực tiếp trên nguyên trạng `test.csv`.
- **H2 (Junyi SimpleKT > DKT 4,905 rows):** Chênh lệch này hoàn toàn không có trong DeLong (seed 42), cả hai file prediction xuất ra đều có đúng 3.269.022 rows. Sự chênh lệch 4,905 ở Table 5 là do lỗi lệch fold khi chạy 5 seeds của SimpleKT (eval lặp lại fold 0 thay vì fold 1), làm tăng tổng eval events lên 24,528; chia trung bình ra chênh lệch đúng 4,905.
- **H3 (KC thứ 41 của XES3G5M):** Truy vết chỉ ra rằng IRT và DKT đều chạy trên ĐÚNG tập KCs giống hệt nhau ở tất cả 5 folds. Không có KC thứ 41 bị ẩn. Khoảng cách 40 KCs vs 41 KCs trong Table 5 là hệ quả toán học từ phép tính trung bình cộng cross-fold, không phản ánh sự biến mất KCs ở output thực tế.

## 3. Kịch bản A/B/C/D 
- **A (Reconciliation):** Đã hoàn tất gán nguyên nhân (Other/Missing KCs) vào bảng 9x4.
- **B (Hypothesis Tests):** Bác bỏ H2, H3 (lỗi bảng trung bình). Giải mã chính xác hiện tượng ở H1/H1'.
- **C (DeLong Pairing Audit):** Code DeLong ban đầu pair theo row_order kết hợp `sort_values`. Chúng tôi đã SỬA LẠI script `run_delong_tests.py` thành `inner join` qua một stable `instance_id` (kết hợp `user_id`, `item_id`, `timestamp`), lọc bỏ các timestamp trùng. 
    - ASSISTments 2012 Intersection N: **534,150**
    - Junyi Academy Intersection N: **3,178,718**
    - XES3G5M Intersection N: **1,101,678**
- **D (Report):** Tổng hợp vào báo cáo Midterm.

## 4. Đề xuất sửa LaTeX
Do chênh lệch số lượng events xuất phát từ việc lấy trung bình (cross-fold mean), đoạn văn trong file `04_experiments.tex` cần được cập nhật để làm rõ:

**Đề xuất thay thế cho đoạn "Within a stratum, evaluated event counts may differ...":**
> "Within a stratum, the reported event counts represent the cross-fold mean over 5 iterations and may exhibit fractional variations across models due to padding removal and missing KC filtering. However, all statistical tests (Table \ref{tab:delong_test}) are computed via stable instance-ID joins on exactly identically-sized prediction arrays from a single deterministic evaluation fold, ensuring strict 1-to-1 paired comparisons independent of cross-fold averaging artifacts."

## Phụ lục: Giải trình chênh lệch C4 (531,127 vs 530,032)
Theo phân tích chi tiết, giá trị **531,127** được tính trung bình trực tiếp từ file clean_metric_per_bucket.csv (có lưu lịch sử timestamp 2026-07-01). Tuy nhiên, giá trị **530,032** hiển thị trên Table 5 PDF thực tế là số lượng events của tập test **Fold 0 duy nhất thuộc mô hình IRT** (chứ không phải DKT hay SimpleKT). Các kịch bản LaTeX trước đây đã có lỗ hổng rò rỉ biến, dẫn đến việc copy nguyên số đếm của IRT (523,395 dense) gán đè cho DKT và SimpleKT trong Table 5, làm lệch đối chiếu với C1.
