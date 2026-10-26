import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(17330, min(len(lines), 17430)):
    print(f"{i+1}: {repr(lines[i])}")
