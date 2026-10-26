import os
import time
from flask import Blueprint, request, jsonify, session, send_from_directory, current_app
from werkzeug.utils import secure_filename
from services.resource_service import (
    create_academic_resource,
    get_academic_resources,
    get_academic_resource_by_id,
    update_academic_resource,
    delete_academic_resource,
    analyze_academic_resource
)

resource_bp = Blueprint('resource', __name__)

from config import Config
UPLOAD_DIR = os.path.join(Config.UPLOAD_FOLDER, 'resources')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@resource_bp.route('/api/resources', methods=['POST'])
def create_resource():
    """
    POST /api/resources
    Creates a new academic resource record. Role: Faculty only.
    Handles multipart/form-data for file uploads.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can create resources."}), 403

    ensure_upload_dir()

    # Extract form or JSON data
    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True) or {}

    file_info = None
    uploaded_file = request.files.get('file') or request.files.get('resourceFile')

    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        if not allowed_file(filename):
            return jsonify({"status": "error", "message": "Invalid file type. Allowed: PDF, DOCX, DOC, PPT, PPTX, TXT, PNG, JPG."}), 400

        # Save with timestamp prefix to prevent name collisions
        timestamp_prefix = int(time.time())
        saved_filename = f"{timestamp_prefix}_{filename}"
        saved_path = os.path.join(UPLOAD_DIR, saved_filename)
        uploaded_file.save(saved_path)

        file_info = {
            "file_name": uploaded_file.filename,
            "file_path": f"uploads/resources/{saved_filename}"
        }

    success, result, status_code = create_academic_resource(user_id, data, file_info)
    return jsonify(result), status_code


@resource_bp.route('/api/resources', methods=['GET'])
def get_resources():
    """
    GET /api/resources
    Returns academic resources.
    Faculty sees owned resources; Students see published/available materials.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    filters = {
        "subject": request.args.get('subject'),
        "department": request.args.get('department'),
        "resource_type": request.args.get('resource_type')
    }

    success, result, status_code = get_academic_resources(user_id, role, filters)
    return jsonify(result), status_code


@resource_bp.route('/api/resources/<int:resource_id>', methods=['GET'])
def get_resource(resource_id):
    """
    GET /api/resources/<id>
    Retrieves single academic resource record by ID.
    """
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    resource = get_academic_resource_by_id(resource_id)
    if not resource:
        return jsonify({"status": "error", "message": "Academic resource not found."}), 404

    # Faculty data isolation check: Faculty members can only view their own resources
    if role == 'faculty' and resource.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You are not authorized to view this resource."}), 403

    return jsonify({"status": "success", "resource": resource}), 200


@resource_bp.route('/api/resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """
    PUT /api/resources/<id>
    Updates an existing academic resource. Role: Faculty only (creator).
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can edit resources."}), 403

    ensure_upload_dir()

    if request.content_type and 'multipart/form-data' in request.content_type:
        data = request.form.to_dict()
    else:
        data = request.get_json(silent=True) or {}

    file_info = None
    uploaded_file = request.files.get('file') or request.files.get('resourceFile')

    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        if not allowed_file(filename):
            return jsonify({"status": "error", "message": "Invalid file type. Allowed: PDF, DOCX, DOC, PPT, PPTX, TXT, PNG, JPG."}), 400

        timestamp_prefix = int(time.time())
        saved_filename = f"{timestamp_prefix}_{filename}"
        saved_path = os.path.join(UPLOAD_DIR, saved_filename)
        uploaded_file.save(saved_path)

        file_info = {
            "file_name": uploaded_file.filename,
            "file_path": f"uploads/resources/{saved_filename}"
        }

    success, result, status_code = update_academic_resource(resource_id, user_id, data, file_info)
    return jsonify(result), status_code


@resource_bp.route('/api/resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """
    DELETE /api/resources/<id>
    Deletes an academic resource. Role: Faculty only (creator).
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can delete resources."}), 403

    success, result, status_code = delete_academic_resource(resource_id, user_id)
    return jsonify(result), status_code


@resource_bp.route('/api/resources/<int:resource_id>/analyze', methods=['POST'])
def analyze_resource(resource_id):
    """
    POST /api/resources/<id>/analyze
    Performs content analysis on an academic resource and updates status/metadata. Role: Faculty only (creator).
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can analyze resources."}), 403

    success, result, status_code = analyze_academic_resource(resource_id, user_id)
    return jsonify(result), status_code


@resource_bp.route('/api/resources/file/<filename>', methods=['GET'])
def download_file(filename):
    """
    GET /api/resources/file/<filename>
    Safely serves uploaded resource files.
    Resolves both direct disk filenames and original filenames prefixed with timestamps.
    """
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
    """
    GET /api/resources/<id>/file
    Directly serves the file associated with an academic resource ID.
    """
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
    """
    GET /api/student/subjects
    Returns registered curriculum courses for the authenticated student,
    including real-time counts of materials, quizzes, assignments, and question papers.
    """
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
            cur.execute("""
                SELECT DISTINCT subject FROM (
                    SELECT subject FROM academic_resources WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM question_papers WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM quizzes WHERE subject IS NOT NULL AND subject != ''
                    UNION
                    SELECT subject FROM assignments WHERE subject IS NOT NULL AND subject != ''
                ) as s_list
            """)
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
        return jsonify({"status": "error", "message": str(e)}), 500