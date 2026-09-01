#!/usr/bin/env python3
from __future__ import annotations

import re
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parent / "main_ijiet_step10.docx"
xml = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
out = Path(__file__).resolve().parents[1] / "audit" / "step10_results.txt"
paras = []
for m in re.finditer(r"<w:p[ >].*?</w:p>", xml, re.S):
    block = m.group()
    sm = re.search(r'w:pStyle w:val="([^"]+)"', block)
    style = sm.group(1) if sm else ""
    text = re.sub(r"<[^>]+>", "", block)
    text = (
        text.replace("&gt;", ">")
        .replace("&lt;", "<")
        .replace("&amp;", "&")
        .replace("\xa0", " ")
    )
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        paras.append((style, text))

lines = []
capture = False
for i, (s, t) in enumerate(paras):
    if "RESULT AND DISCUSSION" in t.upper() or t.upper().startswith("IV."):
        capture = True
    if capture and ("CONCLUSION" in t.upper() and "RESULT" not in t.upper() and len(t) < 40):
        lines.append(f"{i:03d} [{s}] {t}")
        break
    if capture:
        if s.startswith("Heading") or len(t) < 120 or t.startswith("Table "):
            lines.append(f"{i:03d} [{s}] {t[:500]}")
        else:
            lines.append(f"{i:03d} [{s}] {t[:400]}")
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", out, "n=", len(lines))
