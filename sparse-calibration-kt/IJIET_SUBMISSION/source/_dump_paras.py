#!/usr/bin/env python3
from pathlib import Path
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "IJIET_SUBMISSION" / "source" / "main_ijiet_full.docx"
OUT = ROOT / "IJIET_SUBMISSION" / "audit" / "step18_paras.txt"


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def main() -> None:
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines = []
    try:
        ranges = list(range(60, 130)) + list(range(180, 260)) + list(range(330, 450))
        for i in ranges:
            if i > doc.Paragraphs.Count:
                break
            p = doc.Paragraphs(i)
            raw = para_text(p)
            flag = ""
            if p.Range.Tables.Count:
                flag = " TBL"
            if p.Range.InlineShapes.Count:
                flag += " FIG"
            sty = ""
            try:
                sty = str(p.Style.NameLocal)[:14]
            except Exception:
                pass
            lines.append(f"P{i:04d}{flag:4} {sty:14} | {raw[:140]!r}")
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
