# CHANGELOG A1

**File sửa:**
- `REV_REVIEWER_CALIBRATION_v1/main_jedm.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/01_introduction.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/04_experiments.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/06_conclusion.tex`

**Nội dung sửa:**
- **Abstract (`main_jedm.tex`):** Xóa bỏ ý niệm "universal degradation". Thay vào đó, khẳng định predictive performance và calibration error thể hiện "heterogeneous behavior" trên các tập dữ liệu, có tập bị degradation, có tập có xu hướng inverted hoặc phẳng.
- **Introduction (`01_introduction.tex`):** Sửa Contribution 1 để nhấn mạnh "heterogeneous predictive behavior or metric instability". Viết lại câu hỏi nghiên cứu RQ1: *"How does predictive performance vary across KC-frequency strata, and is lower training frequency associated with systematic degradation across datasets?"*
- **Experiments (`04_experiments.tex` - Section 4.3):** Làm rõ rằng Table 5 đóng vai trò descriptive diagnostic evidence. Chỉ ra ASSISTments có partial degradation, Junyi không kích hoạt bucket sparse/very-sparse, và XES3G5M có counter-pattern (inverted trend). Kết luận rõ: *frequency is not a universal predictor of AUC degradation*.
- **Conclusion (`06_conclusion.tex`):** Sửa câu khẳng định về calibration degradation thành xu hướng đa dạng (heterogeneous trends) của cả calibration và predictive performance.

**Phân tích mới:**
- Đã đọc toàn bộ dữ liệu từ Table 5 và xuất ra file CSV `analysis/rq1_stratum_heterogeneity.csv` chứa thông tin chi tiết (Dataset, Model, Stratum, AUC, ACC, NLL, RMSE, #KCs, #Events, Reliability flag) và trend tổng thể để khẳng định luận điểm heterogeneous.

**Kết quả:**
- Manuscript hiện tại không còn ngụ ý hay tuyên bố rằng KC thưa (sparse KCs) universally có AUC thấp hơn. Table 5 được hạ vai trò từ "bằng chứng degradation chung" xuống "bằng chứng diagnostic về sự khác biệt giữa các stratum". Các sửa đổi đã được thực hiện an toàn trên bản sao `REV_REVIEWER_CALIBRATION_v1`.

**Nội dung chưa đủ evidence:**
- Không có (tất cả các nhận định mới đều dựa trên dữ liệu hiện có trong Table 5).

**Đề xuất bước tiếp theo:**
- Chờ review task tiếp theo (A2) để thực hiện. Sẵn sàng xử lý các yêu cầu thay đổi logic và viết code nếu cần.
