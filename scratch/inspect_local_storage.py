import re

with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'localStorage\.(?:getItem|setItem)\([\'"]([^\'"]+)[\'"]', text)
print('Unique localStorage keys in app.js:')
for k in sorted(set(matches)):
    print('  ', k)
