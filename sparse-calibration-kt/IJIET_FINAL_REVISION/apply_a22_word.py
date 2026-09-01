#!/usr/bin/env python3
"""A22: reviewer numbers/citation fixes. No locked ASSISTments cells. No new trains."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import (  # noqa: E402
    pack_review_zip,
    patch_blind_data,
    stamp_pdf_metadata,
)
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

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a22"
LOG = HERE / "audit" / "apply_a22_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A22.md"
S1 = HERE / "supplementary" / "Table_S1_calibration_full.tex"
SUP_TEX = HERE / "supplementary" / "supplementary.tex"
SUP_PDF = HERE / "output" / "supplementary.pdf"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "The Brier score [13] and its reliability, resolution, and uncertainty decomposition [14] separate miscalibration from task difficulty, and reliability diagrams display the same probability-level comparison. Complementary post-hoc work has begun to correct per-item bias after a frozen KT backbone [15].",
        "The Brier score [13] and Murphy’s reliability–resolution–uncertainty partition [23] (calibration vs. refinement [14]) separate miscalibration from task difficulty, and reliability diagrams display the same probability-level comparison. Complementary post-hoc work recovers per-item discrimination (AUC) after a frozen KT backbone [15]; it is not an ECE or FAR audit.",
    ),
    (
        "Existing KT benchmarks mainly emphasize aggregate discrimination. Sparse frequency, calibration, sample support, and threshold-based decision error are rarely examined together.",
        "Existing KT benchmarks mainly emphasize aggregate discrimination. Mastery-threshold false positives [24] and first-attempt skill evaluation [25] address related decision errors, but they do not jointly report train-only KC-frequency occupancy, ECE, and a locked-τ FAR. Sparse frequency, calibration, sample support, and threshold-based decision error are rarely examined together.",
    ),
    (
        "Junyi Academy is the Kaggle Online Learning Activity Dataset [19] (not Junyi2015); the KC field is ucid.",
        "Junyi Academy is the Kaggle Online Learning Activity Dataset [19] (not Junyi2015); the operational KC field is ucid (unique content/exercise ID, not a skill tag).",
    ),
    (
        "Table 1. Post-processing cohort statistics (learner-based split). Learner, knowledge-component (KC), interaction, and test-event counts are post-processing totals, not raw public-dump counts.",
        "Table 1. Post-processing cohort statistics (learner-based split). Learner, knowledge-component (KC), interaction, and test-event counts are post-processing totals, not raw public-dump counts. Test events are fold 0.",
    ),
    (
        "We use the binned decomposition Brier = UNC − RES + REL [14], with UNC =",
        "We use the binned Murphy decomposition Brier = UNC − RES + REL [23], with UNC =",
    ),
    (
        "Table 5: GKT FAR is 0.205 [0.194, 0.217] dense versus 0.220 [0.149, 0.295] sparse",
        "On the same seed-42 gate (not shown in Table 5), GKT FAR is 0.205 [0.194, 0.217] dense versus 0.220 [0.149, 0.295] sparse",
    ),
]

NEW_REFS = [
    'A. H. Murphy, “A new vector partition of the probability score,” Journal of Applied Meteorology, vol. 12, no. 4, pp. 595–600, 1973. doi: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2',
    'S. E. Fancsali, T. Nixon, and S. Ritter, “Optimal and worst-case performance of mastery learning assessment with Bayesian Knowledge Tracing,” in Proc. 6th International Conference on Educational Data Mining, 2013, pp. 35–42.',
    'J. Zhang, R. Das, R. S. Baker, and R. Scruggs, “Knowledge tracing models’ predictive performance when a student starts a skill,” in Proc. 14th International Conference on Educational Data Mining, 2021, pp. 625–629.',
]

S1_CAPTION_OLD = (
    "Four-unique-partition event-level calibration by train-only frequency stratum "
    "(same aggregation and $M=15$ equal-width bins as Table 4). $N$ is the mean "
    "test-event count across four unique learner partitions. Flags: Reliable (R) "
    "$N\\ge 1000$; Limited (L) $100\\le N<1000$. Junyi sparse is empty. T-KT is "
    "the local Transformer KT baseline. Brier $=$ UNC $-$ RES $+$ REL is the "
    "binned decomposition already used in the manuscript; components need not "
    "sum exactly to Brier. IRT RES $=0$ on these learner-based strata."
)
S1_CAPTION_NEW = (
    S1_CAPTION_OLD[:-1]
    + ". Junyi T-KT dense $N$ (3,232,614) differs from IRT/DKT (3,226,541) "
    "because those models were scored on separately processed test files; "
    "ASSISTments and XES3G5M share $N$ across models."
)


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
    log.append("counts=" + str({old[:40]: n for old, n in counts.items()}))
    missing = [old[:50] for old, n in counts.items() if n != 1]
    if missing:
        raise SystemExit(f"expected 1 hit each, missing/extra: {missing} {counts}")


def insert_refs(doc, log: list[str]) -> None:
    idx = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if "Knowing when to defer" in doc.Paragraphs(i).Range.Text:
            idx = i
            break
    if idx is None:
        raise SystemExit("Mitton reference paragraph not found")
    mitton = doc.Paragraphs(idx)
    template = mitton.Range.ListFormat.ListTemplate
    for text in NEW_REFS:
        doc.Paragraphs(idx).Range.InsertParagraphAfter()
        np = doc.Paragraphs(idx + 1)
        doc.Range(np.Range.Start, np.Range.End - 1).Text = text
        np.Range.ListFormat.ApplyListTemplateWithLevel(template, True, 0, 1)
        log.append(
            f"ref after {idx}: [{np.Range.ListFormat.ListString}] {text[:40]}"
        )
        idx += 1


def patch_s1_caption() -> None:
    text = S1.read_text(encoding="utf-8")
    if S1_CAPTION_OLD not in text:
        raise SystemExit("S1 caption not found")
    S1.write_text(text.replace(S1_CAPTION_OLD, S1_CAPTION_NEW, 1), encoding="utf-8")


def compile_supplementary(log: list[str]) -> None:
    cmd = shutil.which("pdflatex")
    if not cmd:
        log.append("pdflatex missing; S1 tex patched only")
        return
    for _ in range(2):
        proc = subprocess.run(
            [cmd, "-interaction=nonstopmode", "-halt-on-error", SUP_TEX.name],
            cwd=str(SUP_TEX.parent),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            log.append(proc.stdout[-1500:])
            log.append(proc.stderr[-500:])
            raise SystemExit("pdflatex supplementary failed")
    built = SUP_TEX.with_suffix(".pdf")
    shutil.copy2(built, SUP_PDF)
    log.append(f"supplementary pages copied to {SUP_PDF.name}")


def mark_stale_xes_files() -> None:
    verdict = HERE / "analysis" / "c2_fivefold_verdict.txt"
    body = verdict.read_text(encoding="utf-8")
    banner = (
        "OBSOLETE for XES3G5M gate rows in this file. Use "
        "a2b/analysis/c2_xes_verdict.txt (T-KT ΔFAR mean −0.017, ΔMiss mean −0.183). "
        "ASSISTments locked seed-42 CI [0.006, 0.138] below remains the manuscript source.\n"
    )
    if not body.startswith("OBSOLETE"):
        verdict.write_text(banner + body, encoding="utf-8")
    readme = HERE / "analysis" / "README.md"
    extra = (
        "\n## XES3G5M source of truth (A2B, padding excluded)\n\n"
        "Do not re-derive manuscript XES ECE/FAR/Miss from `c2_fivefold_verdict.txt` "
        "or from unmasked four-partition CSVs. Use `a2b/analysis/` "
        "(`c2_xes_verdict.txt`, `summary_4part_*.csv`, `a9/statistical_summary.csv`). "
        "ASSISTments locked CI in `c2_fivefold_verdict.txt` is unchanged.\n"
    )
    rtxt = readme.read_text(encoding="utf-8")
    if "XES3G5M source of truth" not in rtxt:
        readme.write_text(rtxt + extra, encoding="utf-8")
    matrix = HERE / "audit" / "BASELINE_CLAIM_TO_RESULT_MATRIX.md"
    mtxt = matrix.read_text(encoding="utf-8")
    warn = (
        "> **Obsolete XES rows.** This matrix was frozen before padding exclusion. "
        "Manuscript XES ECE/AUC/ΔMiss/Table 8/regression follow `a2b/` "
        "(ECE 0.1176/0.1129/0.1254; ΔMiss −0.183). ASSISTments locks in this file remain valid.\n\n"
    )
    if not mtxt.startswith("> **Obsolete XES rows.**"):
        matrix.write_text(warn + mtxt, encoding="utf-8")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A22 — Reviewer numbers/citation audit

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** 0.1136 / 0.2280 / 0.196 / 0.268 / 0.047 / [0.006, 0.138] unchanged.

| # | Reviewer item | Action |
|---|---|---|
| 1 | §IV.E Table 5 GKT xref | Same seed-42 gate, not shown in Table 5 |
| 2 | Junyi S1 N mismatch | Caption: T-KT 3,232,614 vs IRT/DKT 3,226,541 |
| 3 | Stale XES CSVs | Banner on `c2_fivefold_verdict.txt`, analysis README, claim matrix |
| 4 | Table 1 test events | Caption: fold 0 |
| 5 | [14] vs Murphy | Formula and lit: Murphy [23]; DeGroot [14] = calibration/refinement |
| 6 | [15] Yan et al. | Recovers per-item AUC, not an ECE/FAR audit |
| 7 | [19] Junyi ucid | Unique content/exercise ID, not a skill tag |
| 8 | FAR lineage | Fancsali/Nixon/Ritter EDM 2013 [24]; Zhang et al. EDM 2021 [25] |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a22`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A22"]
    patch_s1_caption()
    mark_stale_xes_files()
    compile_supplementary(log)
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_paragraphs(full_doc, log)
        insert_refs(full_doc, log)
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
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
        if blind_doc.Tables(5).Rows.Count != 5:
            raise RuntimeError("blind Table 5 row count")
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
    pack_review_zip(log)
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    compact = "".join(full_t.split()).lower()
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    log.append(f"GKT_XREF={'not shown in table 5' in compact}")
    log.append(f"MURPHY={'murphy' in compact}")
    log.append(f"FANCSALI={'fancsali' in compact}")
    log.append(f"ZHANG_SKILL={'starts a skill' in compact}")
    log.append(f"YAN_AUC={'per-item discrimination' in compact}")
    log.append(f"UCID={'exercise id' in compact or 'exercise/id' in compact}")
    log.append(f"FOLD0={'test events are fold 0' in compact}")
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
    if "Table 5: GKT FAR" in full_t:
        raise SystemExit("old GKT Table 5 xref remains")
    if "Murphy" not in full_t:
        raise SystemExit("Murphy ref missing")
    if "Fancsali" not in full_t:
        raise SystemExit("Ritter/Fancsali ref missing")
    if "starts a skill" not in full_t:
        raise SystemExit("Zhang 2021 ref missing")
    if "Khanh-Trinh" in blind_t:
        raise SystemExit("blind identified")
    if "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind github leak")
    if "0.1145" in full_t.replace("10.1145", ""):
        raise SystemExit("obsolete XES ECE 0.1145 in PDF")


if __name__ == "__main__":
    main()
