#!/usr/bin/env python3
"""A31: label ΔFAR 0.056 as 4-partition mean; 0.047 as five-run mean.

Does not change ECE/FAR locks or the seed-42 CI. Named + blind re-export.
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
from apply_a30_submission_pack import copy_ojs, export_named_doc, sync_submission_slots  # noqa: E402
from build_a16_double_blind import (  # noqa: E402
    AUTHORS_META,
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOC,
    FULL_DOCX,
    FULL_PDF,
    anonymize_blind,
    export_pdf,
    lock_checks,
    para_text,
    pdf_text,
    set_word_props,
)

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a31"
LOG = HERE / "audit" / "apply_a31_dfar_units_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A31.md"
PDF_DUMP = HERE / "audit" / "_a31_pdf_text.txt"
LOCKS = HERE / "audit" / "SCIENTIFIC_LOCKS.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

ABS_OLD = (
    "The primary check is 4/4 unique partitions (mean ΔFAR 0.047; five runs, "
    "two sharing a split); the seed-42 95% CI is [0.006, 0.138]."
)
ABS_NEW = (
    "The primary check is 4/4 unique learner partitions (partition-level mean "
    "ΔFAR 0.056, range 0.015–0.087); the five training runs that underlie those "
    "partitions have mean 0.047 (sd 0.033) because seeds 2025 and 2026 share one "
    "split. The seed-42 95% CI is [0.006, 0.138]."
)

CAP_OLD = (
    "Table 6. Gate robustness at τ=0.7 on ASSISTments 2012 (primary unit: four "
    "unique learner partitions). Five training runs (seeds 42, 2024, 2025, 2026, "
    "2027) across those partitions (2025 and 2026 share a split). Partition-level "
    "ΔFAR averages seeds 2025 and 2026 first; T-KT mean 0.056, range 0.015–0.087. "
    "Mean N, Nadvance, and Nincorrect are sparse-stratum denominators. "
    "GKT/CL4KT remain seed 42 only."
)
CAP_NEW = (
    "Table 6. Gate robustness at τ=0.7 on ASSISTments 2012 (primary unit: four "
    "unique learner partitions). T-KT Mean ΔFAR is the partition-level mean 0.056 "
    "(the SD column is the partition range 0.015–0.087) after averaging seeds "
    "2025 and 2026 first. The five training runs have mean 0.047 (sd 0.033) "
    "because those two seeds share one split. DKT remains a five-run summary. "
    "Mean N, Nadvance, and Nincorrect are sparse-stratum denominators. "
    "GKT/CL4KT remain seed 42 only."
)


def find_labeled(doc, label: str) -> int:
    for i in range(1, min(20, doc.Paragraphs.Count + 1)):
        if para_text(doc.Paragraphs(i)).startswith(label):
            return i
    raise SystemExit(f"missing {label!r}")


def cell_text(doc, cell) -> str:
    inner = doc.Range(cell.Range.Start, cell.Range.End - 1)
    return " ".join(inner.Text.replace("\r", " ").replace("\x07", "").split())


def set_cell(doc, cell, text: str) -> None:
    inner = doc.Range(cell.Range.Start, cell.Range.End - 1)
    inner.Text = text


def patch_paragraphs(doc, log: list[str]) -> None:
    pairs = [(ABS_OLD, ABS_NEW), (CAP_OLD, CAP_NEW)]
    counts = {old: 0 for old, _ in pairs}
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
        for old, new in pairs:
            if old in text:
                text = text.replace(old, new, 1)
                counts[old] += 1
                changed = True
        if changed:
            inner.Text = text
            log.append(f"para i={i}")
    missing = [old[:60] for old, n in counts.items() if n != 1]
    log.append("para_counts=" + str({old[:40]: n for old, n in counts.items()}))
    if missing:
        raise SystemExit(f"expected 1 hit each: {missing}")


def patch_table6_tkt(doc, log: list[str]) -> None:
    hits = 0
    for t in range(1, doc.Tables.Count + 1):
        table = doc.Tables(t)
        for r in range(1, table.Rows.Count + 1):
            try:
                runs = cell_text(doc, table.Cell(r, 4))
            except Exception:
                continue
            if "4/4 unique partitions" not in runs:
                continue
            mean = cell_text(doc, table.Cell(r, 2))
            sd = cell_text(doc, table.Cell(r, 3))
            if mean != "0.047" or sd != "0.033":
                raise SystemExit(f"T-KT cells unexpected mean={mean!r} sd={sd!r}")
            set_cell(doc, table.Cell(r, 2), "0.056")
            set_cell(doc, table.Cell(r, 3), "0.015–0.087")
            set_cell(doc, table.Cell(r, 4), "4/4 unique partitions")
            hits += 1
            log.append(f"table{t} r{r} T-KT 0.056 / range / 4/4")
    if hits != 1:
        raise SystemExit(f"Table 6 T-KT hits={hits}, expected 1")


def pdf_title_size(path: Path) -> float | None:
    d = fitz.open(str(path))
    title_sz = None
    for b in d[0].get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s.get("text", "").strip()
                if t.startswith("Reproducible Sparse") and title_sz is None:
                    title_sz = round(s["size"], 1)
    d.close()
    return title_sz


def patch_locks_note() -> None:
    text = LOCKS.read_text(encoding="utf-8")
    old = (
        "Gate \\(\\tau=0.7\\); FAR = \\(P(y=0\\mid p\\ge\\tau)\\). Seed-42 T-KT FAR "
        "0.196 dense → 0.268 sparse. Five-run \\(\\Delta\\)FAR mean 0.047, sd 0.033."
    )
    new = (
        "Gate \\(\\tau=0.7\\); FAR = \\(P(y=0\\mid p\\ge\\tau)\\). Seed-42 T-KT FAR "
        "0.196 dense → 0.268 sparse. Primary robustness unit: four unique "
        "partitions, mean \\(\\Delta\\)FAR 0.056 (range 0.015–0.087) after averaging "
        "seeds 2025/2026 first. Five-run mean 0.047, sd 0.033 (not five "
        "independent folds)."
    )
    if old not in text:
        if "Primary robustness unit" in text:
            return
        raise SystemExit("SCIENTIFIC_LOCKS gate line missing")
    LOCKS.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_changelog(pages: int, blind_pages: int, title_sz: float | None) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A31 — ΔFAR unit labels

**Date:** 2026-09-02
**Retrain:** no. **Locks:** ECE 0.1136 / 0.2280; FAR 0.196 / 0.268; CI [0.006, 0.138].

| # | Edit | Action |
|---|---|---|
| 1 | Abstract | Primary check = 4/4 partitions, mean 0.056 (range 0.015–0.087); five-run 0.047 (sd 0.033) secondary |
| 2 | Table 6 T-KT | Mean 0.056; SD column = partition range; Runs = 4/4 unique partitions only |
| 3 | Table 6 caption | Five-run 0.047/0.033 moved out of the 4/4 cell |

Named/blind: {pages} / {blind_pages} pages. Title size: {title_sz}.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a31`.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not FULL_DOCX.exists():
        raise SystemExit(f"missing {FULL_DOCX}")
    shutil.copy2(FULL_DOCX, BACKUP)
    log: list[str] = ["A31"]
    patch_locks_note()
    log.append("locks note")

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        style_title(full_doc, log)
        patch_paragraphs(full_doc, log)
        patch_table6_tkt(full_doc, log)
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

    export_named_doc(log)
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

    bad_abs = "4/4 unique partitions (mean ΔFAR 0.047" in full_t
    if bad_abs or "4/4 unique partitions; 5/5" in full_t:
        raise SystemExit("0.047 still labeled as 4/4")
    if "partition-level mean" not in full_t or "0.056" not in full_t:
        raise SystemExit("partition mean 0.056 missing")
    if "mean 0.047 (sd 0.033)" not in full_t and "have mean 0.047" not in full_t:
        raise SystemExit("five-run 0.047 missing")
    if "[0.006, 0.138]" not in full_t:
        raise SystemExit("seed-42 CI missing")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit(f"lock checks failed {full_locks} {blind_locks}")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if title_sz != 20.0:
        raise SystemExit(f"title still {title_sz} pt")

    copy_ojs(log)
    sync_submission_slots(log)
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


if __name__ == "__main__":
    main()
