#!/usr/bin/env python3
"""A6: LEVEL 3 naming — our model is Transformer KT baseline, not published SimpleKT.

Does not change numerals. Leaves the bibliography title and explicit
'published SimpleKT' / 'official SimpleKT checkpoint' phrases intact.
"""
from __future__ import annotations

from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
LOG = HERE / "audit" / "apply_a6_word_log.txt"


def find_replace(doc, old: str, new: str, *, allow_missing: bool = False) -> int:
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
    found = finder.Execute(Replace=2)
    leftover = doc.Content.Find
    leftover.ClearFormatting()
    leftover.Text = old
    leftover.Forward = True
    leftover.Wrap = 0
    leftover.MatchCase = True
    leftover.MatchWildcards = False
    if leftover.Execute():
        raise SystemExit(f"leftover after replace: {old!r}")
    if not found and not allow_missing:
        raise SystemExit(f"not found: {old!r}")
    return 1 if found else 0


def count_hits(doc, needle: str) -> int:
    n = 0
    rng = doc.Content
    rng.Find.ClearFormatting()
    rng.Find.Text = needle
    rng.Find.Forward = True
    rng.Find.Wrap = 0
    rng.Find.MatchCase = True
    rng.Find.MatchWildcards = False
    while rng.Find.Execute():
        n += 1
        rng.Collapse(0)  # wdCollapseEnd
        if n > 200:
            break
    return n


def main() -> None:
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    log: list[str] = []
    try:
        protect = [
            (
                "SimpleKT: A simple but tough-to-beat baseline for Knowledge Tracing",
                "@@BIBSIMPLEKT@@",
            ),
            (
                "local IRT, DKT, and SimpleKT implementations",
                "local IRT, DKT, and a Transformer KT baseline",
            ),
            (
                "The local SimpleKT class is a two-layer Transformer encoder and is not byte-identical to the official SimpleKT checkpoint [4].",
                "The Transformer KT baseline is a two-layer Transformer encoder over DKT-style KC-response tokens. It is not the published SimpleKT architecture [4] and is not an official SimpleKT checkpoint.",
            ),
            (
                "and SimpleKT [4], retain that task while substituting self-attention for recurrence.",
                "and published SimpleKT [4], retain that task while substituting self-attention for recurrence. Section IV scores a local Transformer KT baseline, not that published SimpleKT model.",
            ),
            (
                "with IRT, DKT, and SimpleKT.",
                "with IRT, DKT, and a Transformer KT baseline.",
            ),
            ("published SimpleKT architecture [4]", "@@PUBARCH@@"),
            ("official SimpleKT checkpoint", "@@OFFICIALCKPT@@"),
            ("published SimpleKT [4]", "@@PUBCITE@@"),
            ("published SimpleKT model", "@@PUBMODEL@@"),
        ]
        for old, new in protect:
            if len(new) > 250:
                raise SystemExit(f"replacement too long ({len(new)}): {new[:40]!r}")
            find_replace(doc, old, new)
            log.append(f"protect {old[:60]!r}")

        n_before = count_hits(doc, "SimpleKT")
        log.append(f"SimpleKT remaining before bulk={n_before}")
        find_replace(doc, "SimpleKT", "Transformer KT")
        log.append("bulk SimpleKT -> Transformer KT")

        restore = [
            (
                "@@BIBSIMPLEKT@@",
                "SimpleKT: A simple but tough-to-beat baseline for Knowledge Tracing",
            ),
            ("@@PUBARCH@@", "published SimpleKT architecture [4]"),
            ("@@OFFICIALCKPT@@", "official SimpleKT checkpoint"),
            ("@@PUBCITE@@", "published SimpleKT [4]"),
            ("@@PUBMODEL@@", "published SimpleKT model"),
        ]
        for old, new in restore:
            find_replace(doc, old, new)
            log.append(f"restore {new[:50]!r}")

        leftover = count_hits(doc, "SimpleKT")
        log.append(f"SimpleKT leftover (paper-only expected)={leftover}")
        if leftover < 3:
            raise SystemExit(f"too few SimpleKT leftovers (bib/related/methods): {leftover}")
        for tok in ("@@BIBSIMPLEKT@@", "@@PUBARCH@@", "@@OFFICIALCKPT@@", "@@PUBCITE@@", "@@PUBMODEL@@"):
            if count_hits(doc, tok):
                raise SystemExit(f"unrestored {tok}")

        doc.Save()
        log.append("saved")
    finally:
        doc.Close(0)
        word.Quit()
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
