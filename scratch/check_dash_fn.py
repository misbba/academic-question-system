with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'dashboard-stats' in l:
        print(f"Line {i+1}: {l}")
        start = max(0, i-40)
        end = min(len(lines), i+80)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}", end="")
        break
