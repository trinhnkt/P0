# IJIET_FINAL_REVISION

Isolated revision workspace. **Do not edit** `IJIET_SUBMISSION/source/` or `IJIET_SUBMISSION/output/`. Those are the accepted working sources.

| Path | Role |
|------|------|
| `manuscript/` | Working Word sources copied from the accepted pair |
| `analysis/` | Locked numeric artifacts (copies; do not treat as new experiments) |
| `audit/` | Changelogs, locks, compile reports |
| `supplementary/` | Table S1 and extra material |
| `figures/` | Fig. 1 generator and any extracted figure files |
| `tables/` | Numeric table copies used by the manuscript |
| `output/` | PDFs compiled **from this folder only** |

Target manuscript: named `main_ijiet_full` (PDF + Word) and double-blind `main_ijiet_blind` (PDF + Word). Rebuild both with `build_a16_double_blind.py` after named edits.


## Integrity

See `audit/SCIENTIFIC_LOCKS.md`. Every task writes `audit/CHANGELOG_<TASK>.md`, compiles, then **stops**.
