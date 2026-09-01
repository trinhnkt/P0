import pandas as pd
from pathlib import Path

def trace_xes():
    pred_dir = Path("results/predictions")
    irt_path = pred_dir / "xes3g5m_learner_based_irt_1pl_seed42_predictions_rerun.csv"
    
    dkt_path = pred_dir / "xes3g5m_learner_based_dkt_seed42_predictions_rerun.csv"
    if not dkt_path.exists():
        dkt_path = pred_dir / "xes3g5m_learner_based_dkt_seed42.csv"
        
    print(f"Loading IRT: {irt_path}")
    irt = pd.read_csv(irt_path)
    
    print(f"Loading DKT: {dkt_path}")
    dkt = pd.read_csv(dkt_path)
    
    irt_kcs = set(irt['kc_id'].unique())
    dkt_kcs = set(dkt['kc_id'].unique())
    
    diff_dkt = dkt_kcs - irt_kcs
    diff_irt = irt_kcs - dkt_kcs
    
    print('DKT extra KCs (in DKT but not IRT):', diff_dkt)
    print('IRT extra KCs (in IRT but not DKT):', diff_irt)
    
    print('IRT total rows:', len(irt))
    print('DKT total rows:', len(dkt))
    
    # Read strata
    strata = pd.read_csv("results/tables/kc_strata.csv")
    strata = strata[(strata['dataset'] == 'xes3g5m') & (strata['split'] == 'learner_based')]
    
    if diff_dkt:
        extra_kc = list(diff_dkt)[0]
        s = strata[strata['kc_id'] == str(extra_kc)]
        print(f"Strata for extra KC {extra_kc}:")
        print(s)
        
        # Check if this KC exists in train for IRT
        train_path = Path("data/processed/xes3g5m/splits/learner_based/fold_0/train.csv")
        if train_path.exists():
            train_df = pd.read_csv(train_path)
            kc_in_train = str(extra_kc) in train_df['kc_id'].astype(str).values
            print(f"Is KC {extra_kc} in train.csv? {kc_in_train}")
        
    # Let's count rows per KC
    irt_counts = irt.groupby('kc_id').size()
    dkt_counts = dkt.groupby('kc_id').size()
    
    # Check dense KCs where IRT > DKT
    dense_kcs = strata[strata['bucket'] == 'dense']['kc_id'].astype(str).values
    
    irt_dense = 0
    dkt_dense = 0
    
    for kc in dense_kcs:
        i_c = irt_counts.get(int(kc) if kc.isdigit() else kc, irt_counts.get(float(kc) if kc.replace('.','',1).isdigit() else kc, 0))
        d_c = dkt_counts.get(int(kc) if kc.isdigit() else kc, dkt_counts.get(float(kc) if kc.replace('.','',1).isdigit() else kc, 0))
        irt_dense += i_c
        dkt_dense += d_c
        
    print(f"Dense total IRT: {irt_dense}")
    print(f"Dense total DKT: {dkt_dense}")
    print(f"Diff dense: {irt_dense - dkt_dense}")

if __name__ == "__main__":
    trace_xes()
