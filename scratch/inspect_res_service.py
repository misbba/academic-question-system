with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\resource_service.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if l.strip().startswith("def "):
        print(f"\nLine {i+1}: {l.strip()}")
        for j in range(i+1, min(len(lines), i+35)):
            print(f"  {lines[j]}", end="")
