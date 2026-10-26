import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

for fn in ['saveVoiceQuestions', 'saveImageQuestionsToBank', 'saveTranslatedQuestion']:
    m = re.search(r'function\s+' + fn + r'\(\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)', content)
    if m:
        print(f"=== {fn} ===")
        print(m.group(0))
        print("="*40)
