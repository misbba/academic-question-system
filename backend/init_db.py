import sys
import os
import pymysql

# Add parent directory to sys.path so config and models can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from models.database import get_db_connection, DatabaseError

TABLES = {}

TABLES['users'] = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('faculty', 'student') NOT NULL,
    department VARCHAR(255) NOT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_dept (department)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['academic_resources'] = """
CREATE TABLE IF NOT EXISTS academic_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    topic VARCHAR(255) DEFAULT NULL,
    resource_type VARCHAR(100) DEFAULT NULL,
    file_name VARCHAR(255) DEFAULT NULL,
    file_path VARCHAR(500) DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Uploaded',
    analysis_status VARCHAR(50) DEFAULT 'Pending',
    description TEXT DEFAULT NULL,
    analysis_data LONGTEXT DEFAULT NULL,
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_res_dept (department),
    INDEX idx_res_subject (subject),
    INDEX idx_res_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['questions'] = """
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resource_id INT DEFAULT NULL,
    question_text TEXT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    topic VARCHAR(255) DEFAULT NULL,
    question_type VARCHAR(100) DEFAULT 'Short Answer',
    difficulty VARCHAR(50) DEFAULT 'Medium',
    bloom_level VARCHAR(50) DEFAULT 'Understand',
    concept VARCHAR(255) DEFAULT NULL,
    source_unit VARCHAR(100) DEFAULT NULL,
    explanation TEXT DEFAULT NULL,
    marks INT DEFAULT 2,
    status VARCHAR(50) DEFAULT 'Generated',
    is_in_bank BOOLEAN DEFAULT FALSE,
    similarity_score INT DEFAULT 0,
    similarity_level VARCHAR(50) DEFAULT 'Low',
    concept_repeat_count INT DEFAULT 1,
    source_type VARCHAR(50) DEFAULT 'typed',
    source_reference VARCHAR(255) DEFAULT NULL,
    language VARCHAR(50) DEFAULT 'English',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (resource_id) REFERENCES academic_resources(id) ON DELETE SET NULL,
    INDEX idx_q_subject (subject),
    INDEX idx_q_dept (department),
    INDEX idx_q_created_at (created_at),
    INDEX idx_q_is_in_bank (is_in_bank)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['question_options'] = """
CREATE TABLE IF NOT EXISTS question_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_label VARCHAR(10) NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['question_papers'] = """
CREATE TABLE IF NOT EXISTS question_papers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    exam_type VARCHAR(100) DEFAULT 'Internal Assessment',
    exam_date DATE DEFAULT NULL,
    duration_minutes INT DEFAULT 90,
    max_marks INT DEFAULT 100,
    instructions TEXT DEFAULT NULL,
    sha256_hash VARCHAR(64) DEFAULT NULL,
    qr_payload TEXT DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Draft',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_qp_subject (subject),
    INDEX idx_qp_dept (department),
    INDEX idx_qp_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['quizzes'] = """
CREATE TABLE IF NOT EXISTS quizzes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_code VARCHAR(100) DEFAULT NULL,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    topic VARCHAR(255) DEFAULT NULL,
    quiz_type VARCHAR(100) DEFAULT 'Multiple Choice Question',
    blooms_level VARCHAR(50) DEFAULT 'Understand',
    difficulty VARCHAR(50) DEFAULT 'Mixed',
    duration_minutes INT DEFAULT 15,
    marks_per_question INT DEFAULT 1,
    total_questions INT DEFAULT 10,
    questions LONGTEXT DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Published',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_qz_subject (subject),
    INDEX idx_qz_dept (department),
    INDEX idx_qz_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['quiz_attempts'] = """
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id INT NOT NULL,
    student_id INT NOT NULL,
    score INT NOT NULL,
    total_marks INT NOT NULL,
    total_questions INT NOT NULL,
    percentage VARCHAR(20) NOT NULL,
    answers_json LONGTEXT DEFAULT NULL,
    concept_performance_json LONGTEXT DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Completed',
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_qa_quiz (quiz_id),
    INDEX idx_qa_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['assignments'] = """
CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    due_date DATE DEFAULT NULL,
    total_marks INT DEFAULT 50,
    instructions TEXT DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Published',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_asgn_subject (subject),
    INDEX idx_asgn_dept (department),
    INDEX idx_asgn_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['presentations'] = """
