#!/usr/bin/env python3
"""A10: Table 2 checkpoint wording from source audit (no numeric changes)."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a10"
LOG = HERE / "audit" / "apply_a10_word_log.txt"


def main() -> None:
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        t = doc.Tables(2)
        if t.Rows.Count != 10 or t.Columns.Count != 4:
            raise SystemExit(f"unexpected Table 2 shape {t.Rows.Count}x{t.Columns.Count}")
        r7 = t.Cell(7, 1).Range.Text.replace("\r", " ").replace("\x07", "").strip()
        r10 = t.Cell(10, 1).Range.Text.replace("\r", " ").replace("\x07", "").strip()
        if r7 != "Early stopping":
            raise SystemExit(f"row 7 is {r7!r}")
        if r10 != "Selection metric":
            raise SystemExit(f"row 10 is {r10!r}")
        t.Cell(7, 2).Range.Text = "Fixed 10 epochs; final checkpoint."
        t.Cell(7, 3).Range.Text = "Fixed 50 epochs; final checkpoint."
        t.Cell(7, 4).Range.Text = "Fixed 50 epochs; final checkpoint."
        t.Cell(10, 2).Range.Text = "final checkpoint"
        t.Cell(10, 3).Range.Text = "final checkpoint"
        t.Cell(10, 4).Range.Text = "final checkpoint"
        log.append("Table 2 early-stopping and selection-metric cells updated")
        text = doc.Content.Text
        if "validation AUC" in text and "patience 4" not in text:
            pass
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
