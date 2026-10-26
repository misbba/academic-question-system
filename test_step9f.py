import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def test_step9f():
    print("=" * 60)
    print("STARTING STEP 9F AUTOMATED VERIFICATION TEST SUITE")
    print("=" * 60)

    ts = int(time.time())
    faculty_email = f"test.faculty9f_{ts}@university.edu"
    faculty_pass = "Password123!"
    student_email = f"test.student9f_{ts}@university.edu"
    student_pass = "Password123!"

    # 1. Register & Login as Faculty
    faculty_session = requests.Session()
    res_reg = faculty_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Dr. Quiz Faculty",
        "email": faculty_email,
        "password": faculty_pass,
        "role": "faculty",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026"
    })
    assert res_reg.status_code in [200, 201], f"Faculty registration failed: {res_reg.text}"

    res = faculty_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": faculty_email,
        "password": faculty_pass,
        "role": "faculty"
    })
    assert res.status_code == 200, f"Faculty login failed: {res.text}"
    print("1. Faculty Registration & Login: PASSED")

    # 2. Register & Login as Student
    student_session = requests.Session()
    res_sreg = student_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Quiz Student User",
        "email": student_email,
        "password": student_pass,
        "role": "student",
        "department": "Artificial Intelligence & Data Science",
        "semester": "Semester 6",
        "academic_year": "2025-2026"
    })
    assert res_sreg.status_code in [200, 201], f"Student registration failed: {res_sreg.text}"

    res = student_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": student_email,
        "password": student_pass,
        "role": "student"
    })
    assert res.status_code == 200, f"Student login failed: {res.text}"
    print("2. Student Registration & Login: PASSED")

    # 3. Create Quiz as Faculty
    quiz_payload = {
        "title": "Database Indexing & B-Trees Quiz",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit IV — Indexing",
        "topic": "B+ Tree Indexing",
        "quiz_type": "Multiple Choice Question",
        "blooms_level": "Analyze",
        "difficulty": "Medium",
        "duration_minutes": 15,
        "marks_per_question": 2,
        "status": "Published",
        "questions": [
            {
                "num": 1,
                "text": "What is the primary advantage of a B+ Tree over a binary search tree in database systems?",
                "options": ["Faster single-element search", "High fan-out reducing disk I/O", "Less storage space", "Linear search complexity"],
                "correctAnswer": "B. High fan-out reducing disk I/O",
                "correctIndex": 1,
                "concept": "B+ Tree Indexing",
                "difficulty": "Medium"
            },
            {
                "num": 2,
                "text": "Which node type in a B+ Tree contains actual data pointers or record IDs?",
                "options": ["Root Node", "Internal Node", "Leaf Node", "Header Node"],
                "correctAnswer": "C. Leaf Node",
                "correctIndex": 2,
                "concept": "Leaf Node Structure",
                "difficulty": "Easy"
            }
        ]
    }

    res = faculty_session.post(f"{BASE_URL}/api/quizzes", json=quiz_payload)
    assert res.status_code == 201, f"Quiz creation failed: {res.text}"
    quiz_data = res.json()
    assert quiz_data["status"] == "success", f"Quiz response status invalid: {quiz_data}"
    created_quiz = quiz_data["quiz"]
    quiz_id = created_quiz["id"]
    print(f"3. Faculty Create Quiz (ID: {quiz_id}): PASSED")

    # 4. List Quizzes as Faculty
    res = faculty_session.get(f"{BASE_URL}/api/quizzes")
    assert res.status_code == 200, f"Faculty quiz listing failed: {res.text}"
    quizzes = res.json()["quizzes"]
    assert any(q["id"] == quiz_id for q in quizzes), "Created quiz not in faculty list"
    print("4. Faculty List Quizzes: PASSED")

    # 5. Get Quiz by ID
    res = faculty_session.get(f"{BASE_URL}/api/quizzes/{quiz_id}")
    assert res.status_code == 200, f"Get quiz by ID failed: {res.text}"
    assert res.json()["quiz"]["title"] == "Database Indexing & B-Trees Quiz"
    print("5. Get Quiz by ID: PASSED")

    # 6. List Published Quizzes as Student
    res = student_session.get(f"{BASE_URL}/api/quizzes")
    assert res.status_code == 200, f"Student list quizzes failed: {res.text}"
    student_quizzes = res.json()["quizzes"]
    assert any(q["id"] == quiz_id for q in student_quizzes), "Published quiz not visible to student"
    print("6. Student View Published Quizzes: PASSED")

    # 7. Submit Quiz Attempt as Student
    submit_payload = {
        "answers": {
            "0": 1,  # Correct (B)
            "1": 2   # Correct (C)
        }
    }
    res = student_session.post(f"{BASE_URL}/api/quizzes/{quiz_id}/submit", json=submit_payload)
    assert res.status_code == 201, f"Student submit quiz failed: {res.text}"
    attempt_res = res.json()
    assert attempt_res["status"] == "success", f"Submit attempt failed: {attempt_res}"
    attempt = attempt_res["attempt"]
    assert attempt["percentage"] == "100%", f"Score percentage incorrect: {attempt['percentage']}"
    assert attempt["conceptPerformance"]["B+ Tree Indexing"] == True
    print("7. Student Submit Quiz Attempt (Score 100%): PASSED")

    # 8. Student View Attempt History
    res = student_session.get(f"{BASE_URL}/api/quizzes/attempts")
    assert res.status_code == 200, f"Student attempts history failed: {res.text}"
    attempts = res.json()["attempts"]
    assert len(attempts) > 0, "No attempt history found for student"
    print("8. Student View Quiz Attempt History: PASSED")

    # 9. Update Quiz as Faculty
    update_payload = {
        "title": "Database Indexing & B-Trees Quiz (Updated)",
        "duration_minutes": 20
    }
    res = faculty_session.put(f"{BASE_URL}/api/quizzes/{quiz_id}", json=update_payload)
    assert res.status_code == 200, f"Faculty update quiz failed: {res.text}"
    updated_quiz = res.json()["quiz"]
    assert updated_quiz["title"] == "Database Indexing & B-Trees Quiz (Updated)"
    assert updated_quiz["duration_minutes"] == 20
    print("9. Faculty Update Quiz: PASSED")

    # 10. Role Protection Checks
    # Student trying to create quiz -> 403
    res = student_session.post(f"{BASE_URL}/api/quizzes", json=quiz_payload)
    assert res.status_code == 403, f"Expected 403 for student quiz creation, got {res.status_code}"

    # Student trying to update quiz -> 403
    res = student_session.put(f"{BASE_URL}/api/quizzes/{quiz_id}", json=update_payload)
    assert res.status_code == 403, f"Expected 403 for student quiz update, got {res.status_code}"

    # Student trying to delete quiz -> 403
    res = student_session.delete(f"{BASE_URL}/api/quizzes/{quiz_id}")
    assert res.status_code == 403, f"Expected 403 for student quiz delete, got {res.status_code}"

    # Faculty trying to submit quiz attempt -> 403
    res = faculty_session.post(f"{BASE_URL}/api/quizzes/{quiz_id}/submit", json=submit_payload)
    assert res.status_code == 403, f"Expected 403 for faculty quiz submit, got {res.status_code}"
    print("10. Role Protection Checks (403 Forbidden): PASSED")

    # 11. Authentication Checks
    anon_session = requests.Session()
    res = anon_session.get(f"{BASE_URL}/api/quizzes")
    assert res.status_code == 401, f"Expected 401 for unauthenticated quiz list, got {res.status_code}"

    res = anon_session.post(f"{BASE_URL}/api/quizzes", json=quiz_payload)
    assert res.status_code == 401, f"Expected 401 for unauthenticated quiz creation, got {res.status_code}"
    print("11. Authentication Checks (401 Unauthorized): PASSED")

    # 12. Delete Quiz as Faculty
    res = faculty_session.delete(f"{BASE_URL}/api/quizzes/{quiz_id}")
    assert res.status_code == 200, f"Faculty delete quiz failed: {res.text}"
    print("12. Faculty Delete Quiz: PASSED")

    # 13. Regression Tests for Steps 9A - 9E
    res = faculty_session.get(f"{BASE_URL}/api/resources")
    assert res.status_code == 200, f"9C Resources endpoint failed: {res.text}"

    res = faculty_session.get(f"{BASE_URL}/api/questions")
    assert res.status_code == 200, f"9D Questions endpoint failed: {res.text}"

    res = faculty_session.get(f"{BASE_URL}/api/question-papers")
    assert res.status_code == 200, f"9E Papers endpoint failed: {res.text}"
    print("13. Regression Tests (Steps 9A-9E endpoints): PASSED")

    print("=" * 60)
    print("ALL STEP 9F VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_step9f()
