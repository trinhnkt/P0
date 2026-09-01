#!/usr/bin/env python3
"""A25: scientific wording from IJIET editor/reviewer notes.

No locked ASSISTments cells. No new trains. No temperature/Platt experiment.
No Table 2 hash imputation. Does not name JEDM in the article.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
from apply_a24_format import style_labeled_block  # noqa: E402
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

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a25"
LOG = HERE / "audit" / "apply_a25_science_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A25.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "a Transformer KT baseline (T-KT). Lower KC training",
        "a local Transformer KT baseline (T-KT; not SimpleKT [4]). Lower KC training",
    ),
    (
        "The gap stays positive on 5/5 runs and 4/4 unique partitions (mean 0.047); the KC-cluster 95% CI is wide.",
        "The primary check is 4/4 unique partitions (mean ΔFAR 0.047; five runs, two sharing a split); the seed-42 95% CI is [0.006, 0.138].",
    ),
    (
        "command of a skill",
        "mastery of a skill",
    ),
    (
        "a gate that yields more higher-error sparse advance decisions",
        "a gate that yields a higher error rate among sparse advance decisions",
    ),
    (
        "A platform can log Nadvance and FAR by train-only KC stratum from operational traces without an RCT.",
        "A platform can log Nadvance and FAR by train-only KC stratum from operational traces without an RCT. Those checks are not a validated classroom policy.",
    ),
    (
        "pyKT: A python library to benchmark deep learning based Knowledge Tracing models",
        "pyKT: A Python library to benchmark deep learning based Knowledge Tracing models",
    ),
]


def cell_text(cell) -> str:
    return cell.Range.Text.replace("\r", "").replace("\x07", "").strip()


def set_cell(cell, text: str) -> None:
    rng = cell.Range
    rng.MoveEnd(1, -1)  # wdCharacter
    rng.Text = text


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
    log.append("counts=" + str({old[:45]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing} {counts}")


def patch_tables(doc, log: list[str]) -> None:
    t2 = doc.Tables(2)
    n_es = 0
    for ri in range(1, t2.Rows.Count + 1):
        c = t2.Cell(ri, 1)
        if cell_text(c) == "Early stopping":
            set_cell(c, "Training length")
            n_es += 1
            log.append(f"T2 r{ri} Training length")
    if n_es != 1:
        raise SystemExit(f"Early stopping hits={n_es}")

    t7 = doc.Tables(7)
    n_flat = 0
    for ri in range(1, t7.Rows.Count + 1):
        for ci in range(1, t7.Columns.Count + 1):
            try:
                c = t7.Cell(ri, ci)
            except Exception:
                continue
            raw = cell_text(c)
            if "0.118" in raw and "0.125" in raw:
                set_cell(c, "flat 0.1176→0.1254")
                n_flat += 1
                log.append(f"T7 r{ri}c{ci} {raw!r} -> Table 4 digits")
    if n_flat != 1:
        raise SystemExit(f"Table 7 flat-ECE hits={n_flat}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A25 — Scientific wording (IJIET reviewer)

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged. **No temperature/Platt run.**  
**JEDM:** withdrawn; article still does not name JEDM.

| # | Scientific issue | Action |
|---|------------------|--------|
| 1 | T-KT ≠ SimpleKT in abstract | Abstract: local T-KT; not SimpleKT [4] |
| 2 | FAR unit | Lead with 4/4 partitions (mean 0.047); print seed-42 CI [0.006, 0.138] |
| 3 | Table 2 “Early stopping” | Row label → Training length (fixed epochs unchanged) |
| 4 | Double comparative | “higher error rate among sparse advance decisions” |
| 5 | Table 7 rounding | 0.1176→0.1254 (same as Table 4) |
| 6 | Policy overclaim | “not a validated classroom policy” |
| 7 | [5] | Python |
| 8 | Intro diction | mastery of a skill |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a25`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A25"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_paragraphs(full_doc, log)
        patch_tables(full_doc, log)
        style_labeled_block(full_doc, 10, "Abstract—", log, "ABSTRACT")
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
    compact = "".join(full_t.split())
    if "notSimpleKT" not in compact.replace(" ", "") and "not SimpleKT" not in full_t:
        if "notSimpleKT[4]" not in compact:
            raise SystemExit("abstract T-KT≠SimpleKT missing")
    if "[0.006, 0.138]" not in full_t and "[0.006,0.138]" not in compact:
        raise SystemExit("abstract CI missing")
    if "more higher-error" in full_t:
        raise SystemExit("double comparative remains")
    if "Early stopping" in full_t:
        raise SystemExit("Early stopping label remains")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named in article")


if __name__ == "__main__":
    main()
