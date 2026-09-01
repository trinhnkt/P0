#!/usr/bin/env python3
"""A14: replace informal wording; do not change numbers, tables, or conclusions."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a14"
LOG = HERE / "audit" / "apply_a14_word_log.txt"

# Unique prose snippets only. Tables / numbers / citations untouched.
REPLACEMENTS = [
    (
        "sparse advances are dirtier than dense advances",
        "sparse advance decisions are less reliable than dense advance decisions",
    ),
    (
        "Table 3 is the wrong dashboard",
        "Table 3 is an insufficient evaluation summary",
    ),
    (
        "the cautionary case",
        "an illustrative case",
    ),
    (
        "advances more dirty sparse attempts",
        "yields more higher-error sparse advance decisions",
    ),
    (
        "the opposite caution",
        "the contrasting case",
    ),
    (
        "a one-fold accident",
        "a single-partition artifact",
    ),
    (
        "while ranking nothing",
        "while providing no ranking information",
    ),
]

FORBIDDEN = [
    "wrong dashboard",
    "dirty sparse attempts",
    "dirtier",
    "bake-off",
    "bake off",
    "cautionary case",
    "one-fold accident",
    "ranking nothing",
]


def patch_paragraphs(doc, log: list[str]) -> None:
    counts = {old: 0 for old, _ in REPLACEMENTS}
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i).Range
        inner = doc.Range(para.Start, para.End - 1)
        text = inner.Text
        changed = False
        for old, new in REPLACEMENTS:
            if old in text:
                text = text.replace(old, new)
                counts[old] += 1
                changed = True
        if changed:
            inner.Text = text
    for old, n in counts.items():
        if n != 1:
            raise SystemExit(f"replacements for {old!r} = {n}, expected 1")
        log.append(f"replaced {old!r}")


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        patch_paragraphs(doc, log)
        text = doc.Content.Text.lower()
        leftover = [p for p in FORBIDDEN if p.lower() in text]
        if leftover:
            raise SystemExit(f"leftover informal: {leftover}")
        if "0.1136" not in doc.Content.Text or "0.2280" not in doc.Content.Text:
            raise SystemExit("locked ECE cells missing")
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
