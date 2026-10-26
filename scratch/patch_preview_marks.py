import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(path, "r", encoding="utf-8") as f:
    content = f.read().replace("\r\n", "\n")

old_snippet = """                    const subPart = sq.part || (sIdx === 0 ? '(i)' : '(ii)');
                    const subMarks = sq.marks || (sIdx === 0 ? 8 : 5);"""

new_snippet = """                    const subPart = sq.part || (sIdx === 0 ? '(i)' : '(ii)');
                    const subMarks = sq.marks || 8;"""

assert old_snippet in content, "old_snippet not found"
content = content.replace(old_snippet, new_snippet)

old_single = """              const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 13));"""
new_single = """              const marksVal = alt.marks || (sec.marks_per_q || (isInternal ? 8 : 16));"""

assert old_single in content, "old_single not found"
content = content.replace(old_single, new_single)

content_crlf = content.replace("\n", "\r\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(content_crlf)

print("js/app.js preview defaults patched successfully.")
