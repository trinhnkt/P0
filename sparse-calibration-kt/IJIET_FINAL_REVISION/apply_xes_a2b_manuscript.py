#!/usr/bin/env python3
"""Apply A2B-masked XES3G5M numbers to IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx.

Does not write IJIET_SUBMISSION/. Does not change ASSISTments or Junyi cells.
"""
from __future__ import annotations

from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
FIG = HERE / "figures" / "fig1_kc_and_train_volume.png"
LOG = HERE / "audit" / "apply_xes_a2b_log.txt"

# Word constants
WD_REPLACE = 2  # wdReplaceAll
WD_FIND_CONTINUE = 1
WD_STORY = 6
WD_INLINE_PICTURE = 3


def count_hits(doc, old: str) -> int:
    n = 0
    rng = doc.Content
    finder = rng.Find
    finder.ClearFormatting()
    finder.Text = old
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWholeWord = False
    finder.MatchWildcards = False
    while finder.Execute():
        n += 1
        if n > 50:
            raise SystemExit(f"too many hits for {old!r}")
    return n


def find_replace(word, old: str, new: str, expect: int | None = None) -> int:
    doc = word.ActiveDocument
    n = count_hits(doc, old)
    if expect is not None and n != expect:
        raise SystemExit(f"count {old!r}: got {n}, expected {expect}")
    rng = doc.Content
    finder = rng.Find
    finder.ClearFormatting()
    finder.Replacement.ClearFormatting()
    finder.Text = old
    finder.Replacement.Text = new
    finder.Forward = True
    finder.Wrap = 0
    finder.MatchCase = True
    finder.MatchWholeWord = False
    finder.MatchWildcards = False
    finder.Execute(Replace=2)  # wdReplaceAll
    return n


