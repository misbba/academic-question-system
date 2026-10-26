import requests
import re
import os

BASE_API = "http://localhost:5000/api"
BASE_FE = "http://localhost:8080"

print("=" * 60)
print("COMPREHENSIVE FINAL VERIFICATION SUITE")
print("=" * 60)

# ----------------------------------------------------
# 1. VERIFY BACKEND HEALTH & FRONTEND CONNECTIVITY
# ----------------------------------------------------
print("\n[1] Verifying Servers...")
r_health = requests.get(f"{BASE_API}/health")
assert r_health.status_code == 200, f"Backend health failed: {r_health.text}"
print(" -> Backend API Healthy: Port 5000 is active and connected to MySQL.")

r_root = requests.get(f"{BASE_FE}/index.html")
assert r_root.status_code == 200, "Frontend index.html failed"
print(" -> Frontend Server Healthy: Port 8080 is active.")

# ----------------------------------------------------
# 2. FACULTY MURUGAN IDENTITY & DASHBOARD STATS
# ----------------------------------------------------
print("\n[2] Testing Faculty Murugan Identity & Real Stats...")
s_murugan = requests.Session()
r_mlogin = s_murugan.post(f"{BASE_API}/auth/login", json={
    "email": "muruga@vsb.com",
    "password": "Password123!",
    "role": "faculty"
})
assert r_mlogin.status_code == 200, f"Murugan login failed: {r_mlogin.text}"
m_user = r_mlogin.json()["user"]
print(f" -> Authenticated as: {m_user['full_name']} ({m_user['email']}), Role: {m_user['role']}")
assert m_user["full_name"] == "Murugan", f"Expected Murugan, got {m_user['full_name']}"

# Verify /me endpoint
r_m_me = s_murugan.get(f"{BASE_API}/auth/me")
assert r_m_me.status_code == 200
assert r_m_me.json()["user"]["full_name"] == "Murugan"
print(" -> /api/auth/me verified: Murugan")

# Verify real dashboard stats for Murugan
r_m_stats = s_murugan.get(f"{BASE_API}/faculty/dashboard-stats")
assert r_m_stats.status_code == 200
m_stats = r_m_stats.json()
print(f" -> Murugan Dashboard Stats:")
print(f"    - Total Questions: {m_stats['total_questions']}")
print(f"    - Active Courses:  {m_stats['active_courses']}")
print(f"    - Draft Papers:    {m_stats['draft_papers']}")
print(f"    - Published Exams: {m_stats['published_exams']}")
assert m_stats['total_questions'] == 22, f"Expected 22 questions, got {m_stats['total_questions']}"
assert m_stats['active_courses'] == 1, f"Expected 1 course, got {m_stats['active_courses']}"
assert m_stats['draft_papers'] == 2, f"Expected 2 draft papers, got {m_stats['draft_papers']}"
assert m_stats['published_exams'] == 6, f"Expected 6 published exams, got {m_stats['published_exams']}"
assert m_stats['active_paper'] is not None, "Expected active paper object"
print(f"    - Active Paper:    {m_stats['active_paper']['title']} ({m_stats['active_paper']['paper_code']})")

# ----------------------------------------------------
# 3. FACULTY DR. ALAN TURING IDENTITY & DYNAMIC STATS (VERIFY NO HARDCODING)
# ----------------------------------------------------
print("\n[3] Testing Second Faculty Account (Dr. Alan Turing) to Prove Dynamic Behavior...")
s_turing = requests.Session()
r_tlogin = s_turing.post(f"{BASE_API}/auth/login", json={
    "email": "turing@university.edu",
    "password": "Password123!",
    "role": "faculty"
})
assert r_tlogin.status_code == 200, f"Turing login failed: {r_tlogin.text}"
t_user = r_tlogin.json()["user"]
print(f" -> Authenticated as: {t_user['full_name']} ({t_user['email']}), Role: {t_user['role']}")
assert t_user["full_name"] == "Dr. Alan Turing", f"Expected Dr. Alan Turing, got {t_user['full_name']}"

