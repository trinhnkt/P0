#!/usr/bin/env python3
"""A24: restore IJIET template title/affiliation/abstract typography.

Does not change scientific table cells. Named + blind re-export.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOCX,
    FULL_PDF,
    anonymize_blind,
    export_pdf,
    lock_checks,
    para_text,
    pdf_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a24"
LOG = HERE / "audit" / "apply_a24_format_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A24.md"
AUDIT = HERE / "audit" / "FORMAT_A24_AUDIT.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_ALIGN_CENTER = 1
WD_LINE_SINGLE = 0


def style_title(doc, log: list[str]) -> None:
    p = doc.Paragraphs(1)
    raw = para_text(p).strip()
    if raw != PAPER_TITLE:
        raise SystemExit(f"unexpected title: {raw!r}")
    p.Style = "Text"
    p.Alignment = WD_ALIGN_CENTER
    pf = p.Format
    pf.FirstLineIndent = 0
    pf.SpaceBefore = 0
    pf.SpaceAfter = 20
    pf.LineSpacingRule = WD_LINE_SINGLE
    rng = doc.Range(p.Range.Start, p.Range.End - 1)
    rng.Font.Name = "Times New Roman"
    rng.Font.Size = 20
    rng.Font.Bold = False
    rng.Font.Italic = False
    rng.Font.AllCaps = False
    rng.Font.SmallCaps = False
    log.append(
        f"TITLE sz={p.Range.Font.Size} al={p.Alignment} sa={pf.SpaceAfter} "
        f"ind={pf.FirstLineIndent}"
    )


def style_affiliation(doc, log: list[str]) -> None:
    n = 0
    for i in range(1, 12):
        p = doc.Paragraphs(i)
        if p.Style.NameLocal != "Affiliation":
            continue
        rng = doc.Range(p.Range.Start, p.Range.End - 1)
        rng.Font.Name = "Times New Roman"
        rng.Font.Size = 9
        rng.Font.Bold = False
        rng.Font.Italic = False
        rng.Font.Superscript = False
        rng.Font.Subscript = False
        p.Alignment = WD_ALIGN_CENTER
        raw = para_text(p)
        if raw[:1] in "12":
            doc.Range(p.Range.Start, p.Range.Start + 1).Font.Superscript = True
        n += 1
        log.append(f"AFFIL i={i} {raw[:50]!r}")
    if n < 4:
        raise SystemExit(f"affiliation paragraphs {n}")


def style_labeled_block(doc, index: int, label: str, log: list[str], tag: str) -> None:
    p = doc.Paragraphs(index)
    raw = para_text(p)
    if not raw.startswith(label):
        raise SystemExit(f"{tag} missing {label!r}: {raw[:40]!r}")
    rng = doc.Range(p.Range.Start, p.Range.End - 1)
    rng.Font.Name = "Times New Roman"
    rng.Font.Size = 9
    rng.Font.Bold = False
    rng.Font.Italic = True
    lab = doc.Range(p.Range.Start, p.Range.Start + len(label))
    lab.Font.Bold = True
    lab.Font.Italic = True
    lab.Font.Size = 9
    lab.Font.Name = "Times New Roman"
    log.append(f"{tag} i={index} label={label!r}")


def force_body_tnr(doc, log: list[str]) -> None:
    n = 0
    arrow_n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        try:
            if p.Range.Tables.Count:
                continue
        except Exception:
            pass
        st = p.Style.NameLocal
        if st == "Text":
            name = p.Range.Font.Name or ""
            if not name:
                rng = doc.Range(p.Range.Start, p.Range.End - 1)
                rng.Font.Name = "Times New Roman"
                n += 1
        raw = para_text(p)
        if "\u2192" in raw:
            start = p.Range.Start
            text = doc.Range(start, p.Range.End - 1).Text
            pos = 0
            while True:
                j = text.find("\u2192", pos)
                if j < 0:
                    break
                ch = doc.Range(start + j, start + j + 1)
                ch.Font.Name = "Times New Roman"
                ch.Font.Size = 10
                arrow_n += 1
                pos = j + 1
    log.append(f"BODY_TNR_EMPTYFONT={n} ARROWS={arrow_n}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A24 — IJIET template typography

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged.

Title restore (CHANGELOG_TITLE) had replaced paragraph 1 text and dropped
direct formatting: the IJIET template keeps style `Text` with **20 pt**,
centered, no first-line indent. The living file had 10 pt justified body
formatting on the title.

| # | Item | Action |
|---|---|---|
| 1 | Title | 20 pt TNR, not bold, centered, SpaceAfter 20 pt |
| 2 | Affiliation lines | Forced 9 pt TNR (PDF had been 6 pt on university lines) |
| 3 | Abstract— / Keywords— | Label bold+italic; remainder italic 9 pt, not bold |
| 4 | Body TNR | Empty-name Text runs and U+2192 arrows set to Times New Roman |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a24`.
""",
        encoding="utf-8",
    )


