import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "def create_questions_batch" in l:
        for j in range(i, min(len(lines), i+90)):
            print(f"{j+1}: {lines[j]}", end="")
        break
