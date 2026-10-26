import urllib.request
import urllib.parse
import json
import http.cookiejar
import sys

BASE_URL = "http://localhost:5000"
PROXY_URL = "http://localhost:8080"

passed_tests = 0
failed_tests = 0

def log_test(name, passed, detail=""):
    global passed_tests, failed_tests
    if passed:
        passed_tests += 1
        print(f" [PASS] {name} {detail}", flush=True)
    else:
        failed_tests += 1
        print(f" [FAIL] {name} - {detail}", flush=True)

class SessionClient:
    def __init__(self, base=BASE_URL):
        self.base = base
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def request(self, path, method="GET", data=None):
        url = f"{self.base}{path}"
        headers = {}
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=5) as resp:
                status = resp.status
                raw = resp.read().decode("utf-8")
                try:
                    res_json = json.loads(raw)
                except Exception:
                    res_json = raw
                return status, res_json
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            try:
                err_json = json.loads(raw)
            except Exception:
                err_json = raw
            return e.code, err_json
        except Exception as e:
            return 500, str(e)

    def login(self, email, password, role="faculty"):
        status, resp = self.request("/api/auth/login", method="POST", data={
            "email": email,
            "password": password,
            "role": role
        })
        return status == 200 and resp.get("status") == "success", resp


print("=" * 80)
print("FACULTY DATA ISOLATION VERIFICATION SUITE")
print("Target Accounts: Murugan (ID 24) & Mrs V Kavitha (ID 25)")
print("=" * 80)

murugan = SessionClient()
kavitha = SessionClient()

# -------------------------------------------------------------
# 1. AUTHENTICATION TEST
# -------------------------------------------------------------
print("\n--- 1. Authenticating Both Faculty Accounts ---")
m_ok, m_login = murugan.login("muruga@vsb.com", "Password123!")
log_test("Murugan Authentication", m_ok, f"ID={m_login.get('user', {}).get('id')}, Name={m_login.get('user', {}).get('full_name')}")

k_ok, k_login = kavitha.login("kavitha@vsb.com", "Password123!")
log_test("Kavitha Authentication", k_ok, f"ID={k_login.get('user', {}).get('id')}, Name={k_login.get('user', {}).get('full_name')}")

# -------------------------------------------------------------
# 2. FACULTY DASHBOARD STATS (Module 1)
# -------------------------------------------------------------
print("\n--- 2. Dashboard Statistics & Counts (Module 1) ---")
m_s_code, m_stats = murugan.request("/api/faculty/dashboard-stats")
log_test("Murugan Dashboard Stats Success", m_s_code == 200 and m_stats.get("status") == "success")
log_test("Murugan Total Bank Questions", m_stats.get("total_questions") == 35, f"Value: {m_stats.get('total_questions')}")
log_test("Murugan Active Courses Count", m_stats.get("active_courses") == 4, f"Value: {m_stats.get('active_courses')}")
log_test("Murugan Draft Papers Count", m_stats.get("draft_papers") == 3, f"Value: {m_stats.get('draft_papers')}")
log_test("Murugan Published Exams Count", m_stats.get("published_exams") == 6, f"Value: {m_stats.get('published_exams')}")

k_s_code, k_stats = kavitha.request("/api/faculty/dashboard-stats")
log_test("Kavitha Dashboard Stats Success", k_s_code == 200 and k_stats.get("status") == "success")
log_test("Kavitha Total Bank Questions", k_stats.get("total_questions") == 17, f"Value: {k_stats.get('total_questions')} (Target: 17)")
log_test("Kavitha Active Courses Count", k_stats.get("active_courses") == 1, f"Value: {k_stats.get('active_courses')} (Target: 1)")
log_test("Kavitha Draft Papers Count", k_stats.get("draft_papers") == 0, f"Value: {k_stats.get('draft_papers')} (Target: 0)")
log_test("Kavitha Published Exams Count", k_stats.get("published_exams") == 0, f"Value: {k_stats.get('published_exams')} (Target: 0)")

# -------------------------------------------------------------
# 3. ACTIVE COURSES DEDUPLICATION & ISOLATION (Module 1)
# -------------------------------------------------------------
print("\n--- 3. Active Courses Deduplication & Isolation (Module 1) ---")
m_c_code, m_courses_resp = murugan.request("/api/faculty/courses")
m_courses = [c["course_name"] for c in m_courses_resp.get("courses", [])]
log_test("Murugan 4 Unique Courses", len(m_courses) == 4, f"Courses: {m_courses}")
log_test("Murugan Course Deduplication (No duplicates)", len(m_courses) == len(set(m_courses)))

k_c_code, k_courses_resp = kavitha.request("/api/faculty/courses")
k_courses = [c["course_name"] for c in k_courses_resp.get("courses", [])]
log_test("Kavitha Exactly 1 Course", len(k_courses) == 1 and k_courses[0] == "Distributed Computing", f"Courses: {k_courses}")
log_test("Kavitha Has Zero DBMS/ML Courses", "Database Management Systems" not in k_courses and "Machine Learning" not in k_courses)

