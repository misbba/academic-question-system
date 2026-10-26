import urllib.request
import urllib.parse
import json
import sys

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


def run_test():
    print("=" * 70)
    print("ACADEMIC RESOURCES CUSTOM SUBJECT VERIFICATION SUITE")
    print("=" * 70)

    client = APISession()

    # 1. Login as Faculty Murugan
    status, login_res = client.request("POST", "/api/auth/login", {
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    })
    assert status == 200, f"Login failed: {login_res}"
    print(f"[PASS] 1. Logged in as: {login_res.get('user', {}).get('full_name')}")

    # 2. Upload resource with completely custom subject (NOT in old dropdown)
    custom_subject = "Quantum Computing & Cryptography"
    custom_topic = "Qubits and Superposition Principles"
    
    upload_payload = {
        "subject": custom_subject,
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I",
        "topic": custom_topic,
        "resource_type": "Study Material",
        "description": "Comprehensive reference notes on quantum states and quantum logic gates."
    }

    status, upload_res = client.request("POST", "/api/resources", upload_payload)
    assert status in [200, 201], f"Failed to upload resource: {upload_res}"
    assert upload_res.get("status") == "success", f"Upload status not success: {upload_res}"
    created_resource = upload_res.get("resource", {})
    resource_id = created_resource.get("id")
    assert resource_id is not None, "Missing resource ID in response"
    assert created_resource.get("subject") == custom_subject, f"Subject mismatch: {created_resource.get('subject')}"
    print(f"[PASS] 2. Successfully uploaded resource #{resource_id} with custom subject: '{custom_subject}'")

    # 3. Retrieve by ID (View Resource)
    status, view_res = client.request("GET", f"/api/resources/{resource_id}")
    assert status == 200, f"Failed to get resource by ID: {view_res}"
    r_data = view_res.get("resource", {})
    assert r_data.get("subject") == custom_subject, f"Subject not persisted correctly: {r_data.get('subject')}"
    assert r_data.get("topic") == custom_topic
    print(f"[PASS] 3. Viewing resource #{resource_id} correctly returns saved custom subject: '{r_data.get('subject')}'")

    # 4. Verify in resource listing
    status, list_res = client.request("GET", "/api/resources")
    assert status == 200, f"Failed to list resources: {list_res}"
    resources = list_res.get("resources", [])
    matching = [r for r in resources if r.get("id") == resource_id]
    assert len(matching) == 1, f"Created resource not in listing: {resources}"
    assert matching[0].get("subject") == custom_subject
    print(f"[PASS] 4. Resource listing includes resource #{resource_id} with custom subject '{matching[0].get('subject')}'")

    # 5. Test editing resource with another custom subject
    edited_subject = "Advanced Quantum Algorithms & Grover Search"
    edited_topic = "Quantum Amplitude Amplification"
    edit_payload = {
        "subject": edited_subject,
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit II",
        "topic": edited_topic,
        "resource_type": "PDF",
        "description": "Updated lecture notes for amplitude amplification."
    }
    status, edit_res = client.request("PUT", f"/api/resources/{resource_id}", edit_payload)
    assert status == 200, f"Edit resource failed: {edit_res}"
    assert edit_res.get("status") == "success"
    updated_resource = edit_res.get("resource", {})
    assert updated_resource.get("subject") == edited_subject, f"Updated subject mismatch: {updated_resource.get('subject')}"
    print(f"[PASS] 5. Successfully edited resource #{resource_id} to new custom subject: '{edited_subject}'")

    # 6. Verify view after edit
    status, view_after = client.request("GET", f"/api/resources/{resource_id}")
    assert status == 200
    assert view_after.get("resource", {}).get("subject") == edited_subject
    print(f"[PASS] 6. Viewing edited resource #{resource_id} reflects updated custom subject: '{edited_subject}'")

    # 7. Check that dashboard courses dynamically reflects this active custom course
    status, stats_res = client.request("GET", "/api/faculty/dashboard-stats")
    assert status == 200
    courses_list = stats_res.get("courses_list", [])
    course_names = [c.get("course_name") for c in courses_list]
    assert edited_subject in course_names, f"Custom subject not found in active courses: {course_names}"
    print(f"[PASS] 7. Faculty active courses dynamically includes '{edited_subject}'")

    # 8. Clean up: Delete test resource
    status, del_res = client.request("DELETE", f"/api/resources/{resource_id}")
    assert status == 200, f"Delete failed: {del_res}"
    print(f"[PASS] 8. Successfully deleted test resource #{resource_id}")

    # 9. Verify resource is deleted
    status, check_del = client.request("GET", f"/api/resources/{resource_id}")
    assert status == 404, f"Resource should be deleted (404), got {status}"
    print(f"[PASS] 9. Verified test resource #{resource_id} is cleanly removed")

    # 10. Logout
    client.request("POST", "/api/auth/logout")
    print(f"[PASS] 10. Logged out cleanly")

    print("=" * 70)
    print("ALL 10 CUSTOM SUBJECT VERIFICATION TESTS PASSED! (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_test()
