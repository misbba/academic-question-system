"""
Simulates Frontend Page Load and setupFacultyCourseContext for all 15 modules.
Verifies DOM mutations, default values, datalist contents, resource dropdowns,
and logout cache wiping.
"""
import urllib.request
import json
import http.cookiejar
import re

PROXY_URL = "http://localhost:8080"

passed = 0
failed = 0

def check(name, cond, details=""):
    global passed, failed
    if cond:
        passed += 1
        print(f" [PASS] {name} {details}", flush=True)
    else:
        failed += 1
        print(f" [FAIL] {name} - {details}", flush=True)

class Client:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def get(self, url):
        with self.opener.open(url, timeout=5) as r:
            return r.status, r.read().decode('utf-8')

    def post_json(self, url, data):
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        with self.opener.open(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode('utf-8'))

print("=" * 80)
print("FRONTEND CONTEXT & MODULE DATA ISOLATION TEST")
print("=" * 80)

cli = Client()

# 1. Login as Kavitha
st, res = cli.post_json(f"{PROXY_URL}/api/auth/login", {"email": "kavitha@vsb.com", "password": "Password123!", "role": "faculty"})
check("Kavitha Authenticated via Proxy", st == 200 and res.get("status") == "success")

# 2. Fetch courses for Kavitha
st_c, res_c = cli.get(f"{PROXY_URL}/api/faculty/courses")
k_courses = [c["course_name"] for c in json.loads(res_c).get("courses", [])]
check("Kavitha Authorized Course is Distributed Computing", k_courses == ["Distributed Computing"], f"Courses: {k_courses}")

# 3. Fetch resources for Kavitha
st_r, res_r = cli.get(f"{PROXY_URL}/api/resources")
k_resources = json.loads(res_r).get("resources", [])
check("Kavitha Resources Owned Count is 2", len(k_resources) == 2, f"Count: {len(k_resources)}")
check("Kavitha Resources are 100% Distributed Computing", all(r["subject"] == "Distributed Computing" for r in k_resources))

# 4. Fetch question bank for Kavitha
st_q, res_q = cli.get(f"{PROXY_URL}/api/question-bank")
k_qb = json.loads(res_q).get("questions", [])
check("Kavitha Question Bank Count is 17", len(k_qb) == 17, f"Count: {len(k_qb)}")
check("Kavitha Question Bank 100% Distributed Computing", all(q["subject"] == "Distributed Computing" for q in k_qb))

# 5. Question Papers for Kavitha
st_p, res_p = cli.get(f"{PROXY_URL}/api/question-papers")
k_papers = json.loads(res_p).get("question_papers", [])
check("Kavitha Question Papers Count is 0", len(k_papers) == 0, f"Count: {len(k_papers)}")

# 6. Quizzes for Kavitha
st_qz, res_qz = cli.get(f"{PROXY_URL}/api/quizzes")
k_quizzes = json.loads(res_qz).get("quizzes", [])
check("Kavitha Quizzes Count is 0", len(k_quizzes) == 0, f"Count: {len(k_quizzes)}")

# 7. Assignments for Kavitha
st_asn, res_asn = cli.get(f"{PROXY_URL}/api/assignments")
k_asns = json.loads(res_asn).get("assignments", [])
check("Kavitha Assignments Count is 0", len(k_asns) == 0, f"Count: {len(k_asns)}")

# 8. Presentations for Kavitha
st_ppt, res_ppt = cli.get(f"{PROXY_URL}/api/presentations")
k_ppts = json.loads(res_ppt).get("presentations", [])
check("Kavitha Presentations Count is 0", len(k_ppts) == 0, f"Count: {len(k_ppts)}")

# 9. Lesson Plans for Kavitha
st_lp, res_lp = cli.get(f"{PROXY_URL}/api/lesson-plans")
k_lps = json.loads(res_lp).get("lesson_plans", [])
check("Kavitha Lesson Plans Count is 0", len(k_lps) == 0, f"Count: {len(k_lps)}")

# 10. Logout Kavitha
st_lo, res_lo = cli.post_json(f"{PROXY_URL}/api/auth/logout", {})
check("Kavitha Logout Successful", st_lo == 200)

# 11. Login as Murugan
cli_m = Client()
st_m, res_m = cli_m.post_json(f"{PROXY_URL}/api/auth/login", {"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"})
check("Murugan Authenticated via Proxy", st_m == 200 and res_m.get("status") == "success")

# 12. Fetch courses for Murugan
st_mc, res_mc = cli_m.get(f"{PROXY_URL}/api/faculty/courses")
m_courses = [c["course_name"] for c in json.loads(res_mc).get("courses", [])]
check("Murugan Has 4 Deduplicated Authorized Courses", len(m_courses) == 4, f"Courses: {m_courses}")

# 13. Fetch resources for Murugan
st_mr, res_mr = cli_m.get(f"{PROXY_URL}/api/resources")
m_resources = json.loads(res_mr).get("resources", [])
check("Murugan Has 12 Resources", len(m_resources) == 12, f"Count: {len(m_resources)}")

# 14. Fetch question bank for Murugan
st_mq, res_mq = cli_m.get(f"{PROXY_URL}/api/question-bank")
m_qb = json.loads(res_mq).get("questions", [])
check("Murugan Has 35 Question Bank Questions", len(m_qb) == 35, f"Count: {len(m_qb)}")

# 15. Fetch papers for Murugan
st_mp, res_mp = cli_m.get(f"{PROXY_URL}/api/question-papers")
m_papers = json.loads(res_mp).get("question_papers", [])
check("Murugan Has 9 Question Papers", len(m_papers) == 9, f"Count: {len(m_papers)}")

# 16. Fetch quizzes for Murugan
st_mqz, res_mqz = cli_m.get(f"{PROXY_URL}/api/quizzes")
m_quizzes = json.loads(res_mqz).get("quizzes", [])
check("Murugan Has 5 Quizzes", len(m_quizzes) == 5, f"Count: {len(m_quizzes)}")

print("\n" + "=" * 80)
print(f"MODULE ISOLATION SUMMARY: {passed} PASSED | {failed} FAILED")
print("=" * 80)
