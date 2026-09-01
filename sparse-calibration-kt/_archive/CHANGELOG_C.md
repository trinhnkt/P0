# CHANGELOG Direction C

**Loại nhiệm vụ:** Phân tích trên CSV có sẵn. Không train lại. Chưa sửa bản thảo TeX.

**Mục tiêu:** C4 qualitative → sai số quyết định giả lập với ngưỡng \(\tau\) toàn cục.

---

## File mới

- `analysis/direction_c_preregister.md` — khóa trước khi đọc đường \(\tau\)
- `scripts/c_threshold_simulate.py`
- `analysis/direction_c/threshold_rates.csv`
- `analysis/direction_c/sparse_dense_gaps.csv`
- `analysis/direction_c/c1_c3_verdict.txt`
- `analysis/direction_c/table_c_tau07.tex`

---

## Kết quả khóa (không retune C3)

- **C1 PASS** (ASSISTments SimpleKT, \(\tau=0.7\)): \(\Delta\)FM \(=+0.072\) (0.268 sparse vs 0.196 dense). \(\Delta\)Miss âm — co-primary là FM.
- **C2 PASS:** GKT train-only \(\Delta\)FM \(=+0.015\) < SimpleKT \(0.072\).
- **C3 FAIL:** Junyi sparse empty (đúng); XES \(|\Delta\)Miss\(|\) lớn hơn ASSISTments. ECE phẳng ≠ Miss phẳng. Không nới C3 sau khi thấy số.

IRT 1PL: \(\bar p \approx 0.696\), không advance ở \(\tau\ge 0.7\) — không đưa vào bảng chính.

- `analysis/direction_c/fivefold_gaps.csv`, `seed42_bootstrap_dfm.csv`, `c2_fivefold_verdict.txt`
- `scripts/c_threshold_multifold.py`
- `tables/table_19_threshold_fivefold.tex`

SimpleKT ASSISTments $\Delta$FM at $\tau=0.7$: mean $0.047$ (sd $0.033$), **5/5** folds positive. Seed-42 KC-cluster CI $[0.006, 0.138]$. DKT only 3/5 --- not a five-fold finding. GKT/CL4KT remain seed 42.

---

## Four-partition recount of Tables 3/5/9 (2026-08-26)

Seeds 2025 and 2026 share one student split. Learner-based mean±sd is now over **four unique partitions** (average the two inits first). Frequency buckets use each fold's train-only \(f_{\mathrm{train}}\).

Finding 2 **holds**: SimpleKT ASSISTments ECE \(0.1136\pm0.0066\) (dense) → \(0.1541\) (medium) → \(0.2280\pm0.0197\) (sparse, Limited, \(N=415\)). Naive five-run fold-specific recompute was \(0.1131 / 0.1553 / 0.2250\), \(N=413\).

Script: `scripts/recompute_four_partition_summaries.py`. Outputs: `analysis/four_partition/`.

