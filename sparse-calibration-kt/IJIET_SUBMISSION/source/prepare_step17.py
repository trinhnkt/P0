#!/usr/bin/env python3
"""IJIET-17: fix remaining QA issues (no invented ORCID/IRB/dates/numbers)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import fitz
import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
FULL_DOCX = SRC / "main_ijiet_full.docx"
FULL_DOC = SRC / "main_ijiet_full.doc"
BLIND_DOCX = SRC / "main_ijiet_blind.docx"
BLIND_DOC = SRC / "main_ijiet_blind.doc"
OUT_DIR = ROOT / "IJIET_SUBMISSION" / "output"
FULL_PDF = OUT_DIR / "main_ijiet_full.pdf"
BLIND_PDF = OUT_DIR / "main_ijiet_blind.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step17_verify.txt"

sys.path.insert(0, str(SRC))
from prepare_step15 import (  # noqa: E402
    ANON_ACK,
    ANON_AFFIL,
    ANON_AUTHORS,
    ANON_CONTRIB,
    AUTHORS_META,
    IDENTIFYING,
    KEEP_IN_BLIND,
    TITLE,
    compact,
    export_pdf,
    hits,
    neutralize_table_lists,
    para_text,
    pdf_text,
    set_para_text,
    set_word_props,
    stamp_pdf_metadata,
    token_present,
)
from prepare_step16 import restore_h1  # noqa: E402

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_REPLACE_ALL = 2
WD_FIND_CONTINUE = 1
WD_COLLAPSE_END = 0
WD_ALIGN_CENTER = 1
WD_TAB_CENTER = 1
WD_TAB_RIGHT = 2

PARA_ETHICS = (
    "This study is a secondary analysis of publicly released, de-identified "
    "benchmark educational datasets (ASSISTments 2012, Junyi Academy, and "
    "XES3G5M). No new human participants were recruited and no classroom "
    "intervention was conducted. The work uses only records already released "
    "by the original dataset providers."
)
PARA_AI = (
    "During manuscript preparation, the authors used ChatGPT, Claude, and "
    "Google Antigravity for language polishing, formatting, consistency "
    "checking, and reproducibility prompt preparation. Tool versions were not "
    "recorded. These tools were not used to fabricate or alter experimental "
    "results. After using these tools, the authors reviewed and edited the "
    "content. The authors remain responsible for all content. Generative AI "
    "is not listed as a co-author."
)
CAP_SETTINGS = (
    "Table 2. Recovered training settings for the main baselines. "
    "NOT RECOVERED cells were not imputed."
)
CAP_GATE = (
    "Table 5. Simulated gate at τ=0.7, ASSISTments 2012 fold 0 (seed 42). "
    "FAR, Excess FAR, and Miss as defined in Section III.H. FAR 95% CIs: "
    "KC-cluster percentile, B=2000. Not a classroom trial."
)
CAP_ROBUST = (
    "Table 6. Gate robustness at τ=0.7 on ASSISTments 2012. Five training "
    "runs (seeds 42, 2024, 2025, 2026, 2027) across four unique learner "
    "partitions (2025 and 2026 share a split). Mean N, N_advance, and "
    "N_incorrect are sparse-stratum denominators. GKT/CL4KT remain seed 42 only."
)


def shift_table_text(raw: str) -> str:
    if raw.startswith("Table 2. Recovered") or raw.upper().startswith("TABLE 2. RECOVERED"):
        return raw
    out = raw.replace("Tables 4–5", "Tables 5–6").replace("Tables 4-5", "Tables 5–6")
    for old, new in ((7, 8), (6, 7), (5, 6), (4, 5), (3, 4), (2, 3)):
        out = out.replace(f"Table {old}", f"Table {new}")
        out = out.replace(f"TABLE {old}", f"TABLE {new}")
    return out


def renumber_tables(doc, lines: list[str]) -> None:
    n_body = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        new = shift_table_text(raw)
        if new != raw:
            set_para_text(doc.Paragraphs(i), new)
            n_body += 1
    n_cap = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Recovered training settings"):
            set_para_text(doc.Paragraphs(i), CAP_SETTINGS)
            try:
                doc.Paragraphs(i).Style = "Table Title"
            except Exception:
                pass
            doc.Paragraphs(i).Range.Font.Size = 8
            doc.Paragraphs(i).Alignment = WD_ALIGN_CENTER
            n_cap += 1
            lines.append(f"SETTINGS_CAP i={i}")
        elif raw.startswith("Table 5. Simulated gate") or raw.upper().startswith(
            "TABLE 5. SIMULATED GATE"
        ):
            set_para_text(doc.Paragraphs(i), CAP_GATE)
            try:
                doc.Paragraphs(i).Style = "Table Title"
            except Exception:
                pass
            doc.Paragraphs(i).Range.Font.Size = 8
            n_cap += 1
            lines.append(f"GATE_CAP i={i}")
        elif raw.startswith("Table 6. Gate robustness") or raw.upper().startswith(
            "TABLE 6. GATE ROBUSTNESS"
        ):
            set_para_text(doc.Paragraphs(i), CAP_ROBUST)
            try:
                doc.Paragraphs(i).Style = "Table Title"
            except Exception:
                pass
            doc.Paragraphs(i).Range.Font.Size = 8
            n_cap += 1
            lines.append(f"ROBUST_CAP i={i}")
    lines.append(f"TABLE_SHIFTS={n_body} CAPTIONS_PATCHED={n_cap}")


def insert_ece_equation(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Let y") and "expected calibration error" in raw and "ECE =" not in raw:
            lines.append(f"ECE_EQ_ALREADY i={i}")
            return
        if not (raw.startswith("Let y") and "ECE =" in raw and "Brier" in raw):
            continue
        marker = "The Brier score"
        idx = raw.find(marker)
        if idx < 0:
            raise RuntimeError("ECE para missing Brier continuation")
        rest = raw[idx:]
        pre = (
            "Let y∈{0,1} be next-response correctness and p∈[0,1] the predicted "
            "probability. With M=15 equal-width bins, expected calibration error "
            "(ECE) is"
        )
        set_para_text(doc.Paragraphs(i), pre)
        rng = doc.Paragraphs(i).Range
        rng.Collapse(WD_COLLAPSE_END)
        rng.InsertParagraphAfter()
        eq_i = i + 1
        eq_para = doc.Paragraphs(eq_i)
        try:
            eq_para.Style = "equation"
        except Exception:
            pass
        pf = eq_para.Range.ParagraphFormat
        try:
            pf.TabStops.ClearAll()
            pf.TabStops.Add(121.8, WD_TAB_CENTER)
            pf.TabStops.Add(243.65, WD_TAB_RIGHT)
        except Exception:
            pass
        set_para_text(eq_para, "\tECE = Σ_m (n_m / N) |acc_m − conf_m|\t(1)")
        eq_para.Range.Font.Name = "Times New Roman"
        eq_para.Range.Font.Size = 10
        eq_para.Range.Font.Italic = False
        eq_para.Range.Font.Bold = False
        rng2 = eq_para.Range
        rng2.Collapse(WD_COLLAPSE_END)
        rng2.InsertParagraphAfter()
        brier = doc.Paragraphs(eq_i + 1)
        try:
            brier.Style = "Text"
        except Exception:
            pass
        set_para_text(brier, rest)
        lines.append(f"ECE_EQ i={eq_i}")
        return
    raise RuntimeError("ECE paragraph not found")


def patch_end_matter(doc, lines: list[str]) -> None:
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if "AUTHOR ACTION REQUIRED" in raw or (
            raw.startswith("This study is a secondary analysis")
            and "ASSISTments 2012" in raw
        ):
            set_para_text(doc.Paragraphs(i), PARA_ETHICS)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"ETHICS i={i}")
        if raw.startswith("During manuscript preparation"):
            set_para_text(doc.Paragraphs(i), PARA_AI)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"AI i={i}")


def anonymize_blind(doc, lines: list[str]) -> None:
    delete_i: list[int] = []
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if raw.startswith("Khanh-Trinh Nguyen") or "Van-Hau Nguyen" in raw:
            set_para_text(doc.Paragraphs(i), ANON_AUTHORS)
            try:
                doc.Paragraphs(i).Style = "Style Author + (Asian) MS Mincho"
            except Exception:
                pass
            lines.append(f"ANON_AUTHORS i={i}")
        elif "Hung Yen University" in raw:
            set_para_text(doc.Paragraphs(i), ANON_AFFIL)
            lines.append(f"ANON_AFFIL i={i}")
        elif "Academy of Military Science" in raw:
            delete_i.append(i)
            lines.append(f"DEL_AFFIL2 i={i}")
        elif raw.startswith("Email:"):
            delete_i.append(i)
            lines.append(f"DEL_EMAIL i={i}")
        elif "Corresponding author" in raw:
            delete_i.append(i)
            lines.append(f"DEL_CORR i={i}")
        elif raw.startswith("Manuscript received"):
            delete_i.append(i)
            lines.append(f"DEL_DATES i={i}")
        elif raw.startswith("K.-T.N.:"):
            set_para_text(doc.Paragraphs(i), ANON_CONTRIB)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"ANON_CONTRIB i={i}")
        elif "authors’ respective institutions" in raw or (
            "authors' respective institutions" in raw
        ):
            set_para_text(doc.Paragraphs(i), ANON_ACK)
            try:
                doc.Paragraphs(i).Style = "Text"
            except Exception:
                pass
            lines.append(f"ANON_ACK i={i}")
    for i in reversed(delete_i):
        try:
            doc.Paragraphs(i).Range.Delete()
        except Exception as exc:
            lines.append(f"DEL_FAIL i={i} {exc}")


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"Missing {FULL_DOCX}")
    lines: list[str] = []
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_end_matter(full_doc, lines)
        insert_ece_equation(full_doc, lines)
        renumber_tables(full_doc, lines)
        restore_h1(full_doc)
        neutralize_table_lists(full_doc)
        set_word_props(
            full_doc,
            AUTHORS_META,
            "Hung Yen University of Technology and Education",
        )
        full_doc.SaveAs2(str(FULL_DOCX), WD_FORMAT_XML)
        full_doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        export_pdf(full_doc, FULL_PDF)
        lines.append(
            f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count}"
        )

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        restore_h1(blind_doc)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
        lines.append(
            f"BLIND_TABLES={blind_doc.Tables.Count} FIGS={blind_doc.InlineShapes.Count}"
        )
        if full_doc.InlineShapes.Count != 1 or blind_doc.InlineShapes.Count != 1:
            raise RuntimeError("figure count changed")
        if full_doc.Tables.Count < 8 or blind_doc.Tables.Count < 8:
            raise RuntimeError("table count dropped")
    finally:
        if full_doc is not None:
            full_doc.Close(WD_SAVE)
        if blind_doc is not None:
            blind_doc.Close(WD_SAVE)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    full_pages = fitz.open(str(FULL_PDF)).page_count
    blind_pages = fitz.open(str(BLIND_PDF)).page_count
    lines.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")

    compact_t = compact(full_t)
    checks = {
        "no_author_action": "AUTHOR ACTION REQUIRED" not in full_t,
        "no_ai_placeholder": "version to be confirmed" not in full_t.lower(),
        "table2_settings": "RECOVERED TRAINING SETTINGS" in full_t.upper(),
        "table3_auc": "Table 3 reports overall" in full_t
        or "TABLE 3 REPORTS OVERALL" in full_t.upper(),
        "table8": "Table 8." in full_t or "TABLE 8." in full_t.upper(),
        "no_table2_auc": "Table 2 reports overall" not in full_t,
        "ece_eq": "(1)" in full_t and "ECE =" in full_t,
        "ethics_ok": "Nonewhumanparticipantswererecruited" in compact_t,
        "ece_cells": "0.1136" in full_t and "0.2280" in full_t,
        "far_cells": "0.196" in full_t and "0.268" in full_t,
        "authors": "Khanh-Trinh" in full_t,
        "blind_clean": not hits(blind_t, IDENTIFYING),
        "blind_anon": "Anonymous Authors" in blind_t,
        "blind_no_blank_email": "Email:" not in blind_t,
    }
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    lines.append(f"CHECKS={checks}")
    lines.append(f"KEEP={keep_ok}")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise RuntimeError(f"verify failed: {failed}")
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind dropped tokens {keep_ok}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
