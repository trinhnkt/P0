# REVISION_SUMMARY (A10)

**Task:** Rewrite the scientific story after A1–A9. Manuscript only.

**From:** “Sparse KCs fail; therefore our protocol is necessary.”

**To:** “Sparse training evidence does not universally degrade discrimination, but it can expose dataset-dependent calibration vulnerability. We characterize the conditions associated with this vulnerability and provide reproducible diagnostics for identifying when it matters.”

## What changed

- Title kept: it names diagnostics, not a universal sparse-failure law.
- Abstract, Introduction (gap, contributions, RQs), protocol (explanatory analyses), RQ1–RQ4, discussion, threats, conclusion rewritten to six bounded findings.
- A9 three-dataset controlled sparsification is integrated as Finding 4 (CONTROLLED_EXPERIMENT), not as a causal sparsity law.
- Overclaim audit: removed or negated *consistently* / *universally useful* / *primary vulnerability* / *proving* / *robustness confirmed* where they overreached.

## Findings (see `analysis/claim_evidence_matrix.md`)

1. Lower KC frequency ≠ universal AUC degradation (Table 5).
2. Calibration can be more sensitive than aggregate discrimination in some regimes (Table 9, ASSISTments).
3. Calibration–frequency relationship is dataset-dependent (Tables 9, 12).
4. Covariates explain part of the association (A4); same-KC downsampling increases ECE only in some cells (Table 16).
5. Sparse diagnostics are conditionally important (Tables 14–15).
6. L1–L8 is a reproducible workflow; L8 has empirical value (alignment + A7 faults).

## Files

| Role | Path |
|------|------|
| Clean manuscript | `REV_REVIEWER_CALIBRATION_v1/` (`main_jedm.tex`, `main_jedm_anonymous.tex`) |
| Pre-A10 snapshot | `REV_REVIEWER_CALIBRATION_v1/_pre_a10/` |
| Redline | `REV_REVIEWER_CALIBRATION_v1/A10_redline/` (unified diffs; latexdiff needs Perl) |
| Claim matrix | `analysis/claim_evidence_matrix.md` |
| This summary | `REVISION_SUMMARY.md` |
| Changelog | `CHANGELOG_A10.md` |
