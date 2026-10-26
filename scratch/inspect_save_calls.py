with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
patterns = [
    r"localStorage\.setItem\('academic_voice_questions'[^;]+;",
    r"localStorage\.setItem\('academic_image_questions'[^;]+;",
    r"localStorage\.setItem\('academic_translated_questions'[^;]+;",
    r"localStorage\.setItem\('academic_ppts'[^;]+;",
    r"localStorage\.setItem\('academic_lesson_plans'[^;]+;",
    r"localStorage\.setItem\('academic_assignments'[^;]+;"
]

for pat in patterns:
    matches = list(re.finditer(pat, c))
    print(f"\nPattern: {pat} ({len(matches)} matches)")
    for m in matches:
        line_no = c[:m.start()].count('\n') + 1
        print(f"  Line {line_no}: {m.group(0)[:80]}")
