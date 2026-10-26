"""
Academic Question Generation and Difficulty Balancing System
End-to-End Test for AI Question Generator, Resource Proxy & Uploads
"""

import urllib.request
import urllib.error
import http.cookiejar
import json
import os
import io
import mimetypes

COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))

PORT_8080 = "http://127.0.0.1:8080"
PORT_5000 = "http://127.0.0.1:5000"


def make_request(url, method="GET", data=None, headers=None):
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
        with OPENER.open(req, timeout=120) as resp:
            resp_body = resp.read().decode("utf-8")
            is_json = resp.headers.get_content_type() == "application/json" or resp_body.strip().startswith("{")
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
    print("  RUNNING E2E TESTS: AI QUESTION GENERATOR, PROXY & UPLOADS")
    print("=" * 70)

    # 1. Health checks on both ports
    print("[1/6] Checking health endpoints...")
    h8080 = make_request(f"{PORT_8080}/api/health")
    assert h8080["status"] == 200, f"8080 health failed: {h8080}"
    assert h8080["is_json"], "8080 health must return JSON"
    print(f"      PASS: Port 8080 /api/health proxied -> {h8080['data']['status']}")

    h5000 = make_request(f"{PORT_5000}/api/health")
    assert h5000["status"] == 200, f"5000 health failed: {h5000}"
    print(f"      PASS: Port 5000 /api/health direct  -> {h5000['data']['status']}")

    # 2. Login as faculty through port 8080 proxy
    print("\n[2/6] Logging in as faculty (muruga@vsb.com) through port 8080 proxy...")
    login_resp = make_request(f"{PORT_8080}/api/auth/login", method="POST", data={
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_resp["status"] == 200, f"Login failed: {login_resp}"
    assert login_resp["data"]["status"] == "success", f"Login response: {login_resp}"
    faculty_user = login_resp["data"]["user"]
    print(f"      PASS: Faculty logged in! Name: {faculty_user.get('full_name')}, Role: {faculty_user.get('role')}")

    # 3. GET /api/resources through port 8080 (verifying NO 404 HTML!)
    print("\n[3/6] Testing GET /api/resources via port 8080 proxy...")
    res_resp = make_request(f"{PORT_8080}/api/resources")
    assert res_resp["status"] == 200, f"GET /api/resources failed: {res_resp}"
    assert res_resp["is_json"], "Response must be valid JSON, not HTML!"
    existing_resources = res_resp["data"].get("resources", [])
    print(f"      PASS: Found {len(existing_resources)} existing resources. Response is valid JSON!")

    # 4. Quick-upload a study material file (TXT notes) through port 8080 proxy
    print("\n[4/6] Testing Quick Upload (multipart/form-data) via port 8080 proxy...")
    sample_notes = """
    UNIT I: CLOUD COMPUTING FUNDAMENTALS
    Cloud computing is a distributed computing paradigm that delivers on-demand computing services over the internet.
    Key characteristics include on-demand self-service, broad network access, resource pooling, rapid elasticity, and measured service.
    Service models: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), Software as a Service (SaaS).
    Deployment models: Public cloud, Private cloud, Hybrid cloud, and Community cloud.

    UNIT II: VIRTUALIZATION AND HYPERVISORS
    Virtualization creates simulated environments from physical hardware.
    Type 1 Hypervisors run directly on bare metal (e.g. VMware ESXi, KVM).
    Type 2 Hypervisors run as a software layer on top of a host OS (e.g. VirtualBox, VMware Workstation).
    Memory ballooning and live migration optimize virtual resource allocation.
    """
    fields = {
        "subject": "Cloud Computing",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I - Cloud Computing Fundamentals",
        "topic": "Cloud Service Models and Virtualization",
        "resource_type": "Study Material",
        "description": "Quick upload test notes for AI Question Generator"
    }
    files = {
        "file": ("Cloud_Computing_Notes.txt", sample_notes.encode("utf-8"))
    }
    body, ct = encode_multipart_formdata(fields, files)
    upload_resp = make_request(f"{PORT_8080}/api/resources", method="POST", data=body, headers={"Content-Type": ct})
    assert upload_resp["status"] == 201, f"Quick upload failed: {upload_resp}"
    assert upload_resp["is_json"], "Upload response must be JSON"
    uploaded_resource = upload_resp["data"]["resource"]
    res_id = uploaded_resource["id"]
    print(f"      PASS: Quick upload successful! Resource ID: {res_id}, Title: {uploaded_resource['title']}")

    # 5. POST /api/questions/generate with the uploaded resource via port 8080 proxy
    print("\n[5/6] Testing POST /api/questions/generate via port 8080 proxy...")
    gen_payload = {
        "department": "Artificial Intelligence & Data Science",
        "subject": "Cloud Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I - Cloud Computing Fundamentals",
        "topic": "Cloud Service Models and Virtualization",
        "num_questions": 8,
        "question_type": "Short Answer",
        "bloom_level": "Auto Select",
        "diff_easy": 30,
        "diff_medium": 50,
        "diff_hard": 20,
        "resource_id": res_id,
        "use_question_bank": False
    }
    gen_resp = make_request(f"{PORT_8080}/api/questions/generate", method="POST", data=gen_payload)
    assert gen_resp["status"] == 200, f"Question generation failed: {gen_resp}"
    assert gen_resp["is_json"], "Question generation response must be valid JSON!"
    questions = gen_resp["data"].get("questions", [])
    assert len(questions) == 8, f"Expected 8 questions, got {len(questions)}"
    print(f"      PASS: Successfully generated {len(questions)} grounded questions via port 8080 proxy!")
    for idx, q in enumerate(questions[:3], 1):
        print(f"        Q{idx} [{q['marks']}M | {q['difficulty']} | Bloom: {q['bloom_level']}]: {q['question_text']}")

    # 6. POST /api/quizzes/generate via port 8080 proxy
    print("\n[6/6] Testing POST /api/quizzes/generate via port 8080 proxy...")
    quiz_payload = {
        "title": "Cloud Computing Assessment Quiz",
        "department": "Artificial Intelligence & Data Science",
        "subject": "Cloud Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I - Cloud Computing Fundamentals",
        "topic": "Cloud Service Models and Virtualization",
        "duration_minutes": 30,
        "marks_per_question": 1,
        "total_questions": 10
    }
    quiz_resp = make_request(f"{PORT_8080}/api/quizzes/generate", method="POST", data=quiz_payload)
    assert quiz_resp["status"] == 200, f"Quiz generation failed: {quiz_resp}"
    assert quiz_resp["is_json"], "Quiz generation response must be valid JSON!"
    quiz_questions = quiz_resp["data"].get("questions", [])
    assert len(quiz_questions) == 10, f"Expected 10 quiz questions, got {len(quiz_questions)}"
    print(f"      PASS: Successfully generated {len(quiz_questions)} quiz questions via port 8080 proxy!")

    print("\n" + "=" * 70)
    print("  ALL 6 E2E VERIFICATION CHECKS PASSED WITH FLYING COLORS!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
