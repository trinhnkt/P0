#!/usr/bin/env python3
"""Copy named Word to blind and anonymize (P0 inserts already on named)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import patch_blind_data  # noqa: E402
from build_a16_double_blind import (  # noqa: E402
    BLIND_DOCX,
    FULL_DOCX,
    anonymize_blind,
    set_word_props,
)

WD_FORMAT_XML = 16
WD_SAVE = -1


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BLIND_DOCX)
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(BLIND_DOCX))
    try:
        log: list[str] = []
        anonymize_blind(doc, log)
        patch_blind_data(doc, log)
        set_word_props(doc, "", "")
        try:
            doc.RemoveDocumentInformation(1)
        except Exception:
            pass
        body = doc.Content.Text or ""
        if "Khanh-Trinh" in body or "trinhnkt" in body.lower():
            raise SystemExit("blind still named")
        doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        print("blind rebuilt")
        print("\n".join(log))
    finally:
        try:
            doc.Close(WD_SAVE)
        except Exception:
            pass
        word.Quit()


if __name__ == "__main__":
    main()
