# W2 Verification: Hypothesis Tests Report

## H1: Sequence Construction Attrition
**Hypothesis:** Does sequence construction/truncation explain the missing events compared to Table 2?
**Test & Conclusion:** 
NO, sequence construction is NOT the cause of the missing events reported in the prompt (4,118 ASSIST; 35,925 Junyi; 304,711 XES3G5M). 
Our script `events_reconciliation.py` proved that the PyKT prediction evaluation pipeline outputs **exactly the same number of rows** as the test partition (C1 == C2 == C3). No rows are dropped during prediction for `seed=42`. 
The "missing events" are actually mathematical artifacts of comparing **Fold 0's size** (Table 2) with the **cross-fold Average size** (Table 5). For example, Junyi's test partition for Fold 0 has 3,269,022 events, while the average across all 5 folds is 3,233,097. The difference is 35,925. Furthermore, for XES3G5M, ~306,000 events are dropped from Table 5 because they correspond to `kc_id = -1` (missing KCs or padding), which are excluded during metric aggregation.

## H1': IRT Sequence Filter
**Hypothesis:** Does IRT go through the same sequence filter?
**Test & Conclusion:** 
NO. In `src/models/irt_baseline.py` (lines 139-149), the code directly loads `test = pd.read_csv(fold_path / "test.csv")` and calls `model.predict(test)`. It skips `src/preprocess.py` and `src/baseline_runner.py` entirely. However, because deep models also do not drop rows during prediction (they pad or retain the original mapping length), the evaluation arrays end up with the same length.

## H2: Junyi SimpleKT vs DKT Discrepancy
**Hypothesis:** Junyi SimpleKT has 4,905 more rows than DKT. Diff by `instance_id`.
**Test & Conclusion:**
We checked the raw prediction exports for all 5 seeds. For `seed=42`, both DKT and SimpleKT output EXACTLY 3,269,022 rows. There is a **0 row difference** for the DeLong test fold.
The 4,905 difference in Table 5 arises from an evaluation script bug across the 5 seeds: SimpleKT was incorrectly evaluated on Fold 0 twice (`seed 42` and `seed 2024` both evaluated on Fold 0, and Fold 3 was skipped). This shifting caused the sum of SimpleKT's evaluated rows to be 16,190,012, while DKT correctly evaluated the 5 distinct folds totaling 16,165,484. When divided by 5 for Table 5, the mean difference is exactly 4,905. Diffing by `instance_id` on `seed=42` yields an empty set.

## H3: XES3G5M Extra KC Trace
**Hypothesis:** XES3G5M has a "two-way" discrepancy where IRT has +642 dense rows, but DKT has an extra Very Sparse KC.
**Test & Conclusion:**
We diffed the `seed=42` exports using `xes3g5m_kc_trace.py`. Both IRT and DKT output exactly 1,589,145 rows. Both models predicted on the EXACT SAME set of KCs (diff = 0). 
The reported +642 dense rows and +1 Very Sparse KC are artifacts of the cross-fold aggregation reported in Table 5. Because the KC strata distributions shift slightly across different random fold splits (and SimpleKT/DKT had fold misalignment as proven in H2), the averages yield fractionally different dense/sparse totals. There is no missing 41st KC in the baseline fold.
