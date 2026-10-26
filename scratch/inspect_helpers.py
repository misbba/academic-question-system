with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

for fn_name in ['getAllStudentResults', 'getAllFacultyHistory', 'renderFacultyResultsPage']:
    pos = text.find(f'{fn_name}')
    print(f"\n==================== {fn_name} (pos {pos}) ====================")
    while pos != -1:
        line_no = text[:pos].count('\n') + 1
        lines = text[pos:pos+600].split('\n')
        print(f"Line {line_no}:")
        print('\n'.join(lines[:15]))
        pos = text.find(fn_name, pos + len(fn_name))
