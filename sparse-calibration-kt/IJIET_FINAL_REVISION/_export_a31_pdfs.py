#!/usr/bin/env python3
"""Export named/blind PDF+DOC from current Word sources; copy into OJS slots."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, stamp_pdf_metadata  # noqa: E402
from apply_a30_submission_pack import copy_ojs, sync_submission_slots  # noqa: E402
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOC,
    FULL_DOCX,
    FULL_PDF,
    export_pdf,
    lock_checks,
    pdf_text,
    set_word_props,
)

WD_FORMAT_DOC = 0
WD_SAVE = -1


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    log: list[str] = ["export"]
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX), ReadOnly=True)
        try:
            full_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        export_pdf(full_doc, FULL_PDF, include_props=True)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        log.append("full pdf+doc")
        full_doc.Close(0)
        full_doc = None

        blind_doc = word.Documents.Open(str(BLIND_DOCX), ReadOnly=True)
        set_word_props(blind_doc, "", "")
        try:
            blind_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        try:
            blind_doc.RemoveDocumentInformation(1)
        except Exception:
            pass
        export_pdf(blind_doc, BLIND_PDF, include_props=False)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        log.append("blind pdf+doc")
        blind_doc.Close(0)
        blind_doc = None
    finally:
        if full_doc is not None:
            try:
                full_doc.Close(0)
            except Exception:
                pass
        if blind_doc is not None:
            try:
                blind_doc.Close(0)
            except Exception:
                pass
        try:
            word.Quit()
        except Exception:
            pass

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    locks = lock_checks(full_t, full_pages)
    log.append(f"pages {full_pages}/{blind_pages}")
    log.append(str(locks))
    if "4/4 unique partitions (mean ΔFAR 0.047" in full_t:
        raise SystemExit("PDF still labels 0.047 as 4/4")
    if "partition-level mean" not in full_t or "0.056" not in full_t:
        raise SystemExit("PDF missing 0.056 partition mean")
    if "code_for_review_anonymous.zip" not in full_t:
        raise SystemExit("PDF missing Limitations zip sentence")
    i_note = full_t.find("Seed-42 ΔFAR 95% CI")
    after_note = full_t[i_note : i_note + 220] if i_note >= 0 else ""
    if "GKT [" in after_note or "CL4KT [" in after_note:
        raise SystemExit("GKT/CL4KT CI still under Table 5")
    if "GKT/CL4KT remain seed 42 only" in full_t:
        raise SystemExit("orphan GKT/CL4KT clause still on Table 6")
    if "TSCDA" in full_t:
        raise SystemExit("TSCDA still in main PDF")
    if "E. Exploratory GKT" in full_t or "CL4KT protocol adapter are scored" in full_t:
        raise SystemExit("exploratory GKT/CL4KT still in Results")
    if "Table 3. Seven-channel" not in full_t or "Fig. 3." not in full_t:
        raise SystemExit("missing leakage Table 3 or Fig. 3")
    if "Fig. 1. Reproducible" not in full_t:
        raise SystemExit("missing pipeline Fig. 1")
    if "Fig. 2. Distribution of KCs" not in full_t:
        raise SystemExit("missing distribution Fig. 2")
    if "Table 5. Simulated gate" in full_t or "Table 6. Gate robustness" in full_t:
        raise SystemExit("FAR tables still in main PDF")
    if "Supplementary Tables S5" not in full_t and "S5–S6" not in full_t:
        raise SystemExit("main text missing S5–S6 FAR pointer")
    if "Threshold-Based Educational Decisions" in full_t:
        raise SystemExit("old title in main PDF")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if not (8 <= full_pages <= 10 and 8 <= blind_pages <= 10):
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if not all(locks.values()):
        raise SystemExit(f"locks {locks}")
    copy_ojs(log)
    sync_submission_slots(log)
    print("\n".join(log))


if __name__ == "__main__":
    main()
