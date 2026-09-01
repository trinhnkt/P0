# IJIET venue requirements (inspected 2026-08-31)

Official pages (current site, not the unrelated `ijiet.com` aggregator):

- Home: https://www.ijiet.org/
- Submission: https://www.ijiet.org/list-14-1.html
- Scope: https://www.ijiet.org/list-15-1.html
- FAQs: https://www.ijiet.org/list-22-1.html
- Ethics / AI: https://www.ijiet.org/list-77-1.html
- Template (authoritative): https://www.ijiet.org/files/IJIET_template.doc
- OJS: https://ojs.ejournal.net/index.php/ijiet/submissions

## Submission

- Full papers only (not abstracts).
- Upload `.doc` or `.pdf` via OJS.
- Embed figures and tables in the manuscript file.
- Must follow the **Template Paper**. FAQ Q3: papers obviously not matching the template will not be considered.
- Original, unpublished, **not under consideration elsewhere**.
- APC USD 500 after acceptance (Scopus; not SCI).
- Double-blind review is described on the ethics page; published articles show named authors. Follow the template for whether the review copy is anonymized.

## Scope (must match)

In-scope topics that fit this work: learning analytics; evaluation systems; educational technology measurement and evaluation; computer-based training; impact of technology use.

Out of scope: systematic reviews and bibliometrics.

This paper is a **diagnostic evaluation of KT probabilities for mastery/remediation gates**, not a new architecture and not a classroom RCT. Frame it as learning-analytics / evaluation-systems work.

## Publication ethics and generative AI (list-77-1)

Must keep:

- No duplicate submission.
- No fabricated or falsified data.
- Authorship = ICMJE four criteria; no gift/ghost authorship; no AI co-author.
- Disclose AI use in methods or acknowledgments (tool, version, how used). Grammar/language tools are allowed; undisclosed LLM-generated manuscript text is banned.
- Public learner logs: state de-identification / public-dataset status. This study uses published de-identified logs (ASSISTments 2012, Junyi, XES3G5M), not a new classroom trial — do not imply IRB for a classroom intervention that did not occur.
- Open data is encouraged where ethical.

## Template status (Task 1 blocker)

`https://www.ijiet.org/files/IJIET_template.doc` returned **HTTP 500** on repeated fetches (WebFetch and earlier curl). No local copy exists in the repository.

Interim formatting evidence from a **current published article** (not a substitute for the Word template):

- Kazimova et al., IJIET vol. 16, no. 8, pp. 2068–2078, 2026. https://www.ijiet.org/vol16/IJIET-V16N8-2667.pdf

Observed layout (see `FORMAT_FROM_PUBLISHED_ARTICLE.md`): two-column IEEE-like journal, `Abstract—` / `Keywords—`, Roman section numbers, numbered IEEE references, Conflict of Interest, Author Contributions, CC BY 4.0.

**Do not treat `ijiet/main_ijiet.tex` (IEEEtran) as the formatting authority.** Use it only as a content snapshot until the official `.doc` is obtained.

## Dual submission

The JEDM manuscript (`paper/`) and this IJIET conversion share the same experiments. Submitting both in parallel would violate IJIET policy. Withdraw or wait for a JEDM decision before IJIET upload.
