from flask import Blueprint, request, jsonify, session
from services.auth_service import register_user, authenticate_user, get_user_by_id, reset_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Registers a new Faculty or Student user in the MySQL database.
    """
    data = request.get_json(silent=True) or {}
    success, result, status_code = register_user(data)
    return jsonify(result), status_code

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Authenticates a user against MySQL and establishes a Flask server session.
    """
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    password = data.get('password', '')
    role = data.get('role', '')

    success, result, status_code = authenticate_user(email, password, role)
    
    if success:
        user_profile = result.get('user', {})
        # Store user session on Flask server
        session['user_id'] = user_profile.get('id')
        session['role'] = user_profile.get('role')
        session['full_name'] = user_profile.get('full_name')
        session['email'] = user_profile.get('email')

    return jsonify(result), status_code

@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """
    GET /api/auth/me
    Returns current authenticated user profile based on server session.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            "status": "error",
            "authenticated": False,
            "message": "Authentication required"
        }), 401

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({
            "status": "error",
            "authenticated": False,
            "message": "User session invalid or user deleted"
        }), 401

    return jsonify({
        "status": "success",
        "authenticated": True,
        "user": user
    }), 200

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    POST /api/auth/logout
    Clears current Flask server session.
    """
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Logged out successfully"
    }), 200

