# Numerical Consistency Audit Report

| Section | Text claim | Table/Figure value | Consistent? | Problem | Suggested correction |
|---|---|---|---|---|---|
| `04_experiments.tex` | DKT slightly leading SimpleKT on ASSISTments 2012 under the learner-based split (0.6980 ± 0.0013 vs. 0.6840 ± 0.0025). | Table III: DKT 0.6980, SimpleKT 0.6840 | Yes | None | N/A |
| `04_experiments.tex` | IRT performs at random (AUC = 0.5000) on learner-based splits. | Table III: IRT 0.5000 | Yes | None | N/A |
| `04_experiments.tex` | Under temporal splits, IRT's AUC rises to 0.5913 on ASSISTments 2012... | Table VII (App B): 0.5913 | Yes | None | N/A |
| `04_experiments.tex` | ...while SimpleKT (0.6731) slightly outperforms DKT (0.6606)... | Table VII (App B): 0.6731 vs 0.6606 | Yes | None | N/A |
| `04_experiments.tex` | Overall AUC differences between DKT and SimpleKT are statistically significant... after Bonferroni correction | Table DeLong | Yes | None | Explicitly cite DeLong's p-value threshold (e.g., $p < 0.05$) in the text. |
| `04_experiments.tex` | DKT and SimpleKT show high AUC in the very sparse stratum on ASSISTments 2012 (e.g., 0.9045 ± 0.0667 for DKT) | Table IV: 0.9045 | Yes | None | N/A |
| `04_experiments.tex` | DKT and SimpleKT still show higher AUC on sparse KCs than on dense KCs (DKT: 0.8547 vs. 0.8168; SimpleKT: 0.8455 vs. 0.7548) on XES3G5M. | Table IV | Yes | None | N/A |
| `04_experiments.tex` | IRT exhibits very low ECE (e.g., 0.0033 on ASSISTments 2012 and 0.0021 on Junyi Academy) | Table V | Yes | None | N/A |
| `04_experiments.tex` | SimpleKT, ECE increases from 0.1131 in the dense stratum to 0.1578 in the medium stratum and 0.2254 in the sparse stratum. | Table V | Yes | None | N/A |
| `04_experiments.tex` | DKT, where REL increases from 0.0053 (dense) to 0.0316 (medium) and 0.0623 (sparse). | Table V | Yes | None | N/A |
| `04_experiments.tex` | The dense stratum ... has lower ECE (0.0889), whereas the sparse stratum shows higher ECE (0.1624) while retaining meaningful discrimination (AUC = 0.6529). | Figure 3 | Yes | None | N/A |
| `04_experiments.tex` | ...near-random predictive performance (AUC ≈ 0.41 - 0.51) on strict and limited cold-start groups (e.g., DKT AUC is 0.5055 and SimpleKT AUC is 0.4318 on ASSISTments 2012 strict cold-start). | Table VI | Yes | None | N/A |

## Formatting & Statistical Check
- **Mean $\pm$ Std Formatting**: Uniformly used in `04_experiments.tex` for learner-based splits (e.g., `0.6980 \pm 0.0013`). Temporal splits correctly report single deterministic metrics as noted.
- **Statistical Significance**: The claim "statistically significant" is properly backed by the DeLong test (Table DeLong) and Bonferroni correction.
- **Dataset Stats**: The `#KCs`, `#Train`, `#Test`, and sparsity levels cleanly align with the values in Table 1 (`table1_dataset_stats.tex`).

**Conclusion**: The numerical claims strictly map to the tables without fabrication or mismatch.
