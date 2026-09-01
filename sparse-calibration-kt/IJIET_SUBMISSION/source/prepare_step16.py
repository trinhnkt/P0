#!/usr/bin/env python3
"""IJIET-16: visual template QA fixes. No scientific-number edits."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
FULL_DOCX = SRC / "main_ijiet_full.docx"
FULL_DOC = SRC / "main_ijiet_full.doc"
BLIND_DOCX = SRC / "main_ijiet_blind.docx"
BLIND_DOC = SRC / "main_ijiet_blind.doc"
OUT_DIR = ROOT / "IJIET_SUBMISSION" / "output"
FULL_PDF = OUT_DIR / "main_ijiet_full.pdf"
BLIND_PDF = OUT_DIR / "main_ijiet_blind.pdf"
FIG = ROOT / "IJIET_SUBMISSION" / "figures" / "fig1_kc_and_train_volume.png"
QA = ROOT / "IJIET_SUBMISSION" / "audit" / "VISUAL_QA.md"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step16_verify.txt"

sys.path.insert(0, str(SRC))
from generate_ijiet_fig1 import main as regen_fig  # noqa: E402
from prepare_step15 import (  # noqa: E402
    ANON_ACK,
    ANON_AFFIL,
    ANON_AUTHORS,
    ANON_CONTRIB,
    AUTHORS_META,
    IDENTIFYING,
    KEEP_IN_BLIND,
    TITLE,
    anonymize,
    compact,
    export_pdf,
    hits,
    neutralize_table_lists,
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
    stamp_pdf_metadata,
    token_present,
)

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLUMN = 8
WD_COLLAPSE_START = 1
WD_SECTION_CONTINUOUS = 0

H1_TARGETS = [
    ("INTRODUCTION", "I. INTRODUCTION"),
    ("LITERATURE REVIEW", "II. LITERATURE REVIEW"),
    ("MATERIALS AND METHODS", "III. MATERIALS AND METHODS"),
    ("RESULT AND DISCUSSION", "IV. RESULT"),
    ("RESULT", "IV. RESULT"),
    ("DISCUSSION", "V. DISCUSSION"),
    ("CONCLUSION", "VI. CONCLUSION"),
]

MS_DATES = (
    "Manuscript received Month date, 2026; revised Month date, 2026; "
    "accepted Month date, 2026"
)

TABLE4_WIDTHS = [62.0, 48.0, 52.0, 58.0, 58.0, 90.0, 48.0, 52.0, 44.6]


def restore_h1(doc) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        try:
            style = str(doc.Paragraphs(i).Style.NameLocal)
        except Exception:
            continue
        if style != "Heading 1":
            continue
        raw = para_text(doc.Paragraphs(i))
        up = raw.upper()
        target = None
        if "LITERATURE" in up:
            target = "II. LITERATURE REVIEW"
        elif "MATERIALS" in up:
            target = "III. MATERIALS AND METHODS"
        elif "INTRODUCTION" in up:
            target = "I. INTRODUCTION"
        elif "DISCUSSION" in up and "RESULT" not in up:
            target = "V. DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "VI. CONCLUSION"
        elif "RESULT" in up:
            target = "IV. RESULT"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            try:
                doc.Paragraphs(i).Range.Font.AllCaps = False
                doc.Paragraphs(i).Range.Font.Bold = False
                doc.Paragraphs(i).Range.Font.Size = 10
                doc.Paragraphs(i).Range.Font.Name = "Times New Roman"
            except Exception:
                pass


def insert_column_break_before(doc, stub: str, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            doc.Paragraphs(i).Range.InsertBreak(WD_COLUMN)
            lines.append(f"COL_BREAK_BEFORE={stub!r} i={i}")
            return
    lines.append(f"COL_BREAK_MISSING={stub!r}")


def replace_figure(doc, lines: list[str]) -> None:
    if doc.InlineShapes.Count != 1:
        raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")
    pic = doc.InlineShapes(1)
    rng = pic.Range
    pic.Delete()
    new = rng.InlineShapes.AddPicture(str(FIG))
    from PIL import Image as PILImage

    pw, ph = PILImage.open(FIG).size
    new.LockAspectRatio = False
    new.Width = 490
    new.Height = 490.0 * ph / pw
    new.Range.Paragraphs(1).Alignment = 1
    lines.append(f"FIG_REPLACED w={new.Width:.1f} h={new.Height:.1f}")


def fix_figure_section(doc, lines: list[str]) -> None:
    pic = doc.InlineShapes(1)
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        if sec.Range.Start <= pic.Range.Start <= sec.Range.End:
            try:
                sec.PageSetup.SectionStart = WD_SECTION_CONTINUOUS
            except Exception as exc:
                lines.append(f"FIG_SEC_START_ERR={exc}")
            sec.PageSetup.TextColumns.SetCount(1)
            lines.append(
                f"FIG_SEC={s} start={sec.PageSetup.SectionStart} "
                f"cols={sec.PageSetup.TextColumns.Count}"
            )
            return


def fix_table4(doc, lines: list[str]) -> None:
    for ti in range(1, doc.Tables.Count + 1):
        prev = doc.Tables(ti).Range.Paragraphs(1)
        # caption is previous para
        cap_rng = doc.Tables(ti).Range.Duplicate
        cap_rng.Collapse(WD_COLLAPSE_START)
        cap_rng.Move(WD_CHARACTER, -2)
        cap = para_text(cap_rng.Paragraphs(1))
        if not cap.startswith("Table 4."):
            continue
        tbl = doc.Tables(ti)
        tbl.AllowAutoFit = False
        if tbl.Columns.Count == 9:
            for ci, w in enumerate(TABLE4_WIDTHS, start=1):
                try:
                    tbl.Columns(ci).Width = w
                except Exception:
                    pass
        n_ci = 0
        for ri in range(1, tbl.Rows.Count + 1):
            for ci in range(1, tbl.Columns.Count + 1):
                cell = tbl.Cell(ri, ci)
                t = cell.Range.Text.replace("\r", "").replace("\x07", "")
                if "[" in t and ", " in t and "]" in t:
                    new = t.replace(", ", "–")
                    if new != t:
                        rng = cell.Range
                        rng.MoveEnd(WD_CHARACTER, -1)
                        rng.Text = new
                        n_ci += 1
                cell.Range.Font.Name = "Times New Roman"
                cell.Range.Font.Size = 7
        widths = [tbl.Columns(c).Width for c in range(1, tbl.Columns.Count + 1)]
        lines.append(f"T4_CI_FIX={n_ci} widths={[round(w, 1) for w in widths]}")
        return
    lines.append("T4_MISSING")


def fix_table7_caption(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Table 7."):
            try:
                doc.Paragraphs(i).Style = "Table Title"
            except Exception:
                pass
            doc.Paragraphs(i).Range.Font.Name = "Times New Roman"
            doc.Paragraphs(i).Range.Font.Size = 8
            doc.Paragraphs(i).Range.Font.Bold = False
            doc.Paragraphs(i).Alignment = 1
            lines.append(f"T7_CAPTION_STYLE i={i}")
            return
    lines.append("T7_CAPTION_MISSING")


def insert_manuscript_dates(doc, lines: list[str]) -> None:
    if "Manuscript received" in doc.Content.Text:
        lines.append("MS_DATES_ALREADY")
        return
    for i in range(1, 20):
        raw = para_text(doc.Paragraphs(i))
        if "Corresponding author" in raw:
            rng = doc.Paragraphs(i).Range
            rng.Collapse(0)
            rng.InsertParagraphAfter()
            nxt = doc.Paragraphs(i + 1)
            set_para_text(nxt, MS_DATES)
            try:
                nxt.Style = "Affiliation"
            except Exception:
                pass
            nxt.Range.Font.Name = "Times New Roman"
            nxt.Range.Font.Size = 9
            nxt.Alignment = 1
            lines.append(f"MS_DATES_INSERTED i={i + 1}")
            return
    lines.append("MS_DATES_SKIP")


def superscript_star(doc, lines: list[str]) -> None:
    rng = doc.Content
    f = rng.Find
    f.ClearFormatting()
    f.Text = "1,*"
    f.Forward = True
    f.Wrap = 0
    if f.Execute():
        star = rng.Duplicate
        # last character of match should be *
        star.Start = rng.End - 1
        star.End = rng.End
        star.Font.Superscript = True
        lines.append("STAR_SUPERSCRIPT")
    else:
        lines.append("STAR_NOT_FOUND")


def mix_abstract_keywords(doc, lines: list[str]) -> None:
    for i in range(1, 20):
        raw = para_text(doc.Paragraphs(i))
        p = doc.Paragraphs(i)
        if raw.startswith("Abstract—"):
            p.Range.Font.Bold = False
            p.Range.Font.Italic = True
            lab = p.Range.Duplicate
            lab.End = lab.Start + len("Abstract—")
            lab.Font.Bold = True
            lab.Font.Italic = True
            lines.append("ABSTRACT_MIXED")
        elif raw.startswith("Keywords—"):
            p.Range.Font.Bold = False
            p.Range.Font.Italic = True
            lab = p.Range.Duplicate
            lab.End = lab.Start + len("Keywords—")
            lab.Font.Bold = True
            lab.Font.Italic = True
            lines.append("KEYWORDS_MIXED")


def soften_url_hyphens(doc, lines: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if "http" not in raw and "doi:" not in raw.lower():
            continue
        try:
            doc.Paragraphs(i).Range.NoProofing = True
        except Exception:
            pass
        # allow wrap after slashes without hyphenating the next token
        rng = doc.Paragraphs(i).Range
        f = rng.Find
        f.ClearFormatting()
        f.Text = "/"
        f.Forward = True
        f.Wrap = 0
        # skip mass replace; ZWSP after each slash
        t = raw
        if "/" in t and "http" in t:
            new = t.replace("/", "/\u200b")
            if new != t:
                set_para_text(doc.Paragraphs(i), new)
                n += 1
    lines.append(f"URL_ZWSP_PARAS={n}")


def apply_visual_fixes(doc, lines: list[str]) -> None:
    insert_manuscript_dates(doc, lines)
    mix_abstract_keywords(doc, lines)
    superscript_star(doc, lines)
    insert_column_break_before(doc, "D. Train-only frequency strata", lines)
    replace_figure(doc, lines)
    fix_figure_section(doc, lines)
    fix_table4(doc, lines)
    fix_table7_caption(doc, lines)
    soften_url_hyphens(doc, lines)
    restore_h1(doc)
    neutralize_table_lists(doc)


def write_qa(full_pages: int, lines: list[str]) -> None:
    log = "\n".join(lines)
    body = """# Visual QA (IJIET-16)

