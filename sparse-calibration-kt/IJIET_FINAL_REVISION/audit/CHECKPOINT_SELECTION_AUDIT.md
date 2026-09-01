# Checkpoint-selection audit

**Date:** 2026-09-01  
**Retrain:** not performed. **Numeric result cells:** unchanged.

Inspected: `src/models/irt_baseline.py`; `src/baseline_runner.py` `train_torch_model` (DKT and local `SimpleKT` / T-KT); frozen copies in `audit/snapshots/`. Callers for main prediction CSVs: `src/full_baseline_runner.py`, `scripts/run_reruns.py`. Torch on this host: 2.11.0+cu128 (same family as A5). Original training image: **NOT RECOVERED**.

## Answers (main tables: IRT, DKT, T-KT)

| # | Question | IRT 1PL | DKT and local T-KT (`train_torch_model`) |
|---|----------|---------|------------------------------------------|
| 1 | Were all scheduled epochs always run? | **Yes.** `for ep in range(self.epochs)` with `epochs=10`. No `break`. | **Yes.** `for epoch in range(n_epochs)` with `n_epochs=50`. No `break`. |
| 2 | Was the final epoch used? | **Yes.** Parameters after epoch 10 are used for `predict`. | **Yes, effectively.** See aliasing note. |
| 3 | Was the checkpoint with best validation AUC restored? | **No.** Validation is never read in `fit`. | **Intended in source, not effective.** `best_state = model.state_dict()` is not cloned. On torch 2.11.0 those tensors **share storage** with live parameters, so they track the last step. `load_state_dict(best_state)` after epoch 50 is a no-op relative to the final weights. |
| 4 | Was validation AUC merely logged but not used? | Validation file is not used at all. | Validation AUC **is computed** each epoch and compared, but because `best_state` aliases live weights it **does not select** a distinct checkpoint. Test predictions therefore do not come from a stored best-valid snapshot. |
| 5 | Was patience-based early stopping implemented? | **No.** | **No** in the main loop. (Exploratory GKT/CL4KT and `scripts/a9_train.py` do use patience; those are not Table 2.) |
| 6 | Were test metrics ever used for checkpoint selection? | **No.** Test AUC is printed **after** `predict`, not used to pick weights. | **No.** `train_torch_model` never sees the test loader. `predict_sequential` runs after the epoch loop. |

## Aliasing check (torch 2.11.0+cu128)

```text
state_dict shares live params True
state_dict mutated after param update True
storage_ptr of param == storage_ptr of state_dict tensor
```

Contrast: `scripts/a9_train.py` and `scripts/a11_*_train.py` save `{k: v.detach().cpu().clone() ...}` and **do** restore a distinct best-valid checkpoint. Table 8 reduced runs used that A9 path; **Table 2 describes the main DKT/T-KT loop, not A9.**

## Table 2 wording (applied)

| Setting | IRT 1PL | DKT | T-KT |
|---------|---------|-----|------|
| Early stopping | Fixed 10 epochs; final checkpoint. | Fixed 50 epochs; final checkpoint. | Fixed 50 epochs; final checkpoint. |
| Selection metric | final checkpoint | final checkpoint | final checkpoint |

Do **not** list “validation AUC” as the DKT/T-KT selection metric: the comparison exists in source, but it does not determine the weights used for test prediction.

## What this audit did not do

- Did not retrain or rewrite `train_torch_model`.
- Did not change Tables 3–8 numbers.
- Did not treat A9 patience-10 / clone as the main-table procedure.
