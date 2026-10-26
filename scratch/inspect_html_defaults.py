import glob, re

html_files = [
    'faculty-dashboard.html',
    'faculty-resources.html',
    'faculty-generate-questions.html',
    'faculty-voice-question.html',
    'faculty-image-question.html',
    'faculty-language-converter.html',
    'faculty-question-paper.html',
    'faculty-generate-quiz.html',
    'faculty-generate-assignment.html',
    'faculty-generate-ppt.html',
    'faculty-generate-lesson-plan.html',
    'faculty-results.html',
    'faculty-performance.html',
    'faculty-history.html',
    'faculty-profile.html'
]

base_dir = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system'

for fname in html_files:
    fpath = f"{base_dir}\\{fname}"
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for inputs with Database Management Systems or default subject
    dbms_matches = re.findall(r'<input[^>]*value=["\'][^"\']*Database Management Systems[^"\']*["\'][^>]*>', content, re.IGNORECASE)
    select_matches = re.findall(r'<option[^>]*selected[^>]*>[^<]*Database Management Systems[^<]*</option>', content, re.IGNORECASE)
    print(f"\n{fname}:")
    print(f"  Inputs with DBMS default: {len(dbms_matches)}")
    for m in dbms_matches[:3]:
        print(f"    {m[:100]}")
    print(f"  Select options selected DBMS: {len(select_matches)}")
    for m in select_matches[:3]:
        print(f"    {m[:100]}")
