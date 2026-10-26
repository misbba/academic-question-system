with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1370, len(lines)):
    print(f"{i+1}: {lines[i]}", end='')
