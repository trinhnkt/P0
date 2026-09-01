# Recovered training settings (IJIET-07)

Settings below are read from the training source as of this audit. **Do not treat this file as a new experimental result.** Cells that cannot be recovered from source or a locked training commit are marked **NOT RECOVERED**.

Main result tables use the **local** DKT / Transformer KT baseline / IRT implementations, not a pinned pyKT commit.

## Main baselines

| Setting | IRT 1PL | DKT | Transformer KT |
|---------|---------|-----|----------|
| Implementation source | `src/models/irt_baseline.py` | `src/baseline_runner.py` class `DKT` | `src/baseline_runner.py` class `SimpleKT` (local TransformerEncoder; **not** published SimpleKT `[4]`) |
| Model version / git commit of the training snapshot | NOT RECOVERED | NOT RECOVERED | NOT RECOVERED |
| Relationship to published code | Rasch 1PL as described in `[6]` | DKT-style LSTM `[2]`; local reimplementation | Local TransformerEncoder labelled “simpleKT” in source; **LEVEL 3** — not the published SimpleKT architecture `[4]` |
| Major hyperparameters | P(correct) = sigmoid(θ_u − β_c); L2 reg 0.01 | embed_dim=64; LSTM hidden_dim=128; Embedding(n_kcs×2+1) | embed_dim=64; TransformerEncoder 2 layers, nhead=4; Embedding(n_kcs×2+1) |
| Dropout | n/a | not set in source | not passed in source (PyTorch `TransformerEncoderLayer` default 0.1 if that constructor is used as written) |
| Optimizer | SGD | Adam | Adam |
| Learning rate | 0.01 | 1e-3 | 1e-3 |
| Weight decay (Adam) | n/a (SGD L2 0.01) | NOT RECOVERED (not passed) | NOT RECOVERED (not passed) |
| Batch size | 512 | 64 (hardcoded in `src/full_baseline_runner.py`; default 64 in `src/baseline_runner.py`) | 64 |
| Maximum sequence length | n/a (static model) | 200 (`KTDataset` default) | 200 |
| Epochs | 10 | 50 | 50 |
| Early stopping | none; all 10 epochs always run | none; all 50 epochs always run | none; all 50 epochs always run |
| Selection metric | final checkpoint (no validation) | final checkpoint (`state_dict` not cloned; best-valid restore is a no-op) | final checkpoint (`state_dict` not cloned; best-valid restore is a no-op) |
| Unseen learners (learner-based split) | constant/base-rate fallback (`expit(train-mean logit)`); \(\beta_c\) unused; AUC=0.50 in this implementation, not a generic IRT property | sequential history | sequential history |

## Exploratory models (ASSISTments 2012, seed 42 / fold 0 only)

| Setting | GKT | CL4KT-style adapter |
|---------|-----|---------------------|
| Implementation source | pyKT `pykt.models.gkt.GKT` via `scripts/a11_gkt_train.py` | local `src/models/cl4kt.py` via `scripts/a11_cl4kt_train.py` |
| Official checkpoint | n/a | **not** an official CL4KT checkpoint |
| Model version / git commit of the training snapshot | NOT RECOVERED | NOT RECOVERED |
| pyKT library commit | NOT RECOVERED | n/a |
| Graph | train-only transition graph | n/a |
| Major hyperparameters | hidden_dim=32; emb_size=32; dropout=0.5; graph_type=transition; emb_type=qid | hidden_size=64; nhead=4; nlayers=2; dropout=0.2; InfoNCE temp=0.05; reg_cl=0.1 (class defaults) |
| Optimizer | Adam | Adam |
| Learning rate | 1e-3 | 1e-3 |
| Batch size | 16 | 64 |
| Maximum sequence length | 100 | 100 |
| Epochs | 20 | 20 |
| Early stopping | patience 4 on validation AUC | patience 6 on validation AUC |
| Selection metric | best validation AUC | best validation AUC |
