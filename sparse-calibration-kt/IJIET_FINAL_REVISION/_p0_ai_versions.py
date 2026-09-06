#!/usr/bin/env python3
"""C14: restore ChatGPT/Claude/Antigravity with public versions as of 6 Sep 2026."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
FULL = HERE / "manuscript" / "main_ijiet_full.docx"
BAK = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_p0_ai36"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
WD_FORMAT_XML = 16
WD_SAVE = -1

AI_OLD = (
    "During manuscript preparation, the authors used Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using this tool, the authors reviewed "
    "and edited the content. The authors remain responsible for all content. "
    "Generative AI is not listed as a co-author."
)
AI_NEW = (
    "During manuscript preparation, the authors used ChatGPT GPT-6 Astra, "
    "Claude Sonnet 5, Google Antigravity 2.12.0, and Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using these tools, the authors "
    "reviewed and edited the content. The authors remain responsible for "
    "all content. Generative AI is not listed as a co-author."
)

COVER_OLD = (
    "Generative AI. Cursor Grok 4.6 was used for language polishing, formatting,\n"
    "consistency checking, and reproducibility-prompt preparation. AI was not used\n"
    "to fabricate or alter results. Generative AI is not a co-author."
)
COVER_NEW = (
    "Generative AI. ChatGPT GPT-6 Astra, Claude Sonnet 5, Google Antigravity\n"
    "2.12.0, and Cursor Grok 4.6 were used for language polishing, formatting,\n"
    "consistency checking, and reproducibility-prompt preparation. Versions are\n"
    "the public current identifiers as of 6 September 2026. AI was not used to\n"
    "fabricate or alter results. Generative AI is not a co-author."
)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not BAK.exists():
        shutil.copy2(FULL, BAK)
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(FULL))
    n = 0
    try:
        for i in range(1, doc.Paragraphs.Count + 1):
            para = doc.Paragraphs(i)
            try:
                if para.Range.Tables.Count:
                    continue
            except Exception:
                pass
            inner = doc.Range(para.Range.Start, para.Range.End - 1)
            text = inner.Text or ""
            if AI_NEW in text:
                n = 1
                continue
            if AI_OLD in text:
                inner.Text = text.replace(AI_OLD, AI_NEW)
                n += 1
        body = doc.Content.Text or ""
        if n != 1:
            raise SystemExit(f"AI paragraph hits={n}")
        if "ChatGPT GPT-6 Astra" not in body:
            raise SystemExit("GPT-6 Astra missing")
        if "Claude Sonnet 5" not in body:
            raise SystemExit("Sonnet 5 missing")
        if "Antigravity 2.12.0" not in body:
            raise SystemExit("Antigravity 2.12.0 missing")
        if "Cursor Grok 4.6" not in body:
            raise SystemExit("Grok 4.6 missing")
        if "0.1136" not in body or "0.2280" not in body:
            raise SystemExit("ECE locks missing")
        doc.SaveAs2(str(FULL), WD_FORMAT_XML)
        print("ai paragraph n=1")
    finally:
        try:
            doc.Close(WD_SAVE)
        except Exception:
            pass
        word.Quit()

    cover = COVER.read_text(encoding="utf-8")
    if COVER_NEW in cover:
        print("cover already new")
    elif COVER_OLD not in cover:
        raise SystemExit("cover AI block not found")
    else:
        COVER.write_text(cover.replace(COVER_OLD, COVER_NEW), encoding="utf-8")
        print("cover updated")


if __name__ == "__main__":
    main()
