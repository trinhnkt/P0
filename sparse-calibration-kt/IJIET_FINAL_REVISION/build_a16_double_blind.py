#!/usr/bin/env python3
"""A16: named + double-blind IJIET PDFs. Does not change scientific table cells.

Does not write to IJIET_SUBMISSION/.
"""
from __future__ import annotations

import json
import shutil
import ssl
import urllib.request
from pathlib import Path

import fitz
import win32com.client as win32

HERE = Path(__file__).resolve().parent
FULL_DOCX = HERE / "manuscript" / "main_ijiet_full.docx"
FULL_DOC = HERE / "manuscript" / "main_ijiet_full.doc"
BLIND_DOCX = HERE / "manuscript" / "main_ijiet_blind.docx"
BLIND_DOC = HERE / "manuscript" / "main_ijiet_blind.doc"
FULL_PDF = HERE / "output" / "main_ijiet_full.pdf"
BLIND_PDF = HERE / "output" / "main_ijiet_blind.pdf"
AUDIT = HERE / "audit" / "DOUBLE_BLIND_AUDIT.md"
CHANGELOG = HERE / "audit" / "CHANGELOG_A16.md"
VERIFY = HERE / "audit" / "compile_verify.txt"
LOG = HERE / "audit" / "apply_a16_blind_log.txt"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_REPLACE_ALL = 2
WD_FIND_CONTINUE = 1
WD_FORMAT_PDF = 17

TITLE = (
    "Sparse-Concept Calibration of Knowledge Tracing Models "
    "for Threshold-Based Educational Decisions"
)
AUTHORS_META = (
    "Khanh-Trinh Nguyen, Tuan Dao Minh, Duong Nguyen Tien, "
    "Chi Thanh Nguyen, Van-Hau Nguyen"
)
ANON_AUTHORS = "Anonymous Authors"
ANON_AFFIL = "Affiliations omitted for double-blind review."
ANON_CONTRIB = (
    "Author 1: Conceptualization, Methodology, Software, Formal analysis, and "
    "Writing (led diagnostic design, experiments, and manuscript). Authors 2 and 3: "
    "Software (data processing and baseline runs). Author 4: Methodology "
    "(methodological review). Author 5: Supervision and Writing (manuscript "
    "revision). All authors approved the final version."
)
ANON_ACK = "Omitted for double-blind review."
ANON_URL = "https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/"
REPO_API = "https://anonymous.4open.science/api/repo/Sparse-Concept-and-Calibration-6E5B"

IDENTIFYING = [
    "Khanh-Trinh",
    "Tuan Dao Minh",
    "Duong Nguyen Tien",
    "Chi Thanh Nguyen",
    "Van-Hau",
    "Hung Yen",
    "utehy.edu.vn",
    "trinhnk",
    "tuanymc",
    "duongnt@",
    "thanhnc",
    "haunv@",
    "ioit.ai.vn",
    "Military Science",
    "Academy of Military",
    "ORCID",
    "0009-0004",
    "0009-0009",
    "0009-0007",
    "0000-0003-4335",
    "0000-0002-3256",
    "github.com/trinhnkt",
    "K.-T.N.",
    "T.D.M.",
    "D.N.T.",
    "C.T.N.",
    "V.-H.N.",
]

KEEP_IN_BLIND = [
    "ASSISTments",
    "Junyi Academy",
    "XES3G5M",
    ANON_URL,
    "Corbett",
]

BYTE_NEEDLES = [
    b"Khanh-Trinh",
    b"Hung Yen",
    b"utehy.edu",
    b"trinhnk",
    b"Van-Hau Nguyen",
    b"Tuan Dao Minh",
    b"github.com/trinhnkt",
    b"haunv@",
    b"ioit.ai.vn",
]


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def set_word_props(doc, author: str, company: str) -> None:
    def _set(name: str, value: str) -> None:
        try:
            doc.BuiltInDocumentProperties(name).Value = value
        except Exception:
            pass

    _set("Title", TITLE)
    _set("Author", author)
    _set("Last Author", author)
    _set("Company", company)
    _set("Manager", "")
    _set("Comments", "")
    _set("Subject", "")


def export_pdf(doc, path: Path, include_props: bool) -> None:
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.ExportAsFixedFormat(
        str(path),
        WD_FORMAT_PDF,
        OpenAfterExport=False,
        OptimizeFor=0,
        Item=0,
        IncludeDocProps=include_props,
        KeepIRM=True,
        CreateBookmarks=1,
        DocStructureTags=True,
        BitmapMissingFonts=True,
        UseISO19005_1=False,
    )


