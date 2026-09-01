#!/usr/bin/env python3
"""Dump Word sections, tables, figure size for visual QA fixes."""
from __future__ import annotations

from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
DOCX = ROOT / "IJIET_SUBMISSION" / "source" / "main_ijiet_full.docx"
OUT = ROOT / "IJIET_SUBMISSION" / "audit" / "visual_qa_word.txt"
PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_full.pdf"
CROP = ROOT / "IJIET_SUBMISSION" / "audit" / "visual_qa_pages" / "fig1_from_pdf.png"

WD_CHARACTER = 1


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def main() -> None:
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines = []
    try:
        lines.append(f"sections={doc.Sections.Count} tables={doc.Tables.Count} shapes={doc.InlineShapes.Count}")
        for i in range(1, doc.Sections.Count + 1):
            s = doc.Sections(i)
            ps = s.PageSetup
            lines.append(
                f"SEC {i} start={ps.SectionStart} cols={ps.TextColumns.Count} "
                f"colw={ps.TextColumns(1).Width:.2f} space={ps.TextColumns.Spacing:.2f} "
                f"width={ps.PageWidth:.2f} ml={ps.LeftMargin:.2f} mr={ps.RightMargin:.2f}"
            )
        for i in range(1, doc.Tables.Count + 1):
            t = doc.Tables(i)
            cap = ""
            try:
                p = t.Range.Paragraphs(1)
                cap = para_text(p)[:120]
            except Exception:
                pass
            # caption is usually previous paragraph
            prev = t.Range.Paragraphs(1).Range
            try:
                prev.Collapse(1)
                prev.Move(WD_CHARACTER, -2)
                cap_para = prev.Paragraphs(1)
                cap = para_text(cap_para)[:160]
                cap_style = str(cap_para.Style.NameLocal)
                cap_size = cap_para.Range.Font.Size
                cap_caps = cap_para.Range.Font.AllCaps
            except Exception as e:
                cap_style, cap_size, cap_caps = "?", "?", str(e)
            w = t.PreferredWidth
            lines.append(
                f"TBL {i} rows={t.Rows.Count} cols={t.Columns.Count} prefW={w} "
                f"auto={t.AllowAutoFit} capstyle={cap_style} capsize={cap_size} allcaps={cap_caps}"
            )
            lines.append(f"     CAP {cap}")
            # first header row font
            try:
                cell = t.Cell(1, 1)
                lines.append(
                    f"     H1 style={cell.Range.Style.NameLocal} size={cell.Range.Font.Size} "
                    f"w0={t.Columns(1).Width:.1f}"
                )
                widths = [t.Columns(c).Width for c in range(1, t.Columns.Count + 1)]
                lines.append(f"     widths={['%.1f'%x for x in widths]} sum={sum(widths):.1f}")
            except Exception as e:
                lines.append(f"     colerr {e}")
        for i in range(1, doc.InlineShapes.Count + 1):
            sh = doc.InlineShapes(i)
            lines.append(
                f"PIC {i} w={sh.Width:.1f} h={sh.Height:.1f} type={sh.Type}"
            )
        # first 12 paras
        lines.append("--- FRONT ---")
        for i in range(1, 15):
            p = doc.Paragraphs(i)
            raw = para_text(p)
            lines.append(
                f"P{i} style={p.Style.NameLocal} size={p.Range.Font.Size} "
                f"bold={p.Range.Font.Bold} italic={p.Range.Font.Italic} allcaps={p.Range.Font.AllCaps} "
                f"| {raw[:140]}"
            )
        # Heading 1 samples
        lines.append("--- H1 ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            try:
                st = str(doc.Paragraphs(i).Style.NameLocal)
            except Exception:
                continue
            if st == "Heading 1":
                p = doc.Paragraphs(i)
                lines.append(
                    f"H1 i={i} size={p.Range.Font.Size} bold={p.Range.Font.Bold} "
                    f"allcaps={p.Range.Font.AllCaps} | {para_text(p)}"
                )
        # Table Title style
        try:
            st = doc.Styles("Table Title")
            lines.append(
                f"STYLE Table Title size={st.Font.Size} allcaps={st.Font.AllCaps} bold={st.Font.Bold}"
            )
        except Exception as e:
            lines.append(f"STYLE Table Title {e}")
        try:
            st = doc.Styles("equation")
            lines.append(f"STYLE equation exists size={st.Font.Size}")
        except Exception as e:
            lines.append(f"STYLE equation {e}")
    finally:
        doc.Close(0)
        word.Quit()

    d = fitz.open(str(PDF))
    page = d[3]
    # crop figure region: y 50-418
    r = fitz.Rect(40, 45, 555, 420)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=r, alpha=False)
    pix.save(str(CROP))
    d.close()
    lines.append(f"crop {CROP} {pix.width}x{pix.height}")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-40:]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
