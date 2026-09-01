# CHANGELOG A2

**File sửa:**
- `REV_REVIEWER_CALIBRATION_v1/sections/01_introduction.tex`
- `REV_REVIEWER_CALIBRATION_v1/sections/05_discussion_limitations.tex`

**Nội dung sửa:**
- **Introduction:** Bổ sung đoạn làm rõ mục tiêu của protocol không phải là để lựa chọn model mới (model selection) hay lật đổ bảng xếp hạng (leaderboard), mà là để chẩn đoán độ tin cậy (diagnostic of predictive and probabilistic reliability).
- **Discussion:** Thêm giải thích vào phần "For researchers": mặc dù DKT thường vẫn giữ nguyên là model có AUC cao nhất, nhưng protocol giúp phát hiện ra các *diagnostic disagreements* (ví dụ model có AUC cao nhất chưa chắc là model calibrate tốt nhất, như trường hợp của SimpleKT ở stratum medium của ASSISTments 2012).

**Phân tích mới:**
- Tạo file `analysis/model_ranking_by_metric.csv`, tổng hợp model tốt nhất cho từng metric (AUC, ACC, NLL, RMSE, ECE, REL, Brier) trên các stratum và dataset.
- Đã thêm cột `Ranking_Disagreement` để xác định liệu có sự sai khác giữa model dẫn đầu về phân loại (AUC) và model dẫn đầu về calibration (ECE). Phân tích cho thấy không có sự thay đổi model winner một cách phổ quát, nhưng có xuất hiện disagreement ở mặt calibration.

**Kết quả:**
- Manuscript hiện tại không còn overclaim về việc sparse-concept làm thay đổi model selection. Vai trò cốt lõi của bài báo là **diagnostics** đã được định vị chính xác và nhất quán.
- Bảng `Model-ranking agreement` không được thêm vào main paper để tránh làm loãng trọng tâm, theo đúng chiến lược đã được duyệt (không overclaim).

**Nội dung chưa đủ evidence:**
- Không có.

**Đề xuất bước tiếp theo:**
- Chờ nhiệm vụ tiếp theo (nếu có). Toàn bộ nội dung liên quan tới A1 và A2 đã được giải quyết triệt để trong bản `REV_REVIEWER_CALIBRATION_v1`.
