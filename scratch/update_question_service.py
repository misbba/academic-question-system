# Update backend/services/question_service.py for strict 2, 8, 16 marks
import os

WORKSPACE = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
SERVICE_PATH = os.path.join(WORKSPACE, "backend", "services", "question_service.py")

with open(SERVICE_PATH, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update create_question_record marks validation
if "marks_val = data.get('marks', 2)" not in code:
    target_create_marks = "    marks = int(data.get('marks', 2))"
    repl_create_marks = """    marks_val = data.get('marks', 2)
    try:
        marks = int(marks_val)
    except (ValueError, TypeError):
        return False, {"status": "error", "message": f"Marks must be an integer (2, 8, or 16), got '{marks_val}'."}, 400
    if marks not in (2, 8, 16):
        return False, {"status": "error", "message": f"Invalid marks: {marks}. Only 2, 8, and 16 marks are permitted."}, 400"""
    assert target_create_marks in code, "target_create_marks not found!"
    code = code.replace(target_create_marks, repl_create_marks, 1)
    print("Updated create_question_record marks validation")

# 2. Update create_questions_batch marks validation
if "marks_val = item.get('marks', 2)" not in code:
    target_batch_marks = "                marks = int(item.get('marks', 2))"
    repl_batch_marks = """                marks_val = item.get('marks', 2)
                try:
                    marks = int(marks_val)
                except (ValueError, TypeError):
                    conn.rollback()
                    return False, {"status": "error", "message": f"Question marks must be an integer (2, 8, or 16), got '{marks_val}'."}, 400
                if marks not in (2, 8, 16):
                    conn.rollback()
                    return False, {"status": "error", "message": f"Invalid marks: {marks}. Only 2, 8, and 16 marks are permitted."}, 400"""
    assert target_batch_marks in code, "target_batch_marks not found!"
    code = code.replace(target_batch_marks, repl_batch_marks, 1)
    print("Updated create_questions_batch marks validation")

# 3. Update update_question_record marks validation
if "if 'marks' in data and data['marks'] is not None:" not in code:
    target_update_marks = "    marks = int(data.get('marks', existing['marks']))"
    repl_update_marks = """    if 'marks' in data and data['marks'] is not None:
        try:
            marks = int(data['marks'])
        except (ValueError, TypeError):
            return False, {"status": "error", "message": f"Marks must be an integer (2, 8, or 16), got '{data['marks']}'."}, 400
        if marks not in (2, 8, 16):
            return False, {"status": "error", "message": f"Invalid marks: {marks}. Only 2, 8, and 16 marks are permitted."}, 400
    else:
        marks = existing['marks']"""
    assert target_update_marks in code, "target_update_marks not found!"
    code = code.replace(target_update_marks, repl_update_marks, 1)
    print("Updated update_question_record marks validation")

# 4. Update generate_questions_service marks check & QB fallback
if "req_marks = str(data.get('marks') or data.get('marks_per_question') or '').strip()" not in code:
    target_gen_q_start = "    use_qb = bool(data.get('use_question_bank', False))"
    repl_gen_q_start = """    use_qb = bool(data.get('use_question_bank', False))

    req_marks = str(data.get('marks') or data.get('marks_per_question') or '').strip()
    if req_marks and req_marks not in ('2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):
        return False, {"status": "error", "message": f"Invalid marks requested: '{req_marks}'. Only 2, 8, and 16 marks are supported."}, 400"""
    assert target_gen_q_start in code, "target_gen_q_start not found!"
    code = code.replace(target_gen_q_start, repl_gen_q_start, 1)
    print("Updated generate_questions_service marks check")

# QB fallback in generate_questions_service
old_source_marker = 'source_info = {\n\n            "syllabus_units": syllabus_units,\n\n            "notes_statements": notes_statements,\n\n            "question_bank_items": qb_rows if use_qb else [],\n\n            "has_uploaded_material": has_uploaded_material\n\n        }'
new_source_marker = '''if not has_uploaded_material and not syllabus_units and not notes_statements and qb_rows:
            has_uploaded_material = True
            for qb in qb_rows:
                u_name = qb.get('unit') or 'Unit 1'
                top = qb.get('topic') or qb.get('concept') or f"{subject} Core Principles"
                q_txt = qb.get('question_text') or ''
                notes_statements.append(f"{top}: {q_txt}")
                syllabus_units.append({
                    "unit_id": u_name.split('—')[0].strip(),
                    "unit_name": u_name,
                    "title": u_name,
                    "topics": [top],
                    "concepts": [top]
                })

        source_info = {
            "syllabus_units": syllabus_units,
            "notes_statements": notes_statements,
            "question_bank_items": qb_rows,
            "has_uploaded_material": has_uploaded_material
        }'''

# Replace source_info
code_norm = code.replace('\r\n', '\n')
if old_source_marker in code_norm:
    code_norm = code_norm.replace(old_source_marker, new_source_marker, 1)
    print("Updated source_info with QB fallback")
else:
    print("Warning: old_source_marker not found in code_norm")

# 5. Update generate_image_questions_service marks assignment
old_img_marker = """    # Marks per question based on type
    if 'short' in question_type.lower():
        marks_per_q = 2
    elif 'descriptive' in question_type.lower():
        marks_per_q = 16
    elif 'problem' in question_type.lower():
        marks_per_q = 8
    else:
        marks_per_q = 8

    generated_questions = []
    for i in range(count):
        tmpl = templates[i % len(templates)]
        q_diff = diff_pool[i]
        q_bloom = blooms_pool[i]
        q_type = question_type if question_type != 'Diagram Interpretation' or i == 0 else tmpl['type']"""

new_img_marker = """    req_marks = str(data.get('marks') or data.get('marks_per_question') or '').strip()
    if req_marks and req_marks not in ('2', '8', '16', 'Mixed', 'mixed', 'Balanced', 'balanced', 'all', 'ALL', ''):
        return False, {"status": "error", "message": f"Invalid marks requested: '{req_marks}'. Only 2, 8, and 16 marks are supported."}, 400

    generated_questions = []
    for i in range(count):
        if req_marks in ('2', '8', '16'):
            marks_per_q = int(req_marks)
        else:
            # Balanced mixed distribution: 40% 2M, 40% 8M, 20% 16M
            cut2 = max(1, round(count * 0.4))
            cut8 = max(cut2 + 1, round(count * 0.8))
            if i < cut2:
                marks_per_q = 2
            elif i < cut8:
                marks_per_q = 8
            else:
                marks_per_q = 16

        tmpl = templates[i % len(templates)]
        q_diff = diff_pool[i]
        q_bloom = blooms_pool[i]
        if marks_per_q == 2:
            q_type = "Concise Definition (2 Marks)"
        elif marks_per_q == 8:
            q_type = "Sequence Analysis (8 Marks)"
        else:
            q_type = "Comprehensive Architecture (16 Marks)" """

old_img_norm = old_img_marker.replace('\r\n', '\n')
new_img_norm = new_img_marker.replace('\r\n', '\n')
if old_img_norm in code_norm:
    code_norm = code_norm.replace(old_img_norm, new_img_norm, 1)
    print("Updated generate_image_questions_service marks assignment")
else:
    print("Warning: old_img_marker not found in code_norm")

with open(SERVICE_PATH, 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(code_norm)

print("Successfully updated backend/services/question_service.py!")