# -------------------------------------------------------------
# 4. ACADEMIC RESOURCES (Modules 1 & 12)
# -------------------------------------------------------------
print("\n--- 4. Academic Resources Ownership & Access Control (Modules 1 & 12) ---")
m_r_code, m_res_resp = murugan.request("/api/resources")
m_res = m_res_resp.get("resources", [])
log_test("Murugan Resources Count", len(m_res) == 12, f"Count: {len(m_res)}")

k_r_code, k_res_resp = kavitha.request("/api/resources")
k_res = k_res_resp.get("resources", [])
log_test("Kavitha Resources Count", len(k_res) == 2, f"Count: {len(k_res)}")
k_res_subjects = list(set(r["subject"] for r in k_res))
log_test("Kavitha Resources Subject Strictly Distributed Computing", k_res_subjects == ["Distributed Computing"], f"Subjects: {k_res_subjects}")

# Direct Resource Access Tampering Test
if m_res and k_res:
    m_res_id = m_res[0]["id"]
    k_res_id = k_res[0]["id"]
    
    # Kavitha trying to view Murugan's resource
    tamper_code, tamper_resp = kavitha.request(f"/api/resources/{m_res_id}")
    log_test("Kavitha Accessing Murugan Resource Forbidden (403)", tamper_code == 403, f"Code: {tamper_code}")
    
    # Murugan trying to view Kavitha's resource
    tamper_code2, tamper_resp2 = murugan.request(f"/api/resources/{k_res_id}")
    log_test("Murugan Accessing Kavitha Resource Forbidden (403)", tamper_code2 == 403, f"Code: {tamper_code2}")

# -------------------------------------------------------------
# 5. QUESTION BANK & QUESTIONS (Modules 2 & 11)
# -------------------------------------------------------------
print("\n--- 5. Question Bank Ownership & Tampering Protection (Modules 2 & 11) ---")
m_qb_code, m_qb_resp = murugan.request("/api/question-bank")
m_qb = m_qb_resp.get("questions", [])
log_test("Murugan Question Bank Count", len(m_qb) == 35, f"Count: {len(m_qb)}")

k_qb_code, k_qb_resp = kavitha.request("/api/question-bank")
k_qb = k_qb_resp.get("questions", [])
log_test("Kavitha Question Bank Count", len(k_qb) == 17, f"Count: {len(k_qb)}")
k_qb_subjects = list(set(q["subject"] for q in k_qb))
log_test("Kavitha Questions Subject Strictly Distributed Computing", k_qb_subjects == ["Distributed Computing"], f"Subjects: {k_qb_subjects}")

# Direct Question Access Tampering Test
if m_qb and k_qb:
    m_qid = m_qb[0]["id"]
    k_qid = k_qb[0]["id"]
    
    # Kavitha viewing Murugan's question
    tamper_q_code, _ = kavitha.request(f"/api/questions/{m_qid}")
    log_test("Kavitha Accessing Murugan Question Forbidden (403)", tamper_q_code == 403, f"Code: {tamper_q_code}")
    
    # Murugan viewing Kavitha's question
    tamper_q_code2, _ = murugan.request(f"/api/questions/{k_qid}")
    log_test("Murugan Accessing Kavitha Question Forbidden (403)", tamper_q_code2 == 403, f"Code: {tamper_q_code2}")

    # Kavitha editing Murugan's question
    tamper_edit_code, _ = kavitha.request(f"/api/questions/{m_qid}", method="PUT", data={"question_text": "Hacked question"})
    log_test("Kavitha Editing Murugan Question Forbidden (403)", tamper_edit_code == 403, f"Code: {tamper_edit_code}")

    # Kavitha deleting Murugan's question
    tamper_del_code, _ = kavitha.request(f"/api/questions/{m_qid}", method="DELETE")
    log_test("Kavitha Deleting Murugan Question Forbidden (403)", tamper_del_code == 403, f"Code: {tamper_del_code}")

# -------------------------------------------------------------
# 6. QUESTION PAPERS & BUILDER (Modules 6 & 13)
# -------------------------------------------------------------
print("\n--- 6. Question Papers & Builder Isolation (Modules 6 & 13) ---")
m_qp_code, m_qp_resp = murugan.request("/api/question-papers")
m_papers = m_qp_resp.get("question_papers", [])
log_test("Murugan Question Papers Count", len(m_papers) == 9, f"Count: {len(m_papers)}")

k_qp_code, k_qp_resp = kavitha.request("/api/question-papers")
k_papers = k_qp_resp.get("question_papers", [])
log_test("Kavitha Question Papers Count (Zero)", len(k_papers) == 0, f"Count: {len(k_papers)}")

