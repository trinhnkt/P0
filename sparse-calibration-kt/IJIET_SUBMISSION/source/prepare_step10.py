#!/usr/bin/env python3
"""IJIET-10: restore a short explanatory subsection from validated analyses only."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP09 = SRC / "main_ijiet_step09.docx"
STEP10_DOCX = SRC / "main_ijiet_step10.docx"
STEP10_DOC = SRC / "main_ijiet_step10.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step10.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step10_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_START = 1
WD_COLLAPSE_END = 0
WD_ALIGN_CENTER = 1
WD_SECTION_CONTINUOUS = 3
WD_OUTLINE_BODY = 10

HEADING = "Explanatory Analysis of Dataset-Dependent Calibration"

DIFFICULTY_TEXT = (
    "For each KC c we define a training-only difficulty proxy difficulty(c) = "
    "1 − mean_train_correctness(c). The mean is taken on the training file only. "
    "This is an observational proxy for how often c is answered incorrectly in "
    "training; it is not a latent IRT difficulty parameter. The reported Spearman "
    "association is ρ(log(1+f_train), difficulty), computed on training-fold KC "
    "summaries. The same file yields item support (distinct items per KC), learner "
    "exposure (distinct learners per KC), and a curriculum-position proxy (median "
    "normalized sequence position). Results report between-KC associations and a "
    "within-KC sparsification check; neither identifies a causal frequency effect."
)

P1 = (
    "Table 6 records three observational pre-conditions under which a "
    "sparse-calibration contrast is estimable on these logs. The same training-only "
    "file also yields item support, learner exposure, and a curriculum-position "
    "proxy. This subsection reports those descriptors and two distinct estimands. "
    "Neither is a causal claim."
)

P2 = (
    "Sparse mass (share of KCs with f_train<100) is 18.9% on ASSISTments 2012, 0% "
    "on Junyi Academy, and 22.5% on XES3G5M. Sparse test-event support is Limited "
    "(N=415), empty, and Reliable (N=2,010). Frequency–difficulty coupling "
    "(Spearman ρ of log(1+f_train) with 1−mean_train_correctness) is ρ=−0.227 and "
    "ρ=−0.416 (rarer KCs harder) versus a weak opposite-signed ρ=+0.087 on XES3G5M. "
    "Item support: ASSISTments is item-rich (median 44.5 items/KC; dense 205 vs "
    "sparse 1); Junyi is nearly uniform (median 18, IQR 5); XES3G5M is thin "
    "(median 3; dense 9 vs sparse 1). Learner exposure is the count of distinct "
    "training learners per KC. Curriculum-position coupling is ρ=−0.308, −0.324, "
    "and −0.125."
)

P3 = (
    "A test-event-weighted KC-level regression of SimpleKT expected calibration "
    "error (ECE) on those five training-only covariates (n=478, 2,645, and 1,263 "
    "KCs) is a between-KC association: it compares different concepts. Standardized "
    "log(1+f_train) coefficients are −0.079 [−0.097, −0.061] on ASSISTments, −0.010 "
    "[−0.014, −0.007] on Junyi, and −0.117 [−0.171, −0.063] on XES3G5M in the "
    "weighted fit. Difficulty is independently associated on ASSISTments and Junyi. "
    "Learner exposure is independently associated only on ASSISTments (+0.019 "
    "[0.010, 0.027]). These signs do not test a frequency dose on a fixed KC."
)

P4 = (
    "Within-KC controlled sparsification holds KC identity, the test set, labels, "
    "and all other KCs’ training rows fixed, and reduces training rows for 30 "
    "originally dense KCs (f_train≥500; pre-registered selection, seed 42, fold 0) "
    "to 500 or 50 rows. Table 7 reports key paired ΔECE (reduced−full), with "
    "KC-bootstrap 95% CIs. Reducing training evidence for the same KC does not "
    "universally worsen calibration: several CIs lie below 0 or include 0. The "
    "observational ASSISTments SimpleKT dense-to-sparse ECE gradient (0.114→0.228) "
    "is not reproduced by sparsifying originally dense ASSISTments KCs (SimpleKT, "
    "50 rows: +0.002 [−0.021, +0.025]). Frequency alone is therefore not a "
    "universal causal explanation. Junyi SimpleKT at 50 rows does show a large "
    "positive ΔECE; that cell shows a within-KC increase is possible, not that it "
    "is a law."
)

TABLE7_CAPTION = (
    "Table 7. Within-KC controlled sparsification (seed 42; 30 originally dense "
    "KCs per dataset). Delta ECE = reduced−full; positive means worse calibration "
    "after keeping 500 or 50 training rows for the same KC. 95% CIs bootstrap over "
    "KCs. Not a causal law for real-world sparsity."
)
TABLE7_HEADER = [
    "Dataset",
    "Model",
    "Reduction",
    "Delta ECE",
    "95% CI",
    "Interpretation",
]
TABLE7_ROWS = [
    ["ASSISTments 2012", "DKT", "500 rows", "−0.047", "[−0.060, −0.033]", "ECE lower"],
    ["ASSISTments 2012", "SimpleKT", "50 rows", "+0.002", "[−0.021, +0.025]", "CI includes 0"],
    ["Junyi Academy", "DKT", "500 rows", "−0.021", "[−0.041, −0.001]", "ECE lower"],
    ["Junyi Academy", "SimpleKT", "50 rows", "+0.135", "[+0.110, +0.161]", "ECE higher"],
    ["XES3G5M", "DKT", "500 rows", "−0.008", "[−0.019, +0.004]", "CI includes 0"],
]


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def fill_table(table, header, rows) -> None:
    table.Style = "Table Grid"
    for j, h in enumerate(header, 1):
        table.Cell(1, j).Range.Text = h
        table.Cell(1, j).Range.Font.Bold = True
        table.Cell(1, j).Range.Font.Size = 7
        table.Cell(1, j).Range.Font.Name = "Times New Roman"
        table.Cell(1, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    for i, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            table.Cell(i, j).Range.Text = str(val)
            table.Cell(i, j).Range.Font.Bold = False
            table.Cell(i, j).Range.Font.Size = 7
            table.Cell(i, j).Range.Font.Name = "Times New Roman"
            table.Cell(i, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    try:
        table.AutoFitBehavior(2)
    except Exception:
        pass


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
                cell.Range.ParagraphFormat.OutlineLevel = WD_OUTLINE_BODY


def wrap_caption_and_table(doc, stub: str, lines, tag: str) -> None:
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            cap_i = i
            break
    if cap_i is None:
        raise RuntimeError(f"wrap: missing {stub}")
    start = doc.Paragraphs(cap_i).Range.Start
    if start > 0:
        doc.Range(start - 1, start - 1).InsertBreak(WD_SECTION_CONTINUOUS)
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            cap_i = i
            break
    cap = doc.Paragraphs(cap_i)
    probe = doc.Range(cap.Range.End, cap.Range.End + 80)
    if probe.Tables.Count < 1:
        raise RuntimeError(f"wrap: no table after {stub}")
    table = probe.Tables(1)
    end = table.Range
    end.Collapse(WD_COLLAPSE_END)
    end.InsertBreak(WD_SECTION_CONTINUOUS)
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        if sec.Range.Start <= table.Range.Start <= sec.Range.End:
            if not (sec.Range.Start <= cap.Range.Start <= sec.Range.End):
                raise RuntimeError(f"{tag}: caption and table not in the same section")
            sec.PageSetup.TextColumns.SetCount(1)
            lines.append(f"{tag}_SECTION={s} COLS={sec.PageSetup.TextColumns.Count}")
            if s < doc.Sections.Count:
                nxt = doc.Sections(s + 1)
                nxt.PageSetup.TextColumns.SetCount(2)
                try:
                    nxt.PageSetup.TextColumns.EvenlySpaced = True
                    nxt.PageSetup.TextColumns.Spacing = 14.4
                except Exception:
                    pass
            break


def restore_h1(doc, lines) -> None:
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
        if "RESULT AND DISCUSSION" in up:
            target = "IV. RESULT AND DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "V. CONCLUSION"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            lines.append(f"H1_FIX {raw!r} -> {target}")


def insert_explanatory(doc, lines) -> None:
    ti = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if "What This Paper Does Not Show" in para_text(doc.Paragraphs(i)):
            ti = i
            break
    if ti is None:
        raise RuntimeError("insertion point not found")
    blocks = [
        (HEADING, "Heading 2"),
        (P1, None),
        (P2, None),
        (P3, None),
        (P4, None),
        (TABLE7_CAPTION, None),
    ]
    for text, style in blocks:
        doc.Paragraphs(ti).Range.InsertParagraphBefore()
        set_para_text(doc.Paragraphs(ti), text)
        if style:
            doc.Paragraphs(ti).Style = style
        try:
            doc.Paragraphs(ti).Range.ListFormat.RemoveNumbers()
        except Exception:
            pass
        if style == "Heading 2":
            set_para_text(doc.Paragraphs(ti), HEADING)
            doc.Paragraphs(ti).Style = style
        ti += 1
    cap = doc.Paragraphs(ti - 1)
    cap.Range.ParagraphFormat.KeepWithNext = True
    rng = doc.Paragraphs(ti).Range
    rng.Collapse(WD_COLLAPSE_START)
    table = doc.Tables.Add(rng, len(TABLE7_ROWS) + 1, len(TABLE7_HEADER))
    fill_table(table, TABLE7_HEADER, TABLE7_ROWS)
    lines.append(f"INSERTED_BEFORE_PARA={ti} TABLES={doc.Tables.Count}")


def main() -> None:
    if not STEP09.exists():
        raise SystemExit(f"Missing {STEP09}")
    shutil.copy2(STEP09, STEP10_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP10_DOCX))
        if "Table 2 shows learner-based AUC" not in doc.Content.Text:
            raise RuntimeError("Results probe missing")

        for i in range(1, doc.Paragraphs.Count + 1):
            raw = para_text(doc.Paragraphs(i))
            if raw.startswith("For each KC c we define"):
                set_para_text(doc.Paragraphs(i), DIFFICULTY_TEXT)
                break

        insert_explanatory(doc, lines)
        neutralize_table_lists(doc)
        wrap_caption_and_table(doc, "Table 7.", lines, "T7")
        restore_h1(doc, lines)

        full = doc.Content.Text
        checks = {
            "results": "Table 2 shows learner-based AUC" in full,
            "heading": HEADING in full,
            "between": "between-KC association" in full,
            "within": "Within-KC controlled sparsification" in full,
            "t7": "Table 7." in full,
            "dkt_neg": "−0.047" in full or "-0.047" in full,
            "sk_zero": "+0.002" in full,
            "not_universal": "does not universally worsen calibration" in full,
            "not_causal": "not a universal causal explanation" in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "no_old_figcap": "Dense concepts dominate interactions" not in full,
            "h1_results": "IV. RESULT AND DISCUSSION" in full,
            "h1_conclusion": "V. CONCLUSION" in full,
        }
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} "
            f"PICS={doc.InlineShapes.Count} SECTIONS={doc.Sections.Count}"
        )
        if doc.InlineShapes.Count != 1:
            raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")
        if doc.Tables.Count < 8:
            raise RuntimeError(f"expected >=8 tables, got {doc.Tables.Count}")
        if pages > 9:
            raise RuntimeError(f"explanatory section too long: {pages} pages")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP10_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP10_DOC), WD_FORMAT_DOC)
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
        lines.append(
            f"PDF_EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}"
        )
    except Exception:
        if lines:
            REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise
    finally:
        if doc is not None:
            doc.Close(WD_SAVE)
        word.Quit()

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
