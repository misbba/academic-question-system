import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:5000"

def test_login_flow():
    print("=" * 70)
    print("FACULTY LOGIN & DASHBOARD VERIFICATION")
    print("=" * 70)

    # 1. Attempt login with Murugan credentials
    login_url = f"{BASE_URL}/api/auth/login"
    payload = json.dumps({
        "email": "muruga@vsb.com",
        "password": "Password123!",
        "role": "faculty"
    }).encode("utf-8")

    req = urllib.request.Request(
        login_url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST"
    )

    cookie = None
    with urllib.request.urlopen(req) as resp:
        status = resp.status
        cookie_header = resp.headers.get("Set-Cookie")
        if cookie_header:
            cookie = cookie_header.split(";")[0]
        data = json.loads(resp.read().decode("utf-8"))

    assert status == 200, f"Login failed with HTTP {status}: {data}"
    assert data.get("status") == "success"
    user = data.get("user", {})
    assert user.get("full_name") == "Murugan", f"Expected Murugan, got {user.get('full_name')}"
    assert user.get("role") == "faculty"
    print(f"[PASS] 1. POST /api/auth/login succeeded (HTTP 200)")
    print(f"       User: {user.get('full_name')} ({user.get('email')}), Role: {user.get('role')}")
    print(f"       Session Cookie: {cookie[:25]}...")

    # 2. Check /api/auth/me session persistence
    me_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/me",
        headers={"Accept": "application/json", "Cookie": cookie},
        method="GET"
    )
    with urllib.request.urlopen(me_req) as resp:
        me_data = json.loads(resp.read().decode("utf-8"))
    assert resp.status == 200
    assert me_data.get("user", {}).get("full_name") == "Murugan"
    print(f"[PASS] 2. GET /api/auth/me validated session persistence")

    # 3. Check /api/faculty/dashboard-stats
    stats_req = urllib.request.Request(
        f"{BASE_URL}/api/faculty/dashboard-stats",
        headers={"Accept": "application/json", "Cookie": cookie},
        method="GET"
    )
    with urllib.request.urlopen(stats_req) as resp:
        stats_data = json.loads(resp.read().decode("utf-8"))
    assert resp.status == 200
    assert stats_data.get("faculty_name") == "Murugan"
    print(f"[PASS] 3. GET /api/faculty/dashboard-stats returned isolated faculty metrics:")
    print(f"       Total Questions: {stats_data.get('total_questions')}")
    print(f"       Active Courses: {stats_data.get('active_courses')}")
    print(f"       Draft Papers: {stats_data.get('draft_papers')}")
    print(f"       Published Exams: {stats_data.get('published_exams')}")

    # 4. Logout
    logout_req = urllib.request.Request(
        f"{BASE_URL}/api/auth/logout",
        data=b"{}",
        headers={"Content-Type": "application/json", "Cookie": cookie},
        method="POST"
    )
    with urllib.request.urlopen(logout_req) as resp:
        logout_data = json.loads(resp.read().decode("utf-8"))
    assert resp.status == 200
    print(f"[PASS] 4. POST /api/auth/logout succeeded cleanly")

    print("=" * 70)
    print("LOGIN & SESSION WORKFLOW VERIFIED SUCCESSFULLY (100%)")
    print("=" * 70)

if __name__ == "__main__":
    test_login_flow()
