import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(r'async function saveGeneratedToBank\(\)\s*\{[\s\S]*?(?=\n(?:async )?function|\Z)')
m = pattern.search(content)
if m:
    print(m.group(0)[:1000])
