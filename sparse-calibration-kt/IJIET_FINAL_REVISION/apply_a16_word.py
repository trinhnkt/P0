#!/usr/bin/env python3
"""A16: A2B XES cells, received date, IRT split, AI wording. ASSISTments locks untouched."""
from __future__ import annotations

import shutil
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a16"
FIG = HERE / "figures" / "fig1_kc_and_train_volume.png"
LOG = HERE / "audit" / "apply_a16_word_log.txt"
WD_INLINE_PICTURE = 3

PROSE: list[tuple[str, str]] = [
    ("and 7,953,709 (XES3G5M)", "and 6,413,353 (XES3G5M)"),
    (
        "flattened to one row per sequence position.",
        "flattened to one row per unmasked sequence position. Positions with selectmask≠1, KC=−1, question=−1, or a label outside {0,1} are dropped before counting and scoring.",
    ),
    (
        "Table 1 instead lists 866 KCs and 7.95M interactions because flattening kc_level sequences (i) expands multi-KC questions into one row per listed concept and (ii) retains sequence-padding tokens coded skill_id=−1 (with matching question_id=−1). Unique kc_id including that padding token is 866; excluding it is 865. Unique item_id including −1 is 7,653. Subsequent preprocessing dropped 0 rows. We do not retabulate Table 1 to the question-level official totals.",
        "Table 1 lists 865 KCs and 6,413,353 valid KC-level rows: flattening still expands multi-KC questions into one row per listed concept, but padding tokens are excluded. Unique item_id is 7,652. Learner-based fold-0 test events are 1,282,422.",
    ),
    (
        "DKT 0.857 versus 0.817; T-KT 0.847 versus 0.755",
        "DKT 0.858 versus 0.818; T-KT 0.847 versus 0.752",
    ),
    (
        "(0.1145, 0.1114, 0.1248) despite Reliable sparse occupancy (N=2,010)",
        "(0.1176, 0.1129, 0.1254) despite Reliable sparse occupancy (N=1,969)",
    ),
    (
        "On XES3G5M, T-KT ΔFAR is negative on all five runs, but ΔMiss is positive on all five (mean +0.112): among actual incorrect answers, the system still advances more often on sparse than on dense KCs.",
        "On XES3G5M, T-KT ΔFAR is negative on all five runs (mean −0.017), and ΔMiss is also negative (mean −0.183): after padding tokens are excluded, sparse KCs do not show a higher miss rate than dense KCs.",
    ),
    (
        "yet T-KT ECE does not degrade—while miss rates still can.",
        "yet T-KT ECE does not degrade.",
    ),
    ("and 1,263 representing 830)", "and 829 unique KCs)"),
    (
        "and −0.069 [−0.123, −0.015] on XES3G5M",
        "and −0.028 [−0.042, −0.014] on XES3G5M",
    ),
    (
        "Difficulty is independently associated on ASSISTments and Junyi. Learner exposure is independently associated only on ASSISTments (+0.016 [0.004, 0.027]).",
        "Difficulty is independently associated on all three datasets. Learner exposure is independently associated on ASSISTments (+0.016 [0.004, 0.027]).",
    ),
    (
        "XES3G5M T-KT shows a positive Delta ECE at 50 rows (+0.032 [+0.021, +0.043]) and at 100 rows (Supplementary Table S2); those cells are not omitted.",
        "XES3G5M T-KT shows a positive Delta ECE at 50 rows (+0.110 [+0.071, +0.156]) and at 100 rows (Supplementary Table S2); XES3G5M DKT at 500 rows is also positive (+0.142 [+0.104, +0.189]). Those cells are not omitted.",
    ),
    (
        "on XES3G5M, ΔFAR and ΔMiss can move in opposite directions, so a flat ECE is not a flat miss rate.",
        "on XES3G5M, T-KT ΔFAR and ΔMiss are both negative after padding is excluded, so a flat ECE is not by itself a decision-error result.",
    ),
    (
        "Manuscript received Month date, 2026; revised Month date, 2026; accepted Month date, 2026",
        "Manuscript received September 1, 2026; revised Month date, 2026; accepted Month date, 2026",
    ),
    (
        "[AUTHOR ACTION REQUIRED: confirm exact AI tool/model/version before IJIET submission] AI was not used to fabricate or alter experimental results.",
        "Exact model identifiers for ChatGPT, Claude, and Google Antigravity were not retained in project records; later revision used Cursor Grok 4.6. AI was not used to fabricate or alter experimental results.",
    ),
]


