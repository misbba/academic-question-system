import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "function bindGeneratorStubs" in l:
        print(f"Line {i+1}: {l}")
        for j in range(i, min(len(lines), i+60)):
            print(f"{j+1}: {lines[j]}", end="")
        break
