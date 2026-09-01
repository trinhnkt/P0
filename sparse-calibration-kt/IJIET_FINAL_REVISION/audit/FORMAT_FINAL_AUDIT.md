# FORMAT_FINAL_AUDIT — A17

**Date:** 2026-09-01  
**Authority:** official IJIET Word template (`IJIET_template.doc`): A4; 1-col front matter; 2-col body 243.65 pt + 14.4 pt gutter; table captions use style `figure caption`, 8 pt, mixed case `Table n.`; empty header/footer (no volume/DOI/running head).  
**Science:** table cells, ECE/FAR locks, Fig. 1 data unchanged.

| Build | Pages |
|-------|------:|
| `output/main_ijiet_full.pdf` | 8 |
| `output/main_ijiet_blind.pdf` | 8 |

## Requested items

| # | Item | Action | Status |
|---|------|--------|--------|
| 1 | `IV. RESULT` → `IV. RESULTS` | Heading 1 text | PASS |
| 2 | IJIET table-caption style | `figure caption`, 8 pt, small caps off, mixed case `Table n.` | PASS |
| 3 | Table 2 tiny/oversized text | Body 8 pt TNR (was 7 pt) | PASS |
| 4 | Spacing at “They are different quantities.” | Section break split off the paragraph so the last line is not fully justified. The line now wraps normally (page 5 → 6) instead of stretching three words across the full measure. | PASS |
| 5 | Figure 1 print size | Width 501.8 pt, aspect locked; 40° ticks already in PNG | PASS |
| 6 | Manual line breaks | Word `^l` replaced with spaces | PASS |
| 7 | Equations | Display ECE remains style `equation` with `(1)`; `_m` set as subscripts | PASS |
| 8 | Symbol typography | `f_train`, `N_advance`, `N_incorrect` → italic + subscript; `ΔFAR` kept; `Delta ECE` → `ΔECE` | PASS |
| 9 | Tables cited near appearance | Tables 1–8 already cited in the preceding paragraph | PASS |
| 10 | Captions legible | 8 pt TNR, not small caps | PASS |
| 11 | Received/revised/accepted dates | Template placeholders only (`Month date, 2026`) | PASS |
| 12 | Volume / issue / DOI / pages | Not added; headers empty | PASS |

## Locks

Named: {'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}  
Blind: {'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}

`IV. RESULT` (singular) remaining: no  
`September 1, 2026` remaining: no  
`10.18178`: no

## Log

```
A17 format cleanup
DATE restored i=7
H1 i=135 IV. RESULTS
EMPTY_SECBR i=567 restyled
EMPTY_SECBR i=566 restyled
EMPTY_SECBR i=516 restyled
EMPTY_SECBR i=515 restyled
SPLIT_SECBR i=422
EMPTY_SECBR i=376 restyled
EMPTY_SECBR i=375 restyled
EMPTY_SECBR i=374 restyled
SPLIT_SECBR i=348
EMPTY_SECBR i=345 restyled
SPLIT_SECBR i=253
EMPTY_SECBR i=251 restyled
EMPTY_SECBR i=250 restyled
EMPTY_SECBR i=249 restyled
SPLIT_SECBR i=193
EMPTY_SECBR i=190 restyled
EMPTY_SECBR i=123 restyled
EMPTY_SECBR i=122 restyled
SPLIT_SECBR i=119
EMPTY_SECBR i=64 restyled
EMPTY_SECBR i=9 restyled
SPLIT_SECBR_N=5
MANUAL_BR_REPLACE=False
CAP i=34 'Table 1. Post-processing cohort statistics (learner-based split). Lear'
CAP i=65 'Table 2. Recovered training settings for the main baselines. NOT RECOV'
CAP i=139 'Table 3. Overall learner-based area under the ROC curve (AUC) and accu'
CAP i=196 'Table 4. T-KT event-level expected calibration error (ECE) by train-on'
CAP i=257 'Table 5. Simulated gate at τ=0.7, ASSISTments 2012 fold 0 (seed 42). F'
CAP i=353 'Table 6. Gate robustness at τ=0.7 on ASSISTments 2012. Five training r'
CAP i=384 'Table 7. Empirical conditions associated with the availability and dir'
CAP i=428 'Table 8. Within-KC controlled sparsification at protocol endpoints (50'
CAP_N=8
T2 10x4 font=8pt prefW=97.9000015258789
FIG w=501.8 h=352.5
EQSUB acc_m i=129
EQSUB conf_m i=129
EQSUB n_m i=129
EQSUB Σ_m i=129
EQ_TYPED i=129 '\tECE = Σm (nm / N) |accm − confm|\t(1)'
SYM f_train=7
SYM N_advance=8
SYM N_incorrect=7
DELTA_ECE_REPLACE
Delta_ECE_left=0
FIGCAP i=122
FULL_TABLES=8 FIGS=1
ANON_AUTHORS i=2
ANON_AFFIL i=3
DEL_AFFIL2 i=4
DEL_EMAIL i=5
DEL_CORR i=6
ANON_CONTRIB i=538
ANON_ACK i=546
FULL_PAGES=8 BLIND_PAGES=8
FULL_LOCKS={'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}
BLIND_LOCKS={'pages_8': True, 'ece_1136': True, 'ece_2280': True, 'far_196': True, 'far_268': True, 'fig1': True, 'ref21': True, 'ref22': True}
HAS_IV_RESULTS=True
HAS_IV_RESULT_SINGULAR=False
TABLE1_MIXED=True
TABLE1_ALLCAPS=False
DATES_PLACEHOLDER=True
SEP1=False
```