def write_audit(pages: int, blind_pages: int, title_ok: bool) -> None:
    AUDIT.write_text(
        f"""# FORMAT_A24_AUDIT — IJIET_template.doc vs living manuscript

**Date:** 2026-09-01  
**Authority:** https://www.ijiet.org/files/IJIET_template.doc  
**Files:** `manuscript/main_ijiet_full.docx`, `output/main_ijiet_full.pdf` / `main_ijiet_blind.pdf`  
**Pages:** named {pages}, blind {blind_pages}

## After A24

Title 20 pt centered: {title_ok}

## Intentional deviations (do not change unless editor asks)

- Heading 1 ALL CAPS with typed `I.` (matches 2026 published IJIET PDFs; template is sentence case).
- `IV. RESULTS` + `V. DISCUSSION` (template: one `IV. Result and Discussion`).
- Affiliation omits Department/Faculty.
- Extra unnumbered heads: Ethical Statement, Data and Code Availability, Generative AI Statement (IJIET ethics page).
- Table body 7 pt except Table 2 at 8 pt (fit two-column tables).
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not BACKUP.exists():
        shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A24"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        style_title(full_doc, log)
        style_affiliation(full_doc, log)
        style_labeled_block(full_doc, 10, "Abstract—", log, "ABSTRACT")
        style_labeled_block(full_doc, 11, "Keywords—", log, "KEYWORDS")
        force_body_tnr(full_doc, log)
        set_word_props(full_doc, AUTHORS_META, "")
        try:
            full_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        export_pdf(full_doc, FULL_PDF, include_props=True)
        full_doc.Close(WD_SAVE)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, log)
        patch_blind_data(blind_doc, log)
        set_word_props(blind_doc, "", "")
        try:
            blind_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        try:
            blind_doc.RemoveDocumentInformation(1)
        except Exception:
            pass
        if "Khanh-Trinh" in (blind_doc.Content.Text or ""):
            raise RuntimeError("blind Word still contains Khanh-Trinh")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF, include_props=False)
        if blind_doc.Tables.Count != n_tables or blind_doc.InlineShapes.Count != n_figs:
            raise RuntimeError("blind structure changed")
        blind_doc.Close(WD_SAVE)
        blind_doc = None
    finally:
        if full_doc is not None:
            full_doc.Close(0)
        if blind_doc is not None:
            blind_doc.Close(0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")

    import fitz

    d = fitz.open(str(FULL_PDF))
    title_sz = None
    affil_sz = []
    for b in d[0].get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s.get("text", "").strip()
                if t.startswith("Reproducible Sparse") and title_sz is None:
                    title_sz = round(s["size"], 1)
                if t.startswith("1 Hung Yen") or t.startswith("2 Academy"):
                    affil_sz.append(round(s["size"], 1))
    d.close()
    log.append(f"PDF_TITLE_SZ={title_sz} PDF_AFFIL_SZ={affil_sz}")
    title_ok = title_sz == 20.0
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"pdf_title_sz={title_sz}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages)
    write_audit(full_pages, blind_pages, title_ok)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if not title_ok:
        raise SystemExit(f"title still {title_sz} pt")
    if affil_sz and any(s < 8.5 for s in affil_sz):
        raise SystemExit(f"affiliation still small {affil_sz}")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")


if __name__ == "__main__":
    main()
