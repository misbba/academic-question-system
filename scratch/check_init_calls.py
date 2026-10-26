import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

funcs = [
    'initVoiceQuestionForm',
    'initImageQuestionForm',
    'initTransQuestionForm',
    'initPPTQuestionForm',
    'initLPQuestionForm',
    'initAssignmentForm'
]

for fn in funcs:
    matches = [m.start() for m in re.finditer(fn, content)]
    print(f"{fn}: called {len(matches)} times")
