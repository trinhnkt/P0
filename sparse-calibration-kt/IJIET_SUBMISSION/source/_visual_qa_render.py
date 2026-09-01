#!/usr/bin/env python3
"""Rasterize manuscript, template, and 2026 IJIET papers for visual QA."""
from __future__ import annotations

from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "IJIET_SUBMISSION" / "audit"
SRC = ROOT / "IJIET_SUBMISSION" / "source"
OUT = AUDIT / "visual_qa_pages"
REFS = AUDIT / "visual_refs"
FULL_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_full.pdf"
TPL_DOC = SRC / "template" / "IJIET_template.doc"
TPL_PDF = REFS / "IJIET_template.pdf"
DPI = 140


def export_template_pdf() -> None:
    if TPL_PDF.exists() and TPL_PDF.stat().st_size > 10_000:
        return
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(TPL_DOC))
        REFS.mkdir(parents=True, exist_ok=True)
        if TPL_PDF.exists():
            TPL_PDF.unlink()
        doc.ExportAsFixedFormat(str(TPL_PDF), 17, OpenAfterExport=False, OptimizeFor=0)
    finally:
        if doc is not None:
            doc.Close(0)
        word.Quit()


def render(pdf: Path, dest: Path, prefix: str, max_pages: int | None = None) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    d = fitz.open(str(pdf))
    n = d.page_count if max_pages is None else min(d.page_count, max_pages)
    zoom = DPI / 72
    mat = fitz.Matrix(zoom, zoom)
    paths = []
    for i in range(n):
        pix = d[i].get_pixmap(matrix=mat, alpha=False)
        p = dest / f"{prefix}_p{i + 1:02d}.png"
        pix.save(str(p))
        paths.append(p)
        print(f"wrote {p.name} {pix.width}x{pix.height}")
    d.close()
    return paths


def layout_dump(pdf: Path) -> None:
    d = fitz.open(str(pdf))
    lines = [f"pages={d.page_count} size={d[0].rect}"]
    for i, page in enumerate(d):
        r = page.rect
        blocks = page.get_text("blocks")
        imgs = page.get_images()
        lines.append(f"\n=== PAGE {i + 1} rect={r} n_blocks={len(blocks)} n_imgs={len(imgs)} ===")
        for b in blocks:
            x0, y0, x1, y1, text, *_ = b[:6] if len(b) >= 5 else (*b, "")
            t = str(text).replace("\n", " | ")[:180]
            overflow_r = x1 > r.width - 40
            overflow_b = y1 > r.height - 40
            flag = ""
            if overflow_r:
                flag += " RIGHT"
            if overflow_b:
                flag += " BOTTOM"
            w = x1 - x0
            lines.append(
                f"  ({x0:.1f},{y0:.1f})-({x1:.1f},{y1:.1f}) w={w:.1f}{flag} | {t}"
            )
        for ln in page.get_links():
            lines.append(f"  LINK {ln}")
    d.close()
    (AUDIT / "visual_qa_layout.txt").write_text("\n".join(lines), encoding="utf-8")
    print("layout dump written")


def main() -> None:
    export_template_pdf()
    render(FULL_PDF, OUT, "ms")
    render(TPL_PDF, OUT, "tpl", max_pages=2)
    p2484 = REFS / "IJIET-V16N1-2484.pdf"
    p2667 = REFS / "IJIET-V16N8-2667.pdf"
    render(p2484, OUT, "p2484", max_pages=2)
    render(p2667, OUT, "p2667", max_pages=2)
    layout_dump(FULL_PDF)


if __name__ == "__main__":
    main()
