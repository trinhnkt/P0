# Formula Consistency Audit

| Equation | Variables defined? | Text-formula consistency | Problem | Suggested fix |
|---|---|---|---|---|
| $\mathrm{freq}_{\mathrm{train}}(c)$ | Yes ($D_{train}$, $c'$, $u, i, r, \tau$) | Consistent | None | N/A |
| $\text{Strict Cold-start:} \quad \mathrm{freq}_{\mathrm{train}}(c) = 0$, etc. | Yes | Consistent | None | N/A |
| $\mathrm{ECE} = \sum \frac{\|B_m\|}{N} \|\mathrm{acc} - \mathrm{conf}\|$ | Yes ($M$, $N$, $B_m$, $\mathrm{acc}$, $\mathrm{conf}$) | Consistent | None | N/A |
| $\mathrm{Brier} = \frac{1}{N}\sum (p_i - y_i)^2$ | Yes ($N$, $p_i$, $y_i$) | Consistent | None | N/A |
| $\mathrm{Brier} = \mathrm{UNC} - \mathrm{RES} + \mathrm{REL}$ | Yes | Consistent | None | N/A |
| $\mathrm{UNC}$, $\mathrm{REL}$, $\mathrm{RES}$ | Yes ($\bar{y}$, $n_m$, $\mathrm{acc}_m$, $\mathrm{conf}_m$) | Consistent | None | N/A |

## Attention Points Requested by User

1. **KT objective**: Addressed via standard Brier Score / NLL evaluation equations. The binary cross-entropy (BCE) loss is standard and implied but not explicitly mathematically defined in the text, which is acceptable since the paper focuses on the diagnostic protocol, not the training objective.
2. **Concept graph definition**: **DOES NOT EXIST in the manuscript.**
3. **Concept sparsity definition**: Addressed explicitly via the $\mathrm{freq}_{\mathrm{train}}(c)$ strata thresholds.
4. **Supervised KT loss**: **DOES NOT EXIST in the manuscript.** (BCE is standard).
5. **InfoNCE loss**: **DOES NOT EXIST in the manuscript.** 
6. **Total loss**: **DOES NOT EXIST in the manuscript.**
7. **Prerequisite preservation ratio**: **DOES NOT EXIST in the manuscript.**
8. **Adaptive mask rate**: **DOES NOT EXIST in the manuscript.**

*Note: The user prompt appears to include targets (InfoNCE, Adaptive mask rate, Graph definitions) that belong to a Graph Contrastive Learning (GCL) paper. This manuscript is a diagnostic and calibration protocol paper for standard KT baselines. No GCL formulas are present or required.*
