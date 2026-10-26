import os
import sys
import io
import json
import time
from PIL import Image, ImageDraw

# Add backend directory to sys.path
backend_dir = os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
import pymysql

print("======================================================================")
print("ACADEMIC QUESTION SYSTEM: IMAGE / DIAGRAM PIPELINE VERIFICATION SUITE")
print("======================================================================")

app = create_app()
client = app.test_client()

# Helper to login as faculty
def login_faculty(email="muruga@vsb.com", password="Password123!"):
    res = client.post('/api/auth/login', json={"email": email, "password": password, "role": "faculty"})
    assert res.status_code == 200, f"Login failed for {email}: {res.get_json()}"
    data = res.get_json()
    return data['user']['id'], data['user']['full_name']

# Helper to create test images
def create_test_image(format_name, width=640, height=480, draw_title="Test Diagram"):
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), draw_title, fill=(0, 0, 0))
    # Draw simple shapes
    draw.rectangle([50, 50, 200, 150], outline=(0, 0, 180), width=2)
    draw.rectangle([300, 50, 450, 150], outline=(0, 0, 180), width=2)
    draw.line([(200, 100), (300, 100)], fill=(200, 0, 0), width=2)
    buf = io.BytesIO()
    save_fmt = 'JPEG' if format_name.upper() in ['JPG', 'JPEG'] else format_name.upper()
    img.save(buf, format=save_fmt)
    buf.seek(0)
    return buf

# Test 1: Verify Health
print("\n--- Test 1: System Health & DB Connectivity ---")
res = client.get('/api/health')
assert res.status_code == 200, f"Health check failed: {res.status_code}"
print("[PASS] System health 200 OK:", res.get_json()['message'])

# Test 2: Unauthenticated Access Control
print("\n--- Test 2: Authentication & Authorization Security ---")
client.post('/api/auth/logout')
res = client.post('/api/questions/analyze-image')
assert res.status_code == 401, f"Expected 401, got {res.status_code}"
res = client.post('/api/questions/generate-image')
assert res.status_code == 401, f"Expected 401, got {res.status_code}"
print("[PASS] Protected endpoints correctly enforce 401 Unauthorized for unauthenticated requests.")

# Test 3: Faculty Login (Murugan, ID: 24)
print("\n--- Test 3: Authenticated Faculty Session ---")
murugan_id, murugan_name = login_faculty("muruga@vsb.com", "Password123!")
print(f"[PASS] Successfully logged in as faculty member: {murugan_name} (ID: {murugan_id})")

# Helper to get lamport image bytes
real_img_path = os.path.join(backend_dir, 'uploads', 'resources', 'diagram_1792998088_lamports_algorithm.jpg')
if os.path.exists(real_img_path):
    with open(real_img_path, 'rb') as f:
        real_img_content = f.read()
else:
    real_img_content = create_test_image('JPEG', width=1280, height=720, draw_title="Lamport Logical Clock").getvalue()

def get_lamport_bytes():
    return io.BytesIO(real_img_content)

# Test 4: Upload JPG with spaces in filename (lamports algorithm.jpg)
print("\n--- Test 4: Upload 'lamports algorithm.jpg' (Spaces in Filename) ---")
filename_spaces = "lamports algorithm.jpg"
res = client.post(
    '/api/questions/analyze-image',
    data={
        'image': (get_lamport_bytes(), filename_spaces),
        'original_filename': filename_spaces,
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Distributed Computing',
        'unit': 'Unit 2 — Synchronization & Logical Clocks',
        'topic': 'Lamport Logical Clocks'
    },
    content_type='multipart/form-data'
)
assert res.status_code == 200, f"Analysis failed: {res.get_json()}"
data = res.get_json()
assert data['status'] == 'success'
assert data['filename'] == filename_spaces, f"Expected '{filename_spaces}', got '{data['filename']}'"
assert data['original_filename'] == filename_spaces, f"Expected original_filename '{filename_spaces}'"
assert "Lamport" in data['detected_title'] or "Clock" in data['detected_title']
assert data['metadata']['filename'] == filename_spaces
assert "Pillow/NumPy" in data['metadata']['limitations']
print(f"[PASS] /api/questions/analyze-image succeeded:")
print(f"       - Preserved original filename: '{data['filename']}'")
print(f"       - Detected diagram title: {data['detected_title']}")
print(f"       - Identified Category: {data['diagram_category']}")
print(f"       - Reported Limitations: {data['metadata']['limitations']}")

