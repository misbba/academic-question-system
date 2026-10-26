with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\mock-data.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "publishedImageQuestions" in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
