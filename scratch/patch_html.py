path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-generate-questions.html"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

target1 = '<input type="file" class="form-control" id="genQuickUploadFile" accept=".pdf,.docx,.doc,.txt">'
repl1 = '<input type="file" class="form-control" id="genQuickUploadFile" accept=".pdf,.docx,.doc,.txt" onchange="onQuickUploadFileSelected()">'

target2 = '<button type="button" class="btn btn-outline-primary" onclick="handleQuickUploadForGen()">'
repl2 = '<button type="button" id="genQuickUploadBtn" class="btn btn-outline-primary" onclick="handleQuickUploadForGen()">'

assert target1 in c, "target1 not found"
assert target2 in c, "target2 not found"

c = c.replace(target1, repl1)
c = c.replace(target2, repl2)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("faculty-generate-questions.html successfully updated!")
