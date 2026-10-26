from werkzeug.security import check_password_hash

h = 'scrypt:32768:8:1$JmwyWUsa2mU7YJhg$829a4a49f23c3d513e31f4135b141555399e61c56b92c57a877e87f62d95ea9407f5cb16447c14e51e2eac1dec3d34674dad24595c617bc030fa5c65be98722b'

passwords = [
    "Password123!", "password123!", "Password123", "password123",
    "kavitha@vsb.com", "kavitha", "Kavitha", "Kavitha123!", "kavitha123!",
    "VSB@123", "vsb@123", "Vsb@123", "Admin@123", "faculty123", "Faculty123!"
]
for p in passwords:
    if check_password_hash(h, p):
        print("MATCH:", p)
        break
else:
    print("NO MATCH")
