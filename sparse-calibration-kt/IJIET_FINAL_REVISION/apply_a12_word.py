#!/usr/bin/env python3
"""A12: cite Supplementary Table S1 for Brier decomposition (no new claims)."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a12"
LOG = HERE / "audit" / "apply_a12_word_log.txt"

IRT_OLD = "but resolution is zero:"
IRT_NEW = "but resolution is zero (Supplementary Table S1):"
FLAT_OLD = (
    "A flat ECE is not a license to skip occupancy reporting and is not the same as a flat miss rate."
)
FLAT_NEW = (
    "A flat ECE is not a license to skip occupancy reporting and is not the same as a flat miss rate. "
    "Full Brier, reliability, resolution, and uncertainty results are provided in Supplementary Table S1."
)


def patch_paragraphs(doc, log: list[str]) -> None:
    n_irt = 0
    n_flat = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i).Range
        inner = doc.Range(para.Start, para.End - 1)
        text = inner.Text
        changed = False
        if IRT_OLD in text and IRT_NEW not in text:
            text = text.replace(IRT_OLD, IRT_NEW, 1)
            n_irt += 1
            changed = True
        if FLAT_OLD in text and "Full Brier, reliability, resolution, and uncertainty results" not in text:
            text = text.replace(FLAT_OLD, FLAT_NEW, 1)
            n_flat += 1
            changed = True
        if changed:
            inner.Text = text
    if n_irt != 1:
        raise SystemExit(f"IRT cite replacements={n_irt}, expected 1")
    if n_flat != 1:
        raise SystemExit(f"Full-Brier sentence replacements={n_flat}, expected 1")
    log.append(f"patched IRT cite n={n_irt}, Brier sentence n={n_flat}")


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
        text = doc.Content.Text
        if text.count("Supplementary Table S1") < 2:
            raise SystemExit("expected IRT cite and full-Brier sentence")
        if "0.0031" not in text:
            raise SystemExit("locked IRT ECE missing")
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
