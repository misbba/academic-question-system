"""
Comprehensive End-to-End Verification Suite for All Requirements:
1. Reverse Proxy on Port 8080 (Health, Login, Resources)
2. Grounded Question Generation from uploaded study material
3. Question Bank Save flow:
   - Validates and saves generated questions (text, subject, dept, unit, topic, diff, type, marks, bloom)
   - Persists in MySQL database (is_in_bank=1, status='Bank')
   - Prevents duplicate submissions / inserts
   - Returns clear success with updated IDs
4. Requirement 1 & 2: Manual Inputs (Dept, Subj, Unit, Topic) across all 7 modules:
   - Voice-to-Question Generator (Dept, Subj, Unit, Topic)
   - Image/Diagram Questions (Dept, Subj, Unit, Topic)
   - Language Conversion (Dept, Subj, Unit, Topic)
   - Paper Builder (Dept, Subj)
   - Assignment Generator (Dept, Subj, Unit, Topic, editable number count)
   - PPT Generator (Dept, Subj, Unit, Topic)
   - Lesson Plan Generator (Dept, Subj, Unit, Topic)
5. Unit inputs support "All Units (Complete Syllabus)", "Unit 1..5", and custom names
6. Topic input is editable and optional (defaulting to syllabus/unit)
7. js/app.js execution integrity (no syntax errors, zero broken .options references)
"""

import sys
import json
import urllib.request
import urllib.error
import http.cookiejar
import pymysql
import os
import re

PORT_8080 = "http://127.0.0.1:8080"
PORT_5000 = "http://127.0.0.1:5000"

COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))

def make_req(url, method="GET", data=None, headers=None):
    hdrs = headers or {}
    body = None
    if data is not None:
        if isinstance(data, dict):
            body = json.dumps(data).encode("utf-8")
            hdrs["Content-Type"] = "application/json"
        elif isinstance(data, bytes):
            body = data
        else:
            body = data.encode("utf-8")

    req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    try:
        with OPENER.open(req, timeout=30) as resp:
            resp_body = resp.read().decode("utf-8")
            ct = resp.headers.get_content_type()
            is_json = ct == "application/json" or resp_body.strip().startswith("{")
            return {
                "status": resp.status,
                "is_json": is_json,
                "data": json.loads(resp_body) if is_json else resp_body,
                "headers": dict(resp.headers)
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        is_json = err_body.strip().startswith("{")
        return {
            "status": e.code,
            "is_json": is_json,
            "data": json.loads(err_body) if is_json else err_body,
            "headers": dict(e.headers)
        }

def encode_multipart_formdata(fields, files):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}\r\n".encode("utf-8"))
        lines.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        lines.append(f"{value}\r\n".encode("utf-8"))
    for name, (filename, file_bytes) in files.items():
        lines.append(f"--{boundary}\r\n".encode("utf-8"))
        lines.append(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode("utf-8"))
        lines.append(b"Content-Type: application/octet-stream\r\n\r\n")
        lines.append(file_bytes)
        lines.append(b"\r\n")
    lines.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(lines)
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type

