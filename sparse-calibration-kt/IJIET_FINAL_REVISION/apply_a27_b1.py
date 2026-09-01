#!/usr/bin/env python3
"""A27: B1 occupancy/mixed-τ policies on frozen T-KT p. No retrain. No lock edits."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
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

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a27"
LOG = HERE / "audit" / "apply_a27_b1_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A27.md"
SUP_TEX = HERE / "supplementary" / "supplementary.tex"
SUP_PDF = HERE / "output" / "supplementary.pdf"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "On ASSISTments 2012 fold 0, T-KT ΔFAR stays positive at every locked grid point τ∈{0.5, 0.6, 0.7, 0.8} (Supplementary Table S3); the grid is not a search over sparse error.",
        "On ASSISTments 2012 fold 0, T-KT ΔFAR stays positive at every locked grid point τ∈{0.5, 0.6, 0.7, 0.8} (Supplementary Table S3); the grid is not a search over sparse error. Supplementary Table S4 reuses the same frozen p for a Reliable-only advance rule and a mixed τ (sparse 0.8 / else 0.7); those policies are not trained.",
    ),
    (
        "Those checks are not a validated classroom policy. A population AUC win, or an exploratory GKT/CL4KT run, is not by itself evidence that a global gate is safer on the tail.",
        "Those checks are not a validated classroom policy. On the same seed-42 T-KT scores, three simulated policies leave population FAR at 0.197 (Supplementary Table S4): global τ=0.7; advance only on Reliable occupancy; and τ=0.8 on the sparse stratum. Sparse Nadvance is 235, 0, and 218. Population FAR therefore hides the occupancy design; TSCDA reports the slice. A population AUC win, or an exploratory GKT/CL4KT run, is not by itself evidence that a global gate is safer on the tail.",
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
    missing = [old[:60] for old, n in counts.items() if n != 1]
    log.append("counts=" + str({old[:40]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing} {counts}")


def compile_supplementary(log: list[str]) -> None:
    cmd = shutil.which("pdflatex")
    if not cmd:
        log.append("pdflatex missing; S4 tex only")
        return
    for _ in range(2):
        proc = subprocess.run(
            [cmd, "-interaction=nonstopmode", "-halt-on-error", SUP_TEX.name],
            cwd=str(SUP_TEX.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            log.append(proc.stdout[-1500:])
            log.append(proc.stderr[-500:])
            raise SystemExit("pdflatex supplementary failed")
    built = SUP_TEX.with_suffix(".pdf")
    shutil.copy2(built, SUP_PDF)
    log.append(f"supplementary={SUP_PDF.name}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A27 — B1 occupancy/mixed-τ policies

**Date:** 2026-09-01  
**Retrain:** no. **Locks:** Table 5 FAR 0.196/0.268 and Nadvance=235 unchanged.  
**Source:** `analysis/direction_c/threshold_rates.csv` (T-KT = CSV `simplekt`).

Three simulated policies on frozen seed-42 p (ASSISTments fold 0):

| Policy | Pop. FAR | Sparse Nadvance | Sparse FAR |
|--------|----------|-----------------|------------|
| A global τ=0.7 | 0.197 | 235 | 0.268 |
| B Reliable-only | 0.197 | 0 | — |
| C sparse τ=0.8 | 0.197 | 218 | 0.261 |

Finding: population FAR does not move; the design choice appears in the sparse slice (TSCDA).

Named/blind: {pages} / {blind_pages} pages. Table S4 in supplementary.pdf.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a27`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A27"]
    compile_supplementary(log)
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_paragraphs(full_doc, log)
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        try:
            full_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
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
            blind_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
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
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
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
    if "Supplementary Table S4" not in full_t and "Table S4" not in full_t:
        raise SystemExit("S4 citation missing")
    if "218" not in full_t:
        raise SystemExit("policy C Nadvance missing")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")


if __name__ == "__main__":
    main()
