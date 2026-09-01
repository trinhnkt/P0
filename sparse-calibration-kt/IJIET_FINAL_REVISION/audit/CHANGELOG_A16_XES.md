# CHANGELOG_A16_XES — Apply A2B XES; date; AI wording; IRT paragraph

Preserved from the same-day scientific A16 apply. The current `CHANGELOG_A16.md` documents the double-blind manuscript builds.

**Date:** 2026-09-01  
**Retrain:** no. **ASSISTments locks:** unchanged (`0.1136`, `0.2280`, FAR `0.196`/`0.268`, ΔFAR `0.047`, CI `[0.006, 0.138]`).

## 1. A2B XES only

Manuscript now uses the masked XES3G5M tree (`a2b/`). Padding −1 is excluded. Junyi unchanged.

| Location | Old (obsolete) | New |
|---|---|---|
| Table 1 | 866 KC / 7.95M / 1,589,145 | 865 / 6.41M / 1,282,422 |
| Table 3 DKT | 0.8171 / 0.8327 | 0.8180±0.0009 / 0.8321±0.0015 |
| Table 3 T-KT | 0.7557 / 0.8067 | 0.7536±0.0010 / 0.8057±0.0029 |
| Table 4 T-KT ECE | 0.1145 / 0.1114 / 0.1248 N=2,010 | 0.1176 / 0.1129 / 0.1254 N=1,969 |
| XES ΔMiss | +0.112 | **−0.183** (ΔFAR still negative) |
| Table 7 | ρ=+0.087; N=2,010; −0.125 | +0.110; 1,969; −0.126 |
| Table 8 DKT 500 | −0.008 (CI includes 0) | +0.142 [+0.104, +0.189] ECE higher |
| Table 8 T-KT 50 | +0.032 | +0.110 [+0.071, +0.156] |
| Regression XES | n=1,263 / −0.069 | n=829 / −0.028 |

Fig. 1 regenerated with A2B XES strata. Supplementary S1/S2/S-regression XES rows aligned.

Obsolete claim removed: XES ΔFAR and ΔMiss moving in opposite directions.

## 2. AI statement

Did **not** invent ChatGPT/Claude/Antigravity model names. Marker removed. Verifiable revision model: **Cursor Grok 4.6**. The three named tools remain without fabricated versions.

## 3. Date

Manuscript received **September 1, 2026**. Revised/accepted left as `Month date, 2026`.

## 4. IRT paragraph

Methods IRT fallback starts after the GKT/CL4KT sentence (new paragraph).

## Compile

8 pages; locked ASSISTments ECE/FAR checks true.

Backup: `manuscript/main_ijiet_full.docx.bak_pre_a16`.
