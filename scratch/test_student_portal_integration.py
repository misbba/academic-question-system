import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app import app
from models.database import get_db_connection

class StudentPortalIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def login_student(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'nisha@vsb.com',
            'password': '12345678',
            'role': 'student'
        })
        self.assertEqual(res.status_code, 200, f"Student login failed: {res.get_json()}")
        return res.get_json()

    def login_faculty(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'muruga@vsb.com',
            'password': 'Password123!',
            'role': 'faculty'
        })
        self.assertEqual(res.status_code, 200, f"Faculty login failed: {res.get_json()}")
        return res.get_json()

    def logout(self):
        self.client.post('/api/auth/logout')

    # ==========================================================
    # TEST 1: REQUIREMENT 1 - MY SUBJECTS
    # ==========================================================
    def test_01_student_subjects_endpoint(self):
        print("\n--- TEST 1: Student Subjects Endpoint ---")
        self.login_student()
        res = self.client.get('/api/student/subjects')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        subjects = data.get('subjects', [])
        self.assertGreaterEqual(len(subjects), 3)

        sub_names = [s['name'] for s in subjects]
        print(f"Enrolled subjects found: {sub_names}")
        self.assertIn('Database Management Systems', sub_names)
        self.assertIn('Distributed Computing', sub_names)

        dc_sub = next(s for s in subjects if s['name'] == 'Distributed Computing')
        print(f"Distributed Computing counts: Materials={dc_sub['materials_count']}, Quizzes={dc_sub['quizzes_count']}, Papers={dc_sub['papers_count']}, Assignments={dc_sub['assignments_count']}")
        self.assertGreaterEqual(dc_sub['materials_count'], 1)
        self.assertGreaterEqual(dc_sub['quizzes_count'], 1)
        self.assertGreaterEqual(dc_sub['papers_count'], 1)
        self.logout()

    # ==========================================================
    # TEST 2: REQUIREMENT 2 - STUDY MATERIALS & FILE DOWNLOAD
    # ==========================================================
    def test_02_study_materials_view_and_download(self):
        print("\n--- TEST 2: Study Materials View & Download ---")
        self.login_student()
        # 1. Fetch materials list
        res = self.client.get('/api/resources?subject=Distributed Computing')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'success')
        resources = data.get('resources', [])
        self.assertGreaterEqual(len(resources), 1)

        # 2. Pick a resource that has a file
        res_with_file = next((r for r in resources if r.get('file_path')), None)
        self.assertIsNotNone(res_with_file, "At least one resource should have a file attached")
        print(f"Testing resource ID {res_with_file['id']}: {res_with_file['title']} | file_name: {res_with_file['file_name']}")

        # 3. Test GET /api/resources/<id>/file
        file_res = self.client.get(f"/api/resources/{res_with_file['id']}/file")
        self.assertEqual(file_res.status_code, 200, f"File download by ID failed: {file_res.status_code}")
        self.assertGreater(len(file_res.data), 0)
        print(f"Successfully retrieved {len(file_res.data)} bytes via /api/resources/{res_with_file['id']}/file")

        # 4. Test GET /api/resources/file/<filename> using original un-prefixed filename
        if res_with_file.get('file_name'):
            fname_res = self.client.get(f"/api/resources/file/{res_with_file['file_name']}")
            self.assertEqual(fname_res.status_code, 200, f"File download by original name failed: {fname_res.status_code}")
            self.assertGreater(len(fname_res.data), 0)
            print(f"Successfully retrieved {len(fname_res.data)} bytes via /api/resources/file/{res_with_file['file_name']}")

        self.logout()

    # ==========================================================
    # TEST 3: REQUIREMENT 3 - ASSIGNMENTS END-TO-END
    # ==========================================================
    def test_03_assignments_publish_and_student_submit(self):
        print("\n--- TEST 3: Assignments Faculty Publish & Student Submit ---")
        # 1. Faculty creates assignment
        self.login_faculty()
        create_res = self.client.post('/api/assignments', json={
            'title': 'Distributed Mutual Exclusion Proofs',
            'subject': 'Distributed Computing',
            'department': 'Artificial Intelligence & Data Science',
            'academic_year': '2025-2026',
            'semester': 'Semester 6',
            'unit': 'Unit II — Distributed Synchronization',
            'due_date': '2026-11-15',
            'total_marks': 20,
            'instructions': '1. Prove correctness of Ricart-Agrawala algorithm.\\n2. Compare message complexity against Lamport algorithm.',
            'questions': [
                {'text': 'Prove that Ricart-Agrawala algorithm achieves mutual exclusion without deadlock.', 'marks': 10, 'concept': 'Mutual Exclusion'},
                {'text': 'Compute total message traffic per critical section entry under peak load.', 'marks': 10, 'concept': 'Performance Analysis'}
            ],
            'status': 'Published'
        })
        self.assertEqual(create_res.status_code, 201, f"Assignment creation failed: {create_res.get_json()}")
        asn_id = create_res.get_json().get('id')
        self.assertIsNotNone(asn_id)
        print(f"Faculty published assignment ID: {asn_id}")
        self.logout()

        # 2. Student views assignment
        self.login_student()
        get_res = self.client.get('/api/assignments?subject=Distributed Computing')
        self.assertEqual(get_res.status_code, 200)
        asns = get_res.get_json().get('assignments', [])
        found_asn = next((a for a in asns if a['id'] == asn_id), None)
        self.assertIsNotNone(found_asn, "Student should see newly published assignment")
        self.assertFalse(found_asn.get('is_submitted'))
        print(f"Student successfully retrieved assignment: {found_asn['title']} (is_submitted={found_asn['is_submitted']})")

        # 3. Student submits assignment
        sub_res = self.client.post(f'/api/assignments/{asn_id}/submit', json={
            'submission_text': 'Q1: In Ricart-Agrawala algorithm, each request has a unique timestamp (T, i). Critical section permission is granted only when all other nodes reply...\\nQ2: Message complexity is 2*(N-1) messages per entry.'
        })
        self.assertEqual(sub_res.status_code, 200, f"Assignment submission failed: {sub_res.get_json()}")
        print("Student successfully submitted assignment solutions")

        # 4. Verify assignment status updated for student
        get_res_after = self.client.get('/api/assignments?subject=Distributed Computing')
        asns_after = get_res_after.get_json().get('assignments', [])
        found_asn_after = next((a for a in asns_after if a['id'] == asn_id), None)
        self.assertTrue(found_asn_after.get('is_submitted'), "Assignment status should now be is_submitted=True")
        print(f"Verified is_submitted: {found_asn_after.get('is_submitted')}, submitted_at: {found_asn_after.get('student_submitted_at')}")
        self.logout()

    # ==========================================================
    # TEST 4: REQUIREMENT 4 - QUIZZES TAKING & AUTO-EVALUATION
    # ==========================================================
    def test_04_quizzes_taking_and_persistence(self):
        print("\n--- TEST 4: Quizzes Taking & Scoring Persistence ---")
        self.login_student()
        # 1. Fetch published quizzes
        res = self.client.get('/api/quizzes?subject=Distributed Computing')
        self.assertEqual(res.status_code, 200)
        quizzes = res.get_json().get('quizzes', [])
        self.assertGreaterEqual(len(quizzes), 1)

        # Pick a quiz with questions
        quiz = next((q for q in quizzes if q.get('questions')), None)
        self.assertIsNotNone(quiz)
        print(f"Testing quiz ID {quiz['id']}: {quiz['title']}")

        # Verify questions can be parsed and options are not [object Object]
        qs = quiz['questions']
        if isinstance(qs, str):
            qs = json.loads(qs)
        self.assertGreaterEqual(len(qs), 1)
        for i, q in enumerate(qs):
            opts = q.get('options', [])
            for opt in opts:
                opt_str = str(opt)
                self.assertNotIn('[object Object]', opt_str)

        # 2. Submit quiz attempt via POST /api/quizzes/<id>/submit
        submit_res = self.client.post(f"/api/quizzes/{quiz['id']}/submit", json={
            'answers': {'0': 0, '1': 1, '2': 0}
        })
        self.assertIn(submit_res.status_code, [200, 201], f"Quiz submission failed: {submit_res.get_json()}")
        att = submit_res.get_json().get('attempt', {})
        self.assertIn('score', att)
        self.assertIn('percentage', att)
        print(f"Quiz auto-evaluated result: score={att['score']}, percentage={att['percentage']}")

        # 3. Test alias endpoint /api/quizzes/<id>/attempts
        alias_res = self.client.post(f"/api/quizzes/{quiz['id']}/attempts", json={
            'answers': {'0': 0}
        })
        self.assertIn(alias_res.status_code, [200, 201], f"Quiz attempt alias endpoint failed: {alias_res.get_json()}")

        # 4. Fetch attempt history
        hist_res = self.client.get('/api/quizzes/attempts')
        self.assertEqual(hist_res.status_code, 200)
        hist = hist_res.get_json().get('attempts', [])
        self.assertGreaterEqual(len(hist), 1)
        print(f"Student quiz history records: {len(hist)} attempts logged in MySQL")
        self.logout()

    # ==========================================================
    # TEST 5: REQUIREMENT 5 - QUESTION PAPERS WITH PART B EITHER/OR
    # ==========================================================
    def test_05_question_papers_full_display_including_part_b(self):
        print("\n--- TEST 5: Question Papers Full Display (Part A + Part B Either/Or) ---")
        self.login_student()
        # 1. Fetch published papers
        res = self.client.get('/api/question-papers?status=Published')
        self.assertEqual(res.status_code, 200)
        papers = res.get_json().get('question_papers', [])
        self.assertGreaterEqual(len(papers), 1)

        # 2. Pick Paper ID 28 (Distributed Computing End Semester Exam)
        paper28_res = self.client.get('/api/question-papers/28')
        self.assertEqual(paper28_res.status_code, 200)
        paper28 = paper28_res.get_json().get('paper') or paper28_res.get_json().get('question_paper')
        self.assertIsNotNone(paper28)

        secs = paper28.get('sections', [])
        if isinstance(secs, str):
            secs = json.loads(secs)

        self.assertGreaterEqual(len(secs), 2, "Semester examination paper should have at least Part A and Part B")
        sec_a = secs[0]
        sec_b = secs[1]

        # Part A verification
        self.assertGreaterEqual(len(sec_a.get('questions', [])), 10, "Part A should contain 10 questions")
        print(f"Part A verified: {len(sec_a['questions'])} compulsory questions")

        # Part B verification - Either/Or groups
        groups = sec_b.get('either_or_groups', [])
        self.assertEqual(len(groups), 5, "Part B should contain 5 Either/Or groups for 5 units")
        print(f"Part B verified: {len(groups)} Either/Or groups found")

        for i, grp in enumerate(groups):
            self.assertIn('alternative_a', grp, f"Group {i+1} must have alternative_a")
            self.assertIn('alternative_b', grp, f"Group {i+1} must have alternative_b")
            self.assertEqual(grp.get('attempted_marks'), 16, f"Group {i+1} attempted marks must be 16")

        print("All 5 Either/Or pairs (10 complete alternatives) validated with 80 marks total!")
        self.logout()

    # ==========================================================
    # TEST 6: REQUIREMENT 6 - PRESENTATIONS & LESSON PLANS
    # ==========================================================
    def test_06_presentations_and_lesson_plans_end_to_end(self):
        print("\n--- TEST 6: Presentations & Lesson Plans Faculty Publish & Student View ---")
        # 1. Faculty publishes presentation
        self.login_faculty()
        ppt_res = self.client.post('/api/presentations', json={
            'title': 'Lamport Timestamps & Clock Synchronization',
            'subject': 'Distributed Computing',
            'department': 'Artificial Intelligence & Data Science',
            'academic_year': '2025-2026',
            'semester': 'Semester 6',
            'unit': 'Unit I',
            'topic': 'Clock Synchronization',
            'slide_count': 12,
            'presentation_type': 'Classroom Teaching',
            'source_material': 'Distributed Computing Notes',
            'status': 'Published'
        })
        self.assertEqual(ppt_res.status_code, 201)
        ppt_id = ppt_res.get_json().get('id')

        # 2. Faculty publishes lesson plan
        lp_res = self.client.post('/api/lesson-plans', json={
            'title': 'Unit I Lesson Plan: Logical Clocks',
            'subject': 'Distributed Computing',
            'department': 'Artificial Intelligence & Data Science',
            'academic_year': '2025-2026',
            'semester': 'Semester 6',
            'unit': 'Unit I',
            'topic': 'Logical Clocks',
            'duration_minutes': 50,
            'teaching_method': 'Interactive Lecture & Whiteboard',
            'status': 'Published'
        })
        self.assertEqual(lp_res.status_code, 201)
        lp_id = lp_res.get_json().get('id')
        self.logout()

        # 3. Student views presentation
        self.login_student()
        get_ppt = self.client.get('/api/presentations?subject=Distributed Computing')
        self.assertEqual(get_ppt.status_code, 200)
        ppts = get_ppt.get_json().get('presentations', [])
        found_ppt = next((p for p in ppts if p['id'] == ppt_id), None)
        self.assertIsNotNone(found_ppt, "Student should retrieve published presentation")
        print(f"Student retrieved presentation: {found_ppt['title']}")

        # 4. Student views lesson plan
        get_lp = self.client.get('/api/lesson-plans?subject=Distributed Computing')
        self.assertEqual(get_lp.status_code, 200)
        lps = get_lp.get_json().get('lesson_plans', [])
        found_lp = next((l for l in lps if l['id'] == lp_id), None)
        self.assertIsNotNone(found_lp, "Student should retrieve published lesson plan")
        print(f"Student retrieved lesson plan: {found_lp['title']}")
        self.logout()

    # ==========================================================
    # TEST 7: SECURITY & ISOLATION
    # ==========================================================
    def test_07_role_isolation_and_unauthorized_access(self):
        print("\n--- TEST 7: Security & Role Isolation ---")
        # 1. Unauthenticated request to /api/student/subjects
        res = self.client.get('/api/student/subjects')
        self.assertEqual(res.status_code, 401)

        # 2. Student trying to create a resource (forbidden)
        self.login_student()
        res_post = self.client.post('/api/resources', json={'title': 'Hacker notes'})
        self.assertEqual(res_post.status_code, 403)

        # 3. Student trying to create a question paper (forbidden)
        paper_post = self.client.post('/api/question-papers', json={'title': 'Fake Paper'})
        self.assertEqual(paper_post.status_code, 403)
        self.logout()
        print("Role isolation verified: student forbidden from faculty write routes")

if __name__ == '__main__':
    unittest.main()
