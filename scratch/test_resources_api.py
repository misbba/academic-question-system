import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from app import app

client = app.test_client()

# Login as student Nisha
res = client.post('/api/auth/login', json={
    'email': 'nisha@vsb.com',
    'password': '12345678',
    'role': 'student'
})
print("Login status:", res.status_code, res.get_json())

# Call GET /api/resources
res_mat = client.get('/api/resources')
print("Resources status:", res_mat.status_code)
data = res_mat.get_json()
print("Resources count:", data.get('count'))
print("First resource:", data.get('resources', [])[0] if data.get('resources') else None)
