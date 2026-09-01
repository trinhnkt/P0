# CHANGELOG A6

**Loại nhiệm vụ:** CPU + manuscript revision  
**Mục tiêu:** Bỏ overclaim novelty của L1–L8; định vị lại thành *operationalized KT-specific reproducibility and predictive-sanity workflow*.

**File mới:**
- `analysis/audit_claim_inventory.md`
- `analysis/table_a6_audit_classification.tex`
- `CHANGELOG_A6.md`

**File sửa (REV_REVIEWER_CALIBRATION_v1):**
- `sections/01_introduction.tex` — Contribution 3
- `sections/02_related_work.tex` — bỏ “to the best of our knowledge … leakage audit”
- `sections/03_protocol.tex` — L1–L7 = safeguard; L8 = empirical; P4
- `tables/table1_leakage_audit.tex` — bảng phân loại 4 cột
- `sections/04_experiments.tex` — case L8 lên main Results (mức vừa)
- `sections/05_discussion_limitations.tex` — reviewing community + internal validity
- `sections/06_conclusion.tex` — “reproducible audit workflow”
- `main_jedm.tex` / `main_jedm_anonymous.tex` — abstract

---

## Contribution 3 (sau A6)

> We operationalize eight named leakage and predictive-sanity checks into a reproducible KT evaluation workflow with verifiable artifacts. L1–L7 instantiate standard evaluation safeguards as inspectable checks; L8 is a warm-cohort predictive-sanity test that flagged a temporal prediction–label misalignment.

Không còn: “establish an eight-channel … audit checklist.”

---

## Bảng phân loại

Table 1 (`tab:leakage`): Channel | Standard safeguard | KT-specific operationalization | Empirical demonstration

- **L1–L7:** preventative PASS. L4/L7 là KT-encoding của quy tắc chuẩn “không định nghĩa nhóm trên test.”
- **L8:** empirical case (Appendix F). Không phải hàng PASS suông.

---

## L8 trên main text

RQ3: trước correction, deep KT gần random trên *warm* temporal cohorts; IRT vẫn informative → pipeline warning. Sau correction, warm AUC hồi phục. Câu chốt: đây là evidence cho predictive-sanity check, **không** phải new auditing methodology.

---

## Cụm đã loại / làm mềm

| Trước | Sau |
|-------|-----|
| establish an eight-channel … audit checklist | operationalize … workflow with verifiable artifacts |
| eight-channel leakage and predictive-sanity audit | operational leakage and predictive-sanity workflow (L1–L8) / reproducible audit workflow |
| to the best of our knowledge … and a leakage audit | package calibration diagnostics with an operational workflow; L1–L7 not a new auditing theory |
| audit checklist (P4, Internal Validity) | reproducible audit workflow |

Inventory đầy đủ: `analysis/audit_claim_inventory.md`.

---

## Cố ý không làm

- Không claim L8 là phát minh lý thuyết.
- Không xóa Appendix F; chỉ đưa case lên Results/Discussion ở mức vừa.
- Không đổi numbering bảng khác (thay nội dung Table 1 tại chỗ).