@auth_bp.route('/api/auth/status', methods=['GET'])
def auth_status():
    """
    GET /api/auth/status
    Provides authentication API status and current session status.
    """
    user_id = session.get('user_id')
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return jsonify({
                "status": "success",
                "authenticated": True,
                "message": "Authentication API ready",
                "user": {
                    "id": user['id'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            }), 200

    return jsonify({
        "status": "success",
        "authenticated": False,
        "message": "Authentication API is ready"
    }), 200

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password_route():
    """
    POST /api/auth/reset-password
    Validates identity and updates password in MySQL.
    """
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    role = data.get('role', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    success, result, status_code = reset_password(email, role, new_password, confirm_password)
    return jsonify(result), status_code


def get_course_code_for_subject(subject):
    s = (subject or '').strip()
    mapping = {
        'database management systems': 'CS301',
        'dbms': 'CS301',
        'machine learning': 'AI401',
        'ml': 'AI401',
        'data structures & algorithms': 'CS302',
        'data structures': 'CS302',
        'computer networks': 'CC304',
        'artificial intelligence': 'AI301',
        'web technology': 'IT303',
        'operating systems': 'CS304'
    }
    if s.lower() in mapping:
        return mapping[s.lower()]
    words = [w for w in s.split() if w.isalpha()]
    if words:
        acronym = ''.join(w[0].upper() for w in words[:3])
        return f"{acronym}301" if len(acronym) >= 2 else f"CS{abs(hash(s)) % 800 + 100}"
    return "CS301"


@auth_bp.route('/api/faculty/dashboard-stats', methods=['GET'])
def faculty_dashboard_stats():
    """
    GET /api/faculty/dashboard-stats
    Retrieves real real-time counts and metrics from MySQL database
    strictly isolated for the authenticated faculty member's dashboard.
    """
    import json
    from datetime import datetime
    from collections import Counter
    from models.database import get_db_connection

    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Faculty role required."}), 403

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 1. Total questions created by this faculty in question bank
            cursor.execute("SELECT COUNT(*) AS cnt FROM questions WHERE created_by = %s AND is_in_bank = 1", (user_id,))
            total_questions = cursor.fetchone()['cnt'] or 0

            # 2. Active courses for this faculty
            cursor.execute("""
                SELECT subject, 
                       MAX(department) as department, 
                       MAX(academic_year) as academic_year, 
                       MAX(semester) as semester, 
                       COUNT(*) as item_count
                FROM (
                    SELECT subject, department, academic_year, semester FROM questions WHERE created_by = %s AND is_in_bank = 1 AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM academic_resources WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM question_papers WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM quizzes WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                ) AS s
                GROUP BY subject
                ORDER BY subject ASC
            """, (user_id, user_id, user_id, user_id))
            course_rows = cursor.fetchall() or []
            courses_list = []
            for r in course_rows:
                courses_list.append({
                    "course_name": r['subject'],
                    "course_code": get_course_code_for_subject(r['subject']),
                    "department": r.get('department') or 'Artificial Intelligence & Data Science',
                    "semester": r.get('semester') or 'Semester 6',
                    "academic_year": r.get('academic_year') or '2025-2026',
                    "item_count": r.get('item_count', 0),
                    "status": "Active"
                })
            active_courses = len(courses_list)

            # 3. Draft papers created by this faculty
            cursor.execute("""
                SELECT id, paper_code, title, subject, department, academic_year, semester,
                       exam_type, max_marks, total_marks, status, created_at
                FROM question_papers 
                WHERE created_by = %s AND status = 'Draft'
                ORDER BY created_at DESC
            """, (user_id,))
            draft_papers_rows = cursor.fetchall() or []
            for p in draft_papers_rows:
                if isinstance(p.get('created_at'), datetime):
                    p['created_at'] = p['created_at'].strftime('%Y-%m-%d')
            draft_papers = len(draft_papers_rows)

            # 4. Published exams created by this faculty
            cursor.execute("""
                SELECT id, paper_code, title, subject, department, academic_year, semester,
                       exam_type, max_marks, total_marks, status, created_at, published_at
                FROM question_papers 
                WHERE created_by = %s AND status = 'Published'
                ORDER BY published_at DESC, created_at DESC
            """, (user_id,))
            published_exams_rows = cursor.fetchall() or []
            for p in published_exams_rows:
                if isinstance(p.get('created_at'), datetime):
                    p['created_at'] = p['created_at'].strftime('%Y-%m-%d')
                if isinstance(p.get('published_at'), datetime):
                    p['published_at'] = p['published_at'].strftime('%Y-%m-%d')
            published_exams = len(published_exams_rows)

            # 5. Questions created by this faculty in question bank
            cursor.execute("""
                SELECT q.*, u.full_name AS faculty_name 
                FROM questions q 
                LEFT JOIN users u ON q.created_by = u.id 
                WHERE q.created_by = %s AND q.is_in_bank = 1
                ORDER BY q.created_at DESC
            """, (user_id,))
            recent_questions = cursor.fetchall() or []
            for q in recent_questions:
                if isinstance(q.get('created_at'), datetime):
                    q['created_at'] = q['created_at'].strftime('%Y-%m-%d')
                if isinstance(q.get('updated_at'), datetime):
                    q['updated_at'] = q['updated_at'].strftime('%Y-%m-%d')

            # 6. Latest draft paper for difficulty balancer preview
            cursor.execute("""
                SELECT * FROM question_papers 
                WHERE created_by = %s AND status = 'Draft' 
                ORDER BY id DESC LIMIT 1
            """, (user_id,))
            latest_draft = cursor.fetchone()

            active_paper = None
            if latest_draft:
                q_ids = []
                if latest_draft.get('question_ids'):
                    try:
                        q_ids = json.loads(latest_draft['question_ids']) if isinstance(latest_draft['question_ids'], str) else latest_draft['question_ids']
                    except Exception:
                        q_ids = []
                
                q_rows = []
                if q_ids:
                    format_strings = ','.join(['%s'] * len(q_ids))
                    cursor.execute(f"SELECT id, marks, difficulty, bloom_level FROM questions WHERE id IN ({format_strings})", tuple(q_ids))
                    q_rows = cursor.fetchall() or []

                total_marks = int(latest_draft.get('total_marks') or latest_draft.get('max_marks') or 100)
                
                # Breakdown
                easy_q = [q for q in q_rows if (q.get('difficulty') or '').strip().lower() == 'easy']
                medium_q = [q for q in q_rows if (q.get('difficulty') or '').strip().lower() == 'medium']
                hard_q = [q for q in q_rows if (q.get('difficulty') or '').strip().lower() == 'hard']

                easy_count = len(easy_q)
                medium_count = len(medium_q)
                hard_count = len(hard_q)

                easy_marks = sum(int(q.get('marks') or 0) for q in easy_q)
                medium_marks = sum(int(q.get('marks') or 0) for q in medium_q)
                hard_marks = sum(int(q.get('marks') or 0) for q in hard_q)

                marks_sum = easy_marks + medium_marks + hard_marks
                if marks_sum > 0:
                    easy_pct = round((easy_marks / marks_sum) * 100)
                    medium_pct = round((medium_marks / marks_sum) * 100)
                    hard_pct = max(0, 100 - (easy_pct + medium_pct))
                elif q_rows:
                    easy_pct = round((easy_count / len(q_rows)) * 100)
                    medium_pct = round((medium_count / len(q_rows)) * 100)
                    hard_pct = max(0, 100 - (easy_pct + medium_pct))
                else:
                    easy_pct, medium_pct, hard_pct = 30, 50, 20

                blooms = Counter((q.get('bloom_level') or 'Understand').capitalize() for q in q_rows)
                dev = abs(easy_pct - 30) + abs(medium_pct - 50) + abs(hard_pct - 20)
                balance_score = max(70, round(100 - (dev * 0.5)))
                balance_label = f"{balance_score}% Balanced (Bloom Compliant)" if balance_score >= 85 else f"{balance_score}% Balanced (Target: 30:50:20)"

                active_paper = {
                    "id": latest_draft['id'],
                    "paper_code": latest_draft.get('paper_code') or f"EXAM-{latest_draft['id']}",
                    "title": latest_draft.get('title') or 'Draft Question Paper',
                    "subject": latest_draft.get('subject'),
                    "exam_type": latest_draft.get('exam_type') or 'Examination',
                    "total_marks": total_marks,
                    "max_marks": total_marks,
                    "question_count": len(q_rows) if q_rows else len(q_ids),
                    "status": "Draft",
                    "difficulty": {
                        "easy_count": easy_count,
                        "easy_marks": easy_marks,
                        "easy_pct": easy_pct,
                        "medium_count": medium_count,
                        "medium_marks": medium_marks,
                        "medium_pct": medium_pct,
                        "hard_count": hard_count,
                        "hard_marks": hard_marks,
                        "hard_pct": hard_pct
                    },
                    "blooms": dict(blooms),
                    "balance_score": balance_score,
                    "balance_label": balance_label
                }

            # Fetch faculty user name and department
            cursor.execute("SELECT full_name, department FROM users WHERE id = %s", (user_id,))
            u_row = cursor.fetchone() or {}
            faculty_name = session.get('full_name') or u_row.get('full_name') or 'Faculty Member'
            faculty_dept = u_row.get('department') or 'Artificial Intelligence & Data Science'

        conn.close()

        return jsonify({
            "status": "success",
            "faculty_id": user_id,
            "faculty_name": faculty_name,
            "faculty_dept": faculty_dept,
            "total_questions": total_questions,
            "active_courses": active_courses,
            "draft_papers": draft_papers,
            "published_exams": published_exams,
            "courses_list": courses_list,
            "draft_papers_list": draft_papers_rows,
            "published_exams_list": published_exams_rows,
            "recent_questions": recent_questions,
            "active_paper": active_paper
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to retrieve faculty stats: {str(e)}"}), 500


@auth_bp.route('/api/faculty/courses', methods=['GET'])
def faculty_courses_api():
    """
    GET /api/faculty/courses
    Returns active courses for the authenticated faculty member.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Faculty role required."}), 403

    try:
        from models.database import get_db_connection
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT subject, 
                       MAX(department) as department, 
                       MAX(academic_year) as academic_year, 
                       MAX(semester) as semester, 
                       COUNT(*) as item_count
                FROM (
                    SELECT subject, department, academic_year, semester FROM questions WHERE created_by = %s AND is_in_bank = 1 AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM academic_resources WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM question_papers WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                    UNION ALL
                    SELECT subject, department, academic_year, semester FROM quizzes WHERE created_by = %s AND subject IS NOT NULL AND subject != ''
                ) AS s
                GROUP BY subject
                ORDER BY subject ASC
            """, (user_id, user_id, user_id, user_id))
            course_rows = cursor.fetchall() or []
            courses_list = []
            for r in course_rows:
                courses_list.append({
                    "course_name": r['subject'],
                    "course_code": get_course_code_for_subject(r['subject']),
                    "department": r.get('department') or 'Artificial Intelligence & Data Science',
                    "semester": r.get('semester') or 'Semester 6',
                    "academic_year": r.get('academic_year') or '2025-2026',
                    "item_count": r.get('item_count', 0),
                    "status": "Active"
                })
        conn.close()
        return jsonify({"status": "success", "courses": courses_list}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to retrieve faculty courses: {str(e)}"}), 500


