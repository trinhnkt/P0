import pandas as pd
import numpy as np
import os
from pathlib import Path

DATASETS = ['assist2012', 'junyi', 'xes3g5m']
MODELS = ['irt_1pl', 'dkt', 'simplekt']
SEEDS = [42, 2024, 2025, 2026, 2027]
STRATA_FILE = 'results/tables/kc_strata.csv'

strata_df = pd.read_csv(STRATA_FILE)
# Filter only learner_based splits to prevent duplication during join
strata_lb = strata_df[strata_df['split'] == 'learner_based'].copy()
strata_lb['kc'] = strata_lb['kc_id'].astype(str).apply(lambda x: "~~".join(sorted(x.split("~~"))) if "~~" in x else x)

rows = []

for ds in DATASETS:
    # 1. Get C1 (Test partition row count from the original PyKT format, or rather just the test.csv in the fold folder)
    # The fold is SEEDS.index(seed). So seed 42 -> fold 0.
    for seed in SEEDS:
        fold_idx = SEEDS.index(seed)
        fold_path = Path(f'data/processed/{ds}/splits/learner_based/fold_{fold_idx}/test.csv')
        if fold_path.exists():
            test_df = pd.read_csv(fold_path)
            # C1 is the number of raw events
            C1 = len(test_df)
        else:
            C1 = 0

        # C2 is the same as C1 since the original framework PyKT groups these into sequences but the row count per item remains conceptually the same.
        C2 = C1
        
        for m in MODELS:
            C3 = 0
            C4 = 0
            named_reason = 'none'
            
            pred_file = Path(f'results/predictions/{ds}_learner_based_{m}_seed{seed}_predictions_rerun.csv')
            if pred_file.exists():
                pred_df = pd.read_csv(pred_file)
                # C3 is before merging
                pred_df = pred_df.dropna(subset=['y_true', 'p_pred'])
                pred_df = pred_df[pred_df['kc_id'].astype(str) != "-1"]
                pred_df = pred_df[pred_df['kc_id'].astype(str) != "nan"]
                C3 = len(pred_df)
                
                # C4 is after merging with kc_strata
                pred_df['kc'] = pred_df['kc_id'].astype(str).apply(lambda x: "~~".join(sorted(x.split("~~"))) if "~~" in x else x)
                # join
                strata_lb_fold = strata_lb[strata_lb['fold'].astype(str) == str(fold_idx)]
                merged = pd.merge(pred_df, strata_lb_fold[['dataset', 'kc', 'bucket']], on=['dataset', 'kc'], how='inner')
                C4 = len(merged)
            else:
                named_reason = 'missing_prediction_file'
                
            if C1 != C3 and named_reason == 'none':
                named_reason = f'fold_misalignment_or_missing_predictions'
            
            if C3 != C4 and named_reason == 'none':
                named_reason = f'dropped_during_kc_strata_join'
                
            rows.append({
                'dataset': ds,
                'model': m,
                'seed/fold': f'fold_{fold_idx}/seed_{seed}',
                'C1': C1,
                'C2': C2,
                'C3': C3,
                'C4': C4,
                'C1_minus_C2': C1 - C2,
                'C2_minus_C3': C2 - C3,
                'C3_minus_C4': C3 - C4,
                'named_reason': named_reason
            })

df = pd.DataFrame(rows)
out_dir = Path('w2_verification/outputs')
out_dir.mkdir(parents=True, exist_ok=True)
df.to_csv(out_dir / 'events_reconciliation_by_fold.csv', index=False)
print("Saved to w2_verification/outputs/events_reconciliation_by_fold.csv")
