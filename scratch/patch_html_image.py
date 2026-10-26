import os

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-image-question.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

target1 = '<input class="form-control form-control-sm" type="file" id="imageFileInput" accept="image/jpeg,image/png,image/webp">'
repl1 = '<input class="form-control form-control-sm" type="file" id="imageFileInput" accept="image/jpeg,image/png,image/webp,image/jpg" onchange="handleImageFileUpload(event)">'

target2 = '<div id="imageAnalysisStatus"><span class="badge bg-secondary">Image Uploaded</span></div>'
repl2 = '<div id="imageAnalysisStatus"><span class="badge bg-light text-muted border"><i class="bi bi-image me-1"></i> No Image Selected</span></div>'

assert target1 in content, "target1 not found"
assert target2 in content, "target2 not found"

content = content.replace(target1, repl1)
content = content.replace(target2, repl2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("faculty-image-question.html successfully updated!")
