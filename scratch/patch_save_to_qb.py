path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_func_start = text.find('def save_to_question_bank(faculty_id, data):')
old_func_end = text.find('def remove_from_question_bank', old_func_start)

new_func = '''def save_to_question_bank(faculty_id, data):
    """
    Saves questions into Question Bank by setting is_in_bank = True and status = 'Bank'.
    Accepts payload with question_ids list or preview question objects array.
    """
    raw_ids = data.get('question_ids') or []
    if isinstance(data.get('id'), (int, str)):
        raw_ids.append(data.get('id'))

    valid_db_ids = []
    for qid in raw_ids:
        if isinstance(qid, int) or (isinstance(qid, str) and qid.isdigit()):
            valid_db_ids.append(int(qid))

    # If question objects are passed
    if data.get('questions') and isinstance(data.get('questions'), list):
        for q in data.get('questions'):
            if isinstance(q, dict):
                q_id_val = q.get('id')
                if isinstance(q_id_val, int) or (isinstance(q_id_val, str) and str(q_id_val).isdigit()):
                    valid_db_ids.append(int(q_id_val))

    if not valid_db_ids:
        # If new preview question objects passed without DB integer IDs, insert them
        raw_questions = data.get('questions') or []
        if not raw_questions and isinstance(data.get('question'), dict):
            raw_questions = [data.get('question')]

        if raw_questions:
            for q in raw_questions:
                if isinstance(q, dict):
                    q['is_in_bank'] = True
                    q['status'] = 'Bank'
            ok, res, code = create_questions_batch(faculty_id, raw_questions)
            if not ok:
                return ok, res, code
            created_list = res.get('questions', [])
            return True, {
                "status": "success",
                "message": f"Successfully saved {len(created_list)} question(s) to Question Bank.",
                "saved_count": len(created_list),
                "questions": created_list
            }, 200
        else:
            return False, {"status": "error", "message": "Question IDs or question objects are required."}, 400

    try:
        conn = get_db_connection()
        conn.begin()
        with conn.cursor() as cursor:
            format_strings = ','.join(['%s'] * len(valid_db_ids))
            sql = f"""
                UPDATE questions
                SET is_in_bank = TRUE, status = 'Bank'
                WHERE id IN ({format_strings}) AND created_by = %s
            """
            cursor.execute(sql, tuple(valid_db_ids) + (faculty_id,))
        conn.commit()
        conn.close()

        return True, {
            "status": "success",
            "message": f"Successfully saved {len(valid_db_ids)} question(s) to Question Bank.",
            "saved_count": len(valid_db_ids)
        }, 200

    except Exception as e:
        logger.error(f"Error saving questions to bank: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, {"status": "error", "message": "Failed to save questions to Question Bank."}, 500

'''

text = text[:old_func_start] + new_func + text[old_func_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("save_to_question_bank updated successfully.")
