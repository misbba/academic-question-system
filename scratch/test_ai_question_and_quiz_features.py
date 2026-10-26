import urllib.request
import urllib.parse
import json
import http.cookiejar
import sys
import os
import mimetypes

BASE_URL = "http://localhost:5000"

def create_session():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    return opener

def post_json(opener, path, data):
    safe_path = urllib.parse.quote(path, safe='/?&=')
    url = f"{BASE_URL}{safe_path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def post_multipart(opener, path, fields, files):
    safe_path = urllib.parse.quote(path, safe='/?&=')
    url = f"{BASE_URL}{safe_path}"
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    for k, v in fields.items():
        body.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode('utf-8'))
    for k, filepath in files.items():
        filename = os.path.basename(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        with open(filepath, 'rb') as f:
            file_data = f.read()
        body.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{filename}"\r\nContent-Type: {mime_type}\r\n\r\n'.encode('utf-8')
            + file_data + b'\r\n'
        )
    body.append(f'--{boundary}--\r\n'.encode('utf-8'))
    data = b''.join(body)

    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
        method='POST'
    )
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def get_json(opener, path):
    safe_path = urllib.parse.quote(path, safe='/?&=')
    url = f"{BASE_URL}{safe_path}"
    req = urllib.request.Request(url, method='GET')
    try:
        with opener.open(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))

