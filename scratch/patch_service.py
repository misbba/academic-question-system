import sys

path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update create_question_paper
old_create = """    title = (data.get('title') or data.get('paper_title') or '').strip()
    subject = (data.get('subject') or data.get('course') or '').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()
    exam_type = (data.get('exam_type') or 'Model Examination').strip()
    exam_date = data.get('exam_date') or None
    exam_time = (data.get('exam_time') or '10:00 AM - 01:00 PM').strip()
    duration = (data.get('duration') or '3 Hours').strip()
    total_marks = int(data.get('total_marks') or data.get('max_marks') or 100)
    instructions = (data.get('instructions') or '').strip()
    status = (data.get('status') or 'Draft').strip()"""

new_create = """    title = str(data.get('title') or data.get('paper_title') or '').strip()
    subject = str(data.get('subject') or data.get('course') or '').strip()
    department = str(data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = str(data.get('academic_year') or '2025-2026').strip()
    sem_val = data.get('semester') or 'Semester 6'
    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()
    exam_type = str(data.get('exam_type') or 'Model Examination').strip()
    exam_date = data.get('exam_date') or None
    exam_time = str(data.get('exam_time') or '10:00 AM - 01:00 PM').strip()
    duration = str(data.get('duration') or '3 Hours').strip()
    total_marks = int(data.get('total_marks') or data.get('max_marks') or 100)
    instructions = str(data.get('instructions') or '').strip()
    status = str(data.get('status') or 'Draft').strip()"""

# 2. Update update_question_paper
old_update = """    title = (data.get('title') or data.get('paper_title') or existing_paper['title']).strip()
    subject = (data.get('subject') or data.get('course') or existing_paper['subject']).strip()
    department = (data.get('department') or existing_paper['department']).strip()
    academic_year = (data.get('academic_year') or existing_paper['academic_year']).strip()
    semester = (data.get('semester') or existing_paper['semester']).strip()
    exam_type = (data.get('exam_type') or existing_paper['exam_type']).strip()
    raw_exam_date = data.get('exam_date') if data.get('exam_date') is not None else existing_paper.get('exam_date')
    exam_date = raw_exam_date if (raw_exam_date and str(raw_exam_date).strip() not in ['', 'None']) else None
    exam_time = (data.get('exam_time') or existing_paper['exam_time']).strip()
    duration = (data.get('duration') or existing_paper['duration']).strip()
    total_marks = int(data.get('total_marks') or data.get('max_marks') or existing_paper['total_marks'])
    instructions = (data.get('instructions') or existing_paper['instructions']).strip()
    status = (data.get('status') or existing_paper['status']).strip()"""

new_update = """    title = str(data.get('title') or data.get('paper_title') or existing_paper['title']).strip()
    subject = str(data.get('subject') or data.get('course') or existing_paper['subject']).strip()
    department = str(data.get('department') or existing_paper['department']).strip()
    academic_year = str(data.get('academic_year') or existing_paper['academic_year']).strip()
    sem_val = data.get('semester') or existing_paper['semester']
    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()
    exam_type = str(data.get('exam_type') or existing_paper['exam_type']).strip()
    raw_exam_date = data.get('exam_date') if data.get('exam_date') is not None else existing_paper.get('exam_date')
    exam_date = raw_exam_date if (raw_exam_date and str(raw_exam_date).strip() not in ['', 'None']) else None
    exam_time = str(data.get('exam_time') or existing_paper['exam_time']).strip()
    duration = str(data.get('duration') or existing_paper['duration']).strip()
    total_marks = int(data.get('total_marks') or data.get('max_marks') or existing_paper['total_marks'])
    instructions = str(data.get('instructions') or existing_paper['instructions']).strip()
    status = str(data.get('status') or existing_paper['status']).strip()"""

# 3. Update generate_template_paper
old_template = """    template = str(data.get('template') or data.get('template_type') or 'internal_test').lower().strip()
    subject = (data.get('subject') or 'Database Management Systems').strip()
    department = (data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = (data.get('academic_year') or '2025-2026').strip()
    semester = (data.get('semester') or 'Semester 6').strip()"""

new_template = """    template = str(data.get('template') or data.get('template_type') or 'internal_test').lower().strip()
    subject = str(data.get('subject') or 'Database Management Systems').strip()
    department = str(data.get('department') or 'Artificial Intelligence & Data Science').strip()
    academic_year = str(data.get('academic_year') or '2025-2026').strip()
    sem_val = data.get('semester') or 'Semester 6'
    semester = f"Semester {sem_val}" if str(sem_val).isdigit() else str(sem_val).strip()"""

content_lf = content.replace("\r\n", "\n")

assert old_create.replace("\r\n", "\n") in content_lf, "old_create not found"
content_lf = content_lf.replace(old_create.replace("\r\n", "\n"), new_create.replace("\r\n", "\n"))

assert old_update.replace("\r\n", "\n") in content_lf, "old_update not found"
content_lf = content_lf.replace(old_update.replace("\r\n", "\n"), new_update.replace("\r\n", "\n"))

assert old_template.replace("\r\n", "\n") in content_lf, "old_template not found"
content_lf = content_lf.replace(old_template.replace("\r\n", "\n"), new_template.replace("\r\n", "\n"))

content_crlf = content_lf.replace("\n", "\r\n")
with open(path, "w", encoding="utf-8") as f:
    f.write(content_crlf)

print("Patch applied successfully.")
