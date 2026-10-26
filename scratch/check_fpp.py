import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-question-paper.html"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "paperSubject" in line:
        for j in range(max(0, i-2), min(len(lines), i+15)):
            print(f"{j+1}: {lines[j]}", end="")
        break
