import urllib.request
import json

backend_resp = urllib.request.urlopen('http://localhost:5000/api/health')
print("Backend Health HTTP Status:", backend_resp.status)
print("Backend Health Payload:", json.loads(backend_resp.read().decode('utf-8')))

frontend_resp = urllib.request.urlopen('http://localhost:8080/faculty-image-question.html')
print("Frontend HTTP Status:", frontend_resp.status)
print("Frontend Cache-Control Header:", frontend_resp.headers.get('Cache-Control'))
