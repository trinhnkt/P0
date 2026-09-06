#!/usr/bin/env python3
"""P0 items 1–5: ethics, AI, Fig. 1 width, 5-block Abstract, early Table 8 cite."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
FULL = HERE / "manuscript" / "main_ijiet_full.docx"
BAK = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_p0_uplift15"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
WD_FORMAT_XML = 16
WD_SAVE = -1
WD_ALIGN_CENTER = 1
FIG_W = 501.8

ABS_OLD_START = "Abstract—Knowledge Tracing (KT) systems that skip"
ABS_NEW = (
    "Abstract—Knowledge Tracing (KT) systems that skip, remediate, or "
    "advance practice typically consume a predicted probability rather than "
    "an area-under-the-curve (AUC) score, so population ranking can look "
    "acceptable while probabilities are poorly calibrated on rarely practiced "
    "knowledge components (KCs). We specify a train-only sparse-concept "
    "evaluation protocol that combines learner-based and temporal views, "
    "explicit cold-start definitions, occupancy-aware reporting, 15-bin "
    "expected calibration error (ECE), Brier score with the Murphy "
    "decomposition (uncertainty − resolution + reliability), reliability "
    "diagrams, and L1–L7 leakage control. The protocol is applied to three "
    "public logs (ASSISTments 2012, Junyi Academy, and XES3G5M) with IRT, "
    "DKT, and a local Transformer KT baseline (T-KT; not SimpleKT [4]); "
    "official SimpleKT is scored on ASSISTments AUC/ECE only. Lower KC "
    "training frequency does not universally degrade discrimination: Junyi’s "
    "exercise-level operational identifier (ucid) yields no learner-based "
    "sparse stratum, and XES3G5M T-KT ECE is essentially flat (0.1176, "
    "0.1129, 0.1254), whereas ASSISTments 2012 T-KT ECE rises from 0.114 on "
    "dense KCs to 0.228 on sparse KCs (Limited occupancy, N≈415). A frozen "
    "review artifact and a one-command rebuild of the diagnostic tables from "
    "frozen summaries accompany the protocol; a locked simulated gate at "
    "τ=0.7 is reported only as a decision-error probe (Supplementary Tables "
    "S3–S6), not as a primary contribution. This is not a classroom "
    "intervention."
)

ETHICS_DROP = (
    " This manuscript is not under consideration for publication elsewhere."
)
AI_NEW = (
    "During manuscript preparation, the authors used Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using this tool, the authors reviewed "
    "and edited the content. The authors remain responsible for all content. "
    "Generative AI is not listed as a co-author."
)
T8_OLD = "(Limited sparse support, Table 8)"
T8_NEW = "(Limited sparse support, Section IV.D)"

COVER_AI_OLD = (
    "Generative AI. ChatGPT GPT-5.6, Claude Sonnet 5, Google Antigravity 2.11.0,\n"
    "and Cursor Grok 4.6 were used for language polishing, formatting, consistency\n"
    "checking, and reproducibility-prompt preparation. Versions are the public\n"
    "current identifiers as of 1 September 2026. AI was not used to fabricate or\n"
    "alter results. Generative AI is not a co-author."
)
COVER_AI_NEW = (
    "Generative AI. Cursor Grok 4.6 was used for language polishing, formatting,\n"
    "consistency checking, and reproducibility-prompt preparation. AI was not used\n"
    "to fabricate or alter results. Generative AI is not a co-author."
)


def set_inner(doc, para, new: str) -> None:
    inner = doc.Range(para.Range.Start, para.Range.End - 1)
    inner.Text = new


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if not BAK.exists():
        shutil.copy2(FULL, BAK)
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Open(str(FULL))
    hits = {"abs": 0, "eth": 0, "ai": 0, "t8": 0, "fig": 0}
    try:
        for i in range(1, doc.Paragraphs.Count + 1):
            para = doc.Paragraphs(i)
            inner = doc.Range(para.Range.Start, para.Range.End - 1)
            text = inner.Text or ""
            if text.startswith(ABS_OLD_START):
                set_inner(doc, para, ABS_NEW)
                hits["abs"] += 1
            elif text.startswith("This study is a secondary analysis"):
                if ETHICS_DROP in text:
                    inner.Text = text.replace(ETHICS_DROP, "")
                    hits["eth"] += 1
                elif "not under consideration" not in text:
                    hits["eth"] = max(hits["eth"], 1)
            elif text.startswith("During manuscript preparation"):
                set_inner(doc, para, AI_NEW)
                hits["ai"] += 1
            elif T8_OLD in text:
                inner.Text = text.replace(T8_OLD, T8_NEW)
                hits["t8"] += 1

        # Fig. 1 is the first inline shape (pipeline); already in a 1-col band.
        if doc.InlineShapes.Count < 1:
            raise SystemExit("no figures")
        fig1 = doc.InlineShapes(1)
        fig1.LockAspectRatio = True
        fig1.Width = FIG_W
        try:
            fig1.Range.Paragraphs(1).Alignment = WD_ALIGN_CENTER
        except Exception:
            pass
        hits["fig"] = 1
        print(f"fig1 {fig1.Width:.1f}x{fig1.Height:.1f}")

        if hits["abs"] != 1:
            raise SystemExit(f"abstract hits={hits['abs']}")
        if hits["eth"] != 1:
            raise SystemExit(f"ethics hits={hits['eth']}")
        if hits["ai"] != 1:
            raise SystemExit(f"ai hits={hits['ai']}")
        if hits["t8"] != 1:
            raise SystemExit(f"t8 hits={hits['t8']}")

        body = doc.Content.Text or ""
        if "not under consideration" in body:
            raise SystemExit("exclusive sentence still in article")
        if "GPT-5.6" in body or "Sonnet 5" in body or "Antigravity 2.11.0" in body:
            raise SystemExit("invented AI versions remain")
        if "Cursor Grok 4.6" not in body:
            raise SystemExit("Grok 4.6 missing")
        if "occupancy-aware reporting" not in body:
            raise SystemExit("protocol occupancy missing from Abstract")
        if "one-command rebuild" not in body:
            raise SystemExit("artifact missing from Abstract")
        if "Limited sparse support, Table 8" in body:
            raise SystemExit("early Table 8 cite remains")
        if "Section IV.D" not in body:
            raise SystemExit("Section IV.D pointer missing")
        if "0.1136" not in body or "0.2280" not in body:
            raise SystemExit("ECE locks missing")
        if "0.1176" not in body or "0.1254" not in body:
            raise SystemExit("XES ECE missing")
        if "0.196" not in body or "0.268" not in body:
            raise SystemExit("FAR locks missing")
        if fig1.Width < 500:
            raise SystemExit(f"fig1 still narrow {fig1.Width}")

        doc.SaveAs2(str(FULL), WD_FORMAT_XML)
        print("uplift15", hits)
    finally:
        try:
            doc.Close(WD_SAVE)
        except Exception:
            pass
        word.Quit()

    cov = COVER.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in cov else "\n"
    old_ai = COVER_AI_OLD.replace("\n", nl)
    new_ai = COVER_AI_NEW.replace("\n", nl)
    if old_ai not in cov:
        raise SystemExit("cover AI block not found")
    if "Exclusive submission. This manuscript is not under consideration elsewhere." not in cov:
        raise SystemExit("cover exclusive block missing")
    COVER.write_text(cov.replace(old_ai, new_ai), encoding="utf-8")
    print("cover AI updated")


if __name__ == "__main__":
    main()
