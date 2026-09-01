#!/usr/bin/env python3
"""One-shot cleanup: IJIET-facing layout. Does not change manuscript numbers."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "_archive"


def git(*args: str) -> None:
    subprocess.run(["git", *args], cwd=str(ROOT), check=True)


def git_tracked(path: str) -> bool:
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=str(ROOT),
        capture_output=True,
    )
    return r.returncode == 0


def rm_path(p: Path) -> None:
    if not p.exists():
        return
    rel = p.relative_to(ROOT).as_posix()
    if p.is_dir():
        if git_tracked(rel) or any(git_tracked(c.relative_to(ROOT).as_posix()) for c in p.rglob("*") if c.is_file()):
            git("rm", "-rf", "--ignore-unmatch", rel)
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    else:
        if git_tracked(rel):
            git("rm", "-f", "--ignore-unmatch", rel)
        elif p.exists():
            p.unlink()


def git_mv(src: str, dst: str) -> None:
    dest = ROOT / dst
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not (ROOT / src).exists():
        return
    git("mv", src, dst)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ARCHIVE.mkdir(exist_ok=True)

    git_mv("paper", "_archive/jedm_paper")
    git_mv("jedm_upload_folder", "_archive/jedm_upload_folder")
    git_mv("REV_REVIEWER_CALIBRATION_v1", "_archive/REV_REVIEWER_CALIBRATION_v1")
    git_mv("ijiet", "_archive/ijiet_ieee_draft")
    git_mv("w2_verification", "_archive/w2_verification")
    git_mv("audit", "_archive/jedm_audit")
    git_mv("docs", "_archive/docs")

    for name in [
        "CHANGELOG_A1.md",
        "CHANGELOG_A2.md",
        "CHANGELOG_A3.md",
        "CHANGELOG_A4.md",
        "CHANGELOG_A5.md",
        "CHANGELOG_A6.md",
        "CHANGELOG_A7.md",
        "CHANGELOG_A8.md",
        "CHANGELOG_A9.md",
        "CHANGELOG_A10.md",
        "CHANGELOG_C.md",
        "CHANGELOG_SETUP.md",
        "REVISION_SUMMARY.md",
        "controlled_sparsification_protocol.md",
    ]:
        git_mv(name, f"_archive/{name}")

    sub_rm = []
    sub = ROOT / "IJIET_SUBMISSION"
    for p in (sub / "output").glob("main_ijiet_step*"):
        sub_rm.append(p.relative_to(ROOT).as_posix())
    for p in (sub / "source").glob("main_ijiet_step*"):
        sub_rm.append(p.relative_to(ROOT).as_posix())
    for p in (sub / "source").glob("prepare_step*"):
        sub_rm.append(p.relative_to(ROOT).as_posix())
    for p in (sub / "source").glob("_*"):
        sub_rm.append(p.relative_to(ROOT).as_posix())
    for extra in [
        "IJIET_SUBMISSION/output/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.doc",
        "IJIET_SUBMISSION/output/Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing.docx",
        "IJIET_SUBMISSION/source/build_ijiet_docx.py",
        "IJIET_SUBMISSION/source/fill_ijiet_from_template.py",
        "IJIET_SUBMISSION/source/snapshots/main_ijiet_ieee_draft.tex",
        "IJIET_SUBMISSION/source/snapshots/main_ijiet_pre18_snake.doc",
        "IJIET_SUBMISSION/source/snapshots/BIB_SOURCE.txt",
    ]:
        sub_rm.append(extra)
    if (sub / "audit").exists():
        git_mv("IJIET_SUBMISSION/audit", "_archive/ijiet_submission_audit")

    if sub_rm:
        git("rm", "-f", "--ignore-unmatch", *sub_rm)

    junk_dirs = [
        ROOT / ".pytest_cache",
        ROOT / "logs",
        ROOT / "scratch",
        ROOT / "IJIET_SUBMISSION" / "source" / "__pycache__",
        ROOT / "IJIET_SUBMISSION" / "source" / "snapshots",
    ]
    for d in junk_dirs:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)

    for p in ROOT.glob("*.log"):
        p.unlink(missing_ok=True)

    ms = ROOT / "IJIET_FINAL_REVISION" / "manuscript"
    if ms.exists():
        for p in ms.glob("*.bak_pre_*"):
            p.unlink(missing_ok=True)
    for p in (ROOT / "IJIET_SUBMISSION").rglob("~$*"):
        p.unlink(missing_ok=True)
    for p in (ROOT / "IJIET_FINAL_REVISION" / "supplementary").glob("supplementary.*"):
        if p.suffix in {".aux", ".log", ".out"}:
            p.unlink(missing_ok=True)
    base_pdf = ROOT / "IJIET_FINAL_REVISION" / "output" / "baseline_from_ijiet_submission.pdf"
    base_pdf.unlink(missing_ok=True)

    audit = ROOT / "IJIET_FINAL_REVISION" / "audit"
    if audit.exists():
        for pat in (
            "_a*_pdf_text.txt",
            "_desk_*",
            "_rev_*",
            "apply_*_log.txt",
            "format_a23_measure*.txt",
        ):
            for p in audit.glob(pat):
                if p.suffix in {".md"}:
                    continue
                p.unlink(missing_ok=True)

    (ARCHIVE / "README.md").write_text(
        """# Archive (not for IJIET OJS)

Withdrawn JEDM sources and conversion snapshots. Do not upload.

| Path | What |
|------|------|
| `jedm_paper/` | Original JEDM LaTeX (`paper/`) |
| `jedm_upload_folder/` | JEDM camera-ready bundle |
| `REV_REVIEWER_CALIBRATION_v1/` | JEDM reviewer revision |
| `ijiet_ieee_draft/` | Early IEEE-style IJIET TeX |
| `ijiet_submission_audit/` | Step-by-step conversion logs |
| `jedm_audit/`, `docs/`, `w2_verification/` | Pre-IJIET audits |

Submit from `IJIET_FINAL_REVISION/output/OJS_UPLOAD/`.
""",
        encoding="utf-8",
    )
    print("cleanup done")


if __name__ == "__main__":
    main()
