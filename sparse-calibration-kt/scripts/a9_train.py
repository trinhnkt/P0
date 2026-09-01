#!/usr/bin/env python3
"""
A9 retrain DKT / SimpleKT on downsampled training folds.

Writes results/predictions/a9_*.csv only. Official prediction CSVs are not touched.

Prediction is prefix-equivalent to predict_sequential but runs one batched
forward per user-batch (LSTM / causal Transformer), checkpoints the model,
and flushes a .pred.npy so a killed job can resume without a silent 11h loss.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

ROOT = Path(".").resolve()
sys.path.append(str(ROOT))

from src.baseline_runner import DKT, SimpleKT, KTDataset, collate_fn, predict_sequential  # noqa: E402

SPLIT = "learner_based"
FOLD = 0
TEST_N = {
    "assist2012": 534_150,
    "junyi": 3_269_022,
    "xes3g5m": 1_589_145,
}


def data_dir(dataset: str, level: str) -> Path:
    if level == "full":
        return ROOT / "data" / "processed" / dataset / "splits" / SPLIT / f"fold_{FOLD}"
    return ROOT / "data" / "processed" / "a9" / dataset / level / SPLIT / f"fold_{FOLD}"


def pred_out(dataset: str, level: str, model: str, seed: int) -> Path:
    d = ROOT / "results" / "predictions"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"a9_{dataset}_{SPLIT}_{model}_{level}_seed{seed}.csv"


def ckpt_out(dataset: str, level: str, model: str, seed: int) -> Path:
    d = ROOT / "results" / "checkpoints"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"a9_{dataset}_{SPLIT}_{model}_{level}_seed{seed}.pt"


def npy_out(csv_path: Path) -> Path:
    return csv_path.with_name(csv_path.stem + ".pred.npy")


def count_csv_rows(path: Path) -> int:
    with path.open("rb") as f:
        return max(sum(1 for _ in f) - 1, 0)


def csv_is_complete(path: Path, dataset: str, n_test: int | None = None) -> bool:
    need = n_test if n_test is not None else TEST_N.get(dataset)
    if not path.exists() or path.stat().st_size < 10_000:
        return False
    if need is None:
        return False
    return count_csv_rows(path) >= need


def train_with_patience(model, train_loader, valid_loader, device, n_epochs=50, lr=1e-3, patience=10):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = torch.nn.BCELoss(reduction="none")
    best_valid_auc = -1.0
    best_state = None
    wait = 0
    from sklearn.metrics import roc_auc_score

    for epoch in range(1, n_epochs + 1):
        model.train()
        for feats, labels, kcs in train_loader:
            feats, labels, kcs = feats.to(device), labels.to(device), kcs.to(device)
            optimizer.zero_grad()
            preds = model(feats)
            preds_flat = preds.view(-1, model.n_kcs)
            kcs_flat = kcs.view(-1)
            labels_flat = labels.view(-1)
            mask = labels_flat != -1
            target_preds = preds_flat[torch.arange(preds_flat.size(0)), kcs_flat.clamp(min=0)]
            loss = criterion(target_preds[mask], labels_flat[mask]).mean()
            loss.backward()
            optimizer.step()

        model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for feats, labels, kcs in valid_loader:
                feats, labels, kcs = feats.to(device), labels.to(device), kcs.to(device)
                preds = model(feats)
                preds_flat = preds.view(-1, model.n_kcs)
                kcs_flat = kcs.view(-1)
                labels_flat = labels.view(-1)
                mask = labels_flat != -1
                target_preds = preds_flat[torch.arange(preds_flat.size(0)), kcs_flat.clamp(min=0)]
                all_preds.extend(target_preds[mask].cpu().numpy())
                all_labels.extend(labels_flat[mask].cpu().numpy())
        valid_auc = float("nan")
        if len(all_labels) and len(np.unique(all_labels)) > 1:
            valid_auc = float(roc_auc_score(all_labels, all_preds))
        improved = valid_auc > best_valid_auc
        if improved:
            best_valid_auc = valid_auc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
        print(f"    epoch {epoch:02d} val_auc={valid_auc:.4f} best={best_valid_auc:.4f} wait={wait}", flush=True)
        if wait >= patience:
            print("    early stop", flush=True)
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    return model, best_valid_auc


def _user_groups(test_df: pd.DataFrame, kc_map: dict):
    if "timestamp" in test_df.columns:
        sorted_df = test_df.sort_values(["user_id", "timestamp"])
    else:
        sorted_df = test_df.sort_values("user_id")
    users = []
    for _, group in sorted_df.groupby("user_id", sort=True):
        kcs = np.array([kc_map[k] for k in group["kc_id"].values], dtype=np.int64)
        labels = group["correct"].to_numpy()
        row_indices = group.index.to_numpy()
        state_feats = (kcs * 2 + labels.astype(np.int64)).astype(np.int64)
        users.append(
            {
                "kcs": kcs,
                "state_feats": state_feats,
                "row_indices": row_indices,
                "len": int(len(group)),
            }
        )
    users.sort(key=lambda u: -u["len"])
    return users


def _hidden_then_gather(hidden, fc, kcs_pad, lengths, device):
    """hidden: (B, L, H) after seeing feats[:, :t+1]; pred[t+1] uses kcs[:, t+1]."""
    w = fc.weight
    b = fc.bias
    kcs_next = kcs_pad[:, 1:]
    h_prev = hidden[:, :-1, :]
    w_sel = w[kcs_next]
    bias_sel = b[kcs_next]
    logits = (h_prev * w_sel).sum(-1) + bias_sel
    probs = torch.sigmoid(logits)
    out = []
    for i, n in enumerate(lengths):
        row = np.empty(n, dtype=np.float32)
        row[0] = 0.5
        if n > 1:
            row[1:] = probs[i, : n - 1].detach().cpu().numpy()
        out.append(row)
    return out


def _forward_hidden(model, model_name, feat_pad):
    embedded = model.embed(feat_pad)
    if model_name == "dkt":
        hidden, _ = model.lstm(embedded)
        return hidden
    seq_len = feat_pad.size(1)
    attn_mask = torch.triu(
        torch.full((seq_len, seq_len), float("-inf"), device=feat_pad.device, dtype=embedded.dtype),
        diagonal=1,
    )
    return model.transformer(embedded, mask=attn_mask)


def _run_user_batch(model, model_name, batch, device):
    max_len = max(u["len"] for u in batch)
    bsz = len(batch)
    feat_pad = torch.zeros((bsz, max_len), dtype=torch.long, device=device)
    kcs_pad = torch.zeros((bsz, max_len), dtype=torch.long, device=device)
    lengths = []
    for i, u in enumerate(batch):
        n = u["len"]
        lengths.append(n)
        feat_pad[i, :n] = torch.as_tensor(u["state_feats"], device=device)
        kcs_pad[i, :n] = torch.as_tensor(u["kcs"], device=device)
    hidden = _forward_hidden(model, model_name, feat_pad)
    return _hidden_then_gather(hidden, model.fc, kcs_pad, lengths, device)


def _user_done(p_pred: np.ndarray, row_indices: np.ndarray) -> bool:
    return bool(np.isfinite(p_pred[row_indices]).all())


def predict_fast(model, test_df, kc_map, device, model_name: str, npy_path: Path) -> np.ndarray:
    """Prefix-equivalent batched predict; flushes npy_path after each user batch."""
    model.eval()
    n = len(test_df)
    if npy_path.exists():
        p_pred = np.load(npy_path)
        if p_pred.shape != (n,):
            print(f"  discard mismatched npy {p_pred.shape} vs n={n}", flush=True)
            p_pred = np.full(n, np.nan, dtype=np.float32)
    else:
        p_pred = np.full(n, np.nan, dtype=np.float32)

    users = _user_groups(test_df, kc_map)
    pending = [u for u in users if not _user_done(p_pred, u["row_indices"])]
    n_users = len(users)
    n_done_users = n_users - len(pending)
    print(
        f"  predict_fast users={n_users} pending={len(pending)} already={n_done_users} "
        f"model={model_name}",
        flush=True,
    )
    max_tokens = 200_000 if model_name == "dkt" else 12_000
    t0 = time.time()
    i = 0
    batches = 0
    with torch.no_grad():
        while i < len(pending):
            batch = [pending[i]]
            max_len = pending[i]["len"]
            i += 1
            while i < len(pending):
                new_max = max(max_len, pending[i]["len"])
                if new_max * (len(batch) + 1) > max_tokens:
                    break
                batch.append(pending[i])
                max_len = new_max
                i += 1
            rows = _run_user_batch(model, model_name, batch, device)
            for u, row in zip(batch, rows):
                p_pred[u["row_indices"]] = row
            batches += 1
            n_done_users += len(batch)
            if batches == 1 or batches % 5 == 0 or i >= len(pending):
                tmp = npy_path.with_suffix(".tmp.npy")
                np.save(tmp, p_pred)
                tmp.replace(npy_path)
                elapsed = time.time() - t0
                print(
                    f"    users {n_done_users}/{n_users} batches={batches} "
                    f"last_len={max_len} batch_n={len(batch)} {elapsed:.0f}s",
                    flush=True,
                )
            if model_name == "simplekt" and max_len > 2000:
                torch.cuda.empty_cache()
    if not np.isfinite(p_pred).all():
        raise RuntimeError(f"incomplete predictions: nan={int(np.isnan(p_pred).sum())}/{n}")
    np.save(npy_path, p_pred)
    return p_pred


def predict_sequential_ckpt(model, test_df, kc_map, device, npy_path: Path, batch_size=2048):
    """Same loop as predict_sequential, with progress and npy resume (for SimpleKT)."""
    if len(test_df) == 0:
        return np.array([])
    model.eval()
    n = len(test_df)
    step_path = npy_path.with_name(npy_path.stem + ".step")
    if "timestamp" in test_df.columns:
        test_df_sorted = test_df.sort_values(["user_id", "timestamp"])
    else:
        test_df_sorted = test_df.sort_values("user_id")
    users_data = []
    for _, group in test_df_sorted.groupby("user_id", sort=True):
        kcs = [kc_map[k] for k in group["kc_id"].values]
        labels = group["correct"].values
        row_indices = group.index.tolist()
        state_feats = [kcs[i] * 2 + int(labels[i]) for i in range(len(group))]
        users_data.append(
            {
                "kcs": kcs,
                "labels": labels,
                "row_indices": row_indices,
                "state_feats": state_feats,
                "len": len(group),
            }
        )
    max_len = max(u["len"] for u in users_data)
    if npy_path.exists() and step_path.exists():
        p_pred = np.load(npy_path)
        last_step = int(step_path.read_text().strip())
        if p_pred.shape != (n,):
            p_pred = np.full(n, np.nan, dtype=np.float32)
            last_step = 0
    else:
        p_pred = np.full(n, np.nan, dtype=np.float32)
        last_step = 0
    if last_step == 0:
        for u in users_data:
            p_pred[u["row_indices"][0]] = 0.5
    start = 1 if last_step == 0 else last_step + 1
    print(
        f"  predict_sequential_ckpt users={len(users_data)} max_len={max_len} "
        f"resume_from={start}",
        flush=True,
    )
    t0 = time.time()

    def flush(step_idx: int):
        tmp = npy_path.with_suffix(".tmp.npy")
        np.save(tmp, p_pred)
        tmp.replace(npy_path)
        step_path.write_text(str(step_idx))

    def step_bs(step_idx: int, n_active: int) -> int:
        # TransformerEncoderLayer ffn=2048; cap tokens so (B, L) does not OOM.
        max_tokens = 4096
        return max(2, min(batch_size, n_active, max_tokens // max(step_idx, 1)))

    with torch.no_grad():
        for step_idx in range(start, max_len):
            active_users = [u for u in users_data if u["len"] > step_idx]
            if not active_users:
                break
            bs = step_bs(step_idx, len(active_users))
            for start_u in range(0, len(active_users), bs):
                sub_batch = active_users[start_u : start_u + bs]
                inp_list = [u["state_feats"][:step_idx] for u in sub_batch]
                inp_tensor = torch.tensor(inp_list, dtype=torch.long, device=device)
                target_kcs = [u["kcs"][step_idx] for u in sub_batch]
                out = model(inp_tensor)
                preds = out[torch.arange(len(sub_batch), device=device), -1, target_kcs]
                preds = preds.detach().cpu().numpy()
                del out, inp_tensor
                for idx, u in enumerate(sub_batch):
                    p_pred[u["row_indices"][step_idx]] = float(preds[idx])
            if step_idx == start or step_idx % 10 == 0 or step_idx == max_len - 1:
                print(
                    f"    step {step_idx}/{max_len - 1} active={len(active_users)} "
                    f"bs={bs} {time.time() - t0:.0f}s",
                    flush=True,
                )
            if step_idx % 50 == 0:
                flush(step_idx)
            if step_idx % 20 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()
    flush(max_len - 1)
    if not np.isfinite(p_pred).all():
        raise RuntimeError(f"incomplete sequential preds nan={int(np.isnan(p_pred).sum())}/{n}")
    return p_pred


def write_pred_csv(test_df, p_pred, dataset, level, model_name, seed, out: Path):
    pred_df = test_df.copy()
    pred_df["dataset"] = dataset
    pred_df["split_mode"] = SPLIT
    pred_df["model"] = model_name
    pred_df["seed"] = seed
    pred_df["a9_level"] = level
    pred_df["p_pred"] = p_pred
    pred_df["y_true"] = pred_df["correct"]
    cols = [
        "dataset", "split_mode", "model", "seed", "a9_level",
        "user_id", "item_id", "kc_id", "timestamp", "y_true", "p_pred",
    ]
    tmp = out.with_suffix(".tmp.csv")
    pred_df[cols].to_csv(tmp, index=False)
    tmp.replace(out)


def make_model(model_name: str, n_kcs: int, device):
    if model_name == "dkt":
        return DKT(n_kcs).to(device)
    if model_name == "simplekt":
        return SimpleKT(n_kcs).to(device)
    raise ValueError(model_name)


def run_one(dataset: str, level: str, model_name: str, seed: int, epochs: int, patience: int, batch_size: int):
    out = pred_out(dataset, level, model_name, seed)
    ckpt = ckpt_out(dataset, level, model_name, seed)
    npy_path = npy_out(out)

    base = data_dir(dataset, level)
    test_n_expected = TEST_N.get(dataset)
    if csv_is_complete(out, dataset):
        print(f"SKIP complete {out.name} rows={count_csv_rows(out)}", flush=True)
        return

    if out.exists():
        n = count_csv_rows(out)
        print(f"REMOVE truncated {out.name} rows={n} expected={test_n_expected}", flush=True)
        out.unlink()

    test_df = pd.read_csv(base / "test.csv")
    n_test = len(test_df)
    print(f"Loaded test {dataset} {level}: n={n_test}", flush=True)
    if test_n_expected is not None and n_test != test_n_expected:
        print(f"WARNING test rows {n_test} != expected {test_n_expected}", flush=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)
    t0 = time.time()

    if ckpt.exists():
        blob = torch.load(ckpt, map_location=device, weights_only=False)
        n_kcs = int(blob["n_kcs"])
        kc_map = blob["kc_map"]
        model = make_model(model_name, n_kcs, device)
        model.load_state_dict(blob["state_dict"])
        best_auc = float(blob.get("best_valid_auc", float("nan")))
        print(f"  loaded checkpoint {ckpt.name} best_val={best_auc:.4f}", flush=True)
    else:
        train_df = pd.read_csv(base / "train.csv")
        valid_df = pd.read_csv(base / "valid.csv")
        print(
            f"Loaded {dataset} {level}: train={len(train_df)} valid={len(valid_df)} test={n_test}",
            flush=True,
        )
        all_kcs = sorted(pd.concat([train_df["kc_id"], valid_df["kc_id"], test_df["kc_id"]]).unique())
        kc_map = {kc: i for i, kc in enumerate(all_kcs)}
        n_kcs = len(all_kcs)
        torch.manual_seed(seed)
        np.random.seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        train_ds = KTDataset(train_df, kc_map)
        valid_ds = KTDataset(valid_df, kc_map)
        train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
        valid_loader = DataLoader(valid_ds, batch_size=batch_size, shuffle=False, collate_fn=collate_fn)
        model = make_model(model_name, n_kcs, device)
        model, best_auc = train_with_patience(
            model, train_loader, valid_loader, device, n_epochs=epochs, patience=patience
        )
        torch.save(
            {
                "state_dict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
                "n_kcs": n_kcs,
                "kc_map": kc_map,
                "best_valid_auc": best_auc,
                "model_name": model_name,
            },
            ckpt,
        )
        print(f"  saved checkpoint {ckpt.name}", flush=True)

    if npy_path.exists():
        arr = np.load(npy_path)
        if arr.shape == (n_test,) and np.isfinite(arr).all():
            print(f"  npy complete, writing CSV only", flush=True)
            write_pred_csv(test_df, arr, dataset, level, model_name, seed, out)
            print(f"  saved {out} rows={count_csv_rows(out)} in {(time.time()-t0)/60:.1f} min", flush=True)
            return

    print(f"  predicting ({time.time()-t0:.0f}s so far)", flush=True)
    if model_name == "dkt":
        p_pred = predict_fast(model, test_df, kc_map, device, model_name, npy_path)
    else:
        p_pred = predict_sequential_ckpt(model, test_df, kc_map, device, npy_path)
    write_pred_csv(test_df, p_pred, dataset, level, model_name, seed, out)
    n_written = count_csv_rows(out)
    print(f"  saved {out} rows={n_written} in {(time.time()-t0)/60:.1f} min", flush=True)
    if n_written < n_test:
        raise RuntimeError(f"incomplete CSV {n_written} < {n_test}")


def verify_fast(n_users: int = 8):
    """Check batched predict matches predict_sequential on a tiny random model."""
    base = data_dir("assist2012", "t50")
    if not (base / "test.csv").exists():
        base = data_dir("junyi", "t500")
    test_df = pd.read_csv(base / "test.csv")
    keep_users = test_df["user_id"].drop_duplicates().head(n_users)
    test_df = test_df[test_df["user_id"].isin(keep_users)].copy().reset_index(drop=True)
    all_kcs = sorted(test_df["kc_id"].unique())
    kc_map = {kc: i for i, kc in enumerate(all_kcs)}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(0)
    model = DKT(len(all_kcs)).to(device).eval()
    npy_path = ROOT / "results" / "checkpoints" / "_verify_fast.pred.npy"
    npy_path.parent.mkdir(parents=True, exist_ok=True)
    if npy_path.exists():
        npy_path.unlink()
    fast = predict_fast(model, test_df, kc_map, device, "dkt", npy_path)
    seq = predict_sequential(model, test_df, kc_map, device)
    max_abs = float(np.max(np.abs(fast - seq)))
    print(f"verify DKT max_abs={max_abs:.8f} n={len(test_df)}", flush=True)
    if npy_path.exists():
        npy_path.unlink()
    if max_abs > 1e-4:
        raise SystemExit("DKT predict_fast does not match predict_sequential")
    print("verify_fast OK (DKT batched; SimpleKT uses sequential+ckpt)", flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", choices=["assist2012", "junyi", "xes3g5m"])
    p.add_argument("--level", choices=["t500", "t100", "t50"])
    p.add_argument("--model", choices=["dkt", "simplekt"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--verify-fast", action="store_true")
    args = p.parse_args()
    if args.verify_fast:
        verify_fast()
        return
    if not args.dataset or not args.level or not args.model:
        p.error("--dataset --level --model are required unless --verify-fast")
    run_one(args.dataset, args.level, args.model, args.seed, args.epochs, args.patience, args.batch_size)


if __name__ == "__main__":
    main()
