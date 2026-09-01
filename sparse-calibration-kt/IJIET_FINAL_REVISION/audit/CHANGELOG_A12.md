# CHANGELOG_A12 — Brier decomposition evidence (Supplementary Table S1)

**Date:** 2026-09-01  
**Retrain:** no. **Bins:** unchanged (`M=15` equal-width; four-unique-partition aggregation).  
**Locked ASSISTments T-KT ECE:** `0.1136±0.0066` / `0.2280±0.0197` unchanged.

## What was missing

Methods already stated per-stratum ECE, Brier, REL, RES, and UNC. The main Results table (Table 4) reports ECE. The Brier decomposition was computed in the validated four-partition summary and was not shown as a complete table.

## Supplementary Table S1

Built from `IJIET_FINAL_REVISION/analysis/summary_4part_bucket.csv` with `n_partitions==4` (same rule as Table 4). No rebinning. No A2B XES numbers.

Columns: Dataset, Model, Stratum, N, Flag, ECE, Brier, UNC, REL, RES.

Scope: IRT / DKT / T-KT × dense / medium / sparse. Junyi sparse is empty (omitted). `very_sparse` and `strict_cold_start` omitted (not in Table 4). Flag: R \(N\ge 1000\), L \(100\le N<1000\), I \(N<100\) (no I rows in this subset). N = `int(round(n_events_mean))`.

IRT RES is `0.0000` on these learner-based strata in the existing summary (no new claim).

## Manuscript

- Results (IRT sentence): *resolution is zero* now cites Supplementary Table S1. Locked IRT dense ECE `0.0031±0.0006` unchanged.
- Results (after occupancy/miss-rate sentence): *Full Brier, reliability, resolution, and uncertainty results are provided in Supplementary Table S1.*

No new scientific claims.

## Files

- `IJIET_FINAL_REVISION/supplementary/Table_S1_calibration_full.tex`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf`
- `IJIET_FINAL_REVISION/build_a12_s1.py`
- `IJIET_FINAL_REVISION/apply_a12_word.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a12`.

Note: `supplementary/TABLE_S1_MODEL_SETTINGS.md` remains the recovered model-settings audit file, not this calibration table.

## STOP
