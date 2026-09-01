# CHANGELOG A10

**Loại nhiệm vụ:** Manuscript only (sau A1–A9). Không train lại.

**Mục tiêu:** Narrative không còn dựa trên “sparse concepts universally perform worse.”

---

## Câu reviewer

> Sparse training evidence does not universally degrade discrimination, but it can expose dataset-dependent calibration vulnerability. We characterize the conditions associated with this vulnerability and provide reproducible diagnostics for identifying when it matters.

---

## File sửa (clean manuscript)

- `REV_REVIEWER_CALIBRATION_v1/main_jedm.tex` — abstract
- `REV_REVIEWER_CALIBRATION_v1/main_jedm_anonymous.tex` — abstract (đồng bộ)
- `sections/01_introduction.tex` — gap, 3 contributions, 4 RQs, 6 findings
- `sections/03_protocol.tex` — subsection Explanatory Analyses (A4 + A9)
- `sections/04_experiments.tex` — RQ1 Finding 1; RQ2 Finding 2–3; RQ3 + A9
- `sections/05_discussion_limitations.tex` — tiêu đề calibration; Spearman/regression wording; A8 hygiene
- `sections/06_conclusion.tex` — câu đích + A9 dataset–model cells
- `tables/table_14_need_framework.tex` — occupancy hygiene wording

Title giữ nguyên.

---

## File mới

- `analysis/claim_evidence_matrix.md`
- `REVISION_SUMMARY.md`
- `CHANGELOG_A10.md` (file này)
- `REV_REVIEWER_CALIBRATION_v1/_pre_a10/` — snapshot trước A10
- `REV_REVIEWER_CALIBRATION_v1/A10_redline/` — unified diffs (latexdiff cần Perl; máy này chưa có)

---

## Từ không dùng (nếu không đủ evidence)

proves; demonstrates universally; causes (trừ phủ định); consistently (như universal robustness); always (trừ phủ định); robust across datasets; establishes a novel audit methodology.

---

## Strength

- Findings 1–3, 5: DESCRIPTIVE / ASSOCIATIONAL
- Finding 4B (A9), Finding 6C (A7): CONTROLLED_EXPERIMENT
- Không có claim CAUSAL
