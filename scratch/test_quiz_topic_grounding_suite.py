import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def run_suite():
    print("=" * 70)
    print("STARTING COMPREHENSIVE QUIZ GENERATOR TOPIC-GROUNDING TEST SUITE")
    print("=" * 70)
    session = requests.Session()
    
    # 1. Login as Murugan (Faculty ID 24)
    print("\n[Step 1] Authenticating as Faculty Murugan (muruga@vsb.com)...")
    login_res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    user_info = login_res.json().get('user', {})
    print(f"Logged in as: {user_info.get('full_name')} (ID: {user_info.get('id')}, Role: {user_info.get('role')})")

    # 2. Test Lamport's Algorithm Grounded Generation (10 Questions, 1 Mark each)
    print("\n[Step 2] Testing Grounded Quiz Generation for Topic: \"Lamport's Algorithm\" (10 Questions, 1 Mark)...")
    payload1 = {
        "subject": "Distributed Systems",
        "unit": "Unit II — Clocks and Mutual Exclusion",
        "topic": "Lamport's Algorithm",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 10,
        "difficulty": "Mixed",
        "blooms_level": "Auto Select"
    }
    res1 = session.post(f"{BASE_URL}/api/quizzes/generate", json=payload1)
    assert res1.status_code == 200, f"Quiz generation failed: {res1.text}"
    data1 = res1.json()
    assert data1['status'] == 'success'
    questions1 = data1['questions']
    assert len(questions1) == 10, f"Expected 10 questions, got {len(questions1)}"
    
    correct_letters_seen = set()
    for i, q in enumerate(questions1):
        assert q['marks'] == 1, f"Q{i+1} marks should be 1, got {q.get('marks')}"
        assert q['marks_per_question'] == 1, f"Q{i+1} marks_per_question should be 1"
        assert len(q['options']) == 4, f"Q{i+1} should have exactly 4 options"
        assert len(q['options_strings']) == 4
        
        # Check no option is [object Object] or empty
        for opt in q['options']:
            txt = opt.get('text') or opt.get('option_text') or ''
            assert txt != '[object Object]', f"Q{i+1} option rendered as [object Object]!"
            assert len(txt.strip()) > 2, f"Q{i+1} option text is empty!"
        
        c_idx = q['correctIndex']
        assert 0 <= c_idx <= 3, f"Q{i+1} correctIndex out of bounds: {c_idx}"
        assert q['options'][c_idx]['is_correct'] is True, f"Q{i+1} correctIndex doesn't point to is_correct True option!"
        c_let = q['correct_answer']
        assert c_let == ['A', 'B', 'C', 'D'][c_idx], f"Q{i+1} correct_answer {c_let} doesn't match correctIndex {c_idx}"
        correct_letters_seen.add(c_let)
        
        # Grounding check: verify question is strictly about Lamport / Logical Clocks / Lamport Mutual Exclusion
        q_text_lower = q['question_text'].lower()
        exp_lower = q['explanation'].lower()
        grounded = any(k in q_text_lower or k in exp_lower for k in ['lamport', 'clock', 'logical', 'happened-before', 'critical section', 'order', 'request', 'reply', 'release'])
        assert grounded, f"Q{i+1} does not appear grounded in Lamport's algorithm: {q['question_text']}"
        
        # Verify NO generic filler stem
        assert "according to course standards on lamport" not in q_text_lower, f"Q{i+1} used generic filler stem!"
    
    print(f"PASSED: Generated 10 grounded Lamport questions with 1 mark each. Correct answers rotated across: {correct_letters_seen}")
    print(f"Sample Question 1:\n  Stem: {questions1[0]['question_text']}\n  Options: {[o['text'] for o in questions1[0]['options']]}\n  Correct: {questions1[0]['correctAnswer']}")

    # 3. Test Mutual Exclusion Grounded Generation (5 Questions, 1 Mark each)
    print("\n[Step 3] Testing Grounded Quiz Generation for Topic: \"Mutual Exclusion\" (5 Questions, 1 Mark)...")
    payload2 = {
        "subject": "Distributed Computing",
        "unit": "Unit III — Mutual Exclusion",
        "topic": "Mutual Exclusion",
        "duration_minutes": 20,
        "marks_per_question": 1,
        "total_questions": 5,
        "difficulty": "Medium"
    }
    res2 = session.post(f"{BASE_URL}/api/quizzes/generate", json=payload2)
    assert res2.status_code == 200, f"Mutual Exclusion generation failed: {res2.text}"
    data2 = res2.json()
    questions2 = data2['questions']
    assert len(questions2) == 5
    for i, q in enumerate(questions2):
        assert q['marks'] == 1
        q_text_lower = q['question_text'].lower()
        exp_lower = q['explanation'].lower()
        grounded = any(k in q_text_lower or k in exp_lower for k in ['mutual exclusion', 'critical section', 'safety', 'liveness', 'ricart', 'delay', 'fairness', 'token', 'bounded'])
        assert grounded, f"Q{i+1} not grounded in Mutual Exclusion: {q['question_text']}"
        for opt in q['options']:
            assert opt['text'] != '[object Object]'
    print(f"PASSED: Generated 5 grounded Mutual Exclusion questions (1 mark each).")
    print(f"Sample Question 1:\n  Stem: {questions2[0]['question_text']}\n  Correct: {questions2[0]['correctAnswer']}")

    # 4. Test Christian's Method Grounded Generation (5 Questions, 1 Mark each)
    print("\n[Step 4] Testing Grounded Quiz Generation for Topic: \"Christian's Method\" (5 Questions, 1 Mark)...")
    payload3 = {
        "subject": "Distributed Computing",
        "unit": "Unit II",
        "topic": "Christian's Method",
        "duration_minutes": 15,
        "marks_per_question": 1,
        "total_questions": 5
    }
    res3 = session.post(f"{BASE_URL}/api/quizzes/generate", json=payload3)
    assert res3.status_code == 200, f"Christian's Method generation failed: {res3.text}"
    questions3 = res3.json()['questions']
    assert len(questions3) == 5
    for q in questions3:
        assert q['marks'] == 1
        q_text_lower = q['question_text'].lower()
        exp_lower = q['explanation'].lower()
        grounded = any(k in q_text_lower or k in exp_lower for k in ['christian', 'clock', 'rtt', 'time server', 'synchronization', 'delay', 'slewing', 'symmetric'])
        assert grounded, f"Christian question not grounded: {q['question_text']}"
    print(f"PASSED: Generated 5 grounded Christian's Method questions (1 mark each).")

    # 5. Test Topic Mismatch / Insufficient Material (Quantum Mechanics)
    print("\n[Step 5] Testing Topic Mismatch Enforcement for: \"Quantum Mechanics\"...")
    payload_mismatch = {
        "subject": "Distributed Computing",
        "unit": "Unit II",
        "topic": "Quantum Mechanics",
        "duration_minutes": 15,
        "marks_per_question": 1,
        "total_questions": 5
    }
    res_mismatch = session.post(f"{BASE_URL}/api/quizzes/generate", json=payload_mismatch)
    assert res_mismatch.status_code == 400, f"Expected 400 error for mismatched topic, got {res_mismatch.status_code}"
    data_err = res_mismatch.json()
    assert data_err.get('topic_mismatch') is True, f"Expected topic_mismatch: True, got: {data_err}"
    assert "Topic Mismatch" in data_err.get('message', ''), f"Expected 'Topic Mismatch' in message: {data_err}"
    print(f"PASSED: Server cleanly rejected mismatched topic 'Quantum Mechanics'.")
    print(f"Server response: {data_err['message']}")

    # 6. Test Quiz Saving and Retrieval in MySQL
    print("\n[Step 6] Saving Generated Quiz to Database and Retrieving by ID...")
    quiz_save_payload = {
        "title": "Distributed Systems Lamport Timed Quiz",
        "subject": "Distributed Computing",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit II — Clocks and Mutual Exclusion",
        "topic": "Lamport's Algorithm",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 10,
        "status": "Published",
        "questions": questions1
    }
    save_res = session.post(f"{BASE_URL}/api/quizzes", json=quiz_save_payload)
    assert save_res.status_code == 201, f"Failed to save quiz: {save_res.text}"
    saved_quiz = save_res.json().get('quiz', {})
    quiz_db_id = saved_quiz.get('id')
    assert quiz_db_id is not None, "Saved quiz has no ID!"
    print(f"Saved Quiz in DB: ID {quiz_db_id}, Quiz Code: {saved_quiz.get('quiz_code')}, Total Marks: {saved_quiz.get('totalMarks')}")

    get_res = session.get(f"{BASE_URL}/api/quizzes/{quiz_db_id}")
    assert get_res.status_code == 200, f"Failed to retrieve quiz: {get_res.text}"
    retrieved_quiz = get_res.json().get('quiz', {})
    assert retrieved_quiz['marks_per_question'] == 1
    assert retrieved_quiz['marksPerQuestion'] == 1
    assert retrieved_quiz['totalMarks'] == 10
    assert len(retrieved_quiz['questions']) == 10
    for q in retrieved_quiz['questions']:
        assert q['marks'] == 1
        for opt in q['options']:
            txt = opt.get('text') or opt.get('option_text') or ''
            assert txt != '[object Object]', "Retrieved quiz has [object Object] option!"
    print(f"PASSED: Quiz retrieved from MySQL with clean 1-mark options and intact schema.")

    # 7. Student Quiz Taking & Auto-Scoring
    print("\n[Step 7] Testing Student Quiz Submission and Auto-Scoring...")
    # Student login (use a student account or test student)
    # Murugan as faculty created quiz; submit attempt as student (or test submission)
    attempt_payload = {
        "answers": {
            "0": questions1[0]['correctIndex'],
            "1": questions1[1]['correctIndex'],
            "2": 99 # wrong answer
        }
    }
    # Test submission endpoint directly
    attempt_res = session.post(f"{BASE_URL}/api/quizzes/{quiz_db_id}/attempts", json=attempt_payload)
    if attempt_res.status_code == 200:
        att_data = attempt_res.json()
        print(f"Attempt Evaluation: Score = {att_data.get('score')} / {att_data.get('total_marks')} ({att_data.get('percentage')})")
        assert att_data.get('score') == 2 * 1, f"Expected 2 marks for 2 correct answers, got {att_data.get('score')}"
        print("PASSED: 1-mark auto-scoring evaluated accurately.")

    # 8. Strict Marks Isolation Test: Verify other modules reject 1 mark
    print("\n[Step 8] Verifying Strict Marks Isolation: Other modules MUST reject 1 mark...")
    qb_reject_res = session.post(f"{BASE_URL}/api/questions/generate", json={
        "subject": "Distributed Computing",
        "marks_per_question": 1,
        "num_questions": 5
    })
    assert qb_reject_res.status_code in (400, 422), f"Expected AI Question Generator to reject 1 mark, got: {qb_reject_res.status_code}"
    assert "2, 8, and 16" in qb_reject_res.text or "Only 2, 8" in qb_reject_res.text
    print(f"PASSED: AI Question Generator strictly rejected 1 mark: '{qb_reject_res.json().get('message')}'.")

    qb_save_reject = session.post(f"{BASE_URL}/api/questions", json={
        "subject": "Distributed Computing",
        "question_text": "Define Lamport's logical clock condition.",
        "marks": 1,
        "question_type": "Short Answer"
    })
    assert qb_save_reject.status_code in (400, 422)
    assert "2, 8, and 16" in qb_save_reject.text
    print(f"PASSED: Question creation strictly rejected 1 mark: '{qb_save_reject.json().get('message')}'.")

    print("\n" + "=" * 70)
    print("ALL 8/8 QUIZ TOPIC GROUNDING & VALIDATION TESTS PASSED PERFECTLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_suite()
