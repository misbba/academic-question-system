import os, re

base_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
faculty_pages = [
    "faculty-dashboard.html",
    "faculty-resources.html",
    "faculty-generate-questions.html",
    "faculty-voice-question.html",
    "faculty-image-question.html",
    "faculty-language-converter.html",
    "faculty-question-paper.html",
    "faculty-generate-quiz.html",
    "faculty-generate-assignment.html",
    "faculty-generate-ppt.html",
    "faculty-generate-lesson-plan.html",
    "faculty-history.html",
    "faculty-performance.html",
    "faculty-results.html",
    "faculty-profile.html"
]

for p in faculty_pages:
    fpath = os.path.join(base_dir, p)
    if not os.path.exists(fpath):
        print(f"MISSING: {p}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find scripts or functions called
    scripts = re.findall(r'<script(?![^>]*src=)[^>]*>([\s\S]*?)</script>', content)
    body_onload = re.findall(r'<body[^>]*onload=["\']([^"\']+)["\']', content)
    doc_events = re.findall(r'addEventListener\([\'"]DOMContentLoaded[\'"][^)]*\)', content)
    
    print(f"\n=== {p} ===")
    if body_onload:
        print("  body onload:", body_onload)
    print(f"  Inline scripts count: {len(scripts)}")
    for idx, s in enumerate(scripts):
        s_clean = s.strip()
        lines = [l.strip() for l in s_clean.split("\n") if l.strip() and not l.strip().startswith("//")]
        print(f"    Script {idx+1} first 3 lines:", lines[:3])
