import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

import re
save_fn = re.search(r'def save_to_question_bank[\s\S]*?(?=def remove_from_question_bank|\Z)', content)
if save_fn:
    print(save_fn.group(0))
