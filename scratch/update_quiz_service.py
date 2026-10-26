with open('backend/services/quiz_service.py', 'r', encoding='utf-8') as f:
    orig = f.read().replace('\r\n', '\n')

# 1. Update format_quiz_dict to sanitize options
old_format_q = """    if isinstance(questions, list):
        for q in questions:
            if isinstance(q, dict):
                if 'marks' not in q or q['marks'] is None:
                    q['marks'] = int(quiz_row.get('marks_per_question') or 1)
                if 'marks_per_question' not in q or q['marks_per_question'] is None:
                    q['marks_per_question'] = q['marks']"""

new_format_q = """    if isinstance(questions, list):
        for q in questions:
            if isinstance(q, dict):
                if 'marks' not in q or q['marks'] is None:
                    q['marks'] = int(quiz_row.get('marks_per_question') or 1)
                if 'marks_per_question' not in q or q['marks_per_question'] is None:
                    q['marks_per_question'] = q['marks']
                if 'options' in q and isinstance(q['options'], list):
                    clean_opts = []
                    for opt_idx, opt in enumerate(q['options']):
                        if isinstance(opt, dict):
                            txt = opt.get('text') or opt.get('option_text') or ''
                            if txt == '[object Object]' or not txt:
                                txt = f"Option {chr(65 + opt_idx)}"
                            clean_opts.append({
                                "label": opt.get('label') or chr(65 + opt_idx),
                                "option_label": opt.get('label') or chr(65 + opt_idx),
                                "text": txt,
                                "option_text": txt,
                                "is_correct": bool(opt.get('is_correct', False) or (opt_idx == q.get('correctIndex')))
                            })
                        elif isinstance(opt, str):
                            txt = opt if opt != '[object Object]' else f"Option {chr(65 + opt_idx)}"
                            clean_opts.append({
                                "label": chr(65 + opt_idx),
                                "option_label": chr(65 + opt_idx),
                                "text": txt,
                                "option_text": txt,
                                "is_correct": bool(opt_idx == q.get('correctIndex'))
                            })
                    q['options'] = clean_opts
                    q['options_strings'] = [o['text'] for o in clean_opts]"""

assert old_format_q in orig, "old_format_q must be in quiz_service.py!"
updated = orig.replace(old_format_q, new_format_q, 1)

# 2. Update create_quiz_record to sanitize options
old_create_q = """    total_questions = int(data.get('total_questions') or data.get('totalQuestions') or len(questions) or 5)
    for q in questions:
        if isinstance(q, dict):
            if 'marks' not in q or q['marks'] is None:
                q['marks'] = marks_per_question
            if 'marks_per_question' not in q or q['marks_per_question'] is None:
                q['marks_per_question'] = marks_per_question"""

new_create_q = """    total_questions = int(data.get('total_questions') or data.get('totalQuestions') or len(questions) or 5)
    for q in questions:
        if isinstance(q, dict):
            if 'marks' not in q or q['marks'] is None:
                q['marks'] = marks_per_question
            if 'marks_per_question' not in q or q['marks_per_question'] is None:
                q['marks_per_question'] = marks_per_question
            if 'options' in q and isinstance(q['options'], list):
                clean_opts = []
                for opt_idx, opt in enumerate(q['options']):
                    if isinstance(opt, dict):
                        txt = opt.get('text') or opt.get('option_text') or ''
                        if txt == '[object Object]' or not txt:
                            txt = f"Option {chr(65 + opt_idx)}"
                        clean_opts.append({
                            "label": opt.get('label') or chr(65 + opt_idx),
                            "option_label": opt.get('label') or chr(65 + opt_idx),
                            "text": txt,
                            "option_text": txt,
                            "is_correct": bool(opt.get('is_correct', False) or (opt_idx == q.get('correctIndex')))
                        })
                    elif isinstance(opt, str):
                        txt = opt if opt != '[object Object]' else f"Option {chr(65 + opt_idx)}"
                        clean_opts.append({
                            "label": chr(65 + opt_idx),
                            "option_label": chr(65 + opt_idx),
                            "text": txt,
                            "option_text": txt,
                            "is_correct": bool(opt_idx == q.get('correctIndex'))
                        })
                q['options'] = clean_opts
                q['options_strings'] = [o['text'] for o in clean_opts]"""

