# Scientific Logic Chain Audit

| Element | Stated in paper | Supporting evidence | Missing link | Suggested fix |
|---|---|---|---|---|
| **Main Problem** | Aggregate metrics (AUC/ACC) mask degradation on low-frequency concepts and fail to reveal poorly calibrated probabilities. Current pipelines suffer from hidden data leakage. | Section 1 (Introduction) explicitly lists Problem 1, 2, and 3. | None | N/A |
| **Research Gap** | Lack of standardized train-only KC frequency stratification, bucket-level calibration diagnostics, and strict leakage auditing. | Addressed through "Motivating Diagnostic Gap" mapping to Contributions 1, 2, and 3. | None | N/A |
| **RQ1 (Predictive Degradation)** | Do aggregate metrics mask predictive degradation on low-frequency KCs? | Addressed in Section 4.2. Supported by Table III (Overall) and Table IV (Bucket-level breakdowns). | None | N/A |
| **RQ2 (Calibration Profiles)** | How do calibration profiles change across frequency strata? | Addressed in Section 4.3. Supported by Table V (ECE, Brier) and Figure 3 (Reliability Diagrams). | None | N/A |
| **RQ3 (Limited Cold-start)** | How do baseline KT models behave on KCs with zero or limited training-fold frequency? | Addressed in Section 4.4. Supported by Table VI (Cold-start temporal metrics). | None | N/A |
| **Contributions Support** | C1 (Stratification Protocol), C2 (Calibration Reporting), C3 (Leakage Audit) | C1 is proven via Table IV/VI; C2 via Table V/Fig 3; C3 via Table I (Leakage Audit Checklist L1-L8). | None | N/A |
| **Method components unevaluated** | LLM-based KT, Graph-based KT (GKT, CL4KT), sparseKT, csKT. | Discussed heavily in Section 2 (Related Work) as state-of-the-art cold-start or sparse solutions. | The paper evaluates standard baselines (IRT, DKT, SimpleKT) to demonstrate the *diagnostic protocol*, not to propose a new SOTA model. | The logic holds. However, reviewers might ask why sparseKT or csKT wasn't tested using your protocol. Explicitly state in Section 4.1 or Discussion that extending the protocol to test Graph/LLM/csKT models is left for future work. |
| **Results not discussed** | None. All tables (Table I to Table VI, plus App A/B tables) are actively referenced and discussed in Section 4 or Section 5. | Cross-reference checks confirm every table is cited. | None | N/A |

## Overall Assessment
The scientific logic chain is **highly coherent and robust**. 

**Path:** Problem 1,2,3 $\rightarrow$ Contribution 1,2,3 $\rightarrow$ Protocol design (L1-L8, ECE/Brier) $\rightarrow$ RQ1,2,3 $\rightarrow$ Results (Tables 3,4,5,6) $\rightarrow$ Conclusion.

The flow is strictly 1-to-1 mapped. The only minor risk is that the related work heavily discusses advanced Cold-start models (LLMs, Graphs) which are not empirically tested in the paper. As long as the paper is framed purely as proposing an *evaluation/diagnostic protocol* rather than proposing a *new model*, this logic is completely sound.
