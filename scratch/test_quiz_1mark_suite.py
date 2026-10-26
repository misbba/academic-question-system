import urllib.request
import urllib.parse
import json
import http.cookiejar
import os
import sys

BASE_URL = "http://localhost:5000"
BASE_DIR = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"

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

def put_json(opener, path, data):
    safe_path = urllib.parse.quote(path, safe='/?&=')
    url = f"{BASE_URL}{safe_path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='PUT'
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

def run_test_suite():
    print("=" * 70)
    print("QUIZ GENERATOR 1-MARK SUPPORT & ISOLATION VERIFICATION SUITE")
    print("=" * 70)

    # 1. Health check
    opener = create_session()
    code, data = get_json(opener, "/api/health")
    assert code == 200, f"Health check failed: {code} {data}"
    print("[PASS] 1. Backend Health Check OK")

    # 2. Login as Faculty Murugan
    code, data = post_json(opener, "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert code == 200, f"Faculty login failed: {code} {data}"
    print(f"[PASS] 2. Faculty Login Succeeded: {data['user']['full_name']}")

    # 3. Test Quiz Generation with 1 Mark per Question
    print("\n--- Testing Quiz Generation with 1-Mark Questions ---")
    quiz_gen_payload = {
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I — Characterization of Distributed Systems",
        "topic": "Remote Procedure Calls and Message Passing",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 10
    }
    code, data = post_json(opener, "/api/quizzes/generate", quiz_gen_payload)
    assert code == 200, f"Quiz generation failed: {code} {data}"
    assert data.get('status') == 'success', f"Expected success status, got: {data}"
    quiz_preview = data.get('quiz', {})
    questions = data.get('questions', [])
    assert len(questions) > 0, "No questions returned in quiz generation"
    assert quiz_preview.get('marks_per_question') == 1, f"Expected marks_per_question=1, got {quiz_preview.get('marks_per_question')}"
    assert quiz_preview.get('total_marks') == len(questions) * 1, f"Expected total_marks={len(questions)}, got {quiz_preview.get('total_marks')}"
    
    # Verify every question has 1 mark
    for idx, q in enumerate(questions):
        assert q.get('marks') == 1, f"Question {idx+1} does not have marks=1: {q}"
        assert "1 Mark" in q.get('type', ''), f"Question {idx+1} type label doesn't contain '1 Mark': {q.get('type')}"
        assert len(q.get('options', [])) == 4, f"Question {idx+1} does not have 4 options"
        assert q.get('correctAnswer') or q.get('correct_answer'), f"Question {idx+1} missing correct answer"

    # Verify AI prompt explicitly specifies 1 mark
    ai_prompt = quiz_preview.get('ai_prompt', '')
    assert "1 mark" in ai_prompt.lower() or "1 Mark" in ai_prompt, f"AI Prompt does not explicitly mention 1 mark: {ai_prompt}"
    print(f"[PASS] 3. Quiz Generation Succeeded: {len(questions)} MCQs generated, each with exactly 1 mark.")
    print(f"         AI Prompt verified: '{ai_prompt[:90]}...'")

    # 4. Save and Publish the 1-mark Quiz
    print("\n--- Testing Quiz Publishing & Storage with 1 Mark ---")
    publish_payload = {
        "title": "Distributed Computing Unit I 1-Mark Timed Quiz",
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I — Characterization of Distributed Systems",
        "topic": "Remote Procedure Calls and Message Passing",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": len(questions),
        "status": "Published",
        "questions": questions
    }
    code, data = post_json(opener, "/api/quizzes", publish_payload)
    assert code == 201, f"Quiz publish failed: {code} {data}"
    created_quiz = data.get('quiz', {})
    quiz_id = created_quiz['id']
    assert created_quiz.get('marks_per_question') == 1, f"Saved quiz marks_per_question is not 1: {created_quiz}"
    assert created_quiz.get('total_marks') == len(questions) * 1, f"Saved quiz total_marks is not {len(questions)}: {created_quiz}"
    print(f"[PASS] 4. Quiz Published to Database: ID={quiz_id}, Code={created_quiz.get('quiz_code')}, Total Marks={created_quiz.get('total_marks')} (1 Mark/Q)")

    # 5. Retrieve Quiz and verify 1-mark persistence
    print("\n--- Testing Quiz Retrieval & Question Marks Persistence ---")
    code, data = get_json(opener, f"/api/quizzes/{quiz_id}")
    assert code == 200, f"Quiz retrieval failed: {code} {data}"
    retrieved_quiz = data.get('quiz', {})
    assert retrieved_quiz.get('marks_per_question') == 1
    assert retrieved_quiz.get('total_marks') == len(questions) * 1
    for idx, q in enumerate(retrieved_quiz.get('questions', [])):
        assert q.get('marks') == 1, f"Retrieved question {idx+1} does not have marks=1: {q}"
    print("[PASS] 5. Quiz Retrieved successfully: All questions persisted with marks=1.")

    # 6. Update Quiz and verify 1-mark preservation
    print("\n--- Testing Quiz Update & Marks Preservation ---")
    code, data = put_json(opener, f"/api/quizzes/{quiz_id}", {
        "title": "DBMS Unit III 1-Mark Timed Quiz (Updated)",
        "marks_per_question": 1,
        "questions": questions
    })
    assert code == 200, f"Quiz update failed: {code} {data}"
    updated_quiz = data.get('quiz', {})
    assert updated_quiz.get('marks_per_question') == 1
    assert updated_quiz.get('total_marks') == len(questions) * 1
    print("[PASS] 6. Quiz Updated successfully with marks=1 preserved.")

    # 7. Student Attempt & Evaluation with 1-mark questions
    print("\n--- Testing Student Quiz Attempt & 1-Mark Auto-Scoring ---")
    student_opener = create_session()
    code, data = post_json(student_opener, "/api/auth/login", {
        "email": "nisha_quiz_test@vsb.com",
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
    
    # Submit student answers: 8 correct, 2 wrong
    answers = {}
    for i, q in enumerate(questions):
        if i < 8:
            answers[str(i)] = q['correctIndex']
        else:
            answers[str(i)] = (q['correctIndex'] + 1) % 4
    
    code, data = post_json(student_opener, f"/api/quizzes/{quiz_id}/submit", {"answers": answers})
    assert code == 201, f"Student quiz attempt submission failed: {code} {data}"
    attempt = data.get('attempt', {})
    expected_score_str = f"8 / {len(questions)}"
    assert attempt.get('score') == expected_score_str, f"Expected '{expected_score_str}', got '{attempt.get('score')}'"
    print(f"[PASS] 7. Student Quiz Attempt auto-scored correctly: {attempt.get('score')} ({attempt.get('percentage')}%)")

    # 8. Strict Marks Validation: AI Question Generator MUST REJECT 1 MARK
    print("\n--- Verifying AI Question Generator Strictly Rejects 1 Mark ---")
    ai_gen_1mark_payload = {
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I — Characterization of Distributed Systems",
        "topic": "Remote Procedure Calls",
        "num_questions": 5,
        "marks": "1",
        "marks_per_question": 1
    }
    code, data = post_json(opener, "/api/questions/generate", ai_gen_1mark_payload)
    assert code == 400, f"AI Question Generator should reject 1 mark, but returned HTTP {code}: {data}"
    assert "2, 8, and 16" in data.get('message', ''), f"Unexpected error message: {data}"
    print(f"[PASS] 8. AI Question Generator strictly rejected 1 mark: '{data.get('message')}'")

    # 9. Strict Marks Validation: AI Question Generator ACCEPTS 2, 8, 16 marks
    print("\n--- Verifying AI Question Generator Accepts 2, 8, and 16 Marks ---")
    for m in (2, 8, 16):
        ai_gen_valid_payload = {
            "department": "Artificial Intelligence & Data Science",
            "subject": "Distributed Computing",
            "academic_year": "2025-2026",
            "semester": "Semester 6",
            "unit": "Unit I — Characterization of Distributed Systems",
            "topic": "Remote Procedure Calls",
            "num_questions": 2,
            "marks": str(m),
            "marks_per_question": m
        }
        code, data = post_json(opener, "/api/questions/generate", ai_gen_valid_payload)
        assert code == 200, f"AI Question Generator failed for {m} marks: {code} {data}"
        print(f"         Accepted {m} marks -> generated {len(data.get('questions', []))} questions.")
    print("[PASS] 9. AI Question Generator successfully generated questions for 2, 8, and 16 marks.")

    # 10. Strict Marks Validation: Direct Question Bank Creation MUST REJECT 1 MARK
    print("\n--- Verifying Question Bank Creation Rejects 1 Mark ---")
    code, data = post_json(opener, "/api/questions", {
        "subject": "Distributed Computing",
        "department": "Artificial Intelligence & Data Science",
        "question_text": "What is a remote procedure call?",
        "marks": 1
    })
    assert code == 400, f"Question Bank should reject 1 mark, but returned HTTP {code}: {data}"
    assert "2, 8, and 16" in data.get('message', ''), f"Unexpected error message: {data}"
    print(f"[PASS] 10. Question Bank strictly rejected 1 mark: '{data.get('message')}'")

    # 11. Frontend Configuration Verification
    print("\n--- Verifying Frontend HTML and JS Quiz Marks Configuration ---")
    html_path = os.path.join(BASE_DIR, "faculty-generate-quiz.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_src = f.read()
    assert '<option value="1" selected>1 Mark (Objective / MCQ Questions)</option>' in html_src, "HTML missing 1 Mark option"
    
    js_path = os.path.join(BASE_DIR, "js", "app.js")
    with open(js_path, "r", encoding="utf-8") as f:
        js_src = f.read()
    assert 'marksPerQSelect.value = "1"' in js_src, "app.js does not set quiz default to 1 mark"
    assert '<i class="bi bi-award me-1"></i>${q.marks' in js_src or 'q.marks !== undefined' in js_src, "app.js card template missing marks badge"
    print("[PASS] 11. Frontend HTML and JavaScript correctly configured for 1-mark Quiz workflow.")

    print("\n" + "=" * 70)
    print("ALL 11 VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")
    print("Quiz Generator now supports 1-mark questions seamlessly,")
    print("while AI Question Generator, Question Bank, and Exam modules")
    print("continue strictly enforcing ONLY 2, 8, and 16 marks!")
    print("=" * 70)

if __name__ == '__main__':
    run_test_suite()
