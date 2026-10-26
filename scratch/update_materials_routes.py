import os

file_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\academic_material_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_assignments and add submission support
old_assignments = """# ==========================================================
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
                cur.execute(\"\"\"
                    SELECT a.*, u.full_name as faculty_name 
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.created_by = %s
                    ORDER BY a.created_at DESC
                \"\"\", (user_id,))
            else:
                cur.execute(\"\"\"
                    SELECT a.*, u.full_name as faculty_name 
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.status = 'Published'
                    ORDER BY a.created_at DESC
                \"\"\")
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('due_date'), (datetime,)):
                    r['due_date'] = r['due_date'].strftime('%Y-%m-%d')
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "assignments": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

new_assignments = """# ==========================================================
# 1. ASSIGNMENTS
# ==========================================================
def ensure_assignment_submissions_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(\"\"\"
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
            \"\"\")
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
                sql = \"\"\"
                    SELECT a.*, u.full_name as faculty_name 
                    FROM assignments a
                    LEFT JOIN users u ON a.created_by = u.id
                    WHERE a.created_by = %s
                \"\"\"
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND a.subject = %s"
                    params.append(subject)
                sql += " ORDER BY a.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = \"\"\"
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
                \"\"\"
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
            upload_sub_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads', 'assignments'))
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
                cur.execute(\"\"\"
                    UPDATE assignment_submissions
                    SET submission_text = %s, file_name = COALESCE(NULLIF(%s, ''), file_name),
                        file_path = COALESCE(NULLIF(%s, ''), file_path), submitted_at = NOW(), status = 'Submitted'
                    WHERE id = %s
                \"\"\", (submission_text, file_name, file_path, existing['id']))
                sub_id = existing['id']
            else:
                cur.execute(\"\"\"
                    INSERT INTO assignment_submissions
                    (assignment_id, student_id, student_name, submission_text, file_name, file_path, status, submitted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Submitted', NOW())
                \"\"\", (asn_id, user_id, full_name, submission_text, file_name, file_path))
                sub_id = cur.lastrowid
            conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Assignment submitted successfully.", "submission_id": sub_id}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

# Also update get_presentations to filter by subject
old_ppt = """@material_bp.route('/api/presentations', methods=['GET'])
def get_presentations():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                cur.execute(\"\"\"
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.created_by = %s
                    ORDER BY p.created_at DESC
                \"\"\", (user_id,))
            else:
                cur.execute(\"\"\"
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.status = 'Published'
                    ORDER BY p.created_at DESC
                \"\"\")
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "presentations": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

new_ppt = """@material_bp.route('/api/presentations', methods=['GET'])
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
                sql = \"\"\"
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.created_by = %s
                \"\"\"
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND p.subject = %s"
                    params.append(subject)
                sql += " ORDER BY p.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = \"\"\"
                    SELECT p.*, u.full_name as faculty_name 
                    FROM presentations p
                    LEFT JOIN users u ON p.created_by = u.id
                    WHERE p.status = 'Published'
                \"\"\"
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
        return jsonify({"status": "error", "message": str(e)}), 500"""

# Also update get_lesson_plans to filter by subject
old_lp = """@material_bp.route('/api/lesson-plans', methods=['GET'])
def get_lesson_plans():
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            if role == 'faculty':
                cur.execute(\"\"\"
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.created_by = %s
                    ORDER BY lp.created_at DESC
                \"\"\", (user_id,))
            else:
                cur.execute(\"\"\"
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.status = 'Published'
                    ORDER BY lp.created_at DESC
                \"\"\")
            rows = cur.fetchall() or []
            for r in rows:
                if isinstance(r.get('created_at'), (datetime,)):
                    r['created_at'] = r['created_at'].strftime('%Y-%m-%d')
        conn.close()
        return jsonify({"status": "success", "lesson_plans": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

new_lp = """@material_bp.route('/api/lesson-plans', methods=['GET'])
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
                sql = \"\"\"
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.created_by = %s
                \"\"\"
                params = [user_id]
                if subject and subject != 'ALL':
                    sql += " AND lp.subject = %s"
                    params.append(subject)
                sql += " ORDER BY lp.created_at DESC"
                cur.execute(sql, params)
            else:
                sql = \"\"\"
                    SELECT lp.*, u.full_name as faculty_name 
                    FROM lesson_plans lp
                    LEFT JOIN users u ON lp.created_by = u.id
                    WHERE lp.status = 'Published'
                \"\"\"
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
        return jsonify({"status": "error", "message": str(e)}), 500"""

norm = lambda t: '\n'.join(line.rstrip() for line in t.splitlines())
c_norm = norm(content)

if norm(old_assignments) in c_norm:
    c_norm = c_norm.replace(norm(old_assignments), norm(new_assignments))
    print("SUCCESS: Replaced assignments section")
else:
    print("WARNING: Old assignments section not found")

if norm(old_ppt) in c_norm:
    c_norm = c_norm.replace(norm(old_ppt), norm(new_ppt))
    print("SUCCESS: Replaced presentations section")
else:
    print("WARNING: Old presentations section not found")

if norm(old_lp) in c_norm:
    c_norm = c_norm.replace(norm(old_lp), norm(new_lp))
    print("SUCCESS: Replaced lesson plans section")
else:
    print("WARNING: Old lesson plans section not found")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(c_norm)

print("Done updating academic_material_routes.py")
