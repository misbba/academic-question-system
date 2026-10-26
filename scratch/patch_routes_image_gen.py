import os

routes_file = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\question_routes.py"
with open(routes_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update import
old_import = "from services.question_service import (\n    generate_questions_service,"
new_import = "from services.question_service import (\n    generate_questions_service,\n    generate_image_questions_service,"

if "generate_image_questions_service" not in content:
    if old_import in content:
        content = content.replace(old_import, new_import, 1)
    else:
        # try CRLF
        old_import_crlf = "from services.question_service import (\r\n    generate_questions_service,"
        new_import_crlf = "from services.question_service import (\r\n    generate_questions_service,\r\n    generate_image_questions_service,"
        content = content.replace(old_import_crlf, new_import_crlf, 1)

# 2. Add /api/questions/generate-image route and update generate_questions_api to handle multipart
image_route_code = """

@question_bp.route('/api/questions/generate-image', methods=['POST'])
def generate_image_questions_api():
    \"\"\"
    POST /api/questions/generate-image
    Generates preview questions from an uploaded diagram/image file.
    Accepts multipart/form-data with 'image' or 'file' and metadata fields.
    Role: Faculty only.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate diagram questions."}), 403

    uploaded_file = request.files.get('image') or request.files.get('file')
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})
    success, result, status_code = generate_image_questions_service(user_id, uploaded_file, data)
    return jsonify(result), status_code
"""

# Check if route already exists
if "/api/questions/generate-image" not in content:
    # also update generate_questions_api to support multipart image upload if sent to /api/questions/generate
    old_gen = """@question_bp.route('/api/questions/generate', methods=['POST'])
@question_bp.route('/api/ai/generate-questions', methods=['POST'])
def generate_questions_api():
    \"\"\"
    POST /api/questions/generate or POST /api/ai/generate-questions
    Generates preview questions from uploaded materials, syllabus, or question bank.
    Role: Faculty only.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate questions."}), 403

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_questions_service(user_id, data)
    return jsonify(result), status_code"""

    new_gen = """@question_bp.route('/api/questions/generate', methods=['POST'])
@question_bp.route('/api/ai/generate-questions', methods=['POST'])
def generate_questions_api():
    \"\"\"
    POST /api/questions/generate or POST /api/ai/generate-questions
    Generates preview questions from uploaded materials, syllabus, or question bank.
    Role: Faculty only.
    \"\"\"
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
    if role != 'faculty':
        return jsonify({"status": "error", "message": "Forbidden. Only Faculty members can generate questions."}), 403

    uploaded_file = request.files.get('image') or request.files.get('file')
    if uploaded_file or (request.form and (request.form.get('diagram_mode') or request.form.get('question_type') == 'Diagram Interpretation')):
        data = request.form.to_dict() if request.form else {}
        success, result, status_code = generate_image_questions_service(user_id, uploaded_file, data)
        return jsonify(result), status_code

    data = request.get_json(silent=True) or {}
    success, result, status_code = generate_questions_service(user_id, data)
    return jsonify(result), status_code""" + image_route_code

    # normalize line endings for replacement
    content_lf = content.replace("\r\n", "\n")
    if old_gen in content_lf:
        content_lf = content_lf.replace(old_gen, new_gen)
        # restore CRLF if original had it
        if "\r\n" in content:
            content = content_lf.replace("\n", "\r\n")
        else:
            content = content_lf
    else:
        # Just append image_route_code
        content = content + "\n" + image_route_code

with open(routes_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated backend/routes/question_routes.py successfully")
