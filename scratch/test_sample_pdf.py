import sys
import os

backend_dir = os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from utils.document_parser import extract_text_from_file

pdf_path = os.path.join(backend_dir, 'uploads', 'resources', '1790159359_sample_syllabus.pdf')
txt = extract_text_from_file(pdf_path)
print("Extracted length:", len(txt))
print("Sample:\n", txt[:500])
