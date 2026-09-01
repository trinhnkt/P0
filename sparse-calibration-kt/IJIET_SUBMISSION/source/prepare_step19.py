#!/usr/bin/env python3
"""IJIET-19: apply numeric-audit wording fix, then compile named + blind PDFs.

Does not restore the IJIET-18 snapshot. Does not change table cells.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
FULL_DOCX = SRC / "main_ijiet_full.docx"
FULL_DOC = SRC / "main_ijiet_full.doc"
BLIND_DOCX = SRC / "main_ijiet_blind.docx"
BLIND_DOC = SRC / "main_ijiet_blind.doc"
OUT_DIR = ROOT / "IJIET_SUBMISSION" / "output"
FULL_PDF = OUT_DIR / "main_ijiet_full.pdf"
BLIND_PDF = OUT_DIR / "main_ijiet_blind.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step19_verify.txt"
FULLTEXT = ROOT / "IJIET_SUBMISSION" / "audit" / "step19_fulltext.txt"

sys.path.insert(0, str(SRC))
from prepare_step15 import (  # noqa: E402
    AUTHORS_META,
    IDENTIFYING,
    KEEP_IN_BLIND,
    compact,
    export_pdf,
    hits,
    neutralize_table_lists,
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
    stamp_pdf_metadata,
    token_present,
)
from prepare_step16 import restore_h1  # noqa: E402
from prepare_step17 import anonymize_blind  # noqa: E402
from prepare_step18 import restore_h2  # noqa: E402

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

OLD_A = (
    "a five-seed check of the sparse–dense FAR gap on ASSISTments 2012"
)
OLD_B = (
    "a five-seed check of the sparse-dense FAR gap on ASSISTments 2012"
)
NEW = (
    "a check of the sparse–dense FAR gap on ASSISTments 2012 across "
    "five training runs / four unique learner partitions"
)


def patch_intro(doc, lines: list[str]) -> None:
    n = 0
    already = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if "five training runs / four unique learner partitions" in raw and "five-seed check" not in raw:
            already += 1
            continue
        if "five-seed check" not in raw:
            continue
        new = raw.replace(OLD_A, NEW).replace(OLD_B, NEW)
        if new == raw:
            raise RuntimeError(f"five-seed phrase not matched at para {i}: {raw[:240]!r}")
        set_para_text(doc.Paragraphs(i), new)
        n += 1
        lines.append(f"PATCH_INTRO i={i}")
    if n == 0 and already == 1:
        lines.append("PATCH_INTRO already applied")
        return
    if n != 1:
        raise RuntimeError(f"expected 1 intro patch, got {n} (already={already})")


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"Missing {FULL_DOCX}")
    lines: list[str] = ["IJIET-19 numeric-audit compile"]
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    saved = False
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_intro(full_doc, lines)
        restore_h1(full_doc)
        restore_h2(full_doc, lines)
        neutralize_table_lists(full_doc)
        set_word_props(
            full_doc,
            AUTHORS_META,
            "Hung Yen University of Technology and Education",
        )
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        export_pdf(full_doc, FULL_PDF)
        lines.append(
            f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count} "
            f"SECTIONS={full_doc.Sections.Count}"
        )

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        restore_h1(blind_doc)
        restore_h2(blind_doc, lines)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
        if full_doc.InlineShapes.Count != 1 or full_doc.Tables.Count < 8:
            raise RuntimeError("structure lost")
        saved = True
    except Exception as exc:
        REPORT.write_text("\n".join(lines) + "\nERROR: " + str(exc) + "\n", encoding="utf-8")
        raise
    finally:
        if full_doc is not None:
            full_doc.Close(WD_SAVE if saved else 0)
        if blind_doc is not None:
            blind_doc.Close(WD_SAVE if saved else 0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    FULLTEXT.write_text(full_t, encoding="utf-8")
    compact_t = compact(full_t)
    full_pages = fitz.open(str(FULL_PDF)).page_count
    blind_pages = fitz.open(str(BLIND_PDF)).page_count
    lines.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    checks = {
        "ece": "0.1136" in full_t and "0.2280" in full_t,
        "far": "0.196" in full_t and "0.268" in full_t,
        "mean_dfar": "0.047" in full_t,
        "no_five_seed": "five-seedcheck" not in compact_t.lower(),
        "intro_four_part": "fivetrainingruns/fouruniquelearnerpartitions" in compact_t.lower(),
        "gkt_single": "fold0(seed42)" in compact_t.lower(),
        "cl4kt_adapter": "notanofficialcl4ktcheckpoint" in compact_t.lower()
        or "notanofficialcheckpoint" in compact_t.lower(),
        "temporal": "singlecorrectedcutoff" in compact_t.lower(),
        "authors": "Khanh-Trinh" in full_t,
        "blind": not hits(blind_t, IDENTIFYING),
        "fig": "Fig. 1." in full_t,
        "t8": "TABLE 8." in full_t.upper() or "Table 8." in full_t,
    }
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    lines.append(f"CHECKS={checks}")
    lines.append(f"KEEP={keep_ok}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise RuntimeError(f"verify failed: {failed}")
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind dropped {keep_ok}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
