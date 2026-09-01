#!/usr/bin/env python3
"""IJIET-18: close empty space before tables (Word 2-col / 1-col breaks)."""
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
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step18_verify.txt"

sys.path.insert(0, str(SRC))
from prepare_step15 import (  # noqa: E402
    AUTHORS_META,
    IDENTIFYING,
    KEEP_IN_BLIND,
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
from prepare_step16 import restore_h1  # noqa: E402
from prepare_step17 import anonymize_blind  # noqa: E402

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_REPLACE_ALL = 2
WD_FIND_CONTINUE = 1
WD_COLLAPSE_START = 1
WD_COLLAPSE_END = 0
WD_BREAK_SECTION_CONTINUOUS = 3
WD_SECTION_CONTINUOUS = 0
WD_COL_WIDTH = 243.65
WD_FULL_WIDTH = 501.75
WD_GUTTER = 14.4
WD_PREF_POINTS = 2
WD_AUTOFIT_WINDOW = 2
GATE_WIDTHS = [62.0, 48.0, 52.0, 58.0, 58.0, 90.0, 48.0, 52.0, 44.6]


def find_replace(doc, find_text: str, repl: str) -> None:
    f = doc.Content.Find
    f.ClearFormatting()
    f.Replacement.ClearFormatting()
    f.Execute(
        FindText=find_text,
        MatchCase=False,
        MatchWholeWord=False,
        MatchWildcards=False,
        MatchSoundsLike=False,
        MatchAllWordForms=False,
        Forward=True,
        Wrap=WD_FIND_CONTINUE,
        Format=False,
        ReplaceWith=repl,
        Replace=WD_REPLACE_ALL,
    )


def find_para(doc, stub: str) -> int | None:
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            return i
    return None


def two_col(sec) -> None:
    sec.PageSetup.TextColumns.SetCount(2)
    try:
        sec.PageSetup.TextColumns.EvenlySpaced = True
        sec.PageSetup.TextColumns.Spacing = WD_GUTTER
        sec.PageSetup.VerticalAlignment = 0
        sec.PageSetup.SectionStart = WD_SECTION_CONTINUOUS
    except Exception:
        pass


def one_col(sec) -> None:
    sec.PageSetup.TextColumns.SetCount(1)
    try:
        sec.PageSetup.VerticalAlignment = 0
        sec.PageSetup.SectionStart = WD_SECTION_CONTINUOUS
    except Exception:
        pass


def caption_of(tbl) -> str:
    cap_rng = tbl.Range.Duplicate
    cap_rng.Collapse(WD_COLLAPSE_START)
    cap_rng.Move(WD_CHARACTER, -2)
    return para_text(cap_rng.Paragraphs(1))


def fit_table(tbl, width: float) -> None:
    tbl.AllowAutoFit = True
    try:
        tbl.PreferredWidthType = WD_PREF_POINTS
        tbl.PreferredWidth = width
    except Exception:
        pass
    try:
        tbl.AutoFitBehavior(WD_AUTOFIT_WINDOW)
    except Exception:
        pass
    n = tbl.Columns.Count
    if n == 9 and abs(width - WD_FULL_WIDTH) < 1:
        scale = width / sum(GATE_WIDTHS)
        widths = [w * scale for w in GATE_WIDTHS]
    else:
        widths = [width / n] * n
    for c, w in enumerate(widths, start=1):
        try:
            tbl.Columns(c).Width = w
        except Exception:
            pass
    try:
        tbl.Rows.AllowBreakAcrossPages = False
        tbl.AllowBreakAcrossPages = False
        tbl.Rows(1).HeadingFormat = False
        tbl.Range.ParagraphFormat.KeepTogether = True
        for ri in range(1, tbl.Rows.Count):
            tbl.Rows(ri).Range.ParagraphFormat.KeepWithNext = True
            tbl.Rows(ri).AllowBreakAcrossPages = False
    except Exception:
        pass
    for ri in range(1, tbl.Rows.Count + 1):
        for ci in range(1, n + 1):
            cell = tbl.Cell(ri, ci)
            cell.Range.Font.Name = "Times New Roman"
            cell.Range.Font.Size = 7
            try:
                cell.TopPadding = 0.5
                cell.BottomPadding = 0.5
                cell.LeftPadding = 1.0
                cell.RightPadding = 1.0
            except Exception:
                pass


def is_section_boundary(doc, para) -> bool:
    for s in range(1, doc.Sections.Count + 1):
        if abs(para.Range.End - doc.Sections(s).Range.End) <= 2:
            return True
    return False


def delete_junk_paras(doc, lines: list[str]) -> None:
    find_replace(doc, "^n", "")
    find_replace(doc, "^m", "")
    n = 0
    nsec = doc.Sections.Count
    i = doc.Paragraphs.Count
    while i >= 1:
        p = doc.Paragraphs(i)
        if p.Range.InlineShapes.Count or p.Range.Tables.Count:
            i -= 1
            continue
        if is_section_boundary(doc, p):
            i -= 1
            continue
        raw = para_text(p)
        if raw.startswith("Table ") or raw.startswith("Fig. ") or raw.startswith("Abstract"):
            i -= 1
            continue
        stripped = raw.replace("\x0c", "").replace("\x01", "").strip()
        if stripped != "":
            i -= 1
            continue
        try:
            p.Range.Delete()
            n += 1
        except Exception as exc:
            lines.append(f"JUNK_FAIL i={i} {exc}")
        i -= 1
    lines.append(f"DEL_JUNK={n} sections={doc.Sections.Count} (was {nsec})")


def restore_title_onecol(doc, lines: list[str]) -> None:
    """Title/authors stay one-column; Abstract begins the two-column body."""
    i = find_para(doc, "Abstract")
    if i is None:
        i = find_para(doc, "Abstract—")
    if i is None:
        lines.append("ABSTRACT_PARA_MISSING")
        one_col(doc.Sections(1))
        return
    abs_start = doc.Paragraphs(i).Range.Start
    sec1 = doc.Sections(1)
    if sec1.Range.Start <= abs_start <= sec1.Range.End and doc.Sections.Count >= 1:
        if sec1.PageSetup.TextColumns.Count != 1 or abs_start < sec1.Range.End - 5:
            if abs_start > sec1.Range.Start + 20 and abs_start <= sec1.Range.End:
                insert_continuous_break_at(doc, abs_start)
    one_col(doc.Sections(1))
    if doc.Sections.Count >= 2:
        two_col(doc.Sections(2))
    lines.append(
        f"TITLE_SEC1_COLS={doc.Sections(1).PageSetup.TextColumns.Count} "
        f"sections={doc.Sections.Count}"
    )


def assert_captions(doc, lines: list[str] | None = None) -> None:
    found = []
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Table ") or raw.upper().startswith("TABLE ") or raw.startswith("Fig. "):
            found.append(raw[:80])
            if lines is not None:
                lines.append(f"CAP i={i} {raw[:80]!r}")
    blob = "\n".join(found)
    for n in range(1, 9):
        if f"Table {n}." not in blob and f"TABLE {n}." not in blob.upper():
            if lines is not None:
                lines.append(f"MISSING_CAP Table {n}. seen={found!r}")
            raise RuntimeError(f"lost caption Table {n}. seen={found}")
    if "Fig. 1." not in blob:
        raise RuntimeError(f"lost Fig. 1. caption seen={found}")


def restore_heading_d(doc, lines: list[str]) -> None:
    if find_para(doc, "D. Train-only") is not None:
        lines.append("H2_D already present")
        return
    i = find_para(doc, "For each fold, KC frequency")
    if i is None:
        lines.append("H2_D body missing")
        return
    rng = doc.Paragraphs(i).Range
    rng.Collapse(WD_COLLAPSE_START)
    rng.InsertParagraphBefore()
    p = doc.Paragraphs(i)
    try:
        p.Style = "Heading 2"
    except Exception:
        pass
    set_para_text(p, "D. Train-only frequency strata")
    lines.append(f"H2_D_INSERTED i={i}")


H2_MAP = [
    ("Knowledge Tracing and benchmark", "A. Knowledge Tracing and benchmark models"),
    ("Graph and self-supervised", "B. Graph and self-supervised KT"),
    ("Sparse-data and cold-start", "C. Sparse-data and cold-start problems"),
    ("Calibration and educational", "D. Calibration and educational decision support"),
    ("Why datasets differ", "C. Why datasets differ"),
    ("Datasets", "A. Datasets"),
    ("Splits and seeds", "B. Splits and seeds"),
    ("Model settings", "C. Model settings"),
    ("Train-only frequency", "D. Train-only frequency strata"),
    ("Reliability flags", "E. Reliability flags"),
    ("Calibration across frequency", "B. Calibration across frequency strata"),
    ("Difficulty coupling", "G. Difficulty coupling"),
    ("Simulated decision gate", "H. Simulated decision gate"),
    ("Aggregate discrimination", "A. Aggregate discrimination"),
    ("Threshold-based decision", "C. Threshold-based decision error"),
    ("Dataset-dependent", "D. Dataset-dependent explanatory analysis"),
    ("Exploratory GKT", "E. Exploratory GKT/CL4KT result"),
    ("Main empirical", "A. Main empirical findings"),
    ("Practical implications", "B. Practical implications for educational technology"),
    ("Why datasets differ", "C. Why datasets differ"),
    ("Limitations", "D. Limitations"),
    ("Calibration", "F. Calibration"),
]


def restore_h2(doc, lines: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        try:
            style = str(doc.Paragraphs(i).Style.NameLocal)
        except Exception:
            continue
        if style != "Heading 2":
            continue
        raw = para_text(doc.Paragraphs(i))
        target = None
        for key, val in H2_MAP:
            if key.lower() in raw.lower():
                target = val
                break
        if target is None:
            continue
        try:
            doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
        except Exception:
            pass
        if raw != target:
            set_para_text(doc.Paragraphs(i), target)
            n += 1
    lines.append(f"H2_RESTORED={n}")


def flatten_body_to_twocol(doc, lines: list[str]) -> None:
    restore_title_onecol(doc, lines)
    for s in range(2, doc.Sections.Count + 1):
        two_col(doc.Sections(s))
    lines.append(f"BODY_2COL sections={doc.Sections.Count}")


def apply_one_col_range(doc, start_pos: int, end_pos: int, lines: list[str], tag: str) -> None:
    n_one = 0
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        if sec.Range.End <= start_pos:
            continue
        if sec.Range.Start >= end_pos:
            two_col(sec)
            break
        one_col(sec)
        n_one += 1
    lines.append(f"{tag} 1col_sections={n_one}")


def insert_continuous_break_at(doc, pos: int) -> None:
    """Insert a continuous section break without landing inside a table row."""
    rng = doc.Range(pos, pos)
    try:
        rng.InsertBreak(WD_BREAK_SECTION_CONTINUOUS)
        return
    except Exception:
        pass
    rng = doc.Range(pos, pos)
    rng.InsertParagraphBefore()
    rng = doc.Range(pos, pos)
    rng.InsertBreak(WD_BREAK_SECTION_CONTINUOUS)


def log_caps(doc, lines: list[str], tag: str) -> None:
    lines.append(f"--- {tag} tables={doc.Tables.Count} ---")
    for ti in range(1, doc.Tables.Count + 1):
        lines.append(f"  T{ti} prev={caption_of(doc.Tables(ti))[:75]!r}")


def wrap_start_through_caption(
    doc, start_stub: str, cap_stub: str, lines: list[str], tag: str
) -> None:
    si = find_para(doc, start_stub)
    if si is None:
        raise RuntimeError(f"{tag}: missing start {start_stub!r}")
    if find_para(doc, cap_stub) is None:
        raise RuntimeError(f"{tag}: missing caption {cap_stub!r}")
    insert_continuous_break_at(doc, doc.Paragraphs(si).Range.Start)
    ci = find_para(doc, cap_stub)
    if ci is None:
        raise RuntimeError(f"{tag}: caption vanished after start break {cap_stub!r}")
    cap = doc.Paragraphs(ci)
    start_pos = doc.Paragraphs(find_para(doc, start_stub)).Range.Start
    probe = doc.Range(cap.Range.End, cap.Range.End + 80)
    if probe.Tables.Count < 1:
        raise RuntimeError(f"{tag}: no table after {cap_stub!r}")
    table = probe.Tables(1)
    end = table.Range.Duplicate
    end.Collapse(WD_COLLAPSE_END)
    end.InsertBreak(WD_BREAK_SECTION_CONTINUOUS)
    apply_one_col_range(doc, start_pos, table.Range.End, lines, tag)
    lines.append(f"{tag} cap={para_text(cap)[:70]!r}")
    log_caps(doc, lines, tag)


def wrap_start_to_end_stub(doc, start_stub: str, end_stub: str, lines: list[str], tag: str) -> None:
    si = find_para(doc, start_stub)
    ei = find_para(doc, end_stub)
    if si is None or ei is None:
        raise RuntimeError(f"{tag}: missing {start_stub!r} / {end_stub!r}")
    insert_continuous_break_at(doc, doc.Paragraphs(si).Range.Start)
    ei = find_para(doc, end_stub)
    start_pos = doc.Paragraphs(find_para(doc, start_stub)).Range.Start
    end = doc.Paragraphs(ei).Range.Duplicate
    end_pos = end.End
    end.Collapse(WD_COLLAPSE_END)
    end.InsertBreak(WD_BREAK_SECTION_CONTINUOUS)
    apply_one_col_range(doc, start_pos, end_pos, lines, tag)
    log_caps(doc, lines, tag)


def delete_leading_empties(doc, lines: list[str]) -> None:
    n = 0
    for s in range(2, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        if sec.Range.Paragraphs.Count < 1:
            continue
        p = sec.Range.Paragraphs(1)
        if p.Range.InlineShapes.Count or p.Range.Tables.Count:
            continue
        raw = para_text(p).replace("\x0c", "").strip()
        if raw != "":
            continue
        rng = p.Range
        if rng.End >= sec.Range.End:
            rng.MoveEnd(WD_CHARACTER, -1)
        try:
            if rng.Start < rng.End:
                rng.Delete()
                n += 1
        except Exception as exc:
            lines.append(f"DEL_EMPTY_FAIL sec={s} {exc}")
    n_cap = 0
    i = doc.Paragraphs.Count
    while i >= 2:
        raw = para_text(doc.Paragraphs(i))
        if not raw.startswith("Table ") or ". " not in raw[:10]:
            i -= 1
            continue
        if " reports" in raw or " is a " in raw or " checks" in raw or " records" in raw:
            i -= 1
            continue
        prev = doc.Paragraphs(i - 1)
        if prev.Range.InlineShapes.Count or prev.Range.Tables.Count:
            i -= 1
            continue
        if is_section_boundary(doc, prev):
            i -= 1
            continue
        pret = para_text(prev).replace("\x0c", "").strip()
        if pret != "":
            i -= 1
            continue
        try:
            prev.Range.Delete()
            n_cap += 1
        except Exception:
            pass
        i -= 1
    lines.append(f"DEL_LEADING_EMPTY={n} DEL_BEFORE_CAP={n_cap}")


def tighten_captions(doc, lines: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if not (raw.startswith("Table ") or raw.startswith("Fig. ")):
            continue
        if " reports" in raw or " is a " in raw or raw.startswith("Table 6 checks"):
            continue
        if raw.startswith("Table 7 records"):
            continue
        pf = doc.Paragraphs(i).Range.ParagraphFormat
        pf.SpaceBefore = 3
        pf.SpaceAfter = 3
        pf.PageBreakBefore = raw.startswith("Table 4.")
        pf.KeepTogether = False
        pf.KeepWithNext = bool(raw.startswith("Table "))
        n += 1
    lines.append(f"CAPTION_TIGHTEN={n}")


def force_span_sections(doc, lines: list[str]) -> None:
    spans = [
        ("Table 2. Recovered", "Fig. 1."),
        ("B. Calibration across frequency strata", "Table 4."),
        ("C. Threshold-based decision error", "Table 6."),
        ("D. Dataset-dependent explanatory analysis", "Table 8."),
    ]
    n = 0
    for start_stub, end_stub in spans:
        si = find_para(doc, start_stub)
        ei = find_para(doc, end_stub)
        if si is None or ei is None:
            continue
        start = doc.Paragraphs(si).Range.Start
        end = doc.Paragraphs(ei).Range.End
        if end_stub.startswith("Table "):
            probe = doc.Range(doc.Paragraphs(ei).Range.End, doc.Paragraphs(ei).Range.End + 80)
            if probe.Tables.Count:
                end = probe.Tables(1).Range.End
        for s in range(1, doc.Sections.Count + 1):
            sec = doc.Sections(s)
            if sec.Range.End > start and sec.Range.Start < end:
                if sec.PageSetup.TextColumns.Count != 1:
                    one_col(sec)
                    n += 1
    lines.append(f"FORCE_SPAN_1COL={n}")


def size_tables(doc, lines: list[str]) -> None:
    for ti in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(ti)
        s = None
        for k in range(1, doc.Sections.Count + 1):
            sec = doc.Sections(k)
            if sec.Range.Start <= tbl.Range.Start <= sec.Range.End:
                s = sec
                break
        width = WD_FULL_WIDTH
        if s is not None and s.PageSetup.TextColumns.Count == 2:
            width = WD_COL_WIDTH
        fit_table(tbl, width)
        w = sum(tbl.Columns(c).Width for c in range(1, tbl.Columns.Count + 1))
        lines.append(
            f"T{ti} cols={tbl.Columns.Count} w={w:.1f} "
            f"sec_cols={s.PageSetup.TextColumns.Count if s else '?'}"
        )


def pdf_layout_flags(pdf: Path) -> list[str]:
    d = fitz.open(str(pdf))
    flags = [f"FULL_PAGES={d.page_count}"]
    for i, page in enumerate(d):
        blocks = []
        for b in page.get_text("blocks"):
            x0, y0, x1, y1, text, *_ = b[:6]
            t = str(text).replace("\n", " ").strip()
            if not t:
                continue
            col = "L" if x0 < 300 else "R"
            blocks.append((col, y0, y1, t[:70]))
        for col in ("L", "R"):
            col_b = [(y0, y1, t) for c, y0, y1, t in blocks if c == col]
            col_b.sort()
            prev_y1 = 36.0
            for y0, y1, t in col_b:
                gap = y0 - prev_y1
                if gap > 90 and not t.startswith("Fig."):
                    flags.append(
                        f"GAP p{i+1}{col} y={y0:.0f} gap={gap:.0f} | {t[:60]}"
                    )
                prev_y1 = y1
        joined = " ".join(t for *_, t in blocks)
        for needle in ("TABLE 4.", "TABLE 5.", "TABLE 6.", "TABLE 7.", "TABLE 8.", "TABLE 2."):
            if needle in joined.upper() or needle.title() in joined:
                pass
    d.close()
    return flags


def main() -> None:
    if not FULL_DOC.exists():
        raise SystemExit(f"Missing {FULL_DOC}")
    lines: list[str] = []
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    saved = False
    try:
        snap = SRC / "snapshots" / "main_ijiet_pre18_snake.doc"
        snap.parent.mkdir(parents=True, exist_ok=True)
        if not snap.exists():
            shutil.copy2(FULL_DOC, snap)
        src_doc = word.Documents.Open(str(snap))
        src_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        src_doc.Close(0)
        lines.append("RESTORED_FROM_SNAP")
        full_doc = word.Documents.Open(str(FULL_DOCX))
        assert_captions(full_doc, lines)
        delete_junk_paras(full_doc, lines)
        restore_heading_d(full_doc, lines)
        flatten_body_to_twocol(full_doc, lines)
        assert_captions(full_doc, lines)
        log_caps(full_doc, lines, "AFTER_FLATTEN")
        # Top-to-bottom: each wrap's following section is still 2-col body.
        wrap_start_to_end_stub(
            full_doc,
            "Table 2. Recovered",
            "Fig. 1.",
            lines,
            "T2FIG",
        )
        wrap_start_through_caption(
            full_doc,
            "B. Calibration across frequency strata",
            "Table 4.",
            lines,
            "T4",
        )
        wrap_start_through_caption(
            full_doc,
            "C. Threshold-based decision error",
            "Table 6.",
            lines,
            "T5T6",
        )
        wrap_start_through_caption(
            full_doc,
            "D. Dataset-dependent explanatory analysis",
            "Table 8.",
            lines,
            "T7T8",
        )
        assert_captions(full_doc, lines)
        force_span_sections(full_doc, lines)
        delete_leading_empties(full_doc, lines)
        size_tables(full_doc, lines)
        tighten_captions(full_doc, lines)
        restore_h1(full_doc)
        restore_h2(full_doc, lines)
        neutralize_table_lists(full_doc)
        set_word_props(
            full_doc,
            AUTHORS_META,
            "Hung Yen University of Technology and Education",
        )
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        export_pdf(full_doc, FULL_PDF)
        lines.append(
            f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count} "
            f"SECTIONS={full_doc.Sections.Count}"
        )

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        restore_h1(blind_doc)
        restore_h2(blind_doc, lines)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
        if full_doc.InlineShapes.Count != 1 or full_doc.Tables.Count < 8:
            raise RuntimeError("structure lost")
        saved = True
    except Exception as exc:
        REPORT.write_text("\n".join(lines) + "\nERROR: " + str(exc) + "\n", encoding="utf-8")
        raise
    finally:
        if full_doc is not None:
            full_doc.Close(WD_SAVE if saved else 0)
        if blind_doc is not None:
            blind_doc.Close(WD_SAVE if saved else 0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    lines.extend(pdf_layout_flags(FULL_PDF))
    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    checks = {
        "t8": "TABLE 8." in full_t.upper() or "Table 8." in full_t,
        "h2d": "D. Train-only frequency strata" in full_t
        and "A. D. Train-only" not in full_t,
        "ece": "0.1136" in full_t and "0.2280" in full_t,
        "far": "0.196" in full_t and "0.268" in full_t,
        "blind": not hits(blind_t, IDENTIFYING),
        "authors": "Khanh-Trinh" in full_t,
        "fig": "Fig. 1." in full_t,
    }
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    lines.append(f"CHECKS={checks}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise RuntimeError(f"verify failed: {failed}")
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind dropped {keep_ok}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
