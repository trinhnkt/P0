# CHANGELOG_A27 — B1 occupancy/mixed-τ policies

**Date:** 2026-09-01  
**Retrain:** no. **Locks:** Table 5 FAR 0.196/0.268 and Nadvance=235 unchanged.  
**Source:** `analysis/direction_c/threshold_rates.csv` (T-KT = CSV `simplekt`).

Three simulated policies on frozen seed-42 p (ASSISTments fold 0):

| Policy | Pop. FAR | Sparse Nadvance | Sparse FAR |
|--------|----------|-----------------|------------|
| A global τ=0.7 | 0.197 | 235 | 0.268 |
| B Reliable-only | 0.197 | 0 | — |
| C sparse τ=0.8 | 0.197 | 218 | 0.261 |

Finding: population FAR does not move; the design choice appears in the sparse slice (TSCDA).

Named/blind: 8 / 8 pages. Table S4 in supplementary.pdf.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a27`.
