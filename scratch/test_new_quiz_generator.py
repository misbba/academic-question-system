import os
import sys

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from utils.document_parser import extract_text_from_file

u2_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1792995052_dc_unit_2.docx")
u3_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1793005325_unit_3_dc.docx")

t2 = extract_text_from_file(u2_path)
t3 = extract_text_from_file(u3_path)
full_text = t2 + "\n" + t3

# Let's inspect the quiz questions we will construct
print(f"Material loaded: {len(full_text)} characters.")
