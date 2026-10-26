import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

def show_fn(name):
    m = re.search(r'function\s+' + name + r'\s*\([^)]*\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)', content)
    if m:
        print(f"=== {name} ===")
        print(m.group(0)[:1500])
        print("...\n")

show_fn('generateQuestionsFromVoice')
show_fn('generateQuestionsFromImage')
show_fn('convertAcademicLanguage')
show_fn('generatePPTContent')
show_fn('generateLessonPlanContent')
