with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-generate-assignment.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("IDs found in faculty-generate-assignment.html:")
for m in re.finditer(r'id=["\']([^"\']+)["\']', text):
    print(" ", m.group(1))
