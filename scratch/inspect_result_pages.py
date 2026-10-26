with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

for fn_name in ['renderFacultyResultsPage', 'renderFacultyPerformancePage', 'renderFacultyHistoryPage']:
    pos = text.find(f'function {fn_name}')
    print(f"\n==================== {fn_name} (pos {pos}) ====================")
    if pos != -1:
        line_no = text[:pos].count('\n') + 1
        lines = text[pos:pos+1500].split('\n')
        print(f"Line {line_no}:")
        print('\n'.join(lines[:35]))
