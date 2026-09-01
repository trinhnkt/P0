from docx import Document
from pathlib import Path

p = Path(r"C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\source\main_ijiet_step04.docx")
d = Document(str(p))
out = Path(r"C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\audit\step04_intro.txt")
lines = []
capture = False
for para in d.paragraphs:
    st = para.style.name
    t = para.text.strip()
    if st == "Heading 1" and t.startswith("Introduction"):
        capture = True
        lines.append(f"[{st}] {t}")
        continue
    if capture and st == "Heading 1":
        lines.append(f"STOP [{st}] {t}")
        break
    if capture:
        lines.append(f"[{st}] {t}")
out.write_text("\n".join(lines), encoding="utf-8")
print(out.read_text(encoding="utf-8"))
