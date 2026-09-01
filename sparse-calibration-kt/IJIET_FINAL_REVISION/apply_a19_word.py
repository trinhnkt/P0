#!/usr/bin/env python3
"""A19: clear IJIET desk holds. No locked ASSISTments cells. No invented AI versions."""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import fitz
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
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a19"
LOG = HERE / "audit" / "apply_a19_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A19.md"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
REVIEW_ZIP = HERE / "output" / "code_for_review_anonymous.zip"
REVIEW_README = HERE / "output" / "README_CODE_FOR_REVIEW.txt"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

PAPER_TITLE = (
    "Reproducible Sparse-Concept and Calibration Diagnostics for Knowledge Tracing"
)
GITHUB = "https://github.com/trinhnkt/Sparse-Concept-and-Calibration"
GITHUB_WRAP = (
    "https:/\u200b/\u200bgithub.com/\u200btrinhnkt/\u200b"
    "Sparse-Concept-and-Calibration"
)

ETHICS_OLD = (
    "This study is a secondary analysis of publicly released, de-identified "
    "benchmark educational datasets (ASSISTments 2012, Junyi Academy, and "
    "XES3G5M). No new human participants were recruited and no classroom "
    "intervention was conducted. The work uses only records already released "
    "by the original dataset providers."
)
ETHICS_NEW = (
    ETHICS_OLD
    + " This manuscript is not under consideration for publication elsewhere."
)

DATA_NAMED = (
    "Code, data-preprocessing scripts, and evaluation pipelines are available "
    f"at {GITHUB_WRAP}. Source benchmark datasets are publicly released by "
    "their original providers."
)
DATA_BLIND = (
    "Anonymized code, data-preprocessing scripts, and evaluation pipelines "
    "are provided as an OJS supplementary file for double-blind review "
    "(code_for_review_anonymous.zip). Source benchmark datasets are publicly "
    "released by their original providers. A public repository will be "
    "released upon acceptance."
)

AI_OLD = (
    "During manuscript preparation, the authors used ChatGPT, Claude, and "
    "Google Antigravity for language polishing, formatting, consistency "
    "checking, and reproducibility prompt preparation. Exact ChatGPT, Claude, "
    "and Google Antigravity model identifiers were not retained; later "
    "revision used Cursor Grok 4.6. AI was not used to fabricate or alter "
    "experimental results. After using these tools, the authors reviewed and "
    "edited the content. The authors remain responsible for all content. "
    "Generative AI is not listed as a co-author."
)
AI_NEW = (
    "During manuscript preparation, the authors used Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using this tool, the authors reviewed "
    "and edited the content. The authors remain responsible for all content. "
    "Generative AI is not listed as a co-author."
)

COVER_TEXT = """Cover letter — International Journal of Information and Education Technology

Manuscript: Reproducible Sparse-Concept and Calibration Diagnostics for Knowledge Tracing
Corresponding author: Van-Hau Nguyen (haunv@utehy.edu.vn)
Date: 1 September 2026

Dear Editor,

Please consider the enclosed 8-page manuscript for IJIET. The paper is a
diagnostic evaluation of knowledge-tracing calibration on sparse concepts and
a simulated mastery gate. It does not propose a new KT architecture or a
classroom intervention.

Exclusive submission. This manuscript is not under consideration elsewhere.
A longer related write-up previously submitted to the Journal of Educational
Data Mining (JEDM) has been withdrawn by the authors. The IJIET submission
is the sole active version of this work.

Double-blind files. Please send reviewers main_ijiet_blind.pdf together with
supplementary.pdf and code_for_review_anonymous.zip. The named Word/PDF are
for the editorial office only. The zip excludes identity-bearing JEDM sources.

Data. Public code after review: https://github.com/trinhnkt/Sparse-Concept-and-Calibration
Datasets: ASSISTments 2012, Junyi Academy, and XES3G5M (original providers).

Generative AI. Cursor Grok 4.6 was used for language polishing, formatting,
consistency checking, and reproducibility-prompt preparation. AI was not used
to fabricate or alter results. Generative AI is not a co-author. ChatGPT,
Claude, and Google Antigravity are not listed because model versions were not
retained and IJIET ethics §6.3 requires a version with the tool name.

Sincerely,
Van-Hau Nguyen
Hung Yen University of Technology and Education
"""