assert old_create_q in updated, "old_create_q must be in quiz_service.py!"
updated = updated.replace(old_create_q, new_create_q, 1)

# 3. Update update_quiz_record to sanitize options
old_update_q = """    for q in questions:
        if isinstance(q, dict):
            if 'marks' not in q or q['marks'] is None:
                q['marks'] = marks_per_question
            if 'marks_per_question' not in q or q['marks_per_question'] is None:
                q['marks_per_question'] = marks_per_question

    total_questions = int(data.get('total_questions') or len(questions) or existing_quiz['total_questions'])"""

new_update_q = """    for q in questions:
        if isinstance(q, dict):
            if 'marks' not in q or q['marks'] is None:
                q['marks'] = marks_per_question
            if 'marks_per_question' not in q or q['marks_per_question'] is None:
                q['marks_per_question'] = marks_per_question
            if 'options' in q and isinstance(q['options'], list):
                clean_opts = []
                for opt_idx, opt in enumerate(q['options']):
                    if isinstance(opt, dict):
                        txt = opt.get('text') or opt.get('option_text') or ''
                        if txt == '[object Object]' or not txt:
                            txt = f"Option {chr(65 + opt_idx)}"
                        clean_opts.append({
                            "label": opt.get('label') or chr(65 + opt_idx),
                            "option_label": opt.get('label') or chr(65 + opt_idx),
                            "text": txt,
                            "option_text": txt,
                            "is_correct": bool(opt.get('is_correct', False) or (opt_idx == q.get('correctIndex')))
                        })
                    elif isinstance(opt, str):
                        txt = opt if opt != '[object Object]' else f"Option {chr(65 + opt_idx)}"
                        clean_opts.append({
                            "label": chr(65 + opt_idx),
                            "option_label": chr(65 + opt_idx),
                            "text": txt,
                            "option_text": txt,
                            "is_correct": bool(opt_idx == q.get('correctIndex'))
                        })
                q['options'] = clean_opts
                q['options_strings'] = [o['text'] for o in clean_opts]

    total_questions = int(data.get('total_questions') or len(questions) or existing_quiz['total_questions'])"""

assert old_update_q in updated, "old_update_q must be in quiz_service.py!"
updated = updated.replace(old_update_q, new_update_q, 1)

# 4. Update generate_quiz_service resource query and raw_documents collection
old_gen_res = """            else:
                cursor.execute(
                    "SELECT * FROM academic_resources WHERE created_by = %s AND (subject = %s OR subject LIKE %s)",
                    (faculty_id, subject, f"%{subject}%")
                )
                res_rows = cursor.fetchall()"""

new_gen_res = """            else:
                cursor.execute(
                    "SELECT * FROM academic_resources WHERE created_by = %s AND (subject = %s OR subject LIKE %s OR %s LIKE CONCAT('%%', subject, '%%'))",
                    (faculty_id, subject, f"%{subject}%", subject)
                )
                res_rows = cursor.fetchall()
                if not res_rows and len(subject.split()) > 0:
                    first_token = subject.split()[0].strip()
                    if len(first_token) >= 4:
                        cursor.execute(
                            "SELECT * FROM academic_resources WHERE created_by = %s AND (subject LIKE %s OR title LIKE %s)",
                            (faculty_id, f"%{first_token}%", f"%{first_token}%")
                        )
                        res_rows = cursor.fetchall()"""

assert old_gen_res in updated, "old_gen_res must be in quiz_service.py!"
updated = updated.replace(old_gen_res, new_gen_res, 1)

