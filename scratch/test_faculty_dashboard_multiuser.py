import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:5000"

class APISession:
    def __init__(self):
        self.cookie = None

    def request(self, method, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.cookie:
            headers["Cookie"] = self.cookie

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                set_cookie = resp.headers.get("Set-Cookie")
                if set_cookie:
                    self.cookie = set_cookie.split(";")[0]
                status = resp.status
                res_data = resp.read().decode("utf-8")
                return status, json.loads(res_data) if res_data else {}
        except urllib.error.HTTPError as e:
            res_data = e.read().decode("utf-8")
            try:
                parsed = json.loads(res_data)
            except Exception:
                parsed = {"error": res_data}
            return e.code, parsed

def run_tests():
    print("=" * 70)
    print("FACULTY DASHBOARD & MULTI-USER ISOLATION VERIFICATION SUITE")
    print("=" * 70)

    # 1. Health check
    client = APISession()
    status, res = client.request("GET", "/api/health")
    assert status == 200, f"Health check failed with {status}"
    print("[PASS] 1. Backend /api/health is healthy (200 OK)")

    # 2. Login as Murugan
    status, login_res = client.request("POST", "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert status == 200, f"Murugan login failed: {login_res}"
    print(f"[PASS] 2. Logged in as Murugan: {login_res.get('user', {}).get('full_name')}")

    # Check Murugan's dashboard stats
    status, m_stats = client.request("GET", "/api/faculty/dashboard-stats")
    assert status == 200, f"Murugan stats failed: {m_stats}"
    assert m_stats.get("faculty_name") == "Murugan", f"Wrong faculty name: {m_stats.get('faculty_name')}"
    assert m_stats.get("total_questions") == 15, f"Expected 15 questions, got {m_stats.get('total_questions')}"
    assert m_stats.get("active_courses") == 2, f"Expected 2 courses, got {m_stats.get('active_courses')}"
    assert m_stats.get("draft_papers") == 3, f"Expected 3 draft papers, got {m_stats.get('draft_papers')}"
    assert m_stats.get("published_exams") == 6, f"Expected 6 published exams, got {m_stats.get('published_exams')}"
    print(f"[PASS] 3. Murugan Stats isolated: Total Q={m_stats['total_questions']}, Courses={m_stats['active_courses']}, Drafts={m_stats['draft_papers']}, Published={m_stats['published_exams']}")

    # Check Murugan's courses
    courses = m_stats.get("courses_list", [])
    assert len(courses) == 2, f"Expected 2 courses in courses_list, got {len(courses)}"
    print(f"[PASS] 4. Murugan Courses validated: {[c['course_code'] + ' - ' + c['course_name'] for c in courses]}")

    # Check Murugan's active draft paper difficulty balancer
    active_paper = m_stats.get("active_paper")
    assert active_paper is not None, "Murugan should have an active draft paper"
    assert active_paper["status"] == "Draft", f"Expected Draft, got {active_paper['status']}"
    assert "difficulty" in active_paper, "Missing difficulty in active_paper"
    assert "blooms" in active_paper, "Missing blooms in active_paper"
    assert active_paper["difficulty"]["easy_count"] > 0, "Expected easy questions"
    assert active_paper["difficulty"]["medium_count"] > 0, "Expected medium questions"
    print(f"[PASS] 5. Murugan Balancer dynamic: '{active_paper['title']}' | {active_paper['difficulty']['easy_pct']}% Easy, {active_paper['difficulty']['medium_pct']}% Medium, {active_paper['difficulty']['hard_pct']}% Hard | {active_paper['balance_label']}")

    # Check standalone /api/faculty/courses
    status, c_res = client.request("GET", "/api/faculty/courses")
    assert status == 200 and len(c_res.get("courses", [])) == 2
    print(f"[PASS] 6. Standalone /api/faculty/courses responds 200 with 2 courses")

    # Check Murugan questions isolation
    status, q_res = client.request("GET", "/api/questions")
    assert status == 200
    m_questions = q_res.get("questions", [])
    assert len(m_questions) == 15, f"Expected 15 questions, got {len(m_questions)}"
    for q in m_questions:
        assert q.get("created_by") == 24, f"Question not created by Murugan: {q}"
    print(f"[PASS] 7. Murugan /api/questions strictly isolated (all 15 created_by=24)")

    # 3. Logout Murugan
    status, _ = client.request("POST", "/api/auth/logout")
    assert status == 200
    print(f"[PASS] 8. Murugan logged out successfully")

    # 4. Login as Mrs V Kavitha
    client_k = APISession()
    status, k_login = client_k.request("POST", "/api/auth/login", {
        "email": "kavitha@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert status == 200, f"Kavitha login failed: {k_login}"
    print(f"[PASS] 9. Logged in as Mrs V Kavitha: {k_login.get('user', {}).get('full_name')}")

    # Check Kavitha's dashboard stats (ALL COUNTS MUST BE 0!)
    status, k_stats = client_k.request("GET", "/api/faculty/dashboard-stats")
    assert status == 200, f"Kavitha stats failed: {k_stats}"
    assert k_stats.get("faculty_name") == "Mrs V Kavitha", f"Wrong faculty name: {k_stats.get('faculty_name')}"
    assert k_stats.get("total_questions") == 0, f"Expected 0 questions for Kavitha, got {k_stats.get('total_questions')}"
    assert k_stats.get("active_courses") == 0, f"Expected 0 courses for Kavitha, got {k_stats.get('active_courses')}"
    assert k_stats.get("draft_papers") == 0, f"Expected 0 drafts for Kavitha, got {k_stats.get('draft_papers')}"
    assert k_stats.get("published_exams") == 0, f"Expected 0 published exams for Kavitha, got {k_stats.get('published_exams')}"
    assert k_stats.get("courses_list") == [], f"Expected empty courses_list, got {k_stats.get('courses_list')}"
    assert k_stats.get("draft_papers_list") == [], f"Expected empty draft_papers_list, got {k_stats.get('draft_papers_list')}"
    assert k_stats.get("published_exams_list") == [], f"Expected empty published_exams_list, got {k_stats.get('published_exams_list')}"
    assert k_stats.get("recent_questions") == [], f"Expected empty recent_questions, got {k_stats.get('recent_questions')}"
    assert k_stats.get("active_paper") is None, f"Expected None active_paper for Kavitha, got {k_stats.get('active_paper')}"
    print(f"[PASS] 10. Kavitha Stats completely isolated at 0: Total Q=0, Courses=0, Drafts=0, Published=0, active_paper=None")

    # Check Kavitha questions list
    status, k_q = client_k.request("GET", "/api/questions")
    assert status == 200 and len(k_q.get("questions", [])) == 0
    print(f"[PASS] 11. Kavitha /api/questions returns empty list (0 questions)")

    # Check Kavitha question papers list
    status, k_p = client_k.request("GET", "/api/question-papers")
    assert status == 200 and len(k_p.get("question_papers", [])) == 0
    print(f"[PASS] 12. Kavitha /api/question-papers returns empty list (0 papers)")

    # 5. Authorization / Security: Kavitha cannot delete or edit Murugan's draft paper
    murugan_draft_id = 4 # Murugan's draft paper
    status, del_res = client_k.request("DELETE", f"/api/question-papers/{murugan_draft_id}")
    assert status in [403, 404], f"Kavitha was able to delete Murugan's paper! Status: {status}"
    print(f"[PASS] 13. Security enforced: Kavitha cannot delete Murugan's draft paper (HTTP {status})")

    # Kavitha cannot delete Murugan's question
    murugan_q_id = 1 # created by Murugan
    status, del_q_res = client_k.request("DELETE", f"/api/questions/{murugan_q_id}")
    assert status in [403, 404], f"Kavitha was able to delete Murugan's question! Status: {status}"
    print(f"[PASS] 14. Security enforced: Kavitha cannot delete Murugan's question (HTTP {status})")

    # 6. Test Kavitha creating a new question
    status, add_q_res = client_k.request("POST", "/api/questions", {
        "question_text": "What is the difference between supervised and unsupervised learning?",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I",
        "topic": "Learning Paradigms",
        "question_type": "Short Answer",
        "difficulty": "Easy",
        "bloom_level": "Understand",
        "marks": 2,
        "is_in_bank": True
    })
    assert status in [200, 201], f"Failed to add question for Kavitha: {add_q_res}"
    created_q_id = add_q_res.get("question", {}).get("id") or add_q_res.get("id")
    print(f"[PASS] 15. Kavitha created question #{created_q_id}")

    # Check that Kavitha's question count is now 1, and Murugan's is still 15
    status, k_stats_after = client_k.request("GET", "/api/faculty/dashboard-stats")
    assert k_stats_after.get("total_questions") == 1, f"Expected 1 question, got {k_stats_after.get('total_questions')}"
    assert k_stats_after.get("active_courses") == 1, f"Expected 1 active course (ML), got {k_stats_after.get('active_courses')}"
    print(f"[PASS] 16. Kavitha dashboard stats updated dynamically: Total Q=1, Active Courses=1")

    # Murugan verification
    client_m2 = APISession()
    client_m2.request("POST", "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    status, m_stats_after = client_m2.request("GET", "/api/faculty/dashboard-stats")
    assert m_stats_after.get("total_questions") == 15, f"Murugan count changed! Expected 15, got {m_stats_after.get('total_questions')}"
    print(f"[PASS] 17. Murugan dashboard stats remain isolated: Total Q=15 (unaffected by Kavitha)")

    # Clean up Kavitha's test question
    status, del_test_q = client_k.request("DELETE", f"/api/questions/{created_q_id}")
    assert status == 200, f"Failed to clean up test question: {del_test_q}"
    status, k_stats_final = client_k.request("GET", "/api/faculty/dashboard-stats")
    assert k_stats_final.get("total_questions") == 0
    print(f"[PASS] 18. Cleaned up Kavitha test question, count restored to 0")

    # Logout
    client_k.request("POST", "/api/auth/logout")
    client_m2.request("POST", "/api/auth/logout")

    print("=" * 70)
    print("ALL 18 VERIFICATION TESTS PASSED SUCCESSFULLY! (100%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
