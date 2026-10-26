from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models.database import get_db_connection

material_bp = Blueprint('academic_material', __name__)

# ==========================================================
# 1. ASSIGNMENTS
# ==========================================================
def ensure_assignment_submissions_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS assignment_submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    assignment_id INT NOT NULL,
                    student_id INT NOT NULL,
                    student_name VARCHAR(255),
                    submission_text TEXT,
                    file_name VARCHAR(255),
                    file_path VARCHAR(500),
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'Submitted',
                    score INT DEFAULT NULL,
                    feedback TEXT,
                    INDEX (assignment_id),
                    INDEX (student_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        conn.commit()
    except Exception:
        pass


@material_bp.route('/api/assignments', methods=['GET'])
def get_assignments():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    subject = request.args.get('subject')

    try:
        conn = get_db_connection()
        ensure_assignment_submissions_table(conn)
        with conn.cursor() as cur:
            if role == 'faculty':
                sql = """
                    SELECT a.*, u.full_name as faculty_name
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.created_by = %s
                """
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND a.subject = %s"
                    params.append(subject)
                sql += " ORDER BY a.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = """
                    SELECT a.*, u.full_name as faculty_name,
                           sub.id as submission_id,
                           sub.submitted_at as student_submitted_at,
                           sub.status as submission_status,
                           sub.submission_text,
                           sub.file_name as submitted_file_name
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    LEFT JOIN assignment_submissions sub ON a.id = sub.assignment_id AND sub.student_id = %s
                    WHERE a.status = 'Published'
                """
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND a.subject = %s"
                    params.append(subject)
                sql += " ORDER BY a.created_at DESC"
                cur.execute(sql, params)

            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('due_date'), (datetime,)):
                    r['due_date'] = r['due_date'].strftime('%Y-%m-%d')
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
                if isinstance(r.get('student_submitted_at'), (datetime,)):
                    r['student_submitted_at'] = r['student_submitted_at'].strftime('%d %b %Y, %I:%M %p')
                r['is_submitted'] = bool(r.get('submission_id'))
        conn.close()
        return jsonify({"status": "success", "assignments": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/assignments/<int:asn_id>/submit', methods=['POST'])
def submit_assignment(asn_id):
    user_id = session.get('user_id')
    role = session.get('role')
    full_name = session.get('full_name') or 'Student'
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'student':
        return jsonify({"status": "error", "message": "Only students can submit assignments."}), 403

    submission_text = ''
    file_name = ''
    file_path = ''

    if request.content_type and 'multipart/form-data' in request.content_type:
        submission_text = (request.form.get('submission_text') or request.form.get('answer') or '').strip()
        uploaded_file = request.files.get('file') or request.files.get('assignmentFile')
        if uploaded_file and uploaded_file.filename:
            from werkzeug.utils import secure_filename
            import time
            fname = secure_filename(uploaded_file.filename)
            from config import Config
            upload_sub_dir = os.path.join(Config.UPLOAD_FOLDER, 'assignments')
            os.makedirs(upload_sub_dir, exist_ok=True)
            saved_name = f"{int(time.time())}_{fname}"
            uploaded_file.save(os.path.join(upload_sub_dir, saved_name))
            file_name = uploaded_file.filename
            file_path = f"uploads/assignments/{saved_name}"
    else:
        data = request.get_json(silent=True) or {}
        submission_text = (data.get('submission_text') or data.get('answer') or data.get('notes') or '').strip()
        file_name = data.get('file_name') or ''
        file_path = data.get('file_path') or ''

    try:
        conn = get_db_connection()
        ensure_assignment_submissions_table(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM assignment_submissions WHERE assignment_id = %s AND student_id = %s", (asn_id, user_id))
            existing = cur.fetchone()
            if existing:
                cur.execute("""
                    UPDATE assignment_submissions
                    SET submission_text = %s, file_name = COALESCE(NULLIF(%s, ''), file_name),
                        file_path = COALESCE(NULLIF(%s, ''), file_path), submitted_at = NOW(), status = 'Submitted'
                    WHERE id = %s
                """, (submission_text, file_name, file_path, existing['id']))
                sub_id = existing['id']
            else:
                cur.execute("""
                    INSERT INTO assignment_submissions
                    (assignment_id, student_id, student_name, submission_text, file_name, file_path, status, submitted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Submitted', NOW())
                """, (asn_id, user_id, full_name, submission_text, file_name, file_path))
                sub_id = cur.lastrowid
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Assignment submitted successfully.", "submission_id": sub_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/assignments', methods=['POST'])
def create_assignment():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty can create assignments."}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or data.get('assignmentTitle') or 'Assignment').strip()
    subject = (data.get('subject') or '').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit 1').strip()
    due_date = data.get('due_date') or data.get('dueDate') or None
    total_marks = int(data.get('total_marks') or data.get('totalMarks') or 20)
    instructions = data.get('instructions') or data.get('questions') or ''
    if isinstance(instructions, (list, dict)):
        import json
        instructions = json.dumps(instructions)
    status = data.get('status') or 'Published'

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO assignments
                (title, subject, department, academic_year, semester, unit, due_date, total_marks, instructions, status, created_by, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (title, subject, department, academic_year, semester, unit, due_date, total_marks, instructions, status, user_id))
            new_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "success", "message": "Assignment created successfully.", "id": new_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/assignments/<int:asn_id>', methods=['DELETE'])
def delete_assignment(asn_id):
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM assignments WHERE id = %s AND created_by = %s", (asn_id, user_id))
        conn.close()
        return jsonify({"status": "success", "message": "Assignment deleted."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================
# 2. PRESENTATIONS (PPT)
# ==========================================================
@material_bp.route('/api/presentations', methods=['GET'])
def get_presentations():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    subject = request.args.get('subject')

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                sql = """
                    SELECT p.*, u.full_name as faculty_name
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.created_by = %s
                """
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND p.subject = %s"
                    params.append(subject)
                sql += " ORDER BY p.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = """
                    SELECT p.*, u.full_name as faculty_name
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.status = 'Published'
                """
                params = []
                if subject and subject != 'ALL':
                    sql += " AND p.subject = %s"
                    params.append(subject)
                sql += " ORDER BY p.created_at DESC"
                cur.execute(sql, params)
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "presentations": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/presentations', methods=['POST'])
def create_presentation():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or data.get('pptTitle') or 'Presentation').strip()
    subject = (data.get('subject') or '').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit 1').strip()
    topic = (data.get('topic') or '').strip()
    slide_count = int(data.get('slide_count') or data.get('slideCount') or 10)
    presentation_type = (data.get('presentation_type') or data.get('template') or 'Standard').strip()
    source_material = (data.get('source_material') or '').strip()
    status = data.get('status') or 'Published'

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO presentations
                (title, subject, department, academic_year, semester, unit, topic, slide_count, presentation_type, source_material, status, created_by, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (title, subject, department, academic_year, semester, unit, topic, slide_count, presentation_type, source_material, status, user_id))
            new_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "success", "message": "Presentation saved.", "id": new_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/presentations/<int:ppt_id>', methods=['DELETE'])
def delete_presentation(ppt_id):
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM presentations WHERE id = %s AND created_by = %s", (ppt_id, user_id))
        conn.close()
        return jsonify({"status": "success", "message": "Presentation deleted."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================
# 3. LESSON PLANS
# ==========================================================
@material_bp.route('/api/lesson-plans', methods=['GET'])
def get_lesson_plans():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    subject = request.args.get('subject')

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                sql = """
                    SELECT lp.*, u.full_name as faculty_name
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.created_by = %s
                """
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND lp.subject = %s"
                    params.append(subject)
                sql += " ORDER BY lp.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = """
                    SELECT lp.*, u.full_name as faculty_name
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.status = 'Published'
                """
                params = []
                if subject and subject != 'ALL':
                    sql += " AND lp.subject = %s"
                    params.append(subject)
                sql += " ORDER BY lp.created_at DESC"
                cur.execute(sql, params)
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "lesson_plans": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/lesson-plans', methods=['POST'])
def create_lesson_plan():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or data.get('lpTitle') or 'Lesson Plan').strip()
    subject = (data.get('subject') or '').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit 1').strip()
    topic = (data.get('topic') or '').strip()
    duration = int(data.get('duration_minutes') or data.get('duration') or 50)
    teaching_method = (data.get('teaching_method') or data.get('method') or 'Interactive Lecture').strip()
    status = data.get('status') or 'Published'

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lesson_plans
                (title, subject, department, academic_year, semester, unit, topic, duration_minutes, teaching_method, status, created_by, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (title, subject, department, academic_year, semester, unit, topic, duration, teaching_method, status, user_id))
            new_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "success", "message": "Lesson plan saved.", "id": new_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/lesson-plans/<int:lp_id>', methods=['DELETE'])
def delete_lesson_plan(lp_id):
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id or role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden"}), 403

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM lesson_plans WHERE id = %s AND created_by = %s", (lp_id, user_id))
        conn.close()
        return jsonify({"status": "success", "message": "Lesson plan deleted."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ==========================================================
# 4. ACTIVITY HISTORY
# ==========================================================
@material_bp.route('/api/faculty/history', methods=['GET'])
def get_faculty_history():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM activity_history
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 50
            """, (user_id,))
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M')
        conn.close()
        return jsonify({"status": "success", "history": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@material_bp.route('/api/faculty/history', methods=['POST'])
def add_faculty_history():
    user_id = session.get('user_id')
    role = session.get('role') or 'faculty'
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required."}), 401

    data = request.get_json(silent=True) or {}
    activity_type = (data.get('activity_type') or data.get('type') or 'General').strip()
    title = (data.get('title') or '').strip()
    subject = (data.get('subject') or '').strip()
    unit = (data.get('unit') or '').strip()
    status = (data.get('status') or 'Completed').strip()

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO activity_history (user_id, role, activity_type, title, subject, unit, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, role, activity_type, title, subject, unit, status))
            new_id = cur.lastrowid
        conn.close()
        return jsonify({"status": "success", "id": new_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500