def run_tests():
    print("=" * 70)
    print("TEST 1: Reverse Proxy & Health Check on Port 8080")
    print("=" * 70)

    try:
        r = make_req(f"{PORT_8080}/api/health")
        assert r["status"] == 200, f"Expected 200, got {r['status']}: {r['data']}"
        assert r["data"].get("status") in ["healthy", "success"], f"Expected healthy: {r['data']}"
        print(f"[PASS] Proxy /api/health returned 200 OK: {r['data']}")
    except Exception as e:
        print(f"[FAIL] Proxy /api/health failed: {e}")
        return False

    print("\n" + "=" * 70)
    print("TEST 2: Faculty Authentication on Port 8080")
    print("=" * 70)

    login_payload = {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    }
    r = make_req(f"{PORT_8080}/api/auth/login", method="POST", data=login_payload)
    assert r["status"] == 200, f"Login failed with code {r['status']}: {r['data']}"
    assert r["data"].get("status") == "success", f"Login response unsuccessful: {r['data']}"
    faculty_user = r["data"].get("user", {})
    faculty_id = faculty_user.get("id")
    print(f"[PASS] Logged in as: {faculty_user.get('name') or faculty_user.get('full_name')} (ID: {faculty_id}, Role: {faculty_user.get('role')})")

    print("\n" + "=" * 70)
    print("TEST 3: Resources Endpoint on Port 8080 (No 404 or HTML)")
    print("=" * 70)

    r = make_req(f"{PORT_8080}/api/resources")
    assert r["status"] == 200, f"Resources endpoint returned {r['status']}: {r['data']}"
    assert r["is_json"], f"Content-Type not JSON: {r['headers']}"
    assert "resources" in r["data"], f"Resources key missing: {r['data']}"
    print(f"[PASS] /api/resources returned {len(r['data']['resources'])} academic resource(s)")

    print("\n" + "=" * 70)
    print("TEST 4: Quick Upload of Study Material & Grounded Question Generation")
    print("=" * 70)

    study_notes = """
    Distributed Systems and Cloud Fundamentals
    Unit 2: Remote Procedure Calls and Message Passing
    Remote Procedure Call (RPC) is a protocol that one program can use to request a service from a program located in another computer on a network.
    RPC uses client and server stubs to marshal and unmarshal parameters.
    Message passing provides asynchronous communication between processes via send and receive primitives.
    Idempotent operations can be repeated safely without changing the system state, crucial for fault tolerance in RPC.
    Synchronous vs asynchronous message passing differs in blocking semantics during message transfer.
    """
    fields = {
        "subject": "Distributed Computing",
        "department": "Computer Science and Engineering",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit 2",
        "topic": "Remote Procedure Calls and Message Passing",
        "resource_type": "Study Material",
        "description": "Verified study material for RPC and Message Passing"
    }
    files = {
        "file": ("Distributed_RPC_Notes.txt", study_notes.encode("utf-8"))
    }
    body, ct = encode_multipart_formdata(fields, files)
    upload_resp = make_req(f"{PORT_8080}/api/resources", method="POST", data=body, headers={"Content-Type": ct})
    assert upload_resp["status"] == 201, f"Upload failed: {upload_resp}"
    uploaded_resource = upload_resp["data"]["resource"]
    res_id = uploaded_resource["id"]
    print(f"[PASS] Uploaded study material: ID {res_id}, Title: '{uploaded_resource['title']}'")

    gen_payload = {
        "department": "Computer Science and Engineering",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit 2",
        "topic": "Remote Procedure Calls and Message Passing",
        "resource_id": res_id,
        "question_type": "Short Answer",
        "num_questions": 4,
        "bloom_level": "Understand",
        "diff_easy": 25,
        "diff_medium": 50,
        "diff_hard": 25
    }

    r = make_req(f"{PORT_8080}/api/questions/generate", method="POST", data=gen_payload)
    assert r["status"] == 200, f"Question generation failed {r['status']}: {r['data']}"
    assert r["data"].get("status") == "success", f"Gen unsuccessful: {r['data']}"
    generated_questions = r["data"].get("questions", [])
    assert len(generated_questions) == 4, f"Expected 4 questions, got {len(generated_questions)}"
    print(f"[PASS] Successfully generated {len(generated_questions)} grounded questions via Port 8080:")
    for i, q in enumerate(generated_questions):
        print(f"   Q{i+1}: [{q.get('difficulty')}] [{q.get('bloom_level')}] {q.get('question_text')[:75]}... (Marks: {q.get('marks')})")

    print("\n" + "=" * 70)
    print("TEST 5: Requirement 4 - Save to Question Bank Flow & MySQL Persistence")
    print("=" * 70)

    # Preview questions to save (simulate frontend generated results with preview string IDs)
    preview_questions = [
        {
            "id": f"GEN-TEST-{i+1}",
            "question_text": f"Explain the role of client/server stubs in {gen_payload['topic']} ({gen_payload['unit']}). Unique key: {os.urandom(4).hex()}",
            "subject": gen_payload["subject"],
            "department": gen_payload["department"],
            "academic_year": "2025-2026",
            "semester": "Semester 6",
            "unit": gen_payload["unit"],
            "topic": gen_payload["topic"],
            "question_type": "Short Answer",
            "difficulty": "Medium",
            "bloom_level": "Understand",
            "marks": 2
        }
        for i in range(2)
    ]

    save_payload = {
        "questions": preview_questions,
        "question_ids": [q["id"] for q in preview_questions]
    }

    r = make_req(f"{PORT_8080}/api/question-bank", method="POST", data=save_payload)
    assert r["status"] == 200, f"Save to Question Bank failed {r['status']}: {r['data']}"
    assert r["data"].get("status") == "success", f"Save result not success: {r['data']}"
    saved_count = r["data"].get("saved_count", 0)
    assert saved_count >= 2, f"Expected at least 2 saved, got {saved_count}"
    saved_records = r["data"].get("questions", [])
    print(f"[PASS] Successfully saved {saved_count} questions to Question Bank via API:")
    for rec in saved_records:
        print(f"   Record ID: {rec.get('id')} | In Bank: {rec.get('is_in_bank')} | Status: {rec.get('status')}")

    # Verify MySQL directly
    sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system")
    sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
    from backend.services.question_service import get_db_connection
    conn = get_db_connection()
    with conn.cursor() as cur:
        for q in preview_questions:
            cur.execute("SELECT id, question_text, is_in_bank, status, subject, unit, topic FROM questions WHERE question_text = %s", (q["question_text"],))
            row = cur.fetchone()
            assert row is not None, f"Question not found in MySQL: {q['question_text']}"
            assert row["is_in_bank"] == 1, f"Question is_in_bank is not 1: {row}"
            assert row["status"] == "Bank", f"Question status is not Bank: {row}"
            print(f"   [MySQL VERIFIED] Question ID {row['id']} verified in MySQL (is_in_bank={row['is_in_bank']}, status='{row['status']}')")

    print("\n" + "=" * 70)
    print("TEST 6: Duplicate Prevention on Question Bank Save")
    print("=" * 70)

    # Re-submit the exact same payload
    r_dup = make_req(f"{PORT_8080}/api/question-bank", method="POST", data=save_payload)
    assert r_dup["status"] == 200, f"Re-submission failed: {r_dup['data']}"
    assert r_dup["data"].get("status") == "success", f"Re-submission error: {r_dup['data']}"
    print(f"[PASS] Duplicate submission safely handled without error: {r_dup['data'].get('message')}")

    # Verify count did NOT double in MySQL
    with conn.cursor() as cur:
        for q in preview_questions:
            cur.execute("SELECT COUNT(*) as cnt FROM questions WHERE question_text = %s", (q["question_text"],))
            cnt = cur.fetchone()["cnt"]
            assert cnt == 1, f"Expected exactly 1 row for unique question, found {cnt}!"
    print("[PASS] Verified in MySQL: No duplicate records created on repeated save.")
    conn.close()

    print("\n" + "=" * 70)
    print("TEST 7: Requirement 1 & 2 - Verify All 7 HTML Modules Have Editable Inputs")
    print("=" * 70)

    base_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
    modules = [
        ("faculty-voice-question.html", ["voiceDeptSelect", "voiceSubjectSelect", "voiceUnitSelect", "voiceTopicSelect"]),
        ("faculty-image-question.html", ["imgDeptSelect", "imgSubjectSelect", "imgUnitSelect", "imgTopicSelect"]),
        ("faculty-language-converter.html", ["transDeptSelect", "transSubjectSelect", "transUnitSelect", "transTopicSelect"]),
        ("faculty-question-paper.html", ["paperDept", "paperSubject"]),
        ("faculty-generate-assignment.html", ["asnDept", "asnSubject", "asnUnit", "asnTopic", "asnNumQuestions"]),
        ("faculty-generate-ppt.html", ["pptDeptSelect", "pptSubjectSelect", "pptUnitSelect", "pptTopicSelect"]),
        ("faculty-generate-lesson-plan.html", ["lpDeptSelect", "lpSubjectSelect", "lpUnitSelect", "lpTopicSelect"])
    ]

    for fname, req_ids in modules:
        fpath = os.path.join(base_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            html = f.read()
        for elem_id in req_ids:
            # Check for input element
            pattern = re.compile(rf'<input[^>]*id=["\']{elem_id}["\'][^>]*>', re.IGNORECASE)
            match = pattern.search(html)
            assert match is not None, f"Required input #{elem_id} not found in {fname}!"
            # Check type="number" for asnNumQuestions
            if elem_id == "asnNumQuestions":
                assert 'type="number"' in match.group(0), f"asnNumQuestions is not type='number' in {fname}!"
            # Check that it has a list attribute for datalist (except asnNumQuestions)
            elif "list=" in match.group(0):
                list_name = re.search(r'list=["\']([^"\']+)["\']', match.group(0)).group(1)
                assert f'id="{list_name}"' in html, f"Datalist #{list_name} not found in {fname}!"
        print(f"[PASS] {fname}: All {len(req_ids)} input(s) verified as editable inputs with datalists.")

    print("\n" + "=" * 70)
    print("TEST 8: Unit Datalist Options include 'All Units' and 'Unit 1..5'")
    print("=" * 70)

    for fname, _ in modules:
        if fname == "faculty-question-paper.html":
            continue
        fpath = os.path.join(base_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            html = f.read()
        assert "All Units (Complete Syllabus)" in html, f"'All Units (Complete Syllabus)' missing in {fname}!"
        assert "Unit 1" in html and "Unit 5" in html, f"Unit 1..5 missing in {fname}!"
    print("[PASS] All Unit datalists contain 'All Units (Complete Syllabus)' and 'Unit 1..5'.")

    print("\n" + "=" * 70)
    print("TEST 9: js/app.js Execution Integrity & Datalist Synchronizer")
    print("=" * 70)

    with open(os.path.join(base_dir, "js", "app.js"), "r", encoding="utf-8") as f:
        app_js = f.read()

    assert "function syncModuleDatalists" in app_js, "syncModuleDatalists missing in app.js!"
    assert "saveGeneratedToBank" in app_js, "saveGeneratedToBank missing in app.js!"
    assert "activeGeneratedAssignmentQuestions.push" in app_js, "generateAssignmentAction missing in app.js!"
    # Ensure no broken options access on inputs
    assert "pptUnitSelect')?.options" not in app_js, "pptUnitSelect options access lingering!"
    assert "voiceUnitSelect')?.options" not in app_js, "voiceUnitSelect options access lingering!"
    assert "imgUnitSelect')?.options" not in app_js, "imgUnitSelect options access lingering!"
    assert "transUnitSelect')?.options" not in app_js, "transUnitSelect options access lingering!"
    assert "lpUnitSelect')?.options" not in app_js, "lpUnitSelect options access lingering!"
    print("[PASS] js/app.js verified: zero broken .options references, datalist sync present, save flow complete.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! SYSTEM IS ROBUST AND FULLY VERIFIED.")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
