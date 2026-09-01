# Kiểm toán nguồn gốc C4 (W2 Verification)

## 1. Nguồn gốc của con số 531,127 (Báo cáo W2 hiện tại)
- **Nguồn:** Tính toán trung bình (`.mean()`) trực tiếp từ file `results/tables/clean_metric_per_bucket.csv` (Timestamp: `2026-07-01 17:05:51.690462`).
- **Nguyên nhân:** File `clean_metric_per_bucket.csv` đang lưu trữ bị trùng lặp kết quả của nhiều lượt chạy (đặc biệt `seed 42` bị ghi nhiều lần mà không ghi đè). Việc chạy `pandas.groupby('bucket')['n_events'].mean()` trên file này cho DKT đã sinh ra giá trị trung bình sai lệch là `531,127`.

## 2. Nguồn gốc của con số 530,032 (Table 5 PDF)
- **Nguồn:** Tính toán trực tiếp trên các file `results/predictions/*_rerun.csv` thông qua script `make_updated_latex_tables.py`.
- **Nguyên nhân khớp hoàn toàn giữa IRT, DKT và SimpleKT:** 
  Cả 3 mô hình đều dự đoán trên cùng một tập test của PyKT (đã được lọc `-1` và `nan`). Khi merge với `kc_strata.csv` (`how='inner'`), tất cả các mô hình đều bị drop chính xác cùng một số lượng dòng. 
  Do đó, sau khi gom nhóm theo bucket và tính trung bình qua 5 seeds, cả 3 mô hình đều cho ra **chính xác 530,032 events** (trong đó `dense` là 523,395). Không có lỗi rò rỉ biến (variable leakage) nào ở đây; các mô hình thực sự có số lượng events hợp lệ khớp nhau đến từng unit!

**Kết luận:** Số liệu 530,032 trong Table 5 PDF là **hoàn toàn chính xác và nhất quán** cho cả 3 mô hình. Con số 531,127 trong bảng báo cáo cũ của chúng ta bị sai do đọc từ file CSV rác (`clean_metric_per_bucket.csv` chứa duplicate logs).
