#!/usr/bin/env python3
"""A30: pack IJIET OJS upload files from the A29 manuscript.

No scientific edits. Rebuilds the anonymous zip, exports named .doc,
copies living PDFs/Word into OJS_UPLOAD and IJIET_SUBMISSION current slots.
Conversion snapshots were archived to `_archive/`; do not resurrect them.
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

import win32com.client as win32

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_a19_word import (  # noqa: E402
    PAPER_TITLE,
    REVIEW_ZIP,
    pack_review_zip,
)
from build_a16_double_blind import (  # noqa: E402
    BLIND_DOC,
    BLIND_DOCX,
    BLIND_PDF,
    FULL_DOC,
    FULL_DOCX,
    FULL_PDF,
    lock_checks,
    pdf_text,
)

SUB = HERE.parent / "IJIET_SUBMISSION"
OJS = HERE / "output" / "OJS_UPLOAD"
SUP_PDF = HERE / "output" / "supplementary.pdf"
COVER = HERE / "output" / "cover_letter_ijiet.txt"
README_REVIEW = HERE / "output" / "README_CODE_FOR_REVIEW.txt"
LOG = HERE / "audit" / "apply_a30_submission_pack_log.txt"
CHANGELOG = HERE / "audit" / "CHANGELOG_A30.md"
VERIFY = HERE / "audit" / "compile_verify.txt"

WD_FORMAT_DOC = 0
WD_SAVE = -1

OJS_README = """# IJIET OJS upload (P0 protocol manuscript)

**Journal:** International Journal of Information and Education Technology (www.ijiet.org)  
**Title:** Reproducible Sparse-Concept and Calibration Diagnostics for Knowledge Tracing  
**Date packed:** 6 September 2026  
**Length:** 8–10 pages named + blind (current PDFs: 9). Title 20 pt.

This is a protocol/diagnostic paper. TSCDA is **not** named. GKT/CL4KT are **not** scored.

## Upload these files

| OJS slot | File | Who sees it |
|----------|------|-------------|
| Manuscript (editor) | `main_ijiet_full.doc` (or `.docx`) | Editorial office |
| Manuscript PDF (editor) | `main_ijiet_full.pdf` | Editorial office |
| Review file (double-blind) | `main_ijiet_blind.pdf` | Reviewers |
| Optional Word for review | `main_ijiet_blind.doc` | Reviewers if OJS asks for Word |
| Supplementary | `supplementary.pdf` | Reviewers (S1–S10) |
| Code for review | `code_for_review_anonymous.zip` | Reviewers |
| Cover letter | `cover_letter_ijiet.txt` | Editor only (names JEDM withdrawal) |

Do **not** send reviewers `main_ijiet_full.pdf` / named Word.  
Do **not** upload `_archive/`.

## Checks already done

- ASSISTments locks: ECE 0.1136 / 0.2280; FAR 0.196 / 0.268
- Blind PDF has no author names or github.com/trinhnkt
- Article text does not name JEDM
- Zip excludes JEDM sources and named Word

