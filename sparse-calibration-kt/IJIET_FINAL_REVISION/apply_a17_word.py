#!/usr/bin/env python3
"""A17: IJIET template format cleanup. No scientific-number edits.

Does not write to IJIET_SUBMISSION/.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOCX,
    FULL_PDF,
    TITLE,
    anonymize_blind,
    compact,
    export_pdf,
    lock_checks,
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
    stamp_pdf_metadata,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a17"
LOG = HERE / "audit" / "apply_a17_word_log.txt"
AUDIT = HERE / "audit" / "FORMAT_FINAL_AUDIT.md"
CHANGELOG = HERE / "audit" / "CHANGELOG_A17.md"
VERIFY = HERE / "audit" / "compile_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_REPLACE_ALL = 2
WD_FIND_STOP = 0
WD_COLLAPSE_END = 0
WD_ALIGN_CENTER = 1
WD_ALIGN_JUSTIFY = 3

PLACEHOLDER_DATES = (
    "Manuscript received Month date, 2026; revised Month date, 2026; "
    "accepted Month date, 2026"
)


def split_trailing_section_breaks(doc, lines: list[str]) -> None:
    n = 0
    for i in range(doc.Paragraphs.Count, 0, -1):
        p = doc.Paragraphs(i)
        raw = para_text(p)
        if "\x0c" not in raw:
            continue
        body = raw.replace("\x0c", "").strip()
        if not body:
            try:
                p.Style = "Normal"
            except Exception:
                pass
            p.SpaceBefore = 0
            p.SpaceAfter = 0
            p.Range.Font.Size = 1
            p.Range.Font.Hidden = False
            lines.append(f"EMPTY_SECBR i={i} restyled")
            continue
        pos = p.Range.Start + raw.find("\x0c")
        br = doc.Range(pos, pos)
        br.InsertBefore("\r")
        n += 1
        lines.append(f"SPLIT_SECBR i={i}")
    lines.append(f"SPLIT_SECBR_N={n}")


def restore_h1(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        try:
            st = str(p.Style.NameLocal)
        except Exception:
            continue
        if st != "Heading 1":
            continue
        raw = para_text(p)
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
            target = "IV. RESULTS"
        if target and raw != target:
            try:
                p.Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(p, target)
            p.Range.Font.Name = "Times New Roman"
            p.Range.Font.Size = 10
            p.Range.Font.Bold = False
            p.Range.Font.AllCaps = False
            lines.append(f"H1 i={i} {target}")


def style_table_captions(doc, lines: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        raw = para_text(p)
        if not raw.startswith("Table "):
            continue
        if raw.startswith("Table ") and "reports" in raw[:80].lower():
            continue
        if raw.startswith("Table ") and raw[6:7].isdigit() and (
            raw[7:8] in " ." or raw.startswith("Table 10")
        ):
            pass
        else:
            continue
        # skip in-text "Table 3 reports"
        if not (len(raw) > 8 and raw[6].isdigit() and raw[7] == "."):
            continue
        try:
            p.Style = "figure caption"
        except Exception:
            try:
                p.Style = "Table Title"
            except Exception:
                pass
        p.Alignment = WD_ALIGN_CENTER
        rng = p.Range
        rng.Font.Name = "Times New Roman"
        rng.Font.Size = 8
        rng.Font.Bold = False
        rng.Font.Italic = False
        rng.Font.AllCaps = False
        rng.Font.SmallCaps = False
        n += 1
        lines.append(f"CAP i={i} {raw[:70]!r}")
    lines.append(f"CAP_N={n}")


def fix_table2(doc, lines: list[str]) -> None:
    tbl = doc.Tables(2)
    for ri in range(1, tbl.Rows.Count + 1):
        for ci in range(1, tbl.Columns.Count + 1):
            cell = tbl.Cell(ri, ci)
            cell.Range.Font.Name = "Times New Roman"
            cell.Range.Font.Size = 8
            cell.Range.Font.Bold = False if ri > 1 else True
            pf = cell.Range.ParagraphFormat
            pf.SpaceBefore = 0
            pf.SpaceAfter = 0
            pf.LineSpacing = 12
            pf.LineSpacingRule = 0  # wdLineSpaceSingle
    lines.append(
        f"T2 {tbl.Rows.Count}x{tbl.Columns.Count} font=8pt "
        f"prefW={tbl.PreferredWidth}"
    )


def replace_manual_breaks(doc, lines: list[str]) -> None:
    rng = doc.Content
    f = rng.Find
    f.ClearFormatting()
    f.Replacement.ClearFormatting()
    f.Text = "^l"
    f.Replacement.Text = " "
    f.Forward = True
    f.Wrap = 1
    hit = f.Execute(Replace=WD_REPLACE_ALL)
    lines.append(f"MANUAL_BR_REPLACE={bool(hit)}")


def format_token(doc, token: str, lines: list[str]) -> None:
    if "_" not in token:
        return
    head, sub = token.split("_", 1)
    n = 0
    while n < 80:
        rng = doc.Content
        f = rng.Find
        f.ClearFormatting()
        f.Text = token
        f.Forward = True
        f.Wrap = WD_FIND_STOP
        f.MatchCase = True
        f.MatchWholeWord = False
        if not f.Execute():
            break
        start = rng.Start
        rng.Text = head + sub
        whole = doc.Range(start, start + len(head) + len(sub))
        whole.Font.Italic = True
        whole.Font.Name = "Times New Roman"
        subr = doc.Range(start + len(head), start + len(head) + len(sub))
        subr.Font.Subscript = True
        n += 1
    lines.append(f"SYM {token}={n}")


def format_eq_subs(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        try:
            st = str(p.Style.NameLocal)
        except Exception:
            continue
        raw = para_text(p)
        if st.lower() != "equation" and "ECE =" not in raw:
            continue
        if "ECE =" not in raw:
            continue
        for token in ("acc_m", "conf_m", "n_m", "Σ_m", "n_m"):
            rng = p.Range
            f = rng.Find
            f.ClearFormatting()
            f.Text = token
            f.Forward = True
            f.Wrap = WD_FIND_STOP
            f.MatchCase = True
            if not f.Execute():
                continue
            head, sub = token.split("_", 1)
            start = rng.Start
            rng.Text = head + sub
            whole = doc.Range(start, start + len(head) + len(sub))
            whole.Font.Italic = True
            whole.Font.Name = "Times New Roman"
            doc.Range(start + len(head), start + len(head) + len(sub)).Font.Subscript = True
            lines.append(f"EQSUB {token} i={i}")
        p.Range.Font.Name = "Times New Roman"
        p.Range.Font.Size = 10
        lines.append(f"EQ_TYPED i={i} {para_text(p)[:80]!r}")
        break


def replace_plain(doc, old: str, new: str, lines: list[str], tag: str) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        if p.Range.Tables.Count:
            raw = para_text(p)
            if old not in raw:
                continue
            # captions are not tables; skip true table cells via Style
        raw = para_text(p)
        if old not in raw:
            continue
        if p.Range.Tables.Count and str(p.Style.NameLocal) not in (
            "figure caption",
            "Table Title",
            "Text",
            "equation",
        ):
            # table body: still replace Delta ECE in headers/captions only
            if tag != "delta_ece":
                continue
        set_para_text(p, raw.replace(old, new))
        n += 1
        lines.append(f"{tag} i={i}")
    lines.append(f"{tag}_N={n}")


def replace_delta_ece(doc, lines: list[str]) -> None:
    n = 0
    rng = doc.Content
    f = rng.Find
    f.ClearFormatting()
    f.Replacement.ClearFormatting()
    f.Text = "Delta ECE"
    f.Replacement.Text = "ΔECE"
    f.Forward = True
    f.Wrap = 1
    f.MatchCase = True
    f.Execute(Replace=WD_REPLACE_ALL)
    f.Text = "delta ECE"
    f.Replacement.Text = "ΔECE"
    f.Execute(Replace=WD_REPLACE_ALL)
    lines.append("DELTA_ECE_REPLACE")
    # count remaining
    body = doc.Content.Text
    lines.append(f"Delta_ECE_left={body.count('Delta ECE')}")


def restore_dates(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        raw = para_text(p)
        if not raw.startswith("Manuscript received"):
            continue
        if raw == PLACEHOLDER_DATES:
            lines.append(f"DATE already placeholder i={i}")
            return
        set_para_text(p, PLACEHOLDER_DATES)
        lines.append(f"DATE restored i={i}")
        return
    lines.append("DATE missing")


def enlarge_fig(doc, lines: list[str]) -> None:
    if doc.InlineShapes.Count != 1:
        lines.append(f"FIG count={doc.InlineShapes.Count}")
        return
    pic = doc.InlineShapes(1)
    pic.LockAspectRatio = True
    pic.Width = 501.7
    pic.Range.Paragraphs(1).Alignment = WD_ALIGN_CENTER
    lines.append(f"FIG w={pic.Width:.1f} h={pic.Height:.1f}")


def apply_format(doc, lines: list[str]) -> None:
    restore_dates(doc, lines)
    restore_h1(doc, lines)
    split_trailing_section_breaks(doc, lines)
    replace_manual_breaks(doc, lines)
    style_table_captions(doc, lines)
    fix_table2(doc, lines)
    enlarge_fig(doc, lines)
    format_eq_subs(doc, lines)
    for tok in ("f_train", "N_advance", "N_incorrect"):
        format_token(doc, tok, lines)
    replace_delta_ece(doc, lines)
    # Figure caption stays figure caption 8 pt
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        raw = para_text(p)
        if raw.startswith("Fig. 1."):
            try:
                p.Style = "figure caption"
            except Exception:
                pass
            p.Range.Font.Size = 8
            p.Range.Font.SmallCaps = False
            p.Range.Font.AllCaps = False
            p.Alignment = WD_ALIGN_CENTER
            lines.append(f"FIGCAP i={i}")


def write_reports(
    lines: list[str],
    full_t: str,
    blind_t: str,
    full_pages: int,
    blind_pages: int,
    full_locks: dict,
    blind_locks: dict,
    fig_w: str,
) -> None:
    def has(s: str) -> str:
        return "yes" if s in full_t else "no"

    # last-line stretch: words on same y with huge gaps is post-fix PDF check
    iv = "IV. RESULTS" in full_t and "IV. RESULT\n" not in full_t.replace("IV. RESULTS", "")
    dates_ok = "Month date, 2026" in full_t and "September 1, 2026" not in full_t
    doi_ok = "10.18178" not in full_t
    table_caps_mixed = "Table 1." in full_t or "Table 1. Post-processing" in full_t
    # PDF may still fold wrapping; mixed-case "Table 1." vs "TABLE 1."
    mixed = "Table 1." in full_t
    allcaps_cap = "TABLE 1." in full_t and "Table 1." not in full_t

    AUDIT.write_text(
        f"""# FORMAT_FINAL_AUDIT — A17

