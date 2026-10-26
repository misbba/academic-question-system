# Production Deployment Guide
## Academic Question Generation and Difficulty Balancing System

This guide outlines the step-by-step procedure to deploy the **Academic Question Generation and Difficulty Balancing System** into production.

---

## 1. Architecture & Repository Structure

The repository is organized as a decoupled Web Application:

```
academic-question-system/
├── backend/                       # Python Flask REST API
│   ├── app.py                     # Flask factory & application entry point
│   ├── config.py                  # Production configuration & env loader
│   ├── wsgi.py                    # Production WSGI entry point
│   ├── init_db.py                 # MySQL schema migration & table initialization
│   ├── requirements.txt           # Python dependencies (Gunicorn, PyMySQL, etc.)
│   ├── models/                    # PyMySQL database connection & error handling
│   ├── routes/                    # API Blueprints (auth, resources, questions, quizzes, etc.)
│   ├── services/                  # Business logic & AI generation algorithms
│   └── uploads/                   # Local file storage (materials, diagrams, assignments)
├── js/
│   ├── config.js                  # Central frontend environment configuration (API URL)
│   ├── auth.js                    # Session-based authentication client
│   └── app.js                     # Core application logic for faculty & student portals
├── css/                           # Custom stylesheets & Bootstrap overrides
├── *.html                         # Static HTML entry points (Faculty & Student portals)
├── render.yaml                    # Infrastructure-as-Code Blueprint for Render
├── Procfile                       # Production process declaration
└── DEPLOYMENT.md                  # This deployment manual
```

---

## 2. Phase 1: Set Up Cloud MySQL Database

The application requires a MySQL 8.0+ compatible database. Choose any cloud database provider:

### Recommended Free / Managed Providers:
1. **Aiven for MySQL** (Free tier available, TLS/SSL enabled, highly reliable)
2. **TiDB Cloud Serverless** (Free 25 GB storage, MySQL 8.0 protocol compatible)
3. **Railway MySQL** (Pay-as-you-go / developer credits)
4. **AWS RDS / DigitalOcean Managed MySQL**

---

### Step 1.1: Retrieve Connection Credentials
From your cloud database dashboard, gather:
- **Host**: e.g., `mysql-xxxxx.aivencloud.com`
- **Port**: e.g., `3306` (or custom port like `15234`)
- **Database Name**: e.g., `defaultdb` or `academic_question_system`
- **User**: e.g., `avnadmin` or `root`
- **Password**: Your database password
- **SSL**: Enabled (`REQUIRED` or `PREFERRED`)

---

### Step 1.2: Migrate Database Schema Safely

#### Option A: Fresh Schema Initialization (Zero data loss)
Run the built-in database migration script against your cloud database:

```bash
# Set environment variables for the remote cloud database
export DB_HOST="your-cloud-host.com"
export DB_PORT="3306"
export DB_NAME="your-database-name"
export DB_USER="your-db-user"
export DB_PASSWORD="your-db-password"
export DB_SSL="true"

# Execute schema initialization
python backend/init_db.py
```

`init_db.py` uses `CREATE TABLE IF NOT EXISTS` and safe column additions across all 12 core tables:
`users`, `academic_resources`, `questions`, `question_options`, `question_papers`, `quizzes`, `quiz_attempts`, `assignments`, `assignment_submissions`, `presentations`, `lesson_plans`, and `activity_history`.

---

#### Option B: Export & Migrate Existing Local Data
To preserve all your existing faculty accounts, courses, study materials, and questions from your local machine:

1. **Export local database**:
   ```bash
   mysqldump -u root -p academic_question_system > backup_academic_system.sql
   ```

2. **Import into your remote cloud database**:
   ```bash
   mysql -h your-cloud-host.com -P 3306 -u your-db-user -p your-database-name < backup_academic_system.sql
   ```

---

## 3. Phase 2: Deploy Backend to Render (Flask Web Service)

### Step 2.1: Create Web Service on Render
1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Configure service settings:
   - **Name**: `academic-question-system-api`
   - **Region**: Select region closest to your database (e.g., Frankfurt / Oregon / Singapore).
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: Free (or Starter)

---

### Step 2.2: Add Environment Variables
In the Render Web Service **Environment** tab, add the following variables:

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `production` | Enables production mode and secure cookies |
| `SECRET_KEY` | *(Generate a 32-character random string)* | Flask session signature key |
| `DB_HOST` | `mysql-xxxx.aivencloud.com` | Cloud MySQL host |
| `DB_PORT` | `3306` | Cloud MySQL port |
| `DB_NAME` | `academic_question_system` | Database name |
| `DB_USER` | `avnadmin` | Database username |
| `DB_PASSWORD` | *(Your cloud DB password)* | Database password |
| `DB_SSL` | `true` | Enables TLS/SSL for cloud database connection |
| `FRONTEND_ORIGIN` | `https://academic-question-system-web.onrender.com` | Allowed frontend origin for CORS |

*(Note: If your database provider gives a single connection URL, you can alternatively supply `DATABASE_URL=mysql://user:pass@host:port/dbname`)*

