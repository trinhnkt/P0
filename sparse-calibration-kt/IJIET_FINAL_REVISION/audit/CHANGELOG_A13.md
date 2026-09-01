# CHANGELOG_A13 — Partition-level ΔFAR robustness

**Date:** 2026-09-01  
**Retrain:** no. **Five-run T-KT ΔFAR mean `0.047`:** unchanged.

## Rule

Seeds 2025 and 2026 share one learner partition (`fold_2` = `fold_3`). Partition-level ΔFAR averages those two run values first, then summarizes the four unique partitions. Five training-run statistics are retained; they are not replaced.

Source: `IJIET_FINAL_REVISION/analysis/ijiet08_fivefold_denominators.csv` (`dFM` at τ=0.7).

## ASSISTments T-KT (verified)

| Quantity | Result |
|---|---|
| Unique partitions | 4 |
| Partition-level ΔFAR > 0 | **4/4** |
| Partition mean | 0.0556 → display **0.056** |
| Partition range | 0.015–0.087 |
| Five-run | mean **0.047**, sd **0.033**, **5/5** runs (unchanged) |

Duplicated-split average (2025, 2026) = 0.0150, still > 0.

## ASSISTments DKT (CSV only; not a five-run finding)

3/5 runs and **3/4** unique partitions positive. Five-run mean 0.033 unchanged. Not promoted to a 4/4 claim.

## Manuscript

- Table 6 T-KT cell: `5/5 runs; 4/4 unique partitions`. Mean ΔFAR column remains `0.047`.
- Table 6 caption: partition-level ΔFAR averages seeds 2025 and 2026 first; T-KT mean 0.056, range 0.015–0.087.
- Results: *positive in 5/5 training runs* and *positive in 4/4 unique partition-level estimates*.
- Discussion: same two phrases.

## Files

- `IJIET_FINAL_REVISION/analysis/far_partition_robustness.csv`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf`
- `IJIET_FINAL_REVISION/build_a13_far.py`
- `IJIET_FINAL_REVISION/apply_a13_word.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a13`.

## STOP