old_source_coll = """        for r in res_rows:
            f_path = r.get('file_path')
            raw_text = ""
            if f_path:
                abs_f_path = os.path.join(root_dir, f_path)
                if not os.path.exists(abs_f_path):
                    abs_f_path = os.path.join(root_dir, 'uploads', 'resources', os.path.basename(f_path))
                raw_text = extract_text_from_file(abs_f_path)

            if not raw_text and r.get('description'):
                raw_text = r['description']

            r_type = (r.get('resource_type') or '').lower()
            if raw_text:
                has_uploaded_material = True
                if 'syllabus' in r_type or 'curriculum' in r_type:
                    parsed_u = parse_syllabus(raw_text, subject)
                    if parsed_u:
                        syllabus_units.extend(parsed_u)
                else:
                    parsed_notes = parse_notes_content(raw_text)
                    notes_statements.extend(parsed_notes)
                    parsed_u = parse_syllabus(raw_text, subject)
                    if parsed_u:
                        syllabus_units.extend(parsed_u)

        source_info = {
            "syllabus_units": syllabus_units,
            "notes_statements": notes_statements,
            "question_bank_items": qb_rows if use_qb else [],
            "has_uploaded_material": has_uploaded_material
        }"""

new_source_coll = """        raw_documents = []
        for r in res_rows:
            f_path = r.get('file_path')
            raw_text = ""
            if f_path:
                abs_f_path = os.path.join(root_dir, f_path)
                if not os.path.exists(abs_f_path):
                    abs_f_path = os.path.join(root_dir, 'uploads', 'resources', os.path.basename(f_path))
                raw_text = extract_text_from_file(abs_f_path)

            if not raw_text and r.get('description'):
                raw_text = r['description']

            r_type = (r.get('resource_type') or '').lower()
            if raw_text:
                has_uploaded_material = True
                raw_documents.append(raw_text)
                if 'syllabus' in r_type or 'curriculum' in r_type:
                    parsed_u = parse_syllabus(raw_text, subject)
                    if parsed_u:
                        syllabus_units.extend(parsed_u)
                else:
                    parsed_notes = parse_notes_content(raw_text)
                    notes_statements.extend(parsed_notes)
                    parsed_u = parse_syllabus(raw_text, subject)
                    if parsed_u:
                        syllabus_units.extend(parsed_u)

        source_info = {
            "syllabus_units": syllabus_units,
            "notes_statements": notes_statements,
            "raw_documents": raw_documents,
            "question_bank_items": qb_rows if use_qb else [],
            "has_uploaded_material": has_uploaded_material
        }"""

assert old_source_coll in updated, "old_source_coll must be in quiz_service.py!"
updated = updated.replace(old_source_coll, new_source_coll, 1)

# 5. Set difficulty and bloom_level in data before calling generate_grounded_questions
old_gen_cfg = """    data['duration_minutes'] = duration_mins
    data['marks_per_question'] = marks_per_q
    data['marks'] = marks_per_q
    data['num_questions'] = total_q
    data['question_type'] = 'Multiple Choice Question'
    data['is_quiz'] = True
    ai_prompt = build_quiz_ai_prompt(data)"""

new_gen_cfg = """    data['duration_minutes'] = duration_mins
    data['marks_per_question'] = marks_per_q
    data['marks'] = marks_per_q
    data['num_questions'] = total_q
    data['difficulty'] = data.get('difficulty') or 'Mixed'
    data['bloom_level'] = data.get('blooms_level') or data.get('bloom_level') or 'Auto Select'
    data['question_type'] = 'Multiple Choice Question'
    data['is_quiz'] = True
    ai_prompt = build_quiz_ai_prompt(data)"""

assert old_gen_cfg in updated, "old_gen_cfg must be in quiz_service.py!"
updated = updated.replace(old_gen_cfg, new_gen_cfg, 1)

with open('backend/services/quiz_service.py', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(updated)

print("quiz_service.py updated successfully!")
