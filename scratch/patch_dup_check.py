import os, re

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

pattern = re.compile(
    r'(if not q_text or not subj:\s*continue\s*)(cursor\.execute\(sql_q,)',
    re.MULTILINE
)

replacement = r'''\1# Check if identical question already exists for this faculty and subject
                cursor.execute(
                    "SELECT id FROM questions WHERE created_by = %s AND subject = %s AND question_text = %s LIMIT 1",
                    (faculty_id, subj, q_text)
                )
                existing_row = cursor.fetchone()
                if existing_row:
                    q_id = existing_row['id'] if isinstance(existing_row, dict) else existing_row[0]
                    cursor.execute("UPDATE questions SET is_in_bank = TRUE, status = 'Bank' WHERE id = %s", (q_id,))
                    created_ids.append(q_id)
                    continue

                \2'''

content_new, count = pattern.subn(replacement, content, count=1)
if count > 0:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content_new)
    print("SUCCESS: Added duplicate check to create_questions_batch")
else:
    print("WARN: Pattern not matched")