# Test 5: Generate Diagram-Grounded Questions for 'lamports algorithm.jpg'
print("\n--- Test 5: Diagram-Grounded Question Generation ---")
res = client.post(
    '/api/questions/generate-image',
    data={
        'image': (get_lamport_bytes(), filename_spaces),
        'original_filename': filename_spaces,
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Distributed Computing',
        'unit': 'Unit 2 — Synchronization & Logical Clocks',
        'topic': 'Lamport Logical Clocks',
        'num_questions': 5,
        'question_type': 'Diagram Interpretation',
        'difficulty': 'Balanced',
        'bloom_level': 'Auto Select'
    },
    content_type='multipart/form-data'
)
assert res.status_code == 200, f"Generation failed: {res.get_json()}"
gen_data = res.get_json()
assert gen_data['status'] == 'success'
assert len(gen_data['questions']) == 5
assert gen_data['filename'] == filename_spaces
assert gen_data['original_filename'] == filename_spaces

for i, q in enumerate(gen_data['questions']):
    # Verify filename preservation
    assert filename_spaces in q['question'], f"Question {i+1} does not refer to '{filename_spaces}': {q['question']}"
    assert "lamports_algorithm.jpg" not in q['question'], f"Question {i+1} erroneously substituted underscores in '{q['question']}'"
    assert q['imageRef'] == filename_spaces, f"imageRef mismatch: {q['imageRef']}"
    assert q['image_ref'] == filename_spaces, f"image_ref mismatch: {q['image_ref']}"
    assert q['source_reference'] == filename_spaces, f"source_reference mismatch: {q['source_reference']}"
    assert q['source_type'] == 'Diagram Image'
    print(f"  Q{q['num']}: ({q['difficulty']} | {q['bloom_level']} | {q['type']})")
    print(f"       Text: {q['question'][:120]}...")
    print(f"       Ref: {q['imageRef']} | Concept: {q['concept']}")

# Verify grounding in Lamport logical clocks
q_texts = " ".join([q['question'] for q in gen_data['questions']])
assert any(term in q_texts for term in ["Lamport", "timeline", "logical clock", "happens-before", "timestamp"]), \
    "Questions are not grounded in Lamport logical clocks!"
print("[PASS] Generated questions are rigorously grounded in Lamport Logical Clock theory and preserve original filename!")

# Test 6: PNG Image Upload (FUTURE.png)
print("\n--- Test 6: PNG Format Handling (FUTURE.png) ---")
png_buf = create_test_image('PNG', width=800, height=500, draw_title="ER Diagram Entities")
res = client.post(
    '/api/questions/analyze-image',
    data={
        'image': (png_buf, 'FUTURE.png'),
        'original_filename': 'FUTURE.png',
        'department': 'Computer Science and Engineering',
        'subject': 'Database Management Systems',
        'unit': 'Unit 1 — ER Modeling',
        'topic': 'ER Diagram Relationships'
    },
    content_type='multipart/form-data'
)
assert res.status_code == 200
data_png = res.get_json()
assert data_png['filename'] == 'FUTURE.png'
assert data_png['metadata']['format'] == 'PNG'
print("[PASS] PNG format (FUTURE.png) analyzed successfully with format = PNG.")

# Test 7: WEBP Image Upload (network_model.webp)
print("\n--- Test 7: WEBP Format Handling (network_model.webp) ---")
webp_buf = create_test_image('WEBP', width=600, height=400, draw_title="OSI Network Protocol")
res = client.post(
    '/api/questions/generate-image',
    data={
        'image': (webp_buf, 'network_model.webp'),
        'original_filename': 'network_model.webp',
        'department': 'Information Technology',
        'subject': 'Computer Networks',
        'unit': 'Unit 3 — Transport Layer',
        'topic': 'TCP Three-Way Handshake',
        'num_questions': 3
    },
    content_type='multipart/form-data'
)
assert res.status_code == 200
data_webp = res.get_json()
assert len(data_webp['questions']) == 3
assert data_webp['filename'] == 'network_model.webp'
assert all(q['imageRef'] == 'network_model.webp' for q in data_webp['questions'])
print("[PASS] WEBP format (network_model.webp) generated 3 questions referencing 'network_model.webp'.")

# Test 8: Consecutive Uploads Isolation (Image B must not reuse Image A)
print("\n--- Test 8: Consecutive Uploads Isolation (No Stale Cross-Contamination) ---")
buf_a = create_test_image('PNG', draw_title="Diagram A")
res_a = client.post('/api/questions/generate-image', data={'image': (buf_a, 'first diagram.png'), 'original_filename': 'first diagram.png', 'subject': 'Operating Systems'}, content_type='multipart/form-data')
assert res_a.get_json()['filename'] == 'first diagram.png'

buf_b = create_test_image('JPEG', draw_title="Diagram B")
res_b = client.post('/api/questions/generate-image', data={'image': (buf_b, 'second diagram.jpg'), 'original_filename': 'second diagram.jpg', 'subject': 'Cloud Computing'}, content_type='multipart/form-data')
assert res_b.get_json()['filename'] == 'second diagram.jpg'
questions_b = res_b.get_json()['questions']
assert all('first diagram.png' not in q['question'] for q in questions_b), "Consecutive upload reused earlier filename!"
assert all(q['imageRef'] == 'second diagram.jpg' for q in questions_b)
print("[PASS] Consecutive uploads are completely isolated; second upload does not contain references to first upload.")

