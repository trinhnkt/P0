#!/usr/bin/env python3
"""IJIET-02: copy a clean working branch and strip publisher metadata.

Does not modify originals under ijiet/, paper/, or REV_REVIEWER_CALIBRATION_v1/.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT / "IJIET_SUBMISSION"
SRC = SUB / "source"

ORIG_DOCX = (
    ROOT
    / "ijiet"
    / "Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx"
)
ORIG_DOC = (
    ROOT
    / "ijiet"
    / "Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.doc"
)
TEMPLATE_DOC = SUB / "audit" / "IJIET_template.doc"
BIB = ROOT / "paper" / "references.bib"
FIG_PNG = SUB / "figures" / "figure2_bucket_distribution.png"
FIG_PDF = ROOT / "paper" / "figures" / "figure2_bucket_distribution.pdf"

WORK_DOCX = SRC / "main_ijiet_step02.docx"
WORK_DOC = SRC / "main_ijiet_step02.doc"
OUT_PDF = SUB / "output" / "main_ijiet_step02.pdf"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_FORMAT_PDF = 17
WD_SAVE = -1
WD_DO_NOT_SAVE = 0
WD_SEEK_MAIN = 0
WD_SEEK_PRIMARY = 1
WD_HEADER_PRIMARY = 1
WD_HEADER_FIRST = 2
WD_HEADER_EVEN = 3
WD_ALIGN_CENTER = 1


def copy_assets() -> list[str]:
    copied = []
    (SRC / "template").mkdir(parents=True, exist_ok=True)
    (SRC / "figures").mkdir(parents=True, exist_ok=True)
    (SRC / "bibliography").mkdir(parents=True, exist_ok=True)
    (SUB / "output").mkdir(parents=True, exist_ok=True)

    shutil.copy2(ORIG_DOCX, WORK_DOCX)
    copied.append(f"{ORIG_DOCX.name} -> source/main_ijiet_step02.docx")

    if ORIG_DOC.exists():
        shutil.copy2(ORIG_DOC, WORK_DOC)
        copied.append(f"{ORIG_DOC.name} -> source/main_ijiet_step02.doc (pre-clean copy)")

    if TEMPLATE_DOC.exists():
        dest = SRC / "template" / "IJIET_template.doc"
        shutil.copy2(TEMPLATE_DOC, dest)
        copied.append("audit/IJIET_template.doc -> source/template/IJIET_template.doc")

    if BIB.exists():
        shutil.copy2(BIB, SRC / "bibliography" / "references.bib")
        copied.append("paper/references.bib -> source/bibliography/references.bib")

    if FIG_PNG.exists():
        shutil.copy2(FIG_PNG, SRC / "figures" / "figure2_bucket_distribution.png")
        copied.append("figures/figure2_bucket_distribution.png -> source/figures/")

    if FIG_PDF.exists():
        shutil.copy2(FIG_PDF, SRC / "figures" / "figure2_bucket_distribution.pdf")
        copied.append("paper/figures/figure2_bucket_distribution.pdf -> source/figures/")

    return copied


def clear_headers_footers(doc) -> list[str]:
    actions = []
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        for header_idx in (1, 2, 3):
            try:
                hdr = sec.Headers(header_idx)
                hdr.LinkToPrevious = False
                hdr.Range.Text = ""
            except Exception:
                pass
            try:
                ftr = sec.Footers(header_idx)
                ftr.LinkToPrevious = False
                ftr.Range.Text = ""
            except Exception:
                pass
        try:
            sec.PageSetup.DifferentFirstPageHeaderFooter = False
            sec.PageSetup.OddAndEvenPagesHeaderFooter = False
        except Exception:
            pass
        actions.append(f"section {s}: headers/footers cleared")
    return actions


def delete_paras_containing(doc, needles: list[str]) -> list[str]:
    removed = []
    # Walk backwards so indices stay valid.
    for i in range(doc.Paragraphs.Count, 0, -1):
        text = doc.Paragraphs(i).Range.Text
        if any(n.lower() in text.lower() for n in needles):
            snippet = text.strip().replace("\r", " ")[:90]
            doc.Paragraphs(i).Range.Delete()
            removed.append(snippet)
    return removed


def find_hits(doc, needles: list[str]) -> dict[str, bool]:
    out = {}
    for n in needles:
        f = doc.Content.Find
        f.ClearFormatting()
        out[n] = bool(f.Execute(n))
    return out


def clean_and_compile() -> dict:
    report = {
        "removed_paras": [],
        "header_actions": [],
        "hits_before": {},
        "hits_after": {},
        "pages": None,
        "words": None,
        "pdf": str(OUT_PDF),
        "warnings": [],
    }
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(WORK_DOCX))
        report["hits_before"] = find_hits(
            doc,
            [
                "Manuscript received",
                "International Journal of Information",
                "INTERNATIONAL JOURNAL",
                "10.18178",
                "doi:",
                "DOI",
                "Vol.",
                "No.",
            ],
        )
        report["header_actions"] = clear_headers_footers(doc)
        report["removed_paras"] = delete_paras_containing(
            doc,
            [
                "Manuscript received",
                "revised Month",
                "accepted Month date",
            ],
        )
        # Strip PAGE fields if any remain in story ranges.
        try:
            for fld in list(doc.Fields):
                code = str(fld.Code.Text).upper()
                if "PAGE" in code or "NUMPAGES" in code:
                    fld.Delete()
                    report["header_actions"].append("deleted PAGE/NUMPAGES field")
        except Exception as exc:
            report["warnings"].append(f"field sweep: {exc}")

        doc.Fields.Update()
        report["hits_after"] = find_hits(
            doc,
            [
                "Manuscript received",
                "International Journal of Information",
                "INTERNATIONAL JOURNAL",
                "10.18178",
                "doi:",
                "Vol. 16",
            ],
        )
        report["pages"] = doc.ComputeStatistics(2)
        report["words"] = doc.ComputeStatistics(0)

        title = doc.Paragraphs(1).Range.Text.strip()
        if "Sparse-Concept" not in title and "Knowledge Tracing" not in title:
            report["warnings"].append(f"unexpected title after clean: {title[:80]!r}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(WORK_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(WORK_DOC), WD_FORMAT_DOC)
        doc.ExportAsFixedFormat(
            str(OUT_PDF),
            17,  # wdExportFormatPDF
            OpenAfterExport=False,
            OptimizeFor=0,  # wdExportOptimizeForPrint
            Item=0,  # wdExportDocumentContent
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
        )
    finally:
        if doc is not None:
            doc.Close(WD_SAVE)
        word.Quit()
    return report


def main() -> None:
    if not ORIG_DOCX.exists():
        raise SystemExit(f"Missing original manuscript: {ORIG_DOCX}")
    copied = copy_assets()
    report = clean_and_compile()
    report["copied"] = copied
    # Write a machine-readable stub the changelog can quote.
    stub = SRC / "_step02_report.txt"
    lines = ["COPIED"]
    lines.extend(copied)
    lines.append("REMOVED_PARAS")
    lines.extend(report["removed_paras"] or ["(none)"])
    lines.append("HITS_BEFORE")
    lines.extend(f"{k}={v}" for k, v in report["hits_before"].items())
    lines.append("HITS_AFTER")
    lines.extend(f"{k}={v}" for k, v in report["hits_after"].items())
    lines.append(f"PAGES={report['pages']}")
    lines.append(f"WORDS={report['words']}")
    lines.append(f"PDF_EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}")
    lines.append("WARNINGS")
    lines.extend(report["warnings"] or ["(none)"])
    stub.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(stub.read_text(encoding="utf-8"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