def set_inner(doc, rng, text: str) -> None:
    doc.Range(rng.Start, rng.End - 1).Text = text


def cell_txt(cell) -> str:
    return cell.Range.Text.replace("\r", "").replace("\x07", "").strip()


def in_table(para) -> bool:
    try:
        return int(para.Range.Tables.Count) > 0
    except Exception:
        return False


def patch_prose(doc, log: list[str]) -> None:
    remaining = list(PROSE)
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        if in_table(para):
            continue
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        changed = False
        still = []
        for old, new in remaining:
            if old in text:
                text = text.replace(old, new, 1)
                log.append(f"prose {old[:55]!r}")
                changed = True
            else:
                still.append((old, new))
        remaining = still
        if changed:
            inner.Text = text
    if remaining:
        raise SystemExit("unreplaced prose: " + " | ".join(repr(o[:60]) for o, _ in remaining))


def split_irt(doc, log: list[str]) -> None:
    n = 0
    for i in range(1, doc.Paragraphs.Count + 1):
        para = doc.Paragraphs(i)
        if in_table(para):
            continue
        inner = doc.Range(para.Range.Start, para.Range.End - 1)
        text = inner.Text
        key = "selection by validation AUC). In our implementation,"
        if key not in text:
            continue
        inner.Text = text.replace(key, "selection by validation AUC).\rIn our implementation,", 1)
        n += 1
    if n != 1:
        raise SystemExit(f"IRT split={n}")
    log.append("split IRT from GKT/CL4KT")


def patch_tables(doc, log: list[str]) -> None:
    n = 0

    def sub(cell, olds: set[str], new: str) -> None:
        nonlocal n
        v = cell_txt(cell)
        if v in olds:
            set_inner(doc, cell.Range, new)
            n += 1

    for table in doc.Tables:
        for r in range(1, table.Rows.Count + 1):
            raw = table.Rows(r).Range.Text.replace("\r", " ").replace("\x07", " ")
            ncol = table.Rows(r).Cells.Count
            cells = [table.Cell(r, c) for c in range(1, ncol + 1)]
            if "XES3G5M" in raw and "18,066" in raw:
                for c in cells:
                    sub(c, {"866"}, "865")
                    sub(c, {"7.95M"}, "6.41M")
                    sub(c, {"1,589,145"}, "1,282,422")
            if "XES3G5M" in raw and "DKT" in raw and "0.8171" in raw:
                for c in cells:
                    sub(c, {"0.8171±0.0022"}, "0.8180±0.0009")
                    sub(c, {"0.8327±0.0032"}, "0.8321±0.0015")
            if "XES3G5M" in raw and "T-KT" in raw and "0.7557" in raw:
                for c in cells:
                    sub(c, {"0.7557±0.0013"}, "0.7536±0.0010")
                    sub(c, {"0.8067±0.0037"}, "0.8057±0.0029")
            if "XES3G5M" in raw and "dense" in raw and "1,268,696" in raw:
                for c in cells:
                    sub(c, {"1,268,696"}, "1,269,345")
                    sub(c, {"0.1145±0.0011"}, "0.1176±0.0014")
            if "XES3G5M" in raw and "medium" in raw and "12,980" in raw:
                for c in cells:
                    sub(c, {"12,980"}, "12,889")
                    sub(c, {"0.1114±0.0076"}, "0.1129±0.0061")
            if "XES3G5M" in raw and "sparse" in raw and "2,010" in raw and "0.1248" in raw:
                for c in cells:
                    sub(c, {"2,010"}, "1,969")
                    sub(c, {"0.1248±0.0085"}, "0.1254±0.0047")
            if "2,010 (R)" in raw:
                for c in cells:
                    sub(c, {"2,010 (R)"}, "1,969 (R)")
            if "ρ=+0.087" in raw or "+0.087 (weak" in raw:
                for c in cells:
                    sub(c, {"ρ=+0.087 (weak, inverted)"}, "ρ=+0.110 (weak, inverted)")
            if "ρ=−0.125" in raw or "ρ=-0.125" in raw:
                for c in cells:
                    sub(c, {"ρ=−0.125", "ρ=-0.125"}, "ρ=−0.126")
            if "flat 0.114→0.125" in raw:
                for c in cells:
                    sub(c, {"flat 0.114→0.125"}, "flat 0.118→0.125")
            if "XES3G5M" in raw and "DKT" in raw and "500 rows" in raw:
                for c in cells:
                    sub(c, {"−0.008", "-0.008"}, "+0.142")
                    sub(c, {"[−0.019, +0.004]", "[-0.019, +0.004]"}, "[+0.104, +0.189]")
                    sub(c, {"CI includes 0"}, "ECE higher")
            if "XES3G5M" in raw and "DKT" in raw and "50 rows" in raw and "+0.018" in raw:
                for c in cells:
                    sub(c, {"+0.018"}, "+0.161")
                    sub(c, {"[+0.006, +0.029]"}, "[+0.127, +0.196]")
            if "XES3G5M" in raw and "T-KT" in raw and "500 rows" in raw and "+0.014" in raw:
                for c in cells:
                    sub(c, {"+0.014"}, "+0.041")
                    sub(c, {"[−0.002, +0.032]", "[-0.002, +0.032]"}, "[+0.020, +0.063]")
                    sub(c, {"CI includes 0"}, "ECE higher")
            if "XES3G5M" in raw and "T-KT" in raw and "50 rows" in raw and "+0.032" in raw:
                for c in cells:
                    sub(c, {"+0.032"}, "+0.110")
                    sub(c, {"[+0.021, +0.043]"}, "[+0.071, +0.156]")
    log.append(f"table cells updated={n}")
    if n < 20:
        raise SystemExit(f"too few table cell updates: {n}")


