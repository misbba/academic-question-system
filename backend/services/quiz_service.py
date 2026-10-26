import json
import logging
import uuid
from datetime import datetime
from models.database import get_db_connection, DatabaseError
from services.question_service import OFFICIAL_DEPARTMENTS

logger = logging.getLogger(__name__)

def format_quiz_dict(quiz_row):
    """
    Formats raw DB dictionary row into frontend-compatible quiz dictionary object.
    """
    if not quiz_row:
        return None

    questions = []
    if quiz_row.get('questions'):
        try:
            questions = json.loads(quiz_row['questions']) if isinstance(quiz_row['questions'], str) else quiz_row['questions']
        except Exception:
            questions = []
    if isinstance(questions, list):
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
                    q['options_strings'] = [o['text'] for o in clean_opts]

    created_at_str = ''
    if quiz_row.get('created_at'):
        if isinstance(quiz_row['created_at'], (datetime,)):
            created_at_str = quiz_row['created_at'].strftime('%d %b %Y')
            quiz_row['created_at'] = quiz_row['created_at'].isoformat()
        else:
            created_at_str = str(quiz_row['created_at'])

    if quiz_row.get('published_at') and isinstance(quiz_row['published_at'], (datetime,)):
        quiz_row['published_at'] = quiz_row['published_at'].isoformat()

    duration_mins = int(quiz_row.get('duration_minutes') or 10)
    marks_per_q = int(quiz_row['marks_per_question']) if quiz_row.get('marks_per_question') is not None else 1
    total_q = int(quiz_row.get('total_questions') or len(questions) or 5)
    total_marks = total_q * marks_per_q

    quiz_code = quiz_row.get('quiz_code') or f"QUIZ-2026-{quiz_row['id']:04d}"

    return {
        "id": quiz_row['id'],
        "quizId": quiz_code,
        "quiz_code": quiz_code,
        "title": quiz_row.get('title') or 'Academic Quiz',
        "subject": quiz_row['subject'],
        "department": quiz_row['department'],
        "academicYear": quiz_row.get('academic_year') or '2025-2026',
        "academic_year": quiz_row.get('academic_year') or '2025-2026',
        "semester": quiz_row.get('semester') or 'Semester 6',
        "unit": quiz_row.get('unit') or 'Unit III — SQL',
        "topic": quiz_row.get('topic') or 'General Topic',
        "quiz_type": quiz_row.get('quiz_type') or 'Multiple Choice Question',
        "blooms": quiz_row.get('blooms_level') or 'Understand',
        "difficulty": quiz_row.get('difficulty') or 'Mixed',
        "durationMins": duration_mins,
        "duration_minutes": duration_mins,
        "marksPerQuestion": marks_per_q,
        "marks_per_question": marks_per_q,
        "totalQuestions": total_q,
        "total_questions": total_q,
        "totalMarks": total_marks,
        "total_marks": total_marks,
        "status": quiz_row.get('status') or 'Published',
        "createdBy": quiz_row.get('faculty_name') or 'Faculty Member',
        "created_by": quiz_row.get('created_by'),
        "createdDate": created_at_str,
        "created_at": quiz_row.get('created_at'),
        "questions": questions
    }


