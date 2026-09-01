#!/usr/bin/env python3
"""A28: remaining IJIET reviewer nits after A27.

Display τ vs S4 counterfactual; lead with 4/4 partitions; S4 in (iii);
TSCDA in title if 20 pt / 8 pages survive. No lock edits. No C.T.N. invention.
No Table 2 hash. No temperature/Platt. Does not name JEDM in the article.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import PAPER_TITLE, patch_blind_data, stamp_pdf_metadata  # noqa: E402
from apply_a24_format import style_labeled_block, style_title  # noqa: E402
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
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a28"
LOG = HERE / "audit" / "apply_a28_reviewer_nits_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A28.md"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
PDF_DUMP = HERE / "audit" / "_a28_pdf_text.txt"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

OLD_TITLE = (
    "Reproducible Sparse-Concept and Calibration Diagnostics for Knowledge Tracing"
)

REPLACEMENTS = [
    (
        "Sparse events never receive their own tuned τ. The display "
        "threshold is τ=0.7. On ASSISTments 2012 fold 0, T-KT ΔFAR stays "
        "positive at every locked grid point τ∈{0.5, 0.6, 0.7, 0.8} "
        "(Supplementary Table S3); the grid is not a search over sparse error. "
        "Supplementary Table S4 reuses the same frozen p for a Reliable-only "
        "advance rule and a mixed τ (sparse 0.8 / else 0.7); those policies "
        "are not trained.",
        "Sparse events never receive their own tuned τ in the display rule: "
        "Tables 5–6 use one locked global τ=0.7. On ASSISTments 2012 fold 0, "
        "T-KT ΔFAR stays positive at every locked grid point τ∈{0.5, 0.6, "
        "0.7, 0.8} (Supplementary Table S3); the grid is not a search over "
        "sparse error. Supplementary Table S4 is a counterfactual on the same "
        "frozen p (Reliable-only advance; mixed τ sparse 0.8 / else 0.7), not "
        "a trained or displayed mixed-τ rule.",
    ),
    (
        "(iii) a dataset-conditional gate finding on ASSISTments 2012 across "
        "four unique learner partitions (five runs, two sharing a split).",
        "(iii) a dataset-conditional gate finding on ASSISTments 2012 across "
        "four unique learner partitions (five runs, two sharing a split), with "
        "occupancy-policy counterfactuals that leave population FAR unchanged "
        "(Supplementary Table S4).",
    ),
    (
        "It is positive in 5/5 training runs (mean 0.047, sd 0.033) and "
        "positive in 4/4 unique partition-level estimates (mean 0.056, range "
        "0.015–0.087).",
        "It is positive in 4/4 unique partition-level estimates (mean 0.056, "
        "range 0.015–0.087) and in 5/5 training runs (mean 0.047, sd 0.033; "
        "two runs share a split).",
    ),
    (
        "with ΔFAR positive in 5/5 training runs and positive in 4/4 unique "
        "partition-level estimates",
        "with ΔFAR positive in 4/4 unique learner partitions (and in 5/5 "
        "training runs, two of which share a split)",
    ),
]


def find_labeled(doc, label: str) -> int:
    for i in range(1, min(20, doc.Paragraphs.Count + 1)):
        if para_text(doc.Paragraphs(i)).startswith(label):
            return i
    raise SystemExit(f"missing {label!r}")


def patch_title(doc, log: list[str]) -> None:
    raw = para_text(doc.Paragraphs(1)).strip()
    if raw != OLD_TITLE:
        raise SystemExit(f"unexpected title: {raw!r}")
    set_para_text(doc.Paragraphs(1), PAPER_TITLE)
    log.append(f"title -> {PAPER_TITLE}")


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
    log.append("counts=" + str({old[:45]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing} {counts}")


def patch_table6_cell(doc, log: list[str]) -> None:
    old_key = "5/5 runs; 4/4 unique"
    new = "4/4 unique partitions; 5/5 runs"
    hits = 0
    for t in range(1, doc.Tables.Count + 1):
        table = doc.Tables(t)
        for r in range(1, table.Rows.Count + 1):
            for c in range(1, table.Columns.Count + 1):
                try:
                    cell = table.Cell(r, c)
                except Exception:
                    continue
                inner = doc.Range(cell.Range.Start, cell.Range.End - 1)
                text = inner.Text.replace("\r", " ").replace("\x07", "")
                compact = " ".join(text.split())
                if old_key not in compact:
                    continue
                inner.Text = new
                hits += 1
                log.append(f"table{t} r{r}c{c} -> {new!r}")
    if hits != 1:
        raise SystemExit(f"Table 6 cell hits={hits}, expected 1")


def patch_cover() -> None:
    text = COVER.read_text(encoding="utf-8")
    if OLD_TITLE not in text:
        raise SystemExit("cover letter title missing")
    COVER.write_text(text.replace(OLD_TITLE, PAPER_TITLE, 1), encoding="utf-8")


def pdf_title_size(path: Path) -> float | None:
    d = fitz.open(str(path))
    title_sz = None
    for b in d[0].get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s.get("text", "").strip()
                if t.startswith("TSCDA") and title_sz is None:
                    title_sz = round(s["size"], 1)
    d.close()
    return title_sz


def write_changelog(pages: int, blind_pages: int, title_sz: float | None) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A28 — remaining reviewer nits

**Date:** 2026-09-01  
**Retrain:** no. **Locks:** unchanged. **No Table 2 hashes. No C.T.N. invention.**

| # | Nit | Action |
|---|---|---|
| 1 | III.H mixed-τ clash | Display rule = locked global τ=0.7; S4 = frozen-p counterfactual |
| 2 | V.A / Results 5/5-first | Lead with 4/4 unique partitions; 5/5 secondary |
| 3 | Table 6 cell | `4/4 unique partitions; 5/5 runs` |
| 4 | Contribution (iii) | Occupancy-policy counterfactuals leave population FAR unchanged (S4) |
| 5 | Title | `{PAPER_TITLE}` (20 pt check: {title_sz}) |
| skip | C.T.N. ICMJE | Not expanded without author-confirmed credit |
| skip | B2 / temperature | Not run |

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a28`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A28"]
    patch_cover()
    log.append("cover title")
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_title(full_doc, log)
        style_title(full_doc, log)
        patch_paragraphs(full_doc, log)
        patch_table6_cell(full_doc, log)
        abs_i = find_labeled(full_doc, "Abstract—")
        key_i = find_labeled(full_doc, "Keywords—")
        style_labeled_block(full_doc, abs_i, "Abstract—", log, "ABSTRACT")
        style_labeled_block(full_doc, key_i, "Keywords—", log, "KEYWORDS")
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
    PDF_DUMP.write_text(full_t, encoding="utf-8")
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    title_sz = pdf_title_size(FULL_PDF)
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    log.append(f"PDF_TITLE_SZ={title_sz}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"pdf_title_sz={title_sz}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    write_changelog(full_pages, blind_pages, title_sz)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if title_sz != 20.0:
        raise SystemExit(f"title still {title_sz} pt")
    if "counterfactual" not in full_t.lower():
        raise SystemExit("S4 counterfactual wording missing")
    if "positive in 4/4 unique learner partitions" not in full_t and (
        "positive in 4/4 unique partition-level estimates" not in full_t
    ):
        raise SystemExit("4/4-first wording missing")
    if "leave population FAR unchanged" not in full_t:
        raise SystemExit("contribution S4 clause missing")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if "more higher-error" in full_t:
        raise SystemExit("double comparative returned")
    if not PAPER_TITLE.split(":")[0] in full_t:
        raise SystemExit("TSCDA title missing from PDF")


if __name__ == "__main__":
    main()
