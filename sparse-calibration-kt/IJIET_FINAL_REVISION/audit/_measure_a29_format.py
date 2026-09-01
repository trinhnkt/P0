#!/usr/bin/env python3
"""Measure A29 named Word+PDF against IJIET_template.doc geometry."""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent.parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
PDF = HERE / "output" / "main_ijiet_full.pdf"
OUT = HERE / "audit" / "format_a29_measure.txt"

WD_ALIGN = {0: "left", 1: "center", 2: "right", 3: "justify"}

TPL = {
    "page_w": 595.35,
    "page_h": 841.95,
    "T": 50.45,
    "B": 50.45,
    "L": 46.80,
    "R": 46.80,
    "col_w": 243.65,
    "gutter": 14.4,
}


def font_of(rng) -> tuple[str, float, int, int]:
    f = rng.Font
    name = f.Name or ""
    sz = float(f.Size) if f.Size not in (None, 9999999) else -1
    b = int(f.Bold) if f.Bold not in (None, 9999999) else -1
    i = int(f.Italic) if f.Italic not in (None, 9999999) else -1
    return name, sz, b, i


def inner_text(doc, p) -> str:
    return doc.Range(p.Range.Start, p.Range.End - 1).Text.replace("\r", "").replace("\x07", "")


def pdf_page1(path: Path) -> list[str]:
    d = fitz.open(str(path))
    lines = [f"pdf_pages={d.page_count} rect={tuple(round(x, 2) for x in d[0].rect)}"]
    sizes: Counter[tuple[str, float]] = Counter()
    samples = []
    for b in d[0].get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s.get("text", "").strip()
                if not t:
                    continue
                font = s.get("font", "")
                sz = round(s["size"], 1)
                sizes[(font, sz)] += 1
                if any(
                    t.startswith(x)
                    for x in (
                        "Reproducible",
                        "Khanh-Trinh",
                        "1 Hung Yen",
                        "2 Academy",
                        "Email:",
                        "Abstract",
                        "Keywords",
                        "I. INTRODUCTION",
                    )
                ):
                    samples.append(f"  {sz:4.1f} {font} | {t[:70]}")
    d.close()
    lines.append("page1_span_fonts=" + str(dict(sizes)))
    lines.extend(samples)
    return lines


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    lines: list[str] = [f"file={DOCX}", f"pdf={PDF}"]
    try:
        lines.append(
            f"pages={doc.ComputeStatistics(2)} words={doc.ComputeStatistics(0)} "
            f"paras={doc.Paragraphs.Count} tables={doc.Tables.Count} figs={doc.InlineShapes.Count}"
        )
        for i in range(1, doc.Sections.Count + 1):
            s = doc.Sections(i)
            ps = s.PageSetup
            hdr = (s.Headers(1).Range.Text or "").replace("\r", " ").strip()
            ftr = (s.Footers(1).Range.Text or "").replace("\r", " ").strip()
            cols = ps.TextColumns.Count
            gutter = float(ps.TextColumns.Spacing) if cols >= 2 else 0.0
            cw = None
            if cols >= 1:
                try:
                    cw = float(ps.TextColumns(1).Width)
                except Exception:
                    cw = None
            lines.append(
                f"sec{i} paper={ps.PageWidth:.2f}x{ps.PageHeight:.2f} "
                f"T={ps.TopMargin:.2f} B={ps.BottomMargin:.2f} "
                f"L={ps.LeftMargin:.2f} R={ps.RightMargin:.2f} "
                f"cols={cols} colw={cw} gutter={gutter:.2f} "
                f"header={hdr[:40]!r} footer={ftr[:40]!r}"
            )

        lines.append("--- FRONT ---")
        for i in range(1, 16):
            p = doc.Paragraphs(i)
            t = inner_text(doc, p).strip().replace("\x0c", "")
            if not t:
                continue
            name, sz, b, it = font_of(doc.Range(p.Range.Start, p.Range.End - 1))
            al = WD_ALIGN.get(int(p.Alignment), str(p.Alignment))
            pf = p.Format
            lines.append(
                f"P{i} {p.Style.NameLocal!r} {name} {sz}pt b={b} i={it} {al} "
                f"ind={pf.FirstLineIndent:.1f} sa={pf.SpaceAfter:.1f} | {t[:85]}"
            )

        lines.append("--- H1 / H2 / CAPTION / ENDHEAD ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = inner_text(doc, p).strip()
            st = p.Style.NameLocal
            name, sz, b, it = font_of(doc.Range(p.Range.Start, p.Range.End - 1))
            al = WD_ALIGN.get(int(p.Alignment), str(p.Alignment))
            if st.startswith("Heading 1"):
                lines.append(f"H1 i={i} {name} {sz}pt b={b} {al} | {t[:70]}")
            elif st.startswith("Heading 2"):
                lines.append(f"H2 i={i} {name} {sz}pt i={it} {al} | {t[:70]}")
            elif t.startswith("Table ") or t.startswith("Fig."):
                lines.append(f"CAP i={i} {st!r} {name} {sz}pt b={b} i={it} {al} | {t[:80]}")
            elif st == "Reference Head":
                lines.append(f"RH i={i} {name} {sz}pt b={b} {al} | {t[:50]}")

        body_fonts: Counter[str] = Counter()
        body_sz: Counter[float] = Counter()
        indent_set: Counter[float] = Counter()
        space_set: Counter[float] = Counter()
        align_set: Counter[str] = Counter()
        odd: list[str] = []
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            try:
                if p.Range.Tables.Count:
                    continue
            except Exception:
                pass
            if p.Style.NameLocal != "Text":
                continue
            t = inner_text(doc, p).strip()
            if len(t) < 60:
                continue
            name, sz, b, it = font_of(doc.Range(p.Range.Start, p.Range.End - 1))
            al = WD_ALIGN.get(int(p.Alignment), str(p.Alignment))
            body_fonts[name or "(empty)"] += 1
            body_sz[sz] += 1
            indent_set[round(p.Format.FirstLineIndent, 1)] += 1
            space_set[round(p.Format.LineSpacing, 1)] += 1
            align_set[al] += 1
            if name and name != "Times New Roman":
                odd.append(f"nonTNR i={i} {name} {sz} | {t[:50]}")
            if sz not in (-1, 10.0) and "Reproducible" not in t[:20]:
                odd.append(f"sz i={i} {sz} | {t[:50]}")
        lines.append("--- BODY Text ---")
        lines.append(f"body_fonts={dict(body_fonts)}")
        lines.append(f"body_sz={dict(body_sz)}")
        lines.append(f"indent={dict(indent_set)}")
        lines.append(f"line_spacing={dict(space_set)}")
        lines.append(f"align={dict(align_set)}")
        lines.extend(odd[:20])

        lines.append("--- TABLES ---")
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            cell_sz: Counter[float] = Counter()
            cell_font: Counter[str] = Counter()
            for r in range(1, tbl.Rows.Count + 1):
                for c in range(1, tbl.Columns.Count + 1):
                    try:
                        rng = tbl.Cell(r, c).Range
                    except Exception:
                        continue
                    name, sz, b, it = font_of(rng)
                    cell_font[name or "(mixed)"] += 1
                    cell_sz[sz] += 1
            lines.append(
                f"T{ti} {tbl.Rows.Count}x{tbl.Columns.Count} fonts={dict(cell_font)} sz={dict(cell_sz)}"
            )

        lines.append("--- FIG ---")
        for i in range(1, doc.InlineShapes.Count + 1):
            sh = doc.InlineShapes(i)
            lines.append(f"fig{i} w={sh.Width:.1f} h={sh.Height:.1f}")

        lines.append("--- REFS ---")
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            t = inner_text(doc, p).strip()
            if t == "References" or t.startswith("References"):
                for j in range(i, min(i + 6, doc.Paragraphs.Count) + 1):
                    q = doc.Paragraphs(j)
                    qt = inner_text(doc, q).strip()[:70]
                    name, sz, b, it = font_of(doc.Range(q.Range.Start, q.Range.End - 1))
                    lines.append(
                        f"REF {q.Style.NameLocal!r} {name} {sz}pt hang={q.Format.FirstLineIndent:.1f} al={WD_ALIGN.get(int(q.Alignment), q.Alignment)} | {qt}"
                    )
                break

        lines.append("--- PDF P1 ---")
        lines.extend(pdf_page1(PDF))
        lines.append(f"TPL={TPL}")
    finally:
        doc.Close(0)
        word.Quit()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
