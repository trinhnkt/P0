#!/usr/bin/env python3
"""Deeper IJIET format probe: title spacing, H2 italic, back matter, eq, caption order."""
from __future__ import annotations

import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent.parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
OUT = HERE / "audit" / "format_a23_measure2.txt"

WD_ALIGN = {0: "left", 1: "center", 2: "right", 3: "justify"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines: list[str] = []
    try:
        p1 = doc.Paragraphs(1)
        pf = p1.Format
        f = p1.Range.Font
        lines.append(
            f"TITLE style={p1.Style.NameLocal!r} name={f.Name!r} sz={f.Size} "
            f"b={f.Bold} i={f.Italic} align={WD_ALIGN.get(int(p1.Alignment))} "
            f"sb={pf.SpaceBefore} sa={pf.SpaceAfter} ind={pf.FirstLineIndent} "
            f"ls={pf.LineSpacing} text={p1.Range.Text[:80]!r}"
        )
        # column widths of first 2-col section
        s2 = doc.Sections(2)
        tc = s2.PageSetup.TextColumns
        lines.append(f"sec2 cols={tc.Count}")
        for ci in range(1, tc.Count + 1):
            col = tc(ci)
            lines.append(f"  col{ci} width={col.Width}")

        lines.append("--- FRONT SPACING P1-P12 ---")
        for i in range(1, 13):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").strip()[:55]
            lines.append(
                f"P{i} {p.Style.NameLocal!r} sa={p.Format.SpaceAfter} "
                f"sb={p.Format.SpaceBefore} al={WD_ALIGN.get(int(p.Alignment))} | {t}"
            )

        lines.append("--- H2 italic first run ---")
        n = 0
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            if p.Style.NameLocal != "Heading 2":
                continue
            t = p.Range.Text.replace("\r", "").strip()
            r = p.Range
            lines.append(
                f"H2 {t[:50]!r} italic={r.Font.Italic} name={r.Font.Name!r} "
                f"sz={r.Font.Size} al={WD_ALIGN.get(int(p.Alignment))}"
            )
            n += 1
            if n >= 6:
                break

        lines.append("--- BACK MATTER ---")
        keys = (
            "Conflict of Interest",
            "CONFLICT OF INTEREST",
            "Author Contributions",
            "AUTHOR CONTRIBUTIONS",
            "Ethical Statement",
            "Data and Code Availability",
            "Generative AI",
            "Acknowledgment",
            "ACKNOWLEDGMENT",
            "References",
            "REFERENCES",
            "Creative Commons",
            "CC BY",
        )
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").strip()
            if any(k.lower() in t.lower()[:40] for k in keys) and len(t) < 80:
                lines.append(
                    f"BM {p.Style.NameLocal!r} {p.Range.Font.Name!r} "
                    f"{p.Range.Font.Size}pt b={p.Range.Font.Bold} "
                    f"al={WD_ALIGN.get(int(p.Alignment))} | {t[:70]}"
                )

        lines.append("--- EQUATION ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").strip()
            st = p.Style.NameLocal
            if st.lower() == "equation" or t.startswith("ECE"):
                lines.append(
                    f"EQ {st!r} sz={p.Range.Font.Size} name={p.Range.Font.Name!r} | {t[:90]}"
                )

        lines.append("--- CAPTION ORDER (prev style of table/fig) ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").replace("\x07", "").strip()
            if t.startswith("Table ") and len(t) > 10 and t[6].isdigit() and t[7] == ".":
                nxt = doc.Paragraphs(i + 1).Range.Text[:40].replace("\r", " ")
                lines.append(f"TABLECAP then next={nxt!r} | {t[:60]}")
            if t.startswith("Fig. "):
                prev = doc.Paragraphs(i - 1).Range.Text[:40].replace("\r", " ")
                lines.append(f"FIGCAP prev={prev!r} | {t[:70]}")

        lines.append("--- EMPTY FONT BODY ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            try:
                if p.Range.Tables.Count:
                    continue
            except Exception:
                pass
            if p.Style.NameLocal != "Text":
                continue
            name = p.Range.Font.Name or ""
            t = p.Range.Text.replace("\r", "").strip()
            if not name and len(t) > 40:
                lines.append(f"emptyFont i={i} sz={p.Range.Font.Size} | {t[:80]}")

        lines.append("--- TABLE PREF WIDTH ---")
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            lines.append(
                f"T{ti} prefW={tbl.PreferredWidth} rows={tbl.Rows.Count} "
                f"cols={tbl.Columns.Count} nest={tbl.NestingLevel}"
            )
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
