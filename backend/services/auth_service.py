import re
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db_connection, DatabaseError

OFFICIAL_DEPARTMENTS = [
    "Artificial Intelligence & Data Science",
    "Artificial Intelligence & Machine Learning",
    "Computer and Communication Engineering"
]

def is_valid_email(email):
    """Basic regex check for email format"""
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return bool(re.match(pattern, email))

def register_user(data):
    """
    Registers a new Faculty or Student user in the MySQL database.
    Performs validation, duplicate checks, password hashing, and returns (success, result, status_code).
    """
    full_name = data.get('full_name', '').strip()
    raw_email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', '').strip().lower()
    department = data.get('department', '').strip()
    semester = str(data.get('semester', '')).strip()
    academic_year = str(data.get('academic_year', '')).strip()

    # 1. Required Field Validation
    if not full_name:
        return False, {"status": "error", "message": "Full name is required."}, 400

    if not raw_email or not is_valid_email(raw_email):
        return False, {"status": "error", "message": "Please enter a valid email address."}, 400

    if not password or len(password) < 8:
        return False, {"status": "error", "message": "Password must be at least 8 characters long."}, 400

    if role not in ['faculty', 'student']:
        return False, {"status": "error", "message": "Role must be either 'faculty' or 'student'."}, 400

    if not department:
        return False, {"status": "error", "message": "Department is required."}, 400

    if not semester:
        semester = "Semester 6" if role == "student" else "N/A"

    if not academic_year:
        academic_year = "2025-2026"

    normalized_email = raw_email.lower()

    # 2. Database Insert & Duplicate Check
    try:
        conn = get_db_connection(include_db_name=True)
        with conn.cursor() as cursor:
            # Check duplicate email
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s;", (normalized_email,))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return False, {"status": "error", "message": "An account with this email already exists."}, 409

            # Secure password hashing
            password_hash = generate_password_hash(password)

            # Insert new user
            insert_sql = """
                INSERT INTO users (full_name, email, password_hash, role, department, semester, academic_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (full_name, normalized_email, password_hash, role, department, semester, academic_year))
            user_id = cursor.lastrowid

        conn.close()

        user_profile = {
            "id": user_id,
            "full_name": full_name,
            "email": normalized_email,
            "role": role,
            "department": department,
            "semester": semester,
            "academic_year": academic_year
        }

        return True, {
            "status": "success",
            "message": "Registration successful",
            "user": user_profile
        }, 201

    except DatabaseError as e:
        return False, {"status": "error", "message": str(e)}, 500
    except Exception as e:
        return False, {"status": "error", "message": f"Database operation failed: {str(e)}"}, 500

def authenticate_user(raw_email, password, requested_role):
    """
    Authenticates user credentials against the MySQL database.
    Checks email, password hash, and role alignment.
    Returns (success, result, status_code).
    """
    if not raw_email or not password:
        return False, {"status": "error", "message": "Please enter both email and password."}, 400

    normalized_email = raw_email.strip().lower()
    requested_role = (requested_role or '').strip().lower()

    try:
        conn = get_db_connection(include_db_name=True)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, email, password_hash, role, department, semester, academic_year
                FROM users WHERE LOWER(email) = %s;
            """, (normalized_email,))
            user = cursor.fetchone()
        conn.close()

        # Generic 401 for invalid credentials
        if not user or not check_password_hash(user['password_hash'], password):
            return False, {"status": "error", "message": "Invalid email or password."}, 401

        # Role mismatch check (HTTP 403)
        if user['role'] != requested_role:
            if requested_role == 'faculty':
                return False, {"status": "error", "message": "This account is not registered as faculty."}, 403
            elif requested_role == 'student':
                return False, {"status": "error", "message": "This account is not registered as student."}, 403
            else:
                return False, {"status": "error", "message": "Role mismatch for this account."}, 403

        user_profile = {
            "id": user['id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role'],
            "department": user['department'],
            "semester": user['semester'],
            "academic_year": user['academic_year']
        }

        return True, {
            "status": "success",
            "message": "Login successful",
            "user": user_profile
        }, 200

    except DatabaseError as e:
        return False, {"status": "error", "message": str(e)}, 500
    except Exception as e:
        return False, {"status": "error", "message": "An unexpected server error occurred during login."}, 500

def get_user_by_id(user_id):
    """
    Fetches user profile by ID from MySQL (excluding password_hash).
    """
    try:
        conn = get_db_connection(include_db_name=True)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, email, role, department, semester, academic_year
                FROM users WHERE id = %s;
            """, (user_id,))
            user = cursor.fetchone()
        conn.close()
        return user
    except Exception:
        return None

def reset_password(raw_email, requested_role, new_password, confirm_password):
    """
    Validates email, role, and matching passwords, then safely updates the user's password_hash in MySQL.
    Returns (success, result, status_code).
    """
    if not raw_email or not is_valid_email(raw_email):
        return False, {"status": "error", "message": "Please enter a valid email address."}, 400

    role = (requested_role or '').strip().lower()
    if role not in ['faculty', 'student']:
        return False, {"status": "error", "message": "Role must be either 'faculty' or 'student'."}, 400

    if not new_password or len(new_password) < 8:
        return False, {"status": "error", "message": "New password must be at least 8 characters long."}, 400

    if new_password != confirm_password:
        return False, {"status": "error", "message": "New password and confirmation password do not match."}, 400

    normalized_email = raw_email.strip().lower()

    try:
        conn = get_db_connection(include_db_name=True)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, full_name, role FROM users WHERE LOWER(email) = %s;
            """, (normalized_email,))
            user = cursor.fetchone()

            if not user:
                conn.close()
                return False, {"status": "error", "message": "No registered account found with this email address."}, 404

            if user['role'] != role:
                conn.close()
                return False, {"status": "error", "message": f"This account is registered as '{user['role']}', not '{role}'."}, 403

            password_hash = generate_password_hash(new_password)
            cursor.execute("""
                UPDATE users SET password_hash = %s WHERE id = %s;
            """, (password_hash, user['id']))

        conn.close()
        return True, {
            "status": "success",
            "message": "Password has been successfully updated. You can now log in with your new credentials."
        }, 200

    except DatabaseError as e:
        return False, {"status": "error", "message": str(e)}, 500
    except Exception as e:
        return False, {"status": "error", "message": f"Server error: {str(e)}"}, 500

