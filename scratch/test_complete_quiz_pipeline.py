import os
import sys

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

from utils.document_parser import extract_text_from_file

u2_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1792995052_dc_unit_2.docx")
u3_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1793005325_unit_3_dc.docx")

t2 = extract_text_from_file(u2_path)
t3 = extract_text_from_file(u3_path)

print("Unit 2 preview:")
for line in t2.split('\n')[:15]:
    if line.strip(): print("  ", line[:80])

print("\nUnit 3 preview:")
for line in t3.split('\n')[:15]:
    if line.strip(): print("  ", line[:80])
