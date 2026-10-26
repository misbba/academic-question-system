import re

with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\mock-data.js", "r", encoding="utf-8") as f:
    c = f.read()

m = re.findall(r'.{0,40}(?:publishedImageQuestions|\.png|\.jpg|\.jpeg|diagram).{0,40}', c, re.IGNORECASE)
print(f"Found {len(m)} matches in mock-data.js:")
for match in m[:10]:
    print("  ", match.strip())
