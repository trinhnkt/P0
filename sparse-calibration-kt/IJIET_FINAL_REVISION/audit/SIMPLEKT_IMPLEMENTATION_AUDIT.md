# SimpleKT implementation identity audit

**Date:** 2026-09-01  
**Retrain:** not performed. **Manuscript:** not edited.

Cited paper: Liu et al., *simpleKT: A Simple But Tough-to-Beat Baseline for Knowledge Tracing*, ICLR 2023 / arXiv:2302.06881 (`[4]` in the IJIET manuscript). Official code: pyKT `pykt/models/simplekt.py` (https://github.com/pykt-team/pykt-toolkit). That official file is **not** vendored in this repository; it was read from the public master branch for this audit.

Local class name is **not** used as evidence of equivalence.

## Verdict

**LEVEL 3 — GENERIC TRANSFORMER BASELINE**

The local `SimpleKT` class is a two-layer `nn.TransformerEncoder` over DKT-style KC×response tokens, with a DKT-style multi-skill sigmoid head. It does **not** implement the published simpleKT equations (Rasch/question-difficulty embeddings; query/key from KC embeddings and values from interaction embeddings; causal ordinary-attention mask; concatenated MLP prediction head). A comment in source states the naming: *Use a simple Transformer encoder layer as "simpleKT"*.

Shared hyperparameters (embed 64, 2 layers, 4 heads, seq 200, Adam \(10^{-3}\), 50 epochs in this project) do not make the architectures the same.

The manuscript already discloses a local Transformer encoder that is not an official SimpleKT checkpoint. This audit does not change that wording.

## Local implementation inspected

| Item | Location |
|------|----------|
| Model class | `src/baseline_runner.py` class `SimpleKT` (lines 32–48) |
| Dataset / encoding | same file, `KTDataset` |
| Padding | `collate_fn` |
| Loss / train loop | `train_torch_model` |
| Test decoding | `predict_sequential` |
| Instantiation | `run_experiments`; `src/full_baseline_runner.py`; `scripts/a9_train.py`; `IJIET_FINAL_REVISION/a2b/train_models.py` (imports the same class) |
| Configs | `configs/{assist,junyi,xes}_simplekt_one_seed.yaml` |

Frozen copies: `IJIET_FINAL_REVISION/audit/snapshots/`.

### Model class

```python
self.embed = nn.Embedding(n_kcs * 2 + 1, embed_dim)  # embed_dim=64
encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=4, batch_first=True)
self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
self.fc = nn.Linear(embed_dim, n_kcs)
```

`TransformerEncoderLayer` is called without `dropout` or `dim_feedforward`, so PyTorch defaults apply (`dropout=0.1`, `dim_feedforward=2048` on the machine used for this audit, torch 2.11.0).

### Embedding structure

Local: one table indexed by `kc_id * 2 + correct`, identical to local `DKT`. Padding index `0` is a **valid** token (KC 0, incorrect), not a dedicated pad id.

Published simpleKT: separate KC embedding \(\mathbf{z}_{c}\), question-difficulty \(\mathbf{m}_{q}\), KC variation \(\mathbf{v}_{c}\), response \(\mathbf{r}_{q}\):

\[\mathbf{x}_{t}=\mathbf{z}_{c_{k}}\oplus\mathbf{m}_{q_{j}}\odot\mathbf{v}_{c_{k}},\quad
\mathbf{y}_{t}=\mathbf{z}_{c_{k}}\oplus\mathbf{r}_{q_{j}}.\]

Official pyKT also has `difficult_param`, `q_embed_diff`, `qa_embed_diff`, and question ids (`n_pid`). **Absent locally.**

### Attention / transformer

Published: ordinary scaled dot-product attention with

\[\mathbf{h}_{t+1}=\mathrm{SelfAttention}(Q=\mathbf{x}_{t+1},\;K=\{\mathbf{x}_{1},\ldots,\mathbf{x}_{t}\},\;V=\{\mathbf{y}_{1},\ldots,\mathbf{y}_{t}\}).\]

Official code: custom `TransformerLayer` / `MultiHeadAttention`, causal `triu` mask, first-row zero-pad so the current response is not visible, cosine positional embedding.

Local: `self.transformer(embedded)` with **no** `src_mask`, **no** `is_causal`, **no** `src_key_padding_mask`. Attention is bidirectional over the truncated feature window. A comment says a causal mask could be added; it is not.

### Positional / difficulty components

| Component | Published / pyKT | Local |
|-----------|------------------|-------|
| Cosine (or other) positional encoding | yes | **no** |
| Question-specific difficulty \(\mathbf{m}_{q}\) | yes (defining ingredient; ablation NoDiff hurts) | **no** |
| Separate question id | yes | **no** (`item_id` unused in the class) |

### Input encoding

Local `KTDataset`: per user, tokens `kc*2+label`; chunks of `max_seq_len=200`; features `[:-1]` aligned to labels/kcs `[1:]`. This is DKT-style next-step alignment, not the published \((\mathbf{x},\mathbf{y})\) pair with question difficulty.

### Output head

Published: two-layer MLP on \([\mathbf{h}_{t+1};\mathbf{x}_{t+1}]\), then sigmoid BCE.

Local: `Linear(d, n_kcs)` then sigmoid, gather the target KC — the **DKT** head, not the simpleKT concat-MLP.

### Loss

Both use binary cross-entropy on next-response correctness. Local: `nn.BCELoss(reduction='none')` then mean over non-`−1` labels. Not a match of architecture.

### Sequence masking

| Mask | Local | Published / pyKT |
|------|-------|------------------|
| Causal / no-peek current response | no | yes (`mask=0`, zero-pad first query) |
| Padding mask | no; pad id 0 collides with a real token | pad / `sm` mask |
| Label ignore | yes (`labels == -1`) | pyKT `sm` / selectmask |

Training alignment (`features[:-1]` → `labels[1:]`) supplies some next-step structure; it does not implement the paper's attention mask.

### Hyperparameters (this project vs paper search grid)

| Setting | Local (TABLE_S1 / `train_torch_model`) | Paper / pyKT (typical) |
|---------|----------------------------------------|-------------------------|
| Optimizer | Adam \(10^{-3}\) | Adam, lr search |
| Epochs / selection | 50, best valid AUC, no patience | up to 200, early stopping |
| Batch | 64 | pyKT default often 24–256 |
| `d_model` / heads / blocks | 64 / 4 / 2 | searched; 64 / 8 / 1–2 common |
| FFN width | PyTorch default **2048** | `d_ff` often **256** |
| Dropout | default **0.1** (not passed) | searched 0.05–0.5 |
| Max length | 200 | 200 |

## Why not LEVEL 1 or LEVEL 2

- **Not LEVEL 1:** equations for \(\mathbf{x}_{t},\mathbf{y}_{t}\), the Q/K/V split, causal attention, positional encoding, and the concat-MLP head are missing.
- **Not LEVEL 2:** the remaining overlap is “uses multi-head attention at width 64.” That is shared with many KT transformers (SAKT-style, SAINT-style, generic `TransformerEncoder`). The paper’s identity is Rasch question-centric difficulty plus ordinary causal attention with distinct \(\mathbf{x}\) and \(\mathbf{y}\). The local class is closer to **DKT embeddings + vanilla TransformerEncoder** than to published simpleKT, including the official NoDiff ablation (which still keeps Q/K/V and the MLP head).

## What this task did not do

- Did not retrain.
- Did not replace the class with pyKT `simpleKT`.
- Did not edit the manuscript (existing “local SimpleKT / not official checkpoint” language is consistent with LEVEL 3).