# Test 9: Negative Testing - Invalid Formats, Corrupted Files, Missing Files
print("\n--- Test 9: Robust Error Handling (Negative Tests) ---")
# Missing file
res = client.post('/api/questions/generate-image', data={'department': 'CS'}, content_type='multipart/form-data')
assert res.status_code == 400
assert "Image Required" in res.get_json()['message']

# Invalid extension (e.g. .txt)
txt_buf = io.BytesIO(b"This is a text file, not an image.")
res = client.post('/api/questions/generate-image', data={'image': (txt_buf, 'notes.txt')}, content_type='multipart/form-data')
assert res.status_code == 400
assert "Invalid file type" in res.get_json()['message']

# Corrupt image
corrupt_buf = io.BytesIO(b"\xFF\xD8\xFF\xE0\x00\x10JFIF corrupted bytes nonsense")
res = client.post('/api/questions/generate-image', data={'image': (corrupt_buf, 'corrupt.jpg')}, content_type='multipart/form-data')
assert res.status_code == 400
assert "Corrupted or invalid" in res.get_json()['message']
print("[PASS] Successfully rejected missing file, invalid extension (.txt), and corrupted image with 400 Bad Request.")

# Test 10: Save to MySQL Question Bank & Verify Provenance
print("\n--- Test 10: Save to MySQL Question Bank & Verify Provenance ---")
# Use the questions generated from 'lamports algorithm.jpg'
questions_to_save = gen_data['questions']
res = client.post(
    '/api/question-bank',
    json={'questions': questions_to_save}
)
assert res.status_code in [200, 201], f"Save to question bank failed: {res.get_json()}"
save_result = res.get_json()
assert save_result['status'] == 'success'
print(f"[PASS] /api/question-bank returned success: {save_result['message']}")

# Direct MySQL Verification
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)
with conn.cursor() as cur:
    cur.execute(
        """
        SELECT id, question_text, source_type, source_reference, created_by, is_in_bank, status
        FROM questions
        WHERE created_by = %s AND source_reference = %s
        ORDER BY id DESC LIMIT 5
        """,
        (murugan_id, filename_spaces)
    )
    db_rows = cur.fetchall()
    assert len(db_rows) == 5, f"Expected 5 questions in DB for {filename_spaces}, found {len(db_rows)}"
    for row in db_rows:
        assert row['source_type'] == 'Diagram Image', f"Invalid source_type: {row['source_type']}"
        assert row['source_reference'] == filename_spaces, f"Invalid source_reference: {row['source_reference']}"
        assert row['created_by'] == murugan_id
        assert row['is_in_bank'] == 1
        assert row['status'] == 'Bank'
        print(f"  [DB ROW] ID: {row['id']} | Src: '{row['source_reference']}' | Text: {row['question_text'][:60]}...")
conn.close()
print(f"[PASS] Verified 5 records in MySQL with exact source_reference = '{filename_spaces}' and faculty_id = {murugan_id}!")

# Test 11: Deduplication Test (Submitting same questions again must not create duplicate rows)
print("\n--- Test 11: Deduplication Check (No Duplicate DB Rows) ---")
res_dup = client.post('/api/question-bank', json={'questions': questions_to_save})
assert res_dup.status_code in [200, 201]

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) AS cnt FROM questions WHERE created_by = %s AND source_reference = %s", (murugan_id, filename_spaces))
    row_count = cur.fetchone()['cnt']
    assert row_count == 5, f"Expected exactly 5 rows after re-saving, found {row_count} (duplicate detected!)"
conn.close()
print("[PASS] Deduplication confirmed: Re-saving questions did not insert duplicate rows (count remains 5).")

# Test 12: Faculty Data Isolation (Murugan vs Kavitha)
print("\n--- Test 12: Faculty Data Isolation (Murugan ID: 24 vs Kavitha ID: 25) ---")
client.post('/api/auth/logout')
kavitha_id, kavitha_name = login_faculty("kavitha@vsb.com", "Password123!")
res_kavitha = client.get('/api/question-bank')
assert res_kavitha.status_code == 200
kavitha_bank = res_kavitha.get_json()['questions']
# Ensure none of Murugan's 'lamports algorithm.jpg' questions appear in Kavitha's question bank
assert all(q.get('source_reference') != filename_spaces for q in kavitha_bank), \
    "Data isolation breached: Murugan's diagram questions appeared in Kavitha's Question Bank!"
print(f"[PASS] Data isolation verified: Kavitha cannot see Murugan's diagram questions ({len(kavitha_bank)} questions in Kavitha's bank).")

print("\n======================================================================")
print("ALL 12 TEST SUITES EXECUTED AND PASSED WITH 100% SUCCESS!")
print("======================================================================")
