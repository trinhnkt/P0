# CHANGELOG_A10 — training and checkpoint-selection audit

**Date:** 2026-09-01  
**Retrain:** no. **Numeric result cells:** unchanged.

## Finding

Main DKT / T-KT training (`src/baseline_runner.py` `train_torch_model`) **always runs all 50 epochs** (no patience). It computes validation AUC and assigns `best_state = model.state_dict()` **without cloning**. On torch 2.11.0 those tensors alias live parameters, so `load_state_dict` after the loop does **not** restore an earlier best-valid snapshot. Test predictions use the **final checkpoint**. Validation AUC is therefore **not** the selection metric in effect. Test metrics are never used for selection.

IRT 1PL (`src/models/irt_baseline.py`): **10 epochs always**, last epoch, no validation, test AUC printed after predict only.

## Table 2

| Row | Old (ambiguous) | New |
|-----|-----------------|-----|
| Early stopping | none (10/50 epochs) | Fixed 10/50 epochs; final checkpoint. |
| Selection metric | last epoch / validation AUC / validation AUC | final checkpoint |

`supplementary/TABLE_S1_MODEL_SETTINGS.md` aligned with the same finding.

## Files

- `IJIET_FINAL_REVISION/audit/CHECKPOINT_SELECTION_AUDIT.md`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (8 pages; compile checks true)
- `IJIET_FINAL_REVISION/apply_a10_word.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a10`.

## STOP
