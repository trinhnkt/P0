# Direction A — pre-registration (locked before GKT ECE is inspected)

**Scope (this run):** ASSISTments 2012, learner-based `fold_0` ≡ seed 42.
Controls: existing `assist2012_learner_based_{dkt,simplekt}_seed42.csv`.
Primary model: **GKT** (pyKT implementation, Nakagawa et al. 2019).
CL4KT is **not** started until GKT A1–A3 are scored. **Status:** GKT scored 2026-08-25; A1–A3 NULL (GKT wins sparse AUC and ECE). CL4KT unlocked.

| CL4KT (Lee et al., 2022) | Sparse student–question interactions overfit hidden states; contrastive views (mask/crop/permute/replace) of **training** histories help generalization | Same A1–A3 vs DKT on this split; augmentations train-only |

## Original claims (verbatim intent, not numeric copy from other splits)

| Paper | Claim we test | Testable form on *this* split |
|--------|----------------|-------------------------------|
| GKT (Nakagawa et al., 2019) | KC graph lets related skills update together; improves prediction vs sequential KT without extra labels | \(\mathrm{AUC}_{\mathrm{sparse}}(\mathrm{GKT}) > \mathrm{AUC}_{\mathrm{sparse}}(\mathrm{DKT})\) on \(f_{\mathrm{train}}<100\), after **excluding** strict cold-start \(f=0\), with flag ≥ L |
| pyKT GKT graph helper | Transition graph is built from **train+test** CSVs | Ablation G-L9: train-only graph vs full-log graph |
| CL4KT (Lee et al., 2022) | Sparse student–question interactions overfit hidden states; contrastive views help | Same A1–A3 vs DKT; mask/crop/permute/replace on **train** sequences only |

GKT papers report **aggregate AUC**, not train-only KC-frequency ECE. We do **not** compare to their published AUC numbers (different preprocess).

## G-L9 (graph leakage)

- **Primary:** consecutive KC transitions from **train.csv only** (same users as DKT train).
- **Ablation (after primary finishes):** transitions from train+valid+test (pyKT `get_gkt_graph` default).
- Valid/test labels never enter the **primary** adjacency.

## Success (need one; scored after GKT predictions exist)

- **A1 Occupancy:** GKT “sparse gain” lives in Insufficient \(N<100\) or is carried by \(f_{\mathrm{train}}=0\).
- **A2 Discrimination:** \(\Delta\)AUC sparse vs DKT vanishes or flips once strict cold-start is split off.
- **A3 Calibration:** sparse AUC ≥ DKT but sparse ECE **worse** (flag L or R).

Null (GKT wins AUC and ECE on sparse, \(N\) Limited/Reliable) is reported as confirmation, not a protocol failure.

## Locked paths

- Data: `data/processed/assist2012/splits/learner_based/fold_0/{train,valid,test}.csv`
- Strata: `results/tables/kc_strata.csv` rows `assist2012,learner_based,0`
- Thresholds: \(0\) / \(<20\) / \(<100\) / \(<500\) (protocol)
- Flags: R \(N\ge1000\), L \(100\le N<1000\), I \(N<100\)
