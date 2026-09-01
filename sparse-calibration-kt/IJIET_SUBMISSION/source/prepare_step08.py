#!/usr/bin/env python3
"""IJIET-08: rename FM→FAR, add Excess FAR / denominators / recovered CIs.

Does not retune tau. Point estimates in Table 4/5 keep published 3-decimal rates.
Denominators and KC-cluster CIs recovered from prediction exports.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP07 = SRC / "main_ijiet_step07.docx"
STEP08_DOCX = SRC / "main_ijiet_step08.docx"
STEP08_DOC = SRC / "main_ijiet_step08.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step08.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step08_verify.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_START = 1
WD_ALIGN_CENTER = 1

GATE_DEF = (
    "Let A={p≥τ}. The false-advance rate (FAR) is P(y=0 | p≥τ): among responses "
    "for which the simulated system would advance the learner, the proportion whose "
    "observed next response is incorrect. This is not a measurement of latent mastery. "
    "It is a next-response decision-error proxy under a simulated threshold gate. "
    "Miss = P(p≥τ | y=0). Expected FAR under the model probabilities is "
    "E[1−p | p≥τ]. Excess FAR = FAR − E[1−p | p≥τ]. "
    "ΔFAR = FAR_sparse − FAR_dense. FAR is a proportion of N_advance = count(p≥τ) "
    "events, not of N_total; Miss is a proportion of N_incorrect = count(y=0). "
    "N_total alone does not imply the precision of FAR. Where prediction-level "
    "exports exist, 95% intervals use the KC-clustered percentile bootstrap already "
    "used for this gate (B=2000, resample KCs within sparse and within dense). "
    "Positive ΔFAR means sparse advances are dirtier than dense advances. This is a "
    "simulated decision error, not an instructional RCT."
)

RESULTS_C = (
    "Table 4 applies τ=0.7 on ASSISTments fold 0 (seed 42; sparse N_total=444, Limited). "
    "SimpleKT FAR is 0.196 on dense KCs and 0.268 on sparse KCs (ΔFAR=+0.072). "
    "The FAR denominator is N_advance (284,326 dense; 235 sparse), not N_total "
    "(528,018 and 444); N_incorrect is 158,623 dense and 197 sparse. Expected FAR "
    "on sparse advances is 0.050, so Excess FAR is 0.218. DKT shows a similar FAR gap. "
    "Train-only GKT shrinks ΔFAR to +0.015 (FAR 0.205→0.220; Excess FAR 0.063 on sparse). "
    "The CL4KT adapter is intermediate (0.185→0.240). We do not read this as “use GKT "
    "in production”; we read it as: the ASSISTments calibration gradient is not a "
    "property of the dataset alone."
)

RESULTS_C2A = (
    "Table 5 checks whether SimpleKT ΔFAR is a one-fold accident. It is positive on "
    "all five training seeds (mean 0.047, sd 0.033). Mean sparse denominators are "
    "N_total=413, N_advance=227, N_incorrect=155. A KC-clustered bootstrap on seed 42 "
    "yields a 95% interval [0.006, 0.138] for ΔFAR—excluding 0, but wide, as Limited "
    "occupancy and N_advance=235 require. DKT ΔFAR is positive on only three of five "
    "seeds and is not treated as a five-run finding. On XES3G5M, SimpleKT ΔFAR is "
    "negative on all five seeds, but ΔMiss is positive on all five (mean +0.112): "
    "among actual incorrect answers, the system still advances more often on sparse "
    "than on dense KCs. A flat ECE therefore does not imply a flat miss rate."
)

RESULTS_C2B = (
    "Coincidence of digits: SimpleKT dense E[FAR] at τ=0.7 on seed 42 is 0.113, close "
    "to the four-partition dense ECE 0.114. They are different quantities."
)

TABLE4_CAPTION = (
    "Table 4. Simulated gate at τ=0.7, ASSISTments 2012 fold 0. "
    "FAR=P(y=0 | p≥τ) among N_adv advances; Miss among N_inc incorrect responses. "
    "Not latent mastery; not a classroom trial."
)
TABLE4_HEADER = [
    "Model",
    "Stratum",
    "N",
    "N_adv",
    "N_inc",
    "FAR",
    "E[FAR]",
    "Excess",
    "Miss",
]
TABLE4_ROWS = [
    ["SimpleKT", "dense", "528,018", "284,326", "158,623", "0.196", "0.113", "0.083", "0.352"],
    ["SimpleKT", "sparse", "444", "235", "197", "0.268", "0.050", "0.218", "0.320"],
    ["DKT", "dense", "528,018", "315,650", "158,623", "0.200", "0.147", "0.053", "0.398"],
    ["DKT", "sparse", "444", "243", "197", "0.296", "0.057", "0.239", "0.365"],
    ["GKT (train-only)", "dense", "528,018", "351,503", "158,623", "0.205", "0.163", "0.042", "0.455"],
    ["GKT (train-only)", "sparse", "444", "209", "197", "0.220", "0.157", "0.063", "0.234"],
    ["CL4KT (adapter)", "dense", "528,018", "307,479", "158,623", "0.185", "0.175", "0.010", "0.359"],
    ["CL4KT (adapter)", "sparse", "444", "200", "197", "0.240", "0.116", "0.124", "0.244"],
]
TABLE4_NOTE = (
    "FAR 95% CIs (KC-cluster, B=2000): SimpleKT dense [0.186, 0.208], sparse [0.202, 0.337]; "
    "DKT dense [0.190, 0.211], sparse [0.221, 0.383]; GKT sparse [0.149, 0.295]; "
    "CL4KT sparse [0.159, 0.330]. Seed-42 ΔFAR CI: SimpleKT [0.006, 0.138] (locked C2); "
    "DKT [0.019, 0.175]; GKT [−0.054, 0.092]; CL4KT [−0.018, 0.142]."
)

TABLE5_CAPTION = (
    "Table 5. Gate robustness at τ=0.7 on ASSISTments 2012 (five training seeds; "
    "four unique partitions). ΔFAR=FAR_sparse−FAR_dense. Mean N, N_adv, and N_inc "
    "are sparse-stratum denominators. GKT/CL4KT remain seed 42 only."
)
TABLE5_HEADER = ["Model", "Mean ΔFAR", "SD", "Seeds >0", "Mean N", "Mean N_adv", "Mean N_inc"]
TABLE5_ROWS = [
    ["SimpleKT", "0.047", "0.033", "5/5", "413", "227", "155"],
    ["DKT", "0.033", "0.048", "3/5", "413", "226", "155"],
]

# Longer phrases first.
TEXT_REPLACEMENTS = [
    ("simulate FM and Miss", "simulate FAR and Miss"),
    ("seed-42 FM 0.196", "seed-42 FAR 0.196"),
    ("false mastery among advances", "false-advance rate among advances"),
    ("sparse–dense false-mastery gap", "sparse–dense false-advance gap"),
    ("false mastery and miss rates", "false-advance and miss rates"),
    ("higher false-mastery rate", "higher false-advance rate"),
    ("a higher false-mastery rate", "a higher false-advance rate"),
    ("false-mastery rate", "false-advance rate"),
    ("false-mastery error", "false-advance error"),
    ("false mastery (FM)", "false-advance rate (FAR)"),
    ("False mastery (FM)", "The false-advance rate (FAR)"),
    ("false mastery", "false-advance rate"),
    ("E[FM]", "E[FAR]"),
    ("ΔFM", "ΔFAR"),
    ("Mean ΔFM", "Mean ΔFAR"),
    ("FM_sparse", "FAR_sparse"),
    ("FM_dense", "FAR_dense"),
]


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def fill_table(table, header, rows) -> None:
    table.Style = "Table Grid"
    for j, h in enumerate(header, 1):
        table.Cell(1, j).Range.Text = h
        table.Cell(1, j).Range.Font.Bold = True
        table.Cell(1, j).Range.Font.Size = 7
        table.Cell(1, j).Range.Font.Name = "Times New Roman"
        table.Cell(1, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    for i, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            table.Cell(i, j).Range.Text = str(val)
            table.Cell(i, j).Range.Font.Bold = False
            table.Cell(i, j).Range.Font.Size = 7
            table.Cell(i, j).Range.Font.Name = "Times New Roman"
            table.Cell(i, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    try:
        table.AutoFitBehavior(2)
    except Exception:
        pass


def replace_table_by_caption(doc, old_caption_stub: str, new_caption: str, header, rows):
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if old_caption_stub in para_text(doc.Paragraphs(i)):
            cap_i = i
            break
    if cap_i is None:
        raise RuntimeError(f"caption not found: {old_caption_stub}")
    cap = doc.Paragraphs(cap_i)
    set_para_text(cap, new_caption)
    # Table immediately follows the caption paragraph.
    probe = doc.Range(cap.Range.End, cap.Range.End + 50)
    if probe.Tables.Count < 1:
        raise RuntimeError(f"no table after caption: {old_caption_stub}")
    old = probe.Tables(1)
    insert_at = old.Range.Start
    old.Delete()
    rng = doc.Range(insert_at, insert_at)
    table = doc.Tables.Add(rng, len(rows) + 1, len(header))
    fill_table(table, header, rows)
    return table


def apply_replacements(text: str) -> str:
    out = text
    for old, new in TEXT_REPLACEMENTS:
        out = out.replace(old, new)
    return out


def main() -> None:
    if not STEP07.exists():
        raise SystemExit(f"Missing {STEP07}")
    shutil.copy2(STEP07, STEP08_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP08_DOCX))
        if "Table 2 shows learner-based AUC" not in doc.Content.Text:
            raise RuntimeError("Results probe missing")

        n_para = 0
        for i in range(1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            raw = para_text(p)
            if "Let A={p≥τ}" in raw or "Let A={p>=τ}" in raw or "false-advance rate (FAR) is P(y=0 | A)" in raw:
                set_para_text(p, GATE_DEF)
                n_para += 1
                continue
            if raw.startswith("Table 4 applies"):
                set_para_text(p, RESULTS_C)
                n_para += 1
                continue
            if raw.startswith("Table 5 checks"):
                set_para_text(p, RESULTS_C2A)
                n_para += 1
                continue
            if raw.startswith("Coincidence of digits"):
                set_para_text(p, RESULTS_C2B)
                n_para += 1
                continue
            new = apply_replacements(raw)
            if " FM " in new:
                new = new.replace(" FM ", " FAR ")
            if "seed-42 FM" in new:
                new = new.replace("seed-42 FM", "seed-42 FAR")
            if new != raw:
                set_para_text(p, new)
                n_para += 1

        lines.append(f"TEXT_REPLACED_PARAS={n_para}")

        replace_table_by_caption(
            doc,
            "Table 4. Simulated gate",
            TABLE4_CAPTION,
            TABLE4_HEADER,
            TABLE4_ROWS,
        )
        # Note after Table 4, before the next body/caption.
        cap4 = None
        for i in range(1, doc.Paragraphs.Count + 1):
            if "Table 4. Simulated gate" in para_text(doc.Paragraphs(i)):
                cap4 = i
                break
        # Insert note after the table: find Table 5 caption and insert before it.
        cap5_i = None
        for i in range(1, doc.Paragraphs.Count + 1):
            if "Table 5." in para_text(doc.Paragraphs(i)) and "Gate robustness" in para_text(
                doc.Paragraphs(i)
            ):
                cap5_i = i
                break
        if cap5_i is None:
            # Table 5 caption not yet rewritten; original caption.
            for i in range(1, doc.Paragraphs.Count + 1):
                t = para_text(doc.Paragraphs(i))
                if t.startswith("Table 5."):
                    cap5_i = i
                    break
        # Insert note before the paragraph that currently follows Table 4
        # (RESULTS_C2A / "Table 5 checks").
        note_anchor = None
        for i in range(1, doc.Paragraphs.Count + 1):
            if para_text(doc.Paragraphs(i)).startswith("Table 5 checks"):
                note_anchor = i
                break
        if note_anchor is None:
            raise RuntimeError("Table 5 prose not found for note insert")
        doc.Paragraphs(note_anchor).Range.InsertParagraphBefore()
        p = doc.Paragraphs(note_anchor)
        try:
            p.Style = "Text"
        except Exception:
            pass
        set_para_text(p, TABLE4_NOTE)

        replace_table_by_caption(
            doc,
            "Table 5. Gate robustness",
            TABLE5_CAPTION,
            TABLE5_HEADER,
            TABLE5_ROWS,
        )

        full = doc.Content.Text
        checks = {
            "results": "Table 2 shows learner-based AUC" in full,
            "far_def": "false-advance rate (FAR) is P(y=0 | p≥τ)" in full
            or "false-advance rate (FAR) is P(y=0 | p>=τ)" in full,
            "not_latent": "not a measurement of latent mastery" in full,
            "next_response_proxy": "next-response decision-error proxy" in full,
            "e_far": "E[1−p | p≥τ]" in full or "E[1-p | p>=τ]" in full,
            "excess": "Excess FAR" in full,
            "delta_far": "ΔFAR = FAR_sparse − FAR_dense" in full
            or "ΔFAR=FAR_sparse−FAR_dense" in full,
            "n_advance": "N_advance" in full,
            "n_incorrect": "N_incorrect" in full,
            "not_n_total_precision": "does not imply the precision of FAR" in full
            or "N_total alone does not imply" in full,
            "tau07": "τ=0.7" in full,
            "grid": "{0.5, 0.6, 0.7, 0.8}" in full,
            "no_sparse_tune": "not a search over sparse error" in full
            or "Sparse events never receive" in full,
            "table4_nadv": "284,326" in full and "235" in full,
            "table4_ninc": "158,623" in full and "197" in full,
            "table5_nadv": "227" in full and "155" in full,
            "ci_locked": "[0.006, 0.138]" in full,
            "no_fm_header": "E[FM]" not in full,
            "no_dfm": "ΔFM" not in full,
            "far_in_results": "SimpleKT FAR is 0.196" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "no_bare_fm": "simulate FM" not in full and "seed-42 FM" not in full,
        }
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} PICS={doc.InlineShapes.Count}"
        )
        if doc.Tables.Count < 7:
            raise RuntimeError(f"expected >=7 tables, got {doc.Tables.Count}")
        if doc.InlineShapes.Count != 1:
            raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP08_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP08_DOC), WD_FORMAT_DOC)
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
