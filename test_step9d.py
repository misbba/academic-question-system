import requests
import sys

BASE_URL = "http://localhost:5000"

def run_tests():
    print("=" * 70)
    print("STEP 9D VERIFICATION SUITE — QUESTIONS & QUESTION BANK API")
    print("=" * 70)

    fac_session = requests.Session()
    stu_session = requests.Session()
    anon_session = requests.Session()

    # 1. Faculty Registration / Login
    print("\n[TEST 1] Faculty Auth...")
    fac_email = "test.faculty9d@university.edu"
    fac_pass = "Password123!"
    
    # Try register first
    fac_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Dr. Test Faculty 9D",
        "email": fac_email,
        "password": fac_pass,
        "role": "faculty",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026"
    })
    
    resp = fac_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": fac_email,
        "password": fac_pass,
        "role": "faculty"
    })
    assert resp.status_code == 200, f"Faculty login failed: {resp.status_code} {resp.text}"
    print("  [SUCCESS] Faculty login successful")

    # 2. Student Registration / Login
    print("\n[TEST 2] Student Auth...")
    stu_email = "test.student9d@university.edu"
    stu_pass = "Password123!"

    stu_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Test Student 9D",
        "email": stu_email,
        "password": stu_pass,
        "role": "student",
        "department": "Artificial Intelligence & Data Science",
        "semester": "Semester 6",
        "academic_year": "2025-2026"
    })

    resp = stu_session.post(f"{BASE_URL}/api/auth/login", json={
        "email": stu_email,
        "password": stu_pass,
        "role": "student"
    })
    assert resp.status_code == 200, f"Student login failed: {resp.status_code} {resp.text}"
    print("  [SUCCESS] Student login successful")

    # 3. Create Single Question (Faculty)
    print("\n[TEST 3] Create Single Question (Faculty)...")
    single_payload = {
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit III — SQL",
        "topic": "Joins & Subqueries",
        "question_text": "Explain the difference between INNER JOIN and LEFT JOIN in SQL with a query example.",
        "question_type": "Short Answer",
        "bloom_level": "Understand",
        "difficulty": "Medium",
        "concept": "SQL Joins",
        "explanation": "INNER JOIN returns matching rows only; LEFT JOIN returns all left rows plus matching right rows.",
        "marks": 5
    }
    resp = fac_session.post(f"{BASE_URL}/api/questions", json=single_payload)
    assert resp.status_code == 201, f"Failed to create single question: {resp.status_code} {resp.text}"
    q_data = resp.json()
    assert q_data['status'] == 'success', f"Invalid response format: {q_data}"
    created_q1_id = q_data['question']['id']
    print(f"  [SUCCESS] Single question created with ID {created_q1_id}")

    # 4. Create Batch Questions (Faculty) with MCQ Options
    print("\n[TEST 4] Create Batch Questions (Faculty)...")
    batch_payload = {
        "batch": [
            {
                "subject": "Database Management Systems",
                "department": "Artificial Intelligence & Data Science",
                "academic_year": "2025-2026",
                "semester": "Semester 6",
                "unit": "Unit III — SQL",
                "topic": "SQL Commands",
                "question_text": "Which SQL command is used to delete all rows from a table without logging individual row deletions?",
                "question_type": "Multiple Choice Question",
                "bloom_level": "Remember",
                "difficulty": "Easy",
                "concept": "SQL Commands",
                "explanation": "TRUNCATE TABLE is a DDL operation that removes all rows quickly.",
                "marks": 2,
                "options": [
                    {"option_letter": "A", "option_text": "DELETE", "is_correct": False},
                    {"option_letter": "B", "option_text": "TRUNCATE", "is_correct": True},
                    {"option_letter": "C", "option_text": "DROP", "is_correct": False},
                    {"option_letter": "D", "option_text": "REMOVE", "is_correct": False}
                ]
            },
            {
                "subject": "Database Management Systems",
                "department": "Artificial Intelligence & Data Science",
                "academic_year": "2025-2026",
                "semester": "Semester 6",
                "unit": "Unit IV — Normalization",
                "topic": "Functional Dependencies",
                "question_text": "Formulate a relational schema decomposition into BCNF given functional dependencies.",
                "question_type": "Descriptive",
                "bloom_level": "Analyze",
                "difficulty": "Hard",
                "concept": "Normalization",
                "explanation": "Ensure for every non-trivial X -> Y, X is a superkey.",
                "marks": 10
            }
        ]
    }
    resp = fac_session.post(f"{BASE_URL}/api/questions", json=batch_payload)
    assert resp.status_code == 201, f"Failed batch creation: {resp.status_code} {resp.text}"
    batch_res = resp.json()
    assert len(batch_res['questions']) == 2, f"Expected 2 created questions, got {len(batch_res['questions'])}"
    created_mcq_id = batch_res['questions'][0]['id']
    created_hard_id = batch_res['questions'][1]['id']
    print(f"  [SUCCESS] Batch created successfully (IDs: {created_mcq_id}, {created_hard_id})")

    # 5. Get List of Questions with Filters
    print("\n[TEST 5] Get List of Questions (Filtered)...")
    resp = fac_session.get(f"{BASE_URL}/api/questions?subject=Database Management Systems&difficulty=Easy")
    assert resp.status_code == 200, f"Get questions list failed: {resp.status_code} {resp.text}"
    list_res = resp.json()
    assert list_res['status'] == 'success'
    print(f"  [SUCCESS] Retrieved {len(list_res['questions'])} filtered questions")

    # 6. Get Single Question by ID
    print("\n[TEST 6] Get Single Question by ID...")
    resp = fac_session.get(f"{BASE_URL}/api/questions/{created_mcq_id}")
    assert resp.status_code == 200, f"Get question by ID failed: {resp.status_code} {resp.text}"
    single_q = resp.json()['question']
    assert len(single_q['options']) == 4, f"Expected 4 MCQ options, got {len(single_q['options'])}"
    print(f"  [SUCCESS] Retrieved question with {len(single_q['options'])} MCQ options")

    # 7. Edit Question (PUT)
    print("\n[TEST 7] Edit Question (PUT)...")
    edit_payload = {
        "question_text": "UPDATED QUESTION: Which SQL command removes all table rows with minimum rollback logging?",
        "difficulty": "Medium"
    }
    resp = fac_session.put(f"{BASE_URL}/api/questions/{created_mcq_id}", json=edit_payload)
    assert resp.status_code == 200, f"Edit question failed: {resp.status_code} {resp.text}"
    updated_q = resp.json()['question']
    assert "UPDATED QUESTION" in updated_q['question_text']
    print("  [SUCCESS] Question updated successfully")

    # 8. Save Questions to Question Bank
    print("\n[TEST 8] Save Questions to Question Bank...")
    bank_payload = {
        "question_ids": [created_q1_id, created_mcq_id]
    }
    resp = fac_session.post(f"{BASE_URL}/api/question-bank", json=bank_payload)
    assert resp.status_code == 200, f"Save to Question Bank failed: {resp.status_code} {resp.text}"
    print(f"  [SUCCESS] Saved {resp.json().get('saved_count')} questions to Question Bank")

    # 9. Get Question Bank Items
    print("\n[TEST 9] Get Question Bank Repository...")
    resp = fac_session.get(f"{BASE_URL}/api/question-bank?in_bank_only=true")
    assert resp.status_code == 200, f"Get Question Bank failed: {resp.status_code} {resp.text}"
    bank_res = resp.json()
    bank_ids = [q['id'] for q in bank_res['questions']]
    assert created_q1_id in bank_ids and created_mcq_id in bank_ids, f"Expected questions in bank: {bank_ids}"
    print(f"  [SUCCESS] Question Bank retrieved ({len(bank_res['questions'])} items in bank)")

    # 10. Remove Question from Question Bank
    print("\n[TEST 10] Remove Question from Bank...")
    resp = fac_session.delete(f"{BASE_URL}/api/question-bank/{created_q1_id}")
    assert resp.status_code == 200, f"Remove from Question Bank failed: {resp.status_code} {resp.text}"
    print("  [SUCCESS] Question removed from bank successfully")

    # 11. Delete Question Record
    print("\n[TEST 11] Delete Question Record...")
    resp = fac_session.delete(f"{BASE_URL}/api/questions/{created_hard_id}")
    assert resp.status_code == 200, f"Delete question failed: {resp.status_code} {resp.text}"
    print("  [SUCCESS] Question record deleted successfully")

    # 12. Student Role Authorization Checks (403 Forbidden)
    print("\n[TEST 12] Authorization Check — Student Attempting Faculty Actions (403)...")
    
    # Student create question
    resp = stu_session.post(f"{BASE_URL}/api/questions", json=single_payload)
    assert resp.status_code == 403, f"Expected 403 for Student create, got {resp.status_code}"

    # Student edit question
    resp = stu_session.put(f"{BASE_URL}/api/questions/{created_mcq_id}", json=edit_payload)
    assert resp.status_code == 403, f"Expected 403 for Student edit, got {resp.status_code}"

    # Student delete question
    resp = stu_session.delete(f"{BASE_URL}/api/questions/{created_mcq_id}")
    assert resp.status_code == 403, f"Expected 403 for Student delete, got {resp.status_code}"

    # Student save to bank
    resp = stu_session.post(f"{BASE_URL}/api/question-bank", json=bank_payload)
    assert resp.status_code == 403, f"Expected 403 for Student save bank, got {resp.status_code}"

    print("  [SUCCESS] All Student 403 Forbidden checks passed")

    # 13. Unauthenticated Access Check (401 Unauthorized)
    print("\n[TEST 13] Unauthenticated Access Check (401)...")
    resp = anon_session.post(f"{BASE_URL}/api/questions", json=single_payload)
    assert resp.status_code == 401, f"Expected 401 for unauthenticated create, got {resp.status_code}"
    print("  [SUCCESS] Unauthenticated 401 check passed")

    print("\n" + "=" * 70)
    print("ALL 13 TESTS PASSED SUCCESSFULLY! STEP 9D VERIFIED 100%.")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\n❌ TEST FAILURE: {e}")
        sys.exit(1)
