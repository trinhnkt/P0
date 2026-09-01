# XES3G5M rerun manifest (A2B)

**Date:** 2026-08-31  
**Prerequisite:** A1 CASE B.  
**Tree:** `IJIET_FINAL_REVISION/a2b/` (historical `data/processed/xes3g5m` and `results/predictions/` not overwritten).  
**ASSISTments / Junyi:** not updated.  
**Manuscript:** not edited in A2B; numbers below are the replacements a later text task must apply.

## Masking

- Dropped `selectmask != 1` (identical to concept `-1`: 1,540,356 tokens in `train_valid_sequences.csv`).
- Dropped KC `-1`, question `-1`, labels not in {0,1}.
- Official `test.csv` had 0 padding tokens.
- Processed rows: **6,413,353**; KCs **865**; items **7652**; learners **18066**.
- Learner partitions: **same users** as the published folds; padding rows removed from those users.
- fold_2 = fold_3 user sets (locked duplicate partition). Training seeds remain 42, 2024, 2025, 2026, 2027.
- Temporal: 70/10/20 re-cut on the masked table (padding timestamps no longer inflate the length).
- Strata: train-only frequency; **no** `kc_id=-1` row.
- Model settings: DKT/SimpleKT batch 64, 50 epochs, Adam 1e-3, best valid AUC; IRT 1PL lr 0.01, reg 0.01, 10 epochs, batch 512.

## Old manuscript numbers that **must change** (XES only)

Old values are from the accepted IJIET-21 manuscript / `BASELINE_FINAL_NUMERIC_AUDIT.md`. New values are four-partition (or seed-42 where that is what the paper used) on the masked rerun. **Obsolete** = do not keep the old cell.

