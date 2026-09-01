#!/usr/bin/env python3
"""IJIET-14: audit and restyle the numbered reference list."""
from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "IJIET_SUBMISSION" / "source"
STEP13 = SRC / "main_ijiet_step13.docx"
STEP14_DOCX = SRC / "main_ijiet_step14.docx"
STEP14_DOC = SRC / "main_ijiet_step14.doc"
OUT_PDF = ROOT / "IJIET_SUBMISSION" / "output" / "main_ijiet_step14.pdf"
REPORT = ROOT / "IJIET_SUBMISSION" / "audit" / "step14_verify.txt"
CSV_PATH = ROOT / "IJIET_SUBMISSION" / "audit" / "REFERENCE_AUDIT_FULL.csv"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_SAVE = -1
WD_FIND_STOP = 0

# IJIET style: IEEE numbered punctuation; journal/book titles italic;
# verified DOIs as "doi: …" (2026 published IJIET articles); [Online]. Available
# only for electronic dataset records. No invented months, pages, or DOIs.

REFS = [
    {
        "no": 1,
        "match": "A. T. Corbett",
        "first": "Corbett",
        "title": "Knowledge Tracing: Modeling the acquisition of procedural knowledge",
        "venue": "User Modeling and User-Adapted Interaction",
        "year": "1994",
        "doi": "10.1007/BF01099821",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "Springer journal; vol. 4, no. 4, pp. 253-278. Added doi. Q. Liu N/A.",
        "text": (
            "A. T. Corbett and J. R. Anderson, “Knowledge Tracing: Modeling the "
            "acquisition of procedural knowledge,” User Modeling and User-Adapted "
            "Interaction, vol. 4, no. 4, pp. 253–278, 1994. doi: 10.1007/BF01099821"
        ),
        "italic": ["User Modeling and User-Adapted Interaction"],
    },
    {
        "no": 2,
        "match": "C. Piech",
        "first": "Piech",
        "title": "Deep Knowledge Tracing",
        "venue": "Advances in Neural Information Processing Systems",
        "year": "2015",
        "doi": "",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "NIPS 2015 = Adv. Neural Inf. Process. Syst. vol. 28, pp. 505-513. No Crossref journal DOI. Added vol. 28.",
        "text": (
            "C. Piech, J. Bassen, J. Huang, S. Ganguli, M. Sahami, L. J. Guibas, and "
            "J. Sohl-Dickstein, “Deep Knowledge Tracing,” in Advances in Neural "
            "Information Processing Systems, vol. 28, 2015, pp. 505–513."
        ),
        "italic": ["Advances in Neural Information Processing Systems"],
    },
    {
        "no": 3,
        "match": "G. Abdelrahman",
        "first": "Abdelrahman",
        "title": "Knowledge Tracing: A survey",
        "venue": "ACM Computing Surveys",
        "year": "2023",
        "doi": "10.1145/3569576",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "CSUR vol. 55, no. 11, pp. 1-37. B. Nunes matches ACM listing. Added doi.",
        "text": (
            "G. Abdelrahman, Q. Wang, and B. Nunes, “Knowledge Tracing: A survey,” "
            "ACM Computing Surveys, vol. 55, no. 11, pp. 1–37, 2023. doi: 10.1145/3569576"
        ),
        "italic": ["ACM Computing Surveys"],
    },
    {
        "no": 4,
        "match": "SimpleKT",
        "first": "Liu",
        "title": "SimpleKT: A simple but tough-to-beat baseline for Knowledge Tracing",
        "venue": "The Eleventh International Conference on Learning Representations",
        "year": "2023",
        "doi": "",
        "status": "VERIFIED",
        "correction": "NO",
        "notes": "ICLR 2023; OpenReview 9HiGqC9C-KA; arXiv 2302.06881. No Crossref DOI. Q. Liu = Qiongqiong Liu.",
        "text": (
            "Z. Liu, Q. Liu, J. Chen, S. Huang, and W. Luo, “SimpleKT: A simple but "
            "tough-to-beat baseline for Knowledge Tracing,” in The Eleventh "
            "International Conference on Learning Representations, 2023."
        ),
        "italic": [],
    },
    {
        "no": 5,
        "match": "pyKT",
        "first": "Liu",
        "title": "pyKT: A python library to benchmark deep learning based Knowledge Tracing models",
        "venue": "36th Conference on Neural Information Processing Systems Datasets and Benchmarks Track",
        "year": "2022",
        "doi": "",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "NeurIPS 2022 D&B is the 36th conference (paper footer). Not 37th. No book-series volume used (vol. 35 would collide with 36th numbering). No Crossref DOI. Q. Liu = Qiongqiong Liu; J. Tang present.",
        "text": (
            "Z. Liu, Q. Liu, J. Chen, S. Huang, J. Tang, and W. Luo, “pyKT: A python "
            "library to benchmark deep learning based Knowledge Tracing models,” in "
            "Proc. 36th Conference on Neural Information Processing Systems Datasets "
            "and Benchmarks Track, 2022."
        ),
        "italic": [],
    },
    {
        "no": 6,
        "match": "G. Rasch",
        "first": "Rasch",
        "title": "Probabilistic Models for Some Intelligence and Attainment Tests",
        "venue": "Danish Institute for Educational Research",
        "year": "1960",
        "doi": "",
        "status": "VERIFIED",
        "correction": "NO",
        "notes": "Book; no DOI. City not added (not on the title page used here).",
        "text": (
            "G. Rasch, Probabilistic Models for Some Intelligence and Attainment Tests. "
            "Danish Institute for Educational Research, 1960."
        ),
        "italic": ["Probabilistic Models for Some Intelligence and Attainment Tests"],
    },
    {
        "no": 7,
        "match": "A. Ghosh",
        "first": "Ghosh",
        "title": "Context-aware attentive Knowledge Tracing",
        "venue": "Proc. ACM SIGKDD Conf. Knowledge Discovery and Data Mining",
        "year": "2020",
        "doi": "10.1145/3394486.3403282",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "KDD 2020, pp. 2330-2339. Added doi.",
        "text": (
            "A. Ghosh, N. Heffernan, and A. S. Lan, “Context-aware attentive Knowledge "
            "Tracing,” in Proc. ACM SIGKDD Conf. Knowledge Discovery and Data Mining, "
            "2020, pp. 2330–2339. doi: 10.1145/3394486.3403282"
        ),
        "italic": [],
    },
    {
        "no": 8,
        "match": "H. Nakagawa",
        "first": "Nakagawa",
        "title": "Graph-based Knowledge Tracing: Modeling student proficiency using graph neural network",
        "venue": "IEEE/WIC/ACM International Conference on Web Intelligence",
        "year": "2019",
        "doi": "10.1145/3350546.3352513",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "WI 2019, pp. 156-163. Added doi.",
        "text": (
            "H. Nakagawa, Y. Iwasawa, and Y. Matsuo, “Graph-based Knowledge Tracing: "
            "Modeling student proficiency using graph neural network,” in Proc. "
            "IEEE/WIC/ACM International Conference on Web Intelligence, 2019, pp. "
            "156–163. doi: 10.1145/3350546.3352513"
        ),
        "italic": [],
    },
    {
        "no": 9,
        "match": "W. Lee",
        "first": "Lee",
        "title": "Contrastive learning for Knowledge Tracing",
        "venue": "Proc. ACM Web Conference",
        "year": "2022",
        "doi": "10.1145/3485447.3512105",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "WWW 2022, pp. 2330-2338. Last author S. Park (Sungrae Park), not D. Choi. Added doi.",
        "text": (
            "W. Lee, J. Chun, Y. Lee, K. Park, and S. Park, “Contrastive learning for "
            "Knowledge Tracing,” in Proc. ACM Web Conference, 2022, pp. 2330–2338. "
            "doi: 10.1145/3485447.3512105"
        ),
        "italic": [],
    },
    {
        "no": 10,
        "match": "R. Pelánek",
        "first": "Pelánek",
        "title": "Metrics for evaluation of student models",
        "venue": "Journal of Educational Data Mining",
        "year": "2015",
        "doi": "10.5281/zenodo.3554665",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "JEDM vol. 7, no. 2, pp. 1-19. Zenodo DOI. Added doi.",
        "text": (
            "R. Pelánek, “Metrics for evaluation of student models,” Journal of "
            "Educational Data Mining, vol. 7, no. 2, pp. 1–19, 2015. doi: "
            "10.5281/zenodo.3554665"
        ),
        "italic": ["Journal of Educational Data Mining"],
    },
    {
        "no": 11,
        "match": "C. Guo",
        "first": "Guo",
        "title": "On calibration of modern neural networks",
        "venue": "Proc. 34th International Conference on Machine Learning",
        "year": "2017",
        "doi": "",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "ICML 2017 = 34th; PMLR vol. 70, pp. 1321-1330 (proceedings.mlr.press/v70/guo17a). No Crossref DOI added.",
        "text": (
            "C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern "
            "neural networks,” in Proc. 34th International Conference on Machine "
            "Learning, vol. 70, 2017, pp. 1321–1330."
        ),
        "italic": [],
    },
    {
        "no": 12,
        "match": "M. P. Naeini",
        "first": "Naeini",
        "title": "Obtaining well calibrated probabilities using Bayesian binning",
        "venue": "Proc. AAAI Conference on Artificial Intelligence",
        "year": "2015",
        "doi": "10.1609/aaai.v29i1.9602",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "AAAI-15 vol. 29, no. 1. Print pages 2901-2907 appear in some reprints; not added (article-id is the publisher record). Added doi.",
        "text": (
            "M. P. Naeini, G. Cooper, and M. Hauskrecht, “Obtaining well calibrated "
            "probabilities using Bayesian binning,” in Proc. AAAI Conference on "
            "Artificial Intelligence, vol. 29, no. 1, 2015. doi: 10.1609/aaai.v29i1.9602"
        ),
        "italic": [],
    },
    {
        "no": 13,
        "match": "G. W. Brier",
        "first": "Brier",
        "title": "Verification of forecasts expressed in terms of probability",
        "venue": "Monthly Weather Review",
        "year": "1950",
        "doi": "10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "MWR vol. 78, no. 1, pp. 1-3. Official AMS DOI uses angle brackets; not rewritten.",
        "text": (
            "G. W. Brier, “Verification of forecasts expressed in terms of probability,” "
            "Monthly Weather Review, vol. 78, no. 1, pp. 1–3, 1950. doi: "
            "10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2"
        ),
        "italic": ["Monthly Weather Review"],
    },
    {
        "no": 14,
        "match": "M. H. DeGroot",
        "first": "DeGroot",
        "title": "The comparison and evaluation of forecasters",
        "venue": "The Statistician",
        "year": "1983",
        "doi": "10.2307/2987588",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "The Statistician vol. 32, no. 1/2, pp. 12-22 (JSTOR). Later retitled JRSS-D; 1983 venue kept. Added doi.",
        "text": (
            "M. H. DeGroot and S. E. Fienberg, “The comparison and evaluation of "
            "forecasters,” The Statistician, vol. 32, no. 1/2, pp. 12–22, 1983. doi: "
            "10.2307/2987588"
        ),
        "italic": ["The Statistician"],
    },
    {
        "no": 15,
        "match": "X. Yan",
        "first": "Yan",
        "title": "Recovering stranded discrimination in Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage",
        "venue": "arXiv:2606.14123",
        "year": "2026",
        "doi": "10.48550/arXiv.2606.14123",
        "status": "RETAIN_ARXIV",
        "correction": "YES",
        "notes": "GitHub/project pages claim ECML PKDD 2026 acceptance; no Springer LNCS volume, pages, or conference DOI found. Retain verified arXiv. Added arXiv doi only.",
        "text": (
            "X. Yan, C. Tang, and A. Shimada, “Recovering stranded discrimination in "
            "Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage,” "
            "arXiv:2606.14123, 2026. doi: 10.48550/arXiv.2606.14123"
        ),
        "italic": [],
    },
    {
        "no": 16,
        "match": "k-sparse",
        "first": "Huang",
        "title": "Towards robust Knowledge Tracing models via k-sparse attention",
        "venue": "Proc. 46th International ACM SIGIR Conference",
        "year": "2023",
        "doi": "10.1145/3539618.3592073",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "SIGIR 2023, pp. 2441-2445. X. Zhao = Xiangyu Zhao; J. Weng = Jian Weng. Added doi.",
        "text": (
            "S. Huang, Z. Liu, X. Zhao, W. Luo, and J. Weng, “Towards robust Knowledge "
            "Tracing models via k-sparse attention,” in Proc. 46th International ACM "
            "SIGIR Conference, 2023, pp. 2441–2445. doi: 10.1145/3539618.3592073"
        ),
        "italic": [],
    },
    {
        "no": 17,
        "match": "I. Bhattacharjee",
        "first": "Bhattacharjee",
        "title": "Cold start problem: An experimental study of Knowledge Tracing models with new students",
        "venue": "Artificial Intelligence in Education (AIED 2025), LNCS vol. 15880",
        "year": "2025",
        "doi": "10.1007/978-3-031-98459-4_30",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "Springer chapter DOI uses underscore _30 (not hyphen). LNCS 15880, pp. 425-432, AIED 2025 Part IV. Added doi in that form.",
        "text": (
            "I. Bhattacharjee and C. Wayllace, “Cold start problem: An experimental "
            "study of Knowledge Tracing models with new students,” in Artificial "
            "Intelligence in Education (AIED 2025), Lecture Notes in Computer Science, "
            "vol. 15880. Springer, 2025, pp. 425–432. doi: 10.1007/978-3-031-98459-4_30"
        ),
        "italic": ["Lecture Notes in Computer Science"],
    },
    {
        "no": 18,
        "match": "ASSISTmentsData",
        "first": "ASSISTmentsData",
        "title": "ASSISTments 2012–2013 school data with affect",
        "venue": "ASSISTments Public Datasets",
        "year": "2012",
        "doi": "",
        "status": "VERIFIED",
        "correction": "NO",
        "notes": "Official dump landing page used by pyKT. Live 2026-08-31. Feng et al. 2009 is the recommended paper cite for non-affect use; not substituted (would change [18]). URL required for this electronic record.",
        "text": (
            "ASSISTmentsData, “ASSISTments 2012–2013 school data with affect,” "
            "ASSISTments Public Datasets, 2012. [Online]. Available: "
            "https://sites.google.com/site/assistmentsdata/datasets/2012-13-school-data-with-affect"
        ),
        "italic": [],
    },
    {
        "no": 19,
        "match": "Junyi Academy",
        "first": "Junyi Academy",
        "title": "Junyi Academy online learning activity dataset",
        "venue": "Kaggle",
        "year": "2019",
        "doi": "",
        "status": "VERIFIED",
        "correction": "NO",
        "notes": "Official public dump. Kaggle record verified. URL required for this electronic record.",
        "text": (
            "Junyi Academy, “Junyi Academy online learning activity dataset,” Kaggle, "
            "2019. [Online]. Available: "
            "https://www.kaggle.com/datasets/junyiacademy/learning-activity-public-dataset-by-junyi-academy"
        ),
        "italic": [],
    },
    {
        "no": 20,
        "match": "XES3G5M",
        "first": "Liu",
        "title": "XES3G5M: A Knowledge Tracing benchmark dataset with auxiliary information",
        "venue": "37th Conference on Neural Information Processing Systems Datasets and Benchmarks Track",
        "year": "2023",
        "doi": "",
        "status": "VERIFIED_UPDATED",
        "correction": "YES",
        "notes": "NeurIPS 2023 D&B is the 37th conference (paper footer). Hash 67fc628f17c2ad53621fb961c6bafcaf. No Crossref DOI. Book vol. 36 not used (collides with 37th numbering). Q. Liu = Qiongqiong Liu; T. Guo corresponding.",
        "text": (
            "Z. Liu, Q. Liu, T. Guo, J. Chen, S. Huang, X. Zhao, J. Tang, W. Luo, and "
            "J. Weng, “XES3G5M: A Knowledge Tracing benchmark dataset with auxiliary "
            "information,” in Proc. 37th Conference on Neural Information Processing "
            "Systems Datasets and Benchmarks Track, 2023."
        ),
        "italic": [],
    },
]


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def para_text(para) -> str:
    return para.Range.Text.replace("\r", "").replace("\x07", "")


