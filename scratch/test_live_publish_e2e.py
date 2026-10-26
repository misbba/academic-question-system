import urllib.request
import urllib.parse
import http.cookiejar
import json

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print("=" * 80)
print("LIVE HTTP END-TO-END PUBLISH PAPER & VALIDATION TEST")
print("=" * 80)

# 1. Login as Faculty Murugan (Faculty ID 24)
login_url = "http://localhost:5000/api/auth/login"
login_payload = json.dumps({"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_payload, headers={'Content-Type': 'application/json'})
with opener.open(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 200, f"Login failed: {res}"
    print(f"[STEP 1] Login successful as {res.get('user', {}).get('full_name')} (ID: {res.get('user', {}).get('id')})")

# 2. Request Semester Exam Template Generation
template_url = "http://localhost:5000/api/question-papers/generate-template"
tmpl_payload = json.dumps({
    "template_type": "semester_exam",
    "subject": "Distributed Computing",
    "department": "Artificial Intelligence & Data Science",
    "academic_year": "2025-2026",
    "semester": "Sixth Semester"
}).encode('utf-8')
req = urllib.request.Request(template_url, data=tmpl_payload, headers={'Content-Type': 'application/json'})
with opener.open(req) as resp:
    tmpl_res = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 200, f"Template generation failed: {tmpl_res}"
    generated_paper = tmpl_res['paper']
    print(f"[STEP 2] Template generated: {generated_paper['title']} | Total Attempted: {generated_paper['total_marks']}M")

# 3. Save as Draft
save_url = "http://localhost:5000/api/question-papers"
draft_payload = json.dumps({
    "title": generated_paper['title'],
    "subject": generated_paper['subject'],
    "department": generated_paper['department'],
    "academic_year": generated_paper['academic_year'],
    "semester": generated_paper['semester'],
    "exam_type": "Semester Examination",
    "duration": generated_paper['duration'],
    "total_marks": 100,
    "instructions": generated_paper['instructions'],
    "status": "Draft",
    "sections": generated_paper['sections'],
    "question_ids": [q['id'] for q in generated_paper['sections'][0]['questions']]
}).encode('utf-8')
req = urllib.request.Request(save_url, data=draft_payload, headers={'Content-Type': 'application/json'})
with opener.open(req) as resp:
    draft_res = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 201, f"Draft save failed: {draft_res}"
    saved_paper = draft_res.get('question_paper') or draft_res.get('paper')
    paper_id = saved_paper['id']
    print(f"[STEP 3] Paper saved as Draft in MySQL with ID: {paper_id}")

# 4. Publish the Paper (100 Marks Attempted)
pub_url = f"http://localhost:5000/api/question-papers/{paper_id}"
pub_payload = json.dumps({
    "status": "Published"
}).encode('utf-8')
req = urllib.request.Request(pub_url, data=pub_payload, headers={'Content-Type': 'application/json'}, method='PUT')
with opener.open(req) as resp:
    pub_res = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 200, f"Publish failed: {pub_res}"
    print(f"[STEP 4] Paper {paper_id} successfully published to students with status 200!")

# 5. Verify Paper in Published List
list_url = "http://localhost:5000/api/question-papers?status=Published"
req = urllib.request.Request(list_url)
with opener.open(req) as resp:
    list_res = json.loads(resp.read().decode('utf-8'))
    papers = list_res.get('papers') or list_res.get('question_papers') or []
    published_match = any(p['id'] == paper_id for p in papers)
    assert published_match, f"Published paper {paper_id} not found in published list"
    print(f"[STEP 5] Confirmed: Paper {paper_id} is present in Published examination papers list.")

# 6. Attempt to publish an invalid 50-mark paper as Semester Examination
invalid_draft_payload = json.dumps({
    "title": "Invalid 50-Mark Semester Exam",
    "subject": "Distributed Computing",
    "department": "Artificial Intelligence & Data Science",
    "exam_type": "Semester Examination",
    "total_marks": 50,
    "status": "Published",
    "sections": [
        {"name": "PART - A", "count": 5, "marks_per_q": 2},
        {"name": "PART - B", "count": 1, "marks_per_q": 8},
        {"name": "PART - C", "count": 2, "marks_per_q": 16}
    ],
    "question_ids": [101, 102]
}).encode('utf-8')
req = urllib.request.Request(save_url, data=invalid_draft_payload, headers={'Content-Type': 'application/json'})
try:
    with opener.open(req) as resp:
        print(f"FAILED: Invalid paper unexpectedly accepted with status {resp.status}")
except urllib.error.HTTPError as err:
    err_body = json.loads(err.read().decode('utf-8'))
    assert err.code == 400, f"Expected 400, got {err.code}"
    err_msg = err_body.get('message', '')
    assert "Semester Examination must have exactly 100 attempted marks (calculated: 50 marks)" in err_msg
    print(f"[STEP 6] Confirmed: Invalid 50-mark paper correctly rejected with HTTP 400: '{err_msg}'")

print("\n" + "=" * 80)
print("ALL LIVE HTTP END-TO-END TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