r_t_stats = s_turing.get(f"{BASE_API}/faculty/dashboard-stats")
assert r_t_stats.status_code == 200
t_stats = r_t_stats.json()
print(f" -> Dr. Alan Turing Dashboard Stats:")
print(f"    - Total Questions: {t_stats['total_questions']}")
print(f"    - Active Courses:  {t_stats['active_courses']}")
print(f"    - Draft Papers:    {t_stats['draft_papers']}")
print(f"    - Published Exams: {t_stats['published_exams']}")
assert t_stats['total_questions'] == 22, "Expected 22 repository questions"
assert t_stats['draft_papers'] == 0, f"Expected 0 draft papers for Turing, got {t_stats['draft_papers']}"
assert t_stats['published_exams'] == 0, f"Expected 0 published exams for Turing, got {t_stats['published_exams']}"
print(" -> Confirmed: Statistics and profile are 100% dynamic per authenticated account!")

# ----------------------------------------------------
# 4. STUDENT JENITTA BLESSY IDENTITY & FLOW
# ----------------------------------------------------
print("\n[4] Testing Student Jenitta Blessy Authentication & Endpoints...")
s_jeni = requests.Session()
r_jlogin = s_jeni.post(f"{BASE_API}/auth/login", json={
    "email": "jeni@vsb.com",
    "password": "12345678",
    "role": "student"
})
assert r_jlogin.status_code == 200, f"Student login failed: {r_jlogin.text}"
j_user = r_jlogin.json()["user"]
print(f" -> Authenticated as: {j_user['full_name']} ({j_user['email']}), Role: {j_user['role']}")
assert j_user["full_name"] == "Jenitta Blessy", f"Expected Jenitta Blessy, got {j_user['full_name']}"

# Student access to published papers
r_j_papers = s_jeni.get(f"{BASE_API}/question-papers")
assert r_j_papers.status_code == 200
pub_papers = r_j_papers.json().get("question_papers", [])
print(f" -> Student retrieved {len(pub_papers)} published examination papers")
assert len(pub_papers) >= 6, "Expected at least 6 published papers"

# Student access to quizzes
r_j_quizzes = s_jeni.get(f"{BASE_API}/quizzes")
assert r_j_quizzes.status_code == 200
quizzes = r_j_quizzes.json().get("quizzes", [])
print(f" -> Student retrieved {len(quizzes)} published quizzes")

# ----------------------------------------------------
# 5. SCAN ALL 32 FRONTEND HTML PAGES ON PORT 8080
# ----------------------------------------------------
print("\n[5] Scanning All 32 Frontend Pages on Port 8080...")
pages = [
    "index.html",
    "faculty-login.html", "faculty-register.html", "faculty-dashboard.html",
    "faculty-resources.html", "faculty-generate-questions.html", "faculty-voice-question.html",
    "faculty-image-question.html", "faculty-language-converter.html", "faculty-question-paper.html",
    "faculty-generate-quiz.html", "faculty-generate-assignment.html", "faculty-generate-ppt.html",
    "faculty-generate-lesson-plan.html", "faculty-results.html", "faculty-performance.html",
    "faculty-history.html", "faculty-profile.html",
    "student-login.html", "student-register.html", "student-dashboard.html",
    "student-subjects.html", "student-materials.html", "student-question-papers.html",
    "student-quizzes.html", "student-assignments.html", "student-presentations.html",
    "student-lesson-plans.html", "student-results.html", "student-performance.html",
    "student-history.html", "student-profile.html"
]

for page in pages:
    res = requests.get(f"{BASE_FE}/{page}")
    assert res.status_code == 200, f"Page {page} returned status {res.status_code}"
    html = res.text
    # Verify Vance is not present
    assert "Alistair" not in html and "Vance" not in html, f"Page {page} contains Vance!"
    # Verify cache buster present in non-login pages
    if "login" not in page and "register" not in page and page != "index.html":
        assert "js/app.js?v=20261025" in html, f"Page {page} missing cache buster on app.js"
        assert "js/auth.js?v=20261025" in html, f"Page {page} missing cache buster on auth.js"

print(f" -> ALL {len(pages)} PAGES RETURNED HTTP 200 WITH ZERO OCCURRENCES OF DR. ALISTAIR VANCE AND FRESH CACHE BUSTERS!")

print("\n" + "=" * 60)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY (100% PASS)!")
print("=" * 60)