REVIEW_README_TEXT = """Anonymous code bundle for IJIET double-blind review

This zip is the reviewer-facing code supplement. It does not contain:
- _archive/ (withdrawn JEDM sources and conversion snapshots)
- named IJIET Word sources
- multi-GB a2b data dumps or prediction files

It does contain local training/evaluation scripts, table CSVs used by the
8-page manuscript, and a2b Python (no processed logs). Public benchmarks
must be obtained from the original providers (ASSISTments 2012, Junyi
Academy, XES3G5M).

Do not treat the Transformer KT baseline as published SimpleKT.
"""


def stamp_pdf_metadata(path: Path, author: str) -> None:
    d = fitz.open(str(path))
    d.set_metadata(
        {
            "title": PAPER_TITLE,
            "author": author,
            "subject": "",
            "keywords": "",
            "creator": "",
            "producer": "",
            "creationDate": "",
            "modDate": "",
        }
    )
    tmp = path.with_suffix(".tmp.pdf")
    d.save(str(tmp), garbage=4, deflate=True)
    d.close()
    tmp.replace(path)


def patch_named(doc, log: list[str]) -> None:
    counts = {"ethics": 0, "data": 0, "ai": 0}
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        try:
            if para.Range.Tables.Count:
                continue
        except Exception:
            pass
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        if ETHICS_OLD in text and ETHICS_NEW not in text:
            inner.Text = text.replace(ETHICS_OLD, ETHICS_NEW)
            counts["ethics"] += 1
            log.append(f"ethics i={i}")
            continue
        if "Anonymized code, data-preprocessing" in text or "4open.science" in text:
            inner.Text = DATA_NAMED
            counts["data"] += 1
            log.append(f"data i={i}")
            continue
        if AI_OLD in text or (
            "ChatGPT, Claude, and Google Antigravity" in text
            and "Cursor Grok 4.6" in text
        ):
            inner.Text = AI_NEW
            counts["ai"] += 1
            log.append(f"ai i={i}")
    log.append(f"named_counts={counts}")
    if counts["ethics"] != 1 or counts["data"] != 1 or counts["ai"] != 1:
        raise SystemExit(f"named patch counts {counts}")


def patch_blind_data(doc, log: list[str]) -> None:
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
        if "github.com" in text or "Code, data-preprocessing scripts" in text:
            inner.Text = DATA_BLIND
            n += 1
            log.append(f"blind_data i={i}")
    log.append(f"blind_data_n={n}")
    if n != 1:
        raise SystemExit(f"blind data patch expected 1, got {n}")


