#!/usr/bin/env python3
"""A8: OPTION B — declared endpoint Table 8 + pointer to Supplementary Table S2.

Does not change locked ASSISTments ECE/FAR numerals. Table 8 cells come from
the complete A9 grid (500 and 50 rows for every dataset × model).
"""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a8"
LOG = HERE / "audit" / "apply_a8_word_log.txt"

MINUS = "\u2212"

NEW_CAPTION = (
    "Table 8. Within-KC controlled sparsification at protocol endpoints (500 and 50 "
    "training rows; seed 42; 30 originally dense KCs per dataset). The 100-row level "
    "is omitted here by that pre-declared endpoint rule, not by outcome. Delta ECE = "
    "reduced"
    + MINUS
    + "full; positive means worse calibration. 95% CIs bootstrap over KCs. Not a "
    "causal law for real-world sparsity. Complete results for all models, datasets, "
    "and reduction levels are reported in Supplementary Table S2."
)

NEW_PROSE = (
    "Table 8 reports protocol endpoints (500 and 50 rows) for DKT and T-KT on all "
    "three datasets. Complete results for all models, datasets, and reduction levels "
    "are reported in Supplementary Table S2. Reducing training evidence for the same "
    "KC does not universally worsen calibration: several CIs lie below 0 or include 0. "
    "XES3G5M T-KT shows a positive Delta ECE at 50 rows (+0.032 [+0.021, +0.043]) and "
    "at 100 rows (Supplementary Table S2); those cells are not omitted. The observational "
    "ASSISTments T-KT dense-to-sparse ECE gradient (0.114\u21920.228) is not reproduced "
    "by sparsifying originally dense ASSISTments KCs (T-KT, 50 rows: +0.002 ["
    f"{MINUS}0.021, +0.025]). Frequency alone is therefore not a universal causal "
    "explanation. Junyi T-KT at 50 rows does show a large positive Delta ECE; that cell "
    "shows a within-KC increase is possible, not that it is a law."
)

# 12 endpoint rows: dataset, model, reduction, delta, CI, interpretation
TABLE8 = [
    ("ASSISTments 2012", "DKT", "500 rows", f"{MINUS}0.047", f"[{MINUS}0.060, {MINUS}0.033]", "ECE lower"),
    ("ASSISTments 2012", "DKT", "50 rows", f"{MINUS}0.017", f"[{MINUS}0.034, +0.002]", "CI includes 0"),
    ("ASSISTments 2012", "T-KT", "500 rows", f"{MINUS}0.026", f"[{MINUS}0.047, {MINUS}0.002]", "ECE lower"),
    ("ASSISTments 2012", "T-KT", "50 rows", "+0.002", f"[{MINUS}0.021, +0.025]", "CI includes 0"),
    ("Junyi Academy", "DKT", "500 rows", f"{MINUS}0.021", f"[{MINUS}0.041, {MINUS}0.001]", "ECE lower"),
    ("Junyi Academy", "DKT", "50 rows", f"{MINUS}0.004", f"[{MINUS}0.022, +0.013]", "CI includes 0"),
    ("Junyi Academy", "T-KT", "500 rows", "+0.101", "[+0.081, +0.120]", "ECE higher"),
    ("Junyi Academy", "T-KT", "50 rows", "+0.135", "[+0.110, +0.161]", "ECE higher"),
    ("XES3G5M", "DKT", "500 rows", f"{MINUS}0.008", f"[{MINUS}0.019, +0.004]", "CI includes 0"),
    ("XES3G5M", "DKT", "50 rows", "+0.018", "[+0.006, +0.029]", "ECE higher"),
    ("XES3G5M", "T-KT", "500 rows", "+0.014", f"[{MINUS}0.002, +0.032]", "CI includes 0"),
    ("XES3G5M", "T-KT", "50 rows", "+0.032", "[+0.021, +0.043]", "ECE higher"),
]


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


def fill_table8(doc, log: list[str]) -> None:
    t = doc.Tables(8)
    if t.Columns.Count != 6:
        raise SystemExit(f"unexpected Table 8 cols {t.Columns.Count}")
    while t.Rows.Count < 1 + len(TABLE8):
        t.Rows.Add()
    while t.Rows.Count > 1 + len(TABLE8):
        t.Rows(t.Rows.Count).Delete()
    if t.Rows.Count != 13:
        raise SystemExit(f"expected 13 Table 8 rows, got {t.Rows.Count}")
    for i, row in enumerate(TABLE8, start=2):
        for c, val in enumerate(row, start=1):
            t.Cell(i, c).Range.Text = val
    log.append("Table 8 now 12 endpoint rows (500 and 50 for 6 dataset-model pairs)")


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
            "Table 8 reports key paired",
            NEW_PROSE,
            log,
        )
        replace_para_containing(
            doc,
            "Table 8. Within-KC controlled sparsification",
            NEW_CAPTION,
            log,
        )
        fill_table8(doc, log)
        text = doc.Content.Text
        if "Supplementary Table S2" not in text:
            raise SystemExit("S2 pointer missing")
        if "does not universally worsen calibration" not in text:
            raise SystemExit("required interpretation missing")
        if "+0.032" not in text:
            raise SystemExit("XES T-KT t50 positive cell missing")
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
