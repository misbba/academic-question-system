import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

line1_old = "const subMarks = sq.marks || (sIdx === 0 ? 8 : 5);"
line1_new = "const subMarks = sq.marks || 8;"

line2_old = "const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 13));"
line2_new = "const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 16));"

assert line1_old in content, "line1_old not found"
assert line2_old in content, "line2_old not found"

content = content.replace(line1_old, line1_new).replace(line2_old, line2_new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Line replacements applied successfully.")
