#!/usr/bin/env python3
"""IJIET-20: add UKT 2025 and Mitton 2026 cites; Table 2 pointer; RCT expansion.

Does not change table cells, Fig. 1, or ECE/FAR numbers.
Does not restore the IJIET-18 snapshot.
"""
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
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step20_verify.txt"
FULLTEXT = ROOT / "IJIET_SUBMISSION" / "audit" / "step20_fulltext.txt"

sys.path.insert(0, str(SRC))
from prepare_step15 import (  # noqa: E402
    AUTHORS_META,
    IDENTIFYING,
    KEEP_IN_BLIND,
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
from prepare_step17 import anonymize_blind  # noqa: E402
from prepare_step18 import restore_h2  # noqa: E402

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_END = 0
WD_CHARACTER = 1

UKT_SENTENCE = (
    " Uncertainty-aware models such as UKT represent knowledge states as "
    "distributions [21]; they are architecture proposals evaluated mainly on "
    "population ranking, not a train-only frequency-stratum decision audit."
)
MITTON_SENTENCE = (
    " Selective-prediction layers defer the most uncertain next-response scores "
    "to a teacher [22]. Abstention is complementary to a locked global threshold: "
    "this study does not abstain, and it reports the false-advance rate of the "
    "advances that a fixed τ would still make, stratified by train-only KC frequency."
)
REF21 = (
    "W. Cheng, H. Du, C. Li, E. Ni, L. Tan, T. Xu, and Y. Ni, “Uncertainty-aware "
    "Knowledge Tracing,” in Proc. AAAI Conference on Artificial Intelligence, "
    "vol. 39, no. 27, pp. 27905–27913, 2025. doi: 10.1609/aaai.v39i27.35007"
)
REF22 = (
    "J. Mitton, P. Bhattacharyya, R. Abboud, and S. Woodhead, “Knowing when to "
    "defer: Selective prediction for responsible Knowledge Tracing,” in Proc. "
    "Impactful and Responsible AI Systems for Education Workshop, Proc. Machine "
    "Learning Research, vol. 339, 2026, pp. 22–42."
)


def _replace_once(doc, old: str, new: str, tag: str, lines: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if old not in raw:
            continue
        set_para_text(doc.Paragraphs(i), raw.replace(old, new, 1))
        n += 1
        lines.append(f"{tag} i={i}")
        break
    if n != 1:
        raise RuntimeError(f"{tag}: expected 1 hit for {old[:60]!r}, got {n}")


def patch_prose(doc, lines: list[str]) -> None:
    already = any(
        "UKT represent knowledge states" in para_text(doc.Paragraphs(i))
        for i in range(1, doc.Paragraphs.Count + 1)
    )
    if already:
        lines.append("PROSE already applied")
        return

    _replace_once(
        doc,
        "Across this line of work, the primary reported statistic remains population AUC.",
        "Across this line of work, the primary reported statistic remains population AUC."
        + UKT_SENTENCE,
        "UKT_CITE",
        lines,
    )
    _replace_once(
        doc,
        "reported on the pooled population, not on train-only frequency strata.",
        "reported on the pooled population, not on train-only frequency strata."
        + MITTON_SENTENCE,
        "MITTON_CITE",
        lines,
    )
    _replace_once(
        doc,
        "Recovered hyperparameters follow; missing fields are marked NOT RECOVERED and are not imputed.",
        "Table 2 reports recovered training settings; missing fields are marked "
        "NOT RECOVERED and are not imputed.",
        "TABLE2_CITE",
        lines,
    )
    _replace_once(
        doc,
        "This is a simulated decision error, not an instructional RCT.",
        "This is a simulated decision error, not an instructional randomized "
        "controlled trial (RCT).",
        "RCT_EXPAND",
        lines,
    )


def style_ref(para) -> None:
    try:
        para.Style = "References"
    except Exception:
        pass
    para.Range.Font.Name = "Times New Roman"
    para.Range.Font.Size = 8


def insert_new_refs(doc, lines: list[str]) -> None:
    if any(
        "Uncertainty-aware Knowledge Tracing" in para_text(doc.Paragraphs(i))
        and "Cheng" in para_text(doc.Paragraphs(i))
        for i in range(1, doc.Paragraphs.Count + 1)
    ):
        lines.append("REFS already applied")
        return

    idx20 = None
    for i in range(1, doc.Paragraphs.Count + 1):
        raw = para_text(doc.Paragraphs(i))
        if "XES3G5M: A Knowledge Tracing benchmark dataset" in raw:
            idx20 = i
            break
    if idx20 is None:
        raise RuntimeError("reference [20] not found")

    list_str = str(doc.Paragraphs(idx20).Range.ListFormat.ListString or "")
    lines.append(f"REF20_LIST={list_str!r}")

    def insert_after(after_i: int, text: str, numbered: bool) -> int:
        rng = doc.Paragraphs(after_i).Range
        rng.Collapse(WD_COLLAPSE_END)
        rng.InsertParagraphAfter()
        new_i = after_i + 1
        para = doc.Paragraphs(new_i)
        style_ref(para)
        body = text if numbered else text
        set_para_text(para, body)
        style_ref(para)
        return new_i

    # Current refs store the bracket in the auto-list, not in the paragraph text
    # (PDF still prints [20]). Match that: do not prefix "[21]" in the text.
    numbered_in_text = para_text(doc.Paragraphs(idx20)).lstrip().startswith("[20]")
    t21 = ("[21] " + REF21) if numbered_in_text else REF21
    t22 = ("[22] " + REF22) if numbered_in_text else REF22
    i21 = insert_after(idx20, t21, numbered_in_text)
    insert_after(i21, t22, numbered_in_text)
    lines.append(f"INSERTED_REFS after={idx20} numbered_in_text={numbered_in_text}")


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"Missing {FULL_DOCX}")
    lines: list[str] = ["IJIET-20 literature positioning update"]
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    saved = False
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_prose(full_doc, lines)
        insert_new_refs(full_doc, lines)
        restore_h1(full_doc)
        restore_h2(full_doc, lines)
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
            f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count} "
            f"SECTIONS={full_doc.Sections.Count}"
        )

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        restore_h1(blind_doc)
        restore_h2(blind_doc, lines)
        neutralize_table_lists(blind_doc)
        set_word_props(blind_doc, "", "")
        blind_doc.SaveAs2(str(BLIND_DOCX), WD_FORMAT_XML)
        blind_doc.SaveAs2(str(BLIND_DOC), WD_FORMAT_DOC)
        export_pdf(blind_doc, BLIND_PDF)
        if full_doc.InlineShapes.Count != 1 or full_doc.Tables.Count < 8:
            raise RuntimeError("structure lost")
        saved = True
    except Exception as exc:
        REPORT.write_text("\n".join(lines) + "\nERROR: " + str(exc) + "\n", encoding="utf-8")
        raise
    finally:
        if full_doc is not None:
            full_doc.Close(WD_SAVE if saved else 0)
        if blind_doc is not None:
            blind_doc.Close(WD_SAVE if saved else 0)
        word.Quit()

    stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    stamp_pdf_metadata(BLIND_PDF, "")
    full_t = pdf_text(FULL_PDF)
    blind_t = pdf_text(BLIND_PDF)
    FULLTEXT.write_text(full_t, encoding="utf-8")
    compact_t = compact(full_t)
    full_pages = fitz.open(str(FULL_PDF)).page_count
    blind_pages = fitz.open(str(BLIND_PDF)).page_count
    lines.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    checks = {
        "ece": "0.1136" in full_t and "0.2280" in full_t,
        "far": "0.196" in full_t and "0.268" in full_t,
        "ukt": "UKT" in full_t and "[21]" in full_t,
        "mitton": "Selective-prediction" in full_t or "selective prediction" in full_t.lower(),
        "ref21": "27905" in full_t,
        "ref22": "339" in compact_t and "Mitton" in full_t,
        "table2": "table2reportsrecovered" in compact_t.lower(),
        "rct": "randomized controlled trial" in full_t.lower(),
        "authors": "Khanh-Trinh" in full_t,
        "blind": not hits(blind_t, IDENTIFYING),
        "fig": "Fig. 1." in full_t,
        "t8": "TABLE 8." in full_t.upper() or "Table 8." in full_t,
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
        raise RuntimeError(f"blind dropped {keep_ok}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
