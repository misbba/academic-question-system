from flask import Blueprint, request, jsonify, session
from services.question_paper_service import (
    create_question_paper,
    get_question_papers,
    get_question_paper_by_id,
    update_question_paper,
    delete_question_paper,
    verify_paper_fingerprint,
    generate_template_paper
)

question_paper_bp = Blueprint('question_paper', __name__)

@question_paper_bp.route('/api/question-papers/generate-template', methods=['POST'])
def generate_template_paper_api():
    """
    POST /api/question-papers/generate-template
    Generates a structured question paper based on standard templates:
    - Internal Test (50 attempted marks: Sec A 5x2=10, Sec B Either/Or 1x8=8, Sec C Either/Or 2x16=32)
    - Semester Exam (100 attempted marks: Sec A 10x2=20 with 2 per unit, Sec B Either/Or 5x16=80 across 5 units)
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate question papers."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_template_paper(user_id, data)
    return jsonify(result), status_code

@question_paper_bp.route('/api/question-papers', methods=['POST'])
def create_paper_api():
    """
    POST /api/question-papers
    Creates and stores a complete question paper in MySQL. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can create question papers."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = create_question_paper(user_id, data)
    return jsonify(result), status_code


@question_paper_bp.route('/api/question-papers', methods=['GET'])
def get_papers_api():
    """
    GET /api/question-papers
    Returns papers created by the logged-in faculty or published papers for students.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    filters = {
        "subject": request.args.get('subject'),
        "department": request.args.get('department'),
        "semester": request.args.get('semester'),
        "academic_year": request.args.get('academic_year'),
        "exam_type": request.args.get('exam_type'),
        "status": request.args.get('status')
    }

    if role == 'student':
        filters['status'] = 'Published'
        success, result, status_code = get_question_papers(faculty_id=None, filters=filters, is_student=True)
    elif role == 'faculty':
        success, result, status_code = get_question_papers(faculty_id=user_id, filters=filters, is_student=False)
    else:
        return jsonify({"status": "error", "message": "Forbidden. Unauthorized role."}), 403

    return jsonify(result), status_code


@question_paper_bp.route('/api/question-papers/<id>', methods=['GET'])
def get_paper_by_id_api(id):
    """
    GET /api/question-papers/<id>
    Returns details and selected questions for a single question paper.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    paper = get_question_paper_by_id(id)
    if not paper:
        return jsonify({"status": "error", "message": "Question paper not found."}), 404

    # Faculty can only view their own question papers; student can view published paper
    if role == 'faculty' and paper.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You can only view your own question papers."}), 403
    elif role == 'student' and paper.get('status') != 'Published':
        return jsonify({"status": "error", "message": "Forbidden. Students can only view published examination papers."}), 403

    return jsonify({
        "status": "success",
        "question_paper": paper,
        "paper": paper
    }), 200


@question_paper_bp.route('/api/question-papers/<id>', methods=['PUT'])
def update_paper_api(id):
    """
    PUT /api/question-papers/<id>
    Updates an existing question paper and regenerates fingerprint. Role: Faculty owner only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can update question papers."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = update_question_paper(id, user_id, data)
    return jsonify(result), status_code


@question_paper_bp.route('/api/question-papers/<id>', methods=['DELETE'])
def delete_paper_api(id):
    """
    DELETE /api/question-papers/<id>
    Deletes a question paper record. Role: Faculty owner only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can delete question papers."}), 403

    success, result, status_code = delete_question_paper(id, user_id)
    return jsonify(result), status_code


@question_paper_bp.route('/api/question-papers/<id>/verify', methods=['POST'])
def verify_paper_api(id):
    """
    POST /api/question-papers/<id>/verify
    Verifies submitted fingerprint against the paper stored in MySQL.
    """
    data = request.get_json(silent=True) or {}
    submitted_fingerprint = data.get('fingerprint') or data.get('sha256_hash') or ''

    success, result, status_code = verify_paper_fingerprint(id, submitted_fingerprint)
    return jsonify(result), status_code
