#!/usr/bin/env python3
"""IJIET-12: rewrite Discussion (V) and Conclusion (VI)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP11 = SRC / "main_ijiet_step11.docx"
STEP12_DOCX = SRC / "main_ijiet_step12.docx"
STEP12_DOC = SRC / "main_ijiet_step12.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step12.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step12_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

HEAD_IV = "IV. RESULT"
HEAD_V = "V. DISCUSSION"
HEAD_VI = "VI. CONCLUSION"
HEAD_A = "A. Main empirical findings"
HEAD_B = "B. Practical implications for educational technology"
HEAD_C = "C. Why datasets differ"
HEAD_D = "D. Limitations"

PARA_A = (
    "Three empirical regularities, not laws, structure the results. First, "
    "training frequency is not a universal predictor of AUC failure: on XES3G5M, "
    "sparse-stratum AUC is higher than dense-stratum AUC for DKT and SimpleKT "
    "(Reliable occupancy), and Junyi’s learner-based sparse bucket is empty rather "
    "than a ranking collapse. Second, calibration vulnerability is "
    "dataset-dependent. ASSISTments 2012 SimpleKT ECE is associated with a "
    "dense-to-sparse rise under Limited sparse support (Table 3, N=415); XES3G5M "
    "SimpleKT ECE is a counter-pattern that stays essentially flat despite Reliable "
    "sparse occupancy. Calibration is not guaranteed to worsen as frequency falls. "
    "Third, threshold behavior can differ by frequency stratum. The simulated "
    "ASSISTments gate (Tables 4–5) can raise SimpleKT FAR on sparse KCs relative to "
    "dense KCs, with ΔFAR positive in all five training runs spanning four unique "
    "student partitions; on XES3G5M, ΔFAR and ΔMiss can move in opposite directions, "
    "so a flat ECE is not a flat miss rate."
)
PARA_B = (
    "Before using one global KT probability threshold for remediation or "
    "advancement, four checks are warranted under the evaluated conditions: "
    "(i) inspect KC-frequency occupancy on the training fold actually used, "
    "including empty buckets; (ii) evaluate per-stratum calibration separately from "
    "AUC; (iii) evaluate threshold-error metrics (FAR, expected FAR, Excess FAR, "
    "and Miss) with their denominators; (iv) ensure sufficient sample support "
    "before treating a slice as actionable. R/L/I flags are descriptive occupancy "
    "labels, not inferential guarantees. A population AUC win, or an exploratory "
    "GKT/CL4KT run, is not by itself evidence that a global gate is safer on the "
    "tail."
)
PARA_C = (
    "The three logs differ on measured structural descriptors (Table 6): sparse "
    "mass 18.9%, 0%, and 22.5% of KCs; sparse test support Limited (N=415), empty, "
    "and Reliable (N=2,010); frequency–difficulty Spearman ρ=−0.227, −0.416, and "
    "+0.087. Item support is also heterogeneous (median items per KC 44.5, 18, and "
    "3). A curriculum-position proxy (median normalized sequence position) yields "
    "ρ=−0.308, −0.324, and −0.125. Within-KC sparsification (Table 7) does not "
    "reproduce the observational ASSISTments SimpleKT ECE gradient. These are "
    "associations on these datasets. Untested explanations—curriculum hierarchy, "
    "tagging granularity, ceiling effects, and item semantics—are hypotheses unless "
    "experimentally isolated, which this study does not do."
)
PARA_D = (
    "Next-response correctness is not latent mastery: y=0 is an incorrect next "
    "attempt, not a latent-skill diagnosis. The threshold gate is simulated at a "
    "locked τ and is not a classroom policy. There is no classroom RCT. GKT and the "
    "CL4KT adapter are exploratory, single-fold, ASSISTments-only instantiations, "
    "not a state-of-the-art comparison. Temporal evaluation uses a single corrected "
    "cutoff (seed 42), not a multi-cutoff variance estimate. Main multi-run "
    "summaries use only four unique learner partitions (seeds 2025 and 2026 share a "
    "split). R/L/I are descriptive support flags. ECE depends on binning. Three "
    "datasets cannot establish a universal diagnostic law."
)
PARA_CONC = (
    "Under the evaluated conditions, KT probabilities that look adequate on "
    "aggregate AUC can still be poorly calibrated on sparse KCs in some "
    "dataset-model settings, and a global threshold can then raise the "
    "false-advance rate on those skills. That association appears for SimpleKT on "
    "ASSISTments 2012 (Limited sparse support). It is not reported for Junyi’s empty "
    "learner-based sparse bucket, and XES3G5M SimpleKT ECE remains essentially flat. "
    "Sparse-concept occupancy, calibration, and threshold-error checks are therefore "
    "conditionally useful for educational-technology gates. This paper is a "
    "simulated decision-error check, not a new KT model and not a classroom "
    "intervention."
)


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def force_h1(para, title: str) -> None:
    para.Style = "Heading 1"
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)
    para.Style = "Heading 1"
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)


def force_h2(para, title: str) -> None:
    para.Style = "Heading 2"
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)
    para.Style = "Heading 2"
    try:
        para.Range.ListFormat.RemoveNumbers()
    except Exception:
        pass
    set_para_text(para, title)


def force_normal(para, text: str) -> None:
    set_para_text(para, text)
    try:
        para.Style = "Normal"
    except Exception:
        pass
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
        if "RESULT AND DISCUSSION" in up:
            target = HEAD_IV
        elif up.startswith("IV.") and "RESULT" in up:
            target = HEAD_IV
        elif "DISCUSSION" in up and "RESULT" not in up:
            target = HEAD_V
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = HEAD_VI
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            lines.append(f"H1_FIX {raw!r} -> {target}")


def find_heading(doc, *needles: str) -> int | None:
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if any(n in raw for n in needles):
            return i
    return None


def insert_blocks_before(doc, ti: int, blocks: list[tuple[str, bool]]) -> None:
    for text, is_h2 in blocks:
        doc.Paragraphs(ti).Range.InsertParagraphBefore()
        if is_h2:
            force_h2(doc.Paragraphs(ti), text)
        else:
            force_normal(doc.Paragraphs(ti), text)
        ti += 1


def conclusion_slice(full: str) -> str:
    up = full.upper()
    i = up.find("VI. CONCLUSION")
    if i < 0:
        i = up.find("V. CONCLUSION")
    j = up.find("CONFLICT OF INTEREST")
    if i < 0 or j < 0 or j <= i:
        return ""
    return full[i:j]


def main() -> None:
    if not STEP11.exists():
        raise SystemExit(f"Missing {STEP11}")
    shutil.copy2(STEP11, STEP12_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP12_DOCX))
        if "Table 2 reports overall learner-based" not in doc.Content.Text:
            raise RuntimeError("Results probe missing")

        for i in range(1, doc.Paragraphs.Count + 1):
            raw = para_text(doc.Paragraphs(i))
            up = raw.upper()
            if "RESULT AND DISCUSSION" in up:
                force_h1(doc.Paragraphs(i), HEAD_IV)
            elif raw.startswith("F. What this paper does not show") or (
                "What This Paper Does Not Show" in raw
                or raw.startswith("What this paper does not show")
            ):
                force_h1(doc.Paragraphs(i), HEAD_V)
            elif raw.startswith("The gate is not a classroom"):
                force_h2(doc.Paragraphs(i), HEAD_A)
            elif raw.startswith("G. Implications") or (
                "Implications for Information and Education" in raw
                or raw.startswith("Implications for information")
            ):
                force_normal(doc.Paragraphs(i), PARA_A)
            elif raw.startswith("IJIET") and "operational recommendation" in raw:
                force_h2(doc.Paragraphs(i), HEAD_B)
            elif ("CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up
                  and len(raw) < 40):
                force_h1(doc.Paragraphs(i), HEAD_VI)
            elif raw.startswith("KT models that look adequate"):
                force_normal(doc.Paragraphs(i), PARA_CONC)

        ti = find_heading(doc, HEAD_VI, "VI. CONCLUSION")
        if ti is None:
            raise RuntimeError("VI. CONCLUSION heading missing after rewrite")
        insert_blocks_before(
            doc,
            ti,
            [
                (PARA_B, False),
                (HEAD_C, True),
                (PARA_C, False),
                (HEAD_D, True),
                (PARA_D, False),
            ],
        )
        lines.append(f"INSERTED_BEFORE_CONCLUSION={ti}")

        restore_h1(doc, lines)
        neutralize_table_lists(doc)

        full = doc.Content.Text
        conc = conclusion_slice(full)
        conc_l = conc.lower()
        checks = {
            "head_iv": HEAD_IV in full,
            "no_iv_disc": "IV. RESULT AND DISCUSSION" not in full,
            "head_v": HEAD_V in full,
            "head_vi": HEAD_VI in full,
            "head_a": HEAD_A in full,
            "head_b": HEAD_B in full,
            "head_c": HEAD_C in full,
            "head_d": HEAD_D in full,
            "no_old_f": "F. What this paper does not show" not in full,
            "no_old_g": "G. Implications for information and education technology"
            not in full,
            "auc_not_universal": "not a universal predictor of AUC failure" in full,
            "calib_dep": "calibration vulnerability is dataset-dependent" in full,
            "threshold_differs": "threshold behavior can differ by frequency stratum"
            in full,
            "occupancy": "inspect KC-frequency occupancy" in full,
            "per_stratum": "evaluate per-stratum calibration" in full,
            "threshold_metrics": "evaluate threshold-error metrics" in full,
            "sample_support": "ensure sufficient sample support" in full,
            "hypotheses": "are hypotheses unless" in full,
            "hierarchy": "curriculum hierarchy" in full,
            "tagging": "tagging granularity" in full,
            "ceiling": "ceiling effects" in full,
            "semantics": "item semantics" in full,
            "not_mastery": "not latent mastery" in full,
            "simulated": "threshold gate is simulated" in full,
            "no_rct": "no classroom RCT" in full,
            "gkt_expl": "exploratory, single-fold, ASSISTments-only" in full,
            "temporal_cutoff": "single corrected cutoff" in full,
            "four_part": "only four unique learner partitions" in full,
            "flags_desc": "descriptive support flags" in full,
            "ece_bin": "ECE depends on binning" in full,
            "no_law": "cannot establish a universal diagnostic law" in full,
            "conc_under": "Under the evaluated conditions" in conc,
            "conc_assoc": "association appears" in conc,
            "conc_can": " can " in conc,
            "conc_settings": "in some dataset-model settings" in conc,
            "conc_no_proves": "proves" not in conc_l,
            "conc_no_causes": "causes" not in conc_l,
            "conc_no_always": "always" not in conc_l,
            "conc_no_univ": "universally" not in conc_l,
            "five_runs": "five training runs spanning four unique student partitions"
            in full,
            "no_55_seeds": "5/5 seeds" not in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "empty_not_zero": "not a zero-ECE claim" in full,
            "counter": "counter-pattern" in full,
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
        doc.SaveAs2(str(STEP12_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP12_DOC), WD_FORMAT_DOC)
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