| ID | Location | Old (obsolete) | New (A2B) |
|----|----------|----------------|-----------|
| T1.KCs | Table 1 KCs | 866 | 865 |
| T1.items | Table 1 / cohort items (if shown) | 7,653 | 7,652 |
| T1.inter | Table 1 interactions 7.95M | 7,953,709 flattened incl. padding | 6,413,353 valid KC-level rows (padding excluded) |
| T1.test | Table 1 learner-based test events | 1,589,145 (incl. 306,723 pad) | 1,282,422 fold-0 valid rows |
| R3.7 | Table 3 XES IRT AUC/ACC | 0.5000 / 0.7961±0.0031 | 0.5000 (N=1284322) / 0.7961±0.0031 (N=1284322) |
| R3.8 | Table 3 XES DKT AUC/ACC | 0.8171±0.0022 / 0.8327±0.0032 | 0.8180±0.0009 (N=1284322) / 0.8321±0.0015 (N=1284322) |
| R3.9 | Table 3 XES SimpleKT AUC/ACC | 0.7557±0.0013 / 0.8067±0.0037 | 0.7536±0.0010 (N=1284322) / 0.8057±0.0029 (N=1284322) |
| R3.10a | XES DKT sparse vs dense AUC | 0.857 vs 0.817 | 0.8579±0.0087 vs 0.8177±0.0009 |
| R3.10b | XES SimpleKT sparse vs dense AUC | 0.847 vs 0.755 | 0.8466±0.0094 vs 0.7525±0.0010 |
| R4.7d | Table 4 SimpleKT dense ECE | 0.1145±0.0011 | 0.1176±0.0014 N=1269345 |
| R4.7m | Table 4 SimpleKT medium ECE | 0.1114±0.0076 | 0.1129±0.0061 N=12889 |
| R4.7s | Table 4 SimpleKT sparse ECE | 0.1248±0.0085; N=2,010 R | 0.1254±0.0047 N=1969 |
| A4 | Abstract/Discussion 'XES ECE essentially flat' | 0.1145 → 0.1114 → 0.1248 | 0.1176±0.0014 N=1269345 → 0.1129±0.0061 N=12889 → 0.1254±0.0047 N=1969 |
| I2 | Intro sparse AUC > dense | DKT 0.857 vs 0.817; SK 0.847 vs 0.755 | still holds: DKT 0.858 vs 0.818; SK 0.847 vs 0.752 |
| R6.4 | XES SimpleKT ΔFAR / ΔMiss (five-run) | ΔFAR negative 5/5; ΔMiss mean +0.112 5/5 | dFM -0.017 (sd 0.012, pos 0/5); dMiss -0.183 (sd 0.033, pos 0/5) |
| C2xes | c2_fivefold_verdict XES DKT/SimpleKT | dkt dFM 0.004; sk dFM -0.018, dMiss 0.112, sparse_n 2000 | dkt 0.007 (sd 0.010, pos 3/5); sk -0.017 (sd 0.012, pos 0/5) |
| G42sk | seed-42 SimpleKT gate FAR sparse/dense (if cited for XES) | see direction_c XES cells | FM_s=0.127 FM_d=0.139 dFM=-0.012 sparse_n=2164 dense_n=1267014 |
| G42dkt | seed-42 DKT gate | see direction_c XES cells | FM_s=0.127 FM_d=0.109 dFM=0.018 |
| R7.1 | Table 7 sparse mass (XES) | 22.5% of 866 KCs | 22.5% of **865** KCs (195/865=0.2254; −1 was dense) |
| R7.2 | Table 7 sparse N | 2,010 R | 1,969 R (four-partition mean) |
| R7.3 | Table 7 difficulty ρ (XES) | +0.087 | +0.110 (Spearman log-freq vs difficulty_proxy; n=854 KCs with covariates) |
| R7.6 | Table 7 item median (XES) | 3 (dense 9 vs sparse 1) | 3 (dense 9 vs sparse 1); IQR 10 — same medians after dropping −1 |
| R7.7 | Table 7 curriculum ρ (XES) | −0.125 | −0.126 (Spearman log-freq vs median sequence position) |
| R8.6 old | Table 8 XES DKT t500 (old cell) | −0.008 [−0.019, +0.004] | **obsolete**; new +0.142 [+0.104, +0.189] |
| R7.8-9 | Results D regression n / log-freq (XES SimpleKT weighted) | n=1,263; −0.117 [−0.171, −0.063] | n=829; -0.028 [-0.042, -0.014] |
| R8.dkt.t100 | Table 8 XES dkt t100 ΔECE | see old statistical_summary XES rows | +0.137 [+0.107, +0.170] n=30 |
| R8.dkt.t50 | Table 8 XES dkt t50 ΔECE | see old statistical_summary XES rows | +0.161 [+0.127, +0.196] n=30 |
| R8.dkt.t500 | Table 8 XES dkt t500 ΔECE | see old statistical_summary XES rows | +0.142 [+0.104, +0.189] n=30 |
| R8.simplekt.t100 | Table 8 XES simplekt t100 ΔECE | see old statistical_summary XES rows | +0.083 [+0.061, +0.111] n=30 |
| R8.simplekt.t50 | Table 8 XES simplekt t50 ΔECE | see old statistical_summary XES rows | +0.110 [+0.071, +0.156] n=30 |
| R8.simplekt.t500 | Table 8 XES simplekt t500 ΔECE | see old statistical_summary XES rows | +0.041 [+0.020, +0.063] n=30 |
| D1-D3 | Discussion XES AUC/ECE sentences | sparse AUC>dense; ECE essentially flat N=2010 | rewrite from R3.10 and R4.7 |
| C3 | Conclusion XES ECE essentially flat | Table 4 | rewrite from new Table 4 XES row |
| Fig1 | Figure 1 if it encodes 866 / 7.95M / XES ECE | cohort counts + ECE panel | update XES count/ECE traces only |

## Numbers that must **not** change

- All ASSISTments ECE/AUC/FAR cells (0.1136, 0.2280, FAR 0.196/0.268, ΔFAR 0.047, CI [0.006, 0.138]).
- All Junyi cells (sparse empty; dense/medium ECE).
- Gate τ=0.7 definition; occupancy R/L/I; seed list; four-partition vs five-run wording.

