import re

page_funcs = [
    'renderFacultyResourcesTable',
    'initQuestionGeneratorPage',
    'loadQuestionPaperBuilderPage',
    'initQuizGeneratorPage',
    'initAssignmentGeneratorPage',
    'initPPTGeneratorPage',
    'initLessonPlanGeneratorPage',
    'initVoiceQuestionPage',
    'initImageQuestionPage',
    'initLanguageConverterPage',
    'renderFacultyResultsPage',
    'renderFacultyPerformancePage',
    'renderFacultyHistoryPage'
]

with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js", "r", encoding="utf-8") as f:
    text = f.read()

for fn in page_funcs:
    m = re.search(r'(?:async\s+)?function\s+' + fn + r'\s*\([^)]*\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)', text)
    if m:
        print(f"=== {fn} ===")
        print(m.group(0)[:500])
        print("...\n")
    else:
        print(f"NOT FOUND: {fn}\n")
