import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

matches = re.findall(r'function\s+([A-Za-z0-9_]*datalist[A-Za-z0-9_]*|[A-Za-z0-9_]*Units[A-Za-z0-9_]*|[A-Za-z0-9_]*Topics[A-Za-z0-9_]*)\s*\(', content, re.IGNORECASE)
print("Matched functions:", set(matches))
