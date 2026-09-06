# Reproducible Sparse-Concept and Calibration Diagnostics for Knowledge Tracing

Manuscript for the *International Journal of Information and Education Technology* (IJIET, [www.ijiet.org](https://www.ijiet.org)). Diagnostic evaluation of Knowledge Tracing calibration on sparse concepts and a simulated mastery gate. Not a new KT architecture and not a classroom trial.

**T-KT** in the paper is a local Transformer KT baseline, not published SimpleKT.

## IJIET OJS upload

Use **`IJIET_FINAL_REVISION/output/OJS_UPLOAD/`**.

| File | Role |
|------|------|
| `main_ijiet_full.doc` / `.docx` / `.pdf` | Named manuscript (editor) |
| `main_ijiet_blind.pdf` (optional `.doc`) | Double-blind review |
| `supplementary.pdf` | Tables S1–S10 |
| `code_for_review_anonymous.zip` | Anonymous code |
| `cover_letter_ijiet.txt` | Editor only (records JEDM withdrawal) |

Do not send reviewers the named PDF/Word. Do not upload `_archive/`.

The same current Word/PDFs also sit in `IJIET_SUBMISSION/source/` and `IJIET_SUBMISSION/output/`. Official template: `IJIET_SUBMISSION/source/template/IJIET_template.doc`.

## Repository layout

| Path | Role |
|------|------|
| `IJIET_FINAL_REVISION/` | Living Word/PDF (9 pages; allowed 8–10), figures, supplementary, locked analysis |
| `IJIET_SUBMISSION/` | Current OJS copies + official template |
| `src/` `scripts/` `configs/` `tests/` | Training and evaluation code |
| `analysis/` `results/` | Numeric artifacts for reproduction |
| `data/` | Place official ASSISTments 2012, Junyi Academy, XES3G5M dumps here |
| `_archive/` | Withdrawn JEDM sources and conversion snapshots — **not for OJS** |

## Reproduce experiments

```bash
conda create -n sparse_kt python=3.9 -y
conda activate sparse_kt
pip install -r requirements.txt
bash scripts/run_preprocessing.sh
```

Baselines (CSV class `simplekt` = T-KT in the article):

```bash
bash scripts/run_irt.sh
bash scripts/run_dkt.sh
bash scripts/run_simplekt.sh
```

## License

Code is released for IJIET review in `code_for_review_anonymous.zip`. Public repo after review: https://github.com/trinhnkt/Sparse-Concept-and-Calibration
