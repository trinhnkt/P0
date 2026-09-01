#!/usr/bin/env python3
"""A21: IJIET reviewer minor-revision items. No locked ASSISTments cells. No new trains."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import (  # noqa: E402
    DATA_BLIND,
    patch_blind_data,
    stamp_pdf_metadata,
)
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOCX,
    FULL_PDF,
    anonymize_blind,
    export_pdf,
    lock_checks,
    pdf_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a21"
LOG = HERE / "audit" / "apply_a21_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A21.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "from 0.196 (dense) to 0.268 (sparse) on one ASSISTments fold; the sparse–dense gap stays positive on all five training runs and on all four unique partitions (mean 0.047).",
        "from 0.196 (dense) to 0.268 (sparse) on one ASSISTments fold under Limited occupancy (Nadvance=235; seed-42 ΔFAR=0.072). The gap stays positive on 5/5 runs and 4/4 unique partitions (mean 0.047); the KC-cluster 95% CI is wide.",
    ),
    (
        "and published SimpleKT [4], retain that task while substituting self-attention for recurrence.",
        "and SimpleKT [4], retain that task while substituting self-attention for recurrence. SimpleKT [4] is related literature only; it is not the T-KT model scored in Section IV.",
    ),
    (
        "Main tables use local IRT, DKT, and a Transformer KT baseline (T-KT), not a pinned pyKT commit (training snapshot commit: NOT RECOVERED). The Transformer KT baseline is a two-layer Transformer encoder over DKT-style KC-response tokens, not the published SimpleKT architecture [4]. Table 2 reports recovered training settings; missing fields are marked NOT RECOVERED and are not imputed.",
        "Main tables use local IRT, DKT, and a Transformer KT baseline (T-KT). The original training-container commit is NOT RECOVERED and is not imputed. Source bytes used in the A5 audit are recorded at git commit eab9f67. The Transformer KT baseline is a two-layer Transformer encoder over DKT-style KC-response tokens, not the published SimpleKT architecture [4]; no Section IV cell is a SimpleKT [4] result. Table 2 reports recovered training settings; missing fields are marked NOT RECOVERED and are not imputed.",
    ),
    (
        "The display threshold is τ=0.7; the grid {0.5, 0.6, 0.7, 0.8} is recorded in the artifact and is not a search over sparse error.",
        "The display threshold is τ=0.7. On ASSISTments 2012 fold 0, T-KT ΔFAR stays positive at every locked grid point τ∈{0.5, 0.6, 0.7, 0.8} (Supplementary Table S3); the grid is not a search over sparse error.",
    ),
    (
        "DKT FAR is 0.200 [0.190, 0.211] dense and 0.296 [0.221, 0.383] sparse. Exploratory GKT/CL4KT rows of the same table are discussed in subsection E, not as main-model findings.",
        "DKT FAR is 0.200 [0.190, 0.211] dense and 0.296 [0.221, 0.383] sparse. Sparse T-KT FAR uses Limited occupancy (Nadvance=235). Exploratory GKT/CL4KT numbers are in subsection E, not in Table 5.",
    ),
    (
        "Table 5. Simulated gate at τ=0.7, ASSISTments 2012 fold 0 (seed 42). FAR, Excess FAR, and Miss as defined in Section III.H. FAR 95% CIs: KC-cluster percentile, B=2000. Not a classroom trial.",
        "Table 5. Simulated gate at τ=0.7, ASSISTments 2012 fold 0 (seed 42); T-KT and DKT only. Sparse occupancy is Limited. FAR 95% CIs: KC-cluster percentile, B=2000. Not a classroom trial.",
    ),
    (
        "Coincidence of digits: T-KT dense E[FAR] at τ=0.7 on seed 42 is 0.113, close to the four-partition dense ECE 0.114. They are different quantities.",
        "T-KT dense E[FAR] at τ=0.7 on seed 42 is 0.113; four-partition dense ECE is 0.114. These are different functionals.",
    ),
    (
        "Table 6. Gate robustness at τ=0.7 on ASSISTments 2012. Five training runs (seeds 42, 2024, 2025, 2026, 2027) across four unique learner partitions (2025 and 2026 share a split).",
        "Table 6. Gate robustness at τ=0.7 on ASSISTments 2012 (primary unit: four unique learner partitions). Five training runs (seeds 42, 2024, 2025, 2026, 2027) across those partitions (2025 and 2026 share a split).",
    ),
    (
        "A population AUC win, or an exploratory GKT/CL4KT run, is not by itself evidence that a global gate is safer on the tail.",
        "This study does not apply temperature scaling or Platt scaling; those maps would be a separate post-hoc experiment. A platform can log Nadvance and FAR by train-only KC stratum from operational traces without an RCT. A population AUC win, or an exploratory GKT/CL4KT run, is not by itself evidence that a global gate is safer on the tail.",
    ),
]


def patch_paragraphs(doc, log: list[str]) -> None:
    counts = {old: 0 for old, _ in REPLACEMENTS}
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        try:
            if para.Range.Tables.Count:
                continue
        except Exception:
            pass
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        changed = False
        for old, new in REPLACEMENTS:
            if old in text:
                text = text.replace(old, new, 1)
                counts[old] += 1
                changed = True
        if changed:
            inner.Text = text
            log.append(f"para i={i}")
    log.append("counts=" + str({old[:40]: n for old, n in counts.items()}))
    missing = [old[:50] for old, n in counts.items() if n != 1]
    if missing:
        raise SystemExit(f"expected 1 hit each, missing/extra: {missing} {counts}")


def trim_table5(doc, log: list[str]) -> None:
    table = doc.Tables(5)
    if table.Rows.Count != 9:
        raise SystemExit(f"Table 5 rows={table.Rows.Count}, expected 9")
    r6 = table.Cell(6, 1).Range.Text.replace("\r", "").replace("\x07", "").strip()
    if not r6.startswith("GKT"):
        raise SystemExit(f"Table 5 r6={r6!r}, expected GKT")
    for _ in range(4):
        table.Rows(table.Rows.Count).Delete()
    if table.Rows.Count != 5:
        raise SystemExit(f"Table 5 after trim rows={table.Rows.Count}")
    log.append("table5 trimmed to T-KT/DKT")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A21 — Reviewer minor revision

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** 0.1136 / 0.2280 / 0.196 / 0.268 / 0.047 / [0.006, 0.138] unchanged.

| # | Reviewer item | Action |
|---|---|---|
| 1 | FAR headline / Limited occupancy | Abstract: Nadvance=235, seed-42 ΔFAR=0.072, mean 0.047, wide CI |
| 2 | T-KT ≠ SimpleKT [4] | Related work: [4] literature only; methods: no Section IV cell is SimpleKT |
| 3 | τ grid | S3 from existing `threshold_rates.csv`; one sentence in III.H |
| 4 | Post-hoc calibration | Explicitly not applied; occupancy evaluation is the contribution |
| 5 | Snapshot hash | Prose: eab9f67 source audit; Table 2 stays NOT RECOVERED |
| 6 | IRT AUC=0.50 | Already adjacent to Table 3; unchanged |
| 7 | Four partitions primary | Table 6 caption |
| 8 | GKT/CL4KT in Table 5 | Rows removed; numbers remain in IV.E |
| 9 | Coincidence of digits | Replaced with functionals wording |
| 10 | S1 overfull | `resizebox`; added S3 |
| 11 | Log without RCT | V.B sentence on operational Nadvance/FAR logs |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a21`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A21"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        trim_table5(full_doc, log)
        patch_paragraphs(full_doc, log)
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        export_pdf(full_doc, FULL_PDF, include_props=True)
        full_doc.Close(WD_SAVE)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, log)
        patch_blind_data(blind_doc, log)
        set_word_props(blind_doc, "", "")
        try:
            blind_doc.RemoveDocumentInformation(1)
        except Exception:
            pass
        if "Khanh-Trinh" in (blind_doc.Content.Text or ""):
            raise RuntimeError("blind Word still contains Khanh-Trinh")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF, include_props=False)
        if blind_doc.Tables.Count != n_tables or blind_doc.InlineShapes.Count != n_figs:
            raise RuntimeError("blind structure changed")
        if blind_doc.Tables(5).Rows.Count != 5:
            raise RuntimeError("blind Table 5 row count")
        blind_doc.Close(WD_SAVE)
        blind_doc = None
    finally:
        if full_doc is not None:
            full_doc.Close(0)
        if blind_doc is not None:
            blind_doc.Close(0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    compact = "".join(full_t.split()).lower()
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    log.append(f"NADV={'nadvance=235' in compact or 'nadvance =235' in compact}")
    log.append(f"S3={'supplementarytables3' in compact or 'tables3' in compact}")
    log.append(f"EAB={'eab9f67' in full_t}")
    log.append(f"TEMP={'temperature scaling' in full_t.lower()}")
    log.append(f"COINC={'coincidence of digits' not in full_t.lower()}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if "0.196" not in full_t or "0.268" not in full_t or "0.047" not in full_t:
        raise SystemExit("FAR locks missing")
    if "Coincidence of digits" in full_t:
        raise SystemExit("informal coincidence sentence remains")
    if "Khanh-Trinh" in blind_t:
        raise SystemExit("blind identified")
    if "temperaturescaling" not in compact:
        raise SystemExit("temperature sentence missing")
    if "eab9f67" not in full_t:
        raise SystemExit("source hash missing")


if __name__ == "__main__":
    main()
