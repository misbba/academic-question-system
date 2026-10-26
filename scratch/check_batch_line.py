import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(380, 430):
    print(f"{i+1}: {repr(lines[i])}")
