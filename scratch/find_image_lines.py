with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ["handleImage", "generateQuestionsFromImage", "analyzeUploadedImage", "initImageQuestionForm", "saveImageQuestionsToBank", "removeUploadedImage"]):
        print(f"{i+1}: {line.strip()[:100]}")