def create_quiz_record(faculty_id, data):
    """
    Creates a new quiz record and its embedded questions in MySQL.
    """
    title = (data.get('title') or data.get('quizTitle') or '').strip()
    subject = (data.get('subject') or data.get('course') or '').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or data.get('academicYear') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit III — SQL').strip()
    topic = (data.get('topic') or 'General Topic').strip()
    quiz_type = (data.get('quiz_type') or data.get('type') or 'Multiple Choice Question').strip()
    blooms_level = (data.get('blooms_level') or data.get('blooms') or 'Understand').strip()
    difficulty = (data.get('difficulty') or 'Mixed').strip()
    duration_minutes = int(data.get('duration_minutes') or data.get('durationMins') or 10)
    marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')
    marks_per_question = int(marks_val) if marks_val is not None else 1
    if marks_per_question not in (1, 2, 8, 16):
        marks_per_question = 1
    status = (data.get('status') or 'Published').strip()

    questions = data.get('questions') or []
    if isinstance(questions, str):
        try:
            questions = json.loads(questions)
        except Exception:
            questions = []

    total_questions = int(data.get('total_questions') or data.get('totalQuestions') or len(questions) or 5)
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
                q['options_strings'] = [o['text'] for o in clean_opts]

    if not title:
        title = f"{subject} Quiz"
    if not subject:
        return False, {"status": "error", "message": "Subject is required."}, 400
    if not department:
        department = "General Engineering"

    quiz_code = data.get('quiz_code') or data.get('quizId') or f"QUIZ-2026-{uuid.uuid4().hex[:4].upper()}"
    questions_json = json.dumps(questions)

    try:
        conn = get_db_connection()
        conn.begin()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO quizzes
                (quiz_code, title, subject, department, academic_year, semester,
                 unit, topic, quiz_type, blooms_level, difficulty, duration_minutes,
                 marks_per_question, total_questions, questions, status, created_by, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            published_at = datetime.now() if status == 'Published' else None

            cursor.execute(sql, (
                quiz_code, title, subject, department, academic_year, semester,
                unit, topic, quiz_type, blooms_level, difficulty, duration_minutes,
                marks_per_question, total_questions, questions_json, status, faculty_id, published_at
            ))
            quiz_db_id = cursor.lastrowid

        conn.commit()
        conn.close()

        created_quiz = get_quiz_by_id(quiz_db_id)
        return True, {
            "status": "success",
            "message": "Quiz created successfully.",
            "quiz": created_quiz
        }, 201

    except Exception as e:
        logger.error(f"Error creating quiz record: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, {"status": "error", "message": "Failed to create quiz record."}, 500


def get_quizzes_list(user_id, role, filters=None):
    """
    Retrieves quizzes based on user role:
    - Faculty sees created/all quizzes
    - Student sees Published quizzes
    """
    filters = filters or {}
    params = []

    if role == 'student':
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.status = 'Published'"
    elif role == 'faculty':
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.created_by = %s"
        params.append(user_id)
    else:
        sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE 1=1"

    if filters.get('subject'):
        sql += " AND q.subject = %s"
        params.append(filters['subject'])
    if filters.get('department'):
        sql += " AND q.department = %s"
        params.append(filters['department'])
    if filters.get('semester'):
        sql += " AND q.semester = %s"
        params.append(filters['semester'])
    if filters.get('status'):
        sql += " AND q.status = %s"
        params.append(filters['status'])

    sql += " ORDER BY q.created_at DESC"

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
        conn.close()

        quizzes = [format_quiz_dict(row) for row in rows]
        return True, {
            "status": "success",
            "count": len(quizzes),
            "quizzes": quizzes
        }, 200

    except Exception as e:
        logger.error(f"Error fetching quizzes list: {str(e)}")
        return False, {"status": "error", "message": "Failed to fetch quizzes."}, 500


def get_quiz_by_id(quiz_id, user_id=None, role=None):
    """
    Retrieves a single quiz by ID or quiz_code.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            if str(quiz_id).isdigit():
                sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.id = %s"
                cursor.execute(sql, (int(quiz_id),))
            else:
                sql = "SELECT q.*, u.full_name as faculty_name FROM quizzes q LEFT JOIN users u ON q.created_by = u.id WHERE q.quiz_code = %s"
                cursor.execute(sql, (str(quiz_id),))

            row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Check role permission
        if role == 'student' and row['status'] != 'Published':
            return None
        if role == 'faculty' and user_id is not None and row.get('created_by') != user_id:
            return None

        return format_quiz_dict(row)

    except Exception as e:
        logger.error(f"Error fetching quiz by ID: {str(e)}")
        return None


def update_quiz_record(quiz_id, faculty_id, data):
    """
    Updates an existing quiz record owned by faculty.
    """
    existing_quiz = get_quiz_by_id(quiz_id)
    if not existing_quiz:
        return False, {"status": "error", "message": "Quiz not found."}, 404
    if existing_quiz['created_by'] != faculty_id:
        return False, {"status": "error", "message": "Forbidden. You can only update your own quizzes."}, 403

    db_id = existing_quiz['id']

    title = (data.get('title') or data.get('quizTitle') or existing_quiz['title']).strip()
    subject = (data.get('subject') or existing_quiz['subject']).strip()
    department = (data.get('department') or existing_quiz['department']).strip()
    academic_year = (data.get('academic_year') or existing_quiz['academic_year']).strip()
    semester = (data.get('semester') or existing_quiz['semester']).strip()
    unit = (data.get('unit') or existing_quiz['unit']).strip()
    topic = (data.get('topic') or existing_quiz['topic']).strip()
    quiz_type = (data.get('quiz_type') or existing_quiz['quiz_type']).strip()
    blooms_level = (data.get('blooms_level') or existing_quiz['blooms']).strip()
    difficulty = (data.get('difficulty') or existing_quiz['difficulty']).strip()
    duration_minutes = int(data.get('duration_minutes') or existing_quiz['duration_minutes'])
    marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')
    if marks_val is not None:
        marks_per_question = int(marks_val)
    else:
        marks_per_question = int(existing_quiz.get('marks_per_question') if existing_quiz.get('marks_per_question') is not None else 1)
    status = (data.get('status') or existing_quiz['status']).strip()

    questions = data.get('questions') if data.get('questions') is not None else existing_quiz['questions']
    if isinstance(questions, str):
        try:
            questions = json.loads(questions)
        except Exception:
            questions = []

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
                q['options_strings'] = [o['text'] for o in clean_opts]

    total_questions = int(data.get('total_questions') or len(questions) or existing_quiz['total_questions'])
    questions_json = json.dumps(questions)

    try:
        conn = get_db_connection()
        conn.begin()
        with conn.cursor() as cursor:
            sql = """
                UPDATE quizzes
                SET title = %s, subject = %s, department = %s, academic_year = %s,
                    semester = %s, unit = %s, topic = %s, quiz_type = %s,
                    blooms_level = %s, difficulty = %s, duration_minutes = %s,
                    marks_per_question = %s, total_questions = %s, questions = %s,
                    status = %s, published_at = %s
                WHERE id = %s AND created_by = %s
            """
            published_at = datetime.now() if status == 'Published' else None

            cursor.execute(sql, (
                title, subject, department, academic_year,
                semester, unit, topic, quiz_type,
                blooms_level, difficulty, duration_minutes,
                marks_per_question, total_questions, questions_json,
                status, published_at, db_id, faculty_id
            ))

        conn.commit()
        conn.close()

        updated_quiz = get_quiz_by_id(db_id)
        return True, {
            "status": "success",
            "message": "Quiz updated successfully.",
            "quiz": updated_quiz
        }, 200

    except Exception as e:
        logger.error(f"Error updating quiz: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, {"status": "error", "message": "Failed to update quiz record."}, 500


def delete_quiz_record(quiz_id, faculty_id):
    """
    Deletes a quiz record owned by faculty.
    """
    existing_quiz = get_quiz_by_id(quiz_id)
    if not existing_quiz:
        return False, {"status": "error", "message": "Quiz not found."}, 404
    if existing_quiz['created_by'] != faculty_id:
        return False, {"status": "error", "message": "Forbidden. You can only delete your own quizzes."}, 403

    db_id = existing_quiz['id']

    try:
        conn = get_db_connection()
        conn.begin()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM quizzes WHERE id = %s AND created_by = %s", (db_id, faculty_id))
        conn.commit()
        conn.close()

        return True, {
            "status": "success",
            "message": "Quiz deleted successfully."
        }, 200

    except Exception as e:
        logger.error(f"Error deleting quiz: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, {"status": "error", "message": "Failed to delete quiz record."}, 500


def submit_student_quiz_attempt(student_id, quiz_id, data):
    """
    Auto-scores student quiz attempt, generates concept performance, and stores attempt in MySQL quiz_attempts table.
    """
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return False, {"status": "error", "message": "Quiz not found."}, 404

    answers = data.get('answers') or {}
    questions = quiz.get('questions') or []
    marks_per_q = int(quiz.get('marksPerQuestion') if quiz.get('marksPerQuestion') is not None else (quiz.get('marks_per_question') if quiz.get('marks_per_question') is not None else 1))

    correct_count = 0
    total_count = len(questions)
    concept_perf = {}

    for idx, q in enumerate(questions):
        concept = q.get('concept') or 'General'
        correct_idx = q.get('correctIndex') if q.get('correctIndex') is not None else q.get('correct_index')
        if correct_idx is None:
            ca = q.get('correctAnswer') or q.get('correct_answer') or q.get('answer')
            if ca is not None:
                ca_str = str(ca).strip().upper()
                if ca_str == 'A' or ca_str.startswith('A') or 'OPTION A' in ca_str: correct_idx = 0
                elif ca_str == 'B' or ca_str.startswith('B') or 'OPTION B' in ca_str: correct_idx = 1
                elif ca_str == 'C' or ca_str.startswith('C') or 'OPTION C' in ca_str: correct_idx = 2
                elif ca_str == 'D' or ca_str.startswith('D') or 'OPTION D' in ca_str: correct_idx = 3
                elif ca_str.isdigit(): correct_idx = int(ca_str)

        chosen_val = answers.get(str(idx)) if answers.get(str(idx)) is not None else answers.get(idx)
        chosen_idx = None
        if chosen_val is not None:
            if str(chosen_val).isdigit():
                chosen_idx = int(chosen_val)
            else:
                cv = str(chosen_val).strip().upper()
                if cv.startswith('A'): chosen_idx = 0
                elif cv.startswith('B'): chosen_idx = 1
                elif cv.startswith('C'): chosen_idx = 2
                elif cv.startswith('D'): chosen_idx = 3

        is_right = False
        if chosen_idx is not None and correct_idx is not None:
            if chosen_idx == correct_idx:
                is_right = True
                correct_count += 1

        concept_perf[concept] = is_right

    score = correct_count * marks_per_q
    total_marks = total_count * marks_per_q
    percentage = f"{round((correct_count / total_count) * 100) if total_count else 0}%"

    answers_json = json.dumps(answers)
    concept_perf_json = json.dumps(concept_perf)

    try:
        conn = get_db_connection()
        conn.begin()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO quiz_attempts
                (quiz_id, student_id, score, total_marks, total_questions, percentage,
                 answers_json, concept_performance_json, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                quiz['id'], student_id, score, total_marks, total_count,
                percentage, answers_json, concept_perf_json, 'Completed'
            ))
            attempt_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return True, {
            "status": "success",
            "message": "Quiz attempt submitted and evaluated successfully.",
            "score": score,
            "total_marks": total_marks,
            "percentage": percentage,
            "attempt": {
                "id": attempt_id,
                "quizId": quiz['quizId'],
                "title": quiz['title'],
                "subject": quiz['subject'],
                "score": f"{score} / {total_marks}",
                "correct": correct_count,
                "total": total_count,
                "percentage": percentage,
                "date": datetime.now().strftime('%d %b %Y'),
                "conceptPerformance": concept_perf
            }
        }, 201

    except Exception as e:
        logger.error(f"Error recording quiz attempt: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
            conn.close()
        return False, {"status": "error", "message": "Failed to record quiz attempt."}, 500


def get_student_quiz_attempts(student_id=None, role=None, faculty_id=None):
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
            elif student_id:
                sql = """
                    SELECT qa.*, q.title as quiz_title, q.subject as quiz_subject, q.quiz_code,
                           u.full_name as student_name, u.email as student_email
                    FROM quiz_attempts qa
                    JOIN quizzes q ON qa.quiz_id = q.id
                    LEFT JOIN users u ON qa.student_id = u.id
                    WHERE qa.student_id = %s
                    ORDER BY qa.completed_at DESC
                """
                cursor.execute(sql, (student_id,))
            else:
                sql = """
                    SELECT qa.*, q.title as quiz_title, q.subject as quiz_subject, q.quiz_code,
                           u.full_name as student_name, u.email as student_email
                    FROM quiz_attempts qa
                    JOIN quizzes q ON qa.quiz_id = q.id
                    LEFT JOIN users u ON qa.student_id = u.id
                    ORDER BY qa.completed_at DESC
                """
                cursor.execute(sql)

            rows = cursor.fetchall()
        conn.close()

        attempts = []
        for r in rows:
            c_perf = {}
            if r.get('concept_performance_json'):
                try:
                    c_perf = json.loads(r['concept_performance_json'])
                except Exception:
                    c_perf = {}

            completed_date = ''
            if r.get('completed_at'):
                if isinstance(r['completed_at'], (datetime,)):
                    completed_date = r['completed_at'].strftime('%d %b %Y')
                else:
                    completed_date = str(r['completed_at'])

            attempts.append({
                "id": r['id'],
                "quizId": r.get('quiz_code') or f"QUIZ-{r['quiz_id']}",
                "title": r.get('quiz_title') or 'Academic Quiz',
                "subject": r.get('quiz_subject') or 'General Subject',
                "studentName": r.get('student_name') or 'Student',
                "studentEmail": r.get('student_email') or '',
                "score": f"{r['score']} / {r['total_marks']}",
                "correct": r['score'],
                "total": r['total_questions'],
                "percentage": r['percentage'],
                "date": completed_date,
                "conceptPerformance": c_perf
            })

        return True, {
            "status": "success",
            "count": len(attempts),
            "attempts": attempts
        }, 200

    except Exception as e:
        logger.error(f"Error fetching quiz attempts: {str(e)}")
        return False, {"status": "error", "message": "Failed to fetch quiz attempts."}, 500


import os
from utils.document_parser import (
    extract_text_from_file,
    parse_syllabus,
    parse_notes_content,
    generate_grounded_questions
)

def build_quiz_ai_prompt(config):
    """
    Constructs explicit AI prompt for Quiz Generation specifying 1-mark objective questions.
    """
    subject = (config.get('subject') or 'Academic Course').strip()
    department = (config.get('department') or 'General Engineering').strip()
    unit = (config.get('unit') or 'All Units').strip()
    topic = (config.get('topic') or 'Complete Syllabus').strip()
    num_questions = int(config.get('total_questions') or config.get('num_questions') or 30)
    marks_per_q = int(config.get('marks_per_question') or config.get('marksPerQuestion') or 1)
    duration = int(config.get('duration_minutes') or config.get('durationMins') or 30)

    return (
        f"You are an academic course examiner. Generate {num_questions} objective multiple-choice questions (MCQs) "
        f"for the course '{subject}' ({department}).\n"
        f"Unit: {unit}\n"
        f"Topic: {topic}\n"
        f"Assessment Duration: {duration} Minutes\n\n"
        f"CRITICAL MARKS & EVALUATION SPECIFICATION:\n"
        f"- Each quiz question must be worth exactly {marks_per_q} mark ({marks_per_q} {'Mark' if marks_per_q == 1 else 'Marks'} per question).\n"
        f"- Total assessment marks: {num_questions * marks_per_q} Marks ({num_questions} questions x {marks_per_q} mark).\n"
        f"- Question Format: 4 distinct options (A, B, C, D) with exactly one verified correct answer.\n"
        f"- Scope: Concise, objective conceptual questions tailored to {marks_per_q}-mark evaluation."
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
    marks_val = data.get('marks_per_question') if data.get('marks_per_question') is not None else data.get('marksPerQuestion')
    marks_per_q = int(marks_val) if marks_val is not None else 1
    total_q = int(data.get('total_questions') or data.get('totalQuestions') or 30)

    data['duration_minutes'] = duration_mins
    data['marks_per_question'] = marks_per_q
    data['marks'] = marks_per_q
    data['num_questions'] = total_q
    data['difficulty'] = data.get('difficulty') or 'Mixed'
    data['bloom_level'] = data.get('blooms_level') or data.get('bloom_level') or 'Auto Select'
    data['question_type'] = 'Multiple Choice Question'
    data['is_quiz'] = True
    ai_prompt = build_quiz_ai_prompt(data)

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
                        res_rows = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM questions WHERE created_by = %s AND is_in_bank = 1 AND (subject = %s OR subject LIKE %s)",
                (faculty_id, subject, f"%{subject}%")
            )
            qb_rows = cursor.fetchall()

        conn.close()

        raw_documents = []
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
            "ai_prompt": ai_prompt,
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
