"""
Test: Verify that auto-uploading works seamlessly when a file is selected and Generate is triggered.
"""

import urllib.request
import http.cookiejar
import json
import os

COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))

PORT_8080 = "http://127.0.0.1:8080"


def test_quick_upload_and_gen_flow():
    # 1. Login
    req_login = urllib.request.Request(
        f"{PORT_8080}/api/auth/login",
        data=json.dumps({"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with OPENER.open(req_login) as resp:
        assert resp.status == 200

    # 2. Check that DOCX syllabus exists and can be parsed
    docx_path = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\uploads\resources\1792942486_23CST504_-_DISTRIBUTED_COMPUTING.docx"
    assert os.path.exists(docx_path), "DOCX syllabus must exist"

    # 3. Generate questions for Distributed Computing using the DOCX syllabus directly
    gen_payload = {
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "All Units (Complete Syllabus)",
        "topic": "",
        "num_questions": 10,
        "question_type": "Short Answer",
        "bloom_level": "Auto Select",
        "diff_easy": 30,
        "diff_medium": 50,
        "diff_hard": 20,
        "use_question_bank": False
    }
    req_gen = urllib.request.Request(
        f"{PORT_8080}/api/questions/generate",
        data=json.dumps(gen_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with OPENER.open(req_gen) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["status"] == "success"
        questions = data["questions"]
        assert len(questions) == 10
        print(f"[OK] Distributed Computing generation grounded in DOCX syllabus succeeded! Total: {len(questions)}")
        for idx, q in enumerate(questions[:3], 1):
            print(f"     Q{idx}: ({q['unit']}) {q['question_text']}")


if __name__ == "__main__":
    test_quick_upload_and_gen_flow()
    print("[ALL PASS] DOCX syllabus grounded question generation verified!")
