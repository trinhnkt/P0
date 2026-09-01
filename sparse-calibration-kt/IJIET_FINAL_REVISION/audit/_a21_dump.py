from pathlib import Path
import sys
import zipfile
from xml.etree import ElementTree as ET
import win32com.client as win32

sys.stdout.reconfigure(encoding="utf-8")
DOCX = Path("IJIET_FINAL_REVISION/manuscript/main_ijiet_full.docx")
OUT = Path("IJIET_FINAL_REVISION/audit/_a21_dump.txt")
ns_p = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"
ns_t = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
needles = (
    "locked global threshold",
    "published SimpleKT",
    "grid {0.5",
    "Coincidence of digits",
    "Table 5 is a simulated",
    "Table 6. Gate",
    "four checks are warranted",
    "snapshot commit",
    "unseen learners trigger",
    "Exploratory GKT",
    "no classroom RCT",
)
with zipfile.ZipFile(DOCX) as z:
    root = ET.fromstring(z.read("word/document.xml"))
buf: list[str] = []
for i, para in enumerate(root.iter(ns_p)):
    s = "".join((t.text or "") for t in para.iter(ns_t))
    if s.strip() and any(n.lower() in s.lower() for n in needles):
        buf.append(f"--- i={i} ---\n{s}\n")

word = win32.gencache.EnsureDispatch("Word.Application")
word.Visible = False
word.DisplayAlerts = 0
doc = word.Documents.Open(str(DOCX.resolve()), ReadOnly=True)
try:
    t = doc.Tables(5)
    buf.append(f"TABLE5 rows={t.Rows.Count} cols={t.Columns.Count}\n")
    for r in range(1, t.Rows.Count + 1):
        cells = []
        for c in range(1, min(3, t.Columns.Count) + 1):
            txt = t.Cell(r, c).Range.Text.replace("\r", " ").replace("\x07", "").strip()
            cells.append(txt[:48])
        buf.append(f"r{r}: {cells}\n")
    t6 = doc.Tables(6)
    buf.append(f"TABLE6 rows={t6.Rows.Count}\n")
finally:
    doc.Close(0)
    word.Quit()

OUT.write_text("".join(buf), encoding="utf-8")
print("wrote", OUT)
