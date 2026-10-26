import os
import re

for root, dirs, files in os.walk(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"):
    if 'node_modules' in root or '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith(('.js', '.html', '.py', '.json', '.sql')):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read()
                matches = re.findall(r'.{0,40}lamport.{0,40}', c, re.IGNORECASE)
                if matches:
                    print(f"\n{file}:")
                    for m in matches[:5]:
                        print("  ", m.strip())
