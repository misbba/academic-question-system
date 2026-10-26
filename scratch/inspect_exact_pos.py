with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    c = f.read()

c_norm = c.replace('\r\n', '\n')

pos1 = c_norm.find('updateFacultyHeaderProfile(verifiedUser);')
print("--- Pos 1 ---")
print(repr(c_norm[pos1:pos1+150]))

pos9 = c_norm.find('function handleLogout() {')
print("--- Pos 9 ---")
print(repr(c_norm[pos9:pos9+350]))
