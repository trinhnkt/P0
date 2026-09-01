#!/usr/bin/env python3
"""A29: restore A27 title only. No scientific cell or wording edits."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
from apply_a24_format import style_title  # noqa: E402
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
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a29"
LOG = HERE / "audit" / "apply_a29_restore_title_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A29.md"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
PDF_DUMP = HERE / "audit" / "_a29_pdf_text.txt"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

A28_TITLE = (
    "TSCDA: Sparse-Concept and Calibration Diagnostics for Knowledge Tracing"
)


def patch_title(doc, log: list[str]) -> None:
    raw = para_text(doc.Paragraphs(1)).strip()
    if raw != A28_TITLE:
        raise SystemExit(f"unexpected title: {raw!r}")
    set_para_text(doc.Paragraphs(1), PAPER_TITLE)
    log.append(f"title -> {PAPER_TITLE}")


def patch_cover() -> None:
    text = COVER.read_text(encoding="utf-8")
    if A28_TITLE not in text:
        if PAPER_TITLE in text:
            return
        raise SystemExit("cover letter title missing")
    COVER.write_text(text.replace(A28_TITLE, PAPER_TITLE, 1), encoding="utf-8")


def pdf_title_size(path: Path) -> float | None:
    d = fitz.open(str(path))
    title_sz = None
    for b in d[0].get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s.get("text", "").strip()
                if t.startswith("Reproducible Sparse") and title_sz is None:
                    title_sz = round(s["size"], 1)
    d.close()
    return title_sz


def write_changelog(pages: int, blind_pages: int, title_sz: float | None) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A29 — restore A27 title

**Date:** 2026-09-01  
**Retrain:** no. **Locks:** unchanged. **No A28 science wording reverted.**

Title restored to:

> {PAPER_TITLE}

A28 TSCDA-in-title reverted. Abstract/contributions still name TSCDA.
Cover letter title matched.

Named/blind: {pages} / {blind_pages} pages. Title size: {title_sz} pt.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a29`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A29"]
    patch_cover()
    log.append("cover title")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_title(full_doc, log)
        style_title(full_doc, log)
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
    PDF_DUMP.write_text(full_t, encoding="utf-8")
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    title_sz = pdf_title_size(FULL_PDF)
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    log.append(f"PDF_TITLE_SZ={title_sz}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"pdf_title_sz={title_sz}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages, title_sz)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if title_sz != 20.0:
        raise SystemExit(f"title still {title_sz} pt")
    if A28_TITLE in full_t:
        raise SystemExit("A28 title still in PDF")
    if PAPER_TITLE.split()[0] not in full_t:
        raise SystemExit("A27 title missing")
    if "TSCDA" not in full_t:
        raise SystemExit("TSCDA disappeared from body")
    if "counterfactual" not in full_t.lower():
        raise SystemExit("A28 III.H wording lost")
    if "leave population FAR unchanged" not in full_t:
        raise SystemExit("A28 contribution S4 clause lost")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")


if __name__ == "__main__":
    main()
