with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\utils\document_parser.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(230, 330):
    print(f"{i+1}: {lines[i]}", end='')
