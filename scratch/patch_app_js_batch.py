app_js = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"
with open(app_js, "r", encoding="utf-8") as f:
    code = f.read()

target = "body: JSON.stringify({ batch: questionsToSave })"
replacement = "body: JSON.stringify({ questions: questionsToSave, batch: questionsToSave })"

if target in code:
    code = code.replace(target, replacement, 1)
    with open(app_js, "w", encoding="utf-8") as f:
        f.write(code)
    print("Updated saveImageQuestionsToBank in js/app.js")
else:
    print("Already updated or target not found")
