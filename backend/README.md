# Academic Question System — Backend API & Real Authentication (STEP 9B)

Python Flask REST API & MySQL Database Foundation for the Academic Question Generation & Difficulty Balancing System.

---

## 🛠 Tech Stack & Security

- **Python 3.13+**
- **Flask 3.x** with Flask-CORS (`supports_credentials=True`)
- **Werkzeug Security** (`generate_password_hash` & `check_password_hash` with `scrypt`)
- **PyMySQL** (pure Python MySQL database driver)
- **python-dotenv** (environment configuration)
- **MySQL Server 9.7 / 8.0** (Database: `academic_question_system`)

---

## 🚀 IntelliJ IDEA Direct Run Setup (Green ▶ Button)

The project includes pre-configured IntelliJ IDEA Run Configurations in `.idea/runConfigurations/`:

1. **Academic Question System — Run All**: Compound configuration launching **both** Flask Backend (5000) and Frontend HTTP Server (8080) simultaneously with a single click of the green ▶ **Run** button.
2. **Academic Question System - Flask Backend**: Launches Flask REST API on `http://localhost:5000/`.
3. **Academic Question System - Frontend**: Launches Python HTTP Server on `http://localhost:8080/`.

### IntelliJ Execution Steps:
1. Open project `academic-question-system` in IntelliJ IDEA.
2. Verify Python interpreter is configured (`Python 3.13`).
3. Ensure MySQL service (`MySQL97`) is running.
4. In the top toolbar run configuration dropdown, select **`Academic Question System — Run All`**.
5. Click the green ▶ **Run** button (or press `Shift + F10`).
6. Open your browser and navigate to: `http://localhost:8080/index.html`.
7. Click the red ■ **Stop** button in IntelliJ to stop both servers.

---

## 🔌 Authentication REST API Endpoints (STEP 9B)

### 1. User Registration
- **URL**: `POST /api/auth/register`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "full_name": "Dr. Alistair Vance",
  "email": "dr.vance@university.edu",
  "password": "facultyPassword123",
  "role": "faculty",
  "department": "Artificial Intelligence & Data Science",
  "semester": "N/A",
  "academic_year": "2025-2026"
}
```
- **Responses**:
  - `201 Created`: User registered successfully in MySQL `users` table.
  - `409 Conflict`: Duplicate email address.
  - `400 Bad Request`: Validation failure.

### 2. User Login
- **URL**: `POST /api/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "email": "dr.vance@university.edu",
  "password": "facultyPassword123",
  "role": "faculty"
}
```
- **Responses**:
  - `200 OK`: Authenticated. Server session established via HTTP-only cookie.
  - `403 Forbidden`: Role mismatch (e.g. Student trying to access Faculty login).
  - `401 Unauthorized`: Invalid email or password.

### 3. Current Authenticated User Profile
- **URL**: `GET /api/auth/me`
- **Credentials**: `include`
- **Responses**:
  - `200 OK`: Returns authenticated user profile (`id`, `full_name`, `email`, `role`, `department`, `semester`, `academic_year`).
  - `401 Unauthorized`: Unauthenticated request.

### 4. User Logout
- **URL**: `POST /api/auth/logout`
- **Credentials**: `include`
- **Response**: `200 OK` (clears Flask session).

### 5. Health Check Endpoint
- **URL**: `GET /api/health`
- **Response**:
```json
{
  "status": "success",
  "message": "Academic Question System API is running",
  "database": {
    "status": "connected",
    "detail": "Database server connection successful"
  }
}
```

---

## 🗺 Planned Future API Endpoint Groups (STEP 9C+)

- `/api/resources` (Syllabus & Academic Study Materials CRUD)
- `/api/questions` (AI Question Bank & Difficulty Balancer)
- `/api/question-papers` (Exam Paper Builder & Fingerprinting)
- `/api/quizzes` (Online Timed Quizzes Engine)
- `/api/assignments` (Assignment Submissions & Evaluation)
- `/api/presentations` (AI Slide Generator)
- `/api/lesson-plans` (Academic Lesson Plan Generator)
- `/api/results` (Student & Faculty Results Management)
- `/api/performance` (Concept Gap Analysis & Mastery Gauges)
- `/api/history` (Audit Log Activity Store)
