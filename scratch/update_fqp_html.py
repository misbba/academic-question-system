fqp_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-question-paper.html"

with open(fqp_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace <select class="form-select" id="paperExamType">
old_str = '<select class="form-select" id="paperExamType">'
new_str = '<select class="form-select" id="paperExamType" onchange="onExamTypeChanged()">'

assert old_str in content, "Could not find old_str"
content = content.replace(old_str, new_str, 1)

# Add <option value="Internal Examination">Internal Examination</option> right after Semester Examination option
old_opt = '<option value="Semester Examination" selected>Semester Examination</option>'
new_opt = '<option value="Semester Examination" selected>Semester Examination</option>\n                <option value="Internal Examination">Internal Examination</option>'

assert old_opt in content, "Could not find old_opt"
content = content.replace(old_opt, new_opt, 1)

with open(fqp_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated faculty-question-paper.html!")
