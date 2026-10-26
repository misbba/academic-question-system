import sys
import os
import io
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from app import app
from models.database import get_db_connection

def test_flask_image_pipeline():
    client = app.test_client()

    print("\n--- Test 1: Health Endpoint ---")
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print("[PASS] Health endpoint returned 200 OK:", res.get_json())

    print("\n--- Test 2: Unauthenticated Access ---")
    res = client.post('/api/questions/generate-image')
    assert res.status_code == 401, f"Expected 401 unauth, got {res.status_code}"
    res_an = client.post('/api/questions/analyze-image')
    assert res_an.status_code == 401, f"Expected 401 unauth on analyze, got {res_an.status_code}"
    print("[PASS] Unauthenticated access properly rejected with 401 on both endpoints")

    print("\n--- Test 3: Faculty Login (Murugan) ---")
    login_res = client.post('/api/auth/login', json={
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.status_code} {login_res.get_json()}"
    user = login_res.get_json().get('user')
    print(f"[PASS] Successfully logged in as: {user['full_name']} (ID: {user['id']}, Role: {user['role']})")

    # Generate sample test image for FUTURE.png
    img = Image.new('RGB', (600, 400), color=(250, 250, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 220, 160], outline=(30, 60, 180), width=3)
    draw.text((60, 90), "User Interface", fill=(30, 60, 180))
    draw.line([(220, 105), (320, 105)], fill=(50, 50, 50), width=2)
    draw.rectangle([320, 50, 550, 160], outline=(180, 50, 30), width=3)
    draw.text((330, 90), "Database Cluster", fill=(180, 50, 30))

    print("\n--- Test 4: Analyze Diagram Image (Analyze Image Context) ---")
    img_io1 = io.BytesIO()
    img.save(img_io1, format='PNG')
    img_io1.seek(0)

    an_data = {
        'image': (img_io1, 'FUTURE.png'),
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Database Management Systems',
        'unit': 'Unit 1',
        'topic': 'ER Diagram Relationships'
    }

    an_res = client.post(
        '/api/questions/analyze-image',
        data=an_data,
        content_type='multipart/form-data'
    )
    assert an_res.status_code == 200, f"Analyze failed: {an_res.status_code} {an_res.get_json()}"
    an_json = an_res.get_json()
    assert an_json.get('status') == 'success'
    assert an_json.get('metadata', {}).get('width') == 600
    assert an_json.get('metadata', {}).get('height') == 400
    assert an_json.get('metadata', {}).get('format') == 'PNG'
    print(f"[PASS] Diagram analyzed genuinely: {an_json['metadata']}")
    print(f"       Suggested description: {an_json.get('suggested_description')}")

    print("\n--- Test 5: Generate Questions from Diagram Image ---")
    img_io2 = io.BytesIO()
    img.save(img_io2, format='PNG')
    img_io2.seek(0)

    gen_data = {
        'image': (img_io2, 'FUTURE.png'),
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Database Management Systems',
        'unit': 'Unit 1',
        'topic': 'ER Diagram Relationships',
        'num_questions': '5',
        'question_type': 'Diagram Interpretation',
        'difficulty': 'Balanced',
        'bloom_level': 'Analyze',
        'description': an_json.get('suggested_description')
    }

    gen_res = client.post(
        '/api/questions/generate-image',
        data=gen_data,
        content_type='multipart/form-data'
    )
    assert gen_res.status_code == 200, f"Generation failed: {gen_res.status_code} {gen_res.get_json()}"
    gen_json = gen_res.get_json()
    assert gen_json.get('status') == 'success'
    questions = gen_json.get('questions', [])
    assert len(questions) == 5, f"Expected 5 questions, got {len(questions)}"
    print(f"[PASS] Successfully generated {len(questions)} grounded questions from FUTURE.png:")
    for q in questions:
        print(f"  - Q{q['num']}: ({q['difficulty']} | {q['bloom_level']}) {q['question']}")
        assert 'FUTURE.png' in q['question'] or 'FUTURE.png' in q['imageRef']

    print("\n--- Test 6: Verify Saved Diagram File on Disk ---")
    saved_filename = gen_json.get('saved_filename')
    assert saved_filename, "No saved_filename returned"
    upload_path = os.path.abspath(os.path.join(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\uploads\resources", saved_filename))
    assert os.path.exists(upload_path), f"File was not saved to {upload_path}"
    print(f"[PASS] Diagram image exists on disk: {upload_path} ({os.path.getsize(upload_path)} bytes)")

    print("\n--- Test 7: Verify Download / View Route for Diagram ---")
    dl_res = client.get(f"/api/resources/file/{saved_filename}")
    assert dl_res.status_code == 200, f"Expected 200 on download, got {dl_res.status_code}"
    print(f"[PASS] Diagram file download/view route returned 200 OK")

    print("\n--- Test 8: Verify /api/questions/generate with Multipart Image ---")
    img_io3 = io.BytesIO()
    img.save(img_io3, format='PNG')
    img_io3.seek(0)
    data3 = {
        'file': (img_io3, 'FUTURE.png'),
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Database Management Systems',
        'unit': 'Unit 2',
        'topic': 'Fault Tolerance',
        'num_questions': '3',
        'question_type': 'Diagram Interpretation',
        'difficulty': 'Medium',
        'bloom_level': 'Apply',
        'description': 'Fault recovery architecture diagram'
    }
    gen3_res = client.post(
        '/api/questions/generate',
        data=data3,
        content_type='multipart/form-data'
    )
    assert gen3_res.status_code == 200, f"Failed on /api/questions/generate: {gen3_res.status_code}"
    assert len(gen3_res.get_json().get('questions', [])) == 3
    print("[PASS] /api/questions/generate handled multipart diagram generation properly")

    print("\n--- Test 9: Negative Testing - Missing File ---")
    neg_res = client.post(
        '/api/questions/generate-image',
        data={'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res.status_code == 400, f"Expected 400 for missing file, got {neg_res.status_code}"
    neg_msg = neg_res.get_json().get('message')
    print(f"[PASS] Missing file rejected with 400: '{neg_msg}'")
    assert "Image Required: Please upload a diagram image first." in neg_msg

    print("\n--- Test 10: Negative Testing - Invalid File Extension ---")
    bad_file = (io.BytesIO(b"malicious script bytes"), "script.exe")
    neg_res2 = client.post(
        '/api/questions/generate-image',
        data={'image': bad_file, 'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res2.status_code == 400, f"Expected 400 for bad extension, got {neg_res2.status_code}"
    print(f"[PASS] Invalid extension rejected with 400: '{neg_res2.get_json().get('message')}'")

    print("\n--- Test 11: Negative Testing - Corrupt Image File ---")
    corrupt_file = (io.BytesIO(b"corrupted header bytes"), "corrupt.png")
    neg_res3 = client.post(
        '/api/questions/generate-image',
        data={'image': corrupt_file, 'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res3.status_code == 400, f"Expected 400 for corrupt file, got {neg_res3.status_code}"
    print(f"[PASS] Corrupt image rejected with 400: '{neg_res3.get_json().get('message')}'")

    print("\n--- Test 12: Save Generated Questions to MySQL Question Bank ---")
    batch_data = [{
        "question_text": q['question'],
        "subject": q['subject'],
        "department": q['department'],
        "unit": q['unit'],
        "topic": q['topic'],
        "marks": q['marks'],
        "difficulty": q['difficulty'],
        "question_type": q['type'],
        "bloom_level": q['bloom_level'],
        "concept": q['concept'],
        "image_ref": q['imageRef']
    } for q in questions]

    save_res = client.post(
        '/api/question-bank',
        json={'questions': batch_data, 'batch': batch_data}
    )
    assert save_res.status_code in (200, 201), f"Save to question bank failed: {save_res.status_code} {save_res.get_json()}"
    print(f"[PASS] Successfully saved {len(batch_data)} diagram questions to Question Bank in MySQL!")

    # Verify questions exist in DB for Murugan
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, question_text, concept, created_by FROM questions WHERE question_text LIKE %s AND created_by = %s", ('%FUTURE.png%', user['id']))
        rows = cur.fetchall()
        assert len(rows) >= 5, f"Expected >= 5 rows in questions table for Murugan, got {len(rows)}"
        print(f"[PASS] Verified {len(rows)} questions found in MySQL database for faculty ID {user['id']}")
    conn.close()

    print("\n" + "="*70)
    print("ALL 12 BACKEND & SERVICE TESTS COMPLETED AND PASSED WITH 100% SUCCESS!")
    print("="*70)

if __name__ == '__main__':
    test_flask_image_pipeline()
