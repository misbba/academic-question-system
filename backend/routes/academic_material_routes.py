from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models.database import get_db_connection

material_bp = Blueprint('academic_material', __name__)

# ==========================================================
# 1. ASSIGNMENTS
# ==========================================================
@material_bp.route('/api/assignments', methods=['GET'])
def get_assignments():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                cur.execute("""
                    SELECT a.*, u.full_name as faculty_name 
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.created_by = %s
                    ORDER BY a.created_at DESC
                """, (user_id,))
            else:
                cur.execute("""
                    SELECT a.*, u.full_name as faculty_name 
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.status = 'Published'
                    ORDER BY a.created_at DESC
                """)
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('due_date'), (datetime,)):
                    r['due_date'] = r['due_date'].strftime('%Y-%m-%d')
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "assignments": rows}), 200
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

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                cur.execute("""
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.created_by = %s
                    ORDER BY p.created_at DESC
                """, (user_id,))
            else:
                cur.execute("""
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.status = 'Published'
                    ORDER BY p.created_at DESC
                """)
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

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                cur.execute("""
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.created_by = %s
                    ORDER BY lp.created_at DESC
                """, (user_id,))
            else:
                cur.execute("""
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.status = 'Published'
                    ORDER BY lp.created_at DESC
                """)
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
