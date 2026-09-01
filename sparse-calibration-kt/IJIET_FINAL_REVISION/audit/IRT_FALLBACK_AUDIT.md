# IRT unseen-learner fallback audit

**Date:** 2026-09-01  
**Retrain:** no. **Table 3 IRT AUC cells `0.5000`:** unchanged.

Source: `src/models/irt_baseline.py` `IRT1PL.predict`. Exports: `results/predictions/{dataset}_learner_based_irt_1pl_seed{42,2024,2025,2026,2027}_predictions_rerun.csv`.

## Implementation (learner-based test)

Fit stores \(\theta_u\) and \(\beta_c\) on **train** users/KCs, plus a global bias \(\mathrm{logit}(\bar y_{\mathrm{train}})\).

At predict time:

```python
p_pred = expit(self.bias)           # fill all rows
known = user_in_train AND kc_in_train
p_pred[known] = expit(theta[u] - beta[c])
```

Learner-based test users are disjoint from train, so `user_in_train` is false for **every** test row. Then `known` is false regardless of KC.

| Question | Answer in this implementation |
|----------|-------------------------------|
| Is \(\theta_u\) set to a global constant for unseen users? | **No \(\theta_u\) is assigned.** Unseen users are missing from `user_to_idx`. |
| Is \(\beta_c\) still used? | **No.** The Rasch term is applied only when **both** user and KC were seen in training. |
| Constant across all test rows? | **Yes.** One scalar \(\sigma(\mathrm{bias})\) per fold. |
| Varies by KC? | **No.** |
| Global base-rate probability? | **Yes.** \(\sigma(\mathrm{logit}(\bar y_{\mathrm{train}}))\). |

This is **our local fallback**, not a property of IRT in general. A different IRT implementation could use \(\sigma(\bar\theta - \beta_c)\) or a population \(\theta\).

## Prediction-file evidence (learner-based)

Every fold has **one unique** `p_pred`. Std is 0 within float noise (\(\sim 10^{-16}\)). AUC \(= 0.5000\).

| Dataset | Seed | \(n\) | Unique \(p\) | \(p\) (constant) | std | AUC |
|---------|-----:|------:|-------------:|-----------------:|----:|----:|
| ASSISTments 2012 | 42 | 534,150 | 1 | 0.696153 | 0 | 0.5000 |
| ASSISTments 2012 | 2024 | 542,748 | 1 | 0.696189 | \(\sim 0\) | 0.5000 |
| ASSISTments 2012 | 2025 | 528,681 | 1 | 0.696242 | \(\sim 0\) | 0.5000 |
| ASSISTments 2012 | 2026 | 528,681 | 1 | 0.696242 | \(\sim 0\) | 0.5000 |
| ASSISTments 2012 | 2027 | 515,889 | 1 | 0.695993 | \(\sim 0\) | 0.5000 |
| Junyi Academy | 42 | 3,269,022 | 1 | 0.702799 | \(\sim 0\) | 0.5000 |
| Junyi Academy | 2024 | 3,243,926 | 1 | 0.702974 | \(\sim 0\) | 0.5000 |
| Junyi Academy | 2025 | 3,244,494 | 1 | 0.703165 | \(\sim 0\) | 0.5000 |
| Junyi Academy | 2026 | 3,244,494 | 1 | 0.703165 | \(\sim 0\) | 0.5000 |
| Junyi Academy | 2027 | 3,163,548 | 1 | 0.702604 | 0 | 0.5000 |
| XES3G5M | 42 | 1,589,145 | 1 | 0.641307 | \(\sim 0\) | 0.5000 |
| XES3G5M | 2024 | 1,590,128 | 1 | 0.641377 | \(\sim 0\) | 0.5000 |
| XES3G5M | 2025 | 1,591,387 | 1 | 0.642080 | \(\sim 0\) | 0.5000 |
| XES3G5M | 2026 | 1,591,387 | 1 | 0.642080 | \(\sim 0\) | 0.5000 |
| XES3G5M | 2027 | 1,591,247 | 1 | 0.641763 | \(\sim 0\) | 0.5000 |

Seeds 2025 and 2026 share one learner partition (same \(n\) and \(p\)).

CSV: `IJIET_FINAL_REVISION/analysis/irt_fallback_stats.csv`.

## Is AUC = 0.50 mathematically expected?

**Yes, for this implementation.** A predictor that assigns the same score to every test row cannot rank positives above negatives. With both classes present, ROC AUC is 0.5 (all pairs tied). Table 3 `0.5000` is that fact, not a fitted Rasch ranking of new students.

Accuracy is **not** 0.50: the constant \(p\) is \(>0.5\), so the 0.5-threshold classifier predicts all-correct and ACC \(\approx \bar y_{\mathrm{test}}\) (e.g. ASSISTments \(0.6973\)).

## Manuscript

Replaced “AUC is 0.50 by construction / no ability parameter” with: *In our implementation, unseen learners trigger a constant/base-rate fallback, yielding AUC=0.50.* Methods adds that this fallback is not an inherent property of IRT.