def italicize_phrases(para, phrases: list[str]) -> None:
    for phrase in phrases:
        rng = para.Range
        rng.MoveEnd(WD_CHARACTER, -1)
        found = rng.Find
        found.ClearFormatting()
        found.Text = phrase
        found.Forward = True
        found.Wrap = WD_FIND_STOP
        found.MatchCase = True
        if found.Execute():
            rng.Font.Italic = True


def neutralize_table_lists(doc) -> None:
    for ti in range(1, doc.Tables.Count + 1):
        tbl = doc.Tables(ti)
        for ri in range(1, tbl.Rows.Count + 1):
            for ci in range(1, tbl.Columns.Count + 1):
                cell = tbl.Cell(ri, ci)
                try:
                    cell.Range.ListFormat.RemoveNumbers()
                except Exception:
                    pass
                try:
                    cell.Range.Style = "Normal"
                except Exception:
                    pass
                try:
                    cell.Range.ParagraphFormat.OutlineLevel = 10
                except Exception:
                    pass
                cell.Range.Font.Name = "Times New Roman"
                cell.Range.Font.Size = 7


def restore_h1(doc, lines) -> None:
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
        if "RESULT AND DISCUSSION" in up or (up.startswith("IV.") and "RESULT" in up):
            target = "IV. RESULT"
        elif "DISCUSSION" in up and "RESULT" not in up:
            target = "V. DISCUSSION"
        elif "CONCLUSION" in up and "CONFLICT" not in up and "AUTHOR" not in up:
            target = "VI. CONCLUSION"
        if target and raw != target:
            try:
                doc.Paragraphs(i).Range.ListFormat.RemoveNumbers()
            except Exception:
                pass
            set_para_text(doc.Paragraphs(i), target)
            lines.append(f"H1_FIX {raw!r} -> {target}")


