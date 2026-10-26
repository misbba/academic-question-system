with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\quiz_routes.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if l.strip().startswith("def "):
        print(f"\nLine {i+1}: {l.strip()}")
        for j in range(i+1, min(len(lines), i+30)):
            print(f"  {lines[j]}", end="")
