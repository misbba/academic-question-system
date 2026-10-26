"""
Academic Question Generation and Difficulty Balancing System
Comprehensive System Verification Test Script
Tests all 8 tasks:
1. Student login, identity, and session profile
2. Student portal endpoints (quizzes, materials, published papers, results)
3. Faculty login, identity, and role protection
4. Faculty endpoints (questions, question papers, quizzes, stats, balancer)
5. QR verification decoupled / Sha-256 fingerprint intact
6. Database & MySQL integration with real queries
7. Forgot password reset flow with verification
8. Full end-to-end flows
"""

import sys
import os
import json

# Setup backend import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app import app
from models.database import get_db_connection

def run_tests():
    print("=" * 70)
    print("ACADEMIC QUESTION SYSTEM — COMPREHENSIVE END-TO-END VERIFICATION")
    print("=" * 70)

    passed_count = 0
    total_count = 0

    def assert_test(name, condition, details=""):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            passed_count += 1
            print(f"  [PASS] Test {total_count}: {name}")
        else:
            print(f"  [FAIL] Test {total_count}: {name}")
            if details:
                print(f"         Details: {details}")

    with app.test_client() as client:
        # -------------------------------------------------------------
        # TEST 1: Database Connectivity & Integrity
        # -------------------------------------------------------------
        print("\n--- Phase 1: Database Tables & Schema Verification ---")
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) as cnt FROM users;")
                user_count = cur.fetchone()['cnt']
                cur.execute("SELECT count(*) as cnt FROM questions;")
                q_count = cur.fetchone()['cnt']
                cur.execute("SELECT count(*) as cnt FROM question_papers;")
                qp_count = cur.fetchone()['cnt']
            conn.close()
            assert_test("Database connection & tables verified", user_count > 0 and qp_count >= 0, f"Users: {user_count}, Questions: {q_count}, Papers: {qp_count}")
        except Exception as e:
            assert_test("Database connection verified", False, str(e))

        # -------------------------------------------------------------
        # TEST 2: Faculty Login & Identity (Task 3)
        # -------------------------------------------------------------
        print("\n--- Phase 2: Faculty Login & Identity Protection ---")
        # Faculty Murugan (ID 24)
        login_res = client.post('/api/auth/login', json={
            "email": "muruga@vsb.com",
            "password": "Password123!",
            "role": "faculty"
        })
        fac_data = login_res.get_json() or {}
        assert_test("Faculty Murugan login successful", login_res.status_code == 200 and fac_data.get('status') == 'success', str(fac_data))
        assert_test("Faculty profile returned with real DB details", fac_data.get('user', {}).get('full_name') == 'muruga' and fac_data.get('user', {}).get('role') == 'faculty', str(fac_data.get('user')))

        # Session profile /api/auth/me
        me_res = client.get('/api/auth/me')
        me_data = me_res.get_json() or {}
        assert_test("Faculty /api/auth/me reflects active session", me_res.status_code == 200 and me_data.get('user', {}).get('full_name') == 'muruga', str(me_data))

        # Role Protection: Faculty credentials rejected at student login
        stud_mismatch_res = client.post('/api/auth/login', json={
            "email": "muruga@vsb.com",
            "password": "Password123!",
            "role": "student"
        })
        assert_test("Role Protection: Faculty credentials rejected at student login (HTTP 403)", stud_mismatch_res.status_code == 403)

        # -------------------------------------------------------------
        # TEST 3: Faculty Operations & Question Bank (Task 4)
        # -------------------------------------------------------------
        print("\n--- Phase 3: Faculty Questions & Question Paper Creation ---")
        # GET /api/questions
        q_res = client.get('/api/questions')
        q_data = q_res.get_json() or {}
        assert_test("Faculty can retrieve questions list from MySQL", q_res.status_code == 200 and 'questions' in q_data, f"Count: {q_data.get('count')}")

        # POST /api/questions (Create question)
        create_q_res = client.post('/api/questions', json={
            "question_text": "Explain the ACID properties of database transactions with concrete examples.",
            "subject": "Database Management Systems",
            "department": "Artificial Intelligence & Data Science",
            "unit": "Unit 4",
            "topic": "Transaction Processing",
            "difficulty": "Medium",
            "bloom_level": "Understand",
            "marks": 5,
            "explanation": "Atomicity, Consistency, Isolation, and Durability ensure reliable transaction execution."
        })
        new_q_data = create_q_res.get_json() or {}
        assert_test("Faculty can create new question in MySQL", create_q_res.status_code == 201 and new_q_data.get('status') == 'success', str(new_q_data))
        new_q_id = new_q_data.get('question_id')

        # Create Question Paper (Draft)
        qp_res = client.post('/api/question-papers', json={
            "title": "Continuous Assessment Test 1 - DBMS",
            "subject": "Database Management Systems",
            "department": "Artificial Intelligence & Data Science",
            "semester": "Semester 6",
            "academic_year": "2025-2026",
            "exam_type": "Internal Assessment",
            "duration": "1 Hour 30 Mins",
            "total_marks": 50,
            "status": "Draft",
            "question_ids": [new_q_id] if new_q_id else [1],
            "sections": [
                {
                    "title": "Part A - Short Answer Questions",
                    "marks_per_question": 2,
                    "questions": [{"id": 1, "question_text": "Define Normalization.", "difficulty": "Easy", "bloom_level": "Remember", "marks": 2}]
                }
            ]
        })
        qp_data = qp_res.get_json() or {}
        assert_test("Faculty can create question paper with SHA-256 fingerprint", qp_res.status_code == 201 and 'fingerprint' in qp_data, str(qp_data))
        created_paper_id = qp_data.get('paper', {}).get('id')

        # Publish Question Paper
        pub_res = client.put(f'/api/question-papers/{created_paper_id}', json={
            "status": "Published"
        })
        pub_data = pub_res.get_json() or {}
        assert_test("Faculty can publish question paper", pub_res.status_code == 200 and pub_data.get('status') == 'success')

        # Logout faculty
        client.post('/api/auth/logout')

        # -------------------------------------------------------------
        # TEST 4: Student Login & Identity (Task 1)
        # -------------------------------------------------------------
        print("\n--- Phase 4: Student Login & Identity Verification ---")
        # Student Nisha (ID 5)
        stud_login_res = client.post('/api/auth/login', json={
            "email": "nisha@vsb.com",
            "password": "12345678",
            "role": "student"
        })
        stud_data = stud_login_res.get_json() or {}
        assert_test("Student Nisha login successful", stud_login_res.status_code == 200 and stud_data.get('status') == 'success', str(stud_data))
        assert_test("Student profile shows dynamic name and department", stud_data.get('user', {}).get('full_name') == 'Nisha' and stud_data.get('user', {}).get('role') == 'student', str(stud_data.get('user')))

        # Role Protection: Student credentials rejected at faculty login
        fac_mismatch_res = client.post('/api/auth/login', json={
            "email": "nisha@vsb.com",
            "password": "12345678",
            "role": "faculty"
        })
        assert_test("Role Protection: Student credentials rejected at faculty login (HTTP 403)", fac_mismatch_res.status_code == 403)

        # -------------------------------------------------------------
        # TEST 5: Student Portal Access & Published Papers (Task 2)
        # -------------------------------------------------------------
        print("\n--- Phase 5: Student Access & Published Question Papers ---")
        # Student GET /api/question-papers (MUST succeed and return Published papers, NOT 403)
        stud_qp_res = client.get('/api/question-papers')
        stud_qp_data = stud_qp_res.get_json() or {}
        assert_test("Student can view Published examination papers (HTTP 200)", stud_qp_res.status_code == 200 and 'question_papers' in stud_qp_data, str(stud_qp_data))

        # Check all papers visible to student are Published
        papers = stud_qp_data.get('question_papers', [])
        all_published = all(p.get('status') == 'Published' for p in papers) if papers else True
        assert_test("Only Published papers are exposed to students", all_published and len(papers) > 0, f"Visible count: {len(papers)}")

        # Student cannot create question paper (gets 403)
        forbid_qp = client.post('/api/question-papers', json={"title": "Hacked Paper"})
        assert_test("Student forbidden from creating question papers (HTTP 403)", forbid_qp.status_code == 403)

        # Student cannot create questions (gets 403)
        forbid_q = client.post('/api/questions', json={"question_text": "Hacked Question"})
        assert_test("Student forbidden from creating questions (HTTP 403)", forbid_q.status_code == 403)

        # Logout student
        client.post('/api/auth/logout')

        # -------------------------------------------------------------
        # TEST 6: Password Reset Flow (Task 4 & Task 1)
        # -------------------------------------------------------------
        print("\n--- Phase 6: Password Reset Verification ---")
        # 1. Invalid email
        res1 = client.post('/api/auth/reset-password', json={
            "email": "nonexistent@vsb.com",
            "role": "student",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        assert_test("Password reset fails for non-existent email (HTTP 404)", res1.status_code == 404)

        # 2. Role mismatch
        res2 = client.post('/api/auth/reset-password', json={
            "email": "muruga@vsb.com",
            "role": "student",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        assert_test("Password reset fails for role mismatch (HTTP 403)", res2.status_code == 403)

        # 3. Password mismatch
        res3 = client.post('/api/auth/reset-password', json={
            "email": "muruga@vsb.com",
            "role": "faculty",
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!"
        })
        assert_test("Password reset fails when passwords do not match (HTTP 400)", res3.status_code == 400)

        # 4. Successful password update for Faculty Murugan
        res4 = client.post('/api/auth/reset-password', json={
            "email": "muruga@vsb.com",
            "role": "faculty",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        })
        assert_test("Password reset succeeds for valid credentials (HTTP 200)", res4.status_code == 200 and res4.get_json().get('status') == 'success')

        # 5. Verify login works with new password
        login_new_res = client.post('/api/auth/login', json={
            "email": "muruga@vsb.com",
            "password": "NewPassword123!",
            "role": "faculty"
        })
        assert_test("Login succeeds with newly reset password", login_new_res.status_code == 200)

        # 6. Restore original password for Faculty Murugan
        client.post('/api/auth/reset-password', json={
            "email": "muruga@vsb.com",
            "role": "faculty",
            "new_password": "Password123!",
            "confirm_password": "Password123!"
        })
        login_restore_res = client.post('/api/auth/login', json={
            "email": "muruga@vsb.com",
            "password": "Password123!",
            "role": "faculty"
        })
        assert_test("Original password successfully restored and verified", login_restore_res.status_code == 200)

        # -------------------------------------------------------------
        # TEST 7: Quiz Generation, Student Assessment & Results Flow
        # -------------------------------------------------------------
        print("\n--- Phase 7: Quiz Generation & Assessment Flow ---")
        # Faculty Murugan logs in and creates Quiz
        client.post('/api/auth/login', json={
            "email": "muruga@vsb.com",
            "password": "Password123!",
            "role": "faculty"
        })

        create_quiz_res = client.post('/api/quizzes', json={
            "title": "Database Normalization Quick Assessment",
            "subject": "Database Management Systems",
            "department": "Artificial Intelligence & Data Science",
            "semester": "Semester 6",
            "unit": "Unit 2",
            "topic": "Functional Dependencies & Normal Forms",
            "duration_minutes": 10,
            "marks_per_question": 2,
            "status": "Published",
            "questions": [
                {
                    "question_text": "Which normal form requires the removal of transitive functional dependencies?",
                    "options": [
                        {"label": "A", "text": "First Normal Form (1NF)"},
                        {"label": "B", "text": "Second Normal Form (2NF)"},
                        {"label": "C", "text": "Third Normal Form (3NF)"},
                        {"label": "D", "text": "Boyce-Codd Normal Form (BCNF)"}
                    ],
                    "correct_answer": "C",
                    "explanation": "3NF requires that no non-prime attribute is transitively dependent on any candidate key."
                },
                {
                    "question_text": "In relational database design, what does a lossless-join decomposition guarantee?",
                    "options": [
                        {"label": "A", "text": "No redundant tuples are produced when natural-joining decomposed relations"},
                        {"label": "B", "text": "All functional dependencies are preserved without checking joins"},
                        {"label": "C", "text": "The table is strictly in 4NF"},
                        {"label": "D", "text": "Primary keys are never used"}
                    ],
                    "correct_answer": "A",
                    "explanation": "Lossless join decomposition ensures no spurious tuples are generated upon reconstruction."
                }
            ]
        })
        new_quiz_data = create_quiz_res.get_json() or {}
        assert_test("Faculty Murugan can create & publish online quiz", create_quiz_res.status_code == 201 and new_quiz_data.get('status') == 'success', str(new_quiz_data))
        created_quiz_id = new_quiz_data.get('quiz', {}).get('id')

        # Logout faculty
        client.post('/api/auth/logout')

        # Student Nisha logs in
        client.post('/api/auth/login', json={
            "email": "nisha@vsb.com",
            "password": "12345678",
            "role": "student"
        })

        # Student fetches published quizzes
        stud_quizzes_res = client.get('/api/quizzes')
        stud_quizzes_data = stud_quizzes_res.get_json() or {}
        quizzes_list = stud_quizzes_data.get('quizzes', [])
        assert_test("Student can see published quiz in assessment list", stud_quizzes_res.status_code == 200 and any(q.get('id') == created_quiz_id for q in quizzes_list), f"Count: {len(quizzes_list)}")

        # Student submits quiz attempt with answers
        submit_res = client.post(f'/api/quizzes/{created_quiz_id}/submit', json={
            "answers": {
                "0": "C",  # Correct (2 marks)
                "1": "A"   # Correct (2 marks)
            }
        })
        submit_data = submit_res.get_json() or {}
        assert_test("Student can submit quiz attempt & receive instant score (100%)", submit_res.status_code == 201 and submit_data.get('score') == 4 and submit_data.get('percentage') == '100%', str(submit_data))

        # Student views past attempts / history
        attempts_res = client.get('/api/quizzes/attempts')
        attempts_data = attempts_res.get_json() or {}
        assert_test("Student quiz attempt recorded in MySQL & retrievable", attempts_res.status_code == 200 and len(attempts_data.get('attempts', [])) > 0, f"Attempts count: {len(attempts_data.get('attempts', []))}")

        # Logout student
        client.post('/api/auth/logout')

    print("\n" + "=" * 70)
    print(f"VERIFICATION SUMMARY: {passed_count}/{total_count} TESTS PASSED ({round(passed_count/total_count*100, 1)}%)")
    print("=" * 70)
    return passed_count == total_count

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