def pack_review_zip(log: list[str]) -> None:
    root = HERE.parent
    skip_dir_names = {
        "data",
        "predictions",
        "checkpoints",
        "logs",
        "__pycache__",
        ".pytest_cache",
        "manuscript",
        "output",
        "anonymous_overlay",
        "_archive",
    }
    skip_suffix = {".pt", ".pth", ".pkl", ".bin", ".log"}
    skip_files = {
        "main_jedm.tex",
        "main_jedm.pdf",
        "main_ijiet_full.docx",
        "main_ijiet_full.doc",
    }
    skip_name_prefixes = ("generate_pdf_",)
    include_roots = [
        root / "src",
        HERE / "a2b",
        HERE / "analysis",
        HERE / "tables",
        HERE / "figures",
        HERE / "supplementary",
    ]
    include_files = [
        root / "requirements.txt",
        HERE / "README.md",
        HERE / "compile_manuscript.py",
        HERE / "a4_cluster_regression.py",
    ]
    REVIEW_ZIP.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with zipfile.ZipFile(REVIEW_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README_CODE_FOR_REVIEW.txt", REVIEW_README_TEXT)
        for path in include_files:
            if path.is_file() and path.name not in skip_files:
                arc = path.relative_to(root).as_posix()
                zf.write(path, arc)
                n += 1
        for base in include_roots:
            if not base.exists():
                continue
            if base.is_file():
                continue
            for p in base.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix.lower() in skip_suffix:
                    continue
                if p.name in skip_files:
                    continue
                if p.name.startswith(skip_name_prefixes):
                    continue
                if any(part in skip_dir_names for part in p.relative_to(base).parts):
                    continue
                if p.stat().st_size > 8_000_000:
                    continue
                arc = p.relative_to(root).as_posix()
                zf.write(p, arc)
                n += 1
    REVIEW_README.write_text(REVIEW_README_TEXT, encoding="utf-8")
    log.append(f"review_zip={REVIEW_ZIP.name} files={n} bytes={REVIEW_ZIP.stat().st_size}")


def write_changelog(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A19 — Desk-editor holds

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged. **No invented AI versions.**

## Dual submission

Authors withdrew the related JEDM manuscript. Ethical Statement now states
the IJIET paper is not under consideration elsewhere. Cover letter
(`output/cover_letter_ijiet.txt`) records the JEDM withdrawal. The article
text does not name JEDM.

## Data / identity

Named PDF points to `{GITHUB}`. Blind PDF does not use that URL (identity).
Reviewers receive `output/code_for_review_anonymous.zip` instead of the
leaking 4open.science snapshot. Named camera-ready “ignore older files”
sentence removed.

## Generative AI (§6.3)

Unversioned ChatGPT / Claude / Antigravity names removed. Cursor Grok 4.6
retained with uses. Do not re-insert tool names without a recorded version.

## Compile

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a19`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not FULL_DOCX.exists():
        raise SystemExit(f"missing {FULL_DOCX}")
    shutil.copy2(FULL_DOCX, BACKUP)
    COVER.parent.mkdir(parents=True, exist_ok=True)
    COVER.write_text(COVER_TEXT, encoding="utf-8")
    log: list[str] = ["A19"]
    pack_review_zip(log)
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_named(full_doc, log)
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
        if "trinhnkt" in (blind_doc.Content.Text or "").lower():
            raise RuntimeError("blind Word still contains trinhnkt")
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
    log.append(f"EXCL={'not under consideration' in full_t.lower()}")
    log.append(f"GH_NAMED={'github.com/trinhnkt' in full_t.replace(chr(0x200B), '')}")
    log.append(f"GH_BLIND={'trinhnkt' in blind_t.lower()}")
    log.append(f"CHAT_FULL={'ChatGPT' in full_t}")
    log.append(f"CHAT_BLIND={'ChatGPT' in blind_t}")
    log.append(f"GROK={'Grok 4.6' in full_t and 'Grok 4.6' in blind_t}")
    log.append(f"FOUR_OPEN_FULL={'4open.science' in full_t}")
    log.append(f"FOUR_OPEN_BLIND={'4open.science' in blind_t}")
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
    compact = "".join(full_t.split()).lower()
    compact_b = "".join(blind_t.split()).lower()
    if "Khanh-Trinh" in blind_t or "trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if "ChatGPT" in full_t or "ChatGPT" in blind_t:
        raise SystemExit("unversioned ChatGPT still present")
    if "notunderconsideration" not in compact:
        raise SystemExit("exclusive-submission sentence missing")
    if "github.com/trinhnkt" not in full_t.replace("\u200b", ""):
        raise SystemExit("named GitHub URL missing")
    if "4open.science" in full_t or "4open.science" in blind_t:
        raise SystemExit("leaking 4open URL still in PDF")
    if "grok4.6" not in compact or "grok4.6" not in compact_b:
        raise SystemExit("Grok 4.6 missing")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")


if __name__ == "__main__":
    main()
