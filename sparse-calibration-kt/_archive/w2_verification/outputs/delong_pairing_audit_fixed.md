# DeLong Pairing Audit (Fixed version)

## Phương pháp Pairing mới (Kịch bản C được giải quyết)
Trong kịch bản C, việc pair 2 file output của mô hình dựa theo `row_order` hoặc dựa theo khóa định danh `user_id_item_id_timestamp` đã dẫn đến việc mất mát sự kiện do có nhiều KCs giải quyết đồng thời trong một item.

Bằng cách sử dụng **stable instance_id** định nghĩa bởi:
`instance_id = user_id + '_' + item_id + '_' + timestamp + '_' + kc_id + '_' + cumcount()`
Chúng ta đã đảm bảo **không có bất kỳ dòng dữ liệu nào bị drop**, bảo toàn 100% test dataset (Intersection N = C1 = C3).

## Kết quả DeLong Test (Fold 0 / Seed 42)

### 1. ASSISTments 2012
- Intersection $N$: 534,150
- AUC DKT: 0.6989
- AUC SimpleKT: 0.6837
- p-value: $7.10 \times 10^{-82}$ (Significant)

### 2. Junyi Academy
- Intersection $N$: 3,269,022
- AUC DKT: 0.7326
- AUC SimpleKT: 0.7261
- p-value: $8.07 \times 10^{-144}$ (Significant)

### 3. XES3G5M
- Intersection $N$: 1,589,145
- AUC DKT: 0.9176
- AUC SimpleKT: 0.8889
- p-value: $0.0$ (Significant)

**Kết luận:** Phương pháp pairing mới đã phục hồi lại 30% dữ liệu bị mất cho tập XES3G5M. Các kết luận về sự chênh lệch (DKT tốt hơn SimpleKT với ý nghĩa thống kê) vẫn không thay đổi, tuy nhiên AUC trên tập Intersection giờ đây đã chính xác hơn và phản ánh đúng 100% dữ liệu kiểm thử.