def run_tests():
    print("=" * 60)
    print("AI Question Generator & Quiz Generator End-to-End Verification")
    print("=" * 60)

    # 1. Health check
    opener = create_session()
    code, data = get_json(opener, "/api/health")
    assert code == 200, f"Health check failed: {code} {data}"
    print("[PASS] 1. Backend Health Check OK")

    # 2. Login as Murugan (Faculty)
    code, data = post_json(opener, "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert code == 200, f"Faculty login failed: {code} {data}"
    print(f"[PASS] 2. Faculty Login Succeeded: {data['user']['full_name']} ({data['user']['email']})")

    # 3. Test Missing Material Rule
    print("\n--- Testing Rule: Missing Source Material Explanation ---")
    gen_empty_payload = {
        "department": "Custom Department of Quantum Studies",
        "subject": "Quantum Computing and Nanotechnology",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "All Units (Complete Syllabus)",
        "topic": "",
        "num_questions": 10
    }
    code, data = post_json(opener, "/api/questions/generate", gen_empty_payload)
    assert code == 400 and data.get('source_missing') is True, f"Expected 400 source_missing, got {code} {data}"
    print(f"[PASS] 3. Correctly explained missing source content when no material is uploaded:")
    print(f"   Message: {data.get('message')}")

    # 4. Upload Syllabus Material for Murugan
    print("\n--- Uploading Official Syllabus Material ---")
    docx_file = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\uploads\resources\1792942486_23CST504_-_DISTRIBUTED_COMPUTING.docx"
    code, data = post_multipart(
        opener,
        "/api/resources",
        {
            "subject": "Distributed Computing",
            "department": "Custom Department of Advanced Computing",
            "academic_year": "2025-2026",
            "semester": "Semester 6",
            "unit": "All Units (Complete Syllabus)",
            "topic": "Complete Syllabus",
            "resource_type": "Syllabus",
            "description": "Official 5-Unit Syllabus for Distributed Computing"
        },
        {"file": docx_file}
    )
    assert code == 201, f"Failed to upload syllabus: {code} {data}"
    res_obj = data.get('resource', {})
    dist_comp_res_id = res_obj.get('id')
    print(f"[PASS] 4. Uploaded Syllabus docx to MySQL: Resource ID {dist_comp_res_id}, File: {res_obj.get('file_name')}")

    # 5. Generate Grounded Questions from Uploaded Syllabus
    print("\n--- Testing Grounded Question Generation from Uploaded Syllabus ---")
    gen_payload = {
        "department": "Custom Department of Advanced Computing",
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
        "resource_id": dist_comp_res_id
    }
    code, data = post_json(opener, "/api/questions/generate", gen_payload)
    assert code == 200, f"Question generation failed: {code} {data}"
    questions = data.get('questions', [])
    assert len(questions) == 10, f"Expected 10 questions, got {len(questions)}"
    print(f"[PASS] 5. Generated {len(questions)} grounded questions successfully.")
    print(f"   Sample Q1: {questions[0]['text']}")
    print(f"   Sample Q1 Concept: {questions[0]['concept']} | Unit: {questions[0]['unit']} | Bloom: {questions[0]['bloom_level']}")

    # Check that no question text is duplicated
    texts = [q['text'] for q in questions]
    assert len(set(texts)) == len(texts), "Duplicate questions found in generated set!"
    print(f"[PASS] 6. Verified 0 duplicate questions across generated set.")

    # 6. Save generated questions to Question Bank
    code, data = post_json(opener, "/api/question-bank", {"questions": questions})
    assert code == 200, f"Save to question bank failed: {code} {data}"
    print(f"[PASS] 7. Saved questions to Faculty Question Bank. Count: {data.get('saved_count')}")

    # 7. Verify Question Bank Retrieval
    code, data = get_json(opener, "/api/question-bank?subject=Distributed Computing")
    assert code == 200
    bank_questions = data.get('questions', [])
    assert len(bank_questions) >= 10, "Question bank retrieval failed"
    print(f"[PASS] 8. Retrieved {len(bank_questions)} questions from Question Bank for faculty Murugan.")

    # 8. Test Insufficient Source Handling
    print("\n--- Testing Insufficient Source Content Protection ---")
    insuf_payload = {
        "department": "Custom Department of Advanced Computing",
        "subject": "Distributed Computing",
        "unit": "Unit I — INTRODUCTION",
        "topic": "Motivation",
        "num_questions": 30,  # Only 1 candidate available
        "resource_id": dist_comp_res_id
    }
    code, data = post_json(opener, "/api/questions/generate", insuf_payload)
    assert code == 400, f"Expected 400 for insufficient source, got {code}"
    assert data.get('insufficient_source') is True, "Expected insufficient_source flag"
    print(f"[PASS] 9. Insufficient Source correctly rejected without hallucinating or duplicating:")
    print(f"   Notice: {data.get('message')}")

    # 9. Test 30-Minute, 30-Mark Quiz Generator
    print("\n--- Testing Quiz Generator (30 Minutes, 30 Marks) ---")
    quiz_gen_payload = {
        "title": "Distributed Computing Comprehensive Assessment",
        "department": "Custom Department of Advanced Computing",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "All Units (Complete Syllabus)",
        "topic": "",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 30,
        "resource_id": dist_comp_res_id
    }
    code, data = post_json(opener, "/api/quizzes/generate", quiz_gen_payload)
    assert code == 200, f"Quiz generation failed: {code} {data}"
    quiz_questions = data.get('questions', [])
    assert len(quiz_questions) == 30, f"Expected 30 questions, got {len(quiz_questions)}"
    quiz_preview = data.get('quiz', {})
    assert quiz_preview.get('duration_minutes') == 30, f"Expected 30 mins duration, got {quiz_preview.get('duration_minutes')}"
    assert quiz_preview.get('total_marks') == 30, f"Expected 30 total marks, got {quiz_preview.get('total_marks')}"

    # Verify no duplicates in 30 questions
    quiz_texts = [q['text'] for q in quiz_questions]
    assert len(set(quiz_texts)) == len(quiz_texts), "Duplicate questions found in 30-question quiz!"
    print(f"[PASS] 10. Generated 30 distinct questions (30 Marks, 30 Minutes duration). 0 duplicates.")
    print(f"   Sample Quiz Q1: {quiz_questions[0]['text']}")
    print(f"   Options: {quiz_questions[0]['options_strings']}")
    print(f"   Correct Answer: {quiz_questions[0]['correctAnswer']}")

    # 10. Publish Quiz
    code, data = post_json(opener, "/api/quizzes", {
        "title": quiz_preview['title'],
        "subject": quiz_preview['subject'],
        "department": quiz_preview['department'],
        "academic_year": quiz_preview['academic_year'],
        "semester": quiz_preview['semester'],
        "unit": quiz_preview['unit'],
        "topic": quiz_preview['topic'],
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 30,
        "status": "Published",
        "questions": quiz_questions
    })
    assert code == 201, f"Publish quiz failed: {code} {data}"
    created_quiz = data.get('quiz', {})
    quiz_id = created_quiz['id']
    print(f"[PASS] 11. Quiz Published to MySQL: ID {quiz_id}, Code {created_quiz['quiz_code']}, Duration {created_quiz['duration_minutes']} Mins, Marks {created_quiz['total_marks']}")

    # 11. Test Student View & Live Timed Quiz Attempt
    print("\n--- Testing Student Quiz Attempt & Timer Workflow ---")
    student_opener = create_session()
    code, data = post_json(student_opener, "/api/auth/login", {
        "email": "student.step9d@university.edu",
        "password": "Password123!",
        "role": "student"
    })
    if code != 200:
        post_json(student_opener, "/api/auth/register", {
            "full_name": "Nisha Student",
            "email": "nisha_quiz_test@vsb.com",
            "password": "Password123!",
            "role": "student",
            "department": "Artificial Intelligence & Data Science",
            "semester": "Semester 6",
            "academic_year": "2025-2026"
        })
        code, data = post_json(student_opener, "/api/auth/login", {
            "email": "nisha_quiz_test@vsb.com",
            "password": "Password123!",
            "role": "student"
        })
    assert code == 200, f"Student login failed: {code} {data}"
    print(f"[PASS] 12. Student Login Succeeded: {data['user']['full_name']}")

    # Student retrieves published quizzes
    code, data = get_json(student_opener, "/api/quizzes")
    assert code == 200
    student_quizzes = data.get('quizzes', [])
    found_quiz = next((q for q in student_quizzes if q['id'] == quiz_id), None)
    assert found_quiz is not None, "Student could not see published quiz!"
    assert found_quiz['duration_minutes'] == 30, f"Expected 30 mins, got {found_quiz['duration_minutes']}"
    assert found_quiz['total_marks'] == 30, f"Expected 30 marks, got {found_quiz['total_marks']}"
    print(f"[PASS] 13. Student retrieved published 30-min quiz with 30 marks.")

    # Student submits quiz attempt with answers
    # Answer 28 correct, 2 incorrect/unanswered
    student_answers = {}
    for i, q in enumerate(quiz_questions):
        if i < 28:
            student_answers[str(i)] = q['correctIndex']
        elif i == 28:
            student_answers[str(i)] = (q['correctIndex'] + 1) % 4  # Wrong
        # Question 29 is left unanswered

    code, data = post_json(student_opener, f"/api/quizzes/{quiz_id}/submit", {
        "answers": student_answers
    })
    assert code == 201, f"Student quiz submission failed: {code} {data}"
    attempt = data.get('attempt', {})
    assert attempt.get('score') == "28 / 30", f"Expected '28 / 30', got {attempt.get('score')}"
    print(f"[PASS] 14. Student Quiz Attempt evaluated and recorded: Score {attempt.get('score')}, Percentage {attempt.get('percentage')}")

    # 12. Test Faculty & Student Data Isolation
    print("\n--- Testing Faculty and Student Data Isolation ---")
    # Faculty A (Murugan) checks quiz attempts
    code, data = get_json(opener, "/api/quizzes/attempts")
    assert code == 200
    faculty_attempts = data.get('attempts', [])
    assert any(a['quizId'] == created_quiz['quiz_code'] for a in faculty_attempts), "Faculty should see attempts on their quiz"
    print(f"[PASS] 15. Faculty Murugan can see attempts on his own quiz ({len(faculty_attempts)} attempt(s)).")

    # Faculty B (Alan Turing) checks quizzes
    turing_opener = create_session()
    code, data = post_json(turing_opener, "/api/auth/login", {
        "email": "turing@university.edu",
        "password": "Password123!",
        "role": "faculty"
    })
    assert code == 200
    code, data = get_json(turing_opener, "/api/quizzes")
    assert code == 200
    turing_quizzes = data.get('quizzes', [])
    assert not any(q['id'] == quiz_id for q in turing_quizzes), "Isolation failure: Turing saw Murugan's quiz!"
    print("[PASS] 16. Faculty Data Isolation: Turing cannot see Murugan's private quizzes.")

    code, data = get_json(turing_opener, "/api/quizzes/attempts")
    assert code == 200
    turing_attempts = data.get('attempts', [])
    assert not any(a['quizId'] == created_quiz['quiz_code'] for a in turing_attempts), "Isolation failure: Turing saw attempts on Murugan's quiz!"
    print("[PASS] 17. Faculty Data Isolation: Turing cannot see attempts on Murugan's quizzes.")

    print("\n" + "=" * 60)
    print("ALL 17 VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
