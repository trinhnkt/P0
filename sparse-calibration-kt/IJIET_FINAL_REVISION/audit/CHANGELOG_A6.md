# CHANGELOG_A6 — align model naming with LEVEL 3 evidence

**Date:** 2026-09-01  
**Prerequisite:** A5 `SIMPLEKT_IMPLEMENTATION_AUDIT.md` — **LEVEL 3 — GENERIC TRANSFORMER BASELINE**.  
**Retrain:** no. **Numeric cells:** unchanged.

## Verdict applied

The local `src/baseline_runner.py` class `SimpleKT` is **not** the published SimpleKT architecture `[4]` (Liu et al., ICLR 2023). Manuscript results are therefore **not** attributed to published SimpleKT.

| Role | Name in this revision |
|------|------------------------|
| Published architecture / citation `[4]` | SimpleKT (literature and bibliography only) |
| Local model scored in Tables 3–8 | **Transformer KT baseline**, abbreviated **T-KT** after first definition |

Source class name `SimpleKT` is unchanged (identity audit, not a rename of code).

## Why “T-KT” rather than spelling “Transformer KT” in every cell

Spelling **Transformer KT** in all former SimpleKT slots (prose + tables) overflowed the IJIET 8-page lock to **9 pages**. After defining **Transformer KT baseline (T-KT)** in the Abstract and Methods, remaining result language and Tables 2–8 use **T-KT**. That recovered **8 pages**. Numerals were not edited to fit.

## Manuscript edits (no numeric changes)

- **Abstract:** IRT, DKT, and a Transformer KT baseline (T-KT). Result sentences that previously said SimpleKT now say T-KT (ECE 0.114→0.228; FAR 0.196→0.268 unchanged).
- **Introduction:** T-KT for local results; no attribution of those numbers to `[4]`.
- **Related Work:** cites **published SimpleKT `[4]`** as literature. Does **not** attach Section IV scores to that paper. (A longer “Section IV scores a local…” sentence was tried and **removed** because it broke the page lock.)
- **Methods (III.C / Table 2):** “Main tables use local IRT, DKT, and a Transformer KT baseline (T-KT)… The Transformer KT baseline is a two-layer Transformer encoder over DKT-style KC-response tokens, not the published SimpleKT architecture `[4]`.” Table 2 header **T-KT** / Implementation **local T-KT**.
- **Tables 3–8:** model rows and Table 4 caption **T-KT**. Locked ASSISTments cells still `0.1136`, `0.2280`, FAR `0.196` / `0.268`, ΔFAR `0.047`, seed-42 CI `[0.006, 0.138]`.
- **Discussion / Conclusion:** T-KT for local ECE/FAR associations.
- **Figure legends:** Fig. 1 has no model name (frequency-stratum figure only); no SimpleKT rename needed.

## SimpleKT leftovers (intentional)

Exactly three remaining hits, none of them result cells:

1. Related Work: “published SimpleKT `[4]`”
2. Methods: “not the published SimpleKT architecture `[4]`”
3. Bibliography title of Liu et al. (2023)

## What this task did not do

- Did not change any numeric value.
- Did not apply A2B XES cells.
- Did not retrain or rename the Python class.
- Did not claim the local encoder is published SimpleKT or an official checkpoint.

## Files

- `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx`
- `IJIET_FINAL_REVISION/output/main_ijiet_full.pdf` (8 pages; compile checks `ece_1136`, `ece_2280`, `far_196`, `far_268` true)
- `IJIET_FINAL_REVISION/apply_a6_word.py` (Word Find/Replace helper)
- `IJIET_FINAL_REVISION/audit/SCIENTIFIC_LOCKS.md` (lock **labels** T-KT; numbers unchanged)
- `IJIET_FINAL_REVISION/supplementary/TABLE_S1_MODEL_SETTINGS.md` (already LEVEL 3 from A5)
- this changelog

Backup before first A6 Word pass: `manuscript/main_ijiet_full.docx.bak_pre_a6`.

## STOP
