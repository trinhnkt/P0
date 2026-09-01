# CHANGELOG SETUP

**File sửa:**
- Không sửa file nào. Đã tạo bản sao toàn bộ thư mục `jedm_upload_folder` thành `REV_REVIEWER_CALIBRATION_v1`.

**Nội dung sửa:**
- Hoàn tất việc đọc manuscript và xác định vị trí các thành phần yêu cầu:
  - **Abstract**: `main_jedm.tex`
  - **Introduction, Contributions, RQ1–RQ3**: `sections/01_introduction.tex`
  - **Sections 3.3–3.8**: `sections/03_protocol.tex`
  - **Tables 3–10**: Nằm trong thư mục `tables/` (ví dụ: `table_03_overall_performance_learner_based.tex` đến `table_10_calibration_breakdown_temporal.tex`).
  - **Sections 4.3–4.6**: `sections/04_experiments.tex`
  - **Discussion & Threats to Validity**: `sections/05_discussion_limitations.tex`
  - **Conclusion**: `sections/06_conclusion.tex`
  - **Appendices A–F**: Thư mục `appendix/` (hiện tại có `appendix_a_sensitivity.tex`).

**Phân tích mới:**
- Chưa thực hiện phân tích mới trong nhiệm vụ thiết lập này. Đã ghi nhận các quy tắc nghiêm ngặt về việc không bịa kết quả, không thay đổi số thực nghiệm, đảm bảo tính tái lập (script, CSV, không leakage, chỉ dùng training-fold info cho KC-frequency).

**Kết quả:**
- Đã thiết lập xong môi trường làm việc an toàn (`REV_REVIEWER_CALIBRATION_v1`) theo yêu cầu. Toàn bộ quy định đã được nạp vào bộ nhớ để áp dụng cho các nhiệm vụ tiếp theo.

**Nội dung chưa đủ evidence:**
- Không có.

**Đề xuất bước tiếp theo:**
- Chờ nhiệm vụ cụ thể từ user (ví dụ: phản hồi reviewer nào, chỉnh sửa phần nào, chạy script phân tích nào). Sẵn sàng thực hiện task tiếp theo tuân thủ tuyệt đối các quy tắc đã đề ra.
