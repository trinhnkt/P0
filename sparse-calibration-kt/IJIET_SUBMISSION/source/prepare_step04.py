#!/usr/bin/env python3
"""IJIET-04: revise Abstract only. No Results edits. No original-manuscript edits."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP03 = SRC / "main_ijiet_step03.docx"
STEP04_DOCX = SRC / "main_ijiet_step04.docx"
STEP04_DOC = SRC / "main_ijiet_step04.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step04.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step04_verify.txt"

ABSTRACT_BODY = (
    "Knowledge Tracing (KT) systems that skip, remediate, or advance practice typically "
    "consume a predicted probability rather than an area-under-the-curve (AUC) score, so "
    "population ranking can look acceptable while probabilities are poorly calibrated on "
    "rarely practiced knowledge components (KCs). This paper reports a diagnostic "
    "evaluation—not a new KT architecture—of train-only KC-frequency strata on three "
    "public logs (ASSISTments 2012, Junyi Academy, and XES3G5M) with IRT, DKT, and "
    "SimpleKT. Lower KC training frequency does not universally degrade discrimination, "
    "but calibration can become less reliable in some sparse-concept regimes. On "
    "ASSISTments 2012, SimpleKT expected calibration error (ECE) rises from 0.114 on "
    "dense KCs to 0.228 on sparse KCs (Limited occupancy, N≈415); Junyi has no "
    "learner-based sparse stratum, and XES3G5M SimpleKT ECE is essentially flat. A "
    "locked global threshold at τ=0.7 raises the SimpleKT false-advance rate "
    "(incorrect-response rate among advance decisions) from 0.196 (dense) to 0.268 "
    "(sparse) on one ASSISTments fold; the sparse–dense gap stays positive on all five "
    "training seeds (mean 0.047; four unique student partitions). This is a simulated "
    "decision gate, not a classroom intervention. Probability-threshold decisions should "
    "be validated by KC-frequency stratum rather than on population AUC or ECE alone."
)

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_ALIGN_JUSTIFY = 3
WD_SAVE = -1


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def find_para(doc, startswith: str) -> int:
    for i in range(1, doc.Paragraphs.Count + 1):
        if doc.Paragraphs(i).Range.Text.strip().startswith(startswith):
            return i
    raise RuntimeError(f"paragraph not found: {startswith}")


def style_abstract(para) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Font.Name = "Times New Roman"
    rng.Font.Size = 9
    rng.Font.Bold = False
    rng.Font.Italic = True
    text = rng.Text
    marker = "Abstract—"
    if not text.startswith(marker):
        marker = "Abstract-"
    n = len(marker) if text.startswith(marker) else len("Abstract")
    label = para.Range
    label.Start = para.Range.Start
    label.End = para.Range.Start + n
    label.Font.Bold = True
    label.Font.Italic = False
    label.Font.Name = "Times New Roman"
    label.Font.Size = 9


def main() -> None:
    if not STEP03.exists():
        raise SystemExit(f"Missing {STEP03}")
    shutil.copy2(STEP03, STEP04_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP04_DOCX))
        results_probe = "Table 2 shows learner-based AUC"
        if results_probe not in doc.Content.Text:
            raise RuntimeError("Results probe missing before edit")

        ia = find_para(doc, "Abstract")
        p = doc.Paragraphs(ia)
        try:
            p.Style = "Abstract"
        except Exception:
            pass
        set_para_text(p, "Abstract—" + ABSTRACT_BODY)
        p.Alignment = WD_ALIGN_JUSTIFY
        style_abstract(p)

        body = doc.Content.Text
        checks = {
            "bounded_claim": "Lower KC training frequency does not universally degrade discrimination, but calibration can become less reliable in some sparse-concept regimes."
            in body,
            "ece_dense": "0.114" in body,
            "ece_sparse": "0.228" in body,
            "N415": "415" in body,
            "simulated_gate": "This is a simulated decision gate, not a classroom intervention."
            in body,
            "false_advance": "false-advance rate" in body,
            "no_gt_non_mastery": "ground-truth non-mastery" not in body,
            "no_gkt": "GKT" not in body.split("Abstract")[1].split("Keywords")[0]
            if "Keywords" in body
            else "GKT" not in ABSTRACT_BODY,
            "stratum": "KC-frequency stratum" in body,
            "results_untouched": results_probe in body,
            "one_abstract": body.count("Abstract—") + body.count("Abstract-") >= 1,
        }
        # GKT may still appear in Results; that is allowed. Check Abstract paragraph only.
        abs_text = p.Range.Text
        checks["gkt_in_abstract"] = "GKT" in abs_text or "graph KT" in abs_text.lower()
        checks["universal_cal_fail"] = "always" in abs_text.lower() and "calibrat" in abs_text.lower()

        lines.append(f"ABSTRACT={abs_text.strip()[:500]}")
        lines.append(f"ABS_LEN={len(ABSTRACT_BODY)}")
        for k, v in checks.items():
            lines.append(f"{k}={v}")

        if not checks["bounded_claim"]:
            raise RuntimeError("bounded claim missing")
        if not checks["simulated_gate"]:
            raise RuntimeError("simulated-gate sentence missing")
        if checks["gkt_in_abstract"]:
            raise RuntimeError("GKT still in Abstract")
        if not checks["results_untouched"]:
            raise RuntimeError("Results probe disappeared")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(f"PAGES={pages} WORDS={words}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP04_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP04_DOC), WD_FORMAT_DOC)
        doc.ExportAsFixedFormat(
            str(OUT_PDF),
            17,
            OpenAfterExport=False,
            OptimizeFor=0,
            Item=0,
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
        )
        lines.append(f"PDF_EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}")
    finally:
        if doc is not None:
            doc.Close(WD_SAVE)
        word.Quit()

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.read_text(encoding="utf-8"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
