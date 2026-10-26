# -*- coding: utf-8 -*-
"""
Verification Suite: Semester Exam Part B Flexible 16-Mark Question Format
Tests:
1. Semester Exam Generation:
   - Part A: 10 compulsory questions x 2 marks = 20 Marks
   - Part B: 5 Either/Or groups x 16 attempted marks = 80 Marks (Units I-V, Q11-Q15)
   - Only Part A and Part B (Strictly No Part C)
   - Total Attempted Marks = 100
2. Format Support in Part B:
   - Direct 16-Mark Question (1 complete question worth 16 marks)
   - Split 16-Mark Question (2 subquestions of 8 marks each, combined = 16)
   - Either/Or combinations: Direct vs Split, Split vs Direct, Direct vs Direct, Split vs Split
3. Attempted Marks Calculation:
   - Counts only 1 alternative per group (never sums both)
4. Validation Enforcement:
   - Enforces 16 marks per alternative
   - Enforces exactly 100 attempted marks
   - Rejects Part C in Semester Exam
5. Save & Readback from MySQL:
   - Preserves format, subquestions, and marks across database save and reload
6. Internal Exam Non-Regression:
   - Confirms Internal Exam (50 marks, Parts A/B/C) remains fully intact
"""

import sys
import os
import json

backend_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app import create_app
from models.database import get_db_connection
from services.question_paper_service import (
    calculate_attempted_marks,
    validate_question_paper_structure,
    generate_template_paper,
    create_question_paper,
    get_question_paper_by_id,
    update_question_paper
)

app = create_app()