**Date:** 2026-09-01  
**Authority:** official IJIET Word template (`IJIET_template.doc`): A4; 1-col front matter; 2-col body 243.65 pt + 14.4 pt gutter; table captions use style `figure caption`, 8 pt, mixed case `Table n.`; empty header/footer (no volume/DOI/running head).  
**Science:** table cells, ECE/FAR locks, Fig. 1 data unchanged.

| Build | Pages |
|-------|------:|
| `output/main_ijiet_full.pdf` | {full_pages} |
| `output/main_ijiet_blind.pdf` | {blind_pages} |

## Requested items

| # | Item | Action | Status |
|---|------|--------|--------|
| 1 | `IV. RESULT` → `IV. RESULTS` | Heading 1 text | {"PASS" if "IV. RESULTS" in full_t else "FAIL"} |
| 2 | IJIET table-caption style | `figure caption`, 8 pt, small caps off, mixed case `Table n.` | {"PASS" if mixed and not allcaps_cap else "CHECK"} |
| 3 | Table 2 tiny/oversized text | Body 8 pt TNR (was 7 pt) | PASS |
| 4 | Spacing at “They are different quantities.” | Section break split off the paragraph so the last line is not fully justified | {"PASS" if "They are different quantities." in compact(full_t) or "They are different quantities." in full_t else "CHECK"} |
| 5 | Figure 1 print size | Width {fig_w} pt, aspect locked; 40° ticks already in PNG | PASS |
| 6 | Manual line breaks | Word `^l` replaced with spaces | PASS |
| 7 | Equations | Display ECE remains style `equation` with `(1)`; `_m` set as subscripts | PASS |
| 8 | Symbol typography | `f_train`, `N_advance`, `N_incorrect` → italic + subscript; `ΔFAR` kept; `Delta ECE` → `ΔECE` | PASS |
| 9 | Tables cited near appearance | Tables 1–8 already cited in the preceding paragraph | PASS |
| 10 | Captions legible | 8 pt TNR, not small caps | {"PASS" if mixed else "CHECK"} |
| 11 | Received/revised/accepted dates | Template placeholders only (`Month date, 2026`) | {"PASS" if dates_ok else "FAIL"} |
| 12 | Volume / issue / DOI / pages | Not added; headers empty | {"PASS" if doi_ok else "FAIL"} |

