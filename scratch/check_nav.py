import os, re

root = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
found = []
for f in os.listdir(root):
    if f.endswith('.html'):
        p = os.path.join(root, f)
        with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
            c = fp.read()
            for line in c.splitlines():
                if any(k in line.lower() for k in ['fingerprint', 'biometric']):
                    found.append((f, line.strip()))

for f, l in found:
    print(f"{f}: {l}")
