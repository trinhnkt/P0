# Model snapshot manifest (A5)

**Date:** 2026-09-01  
**Purpose:** pin the exact local SimpleKT (and sibling DKT/IRT) code that produced the IJIET main-table runs, without retraining.

Git repository root: `C:/TRINH/Sparse-Concept and Calibration`  
Tracked path of the class: `sparse-calibration-kt/src/baseline_runner.py`  
Last commit that touched that file: `ad0884f0b5b9ed64c7c8b69499ef38c7ac11c04b` (`Lan 18`)  
HEAD at snapshot time: recorded in `CHANGELOG_A5.md` after the A5 commit.

Official simpleKT / pyKT source is **not** in this repo. Reference read for the audit: public `pykt/models/simplekt.py` on GitHub `pykt-team/pykt-toolkit` master (not hashed here; not the training code).

## SHA-256 (files as of 2026-09-01)

| SHA-256 | File |
|---------|------|
| `6da21b73e452a5e8f7341610283c84772cc6a694b293f268eeb7ce1dc55ecbab` | `src/baseline_runner.py` (class `SimpleKT`, `DKT`, `KTDataset`, train/predict) |
| `e2e88cce4614364e9cfef533d3b66e4a9909ef9e191b45d9b223234414f1d61d` | `src/full_baseline_runner.py` |
| `0c658e40c15164acd6cc87195dfad9480213f560fb5d3fbe5c3227c82e132144` | `src/models/irt_baseline.py` |
| `ddd61cff97b77eecc2f5ef5e0002a472bcf9068f2c4659a8d1a174b2f1b7a0bf` | `configs/assist_simplekt_one_seed.yaml` |
| `df3f99196ad3b3004099e8a0c39bef818d60c66be1816f46a59340c4ee8f75dd` | `configs/junyi_simplekt_one_seed.yaml` |
| `1c1ec311c1402b2448027f28dff1583545765fd438fc569f9572b47375d748e1` | `configs/xes_simplekt_one_seed.yaml` |
| `890607756a99ff4d608fb90feaf8b6e7602f1af48dbc1fef452cd1abcc959066` | `IJIET_FINAL_REVISION/a2b/train_models.py` (imports the same `SimpleKT`) |
| `1d5d201b3cb316971b0b611b8c08040a8499f5a5aba32f9e41e4a8466072beab` | `IJIET_FINAL_REVISION/supplementary/TABLE_S1_MODEL_SETTINGS.md` |

Byte-identical frozen copies:

- `IJIET_FINAL_REVISION/audit/snapshots/baseline_runner.py`
- `IJIET_FINAL_REVISION/audit/snapshots/full_baseline_runner.py`

## Environment recovered on this machine (not claimed as the original training image)

Original training-image / lockfile: **NOT RECOVERED** (TABLE_S1). Versions below are whatever this host had on 2026-09-01.

| Package | Version |
|---------|---------|
| Python | 3.14.4 (MSC v.1944, 64-bit) |
| torch | 2.11.0+cu128 (CUDA 12.8 reported; GPU available) |
| numpy | 2.4.3 |
| pandas | 2.3.3 |
| scikit-learn | 1.8.0 |
| PyYAML | 6.0.3 |

`nn.TransformerEncoderLayer` defaults on this torch: `dim_feedforward=2048`, `dropout=0.1`, `activation=relu`, `batch_first` default False (local code sets `batch_first=True`).

## Training commit

TABLE_S1: training snapshot commit **NOT RECOVERED**. This A5 git commit records the source bytes above for later runs; it does not reconstruct the 2026 training container.
