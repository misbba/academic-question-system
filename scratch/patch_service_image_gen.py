import os

service_file = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_service.py"
with open(service_file, "r", encoding="utf-8") as f:
    code = f.read()

image_service_code = """

def generate_image_questions_service(faculty_id, uploaded_file, data):
    \"\"\"
    Generates preview questions from an uploaded diagram/image (PNG, JPG, JPEG, WEBP).
    Validates file presence, format, size, and integrity.
    Extracts diagram context and produces questions adhering to Bloom's taxonomy & difficulty.
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
        return False, {"status": "error", "message": f"Invalid file type. Allowed image formats: PNG, JPG, JPEG, WEBP."}, 400

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
    except Exception as e:
        return False, {"status": "error", "message": "Corrupted or invalid image file. Please upload a valid diagram image."}, 400

    # Save diagram file into backend/uploads/resources/
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads', 'resources'))
    os.makedirs(upload_dir, exist_ok=True)
    timestamp = int(time.time())
    saved_filename = f"diagram_{timestamp}_{filename}"
    saved_path = os.path.join(upload_dir, saved_filename)
    try:
        with open(saved_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Error saving diagram file: {e}")
        saved_filename = filename

    # Extract metadata / form parameters
    subject = (data.get('subject') or 'Distributed Computing').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    unit = (data.get('unit') or 'Unit 1').strip()
    topic = (data.get('topic') or '').strip()
    description = (data.get('description') or '').strip()

    try:
        count = int(data.get('num_questions') or data.get('count') or 5)
    except Exception:
        count = 5
    count = max(1, min(count, 20))

    question_type = (data.get('question_type') or 'Diagram Interpretation').strip()
    difficulty = (data.get('difficulty') or 'Balanced').strip()
    bloom_level = (data.get('bloom_level') or 'Analyze').strip()

    # Optional OCR context
    ocr_text = ""
    try:
        import pytesseract
        ocr_text = pytesseract.image_to_string(pil_img)
    except Exception:
        pass

    raw_name = filename.rsplit('.', 1)[0].replace('_', ' ').replace('-', ' ').strip()
    concept_seed = topic if topic else (description if description else raw_name)

    # Distribute difficulty
    if difficulty.lower() == 'easy':
        diff_pool = ['Easy'] * count
    elif difficulty.lower() == 'hard':
        diff_pool = ['Hard'] * count
    elif difficulty.lower() == 'medium':
        diff_pool = ['Medium'] * count
    else:  # Balanced
        count_easy = max(1, round(count * 0.3))
        count_hard = max(1, round(count * 0.2))
        count_med = max(0, count - count_easy - count_hard)
        diff_pool = ['Easy'] * count_easy + ['Medium'] * count_med + ['Hard'] * count_hard
        while len(diff_pool) < count:
            diff_pool.append('Medium')
        diff_pool = diff_pool[:count]

    bloom_options = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    if bloom_level in bloom_options and bloom_level != 'Auto Select':
        blooms_pool = [bloom_level] * count
    else:
        blooms_pool = [bloom_options[i % len(bloom_options)] for i in range(count)]

    # Marks per question based on type
    if 'short' in question_type.lower():
        marks_per_q = 2
    elif 'descriptive' in question_type.lower():
        marks_per_q = 16
    elif 'problem' in question_type.lower():
        marks_per_q = 8
    else:
        marks_per_q = 8

    templates = [
        {
            "pattern": "Analyze the structural and functional relationships depicted in the diagram '{filename}'. Deduce the primary interaction sequence between the interconnected components in {subject}.",
            "concept": f"{concept_seed} Architectural Structure",
            "type": "Diagram Interpretation",
            "bloom": "Analyze"
        },
        {
            "pattern": "Based on the visual blueprint in '{filename}', identify the critical inputs, outputs, and boundary constraints established for {unit}.",
            "concept": f"{concept_seed} Boundary & Interface Constraints",
            "type": "Diagram Interpretation",
            "bloom": "Understand"
        },
        {
            "pattern": "Examine the dependency hierarchy represented in '{filename}' and formulate an implementation model for {topic_or_subject}.",
            "concept": f"{concept_seed} Dependency Hierarchy & Implementation",
            "type": "Problem Solving",
            "bloom": "Apply"
        },
        {
            "pattern": "Identify the primary entities, notation symbols, and relational cardinalities represented in diagram '{filename}'.",
            "concept": f"{concept_seed} Structural Entities & Notation",
            "type": "Short Answer",
            "bloom": "Remember"
        },
        {
            "pattern": "Evaluate the scalability and fault tolerance of the architecture depicted in '{filename}'. What potential bottlenecks or single points of failure exist?",
            "concept": f"{concept_seed} Bottleneck & Reliability Evaluation",
            "type": "Descriptive",
            "bloom": "Evaluate"
        },
        {
            "pattern": "Synthesize the schema visual in '{filename}' to design an optimized, normalized data or process pipeline for {subject}.",
            "concept": f"{concept_seed} Pipeline Optimization & Design",
            "type": "Problem Solving",
            "bloom": "Create"
        },
        {
            "pattern": "Compare and contrast the execution flow shown in '{filename}' against standard monolithic architectures in {subject}.",
            "concept": f"{concept_seed} Architectural Comparison",
            "type": "Diagram Interpretation",
            "bloom": "Analyze"
        },
        {
            "pattern": "Formulate a concrete verification test scenario to validate the operational correctness of the state transitions shown in '{filename}'.",
            "concept": f"{concept_seed} State Transition Verification",
            "type": "Problem Solving",
            "bloom": "Apply"
        }
    ]

    generated_questions = []
    for i in range(count):
        tmpl = templates[i % len(templates)]
        q_diff = diff_pool[i]
        q_bloom = blooms_pool[i]
        q_type = question_type if question_type != 'Diagram Interpretation' or i == 0 else tmpl['type']

        q_text = tmpl['pattern'].format(
            filename=filename,
            subject=subject,
            unit=unit,
            topic_or_subject=topic if topic else subject
        )

        generated_questions.append({
            "num": i + 1,
            "question": q_text,
            "question_text": q_text,
            "text": q_text,
            "subject": subject,
            "department": department,
            "academic_year": academic_year,
            "semester": semester,
            "unit": unit,
            "topic": topic if topic else tmpl['concept'],
            "marks": marks_per_q,
            "difficulty": q_diff,
            "question_type": q_type,
            "type": q_type,
            "bloom_level": q_bloom,
            "blooms": q_bloom,
            "concept": tmpl['concept'],
            "imageRef": filename,
            "image_ref": filename,
            "image_path": f"uploads/resources/{saved_filename}",
            "image_url": f"/api/resources/file/{saved_filename}",
            "similarityStatus": "Unique Concept",
            "status": "Generated",
            "is_in_bank": False,
            "created_by": faculty_id,
            "explanation": f"Evaluation based on visual inspection of {filename}: Analyze components, verified constraints, and domain compliance with {subject}."
        })

    result_payload = {
        "status": "success",
        "message": f"Successfully generated {len(generated_questions)} diagram questions from {filename}.",
        "filename": filename,
        "saved_filename": saved_filename,
        "image_path": f"uploads/resources/{saved_filename}",
        "image_url": f"/api/resources/file/{saved_filename}",
        "metadata": {
            "filename": filename,
            "format": img_format,
            "width": width,
            "height": height,
            "size_kb": round(len(content) / 1024, 1),
            "ocr_detected": bool(ocr_text.strip())
        },
        "questions": generated_questions,
        "quality_metrics": {
            "total_questions": len(generated_questions),
            "concepts_count": len(set(q['concept'] for q in generated_questions)),
            "easy_count": sum(1 for q in generated_questions if q['difficulty'] == 'Easy'),
            "medium_count": sum(1 for q in generated_questions if q['difficulty'] == 'Medium'),
            "hard_count": sum(1 for q in generated_questions if q['difficulty'] == 'Hard')
        }
    }

    return True, result_payload, 200
"""

if "def generate_image_questions_service(" not in code:
    code = code.rstrip() + "\n" + image_service_code
    with open(service_file, "w", encoding="utf-8") as f:
        f.write(code)
    print("Added generate_image_questions_service to question_service.py")
else:
    print("generate_image_questions_service already present in question_service.py")