CREATE TABLE IF NOT EXISTS presentations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    topic VARCHAR(255) DEFAULT NULL,
    slide_count INT DEFAULT 8,
    presentation_type VARCHAR(100) DEFAULT 'Classroom Teaching',
    source_material VARCHAR(255) DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Published',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_ppt_subject (subject),
    INDEX idx_ppt_dept (department),
    INDEX idx_ppt_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['lesson_plans'] = """
CREATE TABLE IF NOT EXISTS lesson_plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    academic_year VARCHAR(50) DEFAULT NULL,
    semester VARCHAR(50) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    topic VARCHAR(255) DEFAULT NULL,
    duration_minutes INT DEFAULT 45,
    teaching_method VARCHAR(100) DEFAULT 'Demonstration & Problem Solving',
    status VARCHAR(50) DEFAULT 'Published',
    created_by INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_lp_subject (subject),
    INDEX idx_lp_dept (department),
    INDEX idx_lp_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

TABLES['activity_history'] = """
CREATE TABLE IF NOT EXISTS activity_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT NULL,
    role VARCHAR(50) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(255) DEFAULT NULL,
    unit VARCHAR(100) DEFAULT NULL,
    status VARCHAR(50) DEFAULT 'Recorded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_hist_role (role),
    INDEX idx_hist_subject (subject),
    INDEX idx_hist_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

def init_database():
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    print("=" * 60)
    print("Academic Question System -- Database Initialization Script")
    print("=" * 60)

    db_name = Config.DB_NAME
    db_host = Config.DB_HOST
    db_port = Config.DB_PORT
    db_user = Config.DB_USER
    
    print(f"Connecting to MySQL Server at {db_host}:{db_port} as user '{db_user}'...")

    try:
        # Step 1: Connect without selecting specific database to ensure DB exists
        conn = get_db_connection(include_db_name=False)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
        print(f"[SUCCESS] Database '{db_name}' created/verified successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to create database '{db_name}': {str(e)}")
        sys.exit(1)

    try:
        # Step 2: Connect to the specific database and create tables
        conn = get_db_connection(include_db_name=True)
        with conn.cursor() as cursor:
            for table_name, table_sql in TABLES.items():
                cursor.execute(table_sql)
                print(f"   * Table '{table_name}' verified/created.")

            # Safe Schema Migration for academic_resources, questions, and question_papers tables
            alter_queries = [
                "ALTER TABLE academic_resources ADD COLUMN status VARCHAR(50) DEFAULT 'Uploaded';",
                "ALTER TABLE academic_resources ADD COLUMN description TEXT DEFAULT NULL;",
                "ALTER TABLE academic_resources ADD COLUMN analysis_data LONGTEXT DEFAULT NULL;",
                "ALTER TABLE questions ADD COLUMN resource_id INT DEFAULT NULL;",
                "ALTER TABLE questions ADD COLUMN source_unit VARCHAR(100) DEFAULT NULL;",
                "ALTER TABLE questions ADD COLUMN explanation TEXT DEFAULT NULL;",
                "ALTER TABLE questions ADD COLUMN marks INT DEFAULT 2;",
                "ALTER TABLE questions ADD COLUMN status VARCHAR(50) DEFAULT 'Generated';",
                "ALTER TABLE questions ADD COLUMN is_in_bank BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE questions ADD COLUMN similarity_score INT DEFAULT 0;",
                "ALTER TABLE questions ADD COLUMN similarity_level VARCHAR(50) DEFAULT 'Low';",
                "ALTER TABLE questions ADD COLUMN concept_repeat_count INT DEFAULT 1;",
                "ALTER TABLE question_papers ADD COLUMN sections LONGTEXT DEFAULT NULL;",
                "ALTER TABLE question_papers ADD COLUMN question_ids LONGTEXT DEFAULT NULL;",
                "ALTER TABLE question_papers ADD COLUMN fingerprint VARCHAR(64) DEFAULT NULL;",
                "ALTER TABLE question_papers ADD COLUMN duration VARCHAR(50) DEFAULT '3 Hours';",
                "ALTER TABLE question_papers ADD COLUMN total_marks INT DEFAULT 100;",
                "ALTER TABLE question_papers ADD COLUMN exam_time VARCHAR(50) DEFAULT '10:00 AM - 01:00 PM';",
                "ALTER TABLE quizzes ADD COLUMN quiz_code VARCHAR(100) DEFAULT NULL;",
                "ALTER TABLE quizzes ADD COLUMN topic VARCHAR(255) DEFAULT NULL;",
                "ALTER TABLE quizzes ADD COLUMN quiz_type VARCHAR(100) DEFAULT 'Multiple Choice Question';",
                "ALTER TABLE quizzes ADD COLUMN blooms_level VARCHAR(50) DEFAULT 'Understand';",
                "ALTER TABLE quizzes ADD COLUMN difficulty VARCHAR(50) DEFAULT 'Mixed';",
                "ALTER TABLE quizzes ADD COLUMN questions LONGTEXT DEFAULT NULL;"
            ]
            for alter_sql in alter_queries:
                try:
                    cursor.execute(alter_sql)
                except Exception:
                    pass  # Column already exists

        conn.close()
        print("[SUCCESS] Tables created/verified successfully.")
        print("=" * 60)
        print("Initialization Complete!")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database tables: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database()

