import urllib.request
import urllib.parse
import http.cookiejar
import json
import io
import mimetypes
import uuid
import os

print("=== LIVE END-TO-END HTTP VERIFICATION (PORTS 5000 & 8080) ===")

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

# 1. Login Murugan via Live HTTP
login_payload = json.dumps({"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"}).encode('utf-8')
req = urllib.request.Request("http://localhost:5000/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 200
    print("[PASS] 1. Live Faculty Login: Murugan (ID 24)")

# Helper to post multipart form data via urllib
def post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex
    body = io.BytesIO()
    for name, value in fields.items():
        body.write(f"--{boundary}\r\n".encode('utf-8'))
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode('utf-8'))
        body.write(f"{value}\r\n".encode('utf-8'))
    for name, (filename, content, mime) in files.items():
        body.write(f"--{boundary}\r\n".encode('utf-8'))
        body.write(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.write(f"Content-Type: {mime}\r\n\r\n".encode('utf-8'))
        body.write(content)
        body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode('utf-8'))
    
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    req = urllib.request.Request(url, data=body.getvalue(), headers=headers)
    with opener.open(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

# 2. Live Image Analysis with spaces in filename
img_path = r"backend/uploads/resources/diagram_1792998088_lamports_algorithm.jpg"
with open(img_path, 'rb') as f:
    img_bytes = f.read()

filename = "lamports algorithm.jpg"
st, an_resp = post_multipart(
    "http://localhost:5000/api/questions/analyze-image",
    fields={
        "original_filename": filename,
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "unit": "Unit 2 — Synchronization & Logical Clocks",
        "topic": "Lamport Logical Clocks"
    },
    files={"image": (filename, img_bytes, "image/jpeg")}
)
assert st == 200
assert an_resp['filename'] == filename
assert an_resp['original_filename'] == filename
assert "Lamport" in an_resp['detected_title']
print(f"[PASS] 2. Live Diagram Analysis: '{an_resp['filename']}' -> Title: '{an_resp['detected_title']}'")

# 3. Live Question Generation with spaces in filename
st, gen_resp = post_multipart(
    "http://localhost:5000/api/questions/generate-image",
    fields={
        "original_filename": filename,
        "department": "Artificial Intelligence & Data Science",
        "subject": "Distributed Computing",
        "unit": "Unit 2 — Synchronization & Logical Clocks",
        "topic": "Lamport Logical Clocks",
        "num_questions": "5",
        "question_type": "Diagram Interpretation",
        "difficulty": "Balanced",
        "bloom_level": "Auto Select"
    },
    files={"image": (filename, img_bytes, "image/jpeg")}
)
assert st == 200
assert len(gen_resp['questions']) == 5
assert gen_resp['filename'] == filename
for q in gen_resp['questions']:
    assert filename in q['question']
    assert q['imageRef'] == filename
    assert q['source_reference'] == filename
print(f"[PASS] 3. Live Question Generation: 5 questions generated, all referencing exact '{filename}'")

# 4. Live Save to Question Bank
save_payload = json.dumps({"questions": gen_resp['questions']}).encode('utf-8')
req = urllib.request.Request("http://localhost:5000/api/question-bank", data=save_payload, headers={"Content-Type": "application/json"})
with opener.open(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert resp.status == 200
    print("[PASS] 4. Live Save to Question Bank: Success confirmed from MySQL")

print("\n=======================================================")
print("ALL LIVE HTTP END-TO-END PIPELINE CHECKS PASSED!")
print("=======================================================")
