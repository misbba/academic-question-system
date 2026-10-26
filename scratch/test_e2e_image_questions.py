import io
import requests
from PIL import Image, ImageDraw

BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:8080"

def run_tests():
    session = requests.Session()

    print("\n--- Test 1: Service Health ---")
    h_resp = session.get(f"{BASE_URL}/api/health")
    assert h_resp.status_code == 200, f"Health check failed: {h_resp.status_code}"
    print("[PASS] Backend /api/health returned 200 OK")

    f_resp = session.get(f"{FRONTEND_URL}/faculty-image-question.html")
    assert f_resp.status_code == 200, f"Frontend check failed: {f_resp.status_code}"
    assert "No Image Selected" in f_resp.text, "Badge should start with 'No Image Selected'"
    print("[PASS] Frontend faculty-image-question.html is accessible and starts with 'No Image Selected'")

    print("\n--- Test 2: Faculty Login ---")
    login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "kavitha@vsb.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.status_code} {login_resp.text}"
    user_data = login_resp.json().get('user', {})
    print(f"[PASS] Successfully logged in as: {user_data.get('name')} (Role: {user_data.get('role')})")

    print("\n--- Test 3: Generate Questions with Valid Image (FUTURE.png) ---")
    # Create sample diagram image in memory
    img = Image.new('RGB', (400, 300), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 180, 150], outline=(0, 0, 128), width=3)
    draw.text((60, 90), "User Entity", fill=(0, 0, 128))
    draw.line([(180, 100), (250, 100)], fill=(0, 0, 0), width=2)
    draw.rectangle([250, 50, 380, 150], outline=(128, 0, 0), width=3)
    draw.text((260, 90), "Order Entity", fill=(128, 0, 0))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    files = {
        'image': ('FUTURE.png', img_bytes, 'image/png')
    }
    form_data = {
        'department': 'Artificial Intelligence & Data Science',
        'subject': 'Database Management Systems',
        'unit': 'Unit 1',
        'topic': 'ER Diagram Relationships',
        'num_questions': 5,
        'question_type': 'Diagram Interpretation',
        'difficulty': 'Balanced',
        'bloom_level': 'Analyze',
        'description': 'ER diagram showing relationship between User and Order entities'
    }

    gen_resp = session.post(f"{BASE_URL}/api/questions/generate-image", files=files, data=form_data)
    print(f"Generate status code: {gen_resp.status_code}")
    assert gen_resp.status_code == 200, f"Expected 200, got {gen_resp.status_code}: {gen_resp.text}"
    gen_data = gen_resp.json()
    assert gen_data.get('status') == 'success', f"Expected status 'success': {gen_data}"
    questions = gen_data.get('questions', [])
    assert len(questions) == 5, f"Expected 5 questions, got {len(questions)}"
    for q in questions:
        assert 'FUTURE.png' in q['imageRef'] or 'FUTURE.png' in q['question'], f"Question does not ground to FUTURE.png: {q}"
        print(f"  [Q{q['num']}] ({q['difficulty']} | {q['bloom_level']}) {q['question'][:80]}...")
    print(f"[PASS] Successfully generated {len(questions)} grounded questions from FUTURE.png")

    print("\n--- Test 4: Also verify /api/questions/generate route handles multipart image ---")
    img_bytes.seek(0)
    files2 = {'image': ('FUTURE.png', img_bytes, 'image/png')}
    gen_resp2 = session.post(f"{BASE_URL}/api/questions/generate", files=files2, data=form_data)
    assert gen_resp2.status_code == 200, f"Expected 200 on /api/questions/generate, got {gen_resp2.status_code}"
    assert len(gen_resp2.json().get('questions', [])) == 5
    print("[PASS] /api/questions/generate route cleanly accepted multipart diagram file")

    print("\n--- Test 5: Negative Testing (Missing Image) ---")
    empty_files = {}
    neg_resp = session.post(f"{BASE_URL}/api/questions/generate-image", files=empty_files, data=form_data)
    assert neg_resp.status_code == 400, f"Expected 400 for missing image, got {neg_resp.status_code}"
    err_json = neg_resp.json()
    assert "Image Required" in err_json.get('message', ''), f"Unexpected message: {err_json}"
    print(f"[PASS] Correctly rejected missing image with 400: '{err_json.get('message')}'")

    print("\n--- Test 6: Negative Testing (Invalid File Type) ---")
    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    inv_files = {'image': ('malicious.exe', fake_exe, 'application/octet-stream')}
    inv_resp = session.post(f"{BASE_URL}/api/questions/generate-image", files=inv_files, data=form_data)
    assert inv_resp.status_code == 400, f"Expected 400 for invalid file type, got {inv_resp.status_code}"
    print(f"[PASS] Correctly rejected invalid file type: '{inv_resp.json().get('message')}'")

    print("\n--- Test 7: Save Generated Questions to Question Bank ---")
    save_batch = [{
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

    save_resp = session.post(f"{BASE_URL}/api/question-bank", json={"batch": save_batch})
    assert save_resp.status_code in (200, 201), f"Expected 200/201 on save, got {save_resp.status_code}: {save_resp.text}"
    print(f"[PASS] Successfully saved batch of {len(save_batch)} questions to Faculty Question Bank!")

    print("\n" + "="*60)
    print("ALL 7 IMAGE/DIAGRAM QUESTIONS UPLOAD & GENERATION TESTS PASSED!")
    print("="*60)

if __name__ == '__main__':
    run_tests()
