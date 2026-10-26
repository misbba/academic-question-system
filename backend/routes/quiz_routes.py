from flask import Blueprint, request, jsonify, session
from services.quiz_service import (
    generate_quiz_service,
    create_quiz_record,
    get_quizzes_list,
    get_quiz_by_id,
    update_quiz_record,
    delete_quiz_record,
    submit_student_quiz_attempt,
    get_student_quiz_attempts
)

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/api/quizzes', methods=['POST'])
def create_quiz_api():
    """
    POST /api/quizzes
    Creates a new quiz record in MySQL. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can create quizzes."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = create_quiz_record(user_id, data)
    return jsonify(result), status_code


@quiz_bp.route('/api/quizzes', methods=['GET'])
def get_quizzes_api():
    """
    GET /api/quizzes
    Retrieves quizzes based on user role (Faculty sees created; Student sees Published).
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    filters = {
        "subject": request.args.get('subject'),
        "department": request.args.get('department'),
        "semester": request.args.get('semester'),
        "status": request.args.get('status')
    }

    success, result, status_code = get_quizzes_list(user_id, role, filters)
    return jsonify(result), status_code


@quiz_bp.route('/api/quizzes/attempts', methods=['GET'])
def get_quiz_attempts_api():
    """
    GET /api/quizzes/attempts
    Retrieves quiz attempts with strict faculty/student isolation.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    if role == 'student':
        success, result, status_code = get_student_quiz_attempts(student_id=user_id, role='student')
    else:
        success, result, status_code = get_student_quiz_attempts(faculty_id=user_id, role='faculty')
    return jsonify(result), status_code


@quiz_bp.route('/api/quizzes/<id>', methods=['GET'])
def get_quiz_by_id_api(id):
    """
    GET /api/quizzes/<id>
    Retrieves a single quiz by ID or quiz_code.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    quiz = get_quiz_by_id(id, user_id, role)
    if not quiz:
        raw_quiz = get_quiz_by_id(id)
        if raw_quiz and role == 'faculty' and raw_quiz.get('created_by') != user_id:
            return jsonify({"status": "error", "message": "Forbidden. You are not authorized to view this quiz."}), 403
        return jsonify({"status": "error", "message": "Quiz not found or access forbidden."}), 404

    return jsonify({
        "status": "success",
        "quiz": quiz
    }), 200


@quiz_bp.route('/api/quizzes/<id>', methods=['PUT'])
def update_quiz_api(id):
    """
    PUT /api/quizzes/<id>
    Updates an existing quiz record. Role: Faculty owner only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can update quizzes."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = update_quiz_record(id, user_id, data)
    return jsonify(result), status_code


@quiz_bp.route('/api/quizzes/<id>', methods=['DELETE'])
def delete_quiz_api(id):
    """
    DELETE /api/quizzes/<id>
    Deletes a quiz record. Role: Faculty owner only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can delete quizzes."}), 403

    success, result, status_code = delete_quiz_record(id, user_id)
    return jsonify(result), status_code


@quiz_bp.route('/api/quizzes/<id>/submit', methods=['POST'])
def submit_quiz_api(id):
    """
    POST /api/quizzes/<id>/submit
    Submits a student's timed quiz attempt, auto-evaluates score, and records attempt in MySQL. Role: Student only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'student':
        return jsonify({"status": "error", "message": "Forbidden. Only Students can submit quiz attempts."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = submit_student_quiz_attempt(user_id, id, data)
    return jsonify(result), status_code

@quiz_bp.route('/api/quizzes/generate', methods=['POST'])
def generate_quiz_api():
    """
    POST /api/quizzes/generate
    Generates preview quiz questions from uploaded materials, syllabus, or question bank.
    Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate quizzes."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_quiz_service(user_id, data)
    return jsonify(result), status_code
