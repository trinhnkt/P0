#!/usr/bin/env python3
"""Train pyKT GKT on locked ASSISTments learner-based fold_0 (seed 42).

Primary graph: train-only transitions (G-L9). Optional --graph full_log.
Does not overwrite official DKT/SimpleKT CSVs.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.gkt_graph import build_graphs  # noqa: E402


class SeqDataset(Dataset):
    def __init__(self, df: pd.DataFrame, kc_map: dict, max_seq_len: int = 200):
        self.rows = []
        d = df.copy()
        if "timestamp" in d.columns:
            d = d.sort_values(["user_id", "timestamp"])
        for _, g in d.groupby("user_id", sort=False):
            kcs = [kc_map[k] for k in g["kc_id"].values]
            ys = g["correct"].astype(int).tolist()
            for i in range(0, len(kcs), max_seq_len):
                q = kcs[i : i + max_seq_len]
                r = ys[i : i + max_seq_len]
                if len(q) < 2:
                    continue
                self.rows.append((q, r))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        q, r = self.rows[i]
        return (
            torch.tensor(q, dtype=torch.long),
            torch.tensor(r, dtype=torch.long),
        )


def collate(batch):
    qs = [b[0] for b in batch]
    rs = [b[1] for b in batch]
    q_pad = nn.utils.rnn.pad_sequence(qs, batch_first=True, padding_value=-1)
    r_pad = nn.utils.rnn.pad_sequence(rs, batch_first=True, padding_value=0)
    return q_pad, r_pad


def masked_auc(pred, q, r):
    # pred: [B, L-1] for positions 1..L-1; q/r: [B, L]
    target = r[:, 1:].float()
    q_next = q[:, 1:]
    mask = q_next != -1
    y = target[mask].detach().cpu().numpy()
    p = pred[mask].detach().cpu().numpy()
    if len(y) < 2 or len(np.unique(y)) < 2:
        return float("nan"), y, p
    return float(roc_auc_score(y, p)), y, p


def train_one_epoch(model, loader, opt, device):
    model.train()
    crit = nn.BCELoss(reduction="none")
    losses = []
    for q, r in loader:
        q, r = q.to(device), r.to(device)
        opt.zero_grad()
        pred = model(q, r)
        target = r[:, 1:].float()
        mask = q[:, 1:] != -1
        loss = crit(pred[mask], target[mask]).mean()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 5.0)
        opt.step()
        losses.append(float(loss.item()))
    return float(np.mean(losses))


@torch.no_grad()
def eval_auc(model, loader, device):
    model.eval()
    ys, ps = [], []
    for q, r in loader:
        q, r = q.to(device), r.to(device)
        pred = model(q, r)
        _, y, p = masked_auc(pred, q, r)
        ys.append(y)
        ps.append(p)
    y = np.concatenate(ys) if ys else np.array([])
    p = np.concatenate(ps) if ps else np.array([])
    if len(y) < 2 or len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, p))


@torch.no_grad()
def predict_test(model, test_df: pd.DataFrame, kc_map: dict, device, n_kcs: int, batch_users: int = 64):
    """Causal GKT: p at t uses history 0..t-1; first event of each user is 0.5."""
    model.eval()
    d = test_df.copy()
    if "timestamp" in d.columns:
        d = d.sort_values(["user_id", "timestamp"])
    users = []
    for _, g in d.groupby("user_id", sort=False):
        users.append(
            {
                "idx": g.index.tolist(),
                "kcs": [kc_map[k] for k in g["kc_id"].values],
                "ys": g["correct"].astype(int).tolist(),
            }
        )
    preds = {i: 0.5 for u in users for i in u["idx"][:1]}
    max_len = max(len(u["kcs"]) for u in users)
    hidden_dim = model.hidden_dim
    ht = torch.zeros((len(users), n_kcs, hidden_dim), device=device)
    for t in tqdm(range(max_len - 1), desc="gkt_predict", mininterval=5):
        active = [i for i, u in enumerate(users) if len(u["kcs"]) > t + 1]
        for start in range(0, len(active), batch_users):
            ids = active[start : start + batch_users]
            q_t = torch.tensor([users[i]["kcs"][t] for i in ids], device=device)
            r_t = torch.tensor([users[i]["ys"][t] for i in ids], device=device)
            q_n = torch.tensor([users[i]["kcs"][t + 1] for i in ids], device=device)
            h_in = ht[ids]
            xt = q_t * 2 + r_t
            tmp = model._aggregate(xt, q_t, h_in, len(ids))
            h_next, _, _, _ = model._update(tmp, h_in, q_t)
            yt = model._predict(h_next, q_t)
            p = model._get_next_pred(yt, q_n).detach().cpu().tolist()
            ht[ids] = h_next
            for j, i in enumerate(ids):
                preds[users[i]["idx"][t + 1]] = float(p[j])
    return np.array([preds[i] for i in test_df.index], dtype=float)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="assist2012")
    p.add_argument("--split", default="learner_based")
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--graph", choices=["train_only", "full_log"], default="train_only")
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--patience", type=int, default=4)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--max-seq-len", type=int, default=100)
    p.add_argument("--hidden-dim", type=int, default=32)
    p.add_argument("--emb-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--predict-only", action="store_true")
    args = p.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    tag = f"gkt_{args.graph}"
    pred_path = ROOT / "results" / "predictions" / (
        f"{args.dataset}_{args.split}_{tag}_seed{args.seed}.csv"
    )
    ckpt_path = ROOT / "results" / "checkpoints" / (
        f"{args.dataset}_{args.split}_{tag}_seed{args.seed}.pt"
    )
    if pred_path.exists() and pred_path.stat().st_size > 1000:
        print(f"skip complete {pred_path}", flush=True)
        return

    base = ROOT / "data" / "processed" / args.dataset / "splits" / args.split / f"fold_{args.fold}"
    train_df = pd.read_csv(base / "train.csv")
    valid_df = pd.read_csv(base / "valid.csv")
    test_df = pd.read_csv(base / "test.csv")
    all_kcs = sorted(pd.concat([train_df["kc_id"], valid_df["kc_id"], test_df["kc_id"]]).unique())
    kc_map = {k: i for i, k in enumerate(all_kcs)}
    n_kcs = len(kc_map)
    print(f"n_kcs={n_kcs} train={len(train_df)} test={len(test_df)} device={device}", flush=True)

    graph_dir = ROOT / "results" / "graphs" / f"{args.dataset}_{args.split}_fold{args.fold}"
    graphs = build_graphs(train_df, valid_df, test_df, kc_map, graph_dir)
    print("G-L9 stats", graphs["stats"], flush=True)
    graph = graphs[args.graph].to(device)

    from pykt.models.gkt import GKT

    model = GKT(
        n_kcs,
        hidden_dim=args.hidden_dim,
        emb_size=args.emb_size,
        graph_type="transition",
        graph=graph,
        dropout=0.5,
        emb_type="qid",
    ).to(device)

    train_loader = valid_loader = opt = None
    if not args.predict_only:
        train_loader = DataLoader(
            SeqDataset(train_df, kc_map, args.max_seq_len),
            batch_size=args.batch_size,
            shuffle=True,
            collate_fn=collate,
            num_workers=0,
        )
        valid_loader = DataLoader(
            SeqDataset(valid_df, kc_map, args.max_seq_len),
            batch_size=args.batch_size,
            shuffle=False,
            collate_fn=collate,
            num_workers=0,
        )
        opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    best_auc, bad, best_state = -1.0, 0, None
    if args.predict_only:
        if not ckpt_path.exists():
            raise SystemExit(f"missing checkpoint {ckpt_path}")
        best_state = torch.load(ckpt_path, map_location="cpu")
        print(f"predict-only from {ckpt_path}", flush=True)
    else:
        for epoch in range(1, args.epochs + 1):
            t0 = time.time()
            tr_loss = train_one_epoch(model, train_loader, opt, device)
            va_auc = eval_auc(model, valid_loader, device)
            print(
                f"epoch {epoch} loss={tr_loss:.4f} valid_auc={va_auc:.4f} sec={time.time()-t0:.1f}",
                flush=True,
            )
            if va_auc > best_auc:
                best_auc, bad = va_auc, 0
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                torch.save(best_state, ckpt_path)
            else:
                bad += 1
                if bad >= args.patience:
                    print("early stop", flush=True)
                    break

    if best_state is not None:
        model.load_state_dict(best_state)
        model.to(device)

    print("predict test...", flush=True)
    p_pred = predict_test(model, test_df, kc_map, device, n_kcs)
    out = test_df.copy()
    out["dataset"] = args.dataset
    out["split_mode"] = args.split
    out["model"] = tag
    out["seed"] = args.seed
    out["p_pred"] = p_pred
    out["y_true"] = out["correct"]
    cols = [
        "dataset",
        "split_mode",
        "model",
        "seed",
        "user_id",
        "item_id",
        "kc_id",
        "timestamp",
        "y_true",
        "p_pred",
    ]
    pred_path.parent.mkdir(parents=True, exist_ok=True)
    out[cols].to_csv(pred_path, index=False)
    print(f"wrote {pred_path} n={len(out)} best_valid_auc={best_auc:.4f}", flush=True)


if __name__ == "__main__":
    main()
