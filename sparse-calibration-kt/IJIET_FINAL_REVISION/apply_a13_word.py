#!/usr/bin/env python3
"""A13: add partition-level ΔFAR robustness; keep five-run 0.047."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a13"
LOG = HERE / "audit" / "apply_a13_word_log.txt"

PROSE_OLD = (
    "It is positive in all five training runs spanning four unique student partitions "
    "(mean 0.047, sd 0.033)."
)
PROSE_NEW = (
    "It is positive in 5/5 training runs (mean 0.047, sd 0.033) and positive in 4/4 "
    "unique partition-level estimates (mean 0.056, range 0.015–0.087)."
)
DISC_OLD = "with ΔFAR positive in all five training runs spanning four unique student partitions"
DISC_NEW = (
    "with ΔFAR positive in 5/5 training runs and positive in 4/4 unique partition-level estimates"
)
CAP_OLD = "across four unique learner partitions (2025 and 2026 share a split)."
CAP_NEW = (
    "across four unique learner partitions (2025 and 2026 share a split). "
    "Partition-level ΔFAR averages seeds 2025 and 2026 first; T-KT mean 0.056, range 0.015–0.087."
)
CELL_OLD = "5/5 runs (4 partitions)"
CELL_NEW = "5/5 runs; 4/4 unique partitions"


def patch_paragraphs(doc, log: list[str]) -> None:
    counts = {"prose": 0, "disc": 0, "cap": 0}
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i).Range
        inner = doc.Range(para.Start, para.End - 1)
        text = inner.Text
        changed = False
        if PROSE_OLD in text:
            text = text.replace(PROSE_OLD, PROSE_NEW, 1)
            counts["prose"] += 1
            changed = True
        if DISC_OLD in text:
            text = text.replace(DISC_OLD, DISC_NEW, 1)
            counts["disc"] += 1
            changed = True
        if CAP_OLD in text and "Partition-level ΔFAR averages seeds 2025 and 2026 first" not in text:
            text = text.replace(CAP_OLD, CAP_NEW, 1)
            counts["cap"] += 1
            changed = True
        if changed:
            inner.Text = text
    if counts["prose"] != 1:
        raise SystemExit(f"Results sentence replacements={counts['prose']}, expected 1")
    if counts["disc"] != 1:
        raise SystemExit(f"Discussion sentence replacements={counts['disc']}, expected 1")
    if counts["cap"] != 1:
        raise SystemExit(f"Table 6 caption replacements={counts['cap']}, expected 1")
    log.append(f"patched prose={counts['prose']} disc={counts['disc']} cap={counts['cap']}")


def patch_table6(doc, log: list[str]) -> None:
    table = doc.Tables(6)
    cell = table.Cell(2, 4)
    inner = doc.Range(cell.Range.Start, cell.Range.End - 1)
    text = inner.Text.replace("\r", "").replace("\x07", "")
    if text != CELL_OLD:
        raise SystemExit(f"Table 6 r2c4={text!r}, expected {CELL_OLD!r}")
    inner.Text = CELL_NEW
    log.append(f"table6 cell {CELL_OLD!r} -> {CELL_NEW!r}")


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        patch_table6(doc, log)
        patch_paragraphs(doc, log)
        text = doc.Content.Text
        if "positive in 5/5 training runs" not in text:
            raise SystemExit("missing 5/5 phrase")
        if "positive in 4/4 unique partition-level estimates" not in text:
            raise SystemExit("missing 4/4 phrase")
        if text.count("positive in 5/5 training runs") < 2:
            raise SystemExit("expected 5/5 in Results and Discussion")
        if "0.047" not in text:
            raise SystemExit("five-run mean 0.047 missing")
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
