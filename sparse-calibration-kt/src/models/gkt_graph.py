"""Train-only vs full-log GKT transition graphs (G-L9)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch


def _sequences(df: pd.DataFrame, kc_map: dict) -> list[list[int]]:
    d = df.copy()
    if "timestamp" in d.columns:
        d = d.sort_values(["user_id", "timestamp"])
    else:
        d = d.sort_values(["user_id"])
    seqs = []
    for _, g in d.groupby("user_id", sort=False):
        idx = [kc_map[k] for k in g["kc_id"].values if k in kc_map]
        if len(idx) >= 2:
            seqs.append(idx)
    return seqs


def transition_matrix(seqs: list[list[int]], n_kcs: int) -> torch.Tensor:
    counts = np.zeros((n_kcs, n_kcs), dtype=np.float64)
    for seq in seqs:
        for a, b in zip(seq[:-1], seq[1:]):
            if a != b:
                counts[a, b] += 1.0
    rowsum = counts.sum(axis=1, keepdims=True)
    graph = np.divide(counts, rowsum, out=np.zeros_like(counts), where=rowsum > 0)
    return torch.from_numpy(graph).float()


def build_graphs(train_df, valid_df, test_df, kc_map: dict, out_dir: Path) -> dict:
    n_kcs = len(kc_map)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_g = transition_matrix(_sequences(train_df, kc_map), n_kcs)
    full_df = pd.concat([train_df, valid_df, test_df], ignore_index=True)
    full_g = transition_matrix(_sequences(full_df, kc_map), n_kcs)
    torch.save(train_g, out_dir / "gkt_graph_train_only.pt")
    torch.save(full_g, out_dir / "gkt_graph_full_log.pt")
    train_nz = int((train_g > 0).sum().item())
    full_nz = int((full_g > 0).sum().item())
    leak_only = int(((full_g > 0) & (train_g == 0)).sum().item())
    stats = {
        "n_kcs": n_kcs,
        "train_nonzero_edges": train_nz,
        "full_nonzero_edges": full_nz,
        "edges_only_in_full": leak_only,
        "mean_outdeg_train": float((train_g > 0).sum(dim=1).float().mean()),
        "mean_outdeg_full": float((full_g > 0).sum(dim=1).float().mean()),
    }
    pd.Series(stats).to_json(out_dir / "gkt_graph_stats.json")
    return {"train_only": train_g, "full_log": full_g, "stats": stats}
