import docx
import os
import re

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
u2_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1792995052_dc_unit_2.docx")
u3_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1793005325_unit_3_dc.docx")

def get_text(path):
    if not os.path.exists(path): return ""
    doc = docx.Document(path)
    lines = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if t: lines.append(t)
    return "\n".join(lines)

t2 = get_text(u2_path)
t3 = get_text(u3_path)
material_text = t2 + "\n" + t3

print(f"Loaded material: {len(material_text)} chars")
