#!/usr/bin/env python3
"""A23: bibliography/citation nits from contribution-and-references review.

No locked ASSISTments cells. No new trains. No supplementary change.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import patch_blind_data, stamp_pdf_metadata  # noqa: E402
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

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a23"
LOG = HERE / "audit" / "apply_a23_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A23.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

REPLACEMENTS = [
    (
        "Educational interaction logs additionally exhibit a long tail in which a small set of dense KCs dominates event volume [20].",
        "The XES3G5M log exhibits a long tail in which a small set of dense KCs dominates event volume [20].",
    ),
    (
        "This study does not apply temperature scaling or Platt scaling; those maps would be a separate post-hoc experiment.",
        "This study does not apply temperature scaling [11] or Platt scaling [26]; those maps would be a separate post-hoc experiment.",
    ),
    (
        "X. Yan, C. Tang, and A. Shimada, “Recovering stranded discrimination in Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage,” arXiv:2606.14123, 2026. doi: 10.48550/arXiv.2606.14123",
        "X. Yan, C. Tang, and A. Shimada, “Recovering stranded discrimination in Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage,” arXiv:2606.14123, 2026, accepted at ECML PKDD 2026. doi: 10.48550/arXiv.2606.14123",
    ),
]

PLATT_REF = (
    "J. Platt, “Probabilistic outputs for support vector machines and "
    "comparisons to regularized likelihood methods,” in Advances in Large "
    "Margin Classifiers, 1999, pp. 61–74."
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
    missing = [old[:55] for old, n in counts.items() if n != 1]
    log.append("counts=" + str({old[:40]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing} {counts}")


def fix_murphy(doc, log: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        try:
            if para.Range.Tables.Count:
                continue
        except Exception:
            pass
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        if "new vector partition of the probability score" not in text:
            continue
        if text.startswith("A. H. Murphy"):
            log.append(f"murphy already A.H. i={i}")
            n += 1
            continue
        if not text.startswith("H. Murphy"):
            raise SystemExit(f"unexpected Murphy text i={i}: {text[:80]!r}")
        inner.Text = "A. H. Murphy" + text[len("H. Murphy") :]
        log.append(
            f"murphy i={i} list={para.Range.ListFormat.ListString!r} now={inner.Text[:40]!r}"
        )
        n += 1
    if n != 1:
        raise SystemExit(f"Murphy hits={n}")


def insert_platt(doc, log: list[str]) -> None:
    idx = None
    template = None
    for i in range(1, doc.Paragraphs.Count + 1):
        t = doc.Paragraphs(i).Range.Text
        if "starts a skill" in t and "Zhang" in t:
            idx = i
            template = doc.Paragraphs(i).Range.ListFormat.ListTemplate
            break
    if idx is None or template is None:
        raise SystemExit("Zhang [25] not found")
    doc.Paragraphs(idx).Range.InsertParagraphAfter()
    np = doc.Paragraphs(idx + 1)
    doc.Range(np.Range.Start, np.Range.End - 1).Text = PLATT_REF
    np.Range.ListFormat.ApplyListTemplateWithLevel(template, True, 0, 1)
    log.append(f"platt list={np.Range.ListFormat.ListString!r}")
    if np.Range.ListFormat.ListString.strip() != "[26]":
        raise SystemExit(f"expected [26], got {np.Range.ListFormat.ListString!r}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A23 — Contribution/reference nits

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged.

| # | Item | Action |
|---|---|---|
| 1 | [23] Murphy initials | Restored A. H. Murphy (Word had eaten A.) |
| 2 | [20] long-tail | Scoped to the XES3G5M log, not all educational logs |
| 3 | [15] venue | arXiv plus accepted at ECML PKDD 2026 |
| 4 | Platt 1999 | [26]; temperature scaling cited as [11] |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a23`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A23"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        word.Options.AutoFormatAsYouTypeApplyNumberedLists = False
    except Exception:
        log.append("could not disable auto numbered lists")
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_paragraphs(full_doc, log)
        fix_murphy(full_doc, log)
        insert_platt(full_doc, log)
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
    if "A. H. Murphy" not in full_t and "A. H.\nMurphy" not in full_t:
        # PDF may wrap; require A. and Murphy near [23]
        compact = "".join(full_t.split())
        if "A.H.Murphy" not in compact and "[23]A.H.Murphy" not in compact:
            if "[23]H.Murphy" in compact or "H. Murphy" in full_t and "A. H. Murphy" not in full_t:
                raise SystemExit("Murphy still missing A.")
    if "Platt scaling [26]" not in full_t and "Platt scaling\n[26]" not in full_t:
        if "[26]" not in full_t:
            raise SystemExit("Platt [26] missing")
    if "ECML PKDD 2026" not in full_t:
        raise SystemExit("[15] venue missing")
    if "The XES3G5M log exhibits a long tail" not in full_t:
        if "XES3G5M log exhibits" not in "".join(full_t.split()):
            raise SystemExit("long-tail scope missing")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")


if __name__ == "__main__":
    main()
