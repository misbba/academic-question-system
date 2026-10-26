with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(21570, 21590):
    print(f"{idx+1}: {repr(lines[idx])}")

print("---")
for idx in range(22360, 22378):
    print(f"{idx+1}: {repr(lines[idx])}")