## Brier / REL / RES

- irt_1pl dense: Brier 0.1622±0.0018 REL 0.0000±0.0000 RES 0.0000
- irt_1pl medium: Brier 0.1696±0.0034 REL 0.0002±0.0001 RES 0.0000
- irt_1pl sparse: Brier 0.1875±0.0055 REL 0.0019±0.0008 RES 0.0000
- dkt dense: Brier 0.1223±0.0009 REL 0.0027±0.0002 RES 0.0420±0.0009
- dkt medium: Brier 0.1186±0.0025 REL 0.0102±0.0008 RES 0.0601±0.0016
- dkt sparse: Brier 0.1391±0.0063 REL 0.0180±0.0011 RES 0.0632±0.0040
- simplekt dense: Brier 0.1562±0.0018 REL 0.0184±0.0005 RES 0.0236±0.0006
- simplekt medium: Brier 0.1366±0.0051 REL 0.0176±0.0018 RES 0.0493±0.0010
- simplekt sparse: Brier 0.1493±0.0043 REL 0.0216±0.0023 RES 0.0567±0.0018

## Temporal (seed 42, masked 70/10/20)

- irt_1pl all: n=1282671 AUC=0.6423 ACC=0.7859 ECE=0.0511
- irt_1pl dense: n=979858 AUC=0.6736 ACC=0.8045 ECE=0.0393
- irt_1pl medium: n=93130 AUC=0.5751 ACC=0.6174 ECE=0.2242
- irt_1pl sparse: n=9699 AUC=0.7210 ACC=0.8498 ECE=0.1334
- irt_1pl very_sparse: n=25058 AUC=0.6833 ACC=0.6991 ECE=0.2685
- irt_1pl strict_cold_start: n=174926 AUC=0.5000 ACC=0.7804 ECE=0.0100
- dkt all: n=1282671 AUC=0.6210 ACC=0.6910 ECE=0.1805
- dkt dense: n=979858 AUC=0.6446 ACC=0.7493 ECE=0.1401
- dkt medium: n=93130 AUC=0.5508 ACC=0.5130 ECE=0.3734
- dkt sparse: n=9699 AUC=0.5726 ACC=0.8535 ECE=0.1276
- dkt very_sparse: n=25058 AUC=0.6489 ACC=0.7145 ECE=0.2052
- dkt strict_cold_start: n=174926 AUC=0.5196 ACC=0.4467 ECE=0.3036
- simplekt all: n=1282671 AUC=0.6357 ACC=0.6986 ECE=0.2070
- simplekt dense: n=979858 AUC=0.6612 ACC=0.7561 ECE=0.1732
- simplekt medium: n=93130 AUC=0.5855 ACC=0.6411 ECE=0.2961
- simplekt sparse: n=9699 AUC=0.6982 ACC=0.8340 ECE=0.1341
- simplekt very_sparse: n=25058 AUC=0.7043 ACC=0.7333 ECE=0.1812
- simplekt strict_cold_start: n=174926 AUC=0.4407 ACC=0.3941 ECE=0.3611

## Artifact map

| Product | Path |
|---|---|
| Processed | `IJIET_FINAL_REVISION/a2b/data/processed/xes3g5m/` |
| Predictions | `IJIET_FINAL_REVISION/a2b/results/predictions/` |
| Strata | `IJIET_FINAL_REVISION/a2b/results/tables/kc_strata.csv` |
| Four-partition | `IJIET_FINAL_REVISION/a2b/analysis/summary_4part_*.csv` |
| Gate | `IJIET_FINAL_REVISION/a2b/analysis/gate_fivefold.csv` |
| Regression | `IJIET_FINAL_REVISION/a2b/analysis/regression_results.csv` |
| A9 | `IJIET_FINAL_REVISION/a2b/analysis/a9/` |

Do not copy these over historical `results/predictions/xes3g5m_*` until a later replace-manuscript task.
