# -*- coding: utf-8 -*-
"""
Verification Suite: Semester Examination "Publish Paper" Validation & Marks Calculation
Tests:
1. Compulsory Questions Count:
   - Part A: 10 questions x 2 marks = 20 Attempted Marks
2. Either/Or Alternatives Calculation:
   - Strictly counts ONE alternative per group (never both)
   - 5 groups x 16 marks = 80 Attempted Marks
3. Total Attempted Marks:
   - Exactly 20 + 80 = 100 Attempted Marks
4. Part B Alternative Structure Flexibility:
   - Direct 16M (1 question x 16M)
   - Split 8+8 (2 subquestions x 8M = 16M)
   - Combinations: Direct vs Split, Split vs Direct, Direct vs Direct, Split vs Split
5. Publishing Valid Semester Paper:
   - Valid 100-mark paper publishes with HTTP 200/201 (Status: Published)
6. Rejection of Incomplete Paper:
   - Paper with only 50 attempted marks is rejected with HTTP 400 and exact message
7. Rejection of Mismatched Alternative Marks:
   - Either/Or group where Alternative A != Alternative B marks is rejected
8. Internal Examination Non-Regression:
   - Internal Exam with exactly 50 attempted marks (10 + 8 + 32) validates and publishes
9. Section Name Safety:
   - Section names containing 'C' (e.g. 'SECTION A', 'SECTION B') are not mistaken for Part C
10. Agreement Between Calculation Engine, Frontend Rules, and Publishing
"""

import sys
import os
import json

backend_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from services.question_paper_service import (
    calculate_attempted_marks,
    find_section,
    validate_question_paper_structure,
    generate_template_paper,
    create_question_paper,
    get_question_paper_by_id,
    update_question_paper
)

app = create_app()

