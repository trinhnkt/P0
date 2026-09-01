#!/usr/bin/env python3
"""Dump paragraph/table/figure order for layout wrapping."""
from __future__ import annotations

from pathlib import Path
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "IJIET_SUBMISSION" / "source" / "main_ijiet_full.docx"
OUT = ROOT / "IJIET_SUBMISSION" / "audit" / "step18_flow.txt"

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
        lines.append(f"sections={doc.Sections.Count} tables={doc.Tables.Count}")
        for s in range(1, doc.Sections.Count + 1):
            sec = doc.Sections(s)
            ps = sec.PageSetup
            head = para_text(sec.Range.Paragraphs(1))[:100]
            lines.append(
                f"SEC {s:02d} start={START.get(int(ps.SectionStart), ps.SectionStart)} "
                f"cols={ps.TextColumns.Count} valign={ps.VerticalAlignment} "
                f"colw={ps.TextColumns(1).Width:.1f} | {head!r}"
            )
        lines.append("")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            raw = para_text(p)
            flags = []
            if p.Range.Tables.Count:
                flags.append("IN_TBL")
            if p.Range.InlineShapes.Count:
                flags.append("FIG")
            style = ""
            try:
                style = str(p.Style.NameLocal)
            except Exception:
                pass
            show = (
                raw.startswith("Table ")
                or raw.startswith("Fig. ")
                or raw.startswith("I. ")
                or raw.startswith("II.")
                or raw.startswith("III.")
                or raw.startswith("IV.")
                or raw.startswith("V. ")
                or raw.startswith("VI.")
                or (len(raw) > 2 and raw[1:3] == ". " and raw[0].isalpha())
                or "FIG" in flags
                or raw.startswith("Let y")
            )
            if not show:
                continue
            snippet = raw[:110].replace("\n", " ")
            lines.append(
                f"P{i:04d} sty={style[:16]!s:16} {' '.join(flags):8} | {snippet!r}"
            )
        lines.append("")
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            cap_rng = tbl.Range.Duplicate
            cap_rng.Collapse(1)
            cap_rng.Move(1, -2)
            cap = para_text(cap_rng.Paragraphs(1))[:90]
            prev = cap_rng.Paragraphs(1).Range.Duplicate
            prev.Collapse(1)
            prev.Move(1, -2)
            intro = para_text(prev.Paragraphs(1))[:90]
            w = sum(tbl.Columns(c).Width for c in range(1, tbl.Columns.Count + 1))
            lines.append(
                f"T{ti} rows={tbl.Rows.Count} cols={tbl.Columns.Count} w={w:.1f} "
                f"break={tbl.Rows.AllowBreakAcrossPages} "
                f"| intro={intro!r} | cap={cap!r}"
            )
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
