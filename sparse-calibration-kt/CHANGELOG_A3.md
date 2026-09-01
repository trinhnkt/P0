# CHANGELOG A3

**File sửa:**
- `REV_REVIEWER_CALIBRATION_v1/main_jedm.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/01_introduction.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/05_discussion_limitations.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/06_conclusion.tex`

**Nội dung sửa:**
- **Abstract (`main_jedm.tex`):** Khẳng định "calibration susceptibility" là điểm yếu mang tính thông tin cao nhất trên các sparse concepts (thay vì AUC degradation). Đồng thời nhấn mạnh hiệu ứng này phụ thuộc vào dataset.
- **Introduction (`01_introduction.tex`):** Sửa Contribution 2 từ việc chỉ mô tả công cụ đánh giá (ECE, Brier) thành đóng góp mang tính thực nghiệm: *characterizing when discrimination and calibration diverge...*
- **Discussion (`05_discussion_limitations.tex`):** Thêm hẳn một subsection có tiêu đề "Calibration, Rather Than AUC, Is the Primary Sparse-Concept Vulnerability". Phân tích chỉ ra dù ở ASSISTments 2012 calibration lỗi nặng dần, nhưng hiện tượng này không mang tính toàn cầu (không xuất hiện ở mọi dataset, ví dụ XES3G5M có counter-patterns).
- **Conclusion (`06_conclusion.tex`):** Phân định rạch ròi 3 ý: predictive heterogeneity (sự khác biệt trong AUC), calibration susceptibility (sự suy yếu của calibration), và dataset dependency (phụ thuộc vào bộ dữ liệu). Định vị lại finding mạnh nhất là calibration susceptibility.

**Phân tích mới:**
- Tạo file `analysis/calibration_gradient_summary.csv`, trích xuất toàn bộ dữ liệu calibration (ECE, REL, Brier, Events) từ Table 9 và 10 cho cả hai loại split (learner-based và temporal). Dữ liệu này chứng minh được "calibration gradient" ở ASSISTments 2012 và các counter-examples.

**Kết quả:**
- Paper đã dịch chuyển trọng tâm từ "universal AUC degradation" sang "dataset-dependent calibration vulnerability". Người đọc sẽ thấy rõ finding mạnh nhất là sự dễ bị tổn thương về độ tin cậy xác suất của các mô hình trên dữ liệu thưa, chứ không phải sự giảm điểm AUC thông thường.

**Nội dung chưa đủ evidence:**
- Không có. (Tất cả xu hướng diễn giải đều lấy từ số liệu đã ghi nhận ở Table 9/10).

**Đề xuất bước tiếp theo:**
- Chờ yêu cầu tiếp theo (nếu có). Trọng tâm của paper đã được thay đổi triệt để và an toàn.