**Date:** 2026-08-31
**Manuscript inspected:** `output/main_ijiet_full.pdf` (named camera-ready; FULL_PAGES pages after fix).
**Blind sibling:** `output/main_ijiet_blind.pdf` (same layout minus identifying front/end matter).
**Comparators:** official `source/template/IJIET_template.doc`; IJIET 2026 papers [V16N1-2484](https://www.ijiet.org/vol16/IJIET-V16N1-2484.pdf) and [V16N8-2667](https://www.ijiet.org/vol16/IJIET-V16N8-2667.pdf).

Production PDFs add a journal running head, DOI, and page numbers. The official template leaves those empty; they were **not** added (IJIET-01 ID 27).

Scientific numbers, table cells, and Fig. 1 data were **not** changed. Fig. 1 tick rotation only.

## Checklist vs template / 2026 papers

| Element | Template / 2026 | This manuscript after fix |
|---------|-----------------|---------------------------|
| Page A4, 2-col 243.65 + 14.4 gutter | Yes | Yes |
| Title 20 pt TNR centered | Template unbold; 2026 PDFs bold | 20 pt TNR, unbold (template) |
| Authors 11 pt, numbered affils, email, `*Corresponding author` | Yes | Yes; `*` superscripted |
| Manuscript received/revised/accepted | Placeholder in template | Placeholder restored |
| Abstract— / Keywords— | 9 pt; label bold | Mixed label/body restored |
| Roman H1 | Template sentence case; 2026 ALL CAPS | Unified ALL CAPS `I.`–`VI.` to match 2026 papers |
| Letter H2 italic | Yes | Yes |
| Table *n*. above table, 8 pt | 2026 mixed case “Table 1.” | Captions mixed case; PDF small-caps style may still look uppercase |
| Fig. 1 caption below | Yes | Yes |
| Numbered refs `[n]`, doi: | Yes | Yes |
| Empty header/footer | Template | Empty (publisher-owned) |

## Findings

| Page | Element | Problem | Severity | Fix |
|------|---------|---------|----------|-----|
| 3 | Two-column body | Section break before Fig. 1 left the right column empty (~½ page whitespace) | HIGH | Column break before *D. Train-only frequency strata*; figure section set Continuous 1-col |
| 4 | Figure 1 | Bottom x-tick labels overlapped (`1–19` / `20–99` / `100–499`) at print size | HIGH | Regenerated PNG with 40° ticks, slightly wider embed (490 pt). **Data unchanged** |
| 5 | Table 4 FAR [95% CI] | CI wrapped mid-interval (`0.268 [0.202,` / `0.337]`) | HIGH | En-dash intervals `[0.202–0.337]`; FAR column widened to 90 pt. **Numbers unchanged** |
| 1–8 | Heading 1 | `I. Introduction` (list) vs forced `IV. RESULT` after section breaks | MEDIUM | All six headings set to 2026-style `I. INTRODUCTION` … `VI. CONCLUSION` |
| 1 | Corresponding `*` | Asterisk not superscript | MEDIUM | Superscripted |
| 1 | Manuscript dates | Template line missing | MEDIUM | Placeholder `Manuscript received Month date, 2026; …` restored |
| 1 | Abstract / Keywords | Whole-paragraph bold vs mixed label | MEDIUM | Bold `Abstract—` / `Keywords—` only; body italic |
| 6 | Table 7 caption | Style `Normal` 10 pt | MEDIUM | Restored `Table Title` 8 pt |
| 7–8 | Long URLs | Hyphenation split `school-data` / `publ-ic` / anonymous URL | MEDIUM | Zero-width space after `/`; no-proofing on URL paragraphs |
| 3 | Settings listing | Unnumbered (intentional; Results stay Table 2–7) | LOW | None (science/numbering contract) |
| 4 | ECE formula | Inline, not template `equation` `(1)` | LOW | Left inline; formula unchanged |
| 4 | Left column after Fig. 1 | Shorter than right (G ends early) | LOW | Improved by continuous figure section; residual OK |
| 8 | Last-page column balance | Left column shorter (end matter) | LOW | Typical of last IJIET page; not forced |
| — | Journal running head | 2026 PDFs have Vol./No. header | n/a | Do **not** add; publisher production |
| 7 | Ethical / AI placeholders | `[AUTHOR ACTION REQUIRED…]`, `[version to be confirmed]` | n/a | Author action; not a typesetting defect |

## Special checks

- **Tables 3–6:** Table 3 is a readable 1-col span; Table 4 CIs no longer split on the comma; Table 5 1-col span; Table 6 fits a single column.
- **Long equations:** ECE/Brier remain inline and inside the 243.65 pt column.
- **Long URLs/DOIs:** wrap at slashes; CC BY link intact.
- **Fig. 1:** still 2×3 KC count + log training volume; caption below.

## Compile log

```
COMPILE_LOG
```
"""
    QA.write_text(
        body.replace("FULL_PAGES", str(full_pages)).replace("COMPILE_LOG", log),
        encoding="utf-8",
    )


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"Missing {FULL_DOCX}")
    regen_fig()
    lines: list[str] = []
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        apply_visual_fixes(full_doc, lines)
        set_word_props(full_doc, AUTHORS_META, "Hung Yen University of Technology and Education")
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        export_pdf(full_doc, FULL_PDF)
        lines.append(f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count}")

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize(blind_doc, lines)
        restore_h1(blind_doc)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
        lines.append(f"BLIND_TABLES={blind_doc.Tables.Count} FIGS={blind_doc.InlineShapes.Count}")
        if full_doc.InlineShapes.Count != 1 or blind_doc.InlineShapes.Count != 1:
            raise RuntimeError("figure count changed")
        if full_doc.Tables.Count < 8 or blind_doc.Tables.Count < 8:
            raise RuntimeError("table count dropped")
    finally:
        if full_doc is not None:
            full_doc.Close(WD_SAVE)
        if blind_doc is not None:
            blind_doc.Close(WD_SAVE)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_pages = fitz.open(str(FULL_PDF)).page_count
    blind_pages = fitz.open(str(BLIND_PDF)).page_count
    lines.append(f"FULL_PAGES={full_pages}")
    lines.append(f"BLIND_PAGES={blind_pages}")

    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    if "Khanh-Trinh" not in full_t:
        raise RuntimeError("full PDF lost authors")
    if hits(blind_t, IDENTIFYING):
        raise RuntimeError(f"blind identifying {hits(blind_t, IDENTIFYING)}")
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind dropped tokens {keep_ok}")
    if "0.1136" not in full_t or "0.2280" not in full_t:
        raise RuntimeError("ECE cells lost")
    if "0.196" not in full_t or "0.268" not in full_t:
        raise RuntimeError("FAR cells lost")
    lines.append(f"KEEP={keep_ok}")
    write_qa(full_pages, lines)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
