#!/usr/bin/env python3
"""IJIET-11: Section IV order A–E and claim-consistent wording."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP10 = SRC / "main_ijiet_step10.docx"
STEP11_DOCX = SRC / "main_ijiet_step11.docx"
STEP11_DOC = SRC / "main_ijiet_step11.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step11.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step11_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_START = 1

HEAD_A = "A. Aggregate discrimination"
HEAD_B = "B. Calibration across frequency strata"
HEAD_C = "C. Threshold-based decision error"
HEAD_D = "D. Dataset-dependent explanatory analysis"
HEAD_E = "E. Exploratory GKT/CL4KT result"
HEAD_F = "F. What this paper does not show"
HEAD_G = "G. Implications for information and education technology"

PARA_A1 = (
    "Table 2 reports overall learner-based area under the ROC curve (AUC) and "
    "accuracy (ACC), mean±sd over four unique partitions. This subsection is "
    "discrimination, not calibration. DKT is slightly above SimpleKT on all three "
    "datasets (ASSISTments DKT 0.6979±0.0014 versus SimpleKT 0.6837±0.0025). IRT "
    "AUC is 0.5000 because unseen test learners have no ability parameter; it is "
    "a base-rate reference, not a ranking competitor."
)
PARA_A2 = (
    "On XES3G5M, sparse-stratum AUC is higher than dense-stratum AUC (DKT 0.857 "
    "versus 0.817; SimpleKT 0.847 versus 0.755; Reliable occupancy). Lower "
    "training frequency is therefore not a universal ranking failure. Junyi’s "
    "learner-based sparse bucket is empty under the pre-registered cuts—a "
    "protocol outcome, not a missing cell and not a zero-ECE claim."
)
PARA_B1 = (
    "Table 3 reports event-level expected calibration error (ECE), not AUC. On "
    "ASSISTments 2012, SimpleKT ECE increases from 0.1136±0.0066 (dense, Reliable, "
    "N=523,971) to 0.1541±0.0051 (medium) to 0.2280±0.0197 (sparse, Limited, "
    "N=415). That sparse cell is Limited support, not a high-N finding. DKT moves "
    "in the same direction on this dataset (dense 0.0602±0.0022 versus sparse "
    "0.2333±0.0084). IRT dense ECE is 0.0031±0.0006, but resolution is zero: a "
    "near-constant predictor can look calibrated while ranking nothing."
)
PARA_B2 = (
    "Calibration does not universally worsen. On Junyi Academy the learner-based "
    "sparse bucket is empty; only dense and medium exist, and SimpleKT ECE rises "
    "from 0.0792±0.0051 to 0.1073±0.0156. On XES3G5M, SimpleKT ECE is a "
    "counter-pattern: essentially flat from dense to sparse (0.1145, 0.1114, "
    "0.1248) despite Reliable sparse occupancy (N=2,010). A flat ECE is not a "
    "license to skip occupancy reporting and is not the same as a flat miss rate."
)
PARA_C1 = (
    "Table 4 is a simulated gate at τ=0.7 on ASSISTments 2012 fold 0 (seed 42), "
    "not a classroom trial. For SimpleKT, false-advance rate (FAR) is 0.196 "
    "[0.186, 0.208] on dense KCs (N=528,018; N_advance=284,326; N_incorrect="
    "158,623; E[FAR]=0.113; Excess FAR=0.083; Miss=0.352) and 0.268 [0.202, 0.337] "
    "on sparse KCs (N=444, Limited; N_advance=235; N_incorrect=197; E[FAR]=0.050; "
    "Excess FAR=0.218; Miss=0.320). ΔFAR=+0.072. DKT FAR is 0.200 [0.190, 0.211] "
    "dense and 0.296 [0.221, 0.383] sparse. Exploratory GKT/CL4KT rows of the same "
    "table are discussed in subsection E, not as main-model findings."
)
PARA_C2 = (
    "Table 5 checks whether SimpleKT ΔFAR is a one-fold accident. It is positive "
    "in all five training runs spanning four unique student partitions (mean 0.047, "
    "sd 0.033). Mean sparse denominators are N=413, N_advance=227, N_incorrect=155. "
    "A KC-clustered bootstrap on seed 42 yields a 95% interval [0.006, 0.138] for "
    "ΔFAR—excluding 0, but wide, as Limited occupancy and N_advance=235 require. "
    "DKT ΔFAR is positive on only three of five runs and is not treated as a "
    "five-run finding. On XES3G5M, SimpleKT ΔFAR is negative on all five runs, but "
    "ΔMiss is positive on all five (mean +0.112): among actual incorrect answers, "
    "the system still advances more often on sparse than on dense KCs."
)
PARA_E = (
    "GKT (a train-only graph) and a CL4KT protocol adapter are scored only on "
    "ASSISTments 2012 fold 0 (seed 42). They are exploratory, single-fold, "
    "ASSISTments-only instantiations: not a state-of-the-art comparison, not a "
    "proposed method, and not an official CL4KT checkpoint. Table 4: GKT FAR is "
    "0.205 [0.194, 0.217] dense versus 0.220 [0.149, 0.295] sparse (ΔFAR=+0.015; "
    "95% CI [−0.054, 0.092] includes 0). The CL4KT adapter FAR is 0.185 "
    "[0.176, 0.194] versus 0.240 [0.159, 0.330] (ΔFAR 95% CI [−0.018, 0.142] "
    "includes 0). A CI that includes 0 is not evidence that either architecture "
    "is safer in production."
)

BODY_NORMAL = (
    "Table 6 records",
    "Sparse mass (share of KCs",
    "A test-event-weighted KC-level",
    "Within-KC controlled sparsification",
    "Table 7.",
)


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


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
            target = "IV. RESULT AND DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "V. CONCLUSION"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            lines.append(f"H1_FIX {raw!r} -> {target}")


def main() -> None:
    if not STEP10.exists():
        raise SystemExit(f"Missing {STEP10}")
    shutil.copy2(STEP10, STEP11_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP11_DOCX))
        if "Table 2 shows learner-based AUC" not in doc.Content.Text and (
            "Table 2 reports overall learner-based" not in doc.Content.Text
        ):
            # probe may still be the old sentence before rewrite
            pass
        if "Table 2" not in doc.Content.Text:
            raise RuntimeError("Table 2 missing")

        # Heading and body rewrites in one pass (indices stable if we only replace text).
        delete_i = None
        insert_e_at = None
        for i in range(1, doc.Paragraphs.Count + 1):
            raw = para_text(doc.Paragraphs(i))
            if raw.startswith("Aggregate Ranking") or "Aggregate Ranking Is Not" in raw:
                force_h2(doc.Paragraphs(i), HEAD_A)
            elif raw.startswith("Calibration Can Move") or (
                "Calibration Can Move When Ranking" in raw
            ):
                force_h2(doc.Paragraphs(i), HEAD_B)
            elif "Global Gate Can Turn" in raw or raw.startswith(
                "C. Threshold-based decision error"
            ):
                force_h2(doc.Paragraphs(i), HEAD_C)
            elif "What a Designer Should Take Away" in raw:
                force_h2(doc.Paragraphs(i), HEAD_D)
            elif raw.strip() in {
                "Explanatory Analysis of Dataset-Dependent Calibration",
                "B. Explanatory Analysis of Dataset-Dependent Calibration",
            } or raw.startswith("Explanatory Analysis of Dataset-Dependent"):
                delete_i = i
            elif "What This Paper Does Not Show" in raw:
                insert_e_at = i
                force_h2(doc.Paragraphs(i), HEAD_F)
            elif "Implications for Information and Education" in raw:
                force_h2(doc.Paragraphs(i), HEAD_G)
            elif raw.startswith("Table 2 shows learner-based AUC"):
                set_para_text(doc.Paragraphs(i), PARA_A1)
            elif raw.startswith("On XES3G5M, sparse AUC is higher"):
                set_para_text(doc.Paragraphs(i), PARA_A2)
            elif raw.startswith("Table 3 is the calibration punchline"):
                set_para_text(doc.Paragraphs(i), PARA_B1)
            elif raw.startswith("On Junyi, only dense and medium"):
                set_para_text(doc.Paragraphs(i), PARA_B2)
            elif raw.startswith("Table 4 applies"):
                set_para_text(doc.Paragraphs(i), PARA_C1)
            elif raw.startswith("Table 5 checks whether SimpleKT"):
                set_para_text(doc.Paragraphs(i), PARA_C2)
            elif "5/5 seeds" in raw:
                set_para_text(
                    doc.Paragraphs(i),
                    raw.replace(
                        "5/5 seeds",
                        "five training runs spanning four unique student partitions",
                    ),
                )
            elif "ΔFAR>0 on 5/5 training runs across four unique learner partitions" in raw:
                set_para_text(
                    doc.Paragraphs(i),
                    raw.replace(
                        "ΔFAR>0 on 5/5 training runs across four unique learner partitions",
                        "ΔFAR positive in all five training runs spanning four unique student partitions",
                    ),
                )
            elif raw.startswith(BODY_NORMAL):
                try:
                    doc.Paragraphs(i).Style = "Normal"
                except Exception:
                    pass

        if delete_i is not None:
            doc.Paragraphs(delete_i).Range.Delete()
            lines.append(f"DELETED_DUP_HEADING={delete_i}")
            if insert_e_at is not None and insert_e_at > delete_i:
                insert_e_at -= 1

        # Re-find F heading after possible delete.
        insert_e_at = None
        for i in range(1, doc.Paragraphs.Count + 1):
            if para_text(doc.Paragraphs(i)).startswith("F. What this paper does not show"):
                insert_e_at = i
                break
        if insert_e_at is None:
            raise RuntimeError("F heading missing after rewrite")

        doc.Paragraphs(insert_e_at).Range.InsertParagraphBefore()
        set_para_text(doc.Paragraphs(insert_e_at), PARA_E)
        try:
            doc.Paragraphs(insert_e_at).Style = "Normal"
        except Exception:
            pass
        doc.Paragraphs(insert_e_at).Range.InsertParagraphBefore()
        force_h2(doc.Paragraphs(insert_e_at), HEAD_E)
        lines.append(f"INSERTED_E_AT={insert_e_at}")

        restore_h1(doc, lines)
        neutralize_table_lists(doc)

        full = doc.Content.Text
        checks = {
            "head_a": HEAD_A in full,
            "head_b": HEAD_B in full,
            "head_c": HEAD_C in full,
            "head_d": HEAD_D in full,
            "head_e": HEAD_E in full,
            "no_old_agg": "Aggregate Ranking Is Not the Sparse Story" not in full,
            "no_univ_auc": "universal ranking failure" in full,
            "empty_not_zero": "not a zero-ECE claim" in full,
            "limited": "Limited, N=415" in full or "Limited, N=415" in full.replace(" ", ""),
            "limited2": "Limited support" in full,
            "counter": "counter-pattern" in full,
            "five_runs_phrase": "positive in all five training runs spanning four unique student partitions"
            in full,
            "no_55_seeds": "5/5 seeds" not in full,
            "gkt_exploratory": "not a state-of-the-art comparison" in full,
            "far_denoms": "N_advance=284,326" in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "t2": "Table 2." in full,
            "t7": "Table 7." in full,
            "h1_iv": "IV. RESULT AND DISCUSSION" in full,
            "h1_v": "V. CONCLUSION" in full,
        }
        # Limited N=415 with various spacing
        checks["limited"] = "Limited, N=415" in full or "Limited, N=415" in full
        if "Limited, N=415" not in full and "Limited, N=415" not in full:
            checks["limited"] = "N=415" in full and "Limited" in full
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
        doc.SaveAs2(str(STEP11_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP11_DOC), WD_FORMAT_DOC)
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