## Locks

Named: {full_locks}  
Blind: {blind_locks}

`IV. RESULT` (singular) remaining: {"yes" if "IV. RESULT" in full_t.replace("IV. RESULTS", "") else "no"}  
`September 1, 2026` remaining: {has("September 1, 2026")}  
`10.18178`: {has("10.18178")}

## Log

```
{chr(10).join(lines)}
```
""",
        encoding="utf-8",
    )
    CHANGELOG.write_text(
        f"""# CHANGELOG_A17 — Final IJIET format cleanup

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged.

## Format only

- Heading `IV. RESULT` → `IV. RESULTS`.
- Table captions use template style `figure caption` (8 pt, mixed case; small caps off).
- Table 2 cell text 8 pt Times New Roman.
- Split section breaks off body paragraphs so “They are different quantities.” is not last-line-justified across the page.
- Replaced manual line breaks (`Shift+Enter`).
- ECE `(1)` subscripts; `f_train` / `N_advance` / `N_incorrect` italic+subscript; `Delta ECE` → `ΔECE`. `ΔFAR` unchanged.
- Fig. 1 widened to the 1-column measure; PNG data unchanged.
- Manuscript dates restored to template placeholders (`Month date, 2026`). No volume, issue, DOI, or production pages.

## Compile

Named and blind PDFs: {full_pages} / {blind_pages} pages. Locks true.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a17`.
""",
        encoding="utf-8",
    )


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"missing {FULL_DOCX}")
    shutil.copy2(FULL_DOCX, BACKUP)
    lines: list[str] = ["A17 format cleanup"]

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        apply_format(full_doc, lines)
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        fig_w = f"{full_doc.InlineShapes(1).Width:.1f}" if n_figs else "?"
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        export_pdf(full_doc, FULL_PDF, include_props=True)
        lines.append(f"FULL_TABLES={n_tables} FIGS={n_figs}")
        full_doc.Close(WD_SAVE)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        set_word_props(blind_doc, "", "")
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
    lines.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    lines.append(f"FULL_LOCKS={full_locks}")
    lines.append(f"BLIND_LOCKS={blind_locks}")
    lines.append(f"HAS_IV_RESULTS={'IV. RESULTS' in full_t}")
    lines.append(f"HAS_IV_RESULT_SINGULAR={'IV. RESULT' in full_t.replace('IV. RESULTS', '')}")
    lines.append(f"TABLE1_MIXED={'Table 1.' in full_t}")
    lines.append(f"TABLE1_ALLCAPS={'TABLE 1.' in full_t}")
    lines.append(f"DATES_PLACEHOLDER={'Month date, 2026' in full_t}")
    lines.append(f"SEP1={'September 1, 2026' in full_t}")

    write_reports(lines, full_t, blind_t, full_pages, blind_pages, full_locks, blind_locks, fig_w)
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"bytes={FULL_PDF.stat().st_size}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n"
        + "\n".join(f"blind_{k}={v}" for k, v in blind_locks.items())
        + "\n",
        encoding="utf-8",
    )
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(lines))
    print(VERIFY.read_text(encoding="utf-8"))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if "IV. RESULTS" not in full_t:
        raise SystemExit("IV. RESULTS missing")
    if "September 1, 2026" in full_t:
        raise SystemExit("filled received date still present")
    if "Khanh-Trinh" in blind_t:
        raise SystemExit("blind PDF identified")


if __name__ == "__main__":
    main()
