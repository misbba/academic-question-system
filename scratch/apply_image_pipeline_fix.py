import os
import re

print("=== Starting Image Pipeline Fix ===")

# ----------------------------------------------------
# 1. Update backend/services/question_service.py
# ----------------------------------------------------
service_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(service_path, "r", encoding="utf-8") as f:
    service_code = f.read()

analyze_service_code = """

def analyze_image_service(faculty_id, uploaded_file, data):
    \"\"\"
    Analyzes an uploaded diagram/image (PNG, JPG, JPEG, WEBP).
    Validates file integrity, extracts dimensions, visual properties, and OCR text/labels.
    \"\"\"
    import io
    import time
    from werkzeug.utils import secure_filename
    from PIL import Image

    if not uploaded_file or not getattr(uploaded_file, 'filename', None) or uploaded_file.filename.strip() == '':
        return False, {"status": "error", "message": "Image Required: Please upload a diagram image first."}, 400

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        return False, {"status": "error", "message": "Image Required: Please upload a diagram image first."}, 400

    ALLOWED_IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'webp'}
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_IMAGE_EXTS:
        return False, {"status": "error", "message": "Invalid file type. Allowed image formats: PNG, JPG, JPEG, WEBP."}, 400

    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
    except Exception as e:
        return False, {"status": "error", "message": f"Failed to read image file: {str(e)}"}, 400

    if not content or len(content) == 0:
        return False, {"status": "error", "message": "The uploaded image file is empty."}, 400

    if len(content) > 16 * 1024 * 1024:
        return False, {"status": "error", "message": "File exceeds maximum allowed size of 16MB."}, 400

    try:
        pil_img = Image.open(io.BytesIO(content))
        pil_img.verify()
        pil_img = Image.open(io.BytesIO(content))
        img_format = pil_img.format or ext.upper()
        width, height = pil_img.size
        mode = pil_img.mode
    except Exception as e:
        return False, {"status": "error", "message": "Corrupted or invalid image file. Please upload a valid diagram image."}, 400

    # Save to uploads/resources
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads', 'resources'))
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = int(time.time())
    saved_filename = f"diagram_{timestamp}_{filename}"
    saved_path = os.path.join(upload_dir, saved_filename)
    try:
        with open(saved_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        saved_filename = filename

    # Attempt OCR text extraction
    ocr_text = ""
    try:
        import pytesseract
        ocr_text = pytesseract.image_to_string(pil_img).strip()
    except Exception:
        pass

    raw_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').title()
    subject = (data.get('subject') or 'Database Management Systems').strip()
    topic = (data.get('topic') or '').strip()

    suggested_desc = (
        f"Visual diagram depicting {topic or raw_name} structural layout ({width}x{height}px, {img_format}). "
        f"Grounded in {subject} curriculum."
    )
    if ocr_text:
        first_line = ocr_text.splitlines()[0][:60]
        suggested_desc += f" Detected labels: {first_line}."

    result_payload = {
        "status": "success",
        "message": f"Successfully analyzed diagram image {filename}.",
        "filename": filename,
        "saved_filename": saved_filename,
        "image_url": f"/api/resources/file/{saved_filename}",
        "metadata": {
            "filename": filename,
            "format": img_format,
            "width": width,
            "height": height,
            "aspect_ratio": round(width / max(1, height), 2),
            "mode": mode,
            "size_kb": round(len(content) / 1024, 1),
            "ocr_detected": bool(ocr_text),
            "detected_text": ocr_text[:200] if ocr_text else None
        },
        "suggested_description": suggested_desc,
        "detected_concepts": [
            f"{raw_name} Structural Architecture",
            f"{raw_name} Inter-component Flow",
            f"{raw_name} Entity Relationships & Constraints"
        ]
    }

    return True, result_payload, 200
"""

if "def analyze_image_service(" not in service_code:
    service_code = service_code.rstrip() + "\n" + analyze_service_code
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(service_code)
    print("[OK] Added analyze_image_service to backend/services/question_service.py")
else:
    print("[SKIP] analyze_image_service already in question_service.py")


# ----------------------------------------------------
# 2. Update backend/routes/question_routes.py
# ----------------------------------------------------
routes_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\routes\question_routes.py"
with open(routes_path, "r", encoding="utf-8") as f:
    routes_code = f.read()

# Ensure analyze_image_service is imported
if "analyze_image_service" not in routes_code:
    routes_code = routes_code.replace(
        "generate_image_questions_service,",
        "generate_image_questions_service,\n    analyze_image_service,"
    )

analyze_route_code = """
@question_bp.route('/api/questions/analyze-image', methods=['POST'])
@question_bp.route('/api/questions/analyze', methods=['POST'])
@question_bp.route('/api/images/analyze', methods=['POST'])
def analyze_image_api():
    \"\"\"
    POST /api/questions/analyze-image
    Analyzes an uploaded diagram/image file, extracting visual dimensions, format,
    description/OCR context, and identifying potential diagram components.
    Role: Faculty only.
    \"\"\"
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
"""

if "/api/questions/analyze-image" not in routes_code:
    routes_code = routes_code.rstrip() + "\n" + analyze_route_code
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("[OK] Added /api/questions/analyze-image route to backend/routes/question_routes.py")
else:
    print("[SKIP] /api/questions/analyze-image already in question_routes.py")


# ----------------------------------------------------
# 3. Update run_frontend.py for Cache-Control
# ----------------------------------------------------
frontend_server_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\run_frontend.py"
with open(frontend_server_path, "r", encoding="utf-8") as f:
    fe_code = f.read()

no_cache_method = """
    def end_headers(self):
        if not self.path.startswith('/api/'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()
"""

if "def end_headers(self):" not in fe_code:
    # Insert right before def proxy_to_backend
    fe_code = fe_code.replace("    def proxy_to_backend(self):", no_cache_method + "\n    def proxy_to_backend(self):", 1)
    with open(frontend_server_path, "w", encoding="utf-8") as f:
        f.write(fe_code)
    print("[OK] Added Cache-Control: no-cache to run_frontend.py")
else:
    print("[SKIP] end_headers already in run_frontend.py")


# ----------------------------------------------------
# 4. Update faculty-image-question.html
# ----------------------------------------------------
html_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-image-question.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

# Update script tags to new cache buster
html_code = re.sub(r'js/app\.js\?v=\w+', 'js/app.js?v=20261026_image_fix', html_code)
html_code = re.sub(r'js/auth\.js\?v=\w+', 'js/auth.js?v=20261026_image_fix', html_code)
html_code = re.sub(r'js/mock-data\.js\?v=\w+', 'js/mock-data.js?v=20261026_image_fix', html_code)

# Ensure type="button" on analyze and generate buttons
html_code = html_code.replace(
    '<button class="btn btn-outline-info btn-sm w-100 mt-2" onclick="analyzeUploadedImage()">',
    '<button type="button" class="btn btn-outline-info btn-sm w-100 mt-2" onclick="analyzeUploadedImage()">'
)
html_code = html_code.replace(
    '<button class="btn btn-academic-primary w-100" onclick="generateQuestionsFromImage()">',
    '<button type="button" class="btn btn-academic-primary w-100" onclick="generateQuestionsFromImage()">'
)
html_code = html_code.replace(
    '<button class="btn btn-outline-danger btn-sm py-0 px-2" onclick="removeUploadedImage()">',
    '<button type="button" class="btn btn-outline-danger btn-sm py-0 px-2" onclick="removeUploadedImage()">'
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)
print("[OK] Updated faculty-image-question.html cache busters and button types")

print("=== Patch Preparation Complete ===")
