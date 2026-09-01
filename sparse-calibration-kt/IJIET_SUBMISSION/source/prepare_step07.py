#!/usr/bin/env python3
"""IJIET-07: revise Section III (Materials and Methods) only.

Does not change Results tables, Table 1 numeric cells, or train-only stratum cuts.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP06 = SRC / "main_ijiet_step06.docx"
STEP07_DOCX = SRC / "main_ijiet_step07.docx"
STEP07_DOC = SRC / "main_ijiet_step07.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step07.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step07_verify.txt"
FIG = ROOT / "IJIET_SUBMISSION" / "figures" / "figure2_bucket_distribution.png"

# Heading 2 titles match IJIET A./B./C. sentence case; one topic per heading.
# Table 1 cells are identical to step06. Settings table is unnumbered so
# Results captions Table 2–6 stay valid.
METHODS_BLOCKS: list[tuple] = [
    (
        "Heading 2",
        "Datasets",
    ),
    (
        "Text",
        "We use three de-identified public logs after a common interaction schema: "
        "ASSISTments 2012 [18], [5], Junyi Academy [19], and XES3G5M [20]. Table 1 "
        "reports post-processing counts: processed learners, processed KCs, processed "
        "interactions, and learner-based test events. Exact processed interaction "
        "totals are 2,657,490 (ASSISTments 2012), 16,215,567 (Junyi Academy), and "
        "7,953,709 (XES3G5M). Preprocessing drops rows with missing learner, KC, or "
        "label identifiers, binarizes correctness, parses timestamps, and keeps "
        "learners with at least two interactions. Those filters—not the raw public "
        "dumps—are what Table 1 counts.",
    ),
    (
        "Text",
        "Provenance. ASSISTments 2012 is the 2012–2013 public release with affect [18], "
        "documented for KT use in pyKT [5]; each retained row already carries one "
        "skill_id. Junyi Academy is the Kaggle Online Learning Activity Dataset [19] "
        "(not Junyi2015); the KC field is ucid. XES3G5M [20] is loaded from the "
        "authors’ kc_level split: train_valid_sequences.csv and test.csv are "
        "concatenated and flattened to one row per sequence position.",
    ),
    (
        "Text",
        "XES3G5M counts. The original dataset paper reports 18,066 students, 7,652 "
        "questions, 865 KCs, and 5,549,635 question-level interactions [20]. Table 1 "
        "instead lists 866 KCs and 7.95M interactions because flattening kc_level "
        "sequences (i) expands multi-KC questions into one row per listed concept and "
        "(ii) retains sequence-padding tokens coded skill_id=−1 (with matching "
        "question_id=−1). Unique kc_id including that padding token is 866; excluding "
        "it is 865. Unique item_id including −1 is 7,653. Subsequent preprocessing "
        "dropped 0 rows. We do not retabulate Table 1 to the question-level official "
        "totals.",
    ),
    ("table1", None),
    (
        "Heading 2",
        "Splits and seeds",
    ),
    (
        "Text",
        "The learner-based split is primary. Users are shuffled with the fold seed; "
        "20% of learners are held out as test, 10% as validation, and the remainder "
        "as training. Within a fold, train, validation, and test learners are disjoint. "
        "The temporal split is complementary: all interactions are sorted by timestamp; "
        "the earliest 70% are training, the next 10% validation, and the latest 20% "
        "test. Gate numbers below are not taken from the temporal split. KC-frequency "
        "buckets are constructed from the training file only.",
    ),
    (
        "Text",
        "Deep models are trained in five runs at seeds 42, 2024, 2025, 2026, and 2027 "
        "(fold_0 through fold_4). Seeds 2025 and 2026 share one student partition "
        "(fold_2 = fold_3) on all three datasets. These are five training runs and "
        "four unique student partitions, not five independent folds. Tables that "
        "report mean±sd therefore summarize four unique partitions: the two "
        "initializations on the duplicated split are averaged first. The "
        "gate-robustness table still lists all five training seeds.",
    ),
    (
        "Heading 2",
        "Model settings",
    ),
    (
        "Text",
        "Main tables use local IRT, DKT, and SimpleKT implementations, not a pinned "
        "pyKT commit (training snapshot commit: NOT RECOVERED). The local SimpleKT "
        "class is a two-layer Transformer encoder and is not byte-identical to the "
        "official SimpleKT checkpoint [4]. Recovered hyperparameters follow; missing "
        "fields are marked NOT RECOVERED and are not imputed.",
    ),
    ("settings_table", None),
    (
        "Text",
        "On ASSISTments fold 0 only we also score a train-only GKT graph [8] (pyKT GKT; "
        "Adam, learning rate 1e−3, batch size 16, maximum length 100, hidden and "
        "embedding size 32, dropout 0.5, 20 epochs, patience 4, selection by "
        "validation AUC) and a CL4KT protocol adapter [9] (contrastive views on "
        "training sequences; not an official CL4KT checkpoint; Adam, learning rate "
        "1e−3, batch size 64, maximum length 100, hidden size 64, 4 heads, 2 layers, "
        "dropout 0.2, 20 epochs, patience 6, selection by validation AUC). IRT under "
        "learner-based splits has no ability parameter for unseen students, so its "
        "AUC is 0.50 by construction; we report it as a base-rate reference, not as a "
        "ranking competitor.",
    ),
    (
        "Heading 2",
        "Train-only frequency strata",
    ),
    (
        "Text",
        "For each fold, KC frequency f_train is counted on the training file only. "
        "Buckets: strict cold-start (f=0), very sparse (0<f<20), sparse (20≤f<100), "
        "medium (100≤f<500), dense (f≥500). Dense KCs dominate event volume while a "
        "non-empty sparse-like tail exists on ASSISTments and XES3G5M.",
    ),
    ("figure", None),
    (
        "Heading 2",
        "Reliability flags",
    ),
    (
        "Text",
        "Occupancy flags follow test-event count N: Reliable (R) N≥1000; Limited (L) "
        "100≤N<1000; Insufficient (I) N<100. We call R, L, and I descriptive "
        "sample-support flags. They are not inferential guarantees, confidence "
        "intervals, or hypothesis tests. Success claims require Limited or Reliable "
        "occupancy. Insufficient cells are descriptive only. Very-sparse ASSISTments "
        "cells are Insufficient and descriptive only.",
    ),
    (
        "Heading 2",
        "Calibration",
    ),
    (
        "Text",
        "Let y∈{0,1} be next-response correctness and p∈[0,1] the predicted "
        "probability. With M=15 equal-width bins, ECE = Σ_m (n_m / N) |acc_m − conf_m|. "
        "The Brier score is (1/N) Σ_i (p_i − y_i)². We use the binned decomposition "
        "Brier = UNC − RES + REL [14], with UNC = ȳ(1−ȳ), "
        "REL = (1/N) Σ_m n_m (conf_m − acc_m)², and "
        "RES = (1/N) Σ_m n_m (acc_m − ȳ)². Because probabilities are binned, the "
        "three components are an empirical approximation and need not sum exactly to "
        "the directly computed Brier score. Lower ECE is better calibration; it is "
        "not a substitute for AUC.",
    ),
    (
        "Heading 2",
        "Difficulty coupling",
    ),
    (
        "Text",
        "For each KC c we define a training-only difficulty proxy "
        "difficulty(c) = 1 − mean_train_correctness(c). The mean is taken on the "
        "training file only. This is an observational proxy for how often c is "
        "answered incorrectly in training; it is not a latent IRT difficulty "
        "parameter. The reported Spearman association is ρ(log(1+f_train), difficulty), "
        "computed on training-fold KC summaries. The association is descriptive and "
        "is not a causal effect of frequency on difficulty or on calibration.",
    ),
    (
        "Heading 2",
        "Simulated decision gate",
    ),
    (
        "Text",
        "For a locked global threshold τ, the system advances (skips remediation) if "
        "p≥τ and triggers remediation otherwise. Sparse events never receive their "
        "own tuned τ. The display threshold is τ=0.7; the grid {0.5, 0.6, 0.7, 0.8} "
        "is recorded in the artifact and is not a search over sparse error.",
    ),
    (
        "Text",
        "Let A={p≥τ}. The false-advance rate (FAR) is P(y=0 | A): among advances, how "
        "often the next response was incorrect. y is observed next-response "
        "correctness, not latent mastery. Miss is P(A | y=0): among incorrect "
        "answers, how often the system still skipped help. Result tables label FAR "
        "as false mastery (FM); the definition is the same. If the model were "
        "calibrated on the advance set, FAR would match E[1−p | A]. We report "
        "ΔFM = FM_sparse − FM_dense. Positive ΔFM means sparse advances are dirtier "
        "than dense advances. This is a simulated decision error, not an "
        "instructional RCT.",
    ),
]

TABLE1_HEADER = ["Dataset", "Learners", "KCs", "Interactions", "Test events"]
TABLE1_ROWS = [
    ["ASSISTments 2012", "27,806", "265", "2.66M", "534,150"],
    ["Junyi Academy", "71,014", "1,326", "16.2M", "3,269,022"],
    ["XES3G5M", "18,066", "866", "7.95M", "1,589,145"],
]
TABLE1_CAPTION = (
    "Table 1. Post-processing cohort statistics (learner-based split). "
    "Displayed interaction totals match the processed counts 2.66M, 16.2M, and 7.95M."
)

SETTINGS_HEADER = ["Setting", "IRT 1PL", "DKT", "SimpleKT"]
SETTINGS_ROWS = [
    ["Implementation", "local IRT", "local DKT", "local SimpleKT"],
    ["Version/commit", "NOT RECOVERED", "NOT RECOVERED", "NOT RECOVERED"],
    ["Major hyperparameters", "1PL: sigmoid(θ−β); L2 0.01", "LSTM embed 64, hidden 128", "Transformer 2 layers, 4 heads, embed 64"],
    ["Optimizer", "SGD", "Adam", "Adam"],
    ["Learning rate", "0.01", "1e−3", "1e−3"],
    ["Early stopping", "none (10 epochs)", "none (50 epochs)", "none (50 epochs)"],
    ["Batch size", "512", "64", "64"],
    ["Max. sequence length", "n/a", "200", "200"],
    ["Selection metric", "last epoch", "validation AUC", "validation AUC"],
]
SETTINGS_CAPTION = (
    "Recovered training settings for the main baselines. "
    "NOT RECOVERED cells were not imputed. This listing is not a Results table."
)

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_START = 1
WD_ALIGN_CENTER = 1


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


def restart_methods_h2(doc, lines) -> None:
    """Force Methods A.–H. after tables split Word’s outline list."""
    letters = "ABCDEFGH"
    meth_i = find_heading(doc, "Materials and Methods")
    res_i = find_heading(doc, "Result and Discussion")
    meth_h2 = []
    for i in range(meth_i + 1, res_i):
        p = doc.Paragraphs(i)
        if p.Style.NameLocal == "Heading 2":
            meth_h2.append(p)
    for i, p in enumerate(meth_h2):
        raw = p.Range.Text.replace("\r", "").replace("\x07", "").strip()
        for prefix in [f"{ch}. " for ch in letters] + [f"{ch}." for ch in letters]:
            if raw.startswith(prefix):
                raw = raw[len(prefix) :].lstrip()
                break
        letter = letters[i] if i < len(letters) else "?"
        try:
            p.Range.ListFormat.RemoveNumbers()
        except Exception as exc:
            lines.append(f"REMOVE_NUM_ERR={exc}")
        set_para_text(p, f"{letter}. {raw}")
    lines.append(
        "METHODS_H2_NUMBERS="
        + ",".join(p.Range.ListFormat.ListString or p.Range.Text.strip()[:4] for p in meth_h2)
    )


def heading2_labels(doc) -> list[str]:
    labels = []
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        if p.Style.NameLocal == "Heading 2":
            try:
                lab = p.Range.ListFormat.ListString
            except Exception:
                lab = "?"
            labels.append(f"{lab} {p.Range.Text.strip()}")
    return labels


def insert_before_heading(doc, heading_name: str, text: str, style: str):
    idx = find_heading(doc, heading_name)
    doc.Paragraphs(idx).Range.InsertParagraphBefore()
    p = doc.Paragraphs(idx)
    try:
        p.Style = style
    except Exception:
        p.Style = "Text"
    set_para_text(p, text)
    return p


def add_table(doc, heading_name: str, header, rows, caption: str, caption_style="Table Title"):
    insert_before_heading(doc, heading_name, caption, caption_style)
    idx = find_heading(doc, heading_name)
    rng = doc.Paragraphs(idx).Range
    rng.Collapse(WD_COLLAPSE_START)
    table = doc.Tables.Add(rng, len(rows) + 1, len(header))
    table.Style = "Table Grid"
    for j, h in enumerate(header, 1):
        table.Cell(1, j).Range.Text = h
        table.Cell(1, j).Range.Font.Bold = True
        table.Cell(1, j).Range.Font.Size = 8
        table.Cell(1, j).Range.Font.Name = "Times New Roman"
        table.Cell(1, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    for i, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            table.Cell(i, j).Range.Text = str(val)
            table.Cell(i, j).Range.Font.Bold = False
            table.Cell(i, j).Range.Font.Size = 8
            table.Cell(i, j).Range.Font.Name = "Times New Roman"
            table.Cell(i, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    try:
        table.AutoFitBehavior(2)
    except Exception:
        pass
    return table


def add_figure(doc, heading_name: str) -> None:
    insert_before_heading(doc, heading_name, " ", "Text")
    idx = find_heading(doc, heading_name)
    rng = doc.Paragraphs(idx - 1).Range
    rng.Collapse(WD_COLLAPSE_START)
    pic = rng.InlineShapes.AddPicture(str(FIG))
    try:
        pic.Width = 240
    except Exception:
        pass
    insert_before_heading(
        doc,
        heading_name,
        "Fig. 1. Train-only KC-frequency strata. Dense concepts dominate "
        "interactions; sparse and cold-start KCs remain the diagnostic tail.",
        "figure caption",
    )


def dump_methods(doc) -> str:
    meth_i = find_heading(doc, "Materials and Methods")
    res_i = find_heading(doc, "Result and Discussion")
    lines = []
    for i in range(meth_i, res_i):
        p = doc.Paragraphs(i)
        style = p.Style.NameLocal
        text = p.Range.Text.replace("\r", " ").replace("\x07", "").strip()
        if not text and style not in ("Heading 1", "Heading 2"):
            continue
        lines.append(f"[{style}] {text}")
    return "\n".join(lines)


def main() -> None:
    if not STEP06.exists():
        raise SystemExit(f"Missing {STEP06}")
    if not FIG.exists():
        raise SystemExit(f"Missing figure {FIG}")
    shutil.copy2(STEP06, STEP07_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP07_DOCX))
        results_probe = "Table 2 shows learner-based AUC"
        if results_probe not in doc.Content.Text:
            raise RuntimeError("Results probe missing before edit")

        tables_before = doc.Tables.Count
        pics_before = doc.InlineShapes.Count
        lines.append(f"BEFORE TABLES={tables_before} PICS={pics_before}")

        meth_i = find_heading(doc, "Materials and Methods")
        res_i = find_heading(doc, "Result and Discussion")
        if meth_i >= res_i:
            raise RuntimeError("unexpected heading order")
        start = doc.Paragraphs(meth_i + 1).Range.Start
        end = doc.Paragraphs(res_i).Range.Start
        doc.Range(start, end).Delete()

        # Range delete re-anchors the old Methods figure onto Copyright at doc end.
        for i in range(doc.InlineShapes.Count, 0, -1):
            doc.InlineShapes(i).Delete()
        lines.append(f"AFTER_DELETE_PICS={doc.InlineShapes.Count}")

        target = "Result and Discussion"
        for kind, text in METHODS_BLOCKS:
            if kind == "table1":
                add_table(
                    doc,
                    target,
                    TABLE1_HEADER,
                    TABLE1_ROWS,
                    TABLE1_CAPTION,
                )
            elif kind == "settings_table":
                add_table(
                    doc,
                    target,
                    SETTINGS_HEADER,
                    SETTINGS_ROWS,
                    SETTINGS_CAPTION,
                )
            elif kind == "figure":
                add_figure(doc, target)
            else:
                insert_before_heading(doc, target, text, kind)

        meth_i = find_heading(doc, "Materials and Methods")
        restart_methods_h2(doc, lines)

        full = doc.Content.Text
        meth_text = dump_methods(doc)
        (ROOT / "IJIET_SUBMISSION" / "audit" / "step07_methods.txt").write_text(
            meth_text + "\n", encoding="utf-8"
        )

        checks = {
            "results": results_probe in full,
            "table2_caption": "Table 2. Overall learner-based AUC" in full,
            "table3_caption": "Table 3. SimpleKT event-level ECE" in full,
            "post_processing": "post-processing counts" in meth_text,
            "xes_official": "5,549,635" in meth_text and "865 KCs" in meth_text,
            "xes_padding": "skill_id" in meth_text and "866" in meth_text,
            "learner_primary": "learner-based split is primary" in meth_text,
            "temporal_comp": "temporal split is complementary" in meth_text,
            "disjoint": "train, validation, and test learners are disjoint" in meth_text,
            "train_only_buckets": "constructed from the training file only" in meth_text,
            "five_seeds": "42, 2024, 2025, 2026, and 2027" in meth_text,
            "four_partitions": "four unique student partitions" in meth_text,
            "not_five_folds": "not five independent folds" in meth_text,
            "no_bare_independent_folds": "five independent folds" in meth_text
            and meth_text.count("five independent folds")
            == meth_text.count("not five independent folds"),
            "not_recovered": "NOT RECOVERED" in meth_text,
            "strata_strict": "strict cold-start (f=0)" in meth_text,
            "strata_vs": "0<f<20" in meth_text,
            "strata_sparse": "20≤f<100" in meth_text,
            "flags_descriptive": "descriptive sample-support flags" in meth_text,
            "not_inferential": "not inferential guarantees" in meth_text,
            "ece": "ECE = Σ_m (n_m / N) |acc_m − conf_m|" in meth_text,
            "brier": "Brier score is (1/N) Σ_i (p_i − y_i)²" in meth_text,
            "rel_res_unc": "Brier = UNC − RES + REL" in meth_text,
            "difficulty": "difficulty(c) = 1 − mean_train_correctness(c)" in meth_text,
            "not_irt_diff": "not a latent IRT difficulty" in meth_text,
            "spearman": "ρ(log(1+f_train), difficulty)" in meth_text,
            "far": "false-advance rate (FAR)" in meth_text,
            "h2_a": "Datasets" in meth_text,
            "h2_settings": "Model settings" in meth_text,
            "table1_assist": "27,806" in meth_text and "265" in meth_text and "2.66M" in meth_text,
            "table1_junyi": "71,014" in meth_text and "1,326" in meth_text and "16.2M" in meth_text,
            "table1_xes": "18,066" in meth_text and "866" in meth_text and "7.95M" in meth_text,
        }

        h2_labels = heading2_labels(doc)
        lines.append("H2_LABELS=")
        lines.extend("  " + x.replace("\r", " ").strip() for x in h2_labels)
        for k, v in checks.items():
            lines.append(f"{k}={v}")

        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        n_tables = doc.Tables.Count
        n_pics = doc.InlineShapes.Count
        lines.append(f"PAGES={pages} WORDS={words} TABLES={n_tables} PICS={n_pics}")
        for i in range(1, n_pics + 1):
            shp = doc.InlineShapes(i)
            try:
                snippet = shp.Range.Paragraphs(1).Range.Text[:80].replace("\r", " ")
                lines.append(f"  pic {i} start={shp.Range.Start} para={snippet!r}")
            except Exception as exc:
                lines.append(f"  pic {i} err={exc}")
        if n_tables < 6:
            raise RuntimeError(f"expected >=6 tables, got {n_tables}")
        if n_pics != 1:
            raise RuntimeError(f"expected 1 figure, got {n_pics}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP07_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP07_DOC), WD_FORMAT_DOC)
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
