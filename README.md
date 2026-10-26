# Academic Question Generation & Difficulty Balancing System

An intelligent academic platform designed for higher education institutions. The system enables faculty to upload syllabus materials, analyze content, generate difficulty-balanced question sets aligned with Bloom's Taxonomy, build examination papers, compute SHA-256 digital paper fingerprints & QR codes, build timed MCQ quizzes, create assignments, generate presentation slide decks, generate structured lesson plans, convert speech to academic text (Voice-to-Question), generate questions from uploaded images/diagrams, convert questions between English and Tamil, track student results & performance analytics, and authenticate users via a real Python Flask REST API + MySQL database backend.

---

## 📌 Project Overview

- **Project Title**: Academic Question Generation & Difficulty Balancing System
- **Current Development Step**: **STEP 9B — Real Faculty & Student Authentication (Flask + MySQL + IntelliJ IDEA Direct Run)**
- **Design Philosophy**: Natural, clean academic college-project appearance built with HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Python 3 Flask REST API, PyMySQL, and Werkzeug password security.

---

## 🛠️ Technology Stack & Architecture

### Frontend Stack (Port 8080)
- **Structure**: HTML5 Semantic Layouts
- **Styling**: Custom Design System + Bootstrap 5.3.3
- **Scripting & State**: Modular JavaScript (Vanilla JS ES6+) with `js/auth.js` helper & LocalStorage fallback
- **Speech Recognition**: Web Speech API (`en-IN` / `ta-IN`) with manual text fallback
- **File Upload & Image Preview**: Client-side `FileReader` API for diagram upload (JPG/PNG/WEBP)
- **Language Conversion**: Academic English ↔ Tamil Translation Engine preserving technical terms
- **Cryptographic Security**: Web Crypto API (`crypto.subtle.digest('SHA-256')`) for digital exam paper fingerprinting

### Backend Stack (Port 5000)
- **Framework**: Python 3.13 + Flask 3.x REST API
- **Authentication**: Werkzeug Password Hashing (`scrypt`) & Flask HTTP-only server sessions
- **Cross-Origin**: Flask-CORS (`supports_credentials=True`) configured for `http://localhost:8080`
- **Database Driver**: PyMySQL (pure Python driver with parameterized queries)
- **Database Engine**: MySQL Server 9.7 / 8.0 (Database: `academic_question_system`)

---

## 🏫 Academic Departments (Standardized)

The application strictly enforces three core department choices:
1. `Artificial Intelligence & Data Science`
2. `Artificial Intelligence & Machine Learning`
3. `Computer and Communication Engineering`

---

## 🚀 How to Run the Entire Project in IntelliJ IDEA

The project is pre-configured with a single one-click run configuration that automatically starts both the Flask Backend (Port 5000) and the Frontend HTTP Server (Port 8080) simultaneously.

### Step-by-Step Instructions:
1. **Open the project** in IntelliJ IDEA (`File` → `Open...` → select `academic-question-system`).
2. **Select `Academic Question System — Run All`** from the run configuration dropdown in IntelliJ's top toolbar.
3. **Click the green Run button** (▶) (or press `Shift + F10`).
4. **Open `http://localhost:8080/`** (or `http://localhost:8080/index.html`) in your web browser.
5. **Stop the application using IntelliJ's Stop button** (■) when finished.

> **Alternative CLI Launcher**: You can also launch both servers with a single command from terminal:
> ```bash
> python run_all.py
> ```

---

## 📁 Project Directory Structure

