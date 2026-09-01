#!/usr/bin/env python3
"""A9: replace unverifiable 'pre-registered' language. Selection rule unchanged."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a9"
LOG = HERE / "audit" / "apply_a9_word_log.txt"

MINUS = "\u2212"

NEW_SPARSE_PROSE = (
    "Within-KC controlled sparsification holds KC identity, the test set, labels, "
    "and all other KCs' training rows fixed, and reduces training rows for 30 "
    "originally dense KCs (f_train\u2265500; seed 42, fold 0) to 500 or 50 rows. "
    "The selection rule was fixed and recorded before reduced-evidence ECE was "
    "inspected. Table 8 reports protocol endpoints (500 and 50 rows) for DKT and "
    "T-KT on all three datasets. Complete results for all models, datasets, and "
    "reduction levels are reported in Supplementary Table S2. Reducing training "
    "evidence for the same KC does not universally worsen calibration: several CIs "
    "lie below 0 or include 0. XES3G5M T-KT shows a positive Delta ECE at 50 rows "
    "(+0.032 [+0.021, +0.043]) and at 100 rows (Supplementary Table S2); those cells "
    "are not omitted. The observational ASSISTments T-KT dense-to-sparse ECE gradient "
    "(0.114\u21920.228) is not reproduced by sparsifying originally dense ASSISTments "
    f"KCs (T-KT, 50 rows: +0.002 [{MINUS}0.021, +0.025]). Frequency alone is therefore "
    "not a universal causal explanation. Junyi T-KT at 50 rows does show a large "
    "positive Delta ECE; that cell shows a within-KC increase is possible, not that "
    "it is a law."
)


def find_replace(doc, old: str, new: str, log: list[str]) -> None:
    if len(new) > 250:
        raise SystemExit(f"replacement too long ({len(new)}): {old[:40]!r}")
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
    ok = bool(finder.Execute(Replace=2))
    leftover = doc.Content.Find
    leftover.ClearFormatting()
    leftover.Text = old
    leftover.Forward = True
    leftover.Wrap = 0
    leftover.MatchCase = True
    leftover.MatchWildcards = False
    if leftover.Execute():
        raise SystemExit(f"leftover: {old!r}")
    if not ok:
        raise SystemExit(f"not found: {old!r}")
    log.append(f"replaced {old!r} -> {new!r}")


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


def leftover_forbidden(doc) -> list[str]:
    text = doc.Content.Text.lower()
    bad = []
    for needle in (
        "pre-registered",
        "preregistered",
        "pre-registration",
        "preregistration",
    ):
        if needle in text:
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
        find_replace(doc, "pre-registered cuts", "pre-specified cuts", log)
        find_replace(
            doc,
            "under the registered thresholds",
            "under the protocol thresholds",
            log,
        )
        replace_para_containing(
            doc,
            "Table 8 reports protocol endpoints (500 and 50 rows)",
            NEW_SPARSE_PROSE,
            log,
        )
        bad = leftover_forbidden(doc)
        if bad:
            raise SystemExit(f"forbidden leftover: {bad}")
        if "The selection rule was fixed and recorded before reduced-evidence ECE was inspected." not in doc.Content.Text:
            raise SystemExit("preferred sparsification sentence missing")
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
