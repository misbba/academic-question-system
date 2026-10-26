import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from services.question_paper_service import (
    generate_template_paper,
    create_question_paper,
    get_question_paper_by_id,
    calculate_attempted_marks,
    validate_question_paper_structure
)
from models.database import get_db_connection

def test_templates():
    print("=" * 60)
    print("TESTING ACADEMIC QUESTION PAPER GENERATOR TEMPLATES")
    print("=" * 60)

    # 1. Fetch a faculty user ID
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, full_name FROM users WHERE role = 'faculty' LIMIT 1")
        fac = cur.fetchone()
    conn.close()
    faculty_id = fac['id']
    print(f"Testing with Faculty: {fac['full_name']} (ID: {faculty_id})")

    # ----------------------------------------------------
    # TEST 1: INTERNAL TEST TEMPLATE GENERATION (50 MARKS)
    # ----------------------------------------------------
    print("\n--- Test 1: Internal Test Generation ---")
    ok, res, code = generate_template_paper(faculty_id, {
        "template": "internal_test",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6"
    })
    assert ok, f"Internal test generation failed: {res}"
    assert code == 200
    paper = res["paper"]

    # Verify Attempted Marks = 50
    attempted = res["total_attempted_marks"]
    print(f" -> Internal Test Attempted Marks: {attempted}")
    assert attempted == 50, f"Expected 50 attempted marks, got {attempted}"

    # Verify Section A
    sec_a = paper["sections"][0]
    print(f" -> Section A: {sec_a['name']} - Questions count: {len(sec_a['questions'])}, Marks: {sec_a['attempted_marks']}")
    assert len(sec_a["questions"]) == 5
    assert sec_a["attempted_marks"] == 10
    for q in sec_a["questions"]:
        assert q["marks"] == 2

    # Verify Section B
    sec_b = paper["sections"][1]
    print(f" -> Section B: {sec_b['name']} - Groups: {len(sec_b['groups'])}, Marks: {sec_b['attempted_marks']}")
    assert len(sec_b["groups"]) == 1
    assert sec_b["attempted_marks"] == 8
    g1 = sec_b["groups"][0]
    print(f"    - Alt A: '{g1['lesson_a']}' (8 Marks) | Alt B: '{g1['lesson_b']}' (8 Marks)")
    assert g1["lesson_a"] != g1["lesson_b"], "Alt A and Alt B must be from different lessons!"

    # Verify Section C
    sec_c = paper["sections"][2]
    print(f" -> Section C: {sec_c['name']} - Groups: {len(sec_c['groups'])}, Marks: {sec_c['attempted_marks']}")
    assert len(sec_c["groups"]) == 2
    assert sec_c["attempted_marks"] == 32
    for idx, g in enumerate(sec_c["groups"], 1):
        print(f"    - Group {idx}: Alt A '{g['lesson_a']}' vs Alt B '{g['lesson_b']}' (16 Marks Attempted)")

    # Save to Database
    ok_save, res_save, code_save = create_question_paper(faculty_id, paper)
    assert ok_save, f"Failed to save internal test to DB: {res_save}"
    saved_paper = res_save["paper"]
    print(f" -> Successfully saved Internal Test to MySQL! Paper Code: {saved_paper['paper_code']}, DB Total Marks: {saved_paper['total_marks']}")
    assert saved_paper['total_marks'] == 50, f"Expected total_marks 50 in DB, got {saved_paper['total_marks']}"

    # ----------------------------------------------------
    # TEST 2: SEMESTER EXAM TEMPLATE GENERATION (100 MARKS)
    # ----------------------------------------------------
    print("\n--- Test 2: Semester Exam Generation ---")
    ok2, res2, code2 = generate_template_paper(faculty_id, {
        "template": "semester_exam",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6"
    })
    assert ok2, f"Semester exam generation failed: {res2}"
    assert code2 == 200
    paper2 = res2["paper"]

    # Verify Attempted Marks = 100
    attempted2 = res2["total_attempted_marks"]
    print(f" -> Semester Exam Attempted Marks: {attempted2}")
    assert attempted2 == 100, f"Expected 100 attempted marks, got {attempted2}"

    # Verify Section A: 10 questions with exactly 2 questions per unit
    sec_a2 = paper2["sections"][0]
    print(f" -> Section A: {sec_a2['name']} - Questions count: {len(sec_a2['questions'])}, Marks: {sec_a2['attempted_marks']}")
    assert len(sec_a2["questions"]) == 10
    assert sec_a2["attempted_marks"] == 20

    from services.question_paper_service import normalize_unit
    unit_distribution = {}
    for q in sec_a2["questions"]:
        u = normalize_unit(q["unit"])
        unit_distribution[u] = unit_distribution.get(u, 0) + 1
    print("    - Section A Unit Distribution:", unit_distribution)
    for u in ["Unit I", "Unit II", "Unit III", "Unit IV", "Unit V"]:
        assert unit_distribution.get(u) == 2, f"Unit {u} must have exactly 2 questions, found {unit_distribution.get(u)}"

    # Verify Section B: 5 Either/Or groups across the 5 units
    sec_b2 = paper2["sections"][1]
    print(f" -> Section B: {sec_b2['name']} - Groups: {len(sec_b2['groups'])}, Marks: {sec_b2['attempted_marks']}")
    assert len(sec_b2["groups"]) == 5
    assert sec_b2["attempted_marks"] == 80
    for idx, g in enumerate(sec_b2["groups"], 1):
        print(f"    - Group {idx} ({g['unit']}): Alt A '{g['lesson_a']}' vs Alt B '{g['lesson_b']}' (16 Marks Attempted)")

    # Save to Database
    ok_save2, res_save2, code_save2 = create_question_paper(faculty_id, paper2)
    assert ok_save2, f"Failed to save semester exam to DB: {res_save2}"
    saved_paper2 = res_save2["paper"]
    print(f" -> Successfully saved Semester Exam to MySQL! Paper Code: {saved_paper2['paper_code']}, DB Total Marks: {saved_paper2['total_marks']}")
    assert saved_paper2['total_marks'] == 100, f"Expected total_marks 100 in DB, got {saved_paper2['total_marks']}"

    # ----------------------------------------------------
    # TEST 3: NEGATIVE VALIDATION TESTS
    # ----------------------------------------------------
    print("\n--- Test 3: Validation Rejection on Invalid Marks/Distribution ---")
    # Invalid Internal Test with 60 marks
    bad_int = dict(paper)
    bad_int["sections"] = [
        {"name": "SECTION A", "type": "compulsory", "count": 10, "marks_per_q": 2, "questions": [{"marks": 2}] * 10},
        {"name": "SECTION B", "type": "either_or", "groups": [{"attempted_marks": 8, "alternative_a": {"marks": 8}, "alternative_b": {"marks": 8}}]},
        {"name": "SECTION C", "type": "either_or", "groups": [
            {"attempted_marks": 16, "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}},
            {"attempted_marks": 16, "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}}
        ]}
    ]
    ok_bad, res_bad, _ = create_question_paper(faculty_id, bad_int)
    assert not ok_bad, "Should reject internal test with invalid attempted marks!"
    print(f" -> Correctly rejected invalid internal test: {res_bad['message']}")

    # Invalid Semester Exam with skewed unit distribution
    bad_sem = dict(paper2)
    bad_sem["sections"] = [
        {
            "name": "SECTION A", "type": "compulsory", "count": 10, "marks_per_q": 2,
            "questions": [
                {"unit": "Unit I", "marks": 2}, {"unit": "Unit I", "marks": 2}, {"unit": "Unit I", "marks": 2},
                {"unit": "Unit II", "marks": 2},
                {"unit": "Unit III", "marks": 2}, {"unit": "Unit III", "marks": 2},
                {"unit": "Unit IV", "marks": 2}, {"unit": "Unit IV", "marks": 2},
                {"unit": "Unit V", "marks": 2}, {"unit": "Unit V", "marks": 2}
            ]
        },
        sec_b2
    ]
    ok_bad_sem, res_bad_sem, _ = create_question_paper(faculty_id, bad_sem)
    assert not ok_bad_sem, "Should reject semester exam with skewed unit distribution!"
    print(f" -> Correctly rejected invalid semester exam: {res_bad_sem['message']}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED 100%!")
    print("=" * 60)

if __name__ == '__main__':
    test_templates()
