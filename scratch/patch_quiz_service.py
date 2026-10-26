import os

path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\quiz_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update get_quizzes_list isolation
old_clause = '''    if role == 'student':
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.status = 'Published'"
    else:
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE 1=1"'''

new_clause = '''    if role == 'student':
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.status = 'Published'"
    elif role == 'faculty':
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.created_by = %s"
        params.append(user_id)
    else:
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE 1=1"'''

if old_clause in content:
    content = content.replace(old_clause, new_clause, 1)

# 2. Update get_student_quiz_attempts signature and isolation
old_attempts = '''def get_student_quiz_attempts(student_id=None):
    """
    Retrieves student quiz attempts from MySQL quiz_attempts table.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if student_id:'''

new_attempts = '''def get_student_quiz_attempts(student_id=None, role=None, faculty_id=None):
    """
    Retrieves student quiz attempts from MySQL quiz_attempts table with faculty/student isolation.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if role == 'faculty' or faculty_id:
                fid = faculty_id or (student_id if role == 'faculty' else None)
                sql = """
                    SELECT qa.*, q.title as quiz_title, q.subject as quiz_subject, q.quiz_code,
                           u.full_name as student_name, u.email as student_email
                    FROM quiz_attempts qa
                    JOIN quizzes q ON qa.quiz_id = q.id
                    LEFT JOIN users u ON qa.student_id = u.id
                    WHERE q.created_by = %s
                    ORDER BY qa.completed_at DESC
                """
                cursor.execute(sql, (fid,))
            elif student_id:'''

if old_attempts in content:
    content = content.replace(old_attempts, new_attempts, 1)

# 3. Append generate_quiz_service
quiz_gen_func = '''

import os
from utils.document_parser import (
    extract_text_from_file,
    parse_syllabus,
    parse_notes_content,
    generate_grounded_questions
)

def generate_quiz_service(faculty_id, data):
    """
    Generates preview quiz questions (MCQs) for faculty member using uploaded study materials,
    syllabus, or question bank. Default: 30 minutes, 30 marks (30 questions x 1 mark).
    """
    subject = (data.get('subject') or '').strip()
    if not subject:
        return False, {"status": "error", "message": "Subject name is required."}, 400

    department = (data.get('department') or 'General Engineering').strip()
    resource_id = data.get('resource_id')
    syllabus_id = data.get('syllabus_id')
    notes_id = data.get('notes_id')
    use_qb = bool(data.get('use_question_bank', False))

    duration_mins = int(data.get('duration_minutes') or data.get('durationMins') or 30)
    marks_per_q = int(data.get('marks_per_question') or data.get('marksPerQuestion') or 1)
    total_q = int(data.get('total_questions') or data.get('totalQuestions') or 30)

    data['duration_minutes'] = duration_mins
    data['marks_per_question'] = marks_per_q
    data['num_questions'] = total_q
    data['question_type'] = 'Multiple Choice Question'
    data['is_quiz'] = True

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    syllabus_units = []
    notes_statements = []
    has_uploaded_material = False

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if resource_id:
                cursor.execute(
                    "SELECT * FROM academic_resources WHERE id = %s AND created_by = %s",
                    (resource_id, faculty_id)
                )
                res_rows = cursor.fetchall()
            elif syllabus_id or notes_id:
                ids = [i for i in [syllabus_id, notes_id] if i]
                format_strings = ','.join(['%s'] * len(ids))
                cursor.execute(
                    f"SELECT * FROM academic_resources WHERE id IN ({format_strings}) AND created_by = %s",
                    tuple(ids) + (faculty_id,)
                )
                res_rows = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT * FROM academic_resources WHERE created_by = %s AND (subject = %s OR subject LIKE %s)",
                    (faculty_id, subject, f"%{subject}%")
                )
                res_rows = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM questions WHERE created_by = %s AND is_in_bank = 1 AND (subject = %s OR subject LIKE %s)",
                (faculty_id, subject, f"%{subject}%")
            )
            qb_rows = cursor.fetchall()

        conn.close()

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
        }

        gen_result = generate_grounded_questions(source_info, data)
        if gen_result.get('status') == 'error':
            return False, gen_result, 400

        total_marks = len(gen_result.get('questions', [])) * marks_per_q

        quiz_preview = {
            "title": data.get('title') or data.get('quizTitle') or f"{subject} Timed Assessment Quiz",
            "subject": subject,
            "department": department,
            "academic_year": data.get('academic_year', '2025-2026'),
            "semester": data.get('semester', 'Semester 6'),
            "unit": data.get('unit', 'All Units (Complete Syllabus)'),
            "topic": data.get('topic', 'Complete Syllabus Coverage'),
            "duration_minutes": duration_mins,
            "durationMins": duration_mins,
            "marks_per_question": marks_per_q,
            "marksPerQuestion": marks_per_q,
            "total_questions": len(gen_result.get('questions', [])),
            "totalQuestions": len(gen_result.get('questions', [])),
            "total_marks": total_marks,
            "totalMarks": total_marks,
            "status": "Published",
            "questions": gen_result.get('questions', [])
        }

        return True, {
            "status": "success",
            "message": f"Successfully generated {len(gen_result.get('questions', []))} quiz questions for {subject}.",
            "quiz": quiz_preview,
            "questions": gen_result.get('questions', [])
        }, 200

    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return False, {"status": "error", "message": f"Failed to generate quiz: {str(e)}"}, 500
'''

if "def generate_quiz_service" not in content:
    content += quiz_gen_func

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('quiz_service.py successfully patched and verified.')
