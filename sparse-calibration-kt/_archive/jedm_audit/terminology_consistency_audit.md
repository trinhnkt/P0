# Terminology Consistency Audit Report

## 1. Quantitative Terminology Scan
We searched the entire LaTeX source code for the requested terminology.

| Term | Counts / Variants Found |
|---|---|
| **Knowledge Tracing** | `Knowledge Tracing`: 25 |
| **KT** | `KT`: 56, `kt`: 2 |
| **Knowledge Component(s)** | `Knowledge Components`: 8, `Knowledge Component`: 2, `knowledge components`: 3, `knowledge component`: 1 |
| **KC(s)** | `KC`: 55, `KCs`: 53, `kc`: 5, `kcs`: 2 |
| **concept(s)** | `concept`: 32, `concepts`: 22, `Concept`: 9, `Concepts`: 2 |
| **skill(s)** | `skill`: 8, `Skill`: 2 |
| **Graph terms** | `concept graph`: 0, `prerequisite graph`: 0, `graph aggregation`: 0, `graph contrastive learning`: 0, `GCL`: 0 |
| **SSL terms** | `SSL`: 0, `self-supervised`: 5 |
| **Sparsity terms** | `concept sparsity`: 0, `training-data sparsity`: 0, `sparsity`: 4 |
| **Cold-start** | `cold-start`: 47, `Cold-start`: 41 |
| **Leakage control** | `leakage control`: 2, `Leakage Control`: 1 |
| **Train-only** | `train-only`: 7, `Train-only`: 1 |

## 2. Inconsistent Terms & Problems

| Term Category | Variants found | Problem | Recommended term | Suggested edit |
|---|---|---|---|---|
| **Unit of Learning** | `KC`, `concept`, `skill` | Highly interchangeable. "Concept" is used heavily (65 times) alongside "KC" (108 times). "Skill" is used 10 times. | **Knowledge Component (KC)** | Treat "KC" as the primary scientific entity. Use "concept" only in generic prose (e.g., "sparse-concept diagnostics"). Restrict "skill" exclusively to literal dataset field names (e.g., `skill_id`). |
| **Capitalization of Expansion** | `Knowledge Component` vs `knowledge component` | Mixed capitalization when expanding the acronym. | **Knowledge Component** | Capitalize as a proper domain noun when introducing the acronym: "Knowledge Component (KC)". Use lowercase only in generic mid-sentence descriptions if acronym is not used. |
| **Cold-start** | `Cold-start` vs `cold-start` | Mixed casing, but consistently hyphenated. | **cold-start** | Keep "cold-start" (lowercase) mid-sentence and "Cold-start" at the start of sentences or in Title Case headings. Do not use unhyphenated "cold start". |
| **Sparsity** | `sparsity` vs `sparse` | The explicit phrases `concept sparsity` and `training-data sparsity` are missing (0 occurrences). Instead, the paper uses "sparse KCs", "sparse training evidence", and "sparse strata". | **sparse KCs** / **KC sparsity** | No major issue, but if you intended to use the formal noun "concept sparsity", you should replace instances of "sparse concepts" with it. |
| **Graph / SSL terms** | None (0 occurrences) | The paper discusses Graph KT in related works (`nakagawa2019graph`, `yang2021gikt`, `lee2022cl4kt`) but does not use the specific terms `GCL`, `SSL`, `concept graph`, or `prerequisite graph`. It only uses `self-supervised` (5 times) and `dependency graphs`. | **dependency graphs** / **self-supervised** | If the paper focuses strictly on evaluating KT calibration and cold-start without proposing a new Graph/SSL model, the absence of deep graph terminology is perfectly fine and keeps the scope focused. |

## 3. Terms Used but Not Defined
- **ECE, Brier, UNC, REL, RES**: These are well-defined in the abstract/introduction, but make sure the mathematical decomposition formula is fully introduced before the acronyms are heavily relied upon in the Results section.
- **k5 / k10 cold-start**: Mentioned in Table VI and interpretation guides. Ensure the exact definition ($0 < freq \le 5$, etc.) is explicitly defined in Section 3.3 (Protocol) rather than just leaving it implicit in the tables.

## 4. Suggested Consistent Terminology Map
To maintain rigorous academic writing throughout the manuscript, adhere strictly to this map:
1. **The Task**: Knowledge Tracing (KT).
2. **The Item/Question**: "Item" or "Question" (avoid "problem" unless referring to a math problem).
3. **The Underlying Construct**: Knowledge Component (KC). (Do not use "skill" or "concept" interchangeably when referring to the mathematical dimensions of the model).
4. **The Phenomenon**: "KC sparsity" and "strict cold-start KCs" (hyphenated).
5. **The Metrics**: Expected Calibration Error (ECE), Negative Log-Likelihood (NLL).
