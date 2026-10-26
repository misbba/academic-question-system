import docx
import os
import re

BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
u2_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1792995052_dc_unit_2.docx")
u3_path = os.path.join(BASE_DIR, "backend", "uploads", "resources", "1793005325_unit_3_dc.docx")

def get_text(path):
    if not os.path.exists(path): return ""
    doc = docx.Document(path)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])

t2 = get_text(u2_path)
t3 = get_text(u3_path)
full_text = t2 + "\n" + t3

# Test topic matching
def match_topic_content(topic, text):
    terms = [w.lower() for w in re.findall(r'[a-zA-Z0-9]+', topic) if len(w) > 2 and w.lower() not in ['and', 'for', 'the', 'with', 'unit']]
    matching_lines = []
    for line in text.split('\n'):
        if any(term in line.lower() for term in terms) and len(line) > 20:
            matching_lines.append(line)
    return terms, matching_lines

for top in ["Lamport's Algorithm", "Mutual Exclusion", "Christian's Method", "Vector Clock", "Quantum Mechanics"]:
    terms, matched = match_topic_content(top, full_text)
    print(f"Topic: '{top}' -> {len(matched)} matching lines")
