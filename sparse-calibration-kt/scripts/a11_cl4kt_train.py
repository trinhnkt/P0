#!/usr/bin/env python3
"""Train CL4KT-style model on locked ASSISTments learner-based fold_0.

Contrastive augmentations use training sequences only (no test in views).
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.baseline_runner import predict_sequential  # noqa: E402
from src.models.cl4kt import CL4KT  # noqa: E402


def augment_seq(q: np.ndarray, r: np.ndarray, n_kcs: int, rng: np.random.Generator):
    q, r = q.copy(), r.copy()
    n = len(q)
    if n < 3:
        return q, r
    op = int(rng.integers(0, 4))
    if op == 0:
        m = rng.random(n) < 0.5
        q[m] = int(rng.integers(0, n_kcs))
    elif op == 1:
        keep = max(2, int(n * (1.0 - 0.3 * rng.random())))
        start = int(rng.integers(0, n - keep + 1))
        q, r = q[start : start + keep], r[start : start + keep]
    elif op == 2:
        idx = rng.choice(n, size=2, replace=False)
        a, b = int(min(idx)), int(max(idx))
        if b - a >= 2:
            perm = rng.permutation(b - a)
            q[a:b], r[a:b] = q[a:b][perm], r[a:b][perm]
    else:
        m = rng.random(n) < 0.5
        if m.any():
            q[m] = rng.integers(0, n_kcs, size=int(m.sum()))
    return q, r


class SeqDataset(Dataset):
    def __init__(self, df, kc_map, max_seq_len, n_kcs, augment: bool, seed: int = 0):
        self.n_kcs = n_kcs
        self.augment = augment
        self.rng = np.random.default_rng(seed)
        self.rows = []
        d = df.copy()
        if "timestamp" in d.columns:
            d = d.sort_values(["user_id", "timestamp"])
        for _, g in d.groupby("user_id", sort=False):
            kcs = [kc_map[k] for k in g["kc_id"].values]
            ys = g["correct"].astype(int).tolist()
            for i in range(0, len(kcs), max_seq_len):
                q = np.array(kcs[i : i + max_seq_len], dtype=np.int64)
                r = np.array(ys[i : i + max_seq_len], dtype=np.int64)
                if len(q) < 2:
                    continue
                self.rows.append((q, r))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        q, r = self.rows[i]
        if self.augment:
            q1, r1 = augment_seq(q, r, self.n_kcs, self.rng)
            q2, r2 = augment_seq(q, r, self.n_kcs, self.rng)
            return q, r, q1, r1, q2, r2
        return q, r


def pad_long(seqs, value):
    return nn.utils.rnn.pad_sequence(
        [torch.tensor(s, dtype=torch.long) for s in seqs],
        batch_first=True,
        padding_value=value,
    )


def collate_train(batch):
    q, r, q1, r1, q2, r2 = zip(*batch)
    return (
        pad_long(q, -1),
        pad_long(r, 0),
        pad_long(q1, -1),
        pad_long(r1, 0),
        pad_long(q2, -1),
        pad_long(r2, 0),
    )


def collate_eval(batch):
    q, r = zip(*batch)
    return pad_long(q, -1), pad_long(r, 0)


def feats_from_qr(q, r):
    return torch.where(q >= 0, q * 2 + r.clamp(min=0, max=1), q)


def train_epoch(model, loader, opt, device):
    model.train()
    bce = nn.BCELoss(reduction="none")
    losses = []
    for q, r, q1, r1, q2, r2 in loader:
        q, r = q.to(device), r.to(device)
        q1, r1, q2, r2 = q1.to(device), r1.to(device), q2.to(device), r2.to(device)
        opt.zero_grad()
        feats = feats_from_qr(q[:, :-1], r[:, :-1])
        pred = model(feats)
        kcs_tgt = q[:, 1:].clamp(min=0)
        labels = r[:, 1:].float()
        mask = (q[:, 1:] >= 0) & (q[:, :-1] >= 0)
        target_p = pred.gather(2, kcs_tgt.unsqueeze(-1)).squeeze(-1)
        kt_loss = bce(target_p[mask], labels[mask]).mean()
        z1 = model.pooled(feats_from_qr(q1, r1))
        z2 = model.pooled(feats_from_qr(q2, r2))
        cl = model.infonce(z1, z2)
        loss = kt_loss + model.reg_cl * cl
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
        pred = model(feats_from_qr(q[:, :-1], r[:, :-1]))
        kcs_tgt = q[:, 1:].clamp(min=0)
        labels = r[:, 1:]
        mask = (q[:, 1:] >= 0) & (q[:, :-1] >= 0)
        target_p = pred.gather(2, kcs_tgt.unsqueeze(-1)).squeeze(-1)
        ys.append(labels[mask].cpu().numpy())
        ps.append(target_p[mask].cpu().numpy())
    y = np.concatenate(ys)
    p = np.concatenate(ps)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, p))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="assist2012")
    p.add_argument("--split", default="learner_based")
    p.add_argument("--fold", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--patience", type=int, default=6)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--max-seq-len", type=int, default=100)
    p.add_argument("--hidden-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=1e-3)
    args = p.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    pred_path = ROOT / "results" / "predictions" / (
        f"{args.dataset}_{args.split}_cl4kt_seed{args.seed}.csv"
    )
    ckpt_path = ROOT / "results" / "checkpoints" / (
        f"{args.dataset}_{args.split}_cl4kt_seed{args.seed}.pt"
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
    print(f"CL4KT n_kcs={n_kcs} train={len(train_df)} device={device}", flush=True)

    model = CL4KT(n_kcs, hidden_size=args.hidden_size).to(device)
    train_loader = DataLoader(
        SeqDataset(train_df, kc_map, args.max_seq_len, n_kcs, True, args.seed),
        batch_size=args.batch_size,
        shuffle=True,
        collate_fn=collate_train,
    )
    valid_loader = DataLoader(
        SeqDataset(valid_df, kc_map, args.max_seq_len, n_kcs, False, args.seed),
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=collate_eval,
    )
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)

    best_auc, bad, best_state = -1.0, 0, None
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tr = train_epoch(model, train_loader, opt, device)
        va = eval_auc(model, valid_loader, device)
        print(f"epoch {epoch} loss={tr:.4f} valid_auc={va:.4f} sec={time.time()-t0:.1f}", flush=True)
        if va > best_auc:
            best_auc, bad = va, 0
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
    p_pred = predict_sequential(model, test_df, kc_map, device, batch_size=256)
    out = test_df.copy()
    out["dataset"] = args.dataset
    out["split_mode"] = args.split
    out["model"] = "cl4kt"
    out["seed"] = args.seed
    out["p_pred"] = p_pred
    out["y_true"] = out["correct"]
    cols = [
        "dataset", "split_mode", "model", "seed",
        "user_id", "item_id", "kc_id", "timestamp", "y_true", "p_pred",
    ]
    pred_path.parent.mkdir(parents=True, exist_ok=True)
    out[cols].to_csv(pred_path, index=False)
    print(f"wrote {pred_path} n={len(out)} best_valid_auc={best_auc:.4f}", flush=True)


if __name__ == "__main__":
    main()
