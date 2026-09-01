# A6 — Inventory of L1–L8 novelty / audit claims

Scope: `REV_REVIEWER_CALIBRATION_v1/` (shared `sections/` + both mains).  
Search terms: *new audit method*, *novel auditing framework*, *establish a new audit*, *establish … audit*, *eight-channel*, *L1–L8*, *checklist*, *introduce* (audit context), *to the best of our knowledge* (when tied to leakage audit).

Verdict key: **OVERCLAIM** = sounds like a new auditing method; **BORDERLINE** = could be read that way; **OK** = already conservative or not about L1–L8 novelty.

| # | File | Quote (abridged) | Verdict | Action |
|---|------|------------------|---------|--------|
| 1 | `sections/01_introduction.tex` C3 | “We **establish** an eight-channel leakage and predictive-sanity **audit checklist**” | **OVERCLAIM** | Replace with operationalize-workflow wording. “Establish” + “audit checklist” as a numbered contribution reads as a new method. |
| 2 | `sections/02_related_work.tex` | “To the best of our knowledge, this combination—… **and a leakage audit**—has not been packaged as a reusable … protocol” | **BORDERLINE** | Keep packaging claim for *strata + calibration*; explicitly exclude “new audit theory” for L1–L7. |
| 3 | `sections/02_related_work.tex` | “L1–L8 audit defines named channels tied to verifiable artifacts” | **OK** | Keep; add one sentence that L1–L7 operationalize standard safeguards. |
| 4 | `sections/03_protocol.tex` §audit | “The audit is not a model component; it is an evaluation hygiene requirement.” | **OK** | Strengthen: L1–L7 = operational checklist; L8 = empirical sanity check. |
| 5 | `sections/03_protocol.tex` P4 | “formalized through our L1–L8 **audit checklist**” | **BORDERLINE** | “operationalized as the L1–L8 reproducible audit workflow” |
| 6 | `tables/table1_leakage_audit.tex` caption | “Leakage & Predictive Sanity **Audit Checklist** (L1–L8)” | **OK** (honest) | Retitle to workflow + add classification columns so it cannot be read as a new method. |
| 7 | `main_jedm.tex` abstract | “supported by an eight-channel leakage and predictive-sanity audit” | **OK / mild** | Soften to “operational leakage and predictive-sanity workflow (L1–L8)”. |
| 8 | `main_jedm_anonymous.tex` abstract | same family of wording | **OK / mild** | Same soften. |
| 9 | `01_introduction.tex` ¶3 | “eight-channel leakage and predictive-sanity audit” + L8 case | **OK** | Keep L8 case; do not call the eight channels a new method. |
| 10 | `04_experiments.tex` RQ3 | L8 distinguishes cold-start failure from pipeline-random predictions | **OK** | Elevate slightly as empirical demonstration, not as a new method. |
| 11 | `05_discussion_limitations.tex` Implications | “The audit demonstrates its practical value. Channel L8 caught…” | **OK** | Add explicit “L1–L7 are not claimed as a new auditing methodology.” |
| 12 | `05_discussion_limitations.tex` Internal validity | “automated leakage **audit checklist**” | **OK** | “operational audit workflow” |
| 13 | `06_conclusion.tex` | “eight-channel leakage and predictive-sanity audit” | **OK / mild** | “reproducible audit workflow (L1–L8)” |
| 14 | `06_conclusion.tex` | L8 caught alignment artifact | **OK** | Keep; this is the empirical value. |
| 15 | Artifact checklist | “Automated logs verifying channels L1–L8” | **OK** | No change required. |

## Phrases *not* found (good)

- “new audit method”
- “novel auditing framework”
- “establish a new audit”
- “new auditing methodology”

The residual risk is Contribution 3’s **establish … audit checklist**, plus the related-work “to the best of our knowledge … leakage audit” clause.

## Positioning after A6

| Channels | What they are | What they are not |
|----------|---------------|-------------------|
| L1–L7 | Standard evaluation safeguards, *operationalized* for KT (named checks + artifacts) | A new auditing theory or scientific method |
| L8 | KT-specific predictive-sanity check with a real case study | A generic “PASS” row like L1–L7 |
