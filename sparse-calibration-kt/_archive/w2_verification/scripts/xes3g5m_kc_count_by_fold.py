import pandas as pd
from pathlib import Path

MODELS = ['irt_1pl', 'dkt', 'simplekt']
SEEDS = [42, 2024, 2025, 2026, 2027]
STRATA_FILE = 'results/tables/kc_strata.csv'

strata_df = pd.read_csv(STRATA_FILE)
strata_lb = strata_df[(strata_df['dataset'] == 'xes3g5m') & (strata_df['split'] == 'learner_based')].copy()
strata_lb['kc'] = strata_lb['kc_id'].astype(str).apply(lambda x: "~~".join(sorted(x.split("~~"))) if "~~" in x else x)

rows = []

for m in MODELS:
    for seed in SEEDS:
        fold_idx = SEEDS.index(seed)
        pred_file = Path(f'results/predictions/xes3g5m_learner_based_{m}_seed{seed}_predictions_rerun.csv')
        if not pred_file.exists():
            continue
            
        pred_df = pd.read_csv(pred_file)
        pred_df = pred_df.dropna(subset=['y_true', 'p_pred'])
        pred_df = pred_df[pred_df['kc_id'].astype(str) != "-1"]
        pred_df = pred_df[pred_df['kc_id'].astype(str) != "nan"]
        
        pred_df['kc'] = pred_df['kc_id'].astype(str).apply(lambda x: "~~".join(sorted(x.split("~~"))) if "~~" in x else x)
        
        merged = pd.merge(pred_df, strata_lb[['kc', 'bucket']], on='kc', how='inner')
        
        for bucket, b_df in merged.groupby('bucket'):
            n_kcs = b_df['kc'].nunique()
            rows.append({
                'dataset': 'xes3g5m',
                'model': m,
                'fold': f'fold_{fold_idx}',
                'seed': seed,
                'bucket': bucket,
                'n_kcs': n_kcs
            })

df = pd.DataFrame(rows)
out_dir = Path('w2_verification/outputs')
out_dir.mkdir(parents=True, exist_ok=True)
df.to_csv(out_dir / 'xes3g5m_kc_count_by_fold.csv', index=False)
print("Saved to w2_verification/outputs/xes3g5m_kc_count_by_fold.csv")

# Print a quick summary of the dense bucket counts
dense_df = df[df['bucket'] == 'dense']
for m in MODELS:
    m_df = dense_df[dense_df['model'] == m]
    if not m_df.empty:
        mean_kc = m_df['n_kcs'].mean()
        print(f"[{m}] Dense bucket KCs: {list(m_df['n_kcs'])} -> Mean: {mean_kc}")
