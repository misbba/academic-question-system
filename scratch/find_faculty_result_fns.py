with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'function\s+(renderFaculty[a-zA-Z0-9_]*|init[a-zA-Z0-9_]*Page|load[a-zA-Z0-9_]*)\s*\(', text)
print('Functions found in app.js:', matches)
for m in matches:
    if any(k in m.lower() for k in ['result', 'perf', 'history', 'student']):
        print('  Relevant function:', m)
