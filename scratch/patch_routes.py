import os

# 1. Patch question_routes.py
q_routes_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\question_routes.py'
with open(q_routes_path, 'r', encoding='utf-8') as f:
    q_content = f.read()

if 'generate_questions_service' not in q_content:
    q_content = q_content.replace(
        'from services.question_service import (',
        'from services.question_service import (\n    generate_questions_service,'
    )
    
    q_endpoint = '''
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

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_questions_service(user_id, data)
    return jsonify(result), status_code
'''
    q_content += q_endpoint

    with open(q_routes_path, 'w', encoding='utf-8') as f:
        f.write(q_content)
    print("question_routes.py patched successfully.")
else:
    print("question_routes.py already has generate_questions_service.")


# 2. Patch quiz_routes.py
qz_routes_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\quiz_routes.py'
with open(qz_routes_path, 'r', encoding='utf-8') as f:
    qz_content = f.read()

if 'generate_quiz_service' not in qz_content:
    qz_content = qz_content.replace(
        'from services.quiz_service import (',
        'from services.quiz_service import (\n    generate_quiz_service,'
    )

    old_attempts_route = '''@quiz_bp.route('/api/quizzes/attempts', methods=['GET'])
def get_quiz_attempts_api():
    """
    GET /api/quizzes/attempts
    Retrieves quiz attempts for logged-in student or all attempts for faculty.
    """
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401

    student_filter = user_id if role == 'student' else None
    success, result, status_code = get_student_quiz_attempts(student_filter)
    return jsonify(result), status_code'''

    new_attempts_route = '''@quiz_bp.route('/api/quizzes/attempts', methods=['GET'])
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
    return jsonify(result), status_code'''

    if old_attempts_route in qz_content:
        qz_content = qz_content.replace(old_attempts_route, new_attempts_route, 1)

    qz_endpoint = '''
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
'''
    qz_content += qz_endpoint

    with open(qz_routes_path, 'w', encoding='utf-8') as f:
        f.write(qz_content)
    print("quiz_routes.py patched successfully.")
else:
    print("quiz_routes.py already has generate_quiz_service.")
