import urllib.request

try:
    with urllib.request.urlopen("http://localhost:8080/faculty-question-paper.html", timeout=3) as r:
        print(f"Frontend 8080: Status {r.status} OK")
except Exception as e:
    print(f"Frontend 8080 Error: {e}")

try:
    with urllib.request.urlopen("http://localhost:5000/api/health", timeout=3) as r:
        print(f"Backend 5000: Status {r.status} OK, Data: {r.read().decode('utf-8')[:100]}")
except Exception as e:
    print(f"Backend 5000 Error: {e}")
