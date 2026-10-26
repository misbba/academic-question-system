import glob, re

html_files = [
    'faculty-generate-questions.html',
    'faculty-voice-question.html',
    'faculty-image-question.html',
    'faculty-language-converter.html',
    'faculty-question-paper.html',
    'faculty-generate-quiz.html',
    'faculty-generate-assignment.html',
    'faculty-generate-ppt.html',
    'faculty-generate-lesson-plan.html'
]

base_dir = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system'

for fname in html_files:
    fpath = f"{base_dir}\\{fname}"
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    datalists = re.findall(r'<datalist id=["\']([^"\']+)["\']>(.*?)</datalist>', content, re.DOTALL)
    print(f"\n{fname}:")
    for dl_id, dl_body in datalists:
        opts = re.findall(r'<option value=["\']([^"\']+)["\']', dl_body)
        print(f"  datalist id={dl_id}: {opts}")
