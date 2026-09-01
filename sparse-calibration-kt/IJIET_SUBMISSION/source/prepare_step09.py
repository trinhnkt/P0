#!/usr/bin/env python3
"""IJIET-09: audit/fix figures and table captions without changing verified rates."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP08 = SRC / "main_ijiet_step08.docx"
STEP09_DOCX = SRC / "main_ijiet_step09.docx"
STEP09_DOC = SRC / "main_ijiet_step09.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step09.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step09_verify.txt"
FIG = ROOT / "IJIET_SUBMISSION" / "figures" / "fig1_kc_and_train_volume.png"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_COLLAPSE_START = 1
WD_COLLAPSE_END = 0
WD_ALIGN_CENTER = 1
WD_SECTION_CONTINUOUS = 3
WD_SECTION_NEW_PAGE = 2
WD_OUTLINE_BODY = 10

FIG_CAPTION = (
    "Fig. 1. Distribution of KCs across train-only frequency strata under "
    "learner-based and temporal splits. Bottom: verified training-interaction "
    "counts (sum of train-only f_train on fold 0); volume is not inferred from "
    "KC counts. Bottom y-axis is logarithmic."
)

TABLE1_CAPTION = (
    "Table 1. Post-processing cohort statistics (learner-based split). "
    "Learner, knowledge-component (KC), interaction, and test-event counts are "
    "post-processing totals, not raw public-dump counts."
)
TABLE2_CAPTION = (
    "Table 2. Overall learner-based area under the ROC curve (AUC) and accuracy (ACC) "
    "(mean±sd over four unique partitions)."
)
TABLE3_CAPTION = (
    "Table 3. SimpleKT event-level expected calibration error (ECE) by train-only "
    "frequency stratum. N is the mean test-event count across four unique learner "
    "partitions, not a single-partition count. Flags: Reliable (R) N≥1000; Limited (L) "
    "100≤N<1000. Junyi sparse is empty."
)
TABLE4_CAPTION = (
    "Table 4. Simulated gate at τ=0.7, ASSISTments 2012 fold 0. False-advance rate "
    "(FAR)=P(y=0 | p≥τ) among N_advance advances; Miss among N_incorrect incorrect "
    "responses; Excess FAR=FAR−E[FAR]. FAR 95% CIs: KC-cluster percentile, B=2000. "
    "Not latent mastery; not a classroom trial."
)
TABLE4_HEADER = [
    "Model",
    "Stratum",
    "N",
    "N_advance",
    "N_incorrect",
    "FAR [95% CI]",
    "E[FAR]",
    "Excess FAR",
    "Miss",
]
TABLE4_ROWS = [
    ["SimpleKT", "dense", "528,018", "284,326", "158,623", "0.196 [0.186, 0.208]", "0.113", "0.083", "0.352"],
    ["SimpleKT", "sparse", "444", "235", "197", "0.268 [0.202, 0.337]", "0.050", "0.218", "0.320"],
    ["DKT", "dense", "528,018", "315,650", "158,623", "0.200 [0.190, 0.211]", "0.147", "0.053", "0.398"],
    ["DKT", "sparse", "444", "243", "197", "0.296 [0.221, 0.383]", "0.057", "0.239", "0.365"],
    ["GKT (train-only)", "dense", "528,018", "351,503", "158,623", "0.205 [0.194, 0.217]", "0.163", "0.042", "0.455"],
    ["GKT (train-only)", "sparse", "444", "209", "197", "0.220 [0.149, 0.295]", "0.157", "0.063", "0.234"],
    ["CL4KT (adapter)", "dense", "528,018", "307,479", "158,623", "0.185 [0.176, 0.194]", "0.175", "0.010", "0.359"],
    ["CL4KT (adapter)", "sparse", "444", "200", "197", "0.240 [0.159, 0.330]", "0.116", "0.124", "0.244"],
]
TABLE4_NOTE = (
    "Seed-42 ΔFAR 95% CI (KC-cluster, B=2000): SimpleKT [0.006, 0.138] (locked C2); "
    "DKT [0.019, 0.175]; GKT [−0.054, 0.092]; CL4KT [−0.018, 0.142]."
)
TABLE5_CAPTION = (
    "Table 5. Gate robustness at τ=0.7 on ASSISTments 2012. Five training runs "
    "(seeds 42, 2024, 2025, 2026, 2027) across four unique learner partitions "
    "(2025 and 2026 share a split). ΔFAR=FAR_sparse−FAR_dense. Mean N, N_advance, and "
    "N_incorrect are sparse-stratum denominators. SimpleKT: ΔFAR>0 on 5/5 training runs "
    "and on all four unique partitions. DKT: ΔFAR>0 on 3/5 training runs (the shared "
    "partition is mixed in sign) and is not a five-run finding. GKT/CL4KT remain "
    "seed 42 only."
)
TABLE5_HEADER = [
    "Model",
    "Mean ΔFAR",
    "SD",
    "Runs ΔFAR>0",
    "Mean N",
    "Mean N_advance",
    "Mean N_incorrect",
]
TABLE5_ROWS = [
    ["SimpleKT", "0.047", "0.033", "5/5 runs (4 partitions)", "413", "227", "155"],
    ["DKT", "0.033", "0.048", "3/5 runs", "413", "226", "155"],
]
TABLE6_CAPTION = (
    "Table 6. Empirical observations, on these three datasets, of when a "
    "sparse-calibration contrast is estimable. These are not universal laws. "
    "Sparse mass: share of KCs with train-only frequency f_train<100."
)

DISC_A = (
    "On the three datasets studied here, three empirical conditions track when a "
    "sparse-calibration contrast is estimable rather than empty (Table 6): (1) a "
    "non-empty low-frequency tail under the split actually used; (2) enough sparse "
    "test events for at least a Limited-flag ECE; (3) frequency–difficulty coupling "
    "that is not inverted. ASSISTments 2012 meets all three. That is a diagnostic "
    "pre-condition on these logs, not a universal law and not a claim that training "
    "frequency causes miscalibration."
)

STRATA_TEXT = (
    "For each fold, KC frequency f_train is counted on the training file only. "
    "Buckets: strict cold-start (f=0), very sparse (0<f<20), sparse (20≤f<100), "
    "medium (100≤f<500), dense (f≥500). Fig. 1 (top) shows the number of KCs in "
    "each stratum. Training-interaction volume is shown separately in the bottom "
    "row from summed f_train, not inferred from KC counts."
)


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def fill_table(table, header, rows) -> None:
    table.Style = "Table Grid"
    for j, h in enumerate(header, 1):
        table.Cell(1, j).Range.Text = h
        table.Cell(1, j).Range.Font.Bold = True
        table.Cell(1, j).Range.Font.Size = 7
        table.Cell(1, j).Range.Font.Name = "Times New Roman"
        table.Cell(1, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    for i, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            table.Cell(i, j).Range.Text = str(val)
            table.Cell(i, j).Range.Font.Bold = False
            table.Cell(i, j).Range.Font.Size = 7
            table.Cell(i, j).Range.Font.Name = "Times New Roman"
            table.Cell(i, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    try:
        table.AutoFitBehavior(2)
    except Exception:
        pass


def neutralize_table_lists(doc) -> None:
    """Stop Heading/list autonumber from leaking into table cells."""
    for ti in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(ti)
        for ri in range(1, tbl.Rows.Count + 1):
            for ci in range(1, tbl.Columns.Count + 1):
                cell = tbl.Cell(ri, ci)
                try:
                    cell.Range.ListFormat.RemoveNumbers()
                except Exception:
                    pass
                cell.Range.ParagraphFormat.OutlineLevel = WD_OUTLINE_BODY


def replace_caption(doc, needle: str, new: str) -> bool:
    for i in range(1, doc.Paragraphs.Count + 1):
        if needle in para_text(doc.Paragraphs(i)):
            set_para_text(doc.Paragraphs(i), new)
            return True
    return False


def replace_table_by_caption(doc, old_stub: str, new_caption: str, header, rows):
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if old_stub in para_text(doc.Paragraphs(i)):
            cap_i = i
            break
    if cap_i is None:
        raise RuntimeError(f"caption not found: {old_stub}")
    cap = doc.Paragraphs(cap_i)
    set_para_text(cap, new_caption)
    probe = doc.Range(cap.Range.End, cap.Range.End + 80)
    if probe.Tables.Count < 1:
        raise RuntimeError(f"no table after caption: {old_stub}")
    old = probe.Tables(1)
    insert_at = old.Range.Start
    old.Delete()
    rng = doc.Range(insert_at, insert_at)
    table = doc.Tables.Add(rng, len(rows) + 1, len(header))
    fill_table(table, header, rows)
    return table


def replace_figure(doc, lines) -> None:
    if not FIG.exists():
        raise RuntimeError(f"missing {FIG}")
    if doc.InlineShapes.Count < 1:
        raise RuntimeError("no inline figure")
    shp = doc.InlineShapes(1)
    para = shp.Range.Paragraphs(1)
    shp.Delete()
    rng = para.Range
    rng.Collapse(WD_COLLAPSE_START)
    pic = rng.InlineShapes.AddPicture(str(FIG))
    lines.append(f"FIG_INSERTED width0={pic.Width:.1f}")
    cap_ok = replace_caption(doc, "Fig. 1.", FIG_CAPTION)
    lines.append(f"FIG_CAPTION={cap_ok}")

    # Insert section breaks at the paragraph boundaries, not on the picture Range.
    pic = doc.InlineShapes(1)
    pic_start = pic.Range.Paragraphs(1).Range.Start
    if pic_start > 0:
        doc.Range(pic_start - 1, pic_start - 1).InsertBreak(WD_SECTION_NEW_PAGE)
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith("Fig. 1."):
            cap_i = i
            break
    if cap_i is None:
        raise RuntimeError("Fig. 1 caption missing after replace")
    cap = doc.Paragraphs(cap_i)
    cap.Range.ParagraphFormat.SpaceBefore = 8
    cap.Range.ParagraphFormat.SpaceAfter = 8
    cap_end = cap.Range.End
    doc.Range(cap_end, cap_end).InsertBreak(WD_SECTION_CONTINUOUS)
    pic = doc.InlineShapes(1)
    pic.Range.Paragraphs(1).Range.ParagraphFormat.SpaceAfter = 10
    pic.Range.Paragraphs(1).Range.ParagraphFormat.KeepWithNext = True
    cap = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith("Fig. 1."):
            cap = doc.Paragraphs(i)
            break
    fig_sec = None
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        pic_in = sec.Range.Start <= pic.Range.Start <= sec.Range.End
        cap_in = cap is not None and sec.Range.Start <= cap.Range.Start <= sec.Range.End
        if pic_in:
            lines.append(
                f"FIG_SEC_PROBE s={s} pic_in={pic_in} cap_in={cap_in} "
                f"head={para_text(sec.Range.Paragraphs(1))[:60]!r}"
            )
            if cap_in:
                fig_sec = s
                break
    if fig_sec is None:
        raise RuntimeError("figure and caption are not in the same section")
    sec = doc.Sections(fig_sec)
    head = para_text(sec.Range.Paragraphs(1))[:80]
    if "INTRODUCTION" in head or "MATERIALS" in head:
        raise RuntimeError(f"refusing to 1-col body section starting: {head!r}")
    sec.PageSetup.TextColumns.SetCount(1)
    try:
        from PIL import Image as _PILImage

        pw, ph = _PILImage.open(FIG).size
        pic.LockAspectRatio = False
        pic.Width = 470
        pic.Height = 470.0 * ph / pw
    except Exception as exc:
        lines.append(f"FIG_WIDTH_ERR={exc}")
        try:
            pic.Width = 470
        except Exception:
            pass
    lines.append(
        f"FIG_SECTION={fig_sec} COLS={sec.PageSetup.TextColumns.Count} "
        f"WIDTH={pic.Width:.1f} HEIGHT={pic.Height:.1f} HEAD={head!r}"
    )
    if pic.Height < 250:
        raise RuntimeError(f"figure height too small: {pic.Height:.1f} pt")
    if fig_sec < doc.Sections.Count:
        nxt = doc.Sections(fig_sec + 1)
        nxt.PageSetup.TextColumns.SetCount(2)
        try:
            nxt.PageSetup.TextColumns.EvenlySpaced = True
            nxt.PageSetup.TextColumns.Spacing = 14.4
        except Exception:
            pass
        lines.append(f"FIG_NEXT_COLS={nxt.PageSetup.TextColumns.Count}")


def wrap_caption_and_table(doc, stub: str, lines, tag: str) -> None:
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            cap_i = i
            break
    if cap_i is None:
        raise RuntimeError(f"wrap: missing {stub}")
    start = doc.Paragraphs(cap_i).Range.Start
    if start > 0:
        doc.Range(start - 1, start - 1).InsertBreak(WD_SECTION_CONTINUOUS)
    cap_i = None
    for i in range(1, doc.Paragraphs.Count + 1):
        if para_text(doc.Paragraphs(i)).startswith(stub):
            cap_i = i
            break
    cap = doc.Paragraphs(cap_i)
    probe = doc.Range(cap.Range.End, cap.Range.End + 80)
    if probe.Tables.Count < 1:
        raise RuntimeError(f"wrap: no table after {stub}")
    table = probe.Tables(1)
    end = table.Range
    end.Collapse(WD_COLLAPSE_END)
    end.InsertBreak(WD_SECTION_CONTINUOUS)
    for s in range(1, doc.Sections.Count + 1):
        sec = doc.Sections(s)
        if sec.Range.Start <= table.Range.Start <= sec.Range.End:
            if not (sec.Range.Start <= cap.Range.Start <= sec.Range.End):
                raise RuntimeError(f"{tag}: caption and table not in the same section")
            sec.PageSetup.TextColumns.SetCount(1)
            lines.append(f"{tag}_SECTION={s} COLS={sec.PageSetup.TextColumns.Count}")
            if s < doc.Sections.Count:
                nxt = doc.Sections(s + 1)
                nxt.PageSetup.TextColumns.SetCount(2)
                try:
                    nxt.PageSetup.TextColumns.EvenlySpaced = True
                    nxt.PageSetup.TextColumns.Spacing = 14.4
                except Exception:
                    pass
                lines.append(f"{tag}_NEXT_COLS={nxt.PageSetup.TextColumns.Count}")
            break


def main() -> None:
    if not STEP08.exists():
        raise SystemExit(f"Missing {STEP08}")
    shutil.copy2(STEP08, STEP09_DOCX)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = []
    try:
        doc = word.Documents.Open(str(STEP09_DOCX))
        if "Table 2 shows learner-based AUC" not in doc.Content.Text:
            raise RuntimeError("Results probe missing")

        for i in range(1, doc.Paragraphs.Count + 1):
            raw = para_text(doc.Paragraphs(i))
            if raw.startswith("For each fold, KC frequency"):
                set_para_text(doc.Paragraphs(i), STRATA_TEXT)
                continue
            if raw.startswith("On the three datasets studied here, three empirical") or raw.startswith(
                "Three observable conditions"
            ):
                set_para_text(doc.Paragraphs(i), DISC_A)
                continue
            if raw.startswith("FAR 95% CIs (KC-cluster") or raw.startswith("Seed-42 ΔFAR 95% CI"):
                set_para_text(doc.Paragraphs(i), TABLE4_NOTE)
                continue
            new = raw.replace(
                "all five training runs (four unique learner partitions) "
                "(mean 0.047; four unique student partitions)",
                "all five training runs across four unique learner partitions (mean 0.047)",
            ).replace(
                "all five training seeds (mean 0.047; four unique student partitions)",
                "all five training runs across four unique learner partitions (mean 0.047)",
            ).replace(
                "5/5 seeds",
                "5/5 training runs across four unique learner partitions",
            ).replace(
                "all five training seeds",
                "all five training runs across four unique learner partitions",
            )
            if new != raw:
                set_para_text(doc.Paragraphs(i), new)

        # Document-level sweep (conclusion and any split runs).
        finder = doc.Content.Find
        finder.ClearFormatting()
        finder.Replacement.ClearFormatting()
        finder.Execute(
            FindText="5/5 seeds",
            MatchCase=True,
            MatchWholeWord=False,
            MatchWildcards=False,
            MatchSoundsLike=False,
            MatchAllWordForms=False,
            Forward=True,
            Wrap=1,
            Format=False,
            ReplaceWith="5/5 training runs across four unique learner partitions",
            Replace=2,
        )

        ok1 = replace_caption(doc, "Table 1.", TABLE1_CAPTION)
        ok2 = replace_caption(doc, "Table 2.", TABLE2_CAPTION)
        ok3 = replace_caption(doc, "Table 3.", TABLE3_CAPTION)
        ok6 = replace_caption(doc, "Table 6.", TABLE6_CAPTION)
        lines.append(f"CAP1={ok1} CAP2={ok2} CAP3={ok3} CAP6={ok6}")

        replace_table_by_caption(
            doc, "Table 4. Simulated gate", TABLE4_CAPTION, TABLE4_HEADER, TABLE4_ROWS
        )
        replace_table_by_caption(
            doc, "Table 5. Gate robustness", TABLE5_CAPTION, TABLE5_HEADER, TABLE5_ROWS
        )
        replace_figure(doc, lines)
        wrap_caption_and_table(doc, "Table 3.", lines, "T3")
        wrap_caption_and_table(doc, "Table 4.", lines, "T4")
        wrap_caption_and_table(doc, "Table 5.", lines, "T5")
        neutralize_table_lists(doc)

        # Section breaks restart Heading 1 numbering; restore IJIET I–V.
        for i in range(1, doc.Paragraphs.Count + 1):
            try:
                style = str(doc.Paragraphs(i).Style.NameLocal)
            except Exception:
                continue
            if style != "Heading 1":
                continue
            raw = para_text(doc.Paragraphs(i))
            up = raw.upper()
            target = None
            if "RESULT AND DISCUSSION" in up:
                target = "IV. RESULT AND DISCUSSION"
            elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
                target = "V. CONCLUSION"
            if target and raw != target:
                try:
                    doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
                except Exception:
                    pass
                set_para_text(doc.Paragraphs(i), target)
                lines.append(f"H1_FIX {raw!r} -> {target}")

        for i in range(1, doc.Paragraphs.Count + 1):
            t = para_text(doc.Paragraphs(i))
            if t.startswith("Table ") and len(t) > 7 and t[6].isdigit() and "." in t[:10]:
                doc.Paragraphs(i).Range.ParagraphFormat.KeepWithNext = True

        full = doc.Content.Text
        if "5/5 seeds" in full:
            idx = full.find("5/5 seeds")
            lines.append("T5_SEEDS_CONTEXT=" + repr(full[max(0, idx - 80) : idx + 80]))
        checks = {
            "results": "Table 2 shows learner-based AUC" in full,
            "fig_caption_kcs": "Distribution of KCs across train-only frequency strata" in full,
            "fig_not_infer": "not inferred from KC counts" in full,
            "no_old_figcap": "Dense concepts dominate interactions" not in full,
            "t1_post": "post-processing totals" in full,
            "t2_auc_acc": "area under the ROC curve (AUC) and accuracy (ACC)" in full,
            "t3_mean_n": "mean test-event count across four unique learner partitions" in full,
            "t3_not_single": "not a single-partition count" in full,
            "t4_nadv": "284,326" in full,
            "t4_ci": "0.268 [0.202, 0.337]" in full,
            "t4_excess": "0.218" in full,
            "t5_runs": "5/5 training runs across four unique learner partitions" in full
            or "5/5 runs (4 partitions)" in full,
            "t5_not_indep_seeds": "5/5 seeds" not in full,
            "t6_not_law": "not universal laws" in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
            "h1_results": "IV. RESULT AND DISCUSSION" in full,
            "h1_conclusion": "V. CONCLUSION" in full,
            "titles_above": True,
        }
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        # Caption position audit
        fig_i = cap1 = None
        for i in range(1, doc.Paragraphs.Count + 1):
            t = para_text(doc.Paragraphs(i))
            if t.startswith("Fig. 1."):
                fig_i = i
            if t.startswith("Table 1."):
                cap1 = i
        if fig_i is None or cap1 is None:
            raise RuntimeError("missing Fig. 1 or Table 1 caption")
        lines.append(f"TABLE1_CAPTION_PARA={cap1} FIG_CAPTION_PARA={fig_i}")

        fig_below = False
        if fig_i > 1:
            fig_below = doc.Paragraphs(fig_i - 1).Range.InlineShapes.Count >= 1
        lines.append(f"FIG_CAPTION_BELOW_PIC={fig_below}")
        if not fig_below:
            raise RuntimeError("Fig. 1 caption is not immediately below the figure")

        for n in range(1, 7):
            stub = f"Table {n}."
            found = False
            for i in range(1, doc.Paragraphs.Count + 1):
                t = para_text(doc.Paragraphs(i))
                if t.startswith(stub):
                    probe = doc.Range(
                        doc.Paragraphs(i).Range.End, doc.Paragraphs(i).Range.End + 60
                    )
                    above = probe.Tables.Count >= 1
                    lines.append(f"TITLE_ABOVE_TABLE{n}={above}")
                    if not above:
                        raise RuntimeError(f"Table {n} title is not immediately above the table")
                    found = True
                    break
            if not found:
                raise RuntimeError(f"missing caption {stub}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} "
            f"PICS={doc.InlineShapes.Count} SECTIONS={doc.Sections.Count}"
        )
        if doc.InlineShapes.Count != 1:
            raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")
        if doc.Tables.Count < 7:
            raise RuntimeError(f"expected >=7 tables, got {doc.Tables.Count}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP09_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP09_DOC), WD_FORMAT_DOC)
        doc.ExportAsFixedFormat(
            str(OUT_PDF),
            17,
            OpenAfterExport=False,
            OptimizeFor=0,
            Item=0,
            IncludeDocProps=True,
            KeepIRM=True,
            CreateBookmarks=1,
            DocStructureTags=True,
            BitmapMissingFonts=True,
            UseISO19005_1=False,
        )
        lines.append(
            f"PDF_EXISTS={OUT_PDF.exists()} SIZE={OUT_PDF.stat().st_size if OUT_PDF.exists() else 0}"
        )
    except Exception:
        if lines:
            REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise
    finally:
        if doc is not None:
            doc.Close(WD_SAVE)
        word.Quit()

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
