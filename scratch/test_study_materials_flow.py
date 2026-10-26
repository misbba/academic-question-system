import os
import sys
import io
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app import app
from models.database import get_db_connection

class StudyMaterialsFocusedFlowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        cls.client = app.test_client()

    def login_faculty(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'muruga@vsb.com',
            'password': 'Password123!',
            'role': 'faculty'
        })
        self.assertEqual(res.status_code, 200, f"Faculty login failed: {res.get_json()}")
        return res.get_json()

    def login_student(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'nisha@vsb.com',
            'password': '12345678',
            'role': 'student'
        })
        self.assertEqual(res.status_code, 200, f"Student login failed: {res.get_json()}")
        return res.get_json()

    def logout(self):
        self.client.post('/api/auth/logout')

    def test_01_faculty_publish_and_student_load_materials(self):
        print("\n======================================================================")
        print("STEP 1: Faculty Uploads & Publishes Study Material")
        print("======================================================================")
        self.login_faculty()

        # Faculty uploads new resource file
        test_file_content = b"Distributed Consensus and State Machine Replication: Paxos and Raft algorithm workflows."
        data = {
            'subject': 'Distributed Computing',
            'department': 'Artificial Intelligence & Data Science',
            'academic_year': '2025-2026',
            'semester': 'Semester 6',
            'unit': 'Unit IV - Distributed Consensus',
            'topic': 'Raft and Paxos Consensus',
            'resource_type': 'Lecture Notes',
            'description': 'Comprehensive study notes on Raft election and Paxos phases.',
            'file': (io.BytesIO(test_file_content), 'Distributed_Consensus_Notes.txt')
        }

        upload_res = self.client.post('/api/resources', data=data, content_type='multipart/form-data')
        self.assertEqual(upload_res.status_code, 201, f"Resource upload failed: {upload_res.get_json()}")
        res_data = upload_res.get_json()
        new_resource = res_data.get('resource')
        self.assertIsNotNone(new_resource)
        new_id = new_resource['id']
        print(f"Faculty successfully uploaded new resource ID {new_id}: '{new_resource['title']}'")
        self.logout()

        print("\n======================================================================")
        print("STEP 2: Student Opens Study Materials Page (Calls GET /api/resources)")
        print("======================================================================")
        self.login_student()

        # Student calls exact endpoint used by studentMaterialsTable
        student_res = self.client.get('/api/resources')
        self.assertEqual(student_res.status_code, 200, f"Student GET /api/resources failed: {student_res.status_code}")
        payload = student_res.get_json()
        self.assertEqual(payload.get('status'), 'success')
        resources = payload.get('resources', [])
        print(f"Student successfully retrieved {len(resources)} published academic materials from MySQL!")
        self.assertGreaterEqual(len(resources), 1)

        # Verify newly created resource is in student's list
        found_new = next((r for r in resources if r['id'] == new_id), None)
        self.assertIsNotNone(found_new, "Newly published resource must appear in student's materials list")
        print(f"Found newly published resource in student view:")
        print(f"  - ID: {found_new['id']}")
        print(f"  - Subject: {found_new['subject']}")
        print(f"  - Unit: {found_new['unit']}")
        print(f"  - Topic: {found_new['topic']}")
        print(f"  - Resource Type: {found_new['resource_type']}")
        print(f"  - Title: {found_new['title']}")
        print(f"  - File Name: {found_new['file_name']}")
        print(f"  - Faculty: {found_new['faculty_name']}")
        print(f"  - Published Date: {found_new.get('created_at_str') or found_new.get('created_at')}")

        # Check required fields for frontend table rendering
        for col in ['subject', 'unit', 'topic', 'resource_type', 'title', 'file_name', 'faculty_name']:
            self.assertTrue(found_new.get(col), f"Column {col} must not be empty")

        print("\n======================================================================")
        print("STEP 3: Subject Filtering (e.g. ?subject=Distributed Computing)")
        print("======================================================================")
        filter_res = self.client.get('/api/resources?subject=Distributed Computing')
        self.assertEqual(filter_res.status_code, 200)
        filtered_list = filter_res.get_json().get('resources', [])
        for r in filtered_list:
            self.assertEqual(r['subject'], 'Distributed Computing')
        print(f"Subject filter 'Distributed Computing' returned {len(filtered_list)} matching items.")

        print("\n======================================================================")
        print("STEP 4: File Action - Download / Preview New & Existing Resources")
        print("======================================================================")
        # 1. Download newly uploaded file
        new_file_res = self.client.get(f'/api/resources/{new_id}/file')
        self.assertEqual(new_file_res.status_code, 200, f"Failed downloading newly uploaded file: {new_file_res.status_code}")
        self.assertEqual(new_file_res.data, test_file_content)
        print(f"Verified student file download for new resource ID {new_id} ({len(new_file_res.data)} bytes match exact content)")

        # 2. Download existing resource from earlier (ID 21: unit 3 dc.docx)
        existing_file_res = self.client.get('/api/resources/21/file')
        self.assertEqual(existing_file_res.status_code, 200, f"Failed downloading existing file: {existing_file_res.status_code}")
        self.assertGreater(len(existing_file_res.data), 1000)
        print(f"Verified student file download for existing resource ID 21 ({len(existing_file_res.data)} bytes)")

        # 3. Test download by original un-prefixed filename
        fname_res = self.client.get('/api/resources/file/Distributed_Consensus_Notes.txt')
        self.assertEqual(fname_res.status_code, 200)
        self.assertEqual(fname_res.data, test_file_content)
        print(f"Verified student file download by filename /api/resources/file/Distributed_Consensus_Notes.txt")

        self.logout()

        print("\n======================================================================")
        print("STEP 5: Unauthenticated Access Guard")
        print("======================================================================")
        unauth_res = self.client.get('/api/resources')
        self.assertEqual(unauth_res.status_code, 401)
        print("Unauthenticated request safely blocked with HTTP 401.")
        print("\nALL FOCUSED STUDY MATERIALS TESTS PASSED (100%)!")

if __name__ == '__main__':
    unittest.main()