def replace_fig1(doc, log: list[str]) -> None:
    pics = [s for s in doc.InlineShapes if int(s.Type) == WD_INLINE_PICTURE]
    if len(pics) != 1:
        raise SystemExit(f"expected 1 picture, found {len(pics)}")
    shp = pics[0]
    width, height = shp.Width, shp.Height
    rng = shp.Range
    shp.Delete()
    new_shp = rng.InlineShapes.AddPicture(str(FIG), False, True)
    new_shp.Width = width
    new_shp.Height = height
    log.append(f"fig1 {width:.1f}x{height:.1f}")


def verify(doc) -> None:
    text = doc.Content.Text
    if "AUTHOR ACTION REQUIRED" in text:
        raise SystemExit("AI marker leftover")
    if "7.95M" in text:
        raise SystemExit("7.95M leftover")
    if "1,589,145" in text:
        raise SystemExit("1,589,145 leftover")
    if "2,010" in text:
        raise SystemExit("2,010 leftover")
    if "0.1145±" in text or "(0.1145," in text:
        raise SystemExit("XES ECE 0.1145 leftover")
    if "0.1136" not in text or "0.2280" not in text:
        raise SystemExit("ASSISTments ECE lock missing")
    if "0.196" not in text or "0.268" not in text:
        raise SystemExit("FAR lock missing")
    if "0.047" not in text:
        raise SystemExit("ΔFAR 0.047 missing")
    if "[0.006, 0.138]" not in text:
        raise SystemExit("CI lock missing")
    if "September 1, 2026" not in text:
        raise SystemExit("received date missing")
    if "Cursor Grok 4.6" not in text:
        raise SystemExit("Grok version missing")
    if "6,413,353" not in text or "0.1176" not in text:
        raise SystemExit("A2B XES numbers missing")


def main() -> None:
    if not FIG.exists():
        raise SystemExit(f"missing {FIG}")
    if not BACKUP.exists():
        shutil.copy2(DOCX, BACKUP)
    log: list[str] = []
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    try:
        patch_prose(doc, log)
        split_irt(doc, log)
        patch_tables(doc, log)
        verify(doc)
        replace_fig1(doc, log)
        doc.Save()
        log.append("saved")
    except Exception:
        doc.Close(0)
        word.Quit()
        raise
    doc.Close(0)
    word.Quit()
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
