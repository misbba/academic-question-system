import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace exam_type resolution and section matching in validate_question_paper_structure
old_code = """    exam_type = str(paper_data.get('exam_type') or '').lower()"""
new_code = """    exam_type = str(paper_data.get('exam_type') or paper_data.get('paper_type') or paper_data.get('template') or paper_data.get('template_type') or '').lower()"""

content = content.replace(old_code, new_code)
content = content.replace("str(s.get('name', '')).upper()", "str(s.get('name') or s.get('title') or '').upper()")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("validate_question_paper_structure patched successfully.")
