import os
import sys
import json

backend_dir = os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app

app = create_app()
client = app.test_client()

# Login as Murugan
res = client.post('/api/auth/login', json={"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"})
print("Login status:", res.status_code, res.get_json().get('status'))

# Now test generate questions
payload = {
    "department": "Artificial Intelligence & Data Science",
    "subject": "Database Management Systems",
    "academic_year": "2025-2026",
    "semester": "Semester 6",
    "unit": "All Units (Complete Syllabus)",
    "topic": "",
    "num_questions": 10,
    "question_type": "Short Answer",
    "bloom_level": "Auto Select",
    "diff_easy": 30,
    "diff_medium": 50,
    "diff_hard": 20,
    "resource_id": None,
    "use_question_bank": False
}

res = client.post('/api/questions/generate', json=payload)
print("Generate status code:", res.status_code)
print("Generate response:", res.get_json())
