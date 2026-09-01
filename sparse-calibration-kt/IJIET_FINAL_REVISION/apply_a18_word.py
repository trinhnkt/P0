#!/usr/bin/env python3
"""A18: remaining submission nits. No locked ASSISTments cells. No invented AI versions."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
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
    stamp_pdf_metadata,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a18"
LOG = HERE / "audit" / "apply_a18_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A18.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "the sparse–dense gap stays positive on all five training runs across four unique learner partitions (mean 0.047)",
        "the sparse–dense gap stays positive on all five training runs and on all four unique partitions (mean 0.047)",
    ),
    (
        "(478 KC-fold observations representing 261 unique KCs; 2,645 representing 1,326; and 829 unique KCs) is a between-KC association: it compares different concepts, with cluster-robust standard errors at kc_id.",
        "is a between-KC association: it compares different concepts. ASSISTments (478 KC-fold rows; 261 unique KCs) and Junyi (2,645 KC-fold rows; 1,326 unique KCs) use cluster-robust standard errors at kc_id; XES3G5M is 829 unique KCs in the masked weighted fit.",
    ),
    (
        "Learner exposure is independently associated on ASSISTments (+0.016 [0.004, 0.027]).",
        "Learner exposure is independently associated on ASSISTments (+0.016 [0.004, 0.027]) and on XES3G5M (+0.013 [+0.005, +0.021]).",
    ),
    (
        "and we do not report a classroom intervention.",
        "and we do not report a classroom intervention. This is an evaluation-systems contribution for threshold-based educational decisions, not a new pedagogy.",
    ),
    (
        "A public repository will be released upon acceptance.",
        "A public repository will be released upon acceptance. Named camera-ready manuscripts are not part of this IJIET review snapshot; ignore them if an older copy still contains them.",
    ),
]


def patch(doc, log: list[str]) -> None:
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
                text = text.replace(old, new)
                counts[old] += 1
                changed = True
        if changed:
            inner.Text = text
            log.append(f"patched i={i}")
    for old, n in counts.items():
        log.append(f"count {old[:48]!r}={n}")
        if n != 1:
            raise SystemExit(f"expected 1 hit for {old[:60]!r}, got {n}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A18 — Remaining submission nits

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged.

## Manuscript (this folder only)

- Abstract: ΔFAR positive on **5/5 runs and 4/4 unique partitions** (mean 0.047).
- IV.D: ASSISTments/Junyi = KC-fold + cluster-robust SE at `kc_id`; XES = 829 unique KCs, masked weighted fit.
- Learner exposure also reported for A2B XES (+0.013 [+0.005, +0.021]).
- Introduction: one evaluation-systems sentence (not a new pedagogy).
- Data availability: named camera-ready files are not part of this IJIET snapshot.

## Supplementary

Compiled `output/supplementary.pdf` from Tables S1, S2, and S-regression for OJS attach.

## Anonymous snapshot

Wrote `audit/ANONYMOUS_SNAPSHOT_FIX.md` and overlay files. **Cannot rewrite live 4open.science from this machine.** Re-upload a snapshot without named JEDM `main_jedm.tex`/`.pdf`.

## Not done here (cannot invent / cannot withdraw)

- ChatGPT / Claude / Antigravity **versions**: still not on file; statement already says identifiers were not retained; Cursor Grok 4.6 kept.
- Dual submission vs JEDM `paper/`: author process. Did not edit `paper/` or withdraw JEDM.

## Compile

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a18`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not FULL_DOCX.exists():
        raise SystemExit(f"missing {FULL_DOCX}")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A18"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch(full_doc, log)
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        export_pdf(full_doc, FULL_PDF, include_props=True)
        full_doc.Close(WD_SAVE)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, log)
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
    log.append(f"4of4={'all four unique partitions' in full_t}")
    log.append(f"XES_EXP={'0.013' in full_t}")
    log.append(f"EVAL_SYS={'evaluation-systems' in full_t}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"bytes={FULL_PDF.stat().st_size}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n"
        + "\n".join(f"blind_{k}={v}" for k, v in blind_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages)
    print("\n".join(log))
    print(VERIFY.read_text(encoding="utf-8"))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if "Khanh-Trinh" in blind_t:
        raise SystemExit("blind identified")
    compact = "".join(full_t.split())
    if "allfouruniquepartitions" not in compact.lower():
        raise SystemExit("abstract 4/4 phrase missing")


if __name__ == "__main__":
    main()
