import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(14915, min(len(lines), 14980)):
    print(f"{i+1}: {repr(lines[i])}")
