with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(22050, 22120):
    print(f"{i+1}: {lines[i]}", end='')
