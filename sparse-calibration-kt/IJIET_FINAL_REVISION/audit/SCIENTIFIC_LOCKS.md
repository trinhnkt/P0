# Scientific locks (IJIET_FINAL_REVISION)

Copied from the accepted IJIET-21 manuscript. Do not “improve” these in silence.

## Datasets and models

- Logs: ASSISTments 2012, Junyi Academy, XES3G5M.
- Main baselines: IRT, DKT, Transformer KT baseline (local implementations). Transformer KT is **not** published SimpleKT `[4]` and is **not** an official checkpoint.
- GKT / CL4KT-style: exploratory, seed 42 / fold 0, ASSISTments only. CL4KT is a protocol adapter.

## Protocol

- Train-only KC strata: strict \(f=0\); very sparse \(0<f<20\); sparse \(20\le f<100\); medium \(100\le f<500\); dense \(f\ge 500\).
- Occupancy R/L/I: descriptive flags, not inferential guarantees.
- Seeds **42, 2024, 2025, 2026, 2027**. Seeds 2025 and 2026 share one learner partition (`fold_2` = `fold_3`). Four unique partitions + five trained checkpoints. Never “five independent folds.”
- Dual numbering: four-partition ECE/AUC vs seed-42 gate cells. Do not mix.

## Locked numbers (four unique partitions unless noted)

- ASSISTments T-KT (Transformer KT baseline) ECE: dense \(0.1136\pm0.0066\) (\(N=523{,}971\) R) → medium \(0.1541\pm0.0051\) → sparse \(0.2280\pm0.0197\) (\(N=415\) L). Abstract may round dense ECE to **0.114**.
- Junyi sparse bucket: **empty**.
- XES3G5M T-KT ECE essentially flat after padding exclusion (\(0.1176\), \(0.1129\), \(0.1254\); sparse \(N=1{,}969\) R). Obsolete padded cells \(0.1145/0.1114/0.1248\) (\(N=2{,}010\)) are not used.
- Gate \(\tau=0.7\); FAR = \(P(y=0\mid p\ge\tau)\). Seed-42 T-KT FAR 0.196 dense → 0.268 sparse. Five-run \(\Delta\)FAR mean 0.047, sd 0.033.
- Locked seed-42 KC-cluster CI **[0.006, 0.138]** from `analysis/direction_c/c2_fivefold_verdict.txt`. Do not substitute a recomputed CSV CI.

## Claims that stay off

- No causal effects from observational regressions.
- Repeated KC-fold rows are not independent KCs.
- No “pre-registered” selection rule without a verifiable preregistration.
- No invented generative-AI tool versions, IRB numbers, ORCID, publisher DOI `10.18178/ijiet`, volume, or production pages.

## If a result must be recomputed

Mark the old result **obsolete**. List every downstream table, figure, and prose claim. Do not change ASSISTments or Junyi numbers merely because XES3G5M is corrected.
