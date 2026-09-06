#!/usr/bin/env python3
"""Apply GO/NO-GO necessary wording + Fig. 1 aspect. No numeric lock edits."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
FULL = HERE / "manuscript" / "main_ijiet_full.docx"
BAK = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_p0_gng"

WD_FORMAT_XML = 16
WD_SAVE = -1
WD_ALIGN_CENTER = 1
FIG_W = 501.8
FIG_H = 501.8 * 268 / 809

PAIRS = [
    (
        "Three alternative train-only frequency cuts leave that ASSISTments "
        "T-KT rise positive",
        "Two alternative train-only frequency cut grids leave that "
        "ASSISTments T-KT rise positive",
    ),
    (
        "competitive AUC, Limited-but-estimable sparse occupancy",
        "aggregate discrimination that does not reveal the sparse-stratum "
        "calibration pattern, Limited-but-estimable sparse occupancy",
    ),
    (
        "plenty of sparse mass and Reliable occupancy",
        "plenty of low-frequency tail mass (f_train<100) and Reliable occupancy",
    ),
    (
        "Success claims require Limited or Reliable occupancy. "
        "Insufficient cells are descriptive only.",
        "Substantive stratum-level interpretations require at least Limited "
        "support; Insufficient cells are descriptive only.",
    ),
    (
        "Sparse mass: share of KCs with train-only frequency",
        "Low-frequency tail mass: share of KCs with train-only frequency",
    ),
    (
        "evaluation protocol that combines learner-based and temporal views,",
        "evaluation protocol that combines learner-based primary reporting "
        "with a complementary temporal split,",
    ),
    (
        "evaluation protocol combining learner-based and temporal views,",
        "evaluation protocol with learner-based primary reporting and a "
        "complementary temporal split,",
    ),
]


def cell_text(cell) -> str:
    return " ".join((cell.Range.Text or "").replace("\r", " ").replace("\x07", " ").split())


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not BAK.exists():
        shutil.copy2(FULL, BAK)
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(FULL))
    log: list[str] = ["gng-apply"]
    counts = {old: 0 for old, _ in PAIRS}
    try:
        for i in range(1, doc.Paragraphs.Count + 1):
            para = doc.Paragraphs(i)
            try:
                if para.Range.Tables.Count:
                    continue
            except Exception:
                pass
            inner = doc.Range(para.Range.Start, para.Range.End - 1)
            text = inner.Text or ""
            changed = False
            for old, new in PAIRS:
                if old in text:
                    text = text.replace(old, new, 1)
                    counts[old] += 1
                    changed = True
            if changed:
                inner.Text = text
                log.append(f"p{i}")

        t8_hits = 0
        for ti in range(1, doc.Tables.Count + 1):
            tbl = doc.Tables(ti)
            for r in range(1, tbl.Rows.Count + 1):
                for c in range(1, tbl.Columns.Count + 1):
                    try:
                        txt = cell_text(tbl.Cell(r, c))
                    except Exception:
                        continue
                    if txt == "Sparse mass (E1)":
                        rng = tbl.Cell(r, c).Range
                        rng.Text = "Low-frequency tail mass (E1)"
                        t8_hits += 1
        log.append(f"t8_cells={t8_hits}")
        if t8_hits != 1:
            raise SystemExit(f"Table 8 Sparse mass cell hits={t8_hits}")

        fig1 = doc.InlineShapes(1)
        fig1.LockAspectRatio = False
        fig1.Width = FIG_W
        fig1.Height = FIG_H
        fig1.LockAspectRatio = True
        try:
            fig1.Range.Paragraphs(1).Alignment = WD_ALIGN_CENTER
        except Exception:
            pass
        log.append(f"fig1 {fig1.Width:.1f}x{fig1.Height:.1f}")
        if abs(fig1.Width - FIG_W) > 1.5 or abs(fig1.Height - FIG_H) > 3:
            raise SystemExit(f"fig1 size {fig1.Width:.1f}x{fig1.Height:.1f}")

        body = doc.Content.Text or ""
        if "Three alternative train-only" in body:
            raise SystemExit("C01 old count remains")
        if "two alternative train-only frequency cut grids" not in body.lower():
            raise SystemExit("C01 new grids phrase missing")
        if "competitive AUC" in body:
            raise SystemExit("C06 competitive AUC remains")
        if "aggregate discrimination that does not reveal" not in body:
            raise SystemExit("C06 replacement missing")
        if "plenty of sparse mass" in body or "Sparse mass (E1)" in body:
            raise SystemExit("C10 sparse mass remains")
        if "low-frequency tail mass" not in body.lower():
            raise SystemExit("C10 tail mass missing")
        if "Success claims require" in body:
            raise SystemExit("C13 old success-claims remains")
        if "Substantive stratum-level interpretations" not in body:
            raise SystemExit("C13 replacement missing")
        if "learner-based primary reporting" not in body:
            raise SystemExit("C12 primary-reporting phrase missing")
        if "0.1136" not in body or "0.2280" not in body:
            raise SystemExit("ECE locks missing")
        if "0.1176" not in body or "0.1254" not in body:
            raise SystemExit("XES ECE locks missing")
        missing = [old[:40] for old, n in counts.items() if n != 1]
        if missing:
            raise SystemExit(f"pair counts {counts}")
        log.append("counts=" + str({k[:32]: n for k, n in counts.items()}))
        doc.SaveAs2(str(FULL), WD_FORMAT_XML)
        print("\n".join(log))
    finally:
        try:
            doc.Close(WD_SAVE)
        except Exception:
            pass
        word.Quit()


if __name__ == "__main__":
    main()
