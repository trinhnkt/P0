#!/usr/bin/env python3
"""IJIET-15: named full PDF and double-blind review PDF."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP14 = SRC / "main_ijiet_step14.docx"
FULL_DOCX = SRC / "main_ijiet_full.docx"
FULL_DOC = SRC / "main_ijiet_full.doc"
BLIND_DOCX = SRC / "main_ijiet_blind.docx"
BLIND_DOC = SRC / "main_ijiet_blind.doc"
OUT_DIR = ROOT / "IJIET_SUBMISSION" / "output"
FULL_PDF = OUT_DIR / "main_ijiet_full.pdf"
BLIND_PDF = OUT_DIR / "main_ijiet_blind.pdf"
CHECK = ROOT / "IJIET_SUBMISSION" / "audit" / "DOUBLE_BLIND_CHECK.md"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step15_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

TITLE = (
    "Sparse-Concept Calibration of Knowledge Tracing Models "
    "for Threshold-Based Educational Decisions"
)
AUTHORS_META = (
    "Khanh-Trinh Nguyen, Tuan Dao Minh, Duong Nguyen Tien, "
    "Chi Thanh Nguyen, Van-Hau Nguyen"
)
ANON_AUTHORS = "Anonymous Authors"
ANON_AFFIL = "Affiliations omitted for double-blind review."
ANON_CONTRIB = (
    "Author 1: Conceptualization, Methodology, Software, Formal analysis, and "
    "Writing (led diagnostic design, experiments, and manuscript). Authors 2 and 3: "
    "Software (data processing and baseline runs). Author 4: Methodology "
    "(methodological review). Author 5: Supervision and Writing (manuscript "
    "revision). All authors approved the final version."
)
ANON_ACK = "Omitted for double-blind review."
ANON_URL = "https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/"

IDENTIFYING = [
    "Khanh-Trinh",
    "Tuan Dao Minh",
    "Duong Nguyen Tien",
    "Chi Thanh Nguyen",
    "Van-Hau",
    "Hung Yen",
    "utehy.edu.vn",
    "trinhnk",
    "tuanymc",
    "duongnt@",
    "thanhnc",
    "haunv@",
    "ioit.ai.vn",
    "Military Science",
    "ORCID",
    "0009-0004",
    "0009-0009",
    "0009-0007",
    "0000-0003-4335",
    "0000-0002-3256",
    "github.com/trinhnkt",
    "K.-T.N.",
    "T.D.M.",
    "D.N.T.",
    "C.T.N.",
    "V.-H.N.",
]

KEEP_IN_BLIND = [
    "ASSISTments",
    "Junyi Academy",
    "XES3G5M",
    ANON_URL,
    "Corbett",
]


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def neutralize_table_lists(doc) -> None:
    for ti in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(ti)
        for ri in range(1, tbl.Rows.Count + 1):
            for ci in range(1, tbl.Columns.Count + 1):
                cell = tbl.Cell(ri, ci)
                try:
                    cell.Range.ListFormat.RemoveNumbers()
                except Exception:
                    pass
                try:
                    cell.Range.Style = "Normal"
                except Exception:
                    pass
                try:
                    cell.Range.ParagraphFormat.OutlineLevel = 10
                except Exception:
                    pass
                cell.Range.Font.Name = "Times New Roman"
                cell.Range.Font.Size = 7


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
        if "RESULT AND DISCUSSION" in up or (up.startswith("IV.") and "RESULT" in up):
            target = "IV. RESULT"
        elif "DISCUSSION" in up and "RESULT" not in up:
            target = "V. DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "VI. CONCLUSION"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)


def set_word_props(doc, author: str, company: str) -> None:
    def _set(name: str, value: str) -> None:
        try:
            doc.BuiltInDocumentProperties(name).Value = value
        except Exception:
            pass

    _set("Title", TITLE)
    _set("Author", author)
    _set("Last Author", author)
    _set("Company", company)
    _set("Manager", "")
    _set("Comments", "")
    _set("Subject", "")


def export_pdf(doc, path: Path) -> None:
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.ExportAsFixedFormat(
        str(path),
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


def stamp_pdf_metadata(path: Path, author: str) -> dict:
    d = fitz.open(str(path))
    meta = {
        "title": TITLE,
        "author": author,
        "subject": "",
        "keywords": "",
        "creator": "",
        "producer": "",
        "creationDate": "",
        "modDate": "",
    }
    d.set_metadata(meta)
    tmp = path.with_suffix(".tmp.pdf")
    d.save(str(tmp), garbage=4, deflate=True)
    d.close()
    tmp.replace(path)
    d2 = fitz.open(str(path))
    out = dict(d2.metadata or {})
    d2.close()
    return out


def pdf_text(path: Path) -> str:
    d = fitz.open(str(path))
    t = "\n".join(p.get_text() for p in d)
    d.close()
    return t


def compact(text: str) -> str:
    """PDF extraction can break URLs across lines; compare without whitespace."""
    return "".join(text.split())


def hits(text: str, needles: list[str]) -> list[str]:
    found = []
    low = text.lower()
    compact_low = compact(text).lower()
    for n in needles:
        needle = n.lower()
        if needle in low or needle in compact_low:
            found.append(n)
    return found


def token_present(text: str, token: str) -> bool:
    if token.startswith("http"):
        return token in compact(text)
    return token in text


def anonymize(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Khanh-Trinh Nguyen") or "Van-Hau Nguyen" in raw:
            set_para_text(doc.Paragraphs(i), ANON_AUTHORS)
            try:
                doc.Paragraphs(i).Style = "Style Author + (Asian) MS Mincho"
            except Exception:
                pass
            lines.append(f"ANON_AUTHORS i={i}")
        elif "Hung Yen University" in raw:
            set_para_text(doc.Paragraphs(i), ANON_AFFIL)
            lines.append(f"ANON_AFFIL1 i={i}")
        elif "Academy of Military Science" in raw:
            set_para_text(doc.Paragraphs(i), "")
            lines.append(f"ANON_AFFIL2 i={i}")
        elif raw.startswith("Email:"):
            set_para_text(doc.Paragraphs(i), "")
            lines.append(f"ANON_EMAIL i={i}")
        elif "Corresponding author" in raw:
            set_para_text(doc.Paragraphs(i), "")
            lines.append(f"ANON_CORR i={i}")
        elif raw.startswith("K.-T.N.:"):
            set_para_text(doc.Paragraphs(i), ANON_CONTRIB)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"ANON_CONTRIB i={i}")
        elif "authors’ respective institutions" in raw or (
            "authors' respective institutions" in raw
        ):
            set_para_text(doc.Paragraphs(i), ANON_ACK)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"ANON_ACK i={i}")


def write_check(
    full_meta: dict,
    blind_meta: dict,
    full_hits: list[str],
    blind_hits: list[str],
    keep_ok: dict,
    full_pages: int,
    blind_pages: int,
    byte_hits: list[str],
) -> None:
    lines = [
        "# Double-blind check (IJIET-15)",
        "",
        "**Date:** 2026-08-31  ",
        "**Policy:** IJIET ethics page (list-77-1) uses **double-blind** peer review; FAQ Q1/Q6 say blind review. The official template is named; this task therefore ships **two** PDFs.",
        "",
        "| Build | Path | Pages |",
        "|-------|------|------:|",
        f"| Named (camera-ready / editor) | `output/main_ijiet_full.pdf` | {full_pages} |",
        f"| Double-blind review | `output/main_ijiet_blind.pdf` | {blind_pages} |",
        "",
        "## What was anonymized (blind only)",
        "",
        "- Author names, numbered affiliations, emails, `*Corresponding author`.",
        "- Author-contribution initials (`K.-T.N.` …) replaced with Author 1–5.",
        "- Acknowledgment naming “respective institutions” replaced with “Omitted for double-blind review.”",
        "- Word/PDF `Author` and related document properties cleared.",
        "- No ORCID was present in the Word source; ORCID strings were still scanned.",
        "",
        "## What was **not** anonymized",
        "",
        "- Public dataset names: ASSISTments 2012, Junyi Academy, XES3G5M.",
        "- Numbered literature `[1]`–`[20]`.",
        "- Train-only strata, seeds, occupancy flags, FAR/ECE tables.",
        "- Artifact URL (already anonymous): "
        "`https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/` "
        "(PDF line wrapping is ignored when checking this URL).",
        "",
        "## Repository",
        "",
        "The review artifact is already on anonymous.4open.science. It does not contain "
        "`github.com/trinhnkt` or other owner logins. The same URL is used in both PDFs.",
        "",
        "## PDF metadata",
        "",
        "| Field | Full | Blind |",
        "|-------|------|-------|",
        f"| Author | `{full_meta.get('author', '')}` | `{blind_meta.get('author', '') or '(blank)'}` |",
        f"| Creator | `{full_meta.get('creator', '')}` | `{blind_meta.get('creator', '') or '(blank)'}` |",
        f"| Producer | `{full_meta.get('producer', '')}` | `{blind_meta.get('producer', '') or '(blank)'}` |",
        "",
        "## Identifying-string scan",
        "",
        f"- Full PDF must contain author/affiliation strings. Hits: {', '.join(full_hits) if full_hits else '(none — FAIL)'}",
        f"- Blind PDF must contain **none** of those strings. Hits: {', '.join(blind_hits) if blind_hits else '(none)'}",
        f"- Blind PDF raw-byte scan for names/emails/GitHub: {', '.join(byte_hits) if byte_hits else '(none)'}",
        "",
        "## Kept scientific tokens in the blind PDF",
        "",
    ]
    for k, v in keep_ok.items():
        lines.append(f"- `{k}`: {'present' if v else 'MISSING'}")
    lines.extend(
        [
            "",
            "## Verdict",
            "",
        ]
    )
    ok = bool(full_hits) and not blind_hits and not byte_hits and all(keep_ok.values())
    author_blank = not (blind_meta.get("author") or "").strip()
    if ok and author_blank:
        lines.append(
            "PASS: named PDF identifies authors; blind PDF does not; metadata Author is blank."
        )
    else:
        lines.append(
            f"FAIL: ok={ok} author_blank={author_blank} blind_hits={blind_hits}"
        )
    CHECK.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not STEP14.exists():
        raise SystemExit(f"Missing {STEP14}")
    lines: list[str] = []

    shutil.copy2(STEP14, FULL_DOCX)
    shutil.copy2(STEP14, BLIND_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        if "Khanh-Trinh Nguyen" not in full_doc.Content.Text:
            raise RuntimeError("full source missing author line")
        restore_h1(full_doc)
        neutralize_table_lists(full_doc)
        set_word_props(full_doc, AUTHORS_META, "Hung Yen University of Technology and Education")
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        export_pdf(full_doc, FULL_PDF)

        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize(blind_doc, lines)
        restore_h1(blind_doc)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        try:
            blind_doc.RemoveDocumentInformation(1)  # wdRDIComments = 1
        except Exception:
            pass
        try:
            # wdRDIDocumentProperties = 8 can wipe title; skip. Clear author only.
            pass
        except Exception:
            pass
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
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

    full_meta = stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    blind_meta = stamp_pdf_metadata(BLIND_PDF, "")
    full_pages = fitz.open(str(FULL_PDF)).page_count
    blind_pages = fitz.open(str(BLIND_PDF)).page_count
    lines.append(f"FULL_PAGES={full_pages}")
    lines.append(f"BLIND_PAGES={blind_pages}")
    lines.append(f"FULL_META_AUTHOR={full_meta.get('author')!r}")
    lines.append(f"BLIND_META_AUTHOR={blind_meta.get('author')!r}")

    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    full_hits = hits(full_t, IDENTIFYING)
    blind_hits = hits(blind_t, IDENTIFYING)
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    blind_bytes = BLIND_PDF.read_bytes()
    byte_needles = [
        b"Khanh-Trinh",
        b"Hung Yen",
        b"utehy.edu",
        b"trinhnk",
        b"Van-Hau Nguyen",
        b"Tuan Dao Minh",
        b"github.com/trinhnkt",
    ]
    byte_hits = [n.decode() for n in byte_needles if n in blind_bytes]
    lines.append(f"FULL_HITS={full_hits}")
    lines.append(f"BLIND_HITS={blind_hits}")
    lines.append(f"BLIND_BYTE_HITS={byte_hits}")
    lines.append(f"KEEP={keep_ok}")

    write_check(
        full_meta,
        blind_meta,
        full_hits,
        blind_hits,
        keep_ok,
        full_pages,
        blind_pages,
        byte_hits,
    )

    if "Khanh-Trinh" not in full_t:
        raise RuntimeError("full PDF lost author names")
    if "Hung Yen" not in full_t:
        raise RuntimeError("full PDF lost affiliation")
    if "Email:" not in full_t and "trinhnk" not in full_t:
        raise RuntimeError("full PDF lost emails")
    if blind_hits:
        raise RuntimeError(f"blind PDF still identifying: {blind_hits}")
    if byte_hits:
        raise RuntimeError(f"blind PDF bytes still identifying: {byte_hits}")
    if (blind_meta.get("author") or "").strip():
        raise RuntimeError(f"blind metadata author not blank: {blind_meta.get('author')!r}")
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind PDF dropped scientific tokens: {keep_ok}")
    if "Anonymous Authors" not in blind_t:
        raise RuntimeError("blind PDF missing Anonymous Authors")

    lines.append("PASS")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
