import os
import sys

backend_dir = os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app

app = create_app()
client = app.test_client()

client.post('/api/auth/login', json={"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"})

# Test Distributed Computing
payload_dc = {
    "department": "Artificial Intelligence & Data Science",
    "subject": "Distributed Computing",
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

res = client.post('/api/questions/generate', json=payload_dc)
print("DC Generate status code:", res.status_code)
d = res.get_json()
print("DC Generate status:", d.get('status'))
if d.get('status') == 'success':
    print(f"Generated {len(d.get('questions', []))} questions successfully!")
    for q in d.get('questions', [])[:3]:
        print(" ", q['question'])
else:
    print("DC Error message:", d.get('message'))
