import re

paths = [
    'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/backend/services/question_paper_service.py',
    'C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/backend/services/quiz_service.py'
]

for path in paths:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'if department not in OFFICIAL_DEPARTMENTS:\s+return False, \{"status": "error", "message": f"Invalid department[^"]+"\}, 400', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub('if not department:\n        department = "General Engineering"', content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
    else:
        print(f"Pattern not found in {path}")
