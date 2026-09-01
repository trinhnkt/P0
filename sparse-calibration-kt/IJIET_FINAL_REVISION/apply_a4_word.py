#!/usr/bin/env python3
"""Patch Section IV.D n-unit wording and cluster-robust coefficients in the working Word copy."""
from __future__ import annotations

from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
LOG = HERE / "audit" / "apply_a4_word_log.txt"


def find_replace(doc, old: str, new: str) -> None:
    if old in new:
        raise SystemExit(f"old is substring of new: {old!r}")
    rng = doc.Content
    finder = rng.Find
    finder.ClearFormatting()
    finder.Replacement.ClearFormatting()
    finder.Text = old
    finder.Replacement.Text = new
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWildcards = False
    if not finder.Execute(Replace=2):
        raise SystemExit(f"not found: {old!r}")
    leftover = doc.Content.Find
    leftover.ClearFormatting()
    leftover.Text = old
    leftover.Forward = True
    leftover.Wrap = 0
    leftover.MatchCase = True
    leftover.MatchWildcards = False
    if leftover.Execute():
        raise SystemExit(f"leftover: {old!r}")


def main() -> None:
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    log = []
    try:
        pairs = [
            (
                "(n=478, 2,645, and 1,263 KCs) is a between-KC association: it compares different concepts.",
                "(478 KC-fold observations representing 261 unique KCs; 2,645 representing 1,326; and 1,263 representing 830) is a between-KC association: it compares different concepts, with cluster-robust standard errors at kc_id.",
            ),
            (
                "Standardized log(1+f_train) coefficients are \u22120.079 [\u22120.097, \u22120.061] on ASSISTments, \u22120.010 [\u22120.014, \u22120.007] on Junyi, and \u22120.117 [\u22120.171, \u22120.063] on XES3G5M in the weighted fit.",
                "Standardized log(1+f_train) coefficients are \u22120.068 [\u22120.086, \u22120.050] on ASSISTments, \u22120.014 [\u22120.018, \u22120.010] on Junyi, and \u22120.069 [\u22120.123, \u22120.015] on XES3G5M in the weighted fit.",
            ),
            (
                "Learner exposure is independently associated only on ASSISTments (+0.019 [0.010, 0.027]).",
                "Learner exposure is independently associated only on ASSISTments (+0.016 [0.004, 0.027]).",
            ),
        ]
        for old, new in pairs:
            find_replace(doc, old, new)
            log.append(f"OK {old[:70]!r}")
        doc.Save()
        log.append("saved")
    finally:
        doc.Close(0)
        word.Quit()
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
