import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

funcs = ['populateVoiceTopics', 'populateImageTopics', 'populateTransTopics', 'populatePPTTopics', 'populateLPTopics', 'updateAssignmentUnitsDropdown']

for fn in funcs:
    m = re.search(r'function\s+' + fn + r'\s*\([^)]*\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)', content)
    if m:
        print(f"=== {fn} ===")
        print(m.group(0))
        print("="*40)