# Direct Paper Access Tampering Test
if m_papers:
    m_pid = m_papers[0]["id"]
    tamper_p_code, _ = kavitha.request(f"/api/question-papers/{m_pid}")
    log_test("Kavitha Accessing Murugan Paper Forbidden (403)", tamper_p_code == 403, f"Code: {tamper_p_code}")

# -------------------------------------------------------------
# 7. QUIZZES (Module 7)
# -------------------------------------------------------------
print("\n--- 7. Quiz Isolation & Tampering Protection (Module 7) ---")
m_qz_code, m_qz_resp = murugan.request("/api/quizzes")
m_quizzes = m_qz_resp.get("quizzes", [])
log_test("Murugan Quizzes Count", len(m_quizzes) == 5, f"Count: {len(m_quizzes)}")

k_qz_code, k_qz_resp = kavitha.request("/api/quizzes")
k_quizzes = k_qz_resp.get("quizzes", [])
log_test("Kavitha Quizzes Count (Zero)", len(k_quizzes) == 0, f"Count: {len(k_quizzes)}")

if m_quizzes:
    m_qzid = m_quizzes[0]["id"]
    tamper_qz_code, _ = kavitha.request(f"/api/quizzes/{m_qzid}")
    log_test("Kavitha Accessing Murugan Quiz Forbidden (403)", tamper_qz_code == 403, f"Code: {tamper_qz_code}")

# -------------------------------------------------------------
# 8. ASSIGNMENTS, PPT, LESSON PLANS & HISTORY (Modules 8, 9, 10, 14)
# -------------------------------------------------------------
print("\n--- 8. Assignments, PPT, Lesson Plans & Activity History (Modules 8, 9, 10, 14) ---")

# Test creating an assignment for Murugan
m_asn_code, m_asn_res = murugan.request("/api/assignments", method="POST", data={
    "title": "Murugan DBMS Assignment 1",
    "subject": "Database Management Systems",
    "department": "Artificial Intelligence & Data Science",
    "unit": "Unit 2",
    "total_marks": 20
})
log_test("Murugan Assignment Creation", m_asn_code == 201, f"ID: {m_asn_res.get('id')}")

# Verify Kavitha does NOT see Murugan's assignment
k_asn_code, k_asn_res = kavitha.request("/api/assignments")
k_asns = k_asn_res.get("assignments", [])
k_has_murugan = any(a["title"] == "Murugan DBMS Assignment 1" for a in k_asns)
log_test("Kavitha Cannot See Murugan's Assignment", not k_has_murugan, f"Count: {len(k_asns)}")

# Murugan sees his assignment
m_asn_list_code, m_asn_list = murugan.request("/api/assignments")
m_asns = m_asn_list.get("assignments", [])
m_has_own = any(a["title"] == "Murugan DBMS Assignment 1" for a in m_asns)
log_test("Murugan Sees His Own Assignment", m_has_own, f"Count: {len(m_asns)}")

# Clean up Murugan's test assignment
if m_asn_res.get("id"):
    murugan.request(f"/api/assignments/{m_asn_res['id']}", method="DELETE")

# Test Activity History Isolation
murugan.request("/api/faculty/history", method="POST", data={
    "activity_type": "Paper Generation",
    "title": "Murugan Test Session",
    "subject": "Database Management Systems",
    "unit": "Unit 1"
})
k_hist_code, k_hist_res = kavitha.request("/api/faculty/history")
k_hist = k_hist_res.get("history", [])
k_has_m_hist = any(h["title"] == "Murugan Test Session" for h in k_hist)
log_test("Kavitha Cannot See Murugan Activity History", not k_has_m_hist, f"Kavitha History Count: {len(k_hist)}")

# -------------------------------------------------------------
# 9. FRONTEND PROXY VERIFICATION (PORT 8080)
# -------------------------------------------------------------
print("\n--- 9. Frontend Reverse Proxy on Port 8080 ---")
proxy_client = SessionClient(base=PROXY_URL)
p_ok, p_login = proxy_client.login("kavitha@vsb.com", "Password123!")
log_test("Login via Port 8080 Reverse Proxy", p_ok, f"User: {p_login.get('user', {}).get('full_name')}")

p_code, p_stats = proxy_client.request("/api/faculty/dashboard-stats")
log_test("Dashboard Stats via Port 8080 Proxy", p_code == 200 and p_stats.get("total_questions") == 17)

# -------------------------------------------------------------
# 10. LOGOUT & SESSION INVALIDATION
# -------------------------------------------------------------
print("\n--- 10. Logout & Session Invalidation ---")
lo_code, lo_res = proxy_client.request("/api/auth/logout", method="POST")
log_test("Logout Success", lo_code == 200 and lo_res.get("status") == "success")

# Verify session is dead
after_lo_code, _ = proxy_client.request("/api/auth/me")
log_test("Session Dead After Logout (401)", after_lo_code == 401)

print("\n" + "=" * 80)
print(f"TEST SUMMARY: {passed_tests} PASSED | {failed_tests} FAILED")
print("=" * 80)

if failed_tests > 0:
    sys.exit(1)
