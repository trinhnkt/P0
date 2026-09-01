# CHANGELOG_A11 — IRT unseen-learner fallback

**Date:** 2026-09-01  
**Retrain:** no. **Table 3 IRT AUC `0.5000`:** unchanged.

## Finding

In `IRT1PL.predict`, a test row uses \(\sigma(\theta_u-\beta_c)\) only if **both** the user and the KC were seen in training. Learner-based test users are all unseen, so **every** test row gets the same scalar \(\sigma(\mathrm{logit}(\bar y_{\mathrm{train}}))\). \(\beta_c\) is **not** applied. \(\theta_u\) is **not** filled with a population constant.

All 15 learner-based IRT prediction files have **one unique** `p_pred` (std 0 within float noise) and AUC \(=0.5000\). That AUC is expected for a constant score, **in this implementation**, not as a generic IRT fact.

## Manuscript

- Methods / Results: dropped “AUC=0.50 by construction” / “no ability parameter.”
- New: *In our implementation, unseen learners trigger a constant/base-rate fallback, yielding AUC=0.50.* Methods notes this is not an inherent property of IRT.

## Files

- `IJIET_FINAL_REVISION/audit/IRT_FALLBACK_AUDIT.md`
- `IJIET_FINAL_REVISION/analysis/irt_fallback_stats.csv`
- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (8 pages; compile checks true)
- `IJIET_FINAL_REVISION/apply_a11_word.py`
- `IJIET_FINAL_REVISION/analyze_irt_fallback.py`
- this changelog

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a11`.

## STOP
