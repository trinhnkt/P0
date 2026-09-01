# Preregistration language audit

**Date:** 2026-09-01  
**Scope:** `IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx` and `IJIET_FINAL_REVISION/supplementary/` (Table S1, Table S2, Table S regression).  
**Not in scope for wording edits:** `paper/`, `REV_REVIEWER_CALIBRATION_v1/`, `IJIET_SUBMISSION/`.

Search terms: `pre-registered`, `preregistered`, `pre-registration`, `preregistration` (case-insensitive; hyphen optional).

## Verdict

**No formal preregistration exists** for this study. There is no OSF, AsPredicted, ClinicalTrials, Registered Report, or other independently timestamped public registry record in the manuscript, supplementary files, or repository.

Internal markdown files (`controlled_sparsification_protocol.md`, `analysis/direction_a_preregister.md`, `analysis/direction_c_preregister.md`) are lab lock notes. They are **not** treated as formal preregistration. A rule that existed before analysis is not, by itself, a preregistration.

## Occurrences (before A9)

| # | Location | Quote (abridged) | External/timestamped evidence? | Action |
|---|----------|------------------|--------------------------------|--------|
| 1 | Results IV.A (Junyi empty sparse bucket) | “empty under the **pre-registered** cuts” | None. Frequency bins \(f=0\), \(20\), \(100\), \(500\) are a protocol choice. | Replaced with **pre-specified** cuts. |
| 2 | Results IV.D (controlled sparsification) | “**pre-registered** selection, seed 42, fold 0” | None. Eligible-KC rule is in `controlled_sparsification_protocol.md` (local file). That sentence had already been dropped when A8 replaced the surrounding paragraph. | Restored the selection-rule description **without** the word pre-registered. Preferred sentence added (rule unchanged: 30 originally dense KCs, \(f_{\mathrm{train}}\ge 500\), seed 42, fold 0). |

Supplementary Table S1, Table S2, and Table S regression: **zero** hits.

## Adjacent wording (not an exact search term)

| Location | Quote | Note |
|----------|-------|------|
| IV.D / Table 7 prose | “under the **registered** thresholds” (A7 C1–C2 sentence) | Could be read as a registry. Changed to **protocol** thresholds. Same occupancy/frequency cuts; not a new rule. |
| Table 8 caption | “**pre-declared** endpoint rule” | Display rule for which A8 cells appear in the main paper (500 and 50; 100 in S2). Not a claim of OSF preregistration. **Left unchanged.** |
| `audit/SCIENTIFIC_LOCKS.md` | “No ‘pre-registered’ selection rule without a verifiable preregistration.” | Prohibition, not a manuscript claim. **Left unchanged.** |

## What was not changed

- Frequency cuts \(\{0, 20, 100, 500\}\).
- Sparsification eligibility: dense \(f_{\mathrm{train}}\ge 500\), Limited test support, both labels, difficulty-tertile subsample of 30 KCs, seed 42, fold 0.
- Locked ASSISTments ECE/FAR numerals.

## After A9

Manuscript body: **zero** remaining hits for the four search terms.  
Supplementary: still **zero**.
