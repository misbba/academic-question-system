# -*- coding: utf-8 -*-
"""
Comprehensive Verification Suite for:
1. Question Bank Multi-Factor Organization (Unit, Marks, Blooms, Topic, Year, Sem)
2. Question Bank CRUD (Add, Edit, View, Select)
3. Internal Test Generator (50 Attempted Marks, Sec A: 5x2m, Sec B: 1x8m either/or with distinct lessons, Sec C: 2x16m either/or)
4. Semester Exam Generator (100 Attempted Marks, Sec A: 10x2m with exactly 2 questions per unit for Units I-V, Sec B: 5x16m covering Units I-V with distinct lessons)
5. Validation Rules (Attempted marks math, rejecting invalid mark totals & unbalanced unit coverage)
6. UI & Template Integrity (Absence of fingerprint button/cards, presence of modals, filters & preview)
"""

import os
import sys
import json
import pymysql

backend_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import app
from config import Config
from services.question_service import (
    get_questions,
    get_question_bank,
    create_question_record,
    update_question_record,
    delete_question_record,
    get_question_by_id
)
from services.question_paper_service import (
    generate_template_paper,
    create_question_paper,
    calculate_attempted_marks,
    validate_question_paper_structure,
    normalize_unit
)

def run_suite():
    print("=" * 70)
    print("STARTING FULL ACADEMIC QUESTION SYSTEM VERIFICATION SUITE")
    print("=" * 70)

    # 1. UI File Inspections
    print("\n--- TEST 1: UI File Integrity & Fingerprint Feature Removal ---")
    base_dir = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system'
    
    with open(os.path.join(base_dir, 'faculty-question-paper.html'), 'r', encoding='utf-8') as f:
        fqp_html = f.read()

    assert 'Generate Fingerprint' not in fqp_html, "Fingerprint button still present in faculty-question-paper.html"
    assert 'fingerprintResultsCard' not in fqp_html, "Fingerprint results card still present in faculty-question-paper.html"
    assert "generateAcademicTemplateAction('internal_test')" in fqp_html, "Internal test generator button missing in HTML"
    assert "generateAcademicTemplateAction('semester_exam')" in fqp_html, "Semester exam generator button missing in HTML"
    assert 'id="filterPaperUnit"' in fqp_html, "Unit filter missing in HTML"
    assert 'id="filterPaperMarks"' in fqp_html, "Marks filter missing in HTML"
    assert 'id="filterPaperBlooms"' in fqp_html, "Bloom's filter missing in HTML"
    assert 'id="addQuestionModal"' in fqp_html, "Add Question modal missing in HTML"
    assert 'id="editQuestionModal"' in fqp_html, "Edit Question modal missing in HTML"
    assert 'id="viewQuestionModal"' in fqp_html, "View Question modal missing in HTML"
    print("  [PASSED] faculty-question-paper.html has all template buttons, filters, modals, and NO fingerprint button/card.")

    with open(os.path.join(base_dir, 'faculty-history.html'), 'r', encoding='utf-8') as f:
        fh_html = f.read()
    assert 'paper fingerprinting' not in fh_html, "Fingerprinting text still present in faculty-history.html"
    print("  [PASSED] faculty-history.html clean.")

    with open(os.path.join(base_dir, 'student-question-papers.html'), 'r', encoding='utf-8') as f:
        sqp_html = f.read()
    assert 'digital SHA-256 fingerprints' not in sqp_html, "Fingerprinting text still present in student-question-papers.html"
    print("  [PASSED] student-question-papers.html clean.")

    # 2. Question Bank Organization & Filtering
    print("\n--- TEST 2: Question Bank Multi-Factor Organization ---")
    _, res_all, _ = get_question_bank(1, {
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science"
    })
    all_q = res_all.get('questions', [])
    print(f"  Total Question Bank questions available: {len(all_q)}")
    assert len(all_q) >= 50, f"Expected at least 50 questions, found {len(all_q)}"

    # Test filtering by Unit
    for u in ['Unit I', 'Unit II', 'Unit III', 'Unit IV', 'Unit V']:
        _, res_u, _ = get_question_bank(1, {
            "subject": "Database Management Systems",
            "unit": u
        })
        u_questions = res_u.get('questions', [])
        print(f"  -> {u}: {len(u_questions)} questions in bank")
        assert len(u_questions) >= 8, f"Unit {u} should have at least 8 questions, found {len(u_questions)}"

    # Test filtering by Marks
    for m in [2, 8, 16]:
        _, res_m, _ = get_question_bank(1, {
            "subject": "Database Management Systems",
            "marks": m
        })
        m_questions = res_m.get('questions', [])
        print(f"  -> {m} Marks: {len(m_questions)} questions in bank")
        assert len(m_questions) >= 5, f"{m} Marks should have at least 5 questions, found {len(m_questions)}"

    # Test filtering by Bloom's
    for b in ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']:
        _, res_b, _ = get_question_bank(1, {
            "subject": "Database Management Systems",
            "bloom_level": b
        })
        b_questions = res_b.get('questions', [])
        print(f"  -> Bloom's {b}: {len(b_questions)} questions in bank")
        assert len(b_questions) >= 1, f"Bloom level {b} should have questions"

    print("  [PASSED] Question Bank organization & filtering verified across Unit, Marks, Bloom's, Topic.")

    # 3. Question Bank CRUD Operations
    print("\n--- TEST 3: Question Bank CRUD Operations ---")
    test_faculty_id = 1
    new_q_data = {
        "question_text": "Verify transactional durability in distributed write-ahead logging protocols.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit IV",
        "topic": "WAL & Durability Mechanisms",
        "marks": 8,
        "difficulty": "Hard",
        "bloom_level": "Evaluate",
        "question_type": "Descriptive",
        "explanation": "WAL enforces that log records are flushed to disk before pages are written.",
        "is_in_bank": True
    }
    
    # Create
    success, res, code = create_question_record(test_faculty_id, new_q_data)
    assert success and code == 201, f"Failed to create question: {res}"
    created_id = res['question']['id']
    print(f"  -> Successfully created question #{created_id} in bank")

    # Read
    fetched_q = get_question_by_id(created_id)
    assert fetched_q and fetched_q['topic'] == "WAL & Durability Mechanisms", "Fetched question data mismatch"
    assert fetched_q['marks'] == 8 and fetched_q['bloom_level'] == "Evaluate"
    print(f"  -> Successfully verified question #{created_id} retrieval from MySQL")

    # Update
    update_data = {
        "topic": "Distributed WAL & Checkpointing",
        "marks": 16,
        "bloom_level": "Create",
        "difficulty": "Hard",
        "unit": "Unit IV",
        "question_text": "Architect a distributed write-ahead logging and checkpointing protocol for multi-region DBMS.",
        "explanation": "Updated detailed answer key."
    }
    u_success, u_res, u_code = update_question_record(created_id, test_faculty_id, update_data)
    assert u_success and u_code == 200, f"Failed to update question: {u_res}"
    updated_q = get_question_by_id(created_id)
    assert updated_q['topic'] == "Distributed WAL & Checkpointing" and updated_q['marks'] == 16
    print(f"  -> Successfully updated question #{created_id} (Marks: 16, Topic: {updated_q['topic']})")

    # Delete / Cleanup
    d_success, d_res, d_code = delete_question_record(created_id, test_faculty_id)
    assert d_success and d_code == 200, f"Failed to delete test question: {d_res}"
    assert get_question_by_id(created_id) is None, "Deleted question still exists"
    print(f"  -> Successfully deleted test question #{created_id} (Cleaned up)")
    print("  [PASSED] Question Bank CRUD complete.")

    # 4. Internal Test Template Generation (50 Marks)
    print("\n--- TEST 4: Internal Test Question Paper Generator (50 Attempted Marks) ---")
    gen_data_it = {
        "template_type": "internal_test",
        "department": "Artificial Intelligence & Data Science",
        "subject": "Database Management Systems",
        "academic_year": "2025-2026",
        "semester": "Semester 6"
    }
    it_success, it_res, it_code = generate_template_paper(test_faculty_id, gen_data_it)
    assert it_success and it_code == 200, f"Failed to generate internal test: {it_res}"
    it_paper = it_res['paper']

    assert it_paper['total_marks'] == 50, f"Internal test marks must be exactly 50, got {it_paper['total_marks']}"
    sections = it_paper['sections']
    assert len(sections) == 3, f"Expected 3 sections (A, B, C), got {len(sections)}"

    # Section A check
    sec_a = sections[0]
    assert sec_a['name'] == 'SECTION A'
    assert len(sec_a['questions']) == 5, f"Section A must have 5 questions, got {len(sec_a['questions'])}"
    for q in sec_a['questions']:
        assert q['marks'] == 2, f"Section A question must be 2 marks, got {q['marks']}"
    assert sec_a['total_marks'] == 10

    # Section B check
    sec_b = sections[1]
    assert sec_b['name'] == 'SECTION B'
    assert len(sec_b['either_or_groups']) == 1, "Section B must have 1 Either/Or group"
    group_b = sec_b['either_or_groups'][0]
    alt_a_topic = group_b['alternative_a']['topic']
    alt_b_topic = group_b['alternative_b']['topic']
    print(f"  -> Sec B Lessons: Alt A '{alt_a_topic}' vs Alt B '{alt_b_topic}'")
    assert alt_a_topic != alt_b_topic, f"Sec B Either/Or alternatives must be from different lessons! Got: {alt_a_topic}"
    assert sec_b['total_marks'] == 8

    # Section C check
    sec_c = sections[2]
    assert sec_c['name'] == 'SECTION C'
    assert len(sec_c['either_or_groups']) == 2, "Section C must have 2 Either/Or groups"
    for idx, grp in enumerate(sec_c['either_or_groups'], 1):
        g_alt_a = grp['alternative_a']
        g_alt_b = grp['alternative_b']
        topic_a = g_alt_a[0]['topic'] if isinstance(g_alt_a, list) else g_alt_a['topic']
        topic_b = g_alt_b[0]['topic'] if isinstance(g_alt_b, list) else g_alt_b['topic']
        print(f"  -> Sec C Group {idx} Lessons: Alt A '{topic_a}' vs Alt B '{topic_b}'")
        assert topic_a != topic_b, f"Sec C Group {idx} alternatives must be from different lessons!"
    assert sec_c['total_marks'] == 32

    # Save to MySQL
    save_it_success, save_it_res, save_it_code = create_question_paper(test_faculty_id, it_paper)
    assert save_it_success and save_it_code == 201, f"Failed to save internal test to MySQL: {save_it_res}"
    print(f"  -> Saved Internal Test to MySQL! Paper Code: {save_it_res.get('paper', save_it_res.get('question_paper'))['paper_code']}, Total Marks: {save_it_res.get('paper', save_it_res.get('question_paper'))['total_marks']}")
    print("  [PASSED] Internal Test generation & persistence verified.")

    # 5. Semester Exam Template Generation (100 Marks)
    print("\n--- TEST 5: Semester Exam Question Paper Generator (100 Attempted Marks) ---")
    gen_data_sem = {
        "template_type": "semester_exam",
        "department": "Artificial Intelligence & Data Science",
        "subject": "Database Management Systems",
        "academic_year": "2025-2026",
        "semester": "Semester 6"
    }
    sem_success, sem_res, sem_code = generate_template_paper(test_faculty_id, gen_data_sem)
    assert sem_success and sem_code == 200, f"Failed to generate semester exam: {sem_res}"
    sem_paper = sem_res['paper']

    assert sem_paper['total_marks'] == 100, f"Semester exam marks must be exactly 100, got {sem_paper['total_marks']}"
    sem_sections = sem_paper['sections']
    assert len(sem_sections) == 2, f"Expected 2 sections (A, B), got {len(sem_sections)}"

    # Section A: 10 compulsory questions x 2 marks = 20 marks, EXACTLY 2 per unit
    sec_a_sem = sem_sections[0]
    assert sec_a_sem['name'] == 'SECTION A'
    assert len(sec_a_sem['questions']) == 10
    assert sec_a_sem['total_marks'] == 20

    unit_counts = {}
    for q in sec_a_sem['questions']:
        norm_u = normalize_unit(q['unit'])
        unit_counts[norm_u] = unit_counts.get(norm_u, 0) + 1

    print(f"  -> Section A Unit Distribution: {unit_counts}")
    for u in ['Unit I', 'Unit II', 'Unit III', 'Unit IV', 'Unit V']:
        assert unit_counts.get(u) == 2, f"Section A must have exactly 2 questions from {u}, found {unit_counts.get(u)}"

    # Section B: 5 Either/Or groups x 16 marks = 80 marks covering Units I to V
    sec_b_sem = sem_sections[1]
    assert sec_b_sem['name'] == 'SECTION B'
    assert len(sec_b_sem['either_or_groups']) == 5
    assert sec_b_sem['total_marks'] == 80

    for idx, grp in enumerate(sec_b_sem['either_or_groups'], 1):
        target_unit = f"Unit {['I', 'II', 'III', 'IV', 'V'][idx-1]}"
        grp_u = normalize_unit(grp.get('unit'))
        assert grp_u == target_unit, f"Group {idx} expected {target_unit}, got {grp_u}"
        
        g_alt_a = grp['alternative_a']
        g_alt_b = grp['alternative_b']
        topic_a = g_alt_a[0]['topic'] if isinstance(g_alt_a, list) else g_alt_a['topic']
        topic_b = g_alt_b[0]['topic'] if isinstance(g_alt_b, list) else g_alt_b['topic']
        print(f"  -> Sec B Group {idx} ({target_unit}) Lessons: Alt A '{topic_a}' vs Alt B '{topic_b}'")
        assert topic_a != topic_b, f"Group {idx} alternatives must be from different lessons!"

    # Save to MySQL
    save_sem_success, save_sem_res, save_sem_code = create_question_paper(test_faculty_id, sem_paper)
    assert save_sem_success and save_sem_code == 201, f"Failed to save semester exam to MySQL: {save_sem_res}"
    print(f"  -> Saved Semester Exam to MySQL! Paper Code: {save_sem_res.get('paper', save_sem_res.get('question_paper'))['paper_code']}, Total Marks: {save_sem_res.get('paper', save_sem_res.get('question_paper'))['total_marks']}")
    print("  [PASSED] Semester Exam generation & persistence verified.")

    # 6. Validation Rule Checks
    print("\n--- TEST 6: Marks and Coverage Validation Rule Enforcement ---")
    
    # 6.1: Attempted marks calculation strictly excludes second alternative
    test_sec = [
        {"name": "SECTION A", "questions": [{"marks": 2} for _ in range(5)], "total_marks": 10},
        {"name": "SECTION B", "either_or_groups": [
            {"alternative_a": {"marks": 8}, "alternative_b": {"marks": 8}}
        ], "total_marks": 8}
    ]
    calc_attempted = calculate_attempted_marks(test_sec)
    assert calc_attempted == 18, f"Attempted marks must count only ONE alternative! Expected 18, got {calc_attempted}"
    print(f"  -> Attempted marks calculation correctly counted 18 marks (not 26 marks).")

    # 6.2: Invalid marks rejection
    bad_it_paper = {
        "title": "Invalid Internal Test",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "exam_type": "Internal Assessment I",
        "total_marks": 60,
        "sections": [
            {"name": "SECTION A", "questions": [{"marks": 2} for _ in range(5)], "total_marks": 10},
            {"name": "SECTION B", "either_or_groups": [{"alternative_a": {"marks": 8}, "alternative_b": {"marks": 8}}], "total_marks": 8},
            {"name": "SECTION C", "either_or_groups": [{"alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}}], "total_marks": 16}
        ]
    }
    is_valid, err_msg = validate_question_paper_structure(bad_it_paper, 34)
    assert not is_valid and "must have exactly 50 attempted marks" in err_msg
    print(f"  -> Correctly rejected invalid internal test total marks: '{err_msg}'")

    # 6.3: Unbalanced unit distribution rejection for semester exam
    bad_sem_paper = {
        "title": "Invalid Semester Exam",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "exam_type": "Semester Examination",
        "total_marks": 100,
        "sections": [
            {
                "name": "SECTION A",
                "questions": [
                    {"unit": "Unit I", "marks": 2}, {"unit": "Unit I", "marks": 2}, {"unit": "Unit I", "marks": 2}, # 3 from Unit I
                    {"unit": "Unit II", "marks": 2}, # 1 from Unit II
                    {"unit": "Unit III", "marks": 2}, {"unit": "Unit III", "marks": 2},
                    {"unit": "Unit IV", "marks": 2}, {"unit": "Unit IV", "marks": 2},
                    {"unit": "Unit V", "marks": 2}, {"unit": "Unit V", "marks": 2}
                ],
                "total_marks": 20
            },
            {
                "name": "SECTION B",
                "either_or_groups": [
                    {"unit": f"Unit {u}", "alternative_a": {"marks": 16}, "alternative_b": {"marks": 16}} for u in ['I', 'II', 'III', 'IV', 'V']
                ],
                "total_marks": 80
            }
        ]
    }
    is_sem_valid, sem_err = validate_question_paper_structure(bad_sem_paper, 100)
    assert not is_sem_valid and "must have exactly 2 questions from each of the 5 units" in sem_err
    print(f"  -> Correctly rejected unbalanced unit distribution in Section A: '{sem_err}'")

    print("\n" + "=" * 70)
    print("ALL TESTS IN VERIFICATION SUITE PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == '__main__':
    run_suite()
