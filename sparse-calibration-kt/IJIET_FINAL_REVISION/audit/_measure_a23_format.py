#!/usr/bin/env python3
"""Measure IJIET_FINAL_REVISION Word vs official template geometry."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent.parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
OUT = HERE / "audit" / "format_a23_measure.txt"

WD_ALIGN = {0: "left", 1: "center", 2: "right", 3: "justify"}


def font_of(rng) -> tuple[str, float, int, int]:
    f = rng.Font
    name = f.Name or ""
    sz = float(f.Size) if f.Size not in (None, 9999999) else -1
    b = int(f.Bold) if f.Bold not in (None, 9999999) else -1
    i = int(f.Italic) if f.Italic not in (None, 9999999) else -1
    return name, sz, b, i


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines: list[str] = []
    try:
        lines.append(f"file={DOCX}")
        lines.append(f"pages={doc.ComputeStatistics(2)} words={doc.ComputeStatistics(0)}")
        lines.append(f"sections={doc.Sections.Count} tables={doc.Tables.Count} figs={doc.InlineShapes.Count}")
        for i in range(1, doc.Sections.Count + 1):
            s = doc.Sections(i)
            ps = s.PageSetup
            hdr = s.Headers(1).Range.Text.replace("\r", " ").strip()
            ftr = s.Footers(1).Range.Text.replace("\r", " ").strip()
            lines.append(
                f"  sec{i} paper={ps.PageWidth:.2f}x{ps.PageHeight:.2f} "
                f"T={ps.TopMargin:.2f} B={ps.BottomMargin:.2f} "
                f"L={ps.LeftMargin:.2f} R={ps.RightMargin:.2f} "
                f"cols={ps.TextColumns.Count} gutter={ps.TextColumns.Spacing} "
                f"header={hdr!r} footer={ftr!r}"
            )

        lines.append("--- FRONT / STYLES ---")
        h1s = []
        h2s = []
        caps = []
        fonts = Counter()
        odd_body = []
        for i in range(1, min(doc.Paragraphs.Count, 40) + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").replace("\x07", "").strip()
            if not t or t == "\x0c":
                continue
            st = p.Style.NameLocal
            name, sz, b, it = font_of(p.Range)
            al = WD_ALIGN.get(int(p.Alignment), str(p.Alignment))
            lines.append(f"P{i} {st!r} {name} {sz}pt b={b} i={it} {al} | {t[:90]}")

        lines.append("--- H1 / H2 / CAPTIONS ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").replace("\x07", "").strip()
            st = p.Style.NameLocal
            name, sz, b, it = font_of(p.Range)
            if st.startswith("Heading 1") or t.startswith(
                ("I. ", "II. ", "III. ", "IV. ", "V. ", "VI. ")
            ) and len(t) < 80:
                if "INTRODUCTION" in t or "LITERATURE" in t or "MATERIALS" in t or "RESULT" in t or "DISCUSSION" in t or "CONCLUSION" in t:
                    h1s.append((st, name, sz, b, it, t))
            if st.startswith("Heading 2") or (len(t) > 2 and t[0].isalpha() and t[1] == "." and len(t) < 90):
                if t[:2] in {f"{c}." for c in "ABCDEFGHIJK"}:
                    h2s.append((st, name, sz, it, t[:70]))
            if t.startswith("Table ") or t.startswith("Fig."):
                caps.append((st, name, sz, b, it, t[:90]))

        for row in h1s:
            lines.append(f"H1 {row}")
        for row in h2s[:16]:
            lines.append(f"H2 {row}")
        for row in caps:
            lines.append(f"CAP {row}")

        lines.append("--- BODY SAMPLE (first Text 10pt after intro) ---")
        body_fonts = Counter()
        body_sz = Counter()
        indent_set = Counter()
        space_set = Counter()
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            try:
                if p.Range.Tables.Count:
                    continue
            except Exception:
                pass
            st = p.Style.NameLocal
            if st != "Text":
                continue
            t = p.Range.Text.replace("\r", "").strip()
            if len(t) < 80:
                continue
            name, sz, b, it = font_of(p.Range)
            body_fonts[name] += 1
            body_sz[sz] += 1
            indent_set[round(p.FirstLineIndent, 1)] += 1
            space_set[round(p.LineSpacing, 1)] += 1
        lines.append(f"body_fonts={dict(body_fonts)}")
        lines.append(f"body_sz={dict(body_sz)}")
        lines.append(f"first_indent_pt={dict(indent_set)}")
        lines.append(f"line_spacing_pt={dict(space_set)}")

        lines.append("--- TABLES ---")
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            cell_fonts = Counter()
            cell_sz = Counter()
            nrows, ncols = tbl.Rows.Count, tbl.Columns.Count
            for r in range(1, min(nrows, 4) + 1):
                for c in range(1, min(ncols, 6) + 1):
                    try:
                        rng = tbl.Cell(r, c).Range
                    except Exception:
                        continue
                    name, sz, b, it = font_of(rng)
                    cell_fonts[name] += 1
                    cell_sz[sz] += 1
            lines.append(
                f"T{ti} {nrows}x{ncols} fonts={dict(cell_fonts)} sz={dict(cell_sz)}"
            )

        lines.append("--- FIGURE ---")
        for i in range(1, doc.InlineShapes.Count + 1):
            sh = doc.InlineShapes(i)
            lines.append(f"fig{i} w={sh.Width:.1f} h={sh.Height:.1f} type={sh.Type}")

        lines.append("--- REFS SAMPLE ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = p.Range.Text.replace("\r", " ").strip()
            if t.startswith("References") or t == "REFERENCES":
                for j in range(i, min(i + 8, doc.Paragraphs.Count) + 1):
                    q = doc.Paragraphs(j)
                    qt = q.Range.Text.replace("\r", " ").strip()[:80]
                    name, sz, b, it = font_of(q.Range)
                    st = q.Style.NameLocal
                    lines.append(f"REF {st!r} {name} {sz}pt hang={q.FirstLineIndent:.1f} | {qt}")
                break
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
