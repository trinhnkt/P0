#!/usr/bin/env python3
"""A11: rewrite IRT unseen-learner wording (constant fallback, not generic IRT)."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a11"
LOG = HERE / "audit" / "apply_a11_word_log.txt"


def find_replace(doc, old: str, new: str, log: list[str]) -> None:
    if len(new) > 250:
        raise SystemExit(f"replacement too long ({len(new)})")
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
    log.append(f"replaced {old[:60]!r}")


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        find_replace(
            doc,
            "IRT under learner-based splits has no ability parameter for unseen students, so its AUC is 0.50 by construction; we report it as a base-rate reference, not as a ranking competitor.",
            "In our implementation, unseen learners trigger a constant/base-rate fallback, yielding AUC=0.50; we report IRT as a base-rate reference, not as a ranking competitor. This fallback is not an inherent property of IRT.",
            log,
        )
        find_replace(
            doc,
            "IRT AUC is 0.5000 because unseen test learners have no ability parameter; it is a base-rate reference, not a ranking competitor.",
            "In our implementation, unseen learners trigger a constant/base-rate fallback, yielding AUC=0.5000; it is a base-rate reference, not a ranking competitor.",
            log,
        )
        text = doc.Content.Text.lower()
        if "by construction" in text:
            raise SystemExit("leftover 'by construction'")
        if "no ability parameter" in text:
            raise SystemExit("leftover 'no ability parameter'")
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
