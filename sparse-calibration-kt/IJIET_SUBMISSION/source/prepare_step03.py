#!/usr/bin/env python3
"""IJIET-03: front matter only (title, authors, keywords).

Edits IJIET_SUBMISSION/source/main_ijiet_step03.docx.
Does not modify ijiet/, paper/, or step02 originals.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP02 = SRC / "main_ijiet_step02.docx"
STEP03_DOCX = SRC / "main_ijiet_step03.docx"
STEP03_DOC = SRC / "main_ijiet_step03.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step03.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step03_verify.txt"

TITLE = (
    "Sparse-Concept Calibration of Knowledge Tracing Models "
    "for Threshold-Based Educational Decisions"
)
AUTHORS_PLAIN = (
    "Khanh-Trinh Nguyen1, Tuan Dao Minh1, Duong Nguyen Tien1, "
    "Chi Thanh Nguyen2, and Van-Hau Nguyen1,*"
)
AFFIL_1 = "1 Hung Yen University of Technology and Education, Hung Yen, Vietnam"
AFFIL_2 = "2 Academy of Military Science and Technology, Ha Noi, Vietnam"
EMAIL = (
    "Email: trinhnk@utehy.edu.vn (K.-T.N.); tuanymc@utehy.edu.vn (T.D.M.); "
    "duongnt@utehy.edu.vn (D.N.T.); thanhnc@ioit.ai.vn (C.T.N.); "
    "haunv@utehy.edu.vn (V.-H.N.)"
)
CORR = "*Corresponding author"
KEYWORDS_TERMS = (
    "knowledge tracing, calibration, sparse concepts, learning analytics, "
    "educational decision support, mastery threshold"
)

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_ALIGN_CENTER = 1
WD_ALIGN_JUSTIFY = 3
WD_SAVE = -1


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def find_para(doc, predicate) -> int:
    for i in range(1, doc.Paragraphs.Count + 1):
        if predicate(doc.Paragraphs(i).Range.Text):
            return i
    raise RuntimeError("paragraph not found")


def superscript_chars(para, chars: set[str]) -> list[str]:
    applied = []
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    text = rng.Text
    for i, ch in enumerate(text):
        if ch in chars:
            r = para.Range
            r.Start = para.Range.Start + i
            r.End = r.Start + 1
            r.Font.Superscript = True
            r.Font.Name = "Times New Roman"
            applied.append(ch)
    return applied


def style_keywords(para) -> None:
    """Bold 'Keywords—' only; remainder italic, not bold (IJIET IndexTerms mix)."""
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Font.Name = "Times New Roman"
    rng.Font.Size = 9
    rng.Font.Bold = False
    rng.Font.Italic = True
    text = rng.Text
    marker = "Keywords—"
    if not text.startswith(marker):
        marker = "Keywords-"
    n = len(marker) if text.startswith(marker) else 9  # 'Keywords'
    label = para.Range
    label.Start = para.Range.Start
    label.End = para.Range.Start + n
    label.Font.Bold = True
    label.Font.Italic = False
    label.Font.Name = "Times New Roman"
    label.Font.Size = 9


def main() -> None:
    if not STEP02.exists():
        raise SystemExit(f"Missing {STEP02}")
    shutil.copy2(STEP02, STEP03_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP03_DOCX))

        # Title: first paragraph (template style Text, 20 pt, not bold).
        p1 = doc.Paragraphs(1)
        try:
            p1.Style = "Text"
        except Exception:
            pass
        set_para_text(p1, TITLE)
        r = p1.Range
        r.MoveEnd(WD_CHARACTER, -1)
        r.Font.Name = "Times New Roman"
        r.Font.Size = 20
        r.Font.Bold = False
        r.Font.Italic = False
        p1.Alignment = WD_ALIGN_CENTER
        lines.append(f"TITLE={p1.Range.Text.strip()}")
        lines.append(f"TITLE_BOLD={r.Font.Bold} SIZE={r.Font.Size}")

        # Authors
        p2 = doc.Paragraphs(2)
        try:
            p2.Style = "Style Author + (Asian) MS Mincho"
        except Exception:
            try:
                p2.Style = "Authors"
            except Exception:
                pass
        set_para_text(p2, AUTHORS_PLAIN)
        r2 = p2.Range
        r2.MoveEnd(WD_CHARACTER, -1)
        r2.Font.Name = "Times New Roman"
        r2.Font.Size = 11
        r2.Font.Bold = False
        p2.Alignment = WD_ALIGN_CENTER
        supers = superscript_chars(p2, set("12*"))
        lines.append(f"AUTHORS={p2.Range.Text.strip()}")
        lines.append(f"SUPERSCRIPTS={''.join(supers)}")

        # Affiliations / email / corresponding — locate, do not recreate IEEE \thanks.
        i1 = find_para(doc, lambda t: t.strip().startswith("1 ") and "Hung Yen" in t)
        i2 = find_para(doc, lambda t: t.strip().startswith("2 ") and "Academy" in t)
        ie = find_para(doc, lambda t: t.strip().startswith("Email:"))
        ic = find_para(doc, lambda t: "Corresponding author" in t)

        for idx, text, style in (
            (i1, AFFIL_1, "Affiliation"),
            (i2, AFFIL_2, "Affiliation"),
            (ie, EMAIL, "Affiliation"),
            (ic, CORR, "Affiliation"),
        ):
            p = doc.Paragraphs(idx)
            try:
                p.Style = style
            except Exception:
                pass
            set_para_text(p, text)
            rr = p.Range
            rr.MoveEnd(WD_CHARACTER, -1)
            rr.Font.Name = "Times New Roman"
            rr.Font.Size = 9
            rr.Font.Bold = False
            p.Alignment = WD_ALIGN_CENTER
            lines.append(f"P{idx}={text}")

        # Keywords — IJIET label, not IEEE Index Terms.
        ik = find_para(doc, lambda t: t.strip().startswith("Keywords") or t.strip().startswith("Index Terms"))
        pk = doc.Paragraphs(ik)
        try:
            pk.Style = "IndexTerms"
        except Exception:
            pass
        set_para_text(pk, "Keywords—" + KEYWORDS_TERMS)
        pk.Alignment = WD_ALIGN_JUSTIFY
        style_keywords(pk)
        lines.append(f"KEYWORDS={pk.Range.Text.strip()}")

        # Guard: do not anonymize; names must remain.
        body = doc.Content.Text
        assert "Khanh-Trinh Nguyen" in body
        assert "haunv@utehy.edu.vn" in body
        assert "Index Terms" not in body
        assert "Manuscript received" not in body

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(f"PAGES={pages}")
        lines.append(f"WORDS={words}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP03_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP03_DOC), WD_FORMAT_DOC)
        doc.ExportAsFixedFormat(
            str(OUT_PDF),
            17,
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
        lines.append(f"PDF={OUT_PDF} EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}")
    finally:
        if doc is not None:
            doc.Close(WD_SAVE)
        word.Quit()

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
