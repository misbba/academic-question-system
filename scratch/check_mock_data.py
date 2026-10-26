import re

with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'const AcademicMockData = \{[\s\S]*?\n\};', text)
if m:
    print(m.group(0)[:1500])
