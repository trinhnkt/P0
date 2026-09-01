# IJIET-06 — Related Work restructuring

**Date:** 2026-08-31  
**Scope:** Section II (Literature Review) only, plus two verified corrections in the existing numbered reference list.  
**Working file:** `IJIET_SUBMISSION/source/main_ijiet_step06.docx` (copied from step05).  
**Not modified:** Abstract; Methods onward (including Results tables/figure); originals under `ijiet/` and `paper/`.

---

## Structure (IJIET Heading 2 A.–D.)

- **A. Knowledge Tracing and benchmark models** — BKT `[1]`, IRT/Rasch `[6]`, DKT `[2]`, attention KT `[7]`, SimpleKT `[4]`, pyKT `[5]`, survey `[3]`.
- **B. Graph and self-supervised KT** — GKT `[8]`, CL4KT `[9]`; stated as related architectures, not this paper’s contribution.
- **C. Sparse-data and cold-start problems** — four senses: sparse attention; sparse KC frequency; new-student cold start; concept-level zero-frequency cold start. Explicit sentences: sparseKT-style sparse attention is **not** equivalent to low-frequency KCs `[16]`; new-student cold start is **not** the same as concept-level zero-frequency cold start `[17]`.
- **D. Calibration and educational decision support** — ECE `[12]`, Brier `[13]`, reliability diagrams `[14]`, probability-level evaluation `[10]`, `[11]`; Yan `[15]` as complementary post-hoc work only.

Closing paragraph (no fifth heading): existing KT benchmarks mainly emphasize aggregate discrimination; sparse frequency, calibration, sample support, and threshold-based decision error are rarely examined together.

No fourth research question. No new architecture / calibrator / auditing-theory claim.

## References

- No new numbered citation. Section II uses `[1]`–`[17]`, `[20]` only.
- Corrected `[5]` (NeurIPS 2022 = 36th, not 37th) and `[9]` (last author S. Park, not D. Choi). See `REFERENCE_AUDIT_RELATED_WORK.md`.

## Insertion-order note

`InsertParagraphBefore` the next Heading 1 **appends**. Step05 had used `reversed(...)`, which inverted Section I in the step05 snapshot. Step06 re-inserts the **same** IJIET-05 Introduction wording in reading order. Wording of Section I was not rewritten.

## Compile

`IJIET_SUBMISSION/output/main_ijiet_step06.pdf` — OK (5 pages, 3671 words, 6 tables, 1 figure). Results probe still present. Methods Heading 2 still restarts at A.