Public repo after review: https://github.com/trinhnkt/Sparse-Concept-and-Calibration
"""


def export_named_doc(log: list[str]) -> None:
    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(FULL_DOCX))
        doc.SaveAs2(str(FULL_DOC), WD_FORMAT_DOC)
        log.append(f"named_doc={FULL_DOC.name}")
        doc.Close(WD_SAVE)
        doc = None
    finally:
        if doc is not None:
            doc.Close(0)
        word.Quit()


def zip_ok(path: Path) -> None:
    names = []
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        blob = " ".join(names).lower()
        if "main_jedm" in blob or "khanh-trinh" in blob or "_archive/" in blob:
            raise SystemExit("zip still contains identity/JEDM paths")
        if "main_ijiet_full.docx" in blob:
            raise SystemExit("zip contains named Word")
        if "Table_S4_occupancy_policies.tex" not in " ".join(names):
            raise SystemExit("zip missing Table S4 tex")


def copy_ojs(log: list[str]) -> None:
    if OJS.exists():
        shutil.rmtree(OJS)
    OJS.mkdir(parents=True)
    files = [
        FULL_DOC,
        FULL_DOCX,
        FULL_PDF,
        BLIND_DOC,
        BLIND_DOCX,
        BLIND_PDF,
        SUP_PDF,
        REVIEW_ZIP,
        COVER,
        README_REVIEW,
    ]
    for src in files:
        if not src.is_file():
            raise SystemExit(f"missing {src}")
        shutil.copy2(src, OJS / src.name)
        log.append(f"ojs {src.name}")
    (OJS / "README_SUBMIT.md").write_text(OJS_README, encoding="utf-8")


def sync_submission_slots(log: list[str]) -> None:
    dest_src = SUB / "source"
    dest_out = SUB / "output"
    dest_src.mkdir(parents=True, exist_ok=True)
    dest_out.mkdir(parents=True, exist_ok=True)
    pairs = [
        (FULL_DOCX, dest_src / "main_ijiet_full.docx"),
        (FULL_DOC, dest_src / "main_ijiet_full.doc"),
        (BLIND_DOCX, dest_src / "main_ijiet_blind.docx"),
        (BLIND_DOC, dest_src / "main_ijiet_blind.doc"),
        (FULL_PDF, dest_out / "main_ijiet_full.pdf"),
        (BLIND_PDF, dest_out / "main_ijiet_blind.pdf"),
        (SUP_PDF, dest_out / "supplementary.pdf"),
        (REVIEW_ZIP, dest_out / "code_for_review_anonymous.zip"),
        (COVER, dest_out / "cover_letter_ijiet.txt"),
    ]
    for src, dst in pairs:
        shutil.copy2(src, dst)
        log.append(f"sync {dst.relative_to(SUB.parent)}")
    (dest_out / "CURRENT_A29.txt").write_text(
        "These main_ijiet_full/blind PDFs and source Word files were copied from "
        "IJIET_FINAL_REVISION on 2026-09-06 (P0 protocol pack; 8–10 pages). "
        "Submit from IJIET_FINAL_REVISION/output/OJS_UPLOAD/. Do not upload _archive/.\n",
        encoding="utf-8",
    )


def write_revision_readme() -> None:
    readme = HERE / "README.md"
    text = readme.read_text(encoding="utf-8")
    marker = "## Integrity"
    addition = """## Submit here

OJS files: `output/OJS_UPLOAD/` (see `README_SUBMIT.md` there).

Current named/blind PDFs and Word in `output/` and `manuscript/` are A29
(title restored; A28 science kept). Copies also sit in `IJIET_SUBMISSION/`.
Do not upload `_archive/`.

"""
    if "## Submit here" in text:
        return
    if marker in text:
        readme.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")
    else:
        readme.write_text(text + "\n" + addition, encoding="utf-8")



def write_sub_readme() -> None:
    p = SUB / "README.md"
    p.write_text(
        """# IJIET submission copies

Current named/blind Word: `source/main_ijiet_full.*` and `source/main_ijiet_blind.*`
Current PDFs, supplementary, cover letter, anonymous zip: `output/`

Official template: `source/template/IJIET_template.doc`
Living edits: `../IJIET_FINAL_REVISION/`
Upload pack: `../IJIET_FINAL_REVISION/output/OJS_UPLOAD/`

Withdrawn JEDM sources are in `../_archive/` and are not part of this submission.
""",
        encoding="utf-8",
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    log: list[str] = ["A30"]
    export_named_doc(log)
    pack_review_zip(log)
    zip_ok(REVIEW_ZIP)
    copy_ojs(log)
    sync_submission_slots(log)
    write_revision_readme()
    write_sub_readme()

    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)
    log.append(f"FULL_PAGES={full_pages} BLIND_PAGES={blind_pages}")
    log.append(f"FULL_LOCKS={full_locks}")
    log.append(f"BLIND_LOCKS={blind_locks}")
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"ojs={OJS}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n",
        encoding="utf-8",
    )
    CHANGELOG.write_text(
        f"""# CHANGELOG_A30 — IJIET OJS pack

**Date:** 2026-09-01  
**Retrain:** no. **Title:** A27 string. **Science:** A28 kept.

Packed `output/OJS_UPLOAD/` and synced current slots in `IJIET_SUBMISSION/`
(source Word + output PDFs/zip/cover/supplementary). Step PDFs left in place.

Named/blind: {full_pages} / {blind_pages} pages.
""",
        encoding="utf-8",
    )
    print("\n".join(log))
    if PAPER_TITLE.split()[0] not in full_t:
        raise SystemExit("A27 title missing")
    if "TSCDA: Sparse-Concept and Calibration Diagnostics for Knowledge Tracing" in full_t:
        raise SystemExit("A28 title returned")
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise SystemExit("lock checks failed")
    if full_pages != 8 or blind_pages != 8:
        raise SystemExit("page count")
    if "JEDM" in full_t:
        raise SystemExit("JEDM named")
    if "Khanh-Trinh" in blind_t or "github.com/trinhnkt" in blind_t.lower():
        raise SystemExit("blind identified")


if __name__ == "__main__":
    main()
