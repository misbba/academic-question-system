"""
Test Question Bank save flow directly against active server
"""
import urllib.request
import json
import http.cookiejar

COOKIE_JAR = http.cookiejar.CookieJar()
OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(COOKIE_JAR))

def test_save_to_qb():
    # Login as Murugan
    req = urllib.request.Request(
        "http://127.0.0.1:8080/api/auth/login",
        data=json.dumps({"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with OPENER.open(req) as resp:
        assert resp.status == 200

    # Simulate sending question objects
    sample_q = [{
        "id": "GEN-Q-1",
        "question_text": "What is the primary role of RPC in distributed systems?",
        "subject": "Distributed Computing",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I - Introduction",
        "topic": "RPC",
        "question_type": "Short Answer",
        "difficulty": "Easy",
        "bloom_level": "Remember",
        "marks": 2
    }]

    # Test what current backend does when passed questions: sample_q
    req_save = urllib.request.Request(
        "http://127.0.0.1:8080/api/question-bank",
        data=json.dumps({"questions": sample_q, "question_ids": ["GEN-Q-1"]}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with OPENER.open(req_save) as resp:
            data = json.loads(resp.read().decode())
            print("Save Response:", data)
    except urllib.error.HTTPError as e:
        print("Save HTTP Error:", e.code, e.read().decode())

if __name__ == "__main__":
    test_save_to_qb()
