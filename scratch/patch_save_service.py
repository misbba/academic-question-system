import os

filepath = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update create_questions_batch to check for existing questions before insert
old_create_loop = """            for item in questions_list:
                q_text = (item.get('question_text') or item.get('text') or item.get('question') or '').strip()
                subj = (item.get('subject') or item.get('course') or '').strip()
                dept = (item.get('department') or 'Artificial Intelligence & Data Science').strip()
                year = (item.get('academic_year') or '2025-2026').strip()
                sem = (item.get('semester') or 'Semester 6').strip()
                un = (item.get('unit') or item.get('source_unit') or 'Unit III  SQL').strip()
                top = (item.get('topic') or '').strip()
                q_type = (item.get('question_type') or item.get('type') or 'Short Answer').strip()
                diff = (item.get('difficulty') or 'Medium').strip()
                bloom = (item.get('bloom_level') or item.get('blooms') or item.get('bloomsTaxonomy') or 'Understand').strip()
                cpt = (item.get('concept') or '').strip()
                exp = (item.get('explanation') or '').strip()
                marks = int(item.get('marks', 2))
                status = (item.get('status') or 'Generated').strip()
                in_bank = bool(item.get('is_in_bank', False))
                res_id = item.get('resource_id')

                if not q_text or not subj:
                    continue

                cursor.execute(sql_q, (
                    res_id, q_text, subj, dept, year, sem,
                    un, top, q_type, diff, bloom, cpt,
                    un, exp, marks, status, in_bank, faculty_id
                ))
                q_id = cursor.lastrowid
                created_ids.append(q_id)"""

new_create_loop = """            for item in questions_list:
                q_text = (item.get('question_text') or item.get('text') or item.get('question') or '').strip()
                subj = (item.get('subject') or item.get('course') or '').strip()
                dept = (item.get('department') or 'Artificial Intelligence & Data Science').strip()
                year = (item.get('academic_year') or '2025-2026').strip()
                sem = (item.get('semester') or 'Semester 6').strip()
                un = (item.get('unit') or item.get('source_unit') or 'Unit 1').strip()
                top = (item.get('topic') or '').strip()
                q_type = (item.get('question_type') or item.get('type') or 'Short Answer').strip()
                diff = (item.get('difficulty') or 'Medium').strip()
                bloom = (item.get('bloom_level') or item.get('blooms') or item.get('bloomsTaxonomy') or 'Understand').strip()
                cpt = (item.get('concept') or '').strip()
                exp = (item.get('explanation') or '').strip()
                marks = int(item.get('marks', 2))
                status = (item.get('status') or 'Bank').strip()
                in_bank = bool(item.get('is_in_bank', True))
                res_id = item.get('resource_id')

                if not q_text or not subj:
                    continue

                # Check if identical question already exists for this faculty and subject
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

                cursor.execute(sql_q, (
                    res_id, q_text, subj, dept, year, sem,
                    un, top, q_type, diff, bloom, cpt,
                    un, exp, marks, status, in_bank, faculty_id
                ))
                q_id = cursor.lastrowid
                created_ids.append(q_id)"""

# 2. Replace save_to_question_bank
import re
new_save_fn = """def save_to_question_bank(faculty_id, data):
    \"\"\"
    Saves questions into Question Bank by setting is_in_bank = True and status = 'Bank'.
    Accepts payload with question_ids list or preview question objects array.
    \"\"\"
    raw_ids = data.get('question_ids') or []
    if isinstance(data.get('id'), (int, str)):
        raw_ids.append(data.get('id'))

    valid_db_ids = []
    for qid in raw_ids:
        if isinstance(qid, int) or (isinstance(qid, str) and str(qid).isdigit()):
            valid_db_ids.append(int(qid))

    raw_questions = data.get('questions') or []
    if not raw_questions and isinstance(data.get('question'), dict):
        raw_questions = [data.get('question')]

    new_questions = []
    for q in raw_questions:
        if isinstance(q, dict):
            q_id_val = q.get('id')
            if isinstance(q_id_val, int) or (isinstance(q_id_val, str) and str(q_id_val).isdigit()):
                valid_db_ids.append(int(q_id_val))
            else:
                new_questions.append(q)

    valid_db_ids = list(dict.fromkeys(valid_db_ids))
    all_saved_ids = []

    # If there are new questions to insert
    if new_questions:
        for q in new_questions:
            q['is_in_bank'] = True
            q['status'] = 'Bank'
        ok, res, code = create_questions_batch(faculty_id, new_questions)
        if not ok:
            return ok, res, code
        for created_q in res.get('questions', []):
            if created_q and created_q.get('id'):
                all_saved_ids.append(created_q['id'])

    # If there are existing DB IDs to update
    if valid_db_ids:
        try:
            conn = get_db_connection()
            conn.begin()
            with conn.cursor() as cursor:
                format_strings = ','.join(['%s'] * len(valid_db_ids))
                sql = f\"\"\"
                    UPDATE questions
                    SET is_in_bank = TRUE, status = 'Bank'
                    WHERE id IN ({format_strings}) AND created_by = %s
                \"\"\"
                cursor.execute(sql, tuple(valid_db_ids) + (faculty_id,))
            conn.commit()
            conn.close()
            all_saved_ids.extend(valid_db_ids)
        except Exception as e:
            logger.error(f"Error saving questions to bank: {str(e)}")
            if 'conn' in locals() and conn:
                conn.rollback()
                conn.close()
            return False, {"status": "error", "message": "Failed to save questions to bank."}, 500

    all_saved_ids = list(dict.fromkeys(all_saved_ids))
    if not all_saved_ids:
        return False, {"status": "error", "message": "Question IDs or question objects are required."}, 400

    saved_questions = [get_question_by_id(qid) for qid in all_saved_ids if get_question_by_id(qid)]
    return True, {
        "status": "success",
        "message": f"Successfully saved {len(all_saved_ids)} question(s) to Question Bank.",
        "saved_count": len(all_saved_ids),
        "questions": saved_questions
    }, 200
"""

save_fn_pattern = re.compile(r'def save_to_question_bank\(faculty_id, data\):[\s\S]*?(?=def remove_from_question_bank)', re.MULTILINE)

# Normalize CRLF
content_norm = content.replace("\r\n", "\n")
old_create_loop_norm = old_create_loop.replace("\r\n", "\n")
new_create_loop_norm = new_create_loop.replace("\r\n", "\n")

if old_create_loop_norm in content_norm:
    content_norm = content_norm.replace(old_create_loop_norm, new_create_loop_norm)
    print("MATCH: Updated create_questions_batch duplicate check")
else:
    print("WARN: create_questions_batch loop pattern not found")

content_norm, count = save_fn_pattern.subn(new_save_fn + "\n\n", content_norm)
print(f"MATCH: Updated save_to_question_bank ({count} substitution)")

with open(filepath, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(content_norm.replace("\n", "\r\n"))
print("Done writing question_service.py")
