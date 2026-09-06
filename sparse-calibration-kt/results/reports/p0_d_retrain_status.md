# P0 D retrain status (5 Sep 2026, queues finished)

Do **not** paste these cells into the IJIET manuscript unless asked.
T-KT locks stay: ECE `0.1136` / `0.2280`; FAR `0.196` / `0.268`.

Learner-based folds: 42→0, 2024→1, 2025→2, 2026→3, 2027→4 (`fold_2`=`fold_3`).
Four-partition mean averages seeds 2025/2026 first.

## Test AUC

| Model | Dataset | 42 | 2024 | 2025 | 2026 | 2027 | 5-run | 4-part |
|---|---|---|---|---|---|---|---|---|
| BKT (Laplace EM) | ASSISTments | 0.6248 | 0.6206 | 0.6245 | 0.6245 | 0.6237 | 0.6236±0.0017 | 0.6234 |
| BKT (Laplace EM) | XES3G5M | 0.8306 | 0.8281 | 0.8279 | 0.8279 | 0.8267 | 0.8282±0.0014 | 0.8283 |
| BKT (Laplace EM) | Junyi | 0.6832 | 0.6881 | 0.6869 | 0.6869 | 0.6862 | 0.6863±0.0018 | 0.6861 |
| Official simpleKT | ASSISTments | 0.7715 | 0.7698 | 0.7702 | 0.7705 | 0.7683 | 0.7701±0.0012 | 0.7700 |
| Official simpleKT | XES3G5M | 0.9384 | 0.9371 | 0.9371 | 0.9367 | 0.9369 | 0.9372±0.0007 | 0.9373 |
| Official simpleKT | Junyi | 0.8056 | 0.8027 | 0.8045 | 0.8037 | 0.8031 | 0.8039±0.0012 | 0.8039 |

pyBKT 1.4.1 Assist seed 42 remains rejected (AUC 0.500). All 30 stable/official runs have large `p_unique`.

Official simpleKT is on **our** learner-based folds, not the pyKT 5-fold. The simpleKT paper reports AS2009 `0.7744±0.0018`, not ASSISTments 2012.
