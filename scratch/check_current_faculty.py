import urllib.request
import json

BASE_URL = "http://localhost:5000"

def test_faculty(email, password):
    # Login
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=json.dumps({"email": email, "password": password, "role": "faculty"}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        cookie = resp.headers.get("Set-Cookie").split(";")[0]
        login_data = json.loads(resp.read().decode('utf-8'))
        
    print(f"\nLogged in as {login_data['user']['full_name']} (ID: {login_data['user']['id']})")
    
    # Dashboard stats
    req = urllib.request.Request(f"{BASE_URL}/api/faculty/dashboard-stats", headers={"Cookie": cookie})
    with urllib.request.urlopen(req) as resp:
        stats = json.loads(resp.read().decode('utf-8'))
    print("Dashboard Stats:")
    print(f"  Total Questions: {stats.get('total_questions')}")
    print(f"  Active Courses: {stats.get('active_courses')}")
    print(f"  Draft Papers: {stats.get('draft_papers')}")
    print(f"  Published Exams: {stats.get('published_exams')}")
    print("  Courses List:", [c['course_name'] for c in stats.get('courses_list', [])])
    
    # Standalone /api/faculty/courses
    req = urllib.request.Request(f"{BASE_URL}/api/faculty/courses", headers={"Cookie": cookie})
    with urllib.request.urlopen(req) as resp:
        courses = json.loads(resp.read().decode('utf-8'))
    print("Standalone Courses:", [c['course_name'] for c in courses.get('courses', [])])

    # Standalone /api/resources
    req = urllib.request.Request(f"{BASE_URL}/api/resources", headers={"Cookie": cookie})
    with urllib.request.urlopen(req) as resp:
        resources = json.loads(resp.read().decode('utf-8'))
    print(f"Resources ({len(resources.get('resources', []))}):", [r['title'] for r in resources.get('resources', [])][:5])

    # Standalone /api/question-bank
    req = urllib.request.Request(f"{BASE_URL}/api/question-bank", headers={"Cookie": cookie})
    with urllib.request.urlopen(req) as resp:
        qb = json.loads(resp.read().decode('utf-8'))
    print(f"Question Bank ({len(qb.get('questions', []))}):", list(set(q['subject'] for q in qb.get('questions', []))))

test_faculty("muruga@vsb.com", "Password123!")
test_faculty("kavitha@vsb.com", "Password123!")