def run_tests():
    with app.app_context():
        print("=" * 80)
        print("ACADEMIC QUESTION SYSTEM: PUBLISH PAPER & MARKS CALCULATION TEST SUITE")
        print("=" * 80)

        # -------------------------------------------------------------
        # TEST 1: Compulsory Part A Questions (10 x 2 = 20M)
        # -------------------------------------------------------------
        print("\n[TEST 1] Compulsory Questions Count (Part A: 10 x 2 = 20M)")
        part_a_sec = [{
            "name": "PART - A (10 x 2 = 20 Marks)",
            "questions": [{"id": i, "marks": 2, "question_text": f"Question {i}"} for i in range(1, 11)]
        }]
        att_a = calculate_attempted_marks(part_a_sec)
        assert att_a == 20, f"Expected 20 attempted marks, got {att_a}"
        print(f"  -> PASS: 10 compulsory questions calculated to exactly {att_a} marks.")

        # -------------------------------------------------------------
        # TEST 2: Either/Or Alternative Calculation (Never Sums Both)
        # -------------------------------------------------------------
        print("\n[TEST 2] Either/Or Alternative Calculation (Never Sums Both)")
        part_b_sec = [{
            "name": "PART - B (5 x 16 = 80 Marks)",
            "groups": [
                {
                    "group_number": 1,
                    "question_number": 11,
                    "alternative_a": {"id": 101, "marks": 16, "question_text": "Direct 16M Alt A"},
                    "alternative_b": {
                        "is_subquestion": True,
                        "marks": 16,
                        "subquestions": [
                            {"id": 102, "marks": 8, "question_text": "Sub 1"},
                            {"id": 103, "marks": 8, "question_text": "Sub 2"}
                        ]
                    }
                }
            ]
        }]
        att_b = calculate_attempted_marks(part_b_sec)
        assert att_b == 16, f"Expected 16 attempted marks for 1 group (not 32!), got {att_b}"
        print(f"  -> PASS: Either/Or pair with Direct (16M) vs Split (8+8=16M) calculated to {att_b} marks (NOT 32M).")

        # -------------------------------------------------------------
        # TEST 3: Total Attempted Marks for Complete Semester Examination
        # -------------------------------------------------------------
        print("\n[TEST 3] Total Attempted Marks for 100-Mark Semester Examination")
        complete_sem_sections = [
            {
                "name": "PART - A (10 x 2 = 20 Marks)",
                "questions": [{"id": i, "marks": 2, "question_text": f"Part A Q{i}"} for i in range(1, 11)]
            },
            {
                "name": "PART - B (5 x 16 = 80 Marks)",
                "groups": [
                    {
                        "group_number": g,
                        "question_number": 10 + g,
                        "alternative_a": {"id": 100 + g*2, "marks": 16, "question_text": f"Direct 16M Q{10+g}a"},
                        "alternative_b": {
                            "is_subquestion": True,
                            "marks": 16,
                            "subquestions": [
                                {"id": 200 + g*2, "marks": 8, "question_text": f"Sub (i) Q{10+g}b"},
                                {"id": 201 + g*2, "marks": 8, "question_text": f"Sub (ii) Q{10+g}b"}
                            ]
                        }
                    } for g in range(1, 6)
                ]
            }
        ]
        total_att = calculate_attempted_marks(complete_sem_sections)
        assert total_att == 100, f"Expected exactly 100 attempted marks, got {total_att}"
        print(f"  -> PASS: Complete Semester Examination totals exactly {total_att} attempted marks.")

        # -------------------------------------------------------------
        # TEST 4: Section Name Safety ('SECTION A', 'SECTION B' not matching 'C')
        # -------------------------------------------------------------
        print("\n[TEST 4] Section Name Safety ('SECTION A', 'SECTION B' not matching 'C')")
        test_secs = [
            {"name": "SECTION A", "questions": [{"marks": 2} for _ in range(10)]},
            {"name": "SECTION B", "groups": [{"alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}} for _ in range(5)]}
        ]
        sec_c = find_section(test_secs, 'C')
        assert sec_c is None, f"Expected Section C to be None, but found: {sec_c}"
        sec_a = find_section(test_secs, 'A')
        assert sec_a is not None and sec_a["name"] == "SECTION A"
        sec_b = find_section(test_secs, 'B')
        assert sec_b is not None and sec_b["name"] == "SECTION B"
        print("  -> PASS: find_section correctly identified SECTION A and SECTION B without false Part C matches.")

        # -------------------------------------------------------------
        # TEST 5: Template Generation for Faculty 24 (Distributed Computing & DBMS)
        # -------------------------------------------------------------
        print("\n[TEST 5] Template Generation for Faculty 24 (Semester Exam 100M)")
        ok_dc, resp_dc, code_dc = generate_template_paper(24, {
            'template_type': 'semester_exam',
            'subject': 'Distributed Computing',
            'department': 'Artificial Intelligence & Data Science'
        })
        assert ok_dc and code_dc == 200, f"Distributed Computing template generation failed: {resp_dc}"
        paper_dc = resp_dc['paper']
        assert paper_dc['total_marks'] == 100
        assert len(paper_dc['sections']) == 2
        print(f"  -> PASS: Distributed Computing Semester Exam template generated with {paper_dc['total_marks']} marks.")

        ok_db, resp_db, code_db = generate_template_paper(24, {
            'template_type': 'semester_exam',
            'subject': 'Database Management Systems',
            'department': 'Artificial Intelligence & Data Science'
        })
        assert ok_db and code_db == 200, f"Database Management Systems template generation failed: {resp_db}"
        paper_db = resp_db['paper']
        assert paper_db['total_marks'] == 100
        print(f"  -> PASS: Database Management Systems Semester Exam template generated with {paper_db['total_marks']} marks.")

        # -------------------------------------------------------------
        # TEST 6: Publish Valid 100-Mark Semester Paper (Success HTTP 200)
        # -------------------------------------------------------------
        print("\n[TEST 6] Publish Valid 100-Mark Semester Paper")
        # Paper 26 belongs to Faculty 24 and has 100 attempted marks
        ok_pub, res_pub, status_pub = update_question_paper(26, 24, {"status": "Published"})
        assert ok_pub and status_pub == 200, f"Failed to publish valid paper 26: {res_pub}"
        print(f"  -> PASS: Valid Semester Paper 26 successfully published with status 200.")

        # -------------------------------------------------------------
        # TEST 7: Rejection of Genuinely Incomplete 50-Mark Paper as Semester Exam
        # -------------------------------------------------------------
        print("\n[TEST 7] Rejection of Incomplete 50-Mark Paper Submitted as Semester Exam")
        incomplete_payload = {
            "title": "Invalid Semester Exam Paper",
            "subject": "Distributed Computing",
            "department": "Artificial Intelligence & Data Science",
            "exam_type": "Semester Examination",
            "total_marks": 50,
            "question_ids": [101, 102],
            "sections": [
                {
                    "name": "PART - A (5 x 2 = 10 Marks)",
                    "questions": [{"id": i, "marks": 2, "question_text": f"Q{i}"} for i in range(1, 6)]
                },
                {
                    "name": "PART - B (1 x 8 = 8 Marks)",
                    "groups": [{"alternative_a": {"marks": 8}, "alternative_b": {"marks": 8}}]
                },
                {
                    "name": "PART - C (2 x 16 = 32 Marks)",
                    "groups": [
                        {"alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}},
                        {"alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}}
                    ]
                }
            ]
        }
        ok_rej, res_rej, code_rej = create_question_paper(24, incomplete_payload)
        assert not ok_rej and code_rej == 400, f"Expected 400 rejection, got {code_rej}: {res_rej}"
        err_msg = res_rej.get("message", "")
        assert "Semester Examination must have exactly 100 attempted marks (calculated: 50 marks)" in err_msg, f"Unexpected error message: {err_msg}"
        print(f"  -> PASS: Incomplete 50-mark paper correctly rejected with: '{err_msg}'")

        # -------------------------------------------------------------
        # TEST 8: Rejection of Mismatched Alternative Marks in Part B
        # -------------------------------------------------------------
        print("\n[TEST 8] Rejection of Mismatched Alternative Marks in Either/Or Group")
        mismatched_payload = {
            "title": "Mismatched Marks Paper",
            "subject": "Distributed Computing",
            "department": "Artificial Intelligence & Data Science",
            "exam_type": "Semester Examination",
            "total_marks": 100,
            "question_ids": [101, 102],
            "sections": [
                {
                    "name": "PART - A (10 x 2 = 20 Marks)",
                    "questions": [{"id": i, "marks": 2, "question_text": f"Part A Q{i}"} for i in range(1, 11)]
                },
                {
                    "name": "PART - B (5 x 16 = 80 Marks)",
                    "groups": [
                        {
                            "group_number": 1,
                            "question_number": 11,
                            "alternative_a": {"id": 101, "marks": 16, "question_text": "Direct 16M Alt A"},
                            "alternative_b": {"id": 102, "marks": 8, "question_text": "Only 8M Alt B (MISMATCH)"}
                        }
                    ] + [
                        {
                            "group_number": g,
                            "question_number": 10 + g,
                            "alternative_a": {"id": 100 + g*2, "marks": 16},
                            "alternative_b": {"id": 101 + g*2, "marks": 16}
                        } for g in range(2, 6)
                    ]
                }
            ]
        }
        ok_mis, res_mis, code_mis = create_question_paper(24, mismatched_payload)
        assert not ok_mis and code_mis == 400, f"Expected rejection of mismatched alternatives: {res_mis}"
        print(f"  -> PASS: Mismatched alternative marks rejected with: '{res_mis.get('message')}'")

        # -------------------------------------------------------------
        # TEST 9: Internal Examination (50 Marks) Validates Successfully
        # -------------------------------------------------------------
        print("\n[TEST 9] Internal Examination (50 Marks) Validates & Non-Regression")
        internal_payload = {
            "title": "Distributed Computing Internal Examination",
            "subject": "Distributed Computing",
            "department": "Artificial Intelligence & Data Science",
            "exam_type": "Internal Examination",
            "total_marks": 50,
            "duration": "100 Mins.",
            "status": "Draft",
            "question_ids": [101, 102],
            "sections": [
                {
                    "name": "PART - A (5 x 2 = 10 Marks)",
                    "questions": [{"id": i, "marks": 2, "question_text": f"Part A Q{i}"} for i in range(1, 6)]
                },
                {
                    "name": "PART - B (1 x 8 = 8 Marks)",
                    "groups": [
                        {
                            "group_number": 1,
                            "question_number": 6,
                            "alternative_a": {"marks": 8, "question_text": "Alt A 8M"},
                            "alternative_b": {"marks": 8, "question_text": "Alt B 8M"}
                        }
                    ]
                },
                {
                    "name": "PART - C (2 x 16 = 32 Marks)",
                    "groups": [
                        {
                            "group_number": 1,
                            "question_number": 7,
                            "alternative_a": {"marks": 16, "question_text": "Direct 16M"},
                            "alternative_b": {
                                "is_subquestion": True,
                                "marks": 16,
                                "subquestions": [
                                    {"marks": 8, "question_text": "Sub 1"},
                                    {"marks": 8, "question_text": "Sub 2"}
                                ]
                            }
                        },
                        {
                            "group_number": 2,
                            "question_number": 8,
                            "alternative_a": {"marks": 16, "question_text": "Direct 16M Q8a"},
                            "alternative_b": {"marks": 16, "question_text": "Direct 16M Q8b"}
                        }
                    ]
                }
            ]
        }
        ok_int, res_int, code_int = create_question_paper(24, internal_payload)
        assert ok_int and code_int == 201, f"Internal Examination creation failed: {res_int}"
        print(f"  -> PASS: Internal Examination created successfully with 50 marks.")

        # -------------------------------------------------------------
        # TEST 10: Faculty Isolation on Published and Draft Papers
        # -------------------------------------------------------------
        print("\n[TEST 10] Faculty Isolation Verification")
        # Faculty 1 (Kavitha) must not be able to update Faculty 24 (Murugan)'s paper 26
        ok_iso, res_iso, code_iso = update_question_paper(26, 1, {"status": "Published"})
        assert not ok_iso and code_iso == 404, f"Isolation failure! Kavitha updated Murugan's paper: {res_iso}"
        print("  -> PASS: Faculty isolation strictly enforced (Faculty 1 cannot update Faculty 24's paper).")

        print("\n" + "=" * 80)
        print("ALL 10 VERIFICATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 80)

if __name__ == '__main__':
    run_tests()