def stamp_pdf_metadata(path: Path, author: str) -> dict:
    d = fitz.open(str(path))
    meta = {
        "title": TITLE,
        "author": author,
        "subject": "",
        "keywords": "",
        "creator": "",
        "producer": "",
        "creationDate": "",
        "modDate": "",
    }
    d.set_metadata(meta)
    tmp = path.with_suffix(".tmp.pdf")
    d.save(str(tmp), garbage=4, deflate=True)
    d.close()
    tmp.replace(path)
    d2 = fitz.open(str(path))
    out = dict(d2.metadata or {})
    d2.close()
    return out


def pdf_text(path: Path) -> tuple[str, int]:
    d = fitz.open(str(path))
    t = "\n".join(p.get_text() for p in d)
    n = d.page_count
    d.close()
    return t, n


def compact(text: str) -> str:
    return "".join(text.split())


def hits(text: str, needles: list[str]) -> list[str]:
    found = []
    low = text.lower()
    compact_low = compact(text).lower()
    for n in needles:
        needle = n.lower()
        if needle in low or needle in compact_low:
            found.append(n)
    return found


def token_present(text: str, token: str) -> bool:
    if token.startswith("http"):
        return token in compact(text)
    return token in text


def lock_checks(text: str, n_pages: int) -> dict[str, bool]:
    c = compact(text).lower()
    return {
        "pages_8_to_10": 8 <= n_pages <= 10,
        "ece_1136": "0.1136" in text,
        "ece_2280": "0.2280" in text,
        "far_196": "0.196" in text,
        "far_268": "0.268" in text,
        "fig1": "Fig. 1." in text,
        "ref21": "uncertainty-awareknowledgetracing" in c,
        "ref22": "knowingwhentodefer" in c,
    }


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
        elif raw.startswith("Email:") or raw.startswith("haunv@utehy"):
            delete_i.append(i)
            lines.append(f"DEL_EMAIL i={i}")
        elif "Corresponding author" in raw:
            delete_i.append(i)
            lines.append(f"DEL_CORR i={i}")
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

    for sec in doc.Sections:
        for hf in (sec.Headers, sec.Footers):
            for k in range(1, hf.Count + 1):
                rng = hf(k).Range
                t = rng.Text or ""
                if any(n.lower() in t.lower() for n in IDENTIFYING if len(n) >= 6):
                    rng.Text = ""
                    lines.append("CLEARED_HEADER_FOOTER")


def http_get(path: str) -> bytes:
    url = REPO_API + path
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=ctx, timeout=45) as r:
        return r.read()


