import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

m = re.findall(r'document\.addEventListener\([\'"]DOMContentLoaded[\'"][\s\S]*?(?=\n(?:async\s+)?function|\Z)', content)
for idx, match in enumerate(m):
    print(f"=== DOMContentLoaded {idx+1} ===")
    print(match[:500])
    print("...\n")
