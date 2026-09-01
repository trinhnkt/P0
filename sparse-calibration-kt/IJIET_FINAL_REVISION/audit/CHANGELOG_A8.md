# CHANGELOG_A8 — complete controlled sparsification reporting

**Date:** 2026-09-01  
**Retrain:** no. **Locked ASSISTments ECE/FAR cells:** unchanged.

## Source (not cherry-picked)

Full A9 grid from `analysis/a9_statistical_summary.csv` (historical seed-42 learner-based fold 0; **not** the A2B masked-XES A9 rebuild).

Design that exists: **3 datasets × 2 models × {500, 100, 50} = 18 cells**, \(n_{\mathrm{KC}}=30\) throughout. Eligible-KC rule was fixed and recorded in `controlled_sparsification_protocol.md` before reduced-evidence ECE was inspected (dense \(f_{\mathrm{train}}\ge 500\), Limited test support, both labels, difficulty-tertile subsample). No post-hoc drop of inconvenient cells.

## What was omitted before (the cherry-pick)

Old Table 8 showed 5 illustrative rows and dropped, among others:

- all **100-row** cells
- ASSISTments T-KT @ 500 (\(\Delta\)ECE \(-0.026\))
- Junyi T-KT @ 500 (\(+0.101\))
- **all XES3G5M T-KT cells** (positive \(\Delta\)ECE at 100 and 50; 500 CI includes 0)

Those XES T-KT positives are now in Table 8 (50 and 500) and in Supplementary Table S2 (all three levels). They are not omitted.

## Reporting choice

**OPTION A in the main paper, with OPTION B completeness in S2.**

- **Table 8:** all 3 datasets × 2 models × **{500, 50} = 12 rows**. Declared rule: protocol **endpoints** only. The 100-row level is omitted there by that rule, not by outcome.
- **Supplementary Table S2:** the complete 18-cell grid, including \(\Delta\)REL and share of KCs with ECE increase.
- Required sentence in caption and IV.D: *Complete results for all models, datasets, and reduction levels are reported in Supplementary Table S2.*

Display name remains **T-KT** (A6). CSV `model` keeps source ids `dkt` / `simplekt`.

## Interpretation (unchanged)

“Reducing training evidence for the same KC does not universally worsen calibration.” Several endpoint CIs lie below 0 or include 0 (e.g. ASSISTments DKT/T-KT @ 50; XES DKT @ 500). Junyi T-KT and XES T-KT @ 50 are positive; that is reported.

## Files

- `IJIET_FINAL_REVISION/analysis/controlled_sparsification_full.csv` (18 rows; requested columns)
- `IJIET_FINAL_REVISION/supplementary/Table_S2_controlled_sparsification.tex`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx` (Table 8 + IV.D)
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (8 pages; compile checks true)
- `IJIET_FINAL_REVISION/build_a8_sparsification.py`
- `IJIET_FINAL_REVISION/apply_a8_word.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a8`.

## STOP
