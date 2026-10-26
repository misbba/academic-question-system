with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "def generate_template_paper" in l:
        print(f"Line {i+1}: {l}")
        for j in range(i+1, min(len(lines), i+80)):
            print(f"{j+1}: {lines[j]}", end="")
        break
