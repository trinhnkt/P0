# Analysis copies (not new experiments)

Locked artifacts copied for revision work. Source of truth remains the repo paths named below. Do not edit numbers here and then treat them as a new run.

| File | Source |
|------|--------|
| `four_partition_punchline_ece.csv` | `analysis/four_partition/punchline_ece.csv` |
| `summary_4part_bucket.csv` | `analysis/four_partition/summary_4part_bucket.csv` |
| `c2_fivefold_verdict.txt` | `analysis/direction_c/c2_fivefold_verdict.txt` (locked CI [0.006, 0.138]) |
| `ijiet08_*.csv` | `IJIET_SUBMISSION/audit/` gate recoveries |

## XES3G5M source of truth (A2B, padding excluded)

Do not re-derive manuscript XES ECE/FAR/Miss from `c2_fivefold_verdict.txt` or from unmasked four-partition CSVs. Use `a2b/analysis/` (`c2_xes_verdict.txt`, `summary_4part_*.csv`, `a9/statistical_summary.csv`). ASSISTments locked CI in `c2_fivefold_verdict.txt` is unchanged.
