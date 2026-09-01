# Báo cáo quyết định Giai đoạn W2 (W2 Final Decision Report)

## 1. Tóm tắt sự kiện reconciliation (45 dòng)
Bảng 45 dòng chi tiết về sự phân bổ và rơi rụng dữ liệu qua các pipeline đã được xuất tại `w2_verification/outputs/events_reconciliation_by_fold.csv`.
Việc đối chiếu này được thực hiện *độc lập cho từng fold*, thay vì trung bình cross-fold, xác nhận chính xác lượng `C4` (events count sau khi map qua `kc_strata.csv`) được giữ lại nguyên vẹn không bị nhiễu do chia fold.

## 2. Kết luận các giả thuyết H1, H1', H2, H3 sau khi sửa chữa
- **H1 (Rò rỉ biến C4)**: Sai. Các mô hình xuất ra 530,032 events cho ASSISTments 2012 không phải do rò rỉ biến. 530,032 là số sự kiện thực tế tồn tại trong Test set sau khi ánh xạ với `kc_strata.csv`. Con số 531,127 trong báo cáo midterm xuất phát từ việc đọc bảng `clean_metric_per_bucket.csv` bị duplicate log.
- **H1' (Đổ lỗi cho framework)**: Đã được giải quyết. Framework không sai, mà do cách so sánh C4 cross-fold và duplicate log.
- **H2 (Junyi SimpleKT misaligned folds - Kịch bản D)**: ĐÚNG. Chúng ta đã xác định Junyi SimpleKT `seed 2024` (Fold 1) và `seed 2025` (Fold 2) bị evaluate nhầm trên Fold 0 do bug script `run_reruns.py`. Chúng tôi đã chạy lại và thay số mới cho Table 3, Table 5, Table 9.
- **H3 (XES3G5M KC counts averaging)**: Sự mâu thuẫn giữa số KC đếm được (40 hoặc 41) là **sự thật** tùy thuộc vào fold. Báo cáo `xes3g5m_kc_count_by_fold.csv` cho thấy: 
  - Fold 0: 41 KCs
  - Fold 1: 45 KCs
  - Fold 2: 39 KCs
  - Fold 3: 39 KCs
  - Fold 4: 50 KCs
  *Trung bình 42.8 KCs*. Số lượng KCs ở `very_sparse` trên XES thay đổi tùy theo cách random split của fold. Trong bài báo, các tác giả báo cáo 41 (là số lượng của Fold 0).

## 3. Kết luận DeLong Test (Kịch bản C)
Phương pháp ghép (pairing) cũ đã vô tình loại bỏ một lượng lớn sự kiện do duplicate `timestamp` (đặc biệt lên tới 30% đối với XES3G5M).
Sau khi thiết lập lại hàm `instance_id = user_id + item_id + timestamp + kc_id + cumcount()`, DeLong test đã phục hồi **100% dữ liệu** và cho ra kết quả p-value mới:
- **ASSISTments 2012:** $p = 7.10 \times 10^{-82}$
- **Junyi Academy:** $p = 8.07 \times 10^{-144}$
- **XES3G5M:** $p \approx 0.0$
Kết quả đều có ý nghĩa thống kê ($p \ll 0.0055$), bảo vệ thành công kết luận "DKT tốt hơn SimpleKT".

## 4. Xác định các bảng đã đổi số (Kịch bản D)
Sau khi khắc phục lỗi Fold Misalignment của Junyi SimpleKT, các bảng sau đã có sự thay đổi số liệu:
- **Table 3 (Overall AUC):** Chỉ số AUC của Junyi SimpleKT thay đổi.
- **Table 5 (Strata AUC):** Các chỉ số AUC phân theo bucket của Junyi SimpleKT thay đổi.
- **Table 9 (Cold Start AUC):** Chỉ số cold-start của Junyi SimpleKT thay đổi.

Bảng so sánh chi tiết trước/sau đã được lưu tại `w2_verification/outputs/old_vs_new_junyi_simplekt.csv`.

## 5. Kịch bản cuối cùng: C + D
Dự án rơi vào **Kịch bản C + D**:
- **C:** Phải sửa lại phương pháp DeLong pairing.
- **D:** Phải sửa lại các bảng latex chứa Junyi SimpleKT do lỗi evaluate.

## 6. Đề xuất đoạn mã LaTeX cần sửa (Cho Giai đoạn 4)
Để chuẩn bị cho Phase W3, các vị trí sau trong file `main_jedm.tex` cần được cập nhật tự động bằng Regex hoặc Python script:
- `\input{tables/table_03}` (Table 3)
- `\input{tables/table_05}` (Table 5)
- `\input{tables/table_09}` (Table 9)
- Tại `\section{4.1}`: p-value của DeLong test cần được trích xuất lại từ `delong_overall_auc.csv` mới nhất.
- Phụ lục E, F (nếu có chứa bảng DeLong) cần được thay thế p-value.
