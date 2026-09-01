#!/usr/bin/env python3
"""IJIET-06: restructure Section II (Literature Review) only."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP05 = SRC / "main_ijiet_step05.docx"
STEP06_DOCX = SRC / "main_ijiet_step06.docx"
STEP06_DOC = SRC / "main_ijiet_step06.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step06.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step06_verify.txt"

# Same wording as IJIET-05; re-inserted in reading order (step05 used reversed
# InsertParagraphBefore, which actually appends and inverted Section I).
INTRO_PARAS = [
    "Adaptive practice platforms and intelligent tutoring systems use Knowledge Tracing (KT) to estimate a learner’s command of a skill and to decide whether to skip, remediate, or advance practice [1]–[3]. Those systems rarely consume a population area-under-the-curve (AUC) statistic. They consume a predicted probability p, which is then compared with a threshold τ. If p≥τ, the platform typically withholds additional practice on that skill. The operational chain is therefore population AUC → predicted probability → calibration → threshold-based educational decisions, with particular diagnostic risk on sparsely trained knowledge components (KCs).",
    "KT evaluations typically report population AUC and accuracy [4], [5]. Those metrics rank models, but they can conceal miscalibration on low-frequency KCs—skills with little training-fold evidence—because most test events lie on dense, frequently practiced concepts. A model can discriminate well in aggregate and still assign overconfident probabilities on the sparse tail. When a fixed threshold is applied to p, that overconfidence appears as an advance decision followed by an incorrect next response. We term this the false-advance rate (FAR). Section III defines FAR as P(y=0 | p≥τ); y denotes observed next-response correctness, not latent mastery truth.",
    "This paper treats that mismatch as an evaluation problem for educational technology, not as a reason to propose another KT architecture. The study is organized around three research questions. RQ1: Does lower KC training frequency systematically degrade predictive discrimination? RQ2: How does calibration vary across KC-frequency strata and datasets? RQ3: When a fixed probability threshold is applied, does decision-error behavior differ between sparse and dense KCs?",
    "The empirical answers are bounded. Lower KC training frequency does not universally degrade discrimination: on XES3G5M, sparse AUC is higher than dense AUC for DKT and SimpleKT. Calibration can, however, become less reliable in some sparse-concept regimes. On ASSISTments 2012, SimpleKT expected calibration error (ECE) increases from dense to sparse KCs, and a locked gate at τ=0.7 yields a higher FAR on sparse than on dense advances. The same ECE gradient is absent on Junyi, where the learner-based sparse stratum is empty, and is essentially absent for SimpleKT on XES3G5M. We therefore do not claim that sparse KCs always fail, and we do not claim a causal effect of training frequency on calibration.",
    "Contributions are conservative: (i) a train-only KC-frequency protocol with an explicit strict cold-start group, so the definition of “sparse” cannot leak test-fold counts; (ii) per-stratum calibration (ECE and Brier decomposition) on three public datasets, with occupancy flags (Reliable / Limited / Insufficient); (iii) a locked-threshold simulation of FAR and miss rates, with a five-seed check of the sparse–dense FAR gap on ASSISTments 2012. We do not propose a new KT architecture, a new calibration algorithm, or a new auditing theory, and we do not report a classroom intervention. A graph-KT (GKT) model and a CL4KT-style adapter appear only as an exploratory single-fold diagnostic on ASSISTments.",
]

# Heading 2 titles match the IJIET A./B./C./D. list (sentence case).
LIT_BLOCKS = [
    (
        "Heading 2",
        "Knowledge Tracing and benchmark models",
    ),
    (
        "Text",
        "Knowledge Tracing (KT) models a learner’s evolving proficiency from historical interactions in order to predict the next response [3]. Classical approaches include Bayesian Knowledge Tracing (BKT), which tracks a latent mastery state for each skill [1], and item-response theory (IRT), of which the one-parameter Rasch model is the canonical form used in this study [6]. Deep Knowledge Tracing (DKT) replaced hand-specified mastery dynamics with a recurrent sequence model and established the modern next-response prediction task [2]. Attention-based successors, including context-aware attentive KT [7] and SimpleKT [4], retain that task while substituting self-attention for recurrence. Benchmarking libraries such as pyKT have standardized preprocessing and comparison, and have shown that evaluation choices can distort reported discrimination [5]. Across this line of work, the primary reported statistic remains population AUC.",
    ),
    (
        "Heading 2",
        "Graph and self-supervised KT",
    ),
    (
        "Text",
        "Graph-based KT (GKT) represents knowledge components as nodes of a graph and updates proficiency with a graph neural network [8]. Contrastive learning for KT (CL4KT) trains representations from augmented views of learning histories [9]. These models are related architectures, not the contribution of the present paper. They are included later only as an exploratory single-fold diagnostic on ASSISTments 2012, not as a proposed method and not as a state-of-the-art comparison.",
    ),
    (
        "Heading 2",
        "Sparse-data and cold-start problems",
    ),
    (
        "Text",
        "The term “sparse” is used in several incompatible senses in the KT literature. This paper distinguishes four. (1) Sparse attention: sparseKT applies k-sparse attention so that only a subset of historical interactions receives nonzero weight [16]. (2) Sparse KC frequency: a knowledge component with few training-fold observations. (3) New-student cold start: prediction for learners who have little or no interaction history at test time [17]. (4) Concept-level cold start: a knowledge component with zero training-fold frequency, regardless of whether the learner is new. Educational interaction logs additionally exhibit a long tail in which a small set of dense KCs dominates event volume [20].",
    ),
    (
        "Text",
        "These four problems are not interchangeable. sparseKT-style sparse attention is not equivalent to low-frequency KCs: attention can be sparsified on a frequently practiced skill. New-student cold start is not the same as concept-level zero-frequency cold start: a previously observed learner may still encounter a concept that never appeared in the training fold. The protocol in Section III operationalizes (2) and (4) through train-only KC-frequency strata with an explicit strict cold-start group (f=0).",
    ),
    (
        "Heading 2",
        "Calibration and educational decision support",
    ),
    (
        "Text",
        "When predicted probabilities are consumed as educational decisions, ranking is not a sufficient evaluation [10]. Calibration asks whether the predicted probability p matches the empirical frequency of a correct next response. Expected calibration error (ECE) is the usual bin-wise summary of that mismatch [12]; modern neural networks can remain poorly calibrated even when they discriminate well [11]. The Brier score [13] and its reliability, resolution, and uncertainty decomposition [14] separate miscalibration from task difficulty, and reliability diagrams display the same probability-level comparison. Complementary post-hoc work has begun to correct per-item bias after a frozen KT backbone [15]. Probability-level evaluation of this kind is still typically reported on the pooled population, not on train-only frequency strata.",
    ),
    (
        "Text",
        "Existing KT benchmarks mainly emphasize aggregate discrimination. Sparse frequency, calibration, sample support, and threshold-based decision error are rarely examined together. This study keeps standard models and reports those four quantities jointly, so that a population AUC result can be read as an educational-technology decision rather than only as a leaderboard rank.",
    ),
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


def replace_in_style(doc, style: str, old: str, new: str) -> bool:
    for i in range(1, doc.Paragraphs.Count + 1):
        p = doc.Paragraphs(i)
        if p.Style.NameLocal == style and old in p.Range.Text:
            set_para_text(p, p.Range.Text.replace("\r", "").replace("\x07", "").replace(old, new))
            return True
    return False


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


def main() -> None:
    if not STEP05.exists():
        raise SystemExit(f"Missing {STEP05}")
    shutil.copy2(STEP05, STEP06_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP06_DOCX))
        results_probe = "Table 2 shows learner-based AUC"
        intro_probe = "false-advance rate (FAR)"
        if results_probe not in doc.Content.Text:
            raise RuntimeError("Results probe missing")
        if intro_probe not in doc.Content.Text:
            raise RuntimeError("Introduction FAR probe missing")

        intro_i = find_heading(doc, "Introduction")
        lit_i = find_heading(doc, "Literature Review")
        meth_i = find_heading(doc, "Materials and Methods")
        if not (intro_i < lit_i < meth_i):
            raise RuntimeError("unexpected heading order")

        # InsertParagraphBefore the next Heading 1 appends after already-inserted
        # body, so iterate in reading order (do not reverse).
        start = doc.Paragraphs(intro_i + 1).Range.Start
        end = doc.Paragraphs(lit_i).Range.Start
        doc.Range(start, end).Delete()
        lit_i = find_heading(doc, "Literature Review")
        for text in INTRO_PARAS:
            doc.Paragraphs(lit_i).Range.InsertParagraphBefore()
            p = doc.Paragraphs(lit_i)
            try:
                p.Style = "Text"
            except Exception:
                pass
            set_para_text(p, text)
            lit_i = find_heading(doc, "Literature Review")

        lit_i = find_heading(doc, "Literature Review")
        meth_i = find_heading(doc, "Materials and Methods")
        start = doc.Paragraphs(lit_i + 1).Range.Start
        end = doc.Paragraphs(meth_i).Range.Start
        doc.Range(start, end).Delete()

        meth_i = find_heading(doc, "Materials and Methods")
        for style, text in LIT_BLOCKS:
            doc.Paragraphs(meth_i).Range.InsertParagraphBefore()
            p = doc.Paragraphs(meth_i)
            try:
                p.Style = style
            except Exception:
                p.Style = "Text"
            set_para_text(p, text)
            meth_i = find_heading(doc, "Materials and Methods")

        # Keep Methods A./B./C./D. independent of the new Literature Review A.–D.
        meth_i = find_heading(doc, "Materials and Methods")
        first_methods_h2 = None
        for i in range(meth_i + 1, doc.Paragraphs.Count + 1):
            p = doc.Paragraphs(i)
            if p.Style.NameLocal == "Heading 1":
                break
            if p.Style.NameLocal == "Heading 2":
                first_methods_h2 = p
                break
        if first_methods_h2 is not None:
            lab = first_methods_h2.Range.ListFormat.ListString
            lines.append(f"METHODS_H2_BEFORE_RESTART={lab!r}")
            if "A" not in lab:
                first_methods_h2.Range.ListFormat.RestartNumbering()
                lab = first_methods_h2.Range.ListFormat.ListString
            lines.append(f"METHODS_H2_AFTER={lab!r}")

        ok5 = replace_in_style(
            doc,
            "References",
            "Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2022",
            "Thirty-sixth Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2022",
        )
        ok9 = replace_in_style(
            doc,
            "References",
            "W. Lee, J. Chun, Y. Lee, K. Park, and D. Choi",
            "W. Lee, J. Chun, Y. Lee, K. Park, and S. Park",
        )
        lines.append(f"FIXED_REF5_PYKT_36TH={ok5}")
        lines.append(f"FIXED_REF9_CL4KT_AUTHOR={ok9}")

        lit_i = find_heading(doc, "Literature Review")
        meth_i = find_heading(doc, "Materials and Methods")
        lit_text = doc.Range(
            doc.Paragraphs(lit_i).Range.Start,
            doc.Paragraphs(meth_i).Range.Start,
        ).Text
        n_lit_body = meth_i - lit_i - 1
        cite_nums = [int(x) for x in re.findall(r"\[(\d+)\]", lit_text)]
        h2_labels = heading2_labels(doc)

        intro_text = doc.Range(
            doc.Paragraphs(find_heading(doc, "Introduction")).Range.Start,
            doc.Paragraphs(find_heading(doc, "Literature Review")).Range.Start,
        ).Text
        intro_ok = intro_text.find("Adaptive practice platforms") < intro_text.find("Contributions are conservative")
        lit_ok = lit_text.find("Knowledge Tracing and benchmark models") < lit_text.find(
            "Calibration and educational decision support"
        )
        checks = {
            "intro_order": intro_ok,
            "lit_order": lit_ok,
            "results": results_probe in doc.Content.Text,
            "intro_far": intro_probe in doc.Content.Text,
            "n_lit_body": n_lit_body,
            "h2_a": "Knowledge Tracing and benchmark models" in lit_text,
            "h2_b": "Graph and self-supervised KT" in lit_text,
            "h2_c": "Sparse-data and cold-start problems" in lit_text,
            "h2_d": "Calibration and educational decision support" in lit_text,
            "bkt_irt": "Bayesian Knowledge Tracing (BKT)" in lit_text and "[1]" in lit_text and "[6]" in lit_text,
            "dkt": "Deep Knowledge Tracing (DKT)" in lit_text and "[2]" in lit_text,
            "attention": "self-attention" in lit_text and "[7]" in lit_text,
            "simplekt": "SimpleKT" in lit_text and "[4]" in lit_text,
            "gkt_not_contrib": "related architectures, not the contribution" in lit_text,
            "sparse_attn_neq": "sparseKT-style sparse attention is not equivalent to low-frequency KCs" in lit_text,
            "new_student_neq": "New-student cold start is not the same as concept-level zero-frequency cold start" in lit_text,
            "ece": "Expected calibration error (ECE)" in lit_text,
            "brier": "Brier score" in lit_text,
            "reliability": "reliability diagrams" in lit_text,
            "gap": "Existing KT benchmarks mainly emphasize aggregate discrimination" in lit_text
            and "rarely examined together" in lit_text,
            "no_new_cite": all(n <= 20 for n in cite_nums),
            "cite_max": max(cite_nums) if cite_nums else 0,
            "no_new_arch": "not as a proposed method" in lit_text,
            "no_causal": "causal" not in lit_text.lower(),
        }

        lines.append(f"LIT_BODY_PARAS={n_lit_body}")
        lines.append("H2_LABELS=")
        lines.extend("  " + x.replace("\r", " ").strip() for x in h2_labels)
        lines.append(f"LIT_CITES={sorted(set(cite_nums))}")
        for k, v in checks.items():
            if k == "n_lit_body":
                continue
            lines.append(f"{k}={v}")

        if n_lit_body != len(LIT_BLOCKS):
            raise RuntimeError(f"expected {len(LIT_BLOCKS)} lit blocks, got {n_lit_body}")
        required = [
            "intro_order",
            "lit_order",
            "h2_a",
            "h2_b",
            "h2_c",
            "h2_d",
            "sparse_attn_neq",
            "new_student_neq",
            "gap",
            "results",
            "no_new_cite",
        ]
        missing = [k for k in required if not checks[k]]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")
        if not ok5 or not ok9:
            raise RuntimeError("reference corrections failed")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} PICS={doc.InlineShapes.Count}"
        )

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP06_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP06_DOC), WD_FORMAT_DOC)
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
