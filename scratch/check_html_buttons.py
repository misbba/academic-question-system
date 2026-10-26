with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-image-question.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if any(k in line for k in ["imageFileInput", "analyzeUploadedImage", "generateQuestionsFromImage", "removeUploadedImage", "saveImageQuestionsToBank", "imageAnalysisStatus", "imagePreviewContainer"]):
        print(f"{i+1}: {line.strip()[:100]}")
