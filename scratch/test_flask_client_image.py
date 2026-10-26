import sys
import os
import io
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.abspath(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"))

from app import app
from models.database import get_db_connection

def test_flask_image_flow():
    client = app.test_client()

    print("\n--- Test 1: Health Endpoint ---")
    res = client.get('/api/health')
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    print("[PASS] Health endpoint returned 200 OK:", res.get_json())

    print("\n--- Test 2: Unauthenticated Access ---")
    res = client.post('/api/questions/generate-image')
    assert res.status_code == 401, f"Expected 401 unauth, got {res.status_code}"
    print("[PASS] Unauthenticated access properly rejected with 401")

    print("\n--- Test 3: Faculty Login (Murugan) ---")
    login_res = client.post('/api/auth/login', json={
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.status_code} {login_res.get_json()}"
    user = login_res.get_json().get('user')
    print(f"[PASS] Successfully logged in as: {user['full_name']} (ID: {user['id']}, Role: {user['role']})")

    print("\n--- Test 4: Upload FUTURE.png and Generate Questions ---")
    img = Image.new('RGB', (500, 350), color=(245, 245, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([60, 60, 200, 160], outline=(20, 40, 160), width=3)
    draw.text((70, 100), "Microservice A", fill=(20, 40, 160))
    draw.line([(200, 110), (300, 110)], fill=(0, 0, 0), width=2)
    draw.rectangle([300, 60, 440, 160], outline=(160, 40, 20), width=3)
    draw.text((310, 100), "Microservice B", fill=(160, 40, 20))

    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)

    data = {
        'image': (img_io, 'FUTURE.png'),
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Database Management Systems',
        'unit': 'Unit 1',
        'topic': 'ER Diagram Relationships',
        'num_questions': '5',
        'question_type': 'Diagram Interpretation',
        'difficulty': 'Balanced',
        'bloom_level': 'Analyze',
        'description': 'Architecture diagram illustrating inter-service communication and load distribution'
    }

    gen_res = client.post(
        '/api/questions/generate-image',
        data=data,
        content_type='multipart/form-data'
    )
    assert gen_res.status_code == 200, f"Generation failed: {gen_res.status_code} {gen_res.get_json()}"
    gen_json = gen_res.get_json()
    assert gen_json.get('status') == 'success'
    questions = gen_json.get('questions', [])
    assert len(questions) == 5, f"Expected 5 questions, got {len(questions)}"
    print(f"[PASS] Successfully generated {len(questions)} questions from FUTURE.png:")
    for q in questions:
        print(f"  - Q{q['num']}: ({q['difficulty']} | {q['bloom_level']}) {q['question']}")
        assert 'FUTURE.png' in q['question'] or 'FUTURE.png' in q['imageRef']

    metrics = gen_json.get('quality_metrics', {})
    print(f"[PASS] Quality metrics: {metrics}")

    print("\n--- Test 5: Check Saved Uploaded Image File ---")
    saved_filename = gen_json.get('saved_filename')
    assert saved_filename, "No saved_filename returned"
    upload_path = os.path.abspath(os.path.join(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\uploads\resources", saved_filename))
    assert os.path.exists(upload_path), f"File was not saved to {upload_path}"
    print(f"[PASS] Diagram image successfully written to disk: {upload_path}")

    print("\n--- Test 6: Verify Download / View Route for Diagram ---")
    dl_res = client.get(f"/api/resources/file/{saved_filename}")
    assert dl_res.status_code == 200, f"Expected 200 on download, got {dl_res.status_code}"
    print(f"[PASS] Diagram file download/view route returned 200 OK (Content-Length: {len(dl_res.data)} bytes)")

    print("\n--- Test 7: Verify /api/questions/generate with Multipart Image ---")
    img_io2 = io.BytesIO()
    img.save(img_io2, format='PNG')
    img_io2.seek(0)
    data2 = {
        'file': (img_io2, 'FUTURE.png'),
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
    gen2_res = client.post(
        '/api/questions/generate',
        data=data2,
        content_type='multipart/form-data'
    )
    assert gen2_res.status_code == 200, f"Failed on /api/questions/generate: {gen2_res.status_code}"
    assert len(gen2_res.get_json().get('questions', [])) == 3
    print("[PASS] /api/questions/generate handled multipart diagram generation properly")

    print("\n--- Test 8: Negative Testing - Missing File ---")
    neg_res = client.post(
        '/api/questions/generate-image',
        data={'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res.status_code == 400, f"Expected 400 for missing file, got {neg_res.status_code}"
    neg_msg = neg_res.get_json().get('message')
    print(f"[PASS] Missing file rejected with 400: '{neg_msg}'")
    assert "Image Required: Please upload a diagram image first." in neg_msg

    print("\n--- Test 9: Negative Testing - Invalid File Extension ---")
    bad_file = (io.BytesIO(b"fake executable code"), "dangerous.exe")
    neg_res2 = client.post(
        '/api/questions/generate-image',
        data={'image': bad_file, 'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res2.status_code == 400, f"Expected 400 for bad extension, got {neg_res2.status_code}"
    print(f"[PASS] Invalid extension rejected with 400: '{neg_res2.get_json().get('message')}'")

    print("\n--- Test 10: Negative Testing - Corrupt Image File ---")
    corrupt_file = (io.BytesIO(b"not a valid png file bytes"), "broken.png")
    neg_res3 = client.post(
        '/api/questions/generate-image',
        data={'image': corrupt_file, 'subject': 'Database Management Systems'},
        content_type='multipart/form-data'
    )
    assert neg_res3.status_code == 400, f"Expected 400 for corrupt file, got {neg_res3.status_code}"
    print(f"[PASS] Corrupt image rejected with 400: '{neg_res3.get_json().get('message')}'")

    print("\n--- Test 11: Save Generated Questions to MySQL Question Bank ---")
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
        json={'batch': batch_data}
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
    print("ALL 11 BACKEND & SERVICE TESTS COMPLETED AND PASSED WITH 100% SUCCESS!")
    print("="*70)

if __name__ == '__main__':
    test_flask_image_flow()
