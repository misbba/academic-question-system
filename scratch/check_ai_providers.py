import os
import re

print("--- Checking config.py ---")
cfg_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\config.py"
if os.path.exists(cfg_path):
    with open(cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())

print("\n--- Checking for AI providers across backend ---")
for root, dirs, files in os.walk(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"):
    for file in files:
        if file.endswith('.py'):
            p = os.path.join(root, file)
            with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read()
                matches = re.findall(r'.{0,40}(?:openai|gemini|anthropic|tesseract|vision|api_key|google\.generativeai).{0,40}', c, re.IGNORECASE)
                if matches:
                    print(f"\n{file}:")
                    for m in matches[:5]:
                        print("  ", m.strip())
