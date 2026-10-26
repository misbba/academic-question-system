import os
import re

for root, dirs, files in os.walk(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"):
    for file in files:
        if file.endswith('.py'):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = re.findall(r'.{0,50}(?:diagram|image_file|upload_file|request\.files).{0,50}', content, re.IGNORECASE)
                if matches:
                    print(f"\n--- {file} ({len(matches)} matches) ---")
                    for m in matches[:5]:
                        print("  ", m.strip())
