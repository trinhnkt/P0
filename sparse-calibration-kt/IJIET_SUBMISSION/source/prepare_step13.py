#!/usr/bin/env python3
"""IJIET-13: required end matter (policy-audited; no invented IRB)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP12 = SRC / "main_ijiet_step12.docx"
STEP13_DOCX = SRC / "main_ijiet_step13.docx"
STEP13_DOC = SRC / "main_ijiet_step13.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step13.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step13_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

HEAD_COI = "Conflict of Interest"
HEAD_AUTH = "Author Contributions"
HEAD_ETHICS = "Ethical Statement"
HEAD_DATA = "Data and Code Availability"
HEAD_AI = "Generative AI Statement"
HEAD_ACK = "Acknowledgment"

PARA_COI = "The authors declare no conflict of interest."
PARA_AUTH = (
    "K.-T.N.: Conceptualization, Methodology, Software, Formal analysis, and "
    "Writing (led diagnostic design, experiments, and manuscript). T.D.M. and "
    "D.N.T.: Software (data processing and baseline runs). C.T.N.: Methodology "
    "(methodological review). V.-H.N.: Supervision and Writing (manuscript "
    "revision). All authors approved the final version."
)
PARA_ETHICS = (
    "This study is a secondary analysis of publicly released benchmark educational "
    "datasets (ASSISTments 2012, Junyi Academy, and XES3G5M). The processed records "
    "used here are de-identified. No new participants were recruited, and no "
    "intervention was conducted. [AUTHOR ACTION REQUIRED: verify institutional "
    "ethics/exemption wording]"
)
PARA_DATA = (
    "Anonymized code, data-preprocessing scripts, and evaluation pipelines are "
    "available for peer review at "
    "https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/. "
    "Source benchmark datasets are publicly released by their original providers. "
    "A public repository will be released upon acceptance."
)
PARA_AI = (
    "During manuscript preparation, the authors used ChatGPT [version to be "
    "confirmed], Claude [version to be confirmed], and Google Antigravity "
    "[version to be confirmed] to support language polishing, formatting, "
    "consistency checking, and reproducibility prompt preparation. These tools "
    "were not used to fabricate or alter experimental results. After using these "
    "tools, the authors reviewed and edited the content. The authors remain "
    "responsible for all content. Generative AI is not listed as a co-author."
)
PARA_ACK = (
    "This work was supported by the authors’ respective institutions."
)


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def force_refhead(para, title: str) -> None:
    try:
        para.Style = "Reference Head"
    except Exception:
        para.Style = "Heading 1"
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)
    try:
        para.Style = "Reference Head"
    except Exception:
        pass
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)


def force_text(para, text: str) -> None:
    set_para_text(para, text)
    try:
        para.Style = "Text"
    except Exception:
        para.Style = "Normal"
    try:
        para.Range.ParagraphFormat.OutlineLevel = 10
    except Exception:
        pass


def neutralize_table_lists(doc) -> None:
    for ti in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(ti)
        for ri in range(1, tbl.Rows.Count + 1):
            for ci in range(1, tbl.Columns.Count + 1):
                cell = tbl.Cell(ri, ci)
                try:
                    cell.Range.ListFormat.RemoveNumbers()
                except Exception:
                    pass
                try:
                    cell.Range.Style = "Normal"
                except Exception:
                    pass
                try:
                    cell.Range.ParagraphFormat.OutlineLevel = 10
                except Exception:
                    pass
                cell.Range.Font.Name = "Times New Roman"
                cell.Range.Font.Size = 7


def find_para(doc, needle: str) -> int | None:
    for i in range(1, doc.Paragraphs.Count + 1):
        if needle in para_text(doc.Paragraphs(i)):
            return i
    return None


def insert_before(doc, ti: int, blocks: list[tuple[str, bool]]) -> None:
    for text, is_head in blocks:
        doc.Paragraphs(ti).Range.InsertParagraphBefore()
        if is_head:
            force_refhead(doc.Paragraphs(ti), text)
        else:
            force_text(doc.Paragraphs(ti), text)
        ti += 1


def restore_h1(doc, lines) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        try:
            style = str(doc.Paragraphs(i).Style.NameLocal)
        except Exception:
            continue
        if style != "Heading 1":
            continue
        raw = para_text(doc.Paragraphs(i))
        up = raw.upper()
        target = None
        if "RESULT AND DISCUSSION" in up or (
            up.startswith("IV.") and "RESULT" in up
        ):
            target = "IV. RESULT"
        elif "DISCUSSION" in up and "RESULT" not in up:
            target = "V. DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "VI. CONCLUSION"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            lines.append(f"H1_FIX {raw!r} -> {target}")


def main() -> None:
    if not STEP12.exists():
        raise SystemExit(f"Missing {STEP12}")
    shutil.copy2(STEP12, STEP13_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP13_DOCX))
        if PARA_COI not in doc.Content.Text:
            raise RuntimeError("Conflict-of-interest sentence missing")
        if find_para(doc, HEAD_ACK) is None:
            raise RuntimeError("Acknowledgment heading missing")

        for i in range(1, doc.Paragraphs.Count + 1):
            raw = para_text(doc.Paragraphs(i))
            if raw.startswith("K.-T.N. led the diagnostic design"):
                force_text(doc.Paragraphs(i), PARA_AUTH)
            elif raw.startswith("Anonymized code and prediction exports"):
                force_text(doc.Paragraphs(i), PARA_ACK)
            elif raw.strip() == HEAD_COI or raw.upper() == "CONFLICT OF INTEREST":
                force_refhead(doc.Paragraphs(i), HEAD_COI)
            elif raw.strip() == HEAD_AUTH or raw.upper() == "AUTHOR CONTRIBUTIONS":
                force_refhead(doc.Paragraphs(i), HEAD_AUTH)
            elif raw.strip() == HEAD_ACK or raw.upper() in {
                "ACKNOWLEDGMENT",
                "ACKNOWLEDGEMENT",
            }:
                force_refhead(doc.Paragraphs(i), HEAD_ACK)

        ti = find_para(doc, HEAD_ACK)
        if ti is None:
            raise RuntimeError("Acknowledgment heading missing after rewrite")
        insert_before(
            doc,
            ti,
            [
                (HEAD_ETHICS, True),
                (PARA_ETHICS, False),
                (HEAD_DATA, True),
                (PARA_DATA, False),
                (HEAD_AI, True),
                (PARA_AI, False),
            ],
        )
        lines.append(f"INSERTED_BEFORE_ACK={ti}")

        restore_h1(doc, lines)
        neutralize_table_lists(doc)

        full = doc.Content.Text
        ack_i = full.upper().find("ACKNOWLEDGMENT")
        ack_slice = full[ack_i : full.upper().find("REFERENCES")] if ack_i >= 0 else ""
        checks = {
            "coi": PARA_COI in full,
            "head_ethics": HEAD_ETHICS in full,
            "head_data": HEAD_DATA in full,
            "head_ai": HEAD_AI in full,
            "credit_concept": "Conceptualization" in full,
            "credit_method": "Methodology" in full,
            "credit_software": "Software" in full,
            "credit_formal": "Formal analysis" in full,
            "credit_writing": "Writing" in full,
            "credit_super": "Supervision" in full,
            "no_validation_role": "Validation" not in PARA_AUTH,
            "public_bench": "publicly released benchmark educational datasets" in full,
            "secondary": "secondary analysis" in full,
            "deident": "de-identified" in full,
            "no_new_p": "No new participants were recruited" in full,
            "no_interv": "no intervention was conducted" in full,
            "author_action": "[AUTHOR ACTION REQUIRED: verify institutional ethics/exemption wording]"
            in full,
            "no_irb_claim": "IRB approval was not required" not in full,
            "anon_url": "https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/"
            in full,
            "no_author_gh": "github.com/trinhnkt" not in full,
            "chatgpt": "ChatGPT [version to be confirmed]" in full,
            "claude": "Claude [version to be confirmed]" in full,
            "antigravity": "Google Antigravity [version to be confirmed]" in full,
            "polish": "language polishing" in full,
            "format": "formatting" in full,
            "consist": "consistency checking" in full,
            "prompts": "reproducibility prompt preparation" in full,
            "no_fabricate": "were not used to fabricate or alter experimental results"
            in full,
            "responsible": "remain responsible for all content" in full,
            "ack_inst": "authors’ respective institutions" in full
            or "authors' respective institutions" in full,
            "ack_no_url": "anonymous.4open.science" not in ack_slice,
            "conc_kept": "Under the evaluated conditions" in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "h1_iv": "IV. RESULT" in full,
            "h1_vi": "VI. CONCLUSION" in full,
        }
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} "
            f"PICS={doc.InlineShapes.Count}"
        )
        if doc.InlineShapes.Count != 1:
            raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")
        if doc.Tables.Count < 8:
            raise RuntimeError(f"expected >=8 tables, got {doc.Tables.Count}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP13_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP13_DOC), WD_FORMAT_DOC)
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
        lines.append(
            f"PDF_EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}"
        )
    except Exception:
        if lines:
            REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise
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
