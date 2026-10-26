import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(20970, min(len(lines), 21060)):
    print(f"{i+1}: {repr(lines[i])}")