---

### Step 2.3: Persistent Storage for Uploads (Recommended for Production)
Render free Web Services have ephemeral disks (uploaded files reset when the instance restarts).
- For permanent file uploads (lecture notes, assignments, diagrams), attach a **Render Disk**:
  1. Go to the **Disks** tab in your Web Service settings.
  2. Click **Add Disk**.
  3. Mount Path: `/var/data`
  4. Add an Environment Variable:
     `UPLOAD_FOLDER=/var/data/uploads`

---

### Step 2.4: Verify Backend Health
Once deployed, verify the public health endpoint:
```
GET https://academic-question-system-api.onrender.com/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Academic Question System API is operational"
}
```

---

## 4. Phase 3: Deploy Frontend (Static Site on Render)

### Step 3.1: Configure Backend URL in Frontend
In [`js/config.js`](file:///C:/Users/Nisha/.gemini/antigravity/scratch/academic-question-system/js/config.js), update line 35 with your deployed Render backend URL:

```javascript
// Replace with your real deployed backend URL (no trailing slash):
return 'https://academic-question-system-api.onrender.com';
```

*(Note: Localhost development automatically remains pointing to `http://localhost:5000`)*.

---

### Step 3.2: Create Static Site on Render
1. On [Render Dashboard](https://dashboard.render.com/), click **New +** -> **Static Site**.
2. Connect your GitHub repository.
3. Configure settings:
   - **Name**: `academic-question-system-web`
   - **Root Directory**: `.` (leave empty for repository root)
   - **Build Command**: *(Leave empty — vanilla HTML/CSS/JS)*
   - **Publish Directory**: `.`
4. Click **Create Static Site**.

---

### Step 3.3: Link CORS Origins
Copy the URL of your deployed static site (e.g., `https://academic-question-system-web.onrender.com`).
Go to your **Backend Web Service** -> **Environment**, and ensure `FRONTEND_ORIGIN` is set to that exact URL.

---

## 5. Security & Session Handling Checklist

- [x] **Cross-Origin Cookie Security**: In production (`FLASK_ENV=production` or `RENDER=true`), Flask automatically enforces `SESSION_COOKIE_SAMESITE='None'` and `SESSION_COOKIE_SECURE=True`. This allows `fetch(..., { credentials: 'include' })` to transmit session authentication cookies across domains securely.
- [x] **Reverse Proxy Protocol**: `ProxyFix` middleware is enabled in `backend/app.py` so that Flask recognizes HTTPS requests routed through Render's TLS reverse proxies.
- [x] **CORS with Credentials**: `supports_credentials=True` is enabled and strictly restricted to the specified `FRONTEND_ORIGIN` (wildcards are disallowed by browser security when credentials are included).
- [x] **Database Password Masking**: PyMySQL connection errors automatically mask passwords, preventing sensitive credential leaks in server logs.

---

## 6. Smoke Testing & Verification

Once both frontend and backend are live:

1. **Open Landing Page**: Visit your frontend URL (`https://your-frontend.onrender.com/index.html`).
2. **Faculty Login**:
   - Navigate to `faculty-login.html`.
   - Log in using your faculty credentials (`muruga@vsb.com` / `Password123!`).
   - Confirm redirect to `faculty-dashboard.html` and that authorized subjects load.
3. **Generate Question Paper / Quiz**:
   - Create a 1-mark quiz or 2/8/16-mark semester question paper and publish.
4. **Student Portal Verification**:
   - Open an Incognito window and navigate to `student-login.html`.
   - Log in using student credentials (`nisha@vsb.com` / `12345678`).
   - Visit **My Subjects** (`student-subjects.html`) and check that:
     - Study Materials load genuine files from cloud storage.
     - Published Quizzes can be attempted with live score evaluation.
     - Question Papers render complete Part A + Part B Either/Or options.
     - Assignments accept student solution submissions.

---

## 7. Troubleshooting Common Production Issues

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **CORS blocked error in browser console** | `FRONTEND_ORIGIN` does not match the frontend URL | Ensure `FRONTEND_ORIGIN` has the exact protocol (`https://`) and no trailing slash. Multiple origins can be comma-separated: `https://site1.com,https://site2.com`. |
| **Login succeeds but dashboard says "Unauthorized" (401)** | Third-party cookie blocked or missing HTTPS | Verify backend is accessed over HTTPS and `SESSION_COOKIE_SAMESITE` is `None`. Clear browser cookies and test in Incognito. |
| **Database connection refused (Error 2003)** | Incorrect `DB_HOST`, port, or database firewall | Whitelist `0.0.0.0/0` in your cloud database access rules or add Render's outbound IP ranges. |
| **`caching_sha2_password` error** | MySQL 8 authentication plugin requires cryptography | Ensure `cryptography` is in `requirements.txt` (already added). |
| **Uploaded study materials disappear after deploy** | Ephemeral file system on free tier | Attach a Render Disk at `/var/data` and configure `UPLOAD_FOLDER=/var/data/uploads`. |
