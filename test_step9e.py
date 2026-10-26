import requests
import sys

BASE_URL = "http://localhost:5000"

def run_step9e_tests():
    print("=" * 75)
    print("STEP 9E VERIFICATION SUITE — QUESTION PAPER BUILDER & MYSQL API")
    print("=" * 75)

    fac_session = requests.Session()
    stu_session = requests.Session()
    anon_session = requests.Session()

    # 1. Faculty Auth
    print("\n[TEST 1] Faculty Auth...")
    fac_email = "test.faculty9e@university.edu"
    fac_pass = "Password123!"
    fac_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Dr. Alistair Vance",
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
    print("  [PASSED] Faculty login returned 200 OK")

    # 2. Student Auth
    print("\n[TEST 2] Student Auth...")
    stu_email = "test.student9e@university.edu"
    stu_pass = "Password123!"
    stu_session.post(f"{BASE_URL}/api/auth/register", json={
        "full_name": "Elena Rostova",
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
    print("  [PASSED] Student login returned 200 OK")

    # 3. Create Sample Questions in Question Bank for Paper Building
    print("\n[TEST 3] Setup Sample Question in Question Bank...")
    q_resp = fac_session.post(f"{BASE_URL}/api/questions", json={
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit III — SQL",
        "topic": "Joins & Subqueries",
        "question_text": "Explain relational algebra joins and SQL syntax for INNER JOIN.",
        "question_type": "Short Answer",
        "bloom_level": "Understand",
        "difficulty": "Medium",
        "concept": "SQL Joins",
        "marks": 5
    })
    assert q_resp.status_code == 201, f"Question setup failed: {q_resp.text}"
    q_id = q_resp.json()['question']['id']
    fac_session.post(f"{BASE_URL}/api/question-bank", json={"question_ids": [q_id]})
    print(f"  [PASSED] Sample question #{q_id} created and added to Question Bank")

    # 4. Question Bank Retrieval (200)
    print("\n[TEST 4] Question Bank Retrieval...")
    resp = fac_session.get(f"{BASE_URL}/api/question-bank")
    assert resp.status_code == 200, f"Get question-bank failed: {resp.status_code}"
    bank_questions = resp.json()['questions']
    assert len(bank_questions) > 0
    print(f"  [PASSED] Question Bank retrieved ({len(bank_questions)} items)")

    # 5. Create Question Paper (201)
    print("\n[TEST 5] Create Question Paper (POST)...")
    paper_payload = {
        "title": "Database Management Systems Model Exam 2026",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "exam_type": "Model Examination",
        "exam_date": "2026-10-15",
        "duration": "3 Hours",
        "total_marks": 100,
        "instructions": "1. Answer all questions.\n2. Assume suitable data.",
        "status": "Draft",
        "sections": [
            { "name": "SECTION A", "count": 10, "marks_per_q": 2, "total_marks": 20 },
            { "name": "SECTION B", "count": 5, "marks_per_q": 6, "total_marks": 30 },
            { "name": "SECTION C", "count": 5, "marks_per_q": 10, "total_marks": 50 }
        ],
        "question_ids": [q_id]
    }
    resp = fac_session.post(f"{BASE_URL}/api/question-papers", json=paper_payload)
    assert resp.status_code == 201, f"Create paper failed: {resp.status_code} {resp.text}"
    created_paper = resp.json()['paper']
    created_paper_id = created_paper['id']
    initial_fp = resp.json()['fingerprint']
    assert initial_fp is not None and len(initial_fp) == 64
    print(f"  [PASSED] Question paper created (ID: {created_paper_id}, Fingerprint: {initial_fp[:16]}...)")

    # 6. Retrieve Question Papers List (200)
    print("\n[TEST 6] Retrieve Question Papers List...")
    resp = fac_session.get(f"{BASE_URL}/api/question-papers?subject=Database Management Systems")
    assert resp.status_code == 200, f"Get papers list failed: {resp.status_code}"
    papers_list = resp.json()['question_papers']
    assert any(p['id'] == created_paper_id for p in papers_list)
    print(f"  [PASSED] GET /api/question-papers returned {len(papers_list)} papers")

    # 7. Retrieve Single Paper by ID (200)
    print("\n[TEST 7] Retrieve Single Paper by ID...")
    resp = fac_session.get(f"{BASE_URL}/api/question-papers/{created_paper_id}")
    assert resp.status_code == 200, f"Get paper by ID failed: {resp.status_code}"
    single_p = resp.json()['paper']
    assert len(single_p['questions']) >= 1
    print(f"  [PASSED] GET /api/question-papers/<id> retrieved paper with {len(single_p['questions'])} questions")

    # 8. Verify Fingerprint Match (200)
    print("\n[TEST 8] Verify Fingerprint Match...")
    resp = fac_session.post(f"{BASE_URL}/api/question-papers/{created_paper_id}/verify", json={"fingerprint": initial_fp})
    assert resp.status_code == 200, f"Verify fingerprint failed: {resp.status_code}"
    assert resp.json()['valid'] is True
    print("  [PASSED] Fingerprint verification returned valid match")

    # 9. Update Paper & Confirm Fingerprint Changes (200)
    print("\n[TEST 9] Update Paper & Check Fingerprint Change...")
    update_payload = dict(paper_payload)
    update_payload["instructions"] = "UPDATED INSTRUCTIONS: Answer all questions in Section A and Section B carefully."
    resp = fac_session.put(f"{BASE_URL}/api/question-papers/{created_paper_id}", json=update_payload)
    assert resp.status_code == 200, f"Update paper failed: {resp.status_code}"
    updated_fp = resp.json()['fingerprint']
    assert updated_fp != initial_fp, f"Fingerprint should change when paper content is modified! ({initial_fp} vs {updated_fp})"
    print(f"  [PASSED] Paper updated; fingerprint dynamically updated from {initial_fp[:8]} to {updated_fp[:8]}")

    # 10. Delete Paper (200)
    print("\n[TEST 10] Delete Paper...")
    resp = fac_session.delete(f"{BASE_URL}/api/question-papers/{created_paper_id}")
    assert resp.status_code == 200, f"Delete paper failed: {resp.status_code}"
    print("  [PASSED] Question paper deleted successfully")

    # 11. Student Role Authorization Checks (403)
    print("\n[TEST 11] Student Authorization Checks (403)...")
    resp = stu_session.post(f"{BASE_URL}/api/question-papers", json=paper_payload)
    assert resp.status_code == 403, f"Expected 403 for student create paper, got {resp.status_code}"

    resp = stu_session.put(f"{BASE_URL}/api/question-papers/1", json=paper_payload)
    assert resp.status_code == 403, f"Expected 403 for student update paper, got {resp.status_code}"

    resp = stu_session.delete(f"{BASE_URL}/api/question-papers/1")
    assert resp.status_code == 403, f"Expected 403 for student delete paper, got {resp.status_code}"
    print("  [PASSED] Student 403 Forbidden checks verified")

    # 12. Unauthenticated Request Check (401)
    print("\n[TEST 12] Unauthenticated Check (401)...")
    resp = anon_session.post(f"{BASE_URL}/api/question-papers", json=paper_payload)
    assert resp.status_code == 401, f"Expected 401 for unauthenticated request, got {resp.status_code}"
    print("  [PASSED] Unauthenticated request returned 401 Unauthorized")

    # 13. Regression Checks for Steps 9C & 9D
    print("\n[TEST 13] Regression Checks (Steps 9C & 9D)...")
    res_c = fac_session.get(f"{BASE_URL}/api/resources")
    assert res_c.status_code == 200, f"STEP 9C Resources API failed: {res_c.status_code}"

    q_d = fac_session.get(f"{BASE_URL}/api/questions")
    assert q_d.status_code == 200, f"STEP 9D Questions API failed: {q_d.status_code}"

    print("  [PASSED] STEP 9C & STEP 9D APIs operational and regression-free")

    print("\n" + "=" * 75)
    print("ALL STEP 9E VERIFICATION TESTS PASSED SUCCESSFULLY 100%!")
    print("=" * 75)

if __name__ == '__main__':
    try:
        run_step9e_tests()
    except Exception as e:
        print(f"\n[FAILURE] {e}")
        sys.exit(1)
