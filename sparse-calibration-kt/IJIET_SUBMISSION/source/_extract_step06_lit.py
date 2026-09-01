from pathlib import Path
from docx import Document

p = Path(r"C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\source\main_ijiet_step06.docx")
d = Document(str(p))
out = Path(r"C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\audit\step06_lit.txt")
lines = []
capture = False
for para in d.paragraphs:
    st = para.style.name
    t = para.text.strip()
    if st == "Heading 1" and t.startswith("Introduction"):
        capture = True
        lines.append(f"[{st}] {t}")
        continue
    if capture and st == "Heading 1" and "Materials" in t:
        lines.append(f"STOP [{st}] {t}")
        break
    if capture:
        lines.append(f"[{st}] {t[:500]}")
out.write_text("\n".join(lines), encoding="utf-8")
print("paras", len(lines))
