#!/usr/bin/env python3
"""Fill the official IJIET 2026 Word template with the validated manuscript.

Template source: https://www.ijiet.org/files/IJIET_template.doc
(downloaded 2026-08-31; OLE .doc, A4, Title 20 pt, Heading 1 = I. II. III.)

Does not overwrite paper/, REV_REVIEWER_CALIBRATION_v1/, or ijiet/*.tex.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DOC = ROOT / "IJIET_SUBMISSION" / "audit" / "IJIET_template.doc"
FIG = ROOT / "IJIET_SUBMISSION" / "figures" / "figure2_bucket_distribution.png"
OUT_STEM = "Reproducible_Sparse_Concept_and_Calibration_Diagnostics_for_Knowledge_Tracing"
OUT_DOCX = ROOT / "ijiet" / f"{OUT_STEM}.docx"
OUT_DOC = ROOT / "ijiet" / f"{OUT_STEM}.doc"
COPY_DOCX = ROOT / "IJIET_SUBMISSION" / "output" / f"{OUT_STEM}.docx"

WD_CHARACTER = 1
WD_FORMAT_XML = 16
WD_FORMAT_DOC = 0
WD_COLLAPSE_START = 1
WD_ALIGN_CENTER = 1
WD_ALIGN_JUSTIFY = 3
WD_LINE_EXACTLY = 4
WD_SAVE_CHANGES = -1

TITLE = (
    "Reproducible Sparse-Concept and Calibration Diagnostics "
    "for Knowledge Tracing"
)

ABSTRACT = (
    "Knowledge Tracing (KT) systems that drive practice, remediation, or advancement "
    "typically consume a predicted probability, not an area-under-the-curve (AUC) score. "
    "Aggregate ranking metrics can look acceptable while those probabilities are poorly "
    "calibrated on rarely practiced skills. This paper reports a diagnostic evaluation—not "
    "a new KT architecture—of how calibration behaves across train-only knowledge-component "
    "(KC) frequency strata on three public logs (ASSISTments 2012, Junyi Academy, and "
    "XES3G5M) with IRT, DKT, and SimpleKT. Sparse training evidence does not universally "
    "reduce discrimination. It can, however, expose a dataset-dependent calibration "
    "vulnerability. On ASSISTments 2012, SimpleKT expected calibration error (ECE) rises "
    "from 0.114 on dense KCs to 0.228 on sparse KCs (Limited occupancy, N=415); Junyi has "
    "no learner-based sparse stratum, and XES3G5M SimpleKT ECE is essentially flat. "
    "Treating the same probabilities as a locked global mastery gate at τ=0.7 raises "
    "SimpleKT false mastery among advances from 0.196 (dense) to 0.268 (sparse) on one "
    "ASSISTments fold; the sparse–dense gap stays positive on all five training seeds "
    "(mean 0.047; four unique student partitions). A train-only graph KT instantiation "
    "shrinks that seed-42 gap. The gate is a simulation, not a classroom trial. The "
    "practical implication for educational-technology designers is to validate thresholded "
    "decisions per frequency stratum rather than on population AUC or ECE alone."
)

KEYWORDS = (
    "knowledge tracing, learning analytics, calibration, sparse concepts, "
    "mastery threshold, educational decision support"
)

INTRO = [
    "Adaptive practice engines and intelligent tutoring systems increasingly use Knowledge Tracing (KT) to estimate whether a learner has mastered a skill and to decide whether to skip, remediate, or advance [1]–[3]. In deployment, that decision is rarely the AUC of a leaderboard. It is a probability p compared with a threshold τ: if p is high enough, the system treats the skill as mastered and withholds extra help.",
    "KT papers typically report population AUC and accuracy [4], [5]. Those metrics are useful for ranking models, but they can hide reliability problems on low-frequency knowledge components (KCs)—concepts with little training-fold evidence—because most test events sit on dense, frequently practiced skills. A model can rank well overall and still be overconfident on the sparse tail. When p is used as a mastery or remediation gate, that overconfidence is not a cosmetic reporting issue: it is a false-mastery error.",
    "This paper treats that mismatch as an evaluation problem for educational technology, not as a reason to propose another KT backbone. We ask three questions that a system designer can act on: (1) Does lower KC training frequency systematically worsen ranking (AUC) across datasets? (2) Does it worsen probability reliability (calibration), and is that pattern dataset-dependent? (3) If a global threshold is applied to p, does the sparse stratum produce a dirtier advance decision than the dense stratum?",
    "The empirical story is bounded. Sparse training evidence does not universally degrade discrimination. On XES3G5M, sparse AUC is higher than dense AUC for DKT and SimpleKT. Calibration, however, can be more sensitive than aggregate ranking on some logs. On ASSISTments 2012, SimpleKT ECE increases from dense to sparse concepts, and a locked gate at τ=0.7 produces a higher false-mastery rate among sparse advances. The same ECE gradient is absent on Junyi (empty sparse bucket) and essentially absent for SimpleKT on XES3G5M. We therefore do not claim that “sparse KCs always fail.” We claim that occupancy-aware, stratum-wise calibration—and, when probabilities are consumed as gates, a simulated decision error—should be checked before a KT model is wired into remediation logic.",
    "Contributions, stated conservatively: (i) a train-only KC-frequency protocol with an explicit strict cold-start group, so sparse diagnostics cannot leak test-fold counts into the definition of “sparse”; (ii) per-stratum calibration (ECE, Brier decomposition) on three public datasets, with sample-size flags (Reliable / Limited / Insufficient); (iii) a locked-threshold simulation of false mastery and miss rates, plus a five-seed check of the sparse–dense false-mastery gap on ASSISTments 2012. We do not claim a new audit theory, a new calibrator, or a classroom RCT. Graph KT (GKT) and a CL4KT-style adapter appear only as a single-fold diagnostic instantiation on ASSISTments, not as a model-contribution bake-off.",
]

LIT = [
    "Classical KT uses Bayesian knowledge tracing or item-response models [1], [6]. Deep sequential models (DKT, attentive and transformer KT) improved aggregate prediction [2], [4], [7]. Graph and contrastive variants often motivate architecture by sparse or related skills [8], [9]. Those papers still report mainly population metrics.",
    "Educational measurement has long warned that ranking is not reliability [10]. Calibration error and reliability diagrams quantify whether predicted probabilities match empirical correctness [11]–[14]. Recent KT work has begun to study calibration and sparse-concept evaluation [15]–[17], but deployed tutoring systems still typically consume a single global p. This study sits in that gap: we keep standard models, stratify by training-only frequency, and ask whether a population gate would treat sparse skills more leniently—or more dangerously—than dense ones.",
]

METHODS_A = [
    "We use three de-identified public logs after a common schema: ASSISTments 2012 [18], [5], Junyi Academy [19], and XES3G5M [20]. Table 1 summarizes processed cohort size. Learner-based splits (unseen students) are the primary setting. Temporal splits are a complementary stress test and are not the source of the gate numbers below.",
]
METHODS_A2 = [
    "Baselines: one-parameter IRT [6] as a classical reference, DKT [2], and SimpleKT [4]. On ASSISTments fold 0 only we also score a train-only GKT graph [8] and a CL4KT protocol adapter [9] (contrastive views on training sequences; not an official CL4KT checkpoint). IRT under learner-based splits has no ability parameter for unseen students, so its AUC is 0.50 by construction; we report it as a base-rate reference, not as a ranking competitor.",
    "Deep models are trained at seeds 42, 2024, 2025, 2026, and 2027. The processed partitions for seeds 2025 and 2026 are identical (fold_2 = fold_3) on all three datasets. Tables that report mean±sd therefore summarize four unique student partitions: the two initializations on the duplicated split are averaged first. The gate-robustness table still lists all five training seeds without dropping one after the fact.",
]
METHODS_B = [
    "For each fold, KC frequency f_train is counted on the training file only. Buckets: strict cold-start (f=0), very sparse (0<f<20), sparse (20≤f<100), medium (100≤f<500), dense (f≥500). Dense KCs dominate event volume while a non-empty sparse-like tail exists on ASSISTments and XES3G5M. Occupancy flags follow test-event count N: Reliable (N≥1000), Limited (100≤N<1000), Insufficient (N<100). Success claims require Limited or Reliable occupancy. Very-sparse ASSISTments cells are Insufficient and descriptive only.",
]
METHODS_C = [
    "Let y∈{0,1} be correctness and p∈[0,1] the predicted probability. With M=15 equal-width bins, ECE = Σ_m (n_m / N) |acc_m − conf_m|. We also report the Brier score and its reliability / resolution / uncertainty decomposition [14]. Lower ECE is better calibration; it is not a substitute for AUC.",
]
METHODS_D = [
    "For a locked global threshold τ, the system advances (skips remediation) if p≥τ and triggers remediation otherwise. Sparse events never receive their own tuned τ. The display threshold is τ=0.7; the grid {0.5, 0.6, 0.7, 0.8} is recorded in the artifact and is not a search over sparse error.",
    "Let A={p≥τ}. False mastery (FM) is P(y=0 | A): among advances, how often was the answer wrong. Miss is P(A | y=0): among wrong answers, how often the system still skipped help. If the model were calibrated on the advance set, FM would match E[1−p | A]. We report ΔFM = FM_sparse − FM_dense. Positive ΔFM means sparse advances are dirtier than dense advances. This is a simulated decision error, not an instructional RCT.",
]

RESULTS = [
    "Table 2 shows learner-based AUC. DKT is slightly above SimpleKT on all three datasets. IRT AUC is 0.50 for the reason given above. These numbers would look like a routine KT bake-off. They do not tell a designer whether p is trustworthy on the tail.",
]
RESULTS_2 = [
    "On XES3G5M, sparse AUC is higher than dense AUC (DKT 0.857 vs. 0.817; SimpleKT 0.847 vs. 0.755; Reliable occupancy). Lower frequency is therefore not a universal ranking failure. Junyi’s learner-based sparse bucket is empty under the pre-registered cuts—a protocol outcome, not a missing cell to impute.",
]
RESULTS_B = [
    "Table 3 is the calibration punchline. On ASSISTments 2012, SimpleKT ECE increases from 0.1136±0.0066 (dense, Reliable, N=523,971) to 0.1541 (medium) to 0.2280±0.0197 (sparse, Limited, N=415). DKT shows the same direction (dense ECE 0.060 vs. sparse 0.233). IRT dense ECE is tiny (0.003) but resolution is zero: a constant-like predictor can look “calibrated” while ranking nothing.",
    "On Junyi, only dense and medium strata exist; SimpleKT ECE rises modestly from 0.079 to 0.107. On XES3G5M, SimpleKT ECE is essentially flat (0.114→0.111→0.125 dense/medium/sparse) despite Reliable sparse occupancy (N=2,010). ECE-flat is not a license to skip occupancy reporting, and—as the gate results show—it is not the same as a flat miss rate.",
]
RESULTS_C = [
    "Table 4 applies τ=0.7 on ASSISTments fold 0 (seed 42; sparse N=444, Limited). SimpleKT false mastery among advances is 0.196 on dense KCs and 0.268 on sparse KCs (ΔFM=+0.072). The calibrated expectation E[FM] on sparse advances is only 0.050, so the excess error is large. DKT shows a similar FM gap. Train-only GKT shrinks ΔFM to +0.015 (FM 0.205→0.220). The CL4KT adapter is intermediate (0.185→0.240). We do not read this as “use GKT in production”; we read it as: the ASSISTments calibration gradient is not a property of the dataset alone.",
]
RESULTS_C2 = [
    "Table 5 checks whether SimpleKT ΔFM is a one-fold accident. It is positive on all five training seeds (mean 0.047, sd 0.033). A KC-clustered bootstrap on seed 42 yields a 95% interval [0.006, 0.138]—excluding 0, but wide, as Limited occupancy requires. DKT ΔFM is positive on only three of five seeds and is not treated as a five-run finding. On XES3G5M, SimpleKT ΔFM is negative on all five seeds, but ΔMiss is positive on all five (mean +0.112): among actual incorrect answers, the system still advances more often on sparse than on dense KCs. A flat ECE therefore does not imply a flat miss rate.",
    "Coincidence of digits: SimpleKT dense E[FM] at τ=0.7 on seed 42 is 0.113, close to the four-partition dense ECE 0.114. They are different quantities.",
]
DISC_A = [
    "If a learning platform uses KT probabilities only to sort students, Table 2 may suffice. If it uses p to skip practice or declare mastery, Table 2 is the wrong dashboard. The ASSISTments SimpleKT cell is the cautionary case: competitive AUC, Limited-but-estimable sparse occupancy (about 19% of KCs fall below the sparse threshold on fold 0), a monotonic ECE rise, and a gate that advances more dirty sparse attempts. The XES3G5M cell is the opposite caution: plenty of sparse mass and Reliable occupancy, yet SimpleKT ECE does not degrade—while miss rates still can. Junyi shows that the protocol can refuse a sparse claim when the bucket is empty.",
    "Three observable conditions track when sparse-calibration claims are informative rather than obligatory (Table 6): (1) a non-empty low-frequency tail under the split actually used; (2) enough sparse test events for at least a Limited-flag ECE; (3) frequency–difficulty coupling that is not inverted. ASSISTments meets all three. That is a diagnostic pre-condition, not a claim that training frequency causes miscalibration.",
]
DISC_B = [
    "The gate is not a classroom policy and not an A/B test of remediation. GKT and the CL4KT adapter are single-fold, ASSISTments-only instantiations. Temporal results are a single corrected cutoff (seed 42), not a multi-cutoff variance estimate. IRT is not a fair ranking baseline on unseen learners. We did not tune τ on sparse events, and we do not recommend doing so in deployment without a separate validation design.",
]
DISC_C = [
    "IJIET’s audience includes operators of educational platforms, not only KT researchers. For that audience, the operational recommendation is narrow: (i) log train-only KC frequency with every prediction; (ii) report ECE and occupancy on dense vs. sparse slices before enabling a global mastery threshold; (iii) if a threshold must be global, simulate FM and Miss on the sparse slice at the same τ used in the product; (iv) do not treat a population AUC win, or a graph/contrastive architecture, as automatically safer on the tail.",
]
CONCLUSION = [
    "KT models that look adequate on AUC can still be poorly calibrated on rarely practiced skills, and a global mastery threshold can then produce a higher false-mastery rate on those skills. That pattern appears for SimpleKT on ASSISTments 2012 (ECE 0.114→0.228, Limited N=415; seed-42 FM 0.196→0.268; ΔFM>0 on 5/5 seeds). It does not appear as a universal law: Junyi has no learner-based sparse stratum, and XES3G5M SimpleKT ECE is flat. Sparse-concept diagnostics are therefore conditionally important. The simulation is a decision-error check for educational-technology systems, not a claim of a new KT model and not a classroom intervention.",
]

REFS = [
    'S. Chen, B. Mulgrew, and P. M. Grant, “A clustering technique for digital communications channel equalization using radial basis function networks,” IEEE Trans. Neural Networks, vol. 4, pp. 570–578, July 1993.',  # placeholder overwritten
]
# Real references (IEEE numbered; first-appearance order from the IJIET draft).
REFS = [
    "A. T. Corbett and J. R. Anderson, “Knowledge Tracing: Modeling the acquisition of procedural knowledge,” User Modeling and User-Adapted Interaction, vol. 4, no. 4, pp. 253–278, 1994.",
    "C. Piech, J. Bassen, J. Huang, S. Ganguli, M. Sahami, L. J. Guibas, and J. Sohl-Dickstein, “Deep Knowledge Tracing,” in Advances in Neural Information Processing Systems, 2015, pp. 505–513.",
    "G. Abdelrahman, Q. Wang, and B. Nunes, “Knowledge Tracing: A survey,” ACM Computing Surveys, vol. 55, no. 11, pp. 1–37, 2023.",
    "Z. Liu, Q. Liu, J. Chen, S. Huang, and W. Luo, “SimpleKT: A simple but tough-to-beat baseline for Knowledge Tracing,” in The Eleventh International Conference on Learning Representations, 2023.",
    "Z. Liu, Q. Liu, J. Chen, S. Huang, J. Tang, and W. Luo, “pyKT: A python library to benchmark deep learning based Knowledge Tracing models,” in Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2022.",
    "G. Rasch, Probabilistic Models for Some Intelligence and Attainment Tests. Danish Institute for Educational Research, 1960.",
    "A. Ghosh, N. Heffernan, and A. S. Lan, “Context-aware attentive Knowledge Tracing,” in Proc. ACM SIGKDD Conf. Knowledge Discovery and Data Mining, 2020, pp. 2330–2339.",
    "H. Nakagawa, Y. Iwasawa, and Y. Matsuo, “Graph-based Knowledge Tracing: Modeling student proficiency using graph neural network,” in IEEE/WIC/ACM International Conference on Web Intelligence, 2019, pp. 156–163.",
    "W. Lee, J. Chun, Y. Lee, K. Park, and D. Choi, “Contrastive learning for Knowledge Tracing,” in Proc. ACM Web Conference, 2022, pp. 2330–2338.",
    "R. Pelánek, “Metrics for evaluation of student models,” Journal of Educational Data Mining, vol. 7, no. 2, pp. 1–19, 2015.",
    "C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, “On calibration of modern neural networks,” in Proc. International Conference on Machine Learning, 2017, pp. 1321–1330.",
    "M. P. Naeini, G. Cooper, and M. Hauskrecht, “Obtaining well calibrated probabilities using Bayesian binning,” in Proc. AAAI Conference on Artificial Intelligence, vol. 29, no. 1, 2015.",
    "G. W. Brier, “Verification of forecasts expressed in terms of probability,” Monthly Weather Review, vol. 78, no. 1, pp. 1–3, 1950.",
    "M. H. DeGroot and S. E. Fienberg, “The comparison and evaluation of forecasters,” The Statistician, vol. 32, no. 1/2, pp. 12–22, 1983.",
    "X. Yan, C. Tang, and A. Shimada, “Recovering stranded discrimination in Knowledge Tracing: Per-item bias correction via empirical-Bayes shrinkage,” arXiv:2606.14123, 2026.",
    "S. Huang, Z. Liu, X. Zhao, W. Luo, and J. Weng, “Towards robust Knowledge Tracing models via k-sparse attention,” in Proc. 46th International ACM SIGIR Conference, 2023, pp. 2441–2445.",
    "I. Bhattacharjee and C. Wayllace, “Cold start problem: An experimental study of Knowledge Tracing models with new students,” in Artificial Intelligence in Education (AIED 2025), LNCS vol. 15880, Springer, 2025, pp. 425–432.",
    "ASSISTmentsData, “ASSISTments 2012–2013 school data with affect,” ASSISTments Public Datasets, 2012. [Online]. Available: https://sites.google.com/site/assistmentsdata/datasets/2012-13-school-data-with-affect",
    "Junyi Academy, “Junyi Academy online learning activity dataset,” Kaggle, 2019. [Online]. Available: https://www.kaggle.com/datasets/junyiacademy/learning-activity-public-dataset-by-junyi-academy",
    "Z. Liu, Q. Liu, T. Guo, J. Chen, S. Huang, X. Zhao, J. Tang, W. Luo, and J. Weng, “XES3G5M: A Knowledge Tracing benchmark dataset with auxiliary information,” in Thirty-seventh Conference on Neural Information Processing Systems Datasets and Benchmarks Track, 2023.",
]


def set_para_text(para, text: str) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    rng.Text = text


def find_para_index(doc, needle: str) -> int:
    n = doc.Paragraphs.Count
    for i in range(1, n + 1):
        if needle in doc.Paragraphs(i).Range.Text:
            return i
    raise RuntimeError(f"Paragraph not found: {needle!r}")


def insert_before_index(doc, index: int, text: str, style: str):
    doc.Paragraphs(index).Range.InsertParagraphBefore()
    p = doc.Paragraphs(index)
    try:
        p.Style = style
    except Exception:
        p.Style = "Text"
    set_para_text(p, text)
    return p


def add_table(doc, index: int, header, rows, caption: str, caption_style="Table Title"):
    insert_before_index(doc, index, caption, caption_style)
    # table goes after caption, i.e. before original index+1
    rng = doc.Paragraphs(index + 1).Range
    rng.Collapse(WD_COLLAPSE_START)
    table = doc.Tables.Add(rng, len(rows) + 1, len(header))
    table.Style = "Table Grid"
    for j, h in enumerate(header, 1):
        table.Cell(1, j).Range.Text = h
        table.Cell(1, j).Range.Font.Bold = True
        table.Cell(1, j).Range.Font.Size = 8
        table.Cell(1, j).Range.Font.Name = "Times New Roman"
        table.Cell(1, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    for i, row in enumerate(rows, 2):
        for j, val in enumerate(row, 1):
            table.Cell(i, j).Range.Text = str(val)
            table.Cell(i, j).Range.Font.Bold = False
            table.Cell(i, j).Range.Font.Size = 8
            table.Cell(i, j).Range.Font.Name = "Times New Roman"
            table.Cell(i, j).Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    try:
        table.AutoFitBehavior(2)  # wdAutoFitWindow
    except Exception:
        pass
    return table


def superscript_author_numbers(para) -> None:
    rng = para.Range
    rng.MoveEnd(WD_CHARACTER, -1)
    text = rng.Text
    for i, ch in enumerate(text):
        if ch in "12" and (i == 0 or not text[i - 1].isdigit()):
            r = para.Range
            r.Start = para.Range.Start + i
            r.End = r.Start + 1
            r.Font.Superscript = True


def fill(doc) -> None:
    set_para_text(doc.Paragraphs(1), TITLE)
    doc.Paragraphs(1).Range.Font.Size = 20
    doc.Paragraphs(1).Range.Font.Name = "Times New Roman"
    doc.Paragraphs(1).Range.Font.Bold = True

    authors = (
        "Khanh-Trinh Nguyen1, Tuan Dao Minh1, Duong Nguyen Tien1, "
        "Chi Thanh Nguyen2, and Van-Hau Nguyen1,*"
    )
    set_para_text(doc.Paragraphs(2), authors)
    superscript_author_numbers(doc.Paragraphs(2))

    set_para_text(
        doc.Paragraphs(3),
        "1 Hung Yen University of Technology and Education, Hung Yen, Vietnam",
    )
    set_para_text(
        doc.Paragraphs(4),
        "2 Academy of Military Science and Technology, Ha Noi, Vietnam",
    )
    set_para_text(
        doc.Paragraphs(5),
        "Email: trinhnk@utehy.edu.vn (K.-T.N.); tuanymc@utehy.edu.vn (T.D.M.); "
        "duongnt@utehy.edu.vn (D.N.T.); thanhnc@ioit.ai.vn (C.T.N.); "
        "haunv@utehy.edu.vn (V.-H.N.)",
    )
    set_para_text(doc.Paragraphs(6), "*Corresponding author")
    set_para_text(
        doc.Paragraphs(7),
        "Manuscript received Month date, 2026; revised Month date, 2026; "
        "accepted Month date, 2026",
    )

    abs_i = find_para_index(doc, "Abstract")
    set_para_text(doc.Paragraphs(abs_i), "Abstract—" + ABSTRACT)
    kw_i = find_para_index(doc, "Keywords")
    set_para_text(doc.Paragraphs(kw_i), "Keywords—" + KEYWORDS)

    intro_i = find_para_index(doc, "Introduction")
    copy_i = find_para_index(doc, "Copyright")
    if copy_i <= intro_i:
        raise RuntimeError("Unexpected template order")
    start = doc.Paragraphs(intro_i).Range.Start
    end = doc.Paragraphs(copy_i).Range.Start
    doc.Range(start, end).Delete()

    # Insertion point is now the Copyright paragraph.
    def cursor() -> int:
        return find_para_index(doc, "Copyright")

    def h1(text: str) -> None:
        insert_before_index(doc, cursor(), text, "Heading 1")

    def h2(text: str) -> None:
        insert_before_index(doc, cursor(), text, "Heading 2")

    def body(texts) -> None:
        for t in texts:
            insert_before_index(doc, cursor(), t, "Text")

    def refhead(text: str) -> None:
        insert_before_index(doc, cursor(), text, "Reference Head")

    def figcap(text: str) -> None:
        insert_before_index(doc, cursor(), text, "figure caption")

    h1("Introduction")
    body(INTRO)

    h1("Literature Review")
    body(LIT)

    h1("Materials and Methods")
    h2("Datasets, Splits, and Models")
    body(METHODS_A)
    add_table(
        doc,
        cursor(),
        ["Dataset", "Learners", "KCs", "Interactions", "Test events"],
        [
            ["ASSISTments 2012", "27,806", "265", "2.66M", "534,150"],
            ["Junyi Academy", "71,014", "1,326", "16.2M", "3,269,022"],
            ["XES3G5M", "18,066", "866", "7.95M", "1,589,145"],
        ],
        "Table 1. Processed cohort statistics (learner-based split)",
    )
    body(METHODS_A2)

    h2("Train-Only Frequency Strata")
    body(METHODS_B)
    if FIG.exists():
        rng = doc.Paragraphs(cursor()).Range
        rng.Collapse(WD_COLLAPSE_START)
        pic = rng.InlineShapes.AddPicture(str(FIG))
        try:
            pic.Width = 240  # points, ~column width
        except Exception:
            pass
        figcap(
            "Fig. 1. Train-only KC-frequency strata. Dense concepts dominate "
            "interactions; sparse and cold-start KCs remain the diagnostic tail."
        )

    h2("Calibration")
    body(METHODS_C)
    h2("Simulated Mastery Gate")
    body(METHODS_D)

    h1("Result and Discussion")
    h2("Aggregate Ranking Is Not the Sparse Story")
    body(RESULTS)
    add_table(
        doc,
        cursor(),
        ["Dataset", "Model", "AUC", "ACC"],
        [
            ["ASSISTments 2012", "IRT", "0.5000", "0.6973±0.0004"],
            ["ASSISTments 2012", "DKT", "0.6979±0.0014", "0.7182±0.0014"],
            ["ASSISTments 2012", "SimpleKT", "0.6837±0.0025", "0.6996±0.0032"],
            ["Junyi Academy", "IRT", "0.5000", "0.7053±0.0018"],
            ["Junyi Academy", "DKT", "0.7320±0.0009", "0.7343±0.0015"],
            ["Junyi Academy", "SimpleKT", "0.7231±0.0030", "0.7274±0.0015"],
            ["XES3G5M", "IRT", "0.5000", "0.7961±0.0031"],
            ["XES3G5M", "DKT", "0.8171±0.0022", "0.8327±0.0032"],
            ["XES3G5M", "SimpleKT", "0.7557±0.0013", "0.8067±0.0037"],
        ],
        "Table 2. Overall learner-based AUC (mean±sd over four unique partitions)",
    )
    body(RESULTS_2)

    h2("Calibration Can Move When Ranking Does Not")
    body(RESULTS_B)
    add_table(
        doc,
        cursor(),
        ["Dataset", "Stratum", "N", "Flag", "ECE"],
        [
            ["ASSISTments 2012", "dense", "523,971", "R", "0.1136±0.0066"],
            ["ASSISTments 2012", "medium", "5,963", "R", "0.1541±0.0051"],
            ["ASSISTments 2012", "sparse", "415", "L", "0.2280±0.0197"],
            ["Junyi Academy", "dense", "3,232,614", "R", "0.0792±0.0051"],
            ["Junyi Academy", "medium", "3,836", "R", "0.1073±0.0156"],
            ["XES3G5M", "dense", "1,268,696", "R", "0.1145±0.0011"],
            ["XES3G5M", "medium", "12,980", "R", "0.1114±0.0076"],
            ["XES3G5M", "sparse", "2,010", "R", "0.1248±0.0085"],
        ],
        "Table 3. SimpleKT event-level ECE by train-only frequency stratum (four unique partitions). Flags: R Reliable, L Limited. Junyi sparse is empty.",
    )

    h2("A Global Gate Can Turn the ASSISTments Gradient into a Decision Error")
    body(RESULTS_C)
    add_table(
        doc,
        cursor(),
        ["Model", "Stratum", "N", "FM", "E[FM]", "Miss"],
        [
            ["SimpleKT", "dense", "528,018", "0.196", "0.113", "0.352"],
            ["SimpleKT", "sparse", "444", "0.268", "0.050", "0.320"],
            ["DKT", "dense", "528,018", "0.200", "0.147", "0.398"],
            ["DKT", "sparse", "444", "0.296", "0.057", "0.365"],
            ["GKT (train-only)", "dense", "528,018", "0.205", "0.163", "0.455"],
            ["GKT (train-only)", "sparse", "444", "0.220", "0.157", "0.234"],
            ["CL4KT (adapter)", "dense", "528,018", "0.185", "0.175", "0.359"],
            ["CL4KT (adapter)", "sparse", "444", "0.240", "0.116", "0.244"],
        ],
        "Table 4. Simulated gate at τ=0.7, ASSISTments 2012 fold 0. Advance if p≥τ. Not a classroom trial.",
    )
    body(RESULTS_C2)
    add_table(
        doc,
        cursor(),
        ["Model", "Mean ΔFM", "SD", "Seeds >0", "Mean sparse N"],
        [
            ["SimpleKT", "0.047", "0.033", "5/5", "413"],
            ["DKT", "0.033", "0.048", "3/5", "413"],
        ],
        "Table 5. Gate robustness at τ=0.7 on ASSISTments 2012 (five training seeds; four unique partitions). GKT/CL4KT remain seed 42 only.",
    )

    h2("What a Designer Should Take Away")
    body(DISC_A)
    add_table(
        doc,
        cursor(),
        ["Condition", "ASSISTments", "Junyi", "XES3G5M"],
        [
            ["Sparse mass", "18.9% of KCs", "0%", "22.5% of KCs"],
            ["Sparse N", "415 (L)", "empty", "2,010 (R)"],
            ["Difficulty coupling", "ρ=−0.227 (sparse harder)", "ρ=−0.416", "ρ=+0.087 (weak, inverted)"],
            ["SimpleKT ECE", "0.114→0.228", "dense→medium only", "flat 0.114→0.125"],
        ],
        "Table 6. When a sparse-calibration claim is estimable (findings, not causes). Sparse mass: share of KCs with f_train<100.",
    )
    h2("What This Paper Does Not Show")
    body(DISC_B)
    h2("Implications for Information and Education Technology")
    body(DISC_C)

    h1("Conclusion")
    body(CONCLUSION)

    refhead("Conflict of Interest")
    body(["The authors declare no conflict of interest."])
    refhead("Author Contributions")
    body(
        [
            "K.-T.N. led the diagnostic design, experiments, and manuscript. T.D.M. and D.N.T. contributed data processing and baseline runs. C.T.N. contributed methodological review. V.-H.N. supervised the study and revised the manuscript. All authors approved the final version.",
        ]
    )
    refhead("Acknowledgment")
    body(
        [
            "Anonymized code and prediction exports are available for peer review; a public repository will be released upon acceptance. This study uses de-identified public learner logs (ASSISTments 2012, Junyi Academy, XES3G5M) and is not a classroom trial.",
        ]
    )
    refhead("References")
    for r in REFS:
        insert_before_index(doc, cursor(), r, "References")


def main() -> None:
    if not TEMPLATE_DOC.exists():
        raise SystemExit(f"Missing template: {TEMPLATE_DOC}")
    OUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    COPY_DOCX.parent.mkdir(parents=True, exist_ok=True)

    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = None
    try:
        doc = word.Documents.Open(str(TEMPLATE_DOC))
        fill(doc)
        # Update fields (page numbers, heading lists)
        doc.Fields.Update()
        doc.SaveAs2(str(OUT_DOCX), WD_FORMAT_XML)
        doc.SaveAs2(str(OUT_DOC), WD_FORMAT_DOC)
        pages = doc.ComputeStatistics(2)
        paras = doc.Paragraphs.Count
        print(f"pages={pages} paras={paras}")
        print(f"Wrote {OUT_DOCX}")
        print(f"Wrote {OUT_DOC}")
    finally:
        if doc is not None:
            doc.Close(WD_SAVE_CHANGES)
        word.Quit()
    shutil.copy2(OUT_DOCX, COPY_DOCX)
    print(f"Copied {COPY_DOCX}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
