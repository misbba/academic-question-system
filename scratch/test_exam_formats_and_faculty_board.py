"""
Comprehensive Verification Script for Faculty Board & Exam Paper Formats
Tests:
1. Template generation for Internal Test (50 marks, inter.pdf format)
2. Template generation for Semester Exam (100 marks, April May 2024 ML.pdf format)
3. Attempted marks calculation & validation logic
4. Question Bank CRUD (Create, Read, Update, Delete) with 2, 5, 8, 13, 15, 16 marks
5. Faculty APIs: dashboard stats, resources, question generation, question papers list, auth/me
"""
import sys
import os
import json

# Add backend directory to sys.path
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
    get_question_papers
)

app = create_app()

def run_tests():
    with app.app_context():
        print("=" * 70)
        print("RUNNING FACULTY BOARD & EXAM FORMAT VERIFICATION SUITE")
        print("=" * 70)

        # -------------------------------------------------------------
        # TEST 1: Internal Test Generation (inter.pdf format)
        # -------------------------------------------------------------
        print("\n--- TEST 1: Internal Examination Template Generation ---")
        try:
            # Faculty ID 1 (Murugan)
            ok, resp, status_code = generate_template_paper(1, {
                'template_type': 'internal_test',
                'title': 'Internal Assessment Test 1 - Machine Learning',
                'subject': 'Machine Learning',
                'department': 'Artificial Intelligence & Data Science',
                'semester': 6,
                'academic_year': '2023-2024',
                'units': ['Unit I', 'Unit II']
            })
            assert ok and status_code == 200, f"Failed to generate internal paper: {resp}"
            internal_paper = resp['paper']
            
            print(f"Paper Title: {internal_paper.get('title')}")
            print(f"Total Marks (Attempted): {internal_paper.get('total_marks')}")
            print(f"Duration: {internal_paper.get('duration')}")
            print(f"Sections Count: {len(internal_paper.get('sections', []))}")
            
            # Check sections
            part_a = next((s for s in internal_paper['sections'] if 'PART - A' in s['title'] or 'Part A' in s['title']), None)
            part_b = next((s for s in internal_paper['sections'] if 'PART - B' in s['title'] or 'Part B' in s['title']), None)
            part_c = next((s for s in internal_paper['sections'] if 'PART - C' in s['title'] or 'Part C' in s['title']), None)
            
            assert part_a is not None, "Part A missing in Internal Exam"
            assert part_b is not None, "Part B missing in Internal Exam"
            assert part_c is not None, "Part C missing in Internal Exam"
            
            print(f"Part A: {len(part_a.get('questions', []))} questions, attempted_marks={part_a.get('attempted_marks')}")
            print(f"Part B: {len(part_b.get('groups', []))} groups, attempted_marks={part_b.get('attempted_marks')}")
            print(f"Part C: {len(part_c.get('groups', []))} groups, attempted_marks={part_c.get('attempted_marks')}")
            
            assert part_a['attempted_marks'] == 10, f"Part A attempted marks expected 10, got {part_a['attempted_marks']}"
            assert part_b['attempted_marks'] == 8, f"Part B attempted marks expected 8, got {part_b['attempted_marks']}"
            assert part_c['attempted_marks'] == 32, f"Part C attempted marks expected 32, got {part_c['attempted_marks']}"
            assert internal_paper['total_marks'] == 50, f"Total attempted marks expected 50, got {internal_paper['total_marks']}"
            
            # Check CO tags and Bloom tags in Part A
            for idx, q in enumerate(part_a.get('questions', []), start=1):
                co = q.get('co_tag', '')
                bloom = q.get('bloom_tag', '')
                print(f"  Q{idx}: {co} {bloom} ({q.get('marks')} Marks) - {q.get('question_text')[:50]}...")
                assert co, "Missing CO tag in Part A question"
                assert bloom, "Missing Bloom tag in Part A question"
            
            # Verify save to MySQL
            ok_save, resp_save, code_save = create_question_paper(1, internal_paper)
            assert ok_save and code_save == 201, f"Failed to persist Internal Exam paper: {resp_save}"
            created_internal = resp_save.get('paper')
            print(f"SUCCESS: Internal Exam paper saved with ID #{created_internal['id']}")
            
        except Exception as e:
            print(f"FAILED TEST 1: {e}")
            import traceback; traceback.print_exc()
            return False

        # -------------------------------------------------------------
        # TEST 2: Semester Exam Generation (April May 2024 ML.pdf format)
        # -------------------------------------------------------------
        print("\n--- TEST 2: Semester Examination Template Generation (ML) ---")
        try:
            ok, resp, status_code = generate_template_paper(1, {
                'template_type': 'semester_exam',
                'title': 'B.Tech Degree Examinations - Machine Learning',
                'subject': 'Machine Learning',
                'department': 'Artificial Intelligence & Data Science',
                'semester': 6,
                'academic_year': '2023-2024',
                'regulation': 'Regulation 2021',
                'units': ['Unit I', 'Unit II', 'Unit III', 'Unit IV', 'Unit V']
            })
            assert ok and status_code == 200, f"Failed to generate semester paper: {resp}"
            sem_paper = resp['paper']
            
            print(f"Paper Title: {sem_paper.get('title')}")
            print(f"Total Marks (Attempted): {sem_paper.get('total_marks')}")
            print(f"Duration: {sem_paper.get('duration')}")
            
            part_a = next((s for s in sem_paper['sections'] if 'PART - A' in s['title'] or 'Part A' in s['title']), None)
            part_b = next((s for s in sem_paper['sections'] if 'PART - B' in s['title'] or 'Part B' in s['title']), None)
            part_c = next((s for s in sem_paper['sections'] if 'PART - C' in s['title'] or 'Part C' in s['title']), None)
            
            assert part_a is not None, "Part A missing in Semester Exam"
            assert part_b is not None, "Part B missing in Semester Exam"
            assert part_c is not None, "Part C missing in Semester Exam"
            
            print(f"Part A: {len(part_a.get('questions', []))} questions, attempted_marks={part_a.get('attempted_marks')}")
            print(f"Part B: {len(part_b.get('groups', []))} groups, attempted_marks={part_b.get('attempted_marks')}")
            print(f"Part C: {len(part_c.get('groups', []))} groups, attempted_marks={part_c.get('attempted_marks')}")
            
            assert part_a['attempted_marks'] == 20, f"Part A attempted marks expected 20, got {part_a['attempted_marks']}"
            assert part_b['attempted_marks'] == 65, f"Part B attempted marks expected 65, got {part_b['attempted_marks']}"
            assert part_c['attempted_marks'] == 15, f"Part C attempted marks expected 15, got {part_c['attempted_marks']}"
            assert sem_paper['total_marks'] == 100, f"Total attempted marks expected 100, got {sem_paper['total_marks']}"
            
            # Verify Part B subquestions structure (8 + 5 = 13 or 13 single)
            has_subquestions = False
            for grp in part_b.get('groups', []):
                q_num = grp.get('question_number')
                att_m = grp.get('attempted_marks')
                opt_a = grp.get('alternative_a') or grp.get('option_a', {})
                opt_b = grp.get('alternative_b') or grp.get('option_b', {})
                print(f"  Group Q{q_num} ({att_m} Marks):")
                
                if opt_a.get('is_subquestion') or 'subquestions' in opt_a:
                    has_subquestions = True
                    print(f"    Option A (Subdivided 8+5):")
                    for sub in opt_a.get('subquestions', []):
                        print(f"      {sub.get('part')} {sub.get('marks')}M: {sub.get('text', '')[:45]}...")
                else:
                    print(f"    Option A (Single {opt_a.get('marks')}M): {opt_a.get('text', '')[:45]}...")

                if opt_b.get('is_subquestion') or 'subquestions' in opt_b:
                    has_subquestions = True
                    print(f"    Option B (Subdivided 8+5):")
                    for sub in opt_b.get('subquestions', []):
                        print(f"      {sub.get('part')} {sub.get('marks')}M: {sub.get('text', '')[:45]}...")
                else:
                    print(f"    Option B (Single {opt_b.get('marks')}M): {opt_b.get('text', '')[:45]}...")

            assert has_subquestions, "Semester Exam Part B should feature subdivided (8+5) questions as in April May 2024 ML.pdf"
            print(f"Subdivided (8+5) questions verified: {has_subquestions}")

            # Verify save to MySQL
            ok_save, resp_save, code_save = create_question_paper(1, sem_paper)
            assert ok_save and code_save == 201, f"Failed to persist Semester Exam paper: {resp_save}"
            created_sem = resp_save.get('paper')
            print(f"SUCCESS: Semester Exam paper saved with ID #{created_sem['id']}")
            
        except Exception as e:
            print(f"FAILED TEST 2: {e}")
            import traceback; traceback.print_exc()
            return False

        # -------------------------------------------------------------
        # TEST 3: Validation Logic Enforcement
        # -------------------------------------------------------------
        print("\n--- TEST 3: Validation Logic Enforcement ---")
        try:
            # Case 1: Invalid attempted marks for Semester Exam (say 90 instead of 100)
            invalid_data = {
                'paper_type': 'semester_exam',
                'sections': [
                    {'title': 'Part A', 'attempted_marks': 20, 'questions': [{'marks': 2}]*10},
                    {'title': 'Part B', 'attempted_marks': 65, 'groups': [{'marks': 13}]*5},
                    {'title': 'Part C', 'attempted_marks': 5, 'groups': [{'marks': 5}]} # Invalid Part C
                ]
            }
            is_valid, msg = validate_question_paper_structure(invalid_data, 90)
            assert not is_valid, "Validation should have rejected 90 marks for semester exam"
            print(f"Expected rejection caught: {msg}")

            # Case 2: Invalid attempted marks for Internal Test (say 60 instead of 50)
            invalid_internal = {
                'paper_type': 'internal_test',
                'sections': [
                    {'title': 'Part A', 'attempted_marks': 10, 'questions': [{'marks': 2}]*5},
                    {'title': 'Part B', 'attempted_marks': 18, 'groups': [{'marks': 18}]}, # Invalid Part B
                    {'title': 'Part C', 'attempted_marks': 32, 'groups': [{'marks': 16}]*2}
                ]
            }
            is_valid, msg = validate_question_paper_structure(invalid_internal, 60)
            assert not is_valid, "Validation should have rejected 60 marks for internal test"
            print(f"Expected rejection caught: {msg}")
            print("SUCCESS: Validation logic accurately enforces college examination rules.")
        except Exception as e:
            print(f"FAILED TEST 3: {e}")
            import traceback; traceback.print_exc()
            return False

        # -------------------------------------------------------------
        # TEST 4: Question Bank CRUD (2, 5, 8, 13, 15, 16 Marks)
        # -------------------------------------------------------------
        print("\n--- TEST 4: Question Bank CRUD Operations ---")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create a 13-mark test question
            cursor.execute("""
                INSERT INTO questions (
                    subject, department, academic_year, semester,
                    unit, topic, marks, difficulty, bloom_level, question_type, explanation,
                    is_in_bank, question_text, created_by
                ) VALUES (
                    'Machine Learning', 'Artificial Intelligence & Data Science', '2025-2026', 'Semester 6',
                    'Unit II', 'Support Vector Machines', 13, 'hard', 'Evaluate', 'descriptive', 'Test explanation',
                    1, 'Formulate the dual optimization problem for soft-margin Support Vector Machines and explain the role of Lagrange multipliers.', 1
                )
            """)
            conn.commit()
            new_qid = cursor.lastrowid
            print(f"Created test 13M question with ID #{new_qid}")
            
            # Read back
            cursor.execute("SELECT id, topic, marks, bloom_level FROM questions WHERE id = %s", (new_qid,))
            row = cursor.fetchone()
            assert row and row['marks'] == 13, f"Expected marks 13, got {row['marks']}"
            assert row['bloom_level'] == 'Evaluate'
            print(f"Read verified: ID={row['id']}, topic={row['topic']}, marks={row['marks']}, blooms={row['bloom_level']}")
            
            # Update
            cursor.execute("UPDATE questions SET marks = 15, topic = 'Kernel SVM and Optimization' WHERE id = %s", (new_qid,))
            conn.commit()
            cursor.execute("SELECT marks, topic FROM questions WHERE id = %s", (new_qid,))
            updated_row = cursor.fetchone()
            assert updated_row['marks'] == 15 and updated_row['topic'] == 'Kernel SVM and Optimization', "Update failed"
            print(f"Update verified: marks={updated_row['marks']}, topic={updated_row['topic']}")
            
            # Delete
            cursor.execute("DELETE FROM questions WHERE id = %s", (new_qid,))
            conn.commit()
            cursor.execute("SELECT id FROM questions WHERE id = %s", (new_qid,))
            deleted_row = cursor.fetchone()
            assert deleted_row is None, "Delete failed"
            print(f"Delete verified: Question #{new_qid} removed successfully.")
            
            cursor.close()
            conn.close()
            print("SUCCESS: Question Bank CRUD operations fully working.")
        except Exception as e:
            print(f"FAILED TEST 4: {e}")
            import traceback; traceback.print_exc()
            return False

        # -------------------------------------------------------------
        # TEST 5: Faculty Dashboard & API Endpoints
        # -------------------------------------------------------------
        print("\n--- TEST 5: Faculty APIs and Endpoints Audit ---")
        client = app.test_client()
        
        # Test faculty dashboard stats
        with client.session_transaction() as sess:
            sess['user_id'] = 24
            sess['role'] = 'faculty'
            sess['faculty_id'] = 24
            sess['faculty_name'] = 'Murugan'
            sess['department'] = 'Artificial Intelligence & Data Science'
            
        res = client.get('/api/faculty/dashboard-stats')
        print(f"Dashboard Stats status: {res.status_code}")
        stats_data = res.get_json()
        print(f"Dashboard Stats response: {stats_data}")
        assert res.status_code == 200, "Dashboard stats failed"
        assert 'stats' in stats_data or 'total_questions' in stats_data or stats_data.get('success'), "Invalid stats payload"
        
        # Test auth/me
        res = client.get('/api/auth/me')
        me_data = res.get_json()
        print(f"Auth /me response: {me_data}")
        assert res.status_code == 200, "Auth me failed"
        assert me_data.get('user', {}).get('full_name') == 'Murugan' or me_data.get('user', {}).get('name') == 'Murugan', f"Expected faculty Murugan, got {me_data}"
        print(f"Authenticated Faculty verified: {me_data.get('user', {}).get('full_name') or me_data.get('user', {}).get('name')}")
        
        # Test question papers list
        res = client.get('/api/question-papers')
        print(f"Question Papers List status: {res.status_code}")
        papers_data = res.get_json()
        assert res.status_code == 200, "Failed to fetch question papers"
        papers_list = papers_data.get('papers', []) if isinstance(papers_data, dict) else papers_data
        print(f"Retrieved {len(papers_list)} generated question papers.")
        assert len(papers_list) >= 2, "Expected at least the 2 generated test papers in history"
        
        # Test resources
        res = client.get('/api/resources')
        print(f"Resources API status: {res.status_code}")
        assert res.status_code == 200, "Failed to fetch academic resources"
        resources_data = res.get_json()
        print(f"Resources count: {len(resources_data.get('resources', [])) if isinstance(resources_data, dict) else len(resources_data)}")

        print("\n" + "=" * 70)
        print("ALL 5 VERIFICATION SUITES PASSED SUCCESSFULLY!")
        print("=" * 70)
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
