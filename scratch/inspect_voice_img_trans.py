with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- Voice Lines ~21260-21325 ---")
for i in range(21260, 21330):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Image Lines ~22215-22280 ---")
for i in range(22215, 22285):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Translated Lines ~22840-22910 ---")
for i in range(22840, 22910):
    print(f"{i+1}: {lines[i]}", end='')
