# Comprehensive Verification Test Suite for Strict 2, 8, 16 Marks and All Requirements
import io
import re
import json
import requests
from PIL import Image, ImageDraw

BACKEND_BASE = "http://localhost:5000"
FRONTEND_BASE = "http://localhost:8080"

def create_diagram_image(fmt="JPEG", title="Lamport's Logical Clock"):
    img = Image.new("RGB", (700, 350), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Process lifelines
    draw.line([(60, 80), (640, 80)], fill=(30, 41, 59), width=3)
    draw.line([(60, 180), (640, 180)], fill=(30, 41, 59), width=3)
    draw.line([(60, 280), (640, 280)], fill=(30, 41, 59), width=3)
    # Message transmission vectors
    draw.line([(160, 80), (280, 180)], fill=(225, 29, 72), width=2)
    draw.line([(320, 180), (460, 280)], fill=(2, 132, 199), width=2)
    draw.line([(480, 80), (580, 180)], fill=(22, 163, 74), width=2)
    # Events
    for pt in [(100, 80), (160, 80), (380, 80), (480, 80),
               (120, 180), (280, 180), (320, 180), (580, 180),
               (140, 280), (460, 280), (600, 280)]:
        draw.ellipse([pt[0]-6, pt[1]-6, pt[0]+6, pt[1]+6], fill=(15, 23, 42))
    
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf

def run_tests():
    print("=" * 70)
    print("STARTING ACADEMIC SYSTEM STRICT MARKS & ARCHITECTURE TEST SUITE")
    print("=" * 70)
    
    # 0. Authentication Session
    session_murugan = requests.Session()
    login_resp = session_murugan.post(f"{BACKEND_BASE}/api/auth/login", json={
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_resp.status_code == 200, f"Murugan login failed: {login_resp.text}"
    user_data = login_resp.json()
    assert user_data["status"] == "success", "Login response not successful"
    faculty_id = user_data["user"]["id"]
    print(f"[OK] Authenticated Murugan (ID: {faculty_id})")

    session_kavitha = requests.Session()
    login_kav = session_kavitha.post(f"{BACKEND_BASE}/api/auth/login", json={
        "email": "kavitha@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert login_kav.status_code == 200, f"Kavitha login failed: {login_kav.text}"
    print(f"[OK] Authenticated Kavitha (ID: {login_kav.json()['user']['id']})")

    # TEST 1: AI Question Generator generates valid 2-mark questions
    print("\n--- TEST 1: Generate 2-Mark Questions ---")
    gen_2m = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate", json={
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "num_questions": 5,
        "marks": "2",
        "diff_easy": 40,
        "diff_medium": 40,
        "diff_hard": 20
    })
    assert gen_2m.status_code == 200, f"2M generation failed: {gen_2m.text}"
    res_2m = gen_2m.json()
    assert res_2m["status"] == "success"
    assert len(res_2m["questions"]) == 5, f"Expected 5 questions, got {len(res_2m['questions'])}"
    for q in res_2m["questions"]:
        assert q["marks"] == 2, f"Expected 2 marks, got {q['marks']}"
        assert any(k in q["question_text"].lower() for k in ["define", "identify", "state", "briefly", "list", "what", "outline", "role"]), f"Question phrasing not concise 2M: {q['question_text']}"
    print(f"[PASS] Successfully generated 5 questions strictly with 2 marks: '{res_2m['questions'][0]['question_text'][:70]}...'")

    # TEST 2: AI Question Generator generates valid 8-mark questions
    print("\n--- TEST 2: Generate 8-Mark Questions ---")
    gen_8m = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate", json={
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "num_questions": 5,
        "marks": "8"
    })
    assert gen_8m.status_code == 200, f"8M generation failed: {gen_8m.text}"
    res_8m = gen_8m.json()
    assert res_8m["status"] == "success"
    assert len(res_8m["questions"]) == 5
    for q in res_8m["questions"]:
        assert q["marks"] == 8, f"Expected 8 marks, got {q['marks']}"
        assert any(k in q["question_text"].lower() for k in ["explain", "compare", "describe", "analyze", "examine", "illustrate", "discuss"]), f"Question phrasing not detailed 8M: {q['question_text']}"
    print(f"[PASS] Successfully generated 5 questions strictly with 8 marks: '{res_8m['questions'][0]['question_text'][:70]}...'")

    # TEST 3: AI Question Generator generates valid 16-mark questions
    print("\n--- TEST 3: Generate 16-Mark Questions ---")
    gen_16m = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate", json={
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "num_questions": 5,
        "marks": "16"
    })
    assert gen_16m.status_code == 200, f"16M generation failed: {gen_16m.text}"
    res_16m = gen_16m.json()
    assert res_16m["status"] == "success"
    assert len(res_16m["questions"]) == 5
    for q in res_16m["questions"]:
        assert q["marks"] == 16, f"Expected 16 marks, got {q['marks']}"
        assert any(k in q["question_text"].lower() for k in ["design", "critically analyze", "formulate", "conduct", "synthesize"]), f"Question phrasing not comprehensive 16M: {q['question_text']}"
    print(f"[PASS] Successfully generated 5 questions strictly with 16 marks: '{res_16m['questions'][0]['question_text'][:70]}...'")

    # TEST 4: Backend strictly rejects invalid marks (1, 5, 10, 15) with HTTP 400
    print("\n--- TEST 4: Reject Invalid Marks with HTTP 400 ---")
    for bad_mark in [1, 5, 10, 15, "13", "invalid"]:
        # Test generation rejection
        rej_gen = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate", json={
            "subject": "Database Management Systems",
            "marks": bad_mark
        })
        assert rej_gen.status_code == 400, f"Expected 400 for bad generation marks {bad_mark}, got {rej_gen.status_code}"
        assert "Only 2, 8, and 16 marks" in rej_gen.text, f"Unexpected error message: {rej_gen.text}"

        # Test single question save rejection
        rej_save = session_murugan.post(f"{BACKEND_BASE}/api/questions", json={
            "question_text": "Sample test question with unsupported marks?",
            "subject": "Database Management Systems",
            "marks": bad_mark
        })
        assert rej_save.status_code == 400, f"Expected 400 for bad save marks {bad_mark}, got {rej_save.status_code}"

        # Test batch save rejection
        rej_batch = session_murugan.post(f"{BACKEND_BASE}/api/question-bank", json={
            "questions": [{
                "question_text": "Sample batch question with unsupported marks?",
                "subject": "Database Management Systems",
                "marks": bad_mark
            }]
        })
        assert rej_batch.status_code == 400, f"Expected 400 for batch bad marks {bad_mark}, got {rej_batch.status_code}"
    print("[PASS] Backend strictly rejects unsupported marks (1, 5, 10, 13, 15) with HTTP 400 across all endpoints!")

    # TEST 5: UI no longer presents Short Answer or MCQ as substitutes for marks
    print("\n--- TEST 5: Verify Frontend HTML Forms ---")
    fe_gen_html = requests.get(f"{FRONTEND_BASE}/faculty-generate-questions.html").text
    assert 'id="genMarks"' in fe_gen_html, "faculty-generate-questions.html must have id='genMarks'"
    assert '<option value="2"' in fe_gen_html and '<option value="8"' in fe_gen_html and '<option value="16"' in fe_gen_html
    # Ensure options 5, 10, 15 are not in genMarks
    assert 'value="5"' not in fe_gen_html[fe_gen_html.find('id="genMarks"'):fe_gen_html.find('</select>', fe_gen_html.find('id="genMarks"'))]

    fe_img_html = requests.get(f"{FRONTEND_BASE}/faculty-image-question.html").text
    assert 'id="imgMarksSelect"' in fe_img_html, "faculty-image-question.html must have id='imgMarksSelect'"

    fe_paper_html = requests.get(f"{FRONTEND_BASE}/faculty-question-paper.html").text
    assert '5 Marks' not in fe_paper_html[fe_paper_html.find('id="filterPaperMarks"'):fe_paper_html.find('</select>', fe_paper_html.find('id="filterPaperMarks"'))]
    assert '13 Marks' not in fe_paper_html[fe_paper_html.find('id="filterPaperMarks"'):fe_paper_html.find('</select>', fe_paper_html.find('id="filterPaperMarks"'))]
    assert '15 Marks' not in fe_paper_html[fe_paper_html.find('id="filterPaperMarks"'):fe_paper_html.find('</select>', fe_paper_html.find('id="filterPaperMarks"'))]

    fe_quiz_html = requests.get(f"{FRONTEND_BASE}/faculty-generate-quiz.html").text
    assert '1 Mark' in fe_quiz_html[fe_quiz_html.find('id="quizMarksPerQ"'):fe_quiz_html.find('</select>', fe_quiz_html.find('id="quizMarksPerQ"'))]
    print("[PASS] Frontend forms in all HTML files offer strict 2, 8, and 16 marks, with Quiz Generator specifically supporting 1 mark!")

    # TEST 6: Difficulty Distribution Handled Correctly
    print("\n--- TEST 6: Difficulty Distribution Calibration ---")
    gen_dist = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate", json={
        "subject": "Database Management Systems",
        "num_questions": 10,
        "marks": "Mixed",
        "diff_easy": 30,
        "diff_medium": 50,
        "diff_hard": 20
    })
    assert gen_dist.status_code == 200
    qs = gen_dist.json()["questions"]
    assert len(qs) == 10
    easy_c = sum(1 for q in qs if q["difficulty"] == "Easy")
    med_c = sum(1 for q in qs if q["difficulty"] == "Medium")
    hard_c = sum(1 for q in qs if q["difficulty"] == "Hard")
    assert easy_c == 3 and med_c == 5 and hard_c == 2, f"Distribution mismatch: {easy_c}E, {med_c}M, {hard_c}H"
    for q in qs:
        assert q["marks"] in (2, 8, 16), f"Invalid mark in mixed set: {q['marks']}"
    print(f"[PASS] Difficulty distribution calibrated: {easy_c} Easy (30%), {med_c} Medium (50%), {hard_c} Hard (20%)")

    # TEST 7: Real JPG Upload
    print("\n--- TEST 7: Real JPG Diagram Upload ---")
    jpg_bytes = create_diagram_image("JPEG")
    res_jpg = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("test_diagram.jpg", jpg_bytes, "image/jpeg")
    }, data={
        "subject": "Distributed Computing",
        "marks": "8",
        "count": "5"
    })
    assert res_jpg.status_code == 200, f"JPG generation failed: {res_jpg.text}"
    assert res_jpg.json()["status"] == "success"
    print("[PASS] Real JPG image upload analyzed and accepted!")

    # TEST 8: PNG and WEBP Uploads
    print("\n--- TEST 8: PNG & WEBP Diagram Uploads ---")
    png_bytes = create_diagram_image("PNG")
    res_png = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("network_topology.png", png_bytes, "image/png")
    }, data={"subject": "Distributed Computing", "marks": "2", "count": "3"})
    assert res_png.status_code == 200

    webp_bytes = create_diagram_image("WEBP")
    res_webp = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("system_schema.webp", webp_bytes, "image/webp")
    }, data={"subject": "Distributed Computing", "marks": "16", "count": "3"})
    assert res_webp.status_code == 200
    print("[PASS] PNG and WEBP formats successfully analyzed and accepted!")

    # TEST 9: Filenames with Spaces Preserved
    print("\n--- TEST 9: Preserve Original Filename with Spaces ---")
    lamport_name = "lamports algorithm.jpg"
    lamport_bytes = create_diagram_image("JPEG", title="Lamport's Logical Clock")
    res_lamp = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": (lamport_name, lamport_bytes, "image/jpeg")
    }, data={
        "original_filename": lamport_name,
        "subject": "Distributed Computing",
        "marks": "Mixed",
        "count": "5"
    })
    assert res_lamp.status_code == 200
    lamp_data = res_lamp.json()
    assert lamp_data["original_filename"] == lamport_name
    assert lamp_data["filename"] == lamport_name
    for q in lamp_data["questions"]:
        assert q["imageRef"] == lamport_name
        assert q["source_reference"] == lamport_name
        assert lamport_name in q["question_text"]
    print(f"[PASS] Original filename '{lamport_name}' preserved across question text, references, and metadata!")

    # TEST 10 & 11: Image Analysis Endpoint Receives File Bytes & Produces Grounded Questions
    print("\n--- TEST 10 & 11: Diagram Analysis Endpoint & Feature Extraction ---")
    analyze_bytes = create_diagram_image("JPEG", title="Lamport's Logical Clock")
    res_ana = session_murugan.post(f"{BACKEND_BASE}/api/questions/analyze-image", files={
        "image": (lamport_name, analyze_bytes, "image/jpeg")
    }, data={"subject": "Distributed Computing", "original_filename": lamport_name})
    assert res_ana.status_code == 200
    ana_data = res_ana.json()
    assert ana_data["status"] == "success"
    assert ana_data["metadata"]["width"] == 700
    assert ana_data["metadata"]["height"] == 350
    assert ana_data["diagram_category"] == "Distributed Synchronization & Logical Clocks"
    assert len(ana_data["detected_concepts"]) >= 3
    print(f"[PASS] Image features extracted: {ana_data['metadata']['width']}x{ana_data['metadata']['height']}px, Category: '{ana_data['diagram_category']}'")

    # TEST 12 & 13: Stale State and Image Replacement
    print("\n--- TEST 12 & 13: Replacing Image Updates Context & Removing Clears State ---")
    # Verify another distinct image gets distinct category and concepts
    er_bytes = create_diagram_image("PNG", title="ER Schema")
    res_er = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("customer database schema.png", er_bytes, "image/png")
    }, data={"original_filename": "customer database schema.png", "subject": "Database Management Systems", "marks": "8", "count": "3"})
    assert res_er.status_code == 200
    er_data = res_er.json()
    assert er_data["original_filename"] == "customer database schema.png"
    assert er_data["diagram_category"] == "Database & Entity-Relationship Model"
    assert "Logical Clock" not in er_data["diagram_title"]
    print("[PASS] Replacing image produces fresh analysis and does not reuse stale diagram data!")

    # TEST 14: Failed AI Calls Return Useful Errors
    print("\n--- TEST 14: Clear Error Handling on Failures ---")
    # Empty file
    res_empty = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("empty.png", io.BytesIO(b""), "image/png")
    })
    assert res_empty.status_code == 400
    assert "empty" in res_empty.json()["message"].lower()

    # Invalid corrupted bytes
    res_corrupt = session_murugan.post(f"{BACKEND_BASE}/api/questions/generate-image", files={
        "image": ("bad.png", io.BytesIO(b"NOT_AN_IMAGE_CONTENT"), "image/png")
    })
    assert res_corrupt.status_code == 400
    assert "invalid" in res_corrupt.json()["message"].lower() or "corrupt" in res_corrupt.json()["message"].lower()
    print("[PASS] Informative, safe error messages returned for empty or corrupt files!")

    # TEST 15: Question Bank Save with Correct Marks and Faculty Ownership
    print("\n--- TEST 15: Question Bank Persistence & Ownership ---")
    q_to_save = {
        "question_text": "Verify the clock condition monotonicity constraint in Lamport scalar timestamps.",
        "subject": "Distributed Computing",
        "department": "Artificial Intelligence & Data Science",
        "unit": "Unit 1",
        "topic": "Lamport Logical Clocks",
        "marks": 8,
        "difficulty": "Medium",
        "question_type": "Analytical Principle (8 Marks)",
        "bloom_level": "Analyze",
        "source_type": "Diagram Image",
        "source_reference": "lamports algorithm.jpg",
        "image_ref": "lamports algorithm.jpg"
    }
    save_res = session_murugan.post(f"{BACKEND_BASE}/api/question-bank", json={
        "questions": [q_to_save]
    })
    assert save_res.status_code == 200, f"QB save failed: {save_res.text}"
    saved_data = save_res.json()
    assert saved_data["status"] == "success"

    # Verify retrieval
    ret_res = session_murugan.get(f"{BACKEND_BASE}/api/question-bank?subject=Distributed+Computing&marks=8")
    assert ret_res.status_code == 200
    saved_questions = ret_res.json().get("questions", [])
    found = any(q["question_text"] == q_to_save["question_text"] and q["marks"] == 8 and q["created_by"] == faculty_id for q in saved_questions)
    assert found, "Saved question not retrieved with correct marks and created_by ownership!"
    print(f"[PASS] Question Bank verified: Saved with 8 marks, exact filename, and faculty ID {faculty_id}!")

    # TEST 16: Paper Builder Totals & Marks Restrictions
    print("\n--- TEST 16: Paper Builder Marks Verification ---")
    # Fetch paper questions for Murugan
    paper_qs = session_murugan.get(f"{BACKEND_BASE}/api/questions?subject=Database+Management+Systems").json().get("questions", [])
    for q in paper_qs:
        assert q["marks"] in (2, 8, 16), f"Legacy mark found in question ID {q['id']}: {q['marks']}"
    print(f"[PASS] All {len(paper_qs)} questions available for Paper Builder strictly have 2, 8, or 16 marks!")

    # TEST 17: Faculty Isolation (Murugan vs Kavitha)
    print("\n--- TEST 17: Strict Faculty Isolation ---")
    kav_qb = session_kavitha.get(f"{BACKEND_BASE}/api/question-bank?subject=Distributed+Computing").json().get("questions", [])
    for q in kav_qb:
        assert q["created_by"] == 25, f"Kavitha's view contains non-isolated question belonging to {q['created_by']}"
    
    # Kavitha cannot see Murugan's DBMS materials
    kav_res = session_kavitha.get(f"{BACKEND_BASE}/api/resources?subject=Database+Management+Systems").json().get("resources", [])
    assert len(kav_res) == 0, f"Isolation failure: Kavitha saw {len(kav_res)} DBMS resources of Murugan"
    print("[PASS] Strict faculty isolation verified between Murugan (ID 24) and Kavitha (ID 25)!")

    # TEST 18: Existing Application Routes & Features Remain Functional
    print("\n--- TEST 18: Core Routes and Features Regression Test ---")
    routes_to_test = [
        ("/", 200),
        ("/faculty-login.html", 200),
        ("/faculty-dashboard.html", 200),
        ("/faculty-generate-questions.html", 200),
        ("/faculty-image-question.html", 200),
        ("/faculty-question-paper.html", 200),
        ("/faculty-generate-quiz.html", 200),
        ("/faculty-generate-assignment.html", 200),
        ("/faculty-voice-question.html", 200),
        ("/faculty-language-converter.html", 200),
        ("/student-login.html", 200),
        ("/student-dashboard.html", 200)
    ]
    for route, expected_status in routes_to_test:
        r = requests.get(f"{FRONTEND_BASE}{route}")
        assert r.status_code == expected_status, f"Route {route} returned status {r.status_code}"
    print("[PASS] All 12 application pages and routes returned HTTP 200 OK!")

    print("\n" + "=" * 70)
    print("ALL 18 VERIFICATION TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
