#!/usr/bin/env python3
from __future__ import annotations

import re
import zipfile
from pathlib import Path

p = Path(__file__).resolve().parent / "main_ijiet_step12.docx"
xml = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
out = Path(__file__).resolve().parents[1] / "audit" / "step12_headings.txt"
paras = []
capture = False
for m in re.finditer(r"<w:p[ >].*?</w:p>", xml, re.S):
    block = m.group()
    sm = re.search(r'w:pStyle w:val="([^"]+)"', block)
    style = sm.group(1) if sm else ""
    text = re.sub(r"<[^>]+>", "", block)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        continue
    if "RESULT" in text.upper() and "Heading" in style:
        capture = True
    if capture:
        paras.append(f"{style}\t{text[:220]}")
    if capture and "CONFLICT" in text.upper():
        break
out.write_text("\n".join(paras) + "\n", encoding="utf-8")
print("n", len(paras), "->", out)