```
academic-question-system/
├── .idea/
│   └── runConfigurations/
│       ├── Academic_Question_System____Run_All.xml      # One-Click Combined Run Config
│       ├── Academic_Question_System___Flask_Backend.xml # Backend Run Config (Port 5000)
│       └── Academic_Question_System___Frontend.xml      # Frontend Run Config (Port 8080)
├── run_all.py                      # Unified dual-server launcher & monitor script
├── index.html                      # Landing Page (Role Entry Points)
├── faculty-login.html              # Faculty Real Login Page
├── faculty-register.html           # Faculty Real Registration Page
├── faculty-dashboard.html          # Protected Faculty Workspace Dashboard
├── faculty-resources.html          # Faculty Academic Resources Module (STEP 2)
├── faculty-generate-questions.html # Faculty AI Question Generator & Balancer (STEP 3)
├── faculty-question-paper.html     # Question Paper Builder & Fingerprinter (STEP 4)
├── faculty-generate-quiz.html      # Faculty Quiz Generator & MCQ Publisher (STEP 5)
├── faculty-generate-assignment.html # Faculty Assignment Generator & Publisher (STEP 5)
├── faculty-generate-ppt.html       # Faculty AI Presentation / PPT Generator (STEP 6)
├── faculty-generate-lesson-plan.html # Faculty Academic Lesson Plan Generator (STEP 6)
├── faculty-voice-question.html     # Faculty Voice-to-Question Generator (STEP 7)
├── faculty-image-question.html     # Faculty Image / Diagram Question Generator (STEP 7)
├── faculty-language-converter.html # Faculty English ↔ Tamil Language Converter (STEP 7)
├── faculty-results.html            # Faculty Student Submissions & Evaluation (STEP 8)
├── faculty-performance.html        # Faculty Class Performance & Concept Gaps (STEP 8)
├── faculty-history.html            # Faculty Audit History & Operation Logs (STEP 8)
├── faculty-profile.html            # Faculty Profile & Credentials Management
├── student-login.html              # Student Real Login Page
├── student-register.html           # Student Real Registration Page
├── student-dashboard.html          # Protected Student Portal Dashboard
├── student-subjects.html           # Student Enrolled Subjects Portal
├── student-materials.html          # Student Study Materials Portal (STEP 2)
├── student-question-papers.html    # Student Published Question Papers View (STEP 4)
├── student-quizzes.html            # Student Timed Quizzes & Attempt History (STEP 5)
├── student-assignments.html        # Student Assignments Portal & Submissions (STEP 5)
├── student-presentations.html      # Student Published Presentations Portal (STEP 6)
├── student-lesson-plans.html       # Student Published Lesson Plans Portal (STEP 6)
├── student-results.html            # Student Results & Assessment Breakdown (STEP 8)
├── student-performance.html        # Student Performance Analytics & Concept Mastery (STEP 8)
├── student-history.html            # Student Academic History & Activity Log (STEP 8)
├── student-profile.html            # Student Profile & Credentials Management
├── .env.example                    # Sample DB & Flask Environment Config
├── .gitignore                      # Git Ignore Rules (.env, __pycache__, venv)
├── css/
│   └── custom.css                  # Custom CSS Styles, Badges & Progress Gauges
├── js/
│   ├── auth.js                     # NEW (STEP 9B): Client Auth Helper (Flask API fetch wrapper)
│   ├── mock-data.js                # Master Questions, Voice, Image & Demo Stores
│   └── app.js                      # SpeechRecognition, FileReader, Translation & Analytics
├── backend/                        # Flask & MySQL REST API Backend
│   ├── app.py                      # Flask Application Entrypoint
│   ├── run.py                      # Standalone Backend Runner Script
│   ├── config.py                   # Environment & DB Config Manager
│   ├── init_db.py                  # MySQL Database & 10 Tables Initialization Script
│   ├── requirements.txt            # Flask, PyMySQL, Flask-CORS, python-dotenv
│   ├── README.md                   # Backend API Setup & Sitemap Documentation
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py             # PyMySQL Connection Helper & Error Masking
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health_routes.py        # GET /api/health Endpoint
│   │   └── auth_routes.py          # REST Auth Endpoints (register, login, me, logout, status)
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py         # NEW (STEP 9B): Auth Validation, Password Hashing & MySQL Queries
│   └── utils/
│       └── __init__.py
└── README.md                       # Master Documentation
```

---

## 🔑 Key Features & REST APIs Built in STEP 9B

- `POST /api/auth/register`: Validates name, email format, password min length (8 chars), role, department, semester, academic_year. Checks duplicate email in MySQL (case-insensitive). Hashes password using `scrypt`.
- `POST /api/auth/login`: Authenticates email & password hash. Checks role alignment (rejects cross-role logins with HTTP 403). Sets HTTP-only Flask session cookie.
- `GET /api/auth/me`: Retrieves current authenticated user profile based on active session.
- `POST /api/auth/logout`: Invalidates server session.
- **Protected Dashboards**: `faculty-dashboard.html` and `student-dashboard.html` enforce session & role checks on page load and populate user info from backend.

---

## 📜 System Color Palette Reference
- **Primary**: `#2B193D` (Deep Indigo)
- **Secondary**: `#67405F` (Plum)
- **Background**: `#F7F3ED` (Warm Academic Parchment)
- **Cards**: `#FFFDF9` (Cream White)
- **Accent**: `#E87861` (Terracotta)
- **Text**: `#29252B` (Dark Charcoal)
- **Easy**: `#6B9B78` | **Medium**: `#D99A3D` | **Hard**: `#C9554D`
