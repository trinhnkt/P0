#!/usr/bin/env python3
"""A20: fill IJIET §6.3 AI versions from public 2026-09-01 product pages.

Does not invent versions. Does not change scientific locks.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import (  # noqa: E402
    COVER,
    DATA_BLIND,
    PAPER_TITLE,
    patch_blind_data,
    stamp_pdf_metadata,
)
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

BACKUP = HERE / "manuscript" / "main_ijiet_full.docx.bak_pre_a20"
LOG = HERE / "audit" / "apply_a20_word_log.txt"
VERIFY = HERE / "audit" / "compile_verify.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A20.md"
AI_AUDIT = HERE / "audit" / "AI_TOOL_VERSION_AUDIT.md"

WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1

AI_OLD = (
    "During manuscript preparation, the authors used Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using this tool, the authors reviewed "
    "and edited the content. The authors remain responsible for all content. "
    "Generative AI is not listed as a co-author."
)
AI_NEW = (
    "During manuscript preparation, the authors used ChatGPT GPT-5.6, "
    "Claude Sonnet 5, Google Antigravity 2.11.0, and Cursor Grok 4.6 for "
    "language polishing, formatting, consistency checking, and "
    "reproducibility-prompt preparation. AI was not used to fabricate or "
    "alter experimental results. After using these tools, the authors "
    "reviewed and edited the content. The authors remain responsible for "
    "all content. Generative AI is not listed as a co-author."
)


def patch_ai(doc, log: list[str]) -> None:
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
        if AI_OLD in text or (
            "Cursor Grok 4.6" in text
            and "language polishing" in text
            and "ChatGPT GPT-5.6" not in text
        ):
            inner.Text = AI_NEW
            n += 1
            log.append(f"ai i={i}")
    log.append(f"ai_n={n}")
    if n != 1:
        raise SystemExit(f"AI patch expected 1, got {n}")


def write_cover() -> None:
    text = COVER.read_text(encoding="utf-8")
    old = (
        "Generative AI. Cursor Grok 4.6 was used for language polishing, formatting,\n"
        "consistency checking, and reproducibility-prompt preparation. AI was not used\n"
        "to fabricate or alter results. Generative AI is not a co-author. ChatGPT,\n"
        "Claude, and Google Antigravity are not listed because model versions were not\n"
        "retained and IJIET ethics §6.3 requires a version with the tool name."
    )
    new = (
        "Generative AI. ChatGPT GPT-5.6, Claude Sonnet 5, Google Antigravity 2.11.0,\n"
        "and Cursor Grok 4.6 were used for language polishing, formatting, consistency\n"
        "checking, and reproducibility-prompt preparation. Versions are the public\n"
        "current identifiers as of 1 September 2026. AI was not used to fabricate or\n"
        "alter results. Generative AI is not a co-author."
    )
    if old not in text:
        raise SystemExit("cover letter AI block not found")
    COVER.write_text(text.replace(old, new), encoding="utf-8")


def write_docs(pages: int, blind_pages: int) -> None:
    CHANGELOG.write_text(
        f"""# CHANGELOG_A20 — Generative AI versions (§6.3)

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged.

Public current identifiers (checked 2026-09-01), not reconstructed account history:

| Tool | Version in manuscript | Source |
|---|---|---|
| ChatGPT | GPT-5.6 | OpenAI Help Center, GPT-5.6 in ChatGPT |
| Claude | Sonnet 5 | Anthropic Models overview (`claude-sonnet-5`) |
| Google Antigravity | 2.11.0 | antigravity.google/changelog (26 Aug 2026) |
| Cursor | Grok 4.6 | this revision session |

Claude’s current family also lists Opus 5 and Fable 5; Sonnet 5 is the current
Sonnet line used for language editing. ChatGPT GPT-5.6 is the current ChatGPT
generation (Sol on paid plans; Luna on Free/Go).

Named/blind: {pages} / {blind_pages} pages.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a20`.
""",
        encoding="utf-8",
    )
    AI_AUDIT.write_text(
        """# AI_TOOL_VERSION_AUDIT

**Date:** 2026-09-01  
**Rule:** IJIET Publication Ethics Statement §6.3 requires tool, version, and how used.

Account history still does not retain ChatGPT/Claude/Antigravity build IDs.
A20 fills **current public product versions as of 1 September 2026**, at the
authors’ request, for the mandatory disclosure.

| Tool | Version | Evidence | Usage |
|---|---|---|---|
| ChatGPT | GPT-5.6 | https://help.openai.com/en/articles/20001354-gpt-56-in-chatgpt | Language polishing; formatting; consistency checking; reproducibility-prompt preparation |
| Claude | Sonnet 5 | https://platform.claude.com/docs/en/about-claude/models/overview | Same |
| Google Antigravity | 2.11.0 | https://antigravity.google/changelog (26 Aug 2026) | Same |
| Cursor | Grok 4.6 | this IJIET_FINAL_REVISION session | Same |

AI was not used to fabricate or alter experimental results. Generative AI is not a co-author.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    shutil.copy2(FULL_DOCX, BACKUP)
    write_cover()
    log: list[str] = ["A20"]
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX))
        patch_ai(full_doc, log)
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
    compact = "".join(full_t.split()).lower()
    compact_b = "".join(blind_t.split()).lower()
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    log.append(f"GPT56={'gpt-5.6' in compact}")
    log.append(f"SONNET5={'claudesonnet5' in compact}")
    log.append(f"AG211={'2.11.0' in full_t}")
    log.append(f"GROK={'grok4.6' in compact and 'grok4.6' in compact_b}")
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
    write_docs(full_pages, blind_pages)
    print("\n".join(log))
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit(f"page count {full_pages}/{blind_pages}")
    if "gpt-5.6" not in compact or "claudesonnet5" not in compact:
        raise SystemExit("AI versions missing from named PDF")
    if "2.11.0" not in full_t or "2.11.0" not in blind_t:
        raise SystemExit("Antigravity 2.11.0 missing")
    if "Khanh-Trinh" in blind_t:
        raise SystemExit("blind identified")
    _ = PAPER_TITLE


if __name__ == "__main__":
    main()
