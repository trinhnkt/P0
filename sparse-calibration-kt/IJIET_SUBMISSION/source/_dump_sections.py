#!/usr/bin/env python3
"""Dump Word section starts vs table captions."""
from __future__ import annotations

from pathlib import Path
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "IJIET_SUBMISSION" / "source" / "main_ijiet_full.docx"
OUT = ROOT / "IJIET_SUBMISSION" / "audit" / "step18_sections.txt"

START = {0: "Continuous", 1: "NewCol", 2: "NewPage", 3: "Even", 4: "Odd"}


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def main() -> None:
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines = []
    try:
        lines.append(f"sections={doc.Sections.Count}")
        for s in range(1, doc.Sections.Count + 1):
            sec = doc.Sections(s)
            ps = sec.PageSetup
            head = para_text(sec.Range.Paragraphs(1))[:90]
            lines.append(
                f"SEC {s:02d} start={START.get(int(ps.SectionStart), ps.SectionStart)} "
                f"cols={ps.TextColumns.Count} colw={ps.TextColumns(1).Width:.1f} | {head!r}"
            )
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