def main() -> None:
    if not DOCX.exists():
        raise SystemExit(f"missing {DOCX}")
    if not FIG.exists():
        raise SystemExit(f"missing {FIG}; run generate_fig1_a2b.py first")

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(DOCX), ReadOnly=False)
    log: list[str] = []
    try:
        pairs: list[tuple[str, str, int]] = [
            (
                "and 7,953,709 (XES3G5M)",
                "and 6,413,353 (XES3G5M)",
                1,
            ),
            (
                "flattened to one row per sequence position.",
                "flattened to one row per unmasked sequence position. Positions with selectmask\u22601, KC=\u22121, question=\u22121, or a label outside {0,1} are dropped before counting and scoring.",
                1,
            ),
            (
                "Table 1 instead lists 866 KCs and 7.95M interactions because flattening kc_level sequences (i) expands multi-KC questions into one row per listed concept and (ii) retains sequence-padding tokens coded skill_id=\u22121 (with matching question_id=\u22121). Unique kc_id including that padding token is 866; excluding it is 865. Unique item_id including \u22121 is 7,653. Subsequent preprocessing dropped 0 rows.",
                "Table 1 lists 865 KCs and 6,413,353 valid KC-level rows: flattening still expands multi-KC questions into one row per listed concept, but padding tokens are excluded. Unique item_id is 7,652. Learner-based fold-0 test events are 1,282,422.",
                1,
            ),
            ("7.95M", "6.41M", 1),
            ("1,589,145", "1,282,422", 1),
            ("0.8171\u00b10.0022", "0.8180\u00b10.0009", 1),
            ("0.8327\u00b10.0032", "0.8321\u00b10.0015", 1),
            ("0.7557\u00b10.0013", "0.7536\u00b10.0010", 1),
            ("0.8067\u00b10.0037", "0.8057\u00b10.0029", 1),
            (
                "DKT 0.857 versus 0.817; SimpleKT 0.847 versus 0.755",
                "DKT 0.858 versus 0.818; SimpleKT 0.847 versus 0.753",
                1,
            ),
            (
                "(0.1145, 0.1114, 0.1248) despite Reliable sparse occupancy (N=2,010)",
                "(0.1176, 0.1129, 0.1254) despite Reliable sparse occupancy (N=1,969)",
                1,
            ),
            ("1,268,696", "1,269,345", 1),
            ("0.1145\u00b10.0011", "0.1176\u00b10.0014", 1),
            ("12,980", "12,889", 1),
            ("0.1114\u00b10.0076", "0.1129\u00b10.0061", 1),
            ("0.1248\u00b10.0085", "0.1254\u00b10.0047", 1),
            ("2,010", "1,969", 4),
            (
                "On XES3G5M, SimpleKT \u0394FAR is negative on all five runs, but \u0394Miss is positive on all five (mean +0.112): among actual incorrect answers, the system still advances more often on sparse than on dense KCs.",
                "On XES3G5M, SimpleKT \u0394FAR is negative on all five runs (mean \u22120.017), and \u0394Miss is also negative (mean \u22120.183): after padding tokens are excluded, sparse KCs do not show a higher miss rate than dense KCs.",
                1,
            ),
            (
                "yet SimpleKT ECE does not degrade\u2014while miss rates still can.",
                "yet SimpleKT ECE does not degrade.",
                1,
            ),
            ("\u03c1=+0.087 (weak, inverted)", "\u03c1=+0.110 (weak, inverted)", 1),
            ("flat 0.114\u21920.125", "flat 0.118\u21920.125", 1),
            (
                "versus a weak opposite-signed \u03c1=+0.087 on XES3G5M",
                "versus a weak opposite-signed \u03c1=+0.110 on XES3G5M",
                1,
            ),
            ("and 1,263 KCs", "and 829 KCs", 1),
            (
                "and \u22120.117 [\u22120.171, \u22120.063] on XES3G5M",
                "and \u22120.028 [\u22120.042, \u22120.014] on XES3G5M",
                1,
            ),
            (
                "Frequency alone is therefore not a universal causal explanation.",
                "Frequency alone is therefore not a universal causal explanation. On XES3G5M, DKT at 500 rows shows a large positive \u0394ECE (+0.142 [+0.104, +0.189]).",
                1,
            ),
            ("\u22120.008", "+0.142", 1),
            ("[\u22120.019, +0.004]", "[+0.104, +0.189]", 1),
            (
                "on XES3G5M, \u0394FAR and \u0394Miss can move in opposite directions, so a flat ECE is not a flat miss rate.",
                "on XES3G5M, SimpleKT \u0394FAR and \u0394Miss are both negative after padding is excluded, so a flat ECE is not by itself a decision-error result.",
                1,
            ),
            ("and +0.087.", "and +0.110.", 1),
            ("\u22120.308, \u22120.324, and \u22120.125", "\u22120.308, \u22120.324, and \u22120.126", 2),
        ]

        for old, new, expect in pairs:
            n = find_replace(word, old, new, expect)
            log.append(f"OK {n} | {old[:80]!r} -> {new[:80]!r}")

        # Table 1 KC cell only — do not substring-replace inside 18,066.
        t1 = 0
        for table in doc.Tables:
            for row in table.Rows:
                txt = row.Range.Text
                if "XES3G5M" in txt and "18,066" in txt:
                    for i in range(1, row.Cells.Count + 1):
                        raw = row.Cells(i).Range.Text
                        t = raw.replace("\r", "").replace("\x07", "").strip()
                        if t == "866":
                            row.Cells(i).Range.Text = "865"
                            t1 += 1
        if t1 != 1:
            raise SystemExit(f"Table 1 XES KC replacements={t1}")
        log.append("OK table1 KCs 866 -> 865")

        # Table 8 XES DKT interpretation cell: was "CI includes 0"
        flipped = 0
        for table in doc.Tables:
            for row in table.Rows:
                txt = row.Range.Text.replace("\r", " ").replace("\x07", " ")
                if "XES3G5M" in txt and "DKT" in txt and "500" in txt and "+0.142" in txt:
                    cell = row.Cells(row.Cells.Count)
                    prev = cell.Range.Text
                    cell.Range.Text = "ECE higher"
                    flipped += 1
                    log.append(f"OK table8 interp | {prev.strip()!r} -> 'ECE higher'")
        if flipped != 1:
            raise SystemExit(f"Table 8 XES interpretation replacements={flipped}")

        # Replace embedded Fig. 1 only.
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
        log.append(f"OK fig1 replaced {FIG.name} {width:.1f}x{height:.1f}")

        doc.Save()
        log.append(f"saved {DOCX}")
    finally:
        doc.Close(0)
        word.Quit()

    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
