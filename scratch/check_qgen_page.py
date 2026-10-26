with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'function initQuestionGeneratorPage' in l:
        print(f"Line {i+1}: {l}")
        for j in range(i, min(len(lines), i+90)):
            print(f"{j+1}: {lines[j]}", end="")
        break
