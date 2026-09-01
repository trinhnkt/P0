#!/usr/bin/env python3
"""A26: IJIET novelty framing (TSCDA measurement tool). Tier A only.

No locked cells. No trains. No temperature/Platt. No JEDM name. No title change.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
from apply_a24_format import style_labeled_block  # noqa: E402
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOCX,
    FULL_PDF,
    anonymize_blind,
    export_pdf,
    lock_checks,
    pdf_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a26"
LOG = HERE / "audit" / "apply_a26_novelty_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A26.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "This paper reports a diagnostic evaluation—not a new KT architecture—of train-only KC-frequency strata on three public logs",
        "This paper presents TSCDA (Train-only Sparse-Concept Decision Audit), an evaluation instrument—not a new KT architecture—on three public logs",
    ),
    (
        "Junyi has no learner-based sparse stratum, and XES3G5M T-KT ECE is essentially flat.",
        "Junyi’s exercise-level KC tagging yields no learner-based sparse stratum (estimability, not a missing table), and XES3G5M T-KT ECE is essentially flat.",
    ),
    (
        "Keywords—knowledge tracing, calibration, sparse concepts, learning analytics, educational decision support, mastery threshold",
        "Keywords—knowledge tracing, calibration, sparse concepts, learning analytics, evaluation instrument, mastery threshold",
    ),
    (
        "The study is organized around three research questions. RQ1:",
        "The study is organized around an estimability check (does a sparse stratum exist under the platform’s KC definition?) and three research questions. RQ1:",
    ),
    (
        "Contributions are conservative: (i) a train-only KC-frequency protocol with an explicit strict cold-start group, so the definition of “sparse” cannot leak test-fold counts; (ii) per-stratum calibration (ECE and Brier decomposition) on three public datasets, with occupancy flags (Reliable / Limited / Insufficient); (iii) a locked-threshold simulation of FAR and miss rates, with a check of the sparse–dense FAR gap on ASSISTments 2012 across five training runs / four unique learner partitions. We do not propose a new KT architecture, a new calibration algorithm, or a new auditing theory, and we do not report a classroom intervention. This is an evaluation-systems contribution for threshold-based educational decisions, not a new pedagogy.",
        "Contributions are conservative: (i) TSCDA, a train-only sparse-concept decision audit—frequency strata with a strict cold-start bin, occupancy-gated ECE/Brier, and a locked-τ FAR—so “sparse” cannot leak test-fold counts; (ii) an estimability result: whether that audit has a sparse stratum depends on how the platform defines a KC (skill_id on ASSISTments/XES3G5M versus exercise-level ucid on Junyi); (iii) a dataset-conditional gate finding on ASSISTments 2012 across four unique learner partitions (five runs, two sharing a split). We do not propose a new KT architecture, a new calibration algorithm, or a new auditing theory, and we do not report a classroom intervention. This is an educational-technology measurement contribution for threshold-based practice systems, not a new pedagogy.",
    ),
    (
        "the operational KC field is ucid (unique content/exercise ID, not a skill tag).",
        "the operational KC field is ucid (unique content/exercise ID, not a skill tag); that tagging choice, not a processing error, is why the learner-based sparse bucket is empty (Table 7).",
    ),
    (
        "Training-interaction volume is shown separately in the bottom row from summed ftrain, not inferred from KC counts.",
        "Training-interaction volume is shown separately in the bottom row from summed ftrain, not inferred from KC counts. TSCDA then applies four steps on each fold: (1) assign those train-only strata, including f=0; (2) flag occupancy R/L/I; (3) report ECE/Brier with those flags; (4) apply one locked τ and report FAR with Nadvance (Section III.E–H).",
    ),
    (
        "Before using one global KT probability threshold for remediation or advancement, four checks are warranted under the evaluated conditions:",
        "TSCDA is four checks before using one global KT probability threshold for remediation or advancement:",
    ),
    (
        "Junyi’s learner-based sparse bucket is empty rather than a ranking collapse.",
        "Junyi’s learner-based sparse bucket is empty (exercise-level tagging) rather than a ranking collapse.",
    ),
    (
        "Junyi’s learner-based sparse bucket is empty. ASSISTments and XES3G5M both have a non-empty sparse tail",
        "Junyi’s learner-based sparse bucket is empty because the operational KC is an exercise identifier (ucid), so TSCDA can refuse a sparse claim when tagging is finer than a skill. ASSISTments and XES3G5M both have a non-empty sparse tail",
    ),
    (
        "Sparse-concept occupancy, calibration, and threshold-error checks are therefore conditionally useful for educational-technology gates. This paper is a simulated decision-error check, not a new KT model and not a classroom intervention.",
        "TSCDA occupancy, calibration, and threshold-error checks are therefore conditionally useful for educational-technology gates. This paper is a simulated decision-error audit, not a new KT model and not a classroom intervention.",
    ),
]


def patch_paragraphs(doc, log: list[str]) -> None:
    counts = {old: 0 for old, _ in REPLACEMENTS}
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        try:
            if para.Range.Tables.Count:
                continue
        except Exception:
            pass
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        changed = False
        for old, new in REPLACEMENTS:
            if old in text:
                text = text.replace(old, new, 1)
                counts[old] += 1
                changed = True
        if changed:
            inner.Text = text
            log.append(f"para i={i}")
    missing = [old[:70] for old, n in counts.items() if n != 1]
    log.append("counts=" + str({old[:50]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing} {counts}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A26 — IJIET novelty framing (Tier A)

**Date:** 2026-09-01  
**Retrain:** no. **Locks:** unchanged. **No B1 policy experiment.** **No JEDM name.**

| # | Item | Action |
|---|---|---|
| A1 | Named instrument | TSCDA in abstract, contributions, V.B, conclusion |
| A2 | Junyi estimability | ucid tagging = why sparse bucket is empty (Table 7) |
| A3 | Contribution rewrite | (i) tool (ii) KC-definition estimability (iii) conditional gate |
| A4 | Four steps | Compact list at end of III.D (not a new figure) |
| Keywords | evaluation instrument | Replaces educational decision support |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a26`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A26"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_paragraphs(full_doc, log)
        style_labeled_block(full_doc, 10, "Abstract—", log, "ABSTRACT")
        style_labeled_block(full_doc, 11, "Keywords—", log, "KEYWORDS")
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        try:
            full_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        export_pdf(full_doc, FULL_PDF, include_props=True)
        full_doc.Close(WD_SAVE)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, log)
        patch_blind_data(blind_doc, log)
        set_word_props(blind_doc, "", "")
        try:
            blind_doc.BuiltInDocumentProperties("Title").Value = PAPER_TITLE
        except Exception:
            pass
        try:
            blind_doc.RemoveDocumentInformation(1)
        except Exception:
            pass
        if "Khanh-Trinh" in (blind_doc.Content.Text or ""):
            raise RuntimeError("blind Word still contains Khanh-Trinh")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF, include_props=False)
        if blind_doc.Tables.Count != n_tables or blind_doc.InlineShapes.Count != n_figs:
            raise RuntimeError("blind structure changed")
        blind_doc.Close(WD_SAVE)
        blind_doc = None
    finally:
        if full_doc is not None:
            full_doc.Close(0)
        if blind_doc is not None:
            blind_doc.Close(0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if "TSCDA" not in full_t:
        raise SystemExit("TSCDA missing")
    if "evaluation instrument" not in full_t.lower() and "evaluationinstrument" not in "".join(
        full_t.split()
    ).lower():
        raise SystemExit("evaluation instrument missing")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if "more higher-error" in full_t:
        raise SystemExit("double comparative returned")


if __name__ == "__main__":
    main()
