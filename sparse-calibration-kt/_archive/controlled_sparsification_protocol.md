# A9 Controlled Sparsification Protocol

**Pre-registered before inspecting reduced-evidence ECE/REL.**  
This is a validation experiment. It does not replace the observational analyses in A4/A5.

## Scientific question

What happens to calibration when training evidence is reduced for the *same* concept, while KC identity, concept semantics, the test set, test labels, and curriculum metadata are held fixed?

## What is held fixed

- KC identity and the processed KC vocabulary
- Validation and test CSVs (copied, never edited)
- Test labels and test instance ids
- Curriculum / item / tagging fields (not used as interventions)
- Model class (DKT, SimpleKT), architecture, and optimizer defaults

## What is changed

Only the number of *training* rows retained for selected KCs.

Non-selected KCs keep 100% of their training rows. Original `data/processed/{dataset}/splits/.../train.csv` files are never overwritten.

## Split and fold

- Split: `learner_based` (matches the main calibration tables)
- Fold: `0` (seed-42 partition)
- 100% control: existing published prediction CSVs for DKT and SimpleKT on that fold

## KC selection rule (executed before any reduced training)

A KC is **eligible** if all of the following hold on fold 0:

1. Training support is dense under the protocol threshold: \(f_{\mathrm{train}} \ge 500\).
2. Test support is at least Limited: \(N_{\mathrm{test}} \ge 100\).
3. Both labels are present in test: \(n_{\mathrm{pos}} \ge 20\) and \(n_{\mathrm{neg}} \ge 20\) (so KC-level AUC is defined).
4. The KC appears in the official seed-42 DKT and SimpleKT prediction exports.

**No filtering on ECE, REL, AUC, or any metric from a reduced-evidence run.**  
We do not keep only KCs whose observational ECE was high.

If more than 30 KCs are eligible, take a **difficulty-stratified deterministic subsample**:

- Difficulty proxy = \(1 - \bar{c}_{\mathrm{train}}\) (training-only).
- Split eligible KCs into tertiles of that proxy.
- Within each tertile, sort by `kc_id` as string and take the first 10 (or all if fewer than 10).
- Record the full eligible list and the selected list.

This stratification avoids selecting only easy or only hard KCs. It is not an outcome-based cherry-pick.

## Evidence levels

Target training counts for each selected KC (skip a target if \(f_{\mathrm{train}} \le\) target):

| Level | Keep |
|-------|------|
| `full` | all training rows (100% control) |
| `t500` | 500 rows |
| `t100` | 100 rows |
| `t50`  | 50 rows |

Targets match the protocol’s dense / sparse / near-very-sparse boundaries. Infeasible levels are not imputed.

## Downsampling

For each selected KC and each feasible target \(k\):

1. Take that KC’s training rows in original file order.
2. Draw \(k\) indices uniformly without replacement using `numpy.random.default_rng(2029)` with a per-KC salt `hash(dataset, kc_id, k) mod 2**31`.
3. Drop the complementary rows of that KC only.
4. Concatenate with all training rows of non-selected KCs.
5. Restore original row order.

Log, for every (dataset, kc, level): `n_full`, `n_keep`, `n_drop`, RNG salt.  
Optional compact kept-index parquet for selected-KC rows.

Validation and test files are byte-copied from fold 0.

## Retraining

- Models: DKT, SimpleKT
- Seeds: 42, 2024, 2025 when GPU time allows; seed 42 is the minimum
- Device: CUDA
- Max 50 epochs, Adam \(10^{-3}\), batch size 64, keep best validation AUC (same selection rule as `baseline_runner.py`)
- Early-stop patience 10 on validation AUC (A9 compute constraint; 100% control remains the published 50-epoch run)
- Predictions written to `results/predictions/a9_*` so official CSVs are not overwritten

If GPU time is insufficient for Junyi / XES3G5M, ASSISTments 2012 is the primary instantiation; other datasets keep selection + manifests and are trained as time allows.

## Metrics

Event-level on the **selected-KC test subset only** (test distribution unchanged):

AUC, ACC, NLL, RMSE, ECE (15 bins), Brier, REL, RES.

Primary outcomes: **ECE** and **REL**. AUC is reported, not optimized.

Also report the same metrics pooled across selected KCs and the mean of KC-level ECE/REL.

## Statistical analysis

For each model, dataset, and reduced level:

\[
\Delta\mathrm{ECE} = \mathrm{ECE}_{\mathrm{reduced}} - \mathrm{ECE}_{\mathrm{full}},\qquad
\Delta\mathrm{REL} = \mathrm{REL}_{\mathrm{reduced}} - \mathrm{REL}_{\mathrm{full}}
\]

- Within-KC paired differences (same KC, full vs reduced)
- 95% bootstrap CI over KCs (10{,}000 resamples, seed 2029)
- If multiple seeds: average \(\Delta\) per KC across seeds, then bootstrap KCs

A positive \(\Delta\mathrm{ECE}\) means worse calibration after reducing evidence.

## Causal language (allowed / forbidden)

Allowed: “controlled reduction of training evidence was followed by …”  
Forbidden: “real-world sparsity always causes …”, “frequency is the sole cause of miscalibration.”

## If the effect is absent or reversed

Report it. Conclude that the observational sparse-calibration pattern is likely explained partly by KC composition rather than frequency alone. That is still a result.

## Outputs

- this protocol
- selected-KC tables and downsample manifests
- A9 prediction CSVs
- `analysis/a9_kc_metrics.csv`, `analysis/a9_statistical_summary.csv`
- figure of ECE/REL vs evidence level
- manuscript appendix + discussion note
- `CHANGELOG_A9.md`
