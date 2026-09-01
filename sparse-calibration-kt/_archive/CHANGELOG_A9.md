# CHANGELOG A9

**Loại nhiệm vụ:** GPU RERUN + manuscript. Protocol chọn KC được ghi *trước* khi xem ECE reduced.

**Câu hỏi:** What happens to calibration when evidence is reduced for the same concept?

---

## File mới

- `controlled_sparsification_protocol.md`
- `scripts/a9_select_and_downsample.py`
- `scripts/a9_train.py`
- `scripts/a9_run_assist_queue.py`
- `scripts/a9_analyze.py`
- `analysis/a9/selected_kcs.csv`, `kc_eligibility.csv`
- `analysis/a9/manifests/downsample_plan.csv`
- `data/processed/a9/{assist2012,junyi,xes3g5m}/t{500,100,50}/...` (train copies; val/test copied)
- `results/predictions/a9_{assist2012,junyi,xes3g5m}_learner_based_{dkt,simplekt}_t{500,100,50}_seed42.csv`
- `analysis/a9_kc_metrics.csv`, `a9_sparsification_results.csv`, `a9_statistical_summary.csv`
- `REV_REVIEWER_CALIBRATION_v1/tables/table_16_sparsification.tex`
- `REV_REVIEWER_CALIBRATION_v1/figures/a9_ece_rel_vs_evidence.pdf`
- `CHANGELOG_A9.md` (file này)

Official `train.csv` / prediction CSV **không** bị ghi đè.

---

## GPU đã chạy

ASSISTments 2012, Junyi Academy, XES3G5M: learner-based fold 0, seed 42, DKT + SimpleKT, levels 500 / 100 / 50. Official prediction CSVs were not overwritten. Early-stop patience 10.

---

## Selection (không dùng ECE)

Eligible: $f_{\mathrm{train}}\ge 500$, $N_{\mathrm{test}}\ge 100$, $\ge 20$ pos và 20 neg.  
Nếu >30 KC: 10/tertile difficulty (train-only), sort `kc_id`.  
Cả 3 dataset: 30 KC, 10+10+10 tertiles.

---

## Kết quả chính (within-KC ΔECE, bootstrap 95% CI)

Positive Δ = ECE *xấu hơn* khi giảm evidence. Không phải dose–response universal.

**ASSISTments 2012:** DKT t500 **−0.047** [−0.060, −0.033]; t100 **−0.024**; t50 CI gồm 0. SimpleKT t500 **−0.026**; t100/t50 ≈ 0.

**Junyi Academy:** DKT t500 **−0.021**; t100/t50 CI gồm 0. SimpleKT **+0.101 / +0.132 / +0.135** (93–100% KC xấu hơn).

**XES3G5M:** DKT chỉ t50 **+0.018**. SimpleKT t100 **+0.015**, t50 **+0.032**.

AUC giảm ở mọi cell (ASSISTments DKT 0.690→0.627; SimpleKT 0.679→0.607 full→50).

---

## Diễn giải (không causal quá mức)

Within-KC ECE increase after reducing training rows is **dataset- and model-dependent**.

Observational ASSISTments dense→sparse SimpleKT ECE (0.113→0.225) **không** được tái tạo bằng cách sparsify cùng các KC dense đó.

Junyi SimpleKT **có** tăng ECE trong-KC khi giảm evidence cho cùng KC dense.

Không nói: “real-world sparsity always causes miscalibration.”

Giới hạn: 1 seed; 100% control là published run (50 epoch), A9 reduced dùng early stopping.

---

## Manuscript

- `05_discussion_limitations.tex` — A4 summary + subsection Controlled Reduction…
- `appendix_a_sensitivity.tex` — `app:a9_sparsify`
- `06_conclusion.tex` — không đọc observational gradient như frequency dose–response
