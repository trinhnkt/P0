# IJIET submission summary

**Status:** camera-ready pair updated IJIET-21 (literature [21]–[22]) and ready to upload.  
**Date:** 2026-08-31

---

## Files to upload

| Role | Path | Pages | Notes |
|------|------|------:|-------|
| Named (editor / after acceptance) | `IJIET_SUBMISSION/output/main_ijiet_full.pdf` | 8 | Authors, affiliations, emails, contributions with initials |
| Double-blind review | `IJIET_SUBMISSION/output/main_ijiet_blind.pdf` | 8 | Anonymous Authors; PDF `Author` metadata blank |
| Word sources (if OJS asks `.doc`) | `source/main_ijiet_full.doc` / `.docx` and `source/main_ijiet_blind.doc` / `.docx` | — | Match the PDFs from the IJIET-19 compile |

OJS: https://ojs.ejournal.net/index.php/ijiet/submissions  
Template rule: FAQ Q3 — papers that obviously do not match the template are not considered. These files were filled from the official `IJIET_template.doc`.

**Do not re-export Word → PDF** unless the editor requires a change. Layout is brittle (1-col spans for Tables 2, 4–8 and Fig. 1).

---

## What the paper is

A **diagnostic evaluation** of KT probabilities on train-only KC-frequency strata (ASSISTments 2012, Junyi Academy, XES3G5M; IRT, DKT, SimpleKT). Not a new architecture, not a classroom RCT, not a causal frequency law.

Punchline (four unique learner partitions unless noted):

- ASSISTments SimpleKT ECE **0.114** dense → **0.228** sparse (Limited, \(N\approx 415\)); Results cells **0.1136±0.0066** / **0.2280±0.0197**.
- Simulated gate \(\tau=0.7\), seed 42: SimpleKT FAR **0.196** → **0.268**; five-run mean ΔFAR **0.047** on **five training runs / four unique partitions**.
- Junyi learner-based sparse stratum **empty**; XES3G5M SimpleKT ECE **essentially flat**.
- GKT / CL4KT: exploratory, ASSISTments fold 0 only; CL4KT is a **protocol adapter**, not an official checkpoint.

Numeric trace: `audit/FINAL_NUMERIC_AUDIT.md`. Full checklist: `audit/IJIET_FINAL_CHECKLIST.md`.

---

## Review artifact

https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/

Same URL in both PDFs. Public dumps stay with the original providers ([18]–[20]).

---

## Author / process actions (not in the PDF)

| Item | Action |
|------|--------|
| Dual submission | The JEDM manuscript in `paper/` shares these experiments. Withdraw or wait for a JEDM decision **before** IJIET upload (IJIET unpublished / not under consideration elsewhere). |
| Manuscript dates | Leave `Month date, 2026` until the journal assigns received/revised/accepted dates. Do not invent them. |
| ORCID | None on file. Add only real IDs, in the OJS form or a later proof, not fabricated in the PDF. |
| APC | USD 500 after acceptance (Scopus; not SCI), per venue site. |
| Proof-only nits (optional) | Numbered in-text “Table 2”; expand “RCT” once. Do **not** chase leftover space above Tables 5–6 with another compile unless asked. |

---

## Locked scientific wording (do not “improve” in proofs)

- Five **training runs** / four **unique learner partitions** (2025 and 2026 share a split). Never “five independent folds.”
- Gate = **simulation**, not classroom policy.
- \(y=0\) = incorrect next response, **not** latent mastery.
- Sparse AUC / sparse ECE are **not** universal.
- Occupancy R/L/I are descriptive flags.
- Do not add `INTERNATIONAL JOURNAL OF INFORMATION AND EDUCATION TECHNOLOGY`, `10.18178/ijiet…`, volume, issue, or production page numbers. Those are publisher production.

---

## Freeze

After this check, treat as immutable:

- `output/main_ijiet_full.pdf`
- `output/main_ijiet_blind.pdf`
