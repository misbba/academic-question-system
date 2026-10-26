import requests

base = "http://localhost:5000/api"

# 1. Test Murugan
s_murugan = requests.Session()
r_login = s_murugan.post(f"{base}/auth/login", json={"email": "muruga@vsb.com", "password": "Password123!", "role": "faculty"})
assert r_login.status_code == 200, f"Login failed: {r_login.text}"
print("Murugan Logged in:", r_login.json()['user']['full_name'])

r_stats = s_murugan.get(f"{base}/faculty/dashboard-stats")
print("Murugan Stats status:", r_stats.status_code)
print("Murugan Stats response:", r_stats.json())

# 2. Test Turing
s_turing = requests.Session()
r_tlogin = s_turing.post(f"{base}/auth/login", json={"email": "turing@university.edu", "password": "Password123!", "role": "faculty"})
assert r_tlogin.status_code == 200, f"Login failed: {r_tlogin.text}"
print("\nTuring Logged in:", r_tlogin.json()['user']['full_name'])

r_tstats = s_turing.get(f"{base}/faculty/dashboard-stats")
print("Turing Stats status:", r_tstats.status_code)
print("Turing Stats response:", r_tstats.json())
