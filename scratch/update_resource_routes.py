import os

file_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\resource_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """@resource_bp.route('/api/resources/file/<filename>', methods=['GET'])
def download_file(filename):
    \"\"\"
    GET /api/resources/file/<filename>
    Safely serves uploaded resource files.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    ensure_upload_dir()
    safe_name = secure_filename(filename)

    if not os.path.exists(os.path.join(UPLOAD_DIR, safe_name)):
        return jsonify({"status": "error", "message": "Resource file not found on server."}), 404

    # Faculty file authorization check: Faculty can only download their own resource files
    if role == 'faculty':
        from models.database import get_db_connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM academic_resources WHERE created_by = %s AND (file_path LIKE %s OR file_name = %s)", 
                (user_id, f"%{safe_name}%", safe_name)
            )
            owned = cur.fetchone()
        conn.close()
        if not owned and not safe_name.startswith('diagram_'):
            return jsonify({"status": "error", "message": "Forbidden. You are not authorized to access this file."}), 403

    return send_from_directory(UPLOAD_DIR, safe_name)"""

replacement = """@resource_bp.route('/api/resources/file/<filename>', methods=['GET'])
def download_file(filename):
    \"\"\"
    GET /api/resources/file/<filename>
    Safely serves uploaded resource files.
    Resolves both direct disk filenames and original filenames prefixed with timestamps.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    ensure_upload_dir()
    safe_name = secure_filename(filename)
    target_disk_name = safe_name

    # Check if exists directly on disk
    if not os.path.exists(os.path.join(UPLOAD_DIR, target_disk_name)):
        # Attempt to resolve via academic_resources database
        from models.database import get_db_connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT file_path FROM academic_resources WHERE file_name = %s OR file_path LIKE %s LIMIT 1",
                (filename, f"%{safe_name}")
            )
            found = cur.fetchone()
        conn.close()
        if found and found.get('file_path'):
            resolved_base = os.path.basename(found['file_path'])
            if os.path.exists(os.path.join(UPLOAD_DIR, resolved_base)):
                target_disk_name = resolved_base

    if not os.path.exists(os.path.join(UPLOAD_DIR, target_disk_name)):
        return jsonify({"status": "error", "message": "Resource file not found on server."}), 404

    # Faculty file authorization check: Faculty can only download their own resource files
    if role == 'faculty':
        from models.database import get_db_connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM academic_resources WHERE created_by = %s AND (file_path LIKE %s OR file_name = %s)", 
                (user_id, f"%{target_disk_name}%", filename)
            )
            owned = cur.fetchone()
        conn.close()
        if not owned and not target_disk_name.startswith('diagram_'):
            return jsonify({"status": "error", "message": "Forbidden. You are not authorized to access this file."}), 403

    return send_from_directory(UPLOAD_DIR, target_disk_name)


@resource_bp.route('/api/resources/<int:resource_id>/file', methods=['GET'])
def download_resource_file_by_id(resource_id):
    \"\"\"
    GET /api/resources/<id>/file
    Directly serves the file associated with an academic resource ID.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    resource = get_academic_resource_by_id(resource_id)
    if not resource:
        return jsonify({"status": "error", "message": "Academic resource not found."}), 404

    if role == 'faculty' and resource.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You can only access your own uploaded resources."}), 403
    elif role == 'student' and resource.get('status') == 'Deleted':
        return jsonify({"status": "error", "message": "Forbidden. This resource is no longer available."}), 403

    ensure_upload_dir()
    file_path = resource.get('file_path') or ''
    disk_filename = os.path.basename(file_path) if file_path else ''
    
    if not disk_filename or not os.path.exists(os.path.join(UPLOAD_DIR, disk_filename)):
        # Fallback check file_name
        fallback_name = resource.get('file_name')
        if fallback_name and os.path.exists(os.path.join(UPLOAD_DIR, secure_filename(fallback_name))):
            disk_filename = secure_filename(fallback_name)
        else:
            return jsonify({"status": "error", "message": "Resource file not found on disk storage."}), 404

    return send_from_directory(UPLOAD_DIR, disk_filename)


@resource_bp.route('/api/student/subjects', methods=['GET'])
def get_student_subjects():
    \"\"\"
    GET /api/student/subjects
    Returns registered curriculum courses for the authenticated student,
    including real-time counts of materials, quizzes, assignments, and question papers.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    from models.database import get_db_connection
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, full_name, department, semester, academic_year FROM users WHERE id = %s", (user_id,))
            student = cur.fetchone() or {}
            dept = student.get('department') or 'Artificial Intelligence & Data Science'
            sem = student.get('semester') or 'Semester 6'

            # Standard curriculum courses
            subjects = [
                {
                    "code": "CS301",
                    "name": "Database Management Systems",
                    "department": dept,
                    "credits": 4,
                    "description": "Relational database design, relational algebra, SQL optimization, transactions, ACID properties, and concurrency control."
                },
                {
                    "code": "23CST504",
                    "name": "Distributed Computing",
                    "department": dept,
                    "credits": 4,
                    "description": "Distributed system architectures, RPC, clock synchronization, Lamport logical timestamps, mutual exclusion, and consensus."
                },
                {
                    "code": "AI401",
                    "name": "Machine Learning",
                    "department": dept,
                    "credits": 4,
                    "description": "Supervised and unsupervised learning, classification, neural networks, deep architectures, and model performance metrics."
                },
                {
                    "code": "IT302",
                    "name": "Cloud Computing",
                    "department": dept,
                    "credits": 3,
                    "description": "Cloud virtualization, IaaS, PaaS, SaaS delivery models, distributed storage, and cloud microservices orchestration."
                }
            ]

            # Discover any other subjects in the database
            cur.execute(\"\"\"
                SELECT DISTINCT subject FROM (
                    SELECT subject FROM academic_resources WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM question_papers WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM quizzes WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM assignments WHERE subject IS NOT NULL AND subject != ''
                ) as s_list
            \"\"\")
            known_names = {s["name"].lower() for s in subjects}
            for row in cur.fetchall():
                s_name = row['subject'].strip()
                if s_name and s_name.lower() not in known_names:
                    known_names.add(s_name.lower())
                    subjects.append({
                        "code": f"SUB{len(subjects)+1:03d}",
                        "name": s_name,
                        "department": dept,
                        "credits": 3,
                        "description": f"Curriculum coursework and study materials for {s_name}."
                    })

            for s in subjects:
                s_name = s['name']
                cur.execute("SELECT count(*) as c FROM academic_resources WHERE subject = %s AND status != 'Deleted'", (s_name,))
                s['materials_count'] = cur.fetchone()['c']

                cur.execute("SELECT count(*) as c FROM quizzes WHERE subject = %s AND status = 'Published'", (s_name,))
                s['quizzes_count'] = cur.fetchone()['c']

                cur.execute("SELECT count(*) as c FROM assignments WHERE subject = %s AND status = 'Published'", (s_name,))
                s['assignments_count'] = cur.fetchone()['c']

                cur.execute("SELECT count(*) as c FROM question_papers WHERE subject = %s AND status = 'Published'", (s_name,))
                s['papers_count'] = cur.fetchone()['c']

        conn.close()
        return jsonify({
            "status": "success",
            "department": dept,
            "semester": sem,
            "subjects": subjects
        }), 200
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500"""

target_norm = '\n'.join(line.rstrip() for line in target.splitlines())
content_norm = '\n'.join(line.rstrip() for line in content.splitlines())

if target_norm in content_norm:
    new_content_norm = content_norm.replace(target_norm, '\n'.join(line.rstrip() for line in replacement.splitlines()))
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content_norm)
    print("SUCCESS: Updated resource_routes.py")
else:
    print("ERROR: Target norm not found")
