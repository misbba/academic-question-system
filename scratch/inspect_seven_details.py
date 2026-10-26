import os, re

files = [
    'faculty-voice-question.html',
    'faculty-image-question.html',
    'faculty-language-converter.html',
    'faculty-question-paper.html',
    'faculty-generate-assignment.html',
    'faculty-generate-ppt.html',
    'faculty-generate-lesson-plan.html'
]
base = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system'

for fname in files:
    path = os.path.join(base, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f'=== {fname} ===')
    
    # Check what IDs exist
    ids = re.findall(r'id=["\']([^"\']+)["\']', content)
    dept_subj_ids = [i for i in ids if any(k in i.lower() for k in ['dept', 'subject', 'unit', 'topic', 'question', 'generate', 'assign', 'count', 'num'])]
    print(f'Relevant IDs: {dept_subj_ids}')
    
    # Check button clicks or onclicks
    onclicks = re.findall(r'onclick=["\']([^"\']+)["\']', content)
    print(f'Onclicks: {onclicks}')
    
    # Check inline scripts
    scripts = re.findall(r'<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>', content)
    print(f'Inline script tags count: {len(scripts)}')
    for idx, s in enumerate(scripts):
        s_clean = s.strip()
        if s_clean:
            print(f'  Inline Script {idx+1}: {s_clean[:120]}...\n')
    print('-'*50)
