#!/usr/bin/env python3
"""IJIET-05: revise Section I (Introduction) only."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP04 = SRC / "main_ijiet_step04.docx"
STEP05_DOCX = SRC / "main_ijiet_step05.docx"
STEP05_DOC = SRC / "main_ijiet_step05.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step05.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step05_verify.txt"

INTRO_PARAS = [
    "Adaptive practice platforms and intelligent tutoring systems use Knowledge Tracing (KT) to estimate a learner’s command of a skill and to decide whether to skip, remediate, or advance practice [1]–[3]. Those systems rarely consume a population area-under-the-curve (AUC) statistic. They consume a predicted probability p, which is then compared with a threshold τ. If p≥τ, the platform typically withholds additional practice on that skill. The operational chain is therefore population AUC → predicted probability → calibration → threshold-based educational decisions, with particular diagnostic risk on sparsely trained knowledge components (KCs).",
    "KT evaluations typically report population AUC and accuracy [4], [5]. Those metrics rank models, but they can conceal miscalibration on low-frequency KCs—skills with little training-fold evidence—because most test events lie on dense, frequently practiced concepts. A model can discriminate well in aggregate and still assign overconfident probabilities on the sparse tail. When a fixed threshold is applied to p, that overconfidence appears as an advance decision followed by an incorrect next response. We term this the false-advance rate (FAR). Section III defines FAR as P(y=0 | p≥τ); y denotes observed next-response correctness, not latent mastery truth.",
    "This paper treats that mismatch as an evaluation problem for educational technology, not as a reason to propose another KT architecture. The study is organized around three research questions. RQ1: Does lower KC training frequency systematically degrade predictive discrimination? RQ2: How does calibration vary across KC-frequency strata and datasets? RQ3: When a fixed probability threshold is applied, does decision-error behavior differ between sparse and dense KCs?",
    "The empirical answers are bounded. Lower KC training frequency does not universally degrade discrimination: on XES3G5M, sparse AUC is higher than dense AUC for DKT and SimpleKT. Calibration can, however, become less reliable in some sparse-concept regimes. On ASSISTments 2012, SimpleKT expected calibration error (ECE) increases from dense to sparse KCs, and a locked gate at τ=0.7 yields a higher FAR on sparse than on dense advances. The same ECE gradient is absent on Junyi, where the learner-based sparse stratum is empty, and is essentially absent for SimpleKT on XES3G5M. We therefore do not claim that sparse KCs always fail, and we do not claim a causal effect of training frequency on calibration.",
    "Contributions are conservative: (i) a train-only KC-frequency protocol with an explicit strict cold-start group, so the definition of “sparse” cannot leak test-fold counts; (ii) per-stratum calibration (ECE and Brier decomposition) on three public datasets, with occupancy flags (Reliable / Limited / Insufficient); (iii) a locked-threshold simulation of FAR and miss rates, with a five-seed check of the sparse–dense FAR gap on ASSISTments 2012. We do not propose a new KT architecture, a new calibration algorithm, or a new auditing theory, and we do not report a classroom intervention. A graph-KT (GKT) model and a CL4KT-style adapter appear only as an exploratory single-fold diagnostic on ASSISTments.",
]

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def find_heading(doc, name: str) -> int:
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        if p.Style.NameLocal == "Heading 1" and name.lower() in p.Range.Text.lower():
            return i
    raise RuntimeError(f"Heading 1 not found: {name}")


def main() -> None:
    if not STEP04.exists():
        raise SystemExit(f"Missing {STEP04}")
    shutil.copy2(STEP04, STEP05_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP05_DOCX))
        results_probe = "Table 2 shows learner-based AUC"
        if results_probe not in doc.Content.Text:
            raise RuntimeError("Results probe missing")

        intro_i = find_heading(doc, "Introduction")
        lit_i = find_heading(doc, "Literature Review")
        if lit_i <= intro_i + 1:
            raise RuntimeError("unexpected heading order")

        # Delete existing intro body (keep both headings).
        start = doc.Paragraphs(intro_i + 1).Range.Start
        end = doc.Paragraphs(lit_i).Range.Start
        doc.Range(start, end).Delete()

        lit_i = find_heading(doc, "Literature Review")
        # Insert new paragraphs immediately before Literature Review, in reverse.
        for text in reversed(INTRO_PARAS):
            doc.Paragraphs(lit_i).Range.InsertParagraphBefore()
            p = doc.Paragraphs(lit_i)
            try:
                p.Style = "Text"
            except Exception:
                pass
            set_para_text(p, text)
            lit_i = find_heading(doc, "Literature Review")

        body = doc.Content.Text
        checks = {
            "rq1": "RQ1:" in body and "systematically degrade predictive discrimination" in body,
            "rq2": "RQ2:" in body,
            "rq3": "RQ3:" in body,
            "far": "false-advance rate (FAR)" in body,
            "y_not_mastery": "not latent mastery" in body,
            "no_dirty": "dirty" not in body[body.find("Introduction") : body.find("Literature Review")].lower()
            if "Literature Review" in body
            else False,
            "no_dashboard": "wrong dashboard" not in body,
            "no_bakeoff": "bake-off" not in body,
            "no_new_arch": "do not propose a new KT architecture" in body,
            "no_causal": "do not claim a causal effect" in body,
            "results": results_probe in body,
            "gkt_exploratory": "exploratory single-fold diagnostic" in body,
        }
        intro_i = find_heading(doc, "Introduction")
        lit_i = find_heading(doc, "Literature Review")
        intro_text = doc.Range(
            doc.Paragraphs(intro_i).Range.Start,
            doc.Paragraphs(lit_i).Range.Start,
        ).Text
        checks["no_dirty"] = "dirty" not in intro_text.lower()
        checks["no_dashboard"] = "wrong dashboard" not in intro_text.lower()
        checks["no_bakeoff"] = "bake-off" not in intro_text.lower()
        checks["no_fm_term"] = "false mastery" not in intro_text.lower()
        checks["n_intro_body"] = lit_i - intro_i - 1

        lines.append(f"INTRO_BODY_PARAS={checks['n_intro_body']}")
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        if checks["n_intro_body"] != 5:
            raise RuntimeError(f"expected 5 intro paragraphs, got {checks['n_intro_body']}")
        if not checks["results"]:
            raise RuntimeError("Results changed or missing")
        if not checks["rq1"] or not checks["far"]:
            raise RuntimeError("RQ/FAR missing")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} PICS={doc.InlineShapes.Count}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP05_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP05_DOC), WD_FORMAT_DOC)
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
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
