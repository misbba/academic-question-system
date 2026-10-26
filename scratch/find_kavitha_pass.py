import pymysql
from werkzeug.security import check_password_hash

conn = pymysql.connect(host='localhost', user='root', password='sqlamzad@123', database='academic_question_system', cursorclass=pymysql.cursors.DictCursor)
with conn.cursor() as cur:
    cur.execute("SELECT id, email, full_name, password_hash FROM users WHERE email = 'kavitha@vsb.com'")
    user = cur.fetchone()
    print("User:", user['id'], user['email'], user['full_name'], user['password_hash'])
    
    candidates = [
        "Password123!", "Password123", "password123!", "password123",
        "Kavitha123!", "Kavitha123", "kavitha123!", "kavitha123",
        "Kavitha@123", "Kavitha@123!", "Welcome123!", "Admin123!",
        "Vsb123!", "VSB123!", "12345678", "123456"
    ]
    for c in candidates:
        if check_password_hash(user['password_hash'], c):
            print(f"FOUND PASSWORD: '{c}'")
            break
    else:
        print("None of the common candidates matched.")
conn.close()