def write_csv() -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "RefNo",
                "FirstAuthor",
                "Title",
                "Venue",
                "Year",
                "DOI",
                "Status",
                "CorrectionNeeded",
                "Notes",
            ]
        )
        for r in REFS:
            w.writerow(
                [
                    r["no"],
                    r["first"],
                    r["title"],
                    r["venue"],
                    r["year"],
                    r["doi"],
                    r["status"],
                    r["correction"],
                    r["notes"],
                ]
            )


def main() -> None:
    if not STEP13.exists():
        raise SystemExit(f"Missing {STEP13}")
    shutil.copy2(STEP13, STEP14_DOCX)
    write_csv()

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    lines = [f"CSV={CSV_PATH.exists()}"]
    try:
        doc = word.Documents.Open(str(STEP14_DOCX))
        applied = []
        for i in range(1, doc.Paragraphs.Count + 1):
            try:
                style = str(doc.Paragraphs(i).Style.NameLocal)
            except Exception:
                continue
            if style != "References":
                continue
            raw = para_text(doc.Paragraphs(i))
            for r in REFS:
                if r["match"] in raw:
                    set_para_text(doc.Paragraphs(i), r["text"])
                    try:
                        doc.Paragraphs(i).Style = "References"
                    except Exception:
                        pass
                    italicize_phrases(doc.Paragraphs(i), r["italic"])
                    applied.append(r["no"])
                    break
        lines.append(f"APPLIED={applied}")
        if sorted(applied) != list(range(1, 21)):
            raise RuntimeError(f"expected refs 1-20, got {applied}")

        restore_h1(doc, lines)
        neutralize_table_lists(doc)

        full = doc.Content.Text
        checks = {
            "pykt_36": "Proc. 36th Conference on Neural Information Processing Systems Datasets"
            in full,
            "no_pykt_37": "Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2022"
            not in full,
            "xes_37": "Proc. 37th Conference on Neural Information Processing Systems Datasets"
            in full,
            "park": "and S. Park" in full,
            "bhat_doi": "10.1007/978-3-031-98459-4_30" in full,
            "yan_arxiv": "arXiv:2606.14123" in full,
            "no_yan_ecml": "ECML" not in full,
            "assist_url": "assistmentsdata/datasets/2012-13-school-data-with-affect"
            in full,
            "junyi_kaggle": "junyiacademy/learning-activity-public-dataset-by-junyi-academy"
            in full,
            "guo_vol": "vol. 70, 2017, pp. 1321–1330" in full,
            "piech_vol": "vol. 28, 2015, pp. 505–513" in full,
            "corbett_doi": "doi: 10.1007/BF01099821" in full,
            "end_matter": "Conflict of Interest" in full,
            "auc_untouched": "0.6979±0.0014" in full,
            "ece_untouched": "0.1136±0.0066" in full,
        }
        for k, v in checks.items():
            lines.append(f"{k}={v}")
        missing = [k for k, v in checks.items() if not v]
        if missing:
            raise RuntimeError(f"failed checks: {missing}")

        pages = doc.ComputeStatistics(2)
        words = doc.ComputeStatistics(0)
        lines.append(
            f"PAGES={pages} WORDS={words} TABLES={doc.Tables.Count} "
            f"PICS={doc.InlineShapes.Count}"
        )
        if doc.InlineShapes.Count != 1:
            raise RuntimeError(f"expected 1 figure, got {doc.InlineShapes.Count}")
        if doc.Tables.Count < 8:
            raise RuntimeError(f"expected >=8 tables, got {doc.Tables.Count}")

        OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
        if OUT_PDF.exists():
            OUT_PDF.unlink()
        doc.SaveAs2(str(STEP14_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(STEP14_DOC), WD_FORMAT_DOC)
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
