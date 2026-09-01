#!/usr/bin/env python3
"""A7: split Table 7 into estimability (C1–C2) vs observed pattern (C3+).

Does not change numerals. Uses T-KT (A6 LEVEL 3 name), not SimpleKT.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a7"
LOG = HERE / "audit" / "apply_a7_word_log.txt"

MINUS = "\u2212"  # Unicode minus used in the manuscript tables

NEW_INTRO = (
    "Table 7 separates two questions. C1–C2 determine whether a sparse contrast "
    "can be estimated under the registered thresholds; C3 and other structural "
    "descriptors help characterize the direction of the observed pattern. C1 is a "
    "non-empty low-frequency tail under the split actually used; C2 is enough "
    "sparse test events for at least a Limited-flag ECE. C3 (frequency–difficulty "
    "coupling) is not treated as necessary or sufficient for an adverse gradient. "
    "Junyi fails C1–C2. ASSISTments and XES3G5M both meet C1–C2, yet only "
    "ASSISTments shows a dense-to-sparse T-KT ECE rise."
)

NEW_CAPTION = (
    "Table 7. Empirical conditions associated with the availability and direction "
    "of sparse-calibration contrasts on the three evaluated datasets. Sparse mass: "
    f"share of KCs with train-only frequency f_train<100. C3 is not necessary or "
    "sufficient for an adverse gradient."
)

NEW_AFTER = (
    "Learner exposure (distinct training learners per KC) enters the regressions "
    "below; it is not a C1–C2 estimability criterion. This subsection reports two "
    "distinct estimands. Neither is a causal claim."
)

NEW_DISCUSSION = (
    "The three logs differ on C1–C2 estimability and on structural context "
    "(Table 7). Junyi’s learner-based sparse bucket is empty. ASSISTments and "
    "XES3G5M both have a non-empty sparse tail and at least Limited test support, "
    "yet T-KT ECE rises on ASSISTments and stays essentially flat on XES3G5M. "
    "Frequency–difficulty coupling, item support, and curriculum-position coupling "
    "are reported as context, not as necessary or sufficient conditions for that "
    "direction. Within-KC sparsification (Table 8) does not reproduce the "
    "observational ASSISTments T-KT ECE gradient. These are associations on these "
    "datasets. Untested explanations—curriculum hierarchy, tagging granularity, "
    "ceiling effects, and item semantics—are hypotheses unless experimentally "
    "isolated, which this study does not do."
)


def replace_para_containing(doc, needle: str, new_text: str, log: list[str]) -> None:
    rng = doc.Content
    finder = rng.Find
    finder.ClearFormatting()
    finder.Text = needle
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWildcards = False
    if not finder.Execute():
        raise SystemExit(f"not found: {needle!r}")
    para = rng.Paragraphs(1).Range
    inner = doc.Range(para.Start, para.End - 1)
    inner.Text = new_text
    log.append(f"replaced para containing {needle[:48]!r}")


def delete_para_containing(doc, needle: str, log: list[str]) -> None:
    rng = doc.Content
    finder = rng.Find
    finder.ClearFormatting()
    finder.Text = needle
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWildcards = False
    if not finder.Execute():
        raise SystemExit(f"not found for delete: {needle!r}")
    rng.Paragraphs(1).Range.Delete()
    log.append(f"deleted para containing {needle[:48]!r}")


def set_cell(table, r: int, c: int, text: str) -> None:
    table.Cell(r, c).Range.Text = text


def merge_row(table, r: int, text: str) -> None:
    table.Cell(r, 1).Merge(table.Cell(r, table.Columns.Count))
    cell = table.Cell(r, 1)
    cell.Range.Text = text
    cell.Range.Font.Bold = True
    cell.Range.ParagraphFormat.Alignment = 0  # left
    try:
        cell.Shading.BackgroundPatternColor = 14869218  # light gray
    except Exception:
        pass


def restructure_table7(doc, log: list[str]) -> None:
    t = doc.Tables(7)
    if t.Rows.Count != 5 or t.Columns.Count != 4:
        raise SystemExit(f"unexpected Table 7 shape {t.Rows.Count}x{t.Columns.Count}")
    header = t.Cell(1, 1).Range.Text.replace("\r", " ").replace("\x07", "").strip()
    if header != "Condition":
        raise SystemExit(f"unexpected Table 7 header {header!r}")

    # Insert A header before current sparse-mass row (row 2).
    t.Rows.Add(t.Rows(2))
    # Insert B header before difficulty (now row 5).
    t.Rows.Add(t.Rows(5))
    # Insert item-support before ECE (now row 7).
    t.Rows.Add(t.Rows(7))
    # Insert curriculum before ECE (now row 8).
    t.Rows.Add(t.Rows(8))
    if t.Rows.Count != 9:
        raise SystemExit(f"expected 9 rows after inserts, got {t.Rows.Count}")

    set_cell(t, 3, 1, "Sparse mass (C1)")
    set_cell(t, 4, 1, "Sparse test support (C2)")
    set_cell(t, 6, 1, "Difficulty coupling (C3)")
    set_cell(t, 7, 1, "Item support")
    set_cell(t, 7, 2, "median 44.5 (dense 205 vs sparse 1)")
    set_cell(t, 7, 3, "median 18 (IQR 5)")
    set_cell(t, 7, 4, "median 3 (dense 9 vs sparse 1)")
    set_cell(t, 8, 1, "Curriculum-position coupling")
    set_cell(t, 8, 2, f"ρ={MINUS}0.308")
    set_cell(t, 8, 3, f"ρ={MINUS}0.324")
    set_cell(t, 8, 4, f"ρ={MINUS}0.125")
    set_cell(t, 9, 1, "Observed T-KT ECE")

    merge_row(t, 2, "A. Estimability")
    merge_row(t, 5, "B. Observed pattern/context")
    log.append("restructured Table 7 to 9 rows with A/B blocks")


def leftover_forbidden(doc) -> list[str]:
    text = doc.Content.Text
    bad = []
    for needle in (
        "three empirical conditions",
        "three observational pre-conditions",
        "meets all three",
        "diagnostic pre-condition",
        "three pre-conditions",
    ):
        if needle.lower() in text.lower():
            bad.append(needle)
    return bad


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        replace_para_containing(
            doc,
            "On the three datasets studied here, three empirical conditions track",
            NEW_INTRO,
            log,
        )
        replace_para_containing(
            doc,
            "Table 7. Empirical observations, on these three datasets,",
            NEW_CAPTION,
            log,
        )
        restructure_table7(doc, log)
        replace_para_containing(
            doc,
            "Table 7 records three observational pre-conditions",
            NEW_AFTER,
            log,
        )
        delete_para_containing(
            doc,
            "Sparse mass (share of KCs with f_train<100) is 18.9%",
            log,
        )
        replace_para_containing(
            doc,
            "The three logs differ on measured structural descriptors (Table 7):",
            NEW_DISCUSSION,
            log,
        )
        bad = leftover_forbidden(doc)
        if bad:
            raise SystemExit(f"forbidden leftover phrasing: {bad}")
        doc.Save()
        log.append("saved")
    except Exception:
        doc.Close(0)
        word.Quit()
        raise
    doc.Close(0)
    word.Quit()
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
