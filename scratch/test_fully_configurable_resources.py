import urllib.request
import urllib.parse
import json
import sys
import time

BASE_URL = "http://localhost:5000"

class APISession:
    def __init__(self):
        self.cookie = None

    def request(self, method, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.cookie:
            headers["Cookie"] = self.cookie

        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                set_cookie = resp.headers.get("Set-Cookie")
                if set_cookie:
                    self.cookie = set_cookie.split(";")[0]
                status = resp.status
                res_data = resp.read().decode("utf-8")
                return status, json.loads(res_data) if res_data else {}
        except urllib.error.HTTPError as e:
            res_data = e.read().decode("utf-8")
            try:
                parsed = json.loads(res_data)
            except Exception:
                parsed = {"error": res_data}
            return e.code, parsed


def run_tests():
    print("=" * 75)
    print("ACADEMIC RESOURCES FULL CONFIGURABILITY VERIFICATION SUITE")
    print("=" * 75)

    client = APISession()

    # 1. Register a NEW faculty member with a BRAND NEW DEPARTMENT
    new_email = f"priya.robotics.{int(time.time())}@university.edu"
    new_dept = "Robotics & Automation Engineering"
    
    status, reg_res = client.request("POST", "/api/auth/register", {
        "full_name": "Dr. Priya Sharma",
        "email": new_email,
        "password": "Password123!",
        "role": "faculty",
        "department": new_dept
    })
    assert status == 201, f"Faculty registration with new department failed: {reg_res}"
    print(f"[PASS] 1. Registered new faculty with custom department '{new_dept}': {reg_res.get('user', {}).get('full_name')}")

    # 2. Login as the newly registered faculty member
    status, login_res = client.request("POST", "/api/auth/login", {
        "email": new_email,
        "password": "Password123!",
        "role": "faculty"
    })
    assert status == 200, f"Login failed: {login_res}"
    user_id = login_res.get("user", {}).get("id")
    print(f"[PASS] 2. Logged in as Dr. Priya Sharma (ID {user_id})")

    # 3. Test Workflow A: New Subject + New Dept + "All Units (Complete Syllabus)"
    subject_a = "Kinematics & Dynamics of Robot Manipulators"
    topic_a = "Denavit-Hartenberg Parameters and Forward Kinematics"
    unit_a = "All Units (Complete Syllabus)"
    
    payload_a = {
        "subject": subject_a,
        "department": new_dept,
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": unit_a,
        "topic": topic_a,
        "resource_type": "Syllabus",
        "description": "Full curriculum guidelines for 6-DOF industrial robotic arms."
    }
    
    status, res_a = client.request("POST", "/api/resources", payload_a)
    assert status in [200, 201], f"Failed to save Resource A: {res_a}"
    r_a = res_a.get("resource", {})
    id_a = r_a.get("id")
    assert id_a is not None, "Missing resource ID"
    print(f"[PASS] 3. Created Resource #{id_a} with 'All Units (Complete Syllabus)' and new subject '{subject_a}'")

    # 4. Verify reopen of Resource A (confirm EVERY field retains its value)
    status, view_a = client.request("GET", f"/api/resources/{id_a}")
    assert status == 200, f"Failed to reopen Resource A: {view_a}"
    data_a = view_a.get("resource", {})
    assert data_a.get("subject") == subject_a, f"Subject mismatch: {data_a.get('subject')}"
    assert data_a.get("department") == new_dept, f"Department mismatch: {data_a.get('department')}"
    assert data_a.get("unit") == unit_a, f"Unit mismatch: {data_a.get('unit')}"
    assert data_a.get("topic") == topic_a, f"Topic mismatch: {data_a.get('topic')}"
    assert data_a.get("resource_type") == "Syllabus"
    assert data_a.get("academic_year") == "2025-2026"
    assert data_a.get("semester") == "Semester 6"
    assert "DBMS" not in data_a.get("title") and "SQL" not in data_a.get("title")
    print(f"[PASS] 4. Reopened Resource #{id_a}: All fields verified intact with exact values")

    # 5. Test Workflow B: New Subject + Another New Dept + Individual Unit ("Unit III")
    subject_b = "Biomedical Signal Processing & Neural Interfaces"
    dept_b = "Biomedical Engineering & Bio-Informatics"
    unit_b = "Unit III"
    topic_b = "ECG Wavelet Decomposition and QRS Feature Detection"
    
    payload_b = {
        "subject": subject_b,
        "department": dept_b,
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": unit_b,
        "topic": topic_b,
        "resource_type": "Study Material",
        "description": "Lecture notes and filter specifications for cardiac telemetry."
    }
    
    status, res_b = client.request("POST", "/api/resources", payload_b)
    assert status in [200, 201], f"Failed to save Resource B: {res_b}"
    r_b = res_b.get("resource", {})
    id_b = r_b.get("id")
    print(f"[PASS] 5. Created Resource #{id_b} with individual unit '{unit_b}' and department '{dept_b}'")

    # 6. Verify reopen of Resource B
    status, view_b = client.request("GET", f"/api/resources/{id_b}")
    assert status == 200
    data_b = view_b.get("resource", {})
    assert data_b.get("subject") == subject_b
    assert data_b.get("department") == dept_b
    assert data_b.get("unit") == unit_b
    assert data_b.get("topic") == topic_b
    print(f"[PASS] 6. Reopened Resource #{id_b}: Verified individual unit '{unit_b}' and custom department '{dept_b}'")

    # 7. Test Content Analysis - must be dynamic and appropriate to the subject, not SQL/DBMS
    status, ana_a = client.request("POST", f"/api/resources/{id_a}/analyze")
    assert status == 200, f"Analysis failed: {ana_a}"
    analysis_data = ana_a.get("analysis", {})
    breakdown = analysis_data.get("units_breakdown", [])
    assert len(breakdown) == 5, f"Expected 5 units for All Units, got {len(breakdown)}"
    # Verify no hardcoded DBMS / SQL in the breakdown
    breakdown_text = json.dumps(breakdown)
    assert "DBMS Architecture" not in breakdown_text, "Found hardcoded DBMS Architecture!"
    assert "Relational Queries" not in breakdown_text, "Found hardcoded Relational Queries!"
    assert subject_a in breakdown[0]["unit_name"], f"Subject not reflected in unit 1 name: {breakdown[0]['unit_name']}"
    print(f"[PASS] 7. Content analysis dynamically generated for '{subject_a}' (No DBMS/SQL hardcoding)")

    # 8. Test Editing Resource (change subject, department, unit, and topic)
    edited_subject = "Autonomous Mobile Robots & SLAM Navigation"
    edited_topic = "Extended Kalman Filter SLAM and Occupancy Grids"
    edited_unit = "Unit IV"
    
    edit_payload = {
        "subject": edited_subject,
        "department": new_dept,
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": edited_unit,
        "topic": edited_topic,
        "resource_type": "PDF",
        "description": "Updated navigation algorithms notes."
    }
    status, edit_res = client.request("PUT", f"/api/resources/{id_a}", edit_payload)
    assert status == 200, f"Failed to edit resource: {edit_res}"
    status, view_edited = client.request("GET", f"/api/resources/{id_a}")
    data_edited = view_edited.get("resource", {})
    assert data_edited.get("subject") == edited_subject
    assert data_edited.get("unit") == edited_unit
    assert data_edited.get("topic") == edited_topic
    print(f"[PASS] 8. Successfully edited Resource #{id_a} to '{edited_subject}', unit '{edited_unit}', topic '{edited_topic}'")

    # 9. Clean up test records
    client.request("DELETE", f"/api/resources/{id_a}")
    client.request("DELETE", f"/api/resources/{id_b}")
    print(f"[PASS] 9. Cleaned up test resources #{id_a} and #{id_b}")

    # 10. Verify existing faculty resources (Murugan) still work seamlessly
    client_m = APISession()
    status, _ = client_m.request("POST", "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert status == 200
    status, m_res = client_m.request("GET", "/api/resources")
    assert status == 200
    m_list = m_res.get("resources", [])
    assert len(m_list) > 0, "Murugan existing resources disappeared!"
    print(f"[PASS] 10. Verified existing resources for Murugan are intact ({len(m_list)} resources found)")

    # Logout
    client.request("POST", "/api/auth/logout")
    client_m.request("POST", "/api/auth/logout")

    print("=" * 75)
    print("ALL 10 VERIFICATION TESTS COMPLETED SUCCESSFULLY! (100%)")
    print("=" * 75)

if __name__ == "__main__":
    run_tests()
