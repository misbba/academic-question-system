from flask import Blueprint, request, jsonify, session
from services.question_service import (
    generate_questions_service,
    generate_image_questions_service,
    analyze_image_service,
    create_question_record,
    create_questions_batch,
    get_questions,
    get_question_by_id,
    update_question_record,
    delete_question_record,
    save_to_question_bank,
    remove_from_question_bank,
    get_question_bank
)

question_bp = Blueprint('question', __name__)

@question_bp.route('/api/questions', methods=['POST'])
def create_questions_api():
    """
    POST /api/questions
    Saves generated question(s) into MySQL. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can create questions."}), 403

    data = request.get_json(silent=True) or {}

    if isinstance(data, list):
        success, result, status_code = create_questions_batch(user_id, data)
    elif isinstance(data, dict) and (data.get('batch') or data.get('questions')):
        batch_items = data.get('batch') if data.get('batch') is not None else data.get('questions')
        success, result, status_code = create_questions_batch(user_id, batch_items)
    else:
        success, result, status_code = create_question_record(user_id, data)

    return jsonify(result), status_code


@question_bp.route('/api/questions', methods=['GET'])
def get_questions_api():
    """
    GET /api/questions
    Retrieves filtered questions list.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    filters = {
        "subject": request.args.get('subject'),
        "department": request.args.get('department'),
        "academic_year": request.args.get('academic_year'),
        "semester": request.args.get('semester'),
        "unit": request.args.get('unit'),
        "topic": request.args.get('topic'),
        "marks": request.args.get('marks'),
        "difficulty": request.args.get('difficulty'),
        "question_type": request.args.get('question_type'),
        "bloom_level": request.args.get('bloom_level'),
        "is_in_bank": request.args.get('is_in_bank'),
        "resource_id": request.args.get('resource_id'),
        "search": request.args.get('search')
    }

    success, result, status_code = get_questions(user_id, role, filters)
    return jsonify(result), status_code


@question_bp.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_api(question_id):
    """
    GET /api/questions/<id>
    Retrieves single question details by ID.
    """
    user_id = session.get('user_id')
    role = session.get('role')
    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    question = get_question_by_id(question_id)
    if not question:
        return jsonify({"status": "error", "message": "Question not found."}), 404

    # Faculty data isolation check: Faculty members can only view their own questions
    if role == 'faculty' and question.get('created_by') != user_id:
        return jsonify({"status": "error", "message": "Forbidden. You are not authorized to view this question."}), 403

    return jsonify({"status": "success", "question": question}), 200


@question_bp.route('/api/questions/<int:question_id>', methods=['PUT'])
def update_question_api(question_id):
    """
    PUT /api/questions/<id>
    Updates an existing question record. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can edit questions."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = update_question_record(question_id, user_id, data)
    return jsonify(result), status_code


@question_bp.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question_api(question_id):
    """
    DELETE /api/questions/<id>
    Deletes a question record. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can delete questions."}), 403

    success, result, status_code = delete_question_record(question_id, user_id)
    return jsonify(result), status_code


@question_bp.route('/api/question-bank', methods=['POST'])
@question_bp.route('/api/questions/bank', methods=['POST'])
def save_question_bank_api():
    """
    POST /api/question-bank
    Saves question(s) to Faculty Question Bank. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can save to Question Bank."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = save_to_question_bank(user_id, data)
    return jsonify(result), status_code


@question_bp.route('/api/question-bank', methods=['GET'])
@question_bp.route('/api/questions/bank', methods=['GET'])
def get_question_bank_api():
    """
    GET /api/question-bank
    Retrieves saved questions from Question Bank. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can access Question Bank."}), 403

    filters = {
        "subject": request.args.get('subject'),
        "department": request.args.get('department'),
        "academic_year": request.args.get('academic_year'),
        "semester": request.args.get('semester'),
        "unit": request.args.get('unit'),
        "topic": request.args.get('topic'),
        "marks": request.args.get('marks'),
        "difficulty": request.args.get('difficulty'),
        "question_type": request.args.get('question_type'),
        "bloom_level": request.args.get('bloom_level'),
        "concept": request.args.get('concept'),
        "search": request.args.get('search')
    }

    success, result, status_code = get_question_bank(user_id, filters)
    return jsonify(result), status_code


@question_bp.route('/api/question-bank/<int:question_id>', methods=['DELETE'])
def remove_question_bank_api(question_id):
    """
    DELETE /api/question-bank/<id>
    Removes question from Question Bank. Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can modify Question Bank."}), 403

    success, result, status_code = remove_from_question_bank(question_id, user_id)
    return jsonify(result), status_code

@question_bp.route('/api/questions/generate', methods=['POST'])
@question_bp.route('/api/ai/generate-questions', methods=['POST'])
def generate_questions_api():
    """
    POST /api/questions/generate or POST /api/ai/generate-questions
    Generates preview questions from uploaded materials, syllabus, or question bank.
    Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate questions."}), 403

    uploaded_file = (
        request.files.get('image') or 
        request.files.get('file') or 
        request.files.get('diagram') or 
        request.files.get('resourceFile')
    )
    if uploaded_file or (request.form and (request.form.get('diagram_mode') or request.form.get('question_type') == 'Diagram Interpretation')):
        data = request.form.to_dict() if request.form else {}
        success, result, status_code = generate_image_questions_service(user_id, uploaded_file, data)
        return jsonify(result), status_code

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_questions_service(user_id, data)
    return jsonify(result), status_code

@question_bp.route('/api/questions/generate-image', methods=['POST'])
def generate_image_questions_api():
    """
    POST /api/questions/generate-image
    Generates preview questions from an uploaded diagram/image file.
    Accepts multipart/form-data with 'image' or 'file' and metadata fields.
    Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate diagram questions."}), 403

    uploaded_file = (
        request.files.get('image') or 
        request.files.get('file') or 
        request.files.get('diagram') or 
        request.files.get('resourceFile')
    )
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    success, result, status_code = generate_image_questions_service(user_id, uploaded_file, data)
    return jsonify(result), status_code

@question_bp.route('/api/questions/analyze-image', methods=['POST'])
@question_bp.route('/api/questions/analyze', methods=['POST'])
@question_bp.route('/api/images/analyze', methods=['POST'])
def analyze_image_api():
    """
    POST /api/questions/analyze-image
    Analyzes an uploaded diagram/image file, extracting visual dimensions, format,
    description/OCR context, and identifying potential diagram components.
    Role: Faculty only.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can analyze diagram images."}), 403

    uploaded_file = (
        request.files.get('image') or 
        request.files.get('file') or 
        request.files.get('diagram') or 
        request.files.get('resourceFile')
    )
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    success, result, status_code = analyze_image_service(user_id, uploaded_file, data)
    return jsonify(result), status_code
