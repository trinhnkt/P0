# Format and Cross-Reference Audit

| Item | Location | Problem | Suggested fix |
|---|---|---|---|
| **Unresolved Citations / ??** | Entire document | **None.** The `full_review.py` audit confirmed 0 occurrences of `[?]` or `??`. | N/A |
| **Table/Figure Numbering** | `main_jedm.tex` | **None.** LaTeX strictly handles sequential numbering. Table 7 floats have been correctly locked to Appendix B. | N/A |
| **Orphaned Tables/Figures** | `sections/04_experiments.tex` | **None.** All 12 tables and 3 figures are actively cited in the text using `\ref{}`. | N/A |
| **Label Naming Conventions** | Entire document | **None.** The source code strictly adheres to `tab:...` and `fig:...` namespaces. Equations and algorithms are not explicitly labeled since none exist that require cross-referencing. | N/A |
| **Caption Tone** | `tables/*.tex`, `sections/*.tex` | **None.** Captions are highly descriptive (e.g., "Overall Performance under Future Validation (Temporal Splits)") without making claims of superiority. | N/A |
| **Reference Style** | `main_jedm.tex` | **None.** The document uses JEDM's official author-year citation style via `natbib` (`\citep` and `\citet`) backed by `acmtrans.bst` mapping. | N/A |
| **DOI Formatting** | `references.bbl` | **Missing DOIs.** Several older or standard machine learning papers (e.g., `piech2015deep`, `liu2023simplekt`) lack the `doi={...}` field. | Manually acquire DOIs from publisher sites and append them to `references.bib`, then regenerate `.bbl`. See `reference_existence_audit.md`. |

## Overall Assessment
The LaTeX cross-referencing system is **100% intact**. There are no broken links, missing citations, or floating tables displacing text flow (Table 7 in Appendix B was previously fixed). The only formatting gap is missing DOIs in the bibliography, which must be addressed manually.
