#!/usr/bin/env python3
"""A15: Generative AI statement — author-action marker; no invented versions."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a15"
LOG = HERE / "audit" / "apply_a15_word_log.txt"

OLD = "Tool versions were not recorded. These tools were not used to fabricate or alter experimental results."
NEW = (
    "[AUTHOR ACTION REQUIRED: confirm exact AI tool/model/version before IJIET submission] "
    "AI was not used to fabricate or alter experimental results."
)


def patch_paragraphs(doc, log: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i).Range
        inner = doc.Range(para.Start, para.End - 1)
        text = inner.Text
        if OLD in text:
            inner.Text = text.replace(OLD, NEW, 1)
            n += 1
    if n != 1:
        raise SystemExit(f"replacements={n}, expected 1")
    log.append("replaced unrecorded-versions sentence")


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        patch_paragraphs(doc, log)
        text = doc.Content.Text
        if "Tool versions were not recorded" in text:
            raise SystemExit("leftover 'Tool versions were not recorded'")
        if "[AUTHOR ACTION REQUIRED: confirm exact AI tool/model/version before IJIET submission]" not in text:
            raise SystemExit("marker missing")
        if "language polishing" not in text or "formatting" not in text:
            raise SystemExit("use description missing")
        if "consistency checking" not in text or "reproducibility prompt preparation" not in text:
            raise SystemExit("use description missing")
        if "AI was not used to fabricate or alter experimental results." not in text:
            raise SystemExit("non-fabrication sentence missing")
        if "ChatGPT" not in text or "Claude" not in text or "Google Antigravity" not in text:
            raise SystemExit("tool names missing")
        doc.Save()
        log.append("saved")
    except Exception:
        doc.Close(0)
        word.Quit()
        raise
    doc.Close(0)
    word.Quit()
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
