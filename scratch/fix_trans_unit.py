import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(r"unit:\s*document\.getElementById\('transUnitSelect'\)\?\.options\[document\.getElementById\('transUnitSelect'\)\?\.selectedIndex\]\?\.text\s*\|\|\s*\"[^\"]+\",")
replacement = "unit: (document.getElementById('transUnitSelect')?.value || '').trim() || 'Unit 1',"

content_new, count = pattern.subn(replacement, content)
print(f"Applied {count} substitution(s)")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content_new)
