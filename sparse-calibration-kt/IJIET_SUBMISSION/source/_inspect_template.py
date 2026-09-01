from docx import Document

p = r"C:\TRINH\Sparse-Concept and Calibration\sparse-calibration-kt\IJIET_SUBMISSION\audit\IJIET_template.docx"
d = Document(p)
print("styles:")
for s in d.styles:
    try:
        font = getattr(s, "font", None)
        fn = font.name if font is not None else None
        sz = font.size.pt if font is not None and font.size else None
        print(f"  {s.type} | {s.name!r} | font={fn} size={sz}")
    except Exception as e:
        print("  err", e)
print("\nsections", len(d.sections))
for i, sec in enumerate(d.sections, 1):
    print(
        i,
        "w",
        round(sec.page_width.pt, 2),
        "h",
        round(sec.page_height.pt, 2),
        "m",
        round(sec.top_margin.pt, 2),
        round(sec.bottom_margin.pt, 2),
        round(sec.left_margin.pt, 2),
        round(sec.right_margin.pt, 2),
    )
print("\nfirst 20 paras:")
for i, para in enumerate(d.paragraphs[:20], 1):
    print(i, para.style.name, repr(para.text[:90]))
