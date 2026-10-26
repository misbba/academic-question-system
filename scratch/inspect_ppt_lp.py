with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- PPT Lines ~18320-18350 ---")
for i in range(18320, 18350):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Lesson Plan Lines ~19210-19245 ---")
for i in range(19210, 19245):
    print(f"{i+1}: {lines[i]}", end='')
