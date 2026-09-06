#!/usr/bin/env python3
"""Export manuscript/main_ijiet_full.docx → output/main_ijiet_full.pdf.

Does not save the Word source. Does not touch IJIET_SUBMISSION/.
"""
from __future__ import annotations

from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
PDF = HERE / "output" / "main_ijiet_full.pdf"
REPORT = HERE / "audit" / "compile_verify.txt"

WD_FORMAT_PDF = 17


def main() -> None:
    if not DOCX.exists():
        raise SystemExit(f"missing {DOCX}")
    PDF.parent.mkdir(parents=True, exist_ok=True)
    if PDF.exists():
        PDF.unlink()

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=True)
    try:
        doc.ExportAsFixedFormat(
            str(PDF),
            WD_FORMAT_PDF,
            OpenAfterExport=False,
            OptimizeFor=0,
            Item=0,
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
        )
    finally:
        doc.Close(0)
        word.Quit()

    pdf = fitz.open(str(PDF))
    n_pages = pdf.page_count
    text = "".join(p.get_text() for p in pdf)
    pdf.close()
    compact = "".join(text.split()).lower()
    checks = {
        "pages_8_to_10": 8 <= n_pages <= 10,
        "ece_1136": "0.1136" in text,
        "ece_2280": "0.2280" in text,
        "far_196": "0.196" in text,
        "far_268": "0.268" in text,
        "fig1": "Fig. 1." in text,
        "ref21": "uncertainty-awareknowledgetracing" in compact,
        "ref22": "knowingwhentodefer" in compact,
    }
    REPORT.write_text(
        f"source={DOCX}\n"
        f"pdf={PDF}\n"
        f"pages={n_pages}\n"
        f"bytes={PDF.stat().st_size}\n"
        + "\n".join(f"{k}={v}" for k, v in checks.items())
        + "\n",
        encoding="utf-8",
    )
    print(REPORT.read_text(encoding="utf-8"))
    if not all(checks.values()):
        raise SystemExit("compile checks failed")


if __name__ == "__main__":
    main()
