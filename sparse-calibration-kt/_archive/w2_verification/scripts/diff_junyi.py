import pandas as pd
from pathlib import Path

def diff_junyi():
    pred_dir = Path("results/predictions")
    dkt_path = pred_dir / "junyi_learner_based_dkt_seed42_predictions_rerun.csv"
    if not dkt_path.exists():
        dkt_path = pred_dir / "junyi_learner_based_dkt_seed42.csv"
        
    simplekt_path = pred_dir / "junyi_learner_based_simplekt_seed42_predictions_rerun.csv"
    if not simplekt_path.exists():
        simplekt_path = pred_dir / "junyi_learner_based_simplekt_seed42.csv"

    print("Loading DKT:", dkt_path)
    dkt = pd.read_csv(dkt_path)
    print("Loading SimpleKT:", simplekt_path)
    simplekt = pd.read_csv(simplekt_path)
    
    print(f"DKT rows: {len(dkt)}")
    print(f"SimpleKT rows: {len(simplekt)}")
    print(f"Diff (SimpleKT - DKT): {len(simplekt) - len(dkt)}")
    
    # Check config diff
    # Usually in pyKT, sequence_position is not explicitly saved, but we can infer.
    # Group by learner_id to see where differences are
    dkt_counts = dkt.groupby("user_id").size().reset_index(name="dkt_count")
    simplekt_counts = simplekt.groupby("user_id").size().reset_index(name="simplekt_count")
    
    merged = pd.merge(dkt_counts, simplekt_counts, on="user_id", how="outer").fillna(0)
    diffs = merged[merged["dkt_count"] != merged["simplekt_count"]]
    
    print(f"Users with different event counts: {len(diffs)}")
    if len(diffs) > 0:
        print(diffs.head(10))
        
        # Take a user and diff
        u = diffs.iloc[0]["user_id"]
        dkt_u = dkt[dkt["user_id"] == u].sort_values("timestamp")
        skt_u = simplekt[simplekt["user_id"] == u].sort_values("timestamp")
        
        print("\nDKT for user", u)
        print(dkt_u[["kc_id", "timestamp"]].head(10))
        
        print("\nSimpleKT for user", u)
        print(skt_u[["kc_id", "timestamp"]].head(10))
        
if __name__ == "__main__":
    diff_junyi()
