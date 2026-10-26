with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    text = f.read()

keywords = ['publishedVoiceQuestions', 'publishedImageQuestions', 'publishedTranslatedQuestions', 'publishedAssignments', 'publishedPPTs', 'publishedLessonPlans', 'masterQuestionsPool']
for kw in keywords:
    print(f"\n==================== {kw} ====================")
    idx = 0
    while True:
        pos = text.find(kw, idx)
        if pos == -1:
            break
        # find line number
        line_no = text[:pos].count('\n') + 1
        # extract ~10 lines
        lines = text[max(0, pos-200):min(len(text), pos+300)].split('\n')
        print(f"--- Line ~{line_no} ---")
        print('\n'.join(lines[:6]))
        idx = pos + len(kw)