def check_anonymous_repo() -> dict:
    out: dict = {
        "url": ANON_URL,
        "reachable": False,
        "readme_github_owner": "",
        "named_jedm_hits": [],
        "github_trinhnkt": False,
        "files_with_identity": [],
        "error": "",
    }
    needles = [
        b"github.com/trinhnkt",
        b"utehy.edu.vn",
        b"Hung Yen",
        b"haunv@",
        b"trinhnk@",
        b"Khanh-Trinh",
        b"Van-Hau",
        b"ioit.ai.vn",
        b"tuanymc@",
        b"thanhnc@",
        b"0009-0004",
    ]
    try:
        listing = json.loads(http_get("/files").decode())
        out["reachable"] = True
        out["root_names"] = [x.get("name") for x in listing]
        readme = http_get("/file/sparse-calibration-kt/README.md")
        out["github_trinhnkt"] = b"github.com/trinhnkt" in readme.lower() or (
            b"trinhnkt" in readme.lower()
        )
        rm = readme.decode("utf-8", "replace")
        if "github.com/" in rm:
            for line in rm.splitlines():
                if "github.com/" in line:
                    out["readme_github_owner"] = line.strip()
                    break
        targets = [
            "sparse-calibration-kt/paper/main_jedm.tex",
            "sparse-calibration-kt/jedm_upload_folder/main_jedm.tex",
            "sparse-calibration-kt/paper/main_jedm_anonymous.tex",
            "sparse-calibration-kt/README.md",
            "setup_EXPERIMENT_P0.md",
        ]
        for p in targets:
            data = http_get("/file/" + p)
            found = [n.decode() for n in needles if n.lower() in data.lower()]
            if found:
                out["files_with_identity"].append({"path": p, "hits": found})
            if p.endswith("main_jedm.tex") and not p.endswith("anonymous.tex"):
                out["named_jedm_hits"] = found
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def verdict(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def write_audit(
    full_meta: dict,
    blind_meta: dict,
    full_hits: list[str],
    blind_hits: list[str],
    keep_ok: dict,
    full_pages: int,
    blind_pages: int,
    byte_hits: list[str],
    full_locks: dict,
    blind_locks: dict,
    repo: dict,
    lines: list[str],
    anon_present: bool,
) -> dict[str, str]:
    visible_ok = bool(full_hits) and not blind_hits and not byte_hits
    meta_author = (blind_meta.get("author") or "").strip()
    meta_ok = not meta_author
    # URL / GitHub login in the IJIET link itself
    url_ok = "anonymous.4open.science" in ANON_URL and "trinhnkt" not in ANON_URL
    readme_ok = not repo.get("github_trinhnkt")
    content_ok = not repo.get("files_with_identity")
    repo_ok = (
        repo.get("reachable")
        and url_ok
        and readme_ok
        and content_ok
        and not repo.get("error")
    )
    ack_ok = not any(
        n in (h.lower() for h in [x.lower() for x in blind_hits])
        for n in ("hung yen", "utehy", "military")
    )
    # acknowledgments identity: no institutional wording in blind hits
    ack_pass = visible_ok  # ack replacement is part of visible identity scan

    reports = {
        "visible_author_identity": verdict(visible_ok),
        "pdf_metadata_identity": verdict(meta_ok),
        "repository_identity": verdict(bool(repo_ok)),
        "acknowledgments_identity": verdict(ack_pass),
    }

    keep_lines = [f"- `{k}`: {'present' if v else 'MISSING'}" for k, v in keep_ok.items()]
    repo_files = repo.get("files_with_identity") or []
    repo_file_md = (
        "\n".join(
            f"- `{x['path']}`: {', '.join(x['hits'])}" for x in repo_files
        )
        or "- (none)"
    )

    body = f"""# DOUBLE_BLIND_AUDIT — IJIET named vs review PDF

**Date:** 2026-09-01  
**Policy:** IJIET ethics (list-77-1) uses double-blind peer review. The official template is named; this task ships **two** PDFs. Isolation: `IJIET_FINAL_REVISION/` only.

| Build | Path | Pages |
|-------|------|------:|
| Named (editor / camera-ready) | `output/main_ijiet_full.pdf` | {full_pages} |
| Double-blind review | `output/main_ijiet_blind.pdf` | {blind_pages} |

Word sources: `manuscript/main_ijiet_full.docx` (unchanged science) and `manuscript/main_ijiet_blind.docx`.

## PASS / FAIL

| Check | Result |
|-------|--------|
| Visible author identity (blind PDF) | **{reports['visible_author_identity']}** |
| PDF metadata identity (blind `/Author`) | **{reports['pdf_metadata_identity']}** |
| Repository identity | **{reports['repository_identity']}** |
| Acknowledgments identity (blind PDF) | **{reports['acknowledgments_identity']}** |

## Visible author identity

Blind PDF must contain none of the author names, emails, affiliation strings, or CRediT initials. Named PDF must still contain them.

- Named PDF hits: {', '.join(full_hits) if full_hits else '(none — FAIL)'}
- Blind PDF text hits: {', '.join(blind_hits) if blind_hits else '(none)'}
- Blind PDF raw-byte hits: {', '.join(byte_hits) if byte_hits else '(none)'}
- Blind PDF contains `Anonymous Authors`: {'yes' if anon_present else 'no'}

Removed in the blind Word/PDF only: names; numbered affiliations; emails; `*Corresponding author`; Author-contribution initials (`K.-T.N.` … → Author 1–5).

## PDF metadata identity

| Field | Full | Blind |
|-------|------|-------|
| Author | `{full_meta.get('author', '')}` | `{blind_meta.get('author', '') or '(blank)'}` |
| Creator | `{full_meta.get('creator', '') or '(blank)'}` | `{blind_meta.get('creator', '') or '(blank)'}` |
| Producer | `{full_meta.get('producer', '') or '(blank)'}` | `{blind_meta.get('producer', '') or '(blank)'}` |

## Repository identity

Review URL (retained in both PDFs): `{ANON_URL}`

Live listing via `anonymous.4open.science` API (2026-09-01):

- Reachable: {repo.get('reachable')}
- Root entries: {', '.join(repo.get('root_names') or [])}
- README clone line: `{repo.get('readme_github_owner') or '(none)'}`
- `github.com/trinhnkt` in README: {repo.get('github_trinhnkt')}
- Fetch error: {repo.get('error') or '(none)'}

Identity-bearing files inside that snapshot:

{repo_file_md}

The URL host is anonymous and does not contain a GitHub login. README clones `github.com/anonymous-researcher-2026/sparse-calibration-kt.git` (placeholder owner). The **named** JEDM sources `paper/main_jedm.tex` and `jedm_upload_folder/main_jedm.tex` in the same snapshot still list author names, `utehy.edu.vn` / `ioit.ai.vn` emails, Hung Yen / Military Science affiliations, and ORCID in the named tex. `paper/main_jedm.pdf` is the named compiled JEDM PDF. That is a repository-identity leak for IJIET reviewers who open those paths. `paper/main_jedm_anonymous.tex` uses Anonymous Authors / `anonymous@example.com` and was not counted as a leak.

This task does **not** rewrite the 4open.science snapshot. The IJIET manuscripts keep the existing anonymous URL.

## Acknowledgments identity

Blind acknowledgment body is `Omitted for double-blind review.` Institutional “respective institutions” wording is removed. Dataset names in the ethics statement are public benchmarks and are retained.

## Scientifically retained in the blind PDF

{chr(10).join(keep_lines)}

Public dataset names, numbered model citations, and the anonymous.4open.science URL are retained.

## Scientific locks (both PDFs)

Named: {full_locks}
Blind: {blind_locks}

ASSISTments cells were not edited. Tables/figure counts must match the named source.

## Anonymize log

```
{chr(10).join(lines)}
```
"""
    AUDIT.write_text(body, encoding="utf-8")
    return reports


def main() -> None:
    if not FULL_DOCX.exists():
        raise SystemExit(f"missing {FULL_DOCX}")
    lines: list[str] = ["A16 double-blind build"]
    repo = check_anonymous_repo()
    lines.append(f"REPO={json.dumps(repo, ensure_ascii=False)}")

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    full_doc = None
    blind_doc = None
    try:
        full_doc = word.Documents.Open(str(FULL_DOCX), ReadOnly=True)
        body = full_doc.Content.Text
        if "Khanh-Trinh Nguyen" not in body:
            raise RuntimeError("named source missing author line")
        export_pdf(full_doc, FULL_PDF, include_props=True)
        lines.append(
            f"FULL_TABLES={full_doc.Tables.Count} FIGS={full_doc.InlineShapes.Count}"
        )
        n_tables = full_doc.Tables.Count
        n_figs = full_doc.InlineShapes.Count
        full_doc.Close(0)
        full_doc = None

        shutil.copy2(FULL_DOCX, BLIND_DOCX)
        blind_doc = word.Documents.Open(str(BLIND_DOCX))
        anonymize_blind(blind_doc, lines)
        set_word_props(blind_doc, "", "")
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
            raise RuntimeError(
                f"blind structure changed tables={blind_doc.Tables.Count}/{n_tables} "
                f"figs={blind_doc.InlineShapes.Count}/{n_figs}"
            )
        lines.append(
            f"BLIND_TABLES={blind_doc.Tables.Count} FIGS={blind_doc.InlineShapes.Count}"
        )
        blind_doc.Close(WD_SAVE)
        blind_doc = None
    finally:
        if full_doc is not None:
            full_doc.Close(0)
        if blind_doc is not None:
            blind_doc.Close(0)
        word.Quit()

    full_meta = stamp_pdf_metadata(FULL_PDF, AUTHORS_META)
    blind_meta = stamp_pdf_metadata(BLIND_PDF, "")
    full_t, full_pages = pdf_text(FULL_PDF)
    blind_t, blind_pages = pdf_text(BLIND_PDF)
    full_hits = hits(full_t, IDENTIFYING)
    blind_hits = hits(blind_t, IDENTIFYING)
    keep_ok = {k: token_present(blind_t, k) for k in KEEP_IN_BLIND}
    byte_hits = [n.decode() for n in BYTE_NEEDLES if n in BLIND_PDF.read_bytes()]
    full_locks = lock_checks(full_t, full_pages)
    blind_locks = lock_checks(blind_t, blind_pages)

    lines.append(f"FULL_PAGES={full_pages}")
    lines.append(f"BLIND_PAGES={blind_pages}")
    lines.append(f"FULL_META_AUTHOR={full_meta.get('author')!r}")
    lines.append(f"BLIND_META_AUTHOR={blind_meta.get('author')!r}")
    lines.append(f"FULL_HITS={full_hits}")
    lines.append(f"BLIND_HITS={blind_hits}")
    lines.append(f"BLIND_BYTE_HITS={byte_hits}")
    lines.append(f"KEEP={keep_ok}")
    lines.append(f"FULL_LOCKS={full_locks}")
    lines.append(f"BLIND_LOCKS={blind_locks}")

    if "Anonymous Authors" not in blind_t:
        raise RuntimeError("blind PDF missing Anonymous Authors")
    reports = write_audit(
        full_meta,
        blind_meta,
        full_hits,
        blind_hits,
        keep_ok,
        full_pages,
        blind_pages,
        byte_hits,
        full_locks,
        blind_locks,
        repo,
        lines,
        "Anonymous Authors" in blind_t,
    )

    if "Khanh-Trinh" not in full_t:
        raise RuntimeError("named PDF lost author names")
    if blind_hits:
        raise RuntimeError(f"blind PDF still identifying: {blind_hits}")
    if byte_hits:
        raise RuntimeError(f"blind PDF bytes still identifying: {byte_hits}")
    if (blind_meta.get("author") or "").strip():
        raise RuntimeError(f"blind metadata author not blank: {blind_meta.get('author')!r}")
    if not all(keep_ok.values()):
        raise RuntimeError(f"blind PDF dropped scientific tokens: {keep_ok}")
    if not all(full_locks.values()) or not all(blind_locks.values()):
        raise RuntimeError(f"lock checks failed full={full_locks} blind={blind_locks}")

    VERIFY.write_text(
        f"source={FULL_DOCX}\n"
        f"pdf={FULL_PDF}\n"
        f"blind_pdf={BLIND_PDF}\n"
        f"pages={full_pages}\n"
        f"blind_pages={blind_pages}\n"
        f"bytes={FULL_PDF.stat().st_size}\n"
        + "\n".join(f"{k}={v}" for k, v in full_locks.items())
        + "\n"
        + "\n".join(f"blind_{k}={v}" for k, v in blind_locks.items())
        + "\n"
        + "\n".join(f"audit_{k}={v}" for k, v in reports.items())
        + "\n",
        encoding="utf-8",
    )
    CHANGELOG.write_text(
        f"""# CHANGELOG_A16 — IJIET double-blind manuscript

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged (`0.1136`, `0.2280`, FAR `0.196`/`0.268`, ΔFAR `0.047`, CI `[0.006, 0.138]`).

Same-day XES/A2B scientific apply is preserved in `audit/CHANGELOG_A16_XES.md`.

## Builds

| File | Role |
|------|------|
| `output/main_ijiet_full.pdf` | Named manuscript ({full_pages} pages) |
| `output/main_ijiet_blind.pdf` | Double-blind review ({blind_pages} pages) |
| `manuscript/main_ijiet_full.docx` | Named Word (science unchanged) |
| `manuscript/main_ijiet_blind.docx` | Blind Word |
| `manuscript/main_ijiet_blind.doc` | Blind Word 97–2003 |

## Blind removals

Author names, affiliations, emails, corresponding-author line, CRediT initials, identifying acknowledgment. PDF `/Author` (and Creator/Producer) cleared on the blind file only.

## Retained

Public dataset names; numbered citations; `https://anonymous.4open.science/r/Sparse-Concept-and-Calibration-6E5B/`.

## Audit

See `audit/DOUBLE_BLIND_AUDIT.md`.

| Check | Result |
|-------|--------|
| Visible author identity | {reports['visible_author_identity']} |
| PDF metadata identity | {reports['pdf_metadata_identity']} |
| Repository identity | {reports['repository_identity']} |
| Acknowledgments identity | {reports['acknowledgments_identity']} |

Repository identity is **FAIL** if the live 4open snapshot still contains named JEDM `main_jedm.tex` / emails. The manuscript URL was not changed.

## Files

- `IJIET_FINAL_REVISION/build_a16_double_blind.py`
- `IJIET_FINAL_REVISION/audit/DOUBLE_BLIND_AUDIT.md`
- this changelog
""",
        encoding="utf-8",
    )
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(VERIFY.read_text(encoding="utf-8"))
    print("AUDIT", reports)


if __name__ == "__main__":
    main()