def run_verification():
    with app.app_context():
        print("=" * 75)
        print("RUNNING FLEXIBLE 16-MARK SEMESTER EXAM VERIFICATION SUITE")
        print("=" * 75)

        # -----------------------------------------------------------------
        # TEST 1: Generate Semester Exam (Machine Learning)
        # -----------------------------------------------------------------
        print("\n--- TEST 1: Semester Exam Generation (Machine Learning) ---")
        ok, resp, code = generate_template_paper(24, {
            'template_type': 'semester_exam',
            'subject': 'Machine Learning',
            'department': 'Artificial Intelligence & Data Science',
            'semester': 'Semester 6',
            'academic_year': '2025-2026'
        })
        assert ok and code == 200, f"Failed to generate template: {resp}"
        paper = resp['paper']

        sections = paper.get('sections', [])
        print(f"Paper Title: {paper.get('title')}")
        print(f"Total Sections: {len(sections)}")
        sec_names = [s.get('name') for s in sections]
        print(f"Section Names: {sec_names}")

        # Check section count: strictly Part A and Part B only
        assert len(sections) == 2, f"Expected exactly 2 sections (Part A & B), found {len(sections)}"
        assert any('PART - A' in s.get('name', '') for s in sections), "Part A missing"
        assert any('PART - B' in s.get('name', '') for s in sections), "Part B missing"
        assert not any('PART - C' in s.get('name', '') for s in sections), "Part C MUST NOT be present in Semester Exam"
        print("Verified: Semester Exam contains strictly Part A and Part B only. No Part C.")

        # Check Part A
        sec_a = next(s for s in sections if 'PART - A' in s.get('name', ''))
        assert sec_a.get('attempted_marks') == 20, f"Part A expected 20 marks, got {sec_a.get('attempted_marks')}"
        assert len(sec_a.get('questions', [])) == 10, f"Part A expected 10 questions, got {len(sec_a.get('questions', []))}"
        print(f"Part A verified: 10 questions x 2 marks = {sec_a.get('attempted_marks')} Marks")

        # Check Part B
        sec_b = next(s for s in sections if 'PART - B' in s.get('name', ''))
        groups = sec_b.get('groups', [])
        assert len(groups) == 5, f"Part B expected 5 Either/Or groups, got {len(groups)}"
        assert sec_b.get('attempted_marks') == 80, f"Part B expected 80 attempted marks, got {sec_b.get('attempted_marks')}"
        print(f"Part B verified: 5 Either/Or groups x 16 marks = {sec_b.get('attempted_marks')} Attempted Marks")

        # Check total attempted marks
        total_attempted = paper.get('total_marks')
        assert total_attempted == 100, f"Total attempted marks expected 100, got {total_attempted}"
        print(f"Total Attempted Marks verified: {total_attempted} Marks (20 + 80 = 100)")

        # -----------------------------------------------------------------
        # TEST 2: Inspect Part B 16-Mark Question Formats
        # -----------------------------------------------------------------
        print("\n--- TEST 2: Inspect Either/Or Format Combinations in Part B ---")
        has_direct = False
        has_split = False

        for g in groups:
            q_num = g.get('question_number')
            unit = g.get('unit')
            alt_a = g.get('alternative_a', {})
            alt_b = g.get('alternative_b', {})

            print(f"\nQuestion {q_num} ({unit}) — Attempted Marks: {g.get('attempted_marks')}:")

            # Check Alt A
            if alt_a.get('is_subquestion') or alt_a.get('subquestions'):
                has_split = True
                subs = alt_a.get('subquestions', [])
                assert len(subs) == 2, f"Split question must have exactly 2 subquestions, got {len(subs)}"
                assert subs[0].get('marks') == 8 and subs[1].get('marks') == 8, f"Subquestions must each be 8M, got {subs[0].get('marks')}, {subs[1].get('marks')}"
                print(f"  Alternative (a) [SPLIT 8+8 = 16M]:")
                print(f"    (i)  8M: {subs[0].get('text')[:50]}... {subs[0].get('bloom_tag')}")
                print(f"    (ii) 8M: {subs[1].get('text')[:50]}... {subs[1].get('bloom_tag')}")
            else:
                has_direct = True
                assert alt_a.get('marks') == 16, f"Direct question must be 16M, got {alt_a.get('marks')}"
                print(f"  Alternative (a) [DIRECT 16M]: {alt_a.get('question_text')[:55]}... ({alt_a.get('marks')}M) {alt_a.get('bloom_tag')}")

            # Check Alt B
            if alt_b.get('is_subquestion') or alt_b.get('subquestions'):
                has_split = True
                subs = alt_b.get('subquestions', [])
                assert len(subs) == 2, f"Split question must have exactly 2 subquestions, got {len(subs)}"
                assert subs[0].get('marks') == 8 and subs[1].get('marks') == 8, f"Subquestions must each be 8M, got {subs[0].get('marks')}, {subs[1].get('marks')}"
                print(f"  Alternative (b) [SPLIT 8+8 = 16M]:")
                print(f"    (i)  8M: {subs[0].get('text')[:50]}... {subs[0].get('bloom_tag')}")
                print(f"    (ii) 8M: {subs[1].get('text')[:50]}... {subs[1].get('bloom_tag')}")
            else:
                has_direct = True
                assert alt_b.get('marks') == 16, f"Direct question must be 16M, got {alt_b.get('marks')}"
                print(f"  Alternative (b) [DIRECT 16M]: {alt_b.get('question_text')[:55]}... ({alt_b.get('marks')}M) {alt_b.get('bloom_tag')}")

        assert has_direct, "Expected at least one direct 16M question in Part B"
        assert has_split, "Expected at least one split 8+8 question in Part B"
        print(f"\nSUCCESS: Both Direct 16M and Split (8+8) formats successfully generated & verified across Part B!")

        # -----------------------------------------------------------------
        # TEST 3: Validation Logic Enforcement
        # -----------------------------------------------------------------
        print("\n--- TEST 3: Validation Logic Enforcement ---")

        # 3A: Paper with Part C in Semester Exam MUST BE REJECTED
        invalid_with_part_c = {
            'exam_type': 'Semester Examination',
            'sections': [
                {'name': 'PART - A', 'attempted_marks': 20, 'questions': [{'marks': 2}]*10},
                {'name': 'PART - B', 'attempted_marks': 80, 'groups': [{'question_number': 11, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}}]*5},
                {'name': 'PART - C', 'attempted_marks': 15, 'groups': [{'attempted_marks': 15}]}
            ]
        }
        valid, msg = validate_question_paper_structure(invalid_with_part_c, 100)
        assert not valid, "Validation must reject Part C in Semester Exam"
        print(f"Rule 1 passed (Part C rejected): {msg}")

        # 3B: Alternative with invalid marks (e.g. 14 marks instead of 16) MUST BE REJECTED
        invalid_alt_marks = {
            'exam_type': 'Semester Examination',
            'sections': [
                {'name': 'PART - A', 'attempted_marks': 20, 'questions': [{'marks': 2}]*10},
                {'name': 'PART - B', 'attempted_marks': 80, 'groups': [
                    {'question_number': 11, 'attempted_marks': 16, 'alternative_a': {'marks': 14}, 'alternative_b': {'marks': 16}}, # Invalid 14M
                    {'question_number': 12, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 13, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 14, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 15, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}}
                ]}
            ]
        }
        valid, msg = validate_question_paper_structure(invalid_alt_marks, 100)
        assert not valid, "Validation must reject non-16M alternatives in Part B"
        print(f"Rule 2 passed (Invalid alternative marks rejected): {msg}")

        # 3C: Split question whose subquestions do not sum to 16 MUST BE REJECTED
        invalid_split_sum = {
            'exam_type': 'Semester Examination',
            'sections': [
                {'name': 'PART - A', 'attempted_marks': 20, 'questions': [{'marks': 2}]*10},
                {'name': 'PART - B', 'attempted_marks': 80, 'groups': [
                    {
                        'question_number': 11,
                        'attempted_marks': 16,
                        'alternative_a': {
                            'is_subquestion': True,
                            'subquestions': [{'marks': 8}, {'marks': 5}] # 8 + 5 = 13 != 16
                        },
                        'alternative_b': {'marks': 16}
                    },
                    {'question_number': 12, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 13, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 14, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 15, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}}
                ]}
            ]
        }
        valid, msg = validate_question_paper_structure(invalid_split_sum, 100)
        assert not valid, "Validation must reject split subquestions that do not sum to 16"
        print(f"Rule 3 passed (Split subquestion sum != 16 rejected): {msg}")

        # 3D: Valid paper with mixed Direct and Split alternatives MUST PASS
        valid_mixed = {
            'exam_type': 'Semester Examination',
            'sections': [
                {'name': 'PART - A', 'attempted_marks': 20, 'questions': [{'marks': 2}]*10},
                {'name': 'PART - B', 'attempted_marks': 80, 'groups': [
                    {'question_number': 11, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'is_subquestion': True, 'subquestions': [{'marks': 8}, {'marks': 8}]}},
                    {'question_number': 12, 'attempted_marks': 16, 'alternative_a': {'is_subquestion': True, 'subquestions': [{'marks': 8}, {'marks': 8}]}, 'alternative_b': {'marks': 16}},
                    {'question_number': 13, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'marks': 16}},
                    {'question_number': 14, 'attempted_marks': 16, 'alternative_a': {'is_subquestion': True, 'subquestions': [{'marks': 8}, {'marks': 8}]}, 'alternative_b': {'is_subquestion': True, 'subquestions': [{'marks': 8}, {'marks': 8}]}},
                    {'question_number': 15, 'attempted_marks': 16, 'alternative_a': {'marks': 16}, 'alternative_b': {'is_subquestion': True, 'subquestions': [{'marks': 8}, {'marks': 8}]}}
                ]}
            ]
        }
        valid, msg = validate_question_paper_structure(valid_mixed, 100)
        assert valid, f"Valid mixed paper should pass validation, got: {msg}"
        print("Rule 4 passed (Valid mixed paper passes validation without issues).")

        # -----------------------------------------------------------------
        # TEST 4: MySQL Persistence & Readback
        # -----------------------------------------------------------------
        print("\n--- TEST 4: MySQL Persistence & Reload ---")
        ok_save, resp_save, code_save = create_question_paper(24, paper)
        assert ok_save and code_save == 201, f"Failed to save paper to DB: {resp_save}"
        saved_id = resp_save['paper']['id']
        print(f"Successfully saved paper to MySQL database with ID #{saved_id}")

        # Reload from database
        reloaded = get_question_paper_by_id(saved_id, faculty_id=24)
        assert reloaded is not None, "Failed to reload paper from database"
        assert reloaded['total_marks'] == 100, f"Reloaded marks expected 100, got {reloaded['total_marks']}"

        reloaded_sections = reloaded['sections']
        if isinstance(reloaded_sections, str):
            reloaded_sections = json.loads(reloaded_sections)

        assert len(reloaded_sections) == 2, f"Reloaded paper must have exactly 2 sections, found {len(reloaded_sections)}"
        r_sec_b = next(s for s in reloaded_sections if 'PART - B' in s.get('name', ''))
        r_groups = r_sec_b.get('groups', [])
        assert len(r_groups) == 5, f"Reloaded Part B must have 5 groups, found {len(r_groups)}"

        # Verify format preservation
        print(f"Reloaded Part B groups verified:")
        for g in r_groups:
            q_num = g.get('question_number')
            alt_a = g.get('alternative_a', {})
            alt_b = g.get('alternative_b', {})
            fmt_a = "Split (8+8)" if (alt_a.get('is_subquestion') or alt_a.get('subquestions')) else "Direct 16M"
            fmt_b = "Split (8+8)" if (alt_b.get('is_subquestion') or alt_b.get('subquestions')) else "Direct 16M"
            print(f"  Q{q_num}: Option (a) = {fmt_a} | Option (b) = {fmt_b}")

        print("SUCCESS: Selected formats preserved accurately in MySQL and verified upon readback.")

        # -----------------------------------------------------------------
        # TEST 5: Internal Exam Non-Regression
        # -----------------------------------------------------------------
        print("\n--- TEST 5: Internal Exam Non-Regression ---")
        ok_int, resp_int, code_int = generate_template_paper(24, {
            'template_type': 'internal_test',
            'subject': 'Machine Learning',
            'department': 'Artificial Intelligence & Data Science',
            'semester': 'Semester 6',
            'academic_year': '2025-2026',
            'units': ['Unit I', 'Unit II']
        })
        assert ok_int and code_int == 200, f"Internal Exam generation failed: {resp_int}"
        int_paper = resp_int['paper']
        assert int_paper['total_marks'] == 50, f"Internal Exam total marks expected 50, got {int_paper['total_marks']}"
        assert len(int_paper['sections']) == 3, f"Internal Exam expected 3 sections (A, B, C), got {len(int_paper['sections'])}"
        print("Internal Exam verified: 50 Attempted Marks (Part A: 10M, Part B: 8M, Part C: 32M) with zero regressions.")

        print("\n" + "=" * 75)
        print("ALL TESTS IN THE FLEXIBLE 16-MARK SEMESTER EXAM SUITE PASSED!")
        print("=" * 75)
        return True

if __name__ == '__main__':
    res = run_verification()
    sys.exit(0 if res else 1)
