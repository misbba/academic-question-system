import sys
import os

sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
from models.database import get_db_connection

# Comprehensive question seed set covering Units I to V with 2, 8, and 16 marks across distinct lessons
QUESTIONS_DATA = [
    # ------------------ UNIT I ------------------
    # Lesson 1: DBMS Architecture & Relational Model
    {
        "question_text": "What is data independence in DBMS? Distinguish between physical and logical data independence with examples.",
        "marks": 2, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Easy", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Define schema, instance, and subschema in database management systems.",
        "marks": 2, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "List three primary advantages of using a DBMS over traditional file-oriented systems.",
        "marks": 2, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the three-schema ANSI/SPARC architecture of DBMS with a neat block diagram. Discuss how it achieves data abstraction.",
        "marks": 8, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Describe the relational data model concepts: relations, attributes, tuples, domains, and relational integrity constraints.",
        "marks": 8, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Discuss the overall architecture of a Database Management System in detail with a structural block diagram, explaining query processor and storage manager modules.",
        "marks": 16, "unit": "Unit I", "topic": "DBMS Architecture & Relational Model",
        "difficulty": "Hard", "bloom_level": "Analyze", "question_type": "Descriptive"
    },

    # Lesson 2: ER Modeling & Relational Mapping
    {
        "question_text": "What is the difference between a strong entity set and a weak entity set? State how a weak entity set is represented in ER notation.",
        "marks": 2, "unit": "Unit I", "topic": "ER Modeling & Relational Mapping",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Define primary key, candidate key, super key, and foreign key with a suitable student-course relation example.",
        "marks": 2, "unit": "Unit I", "topic": "ER Modeling & Relational Mapping",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the symbols used in Entity-Relationship modeling. Construct an ER diagram for a Hospital Management System showing cardinalities and participation constraints.",
        "marks": 8, "unit": "Unit I", "topic": "ER Modeling & Relational Mapping",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Problem Solving"
    },
    {
        "question_text": "Explain the step-by-step algorithms used to map regular entity types, weak entities, binary relationships, and multivalued attributes into relational tables.",
        "marks": 8, "unit": "Unit I", "topic": "ER Modeling & Relational Mapping",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "A university database requires tracking students, academic departments, professors, and course enrollments. Design a comprehensive ER diagram and demonstrate step-by-step conversion of the ER schema into relational tables with all primary and foreign key constraints.",
        "marks": 16, "unit": "Unit I", "topic": "ER Modeling & Relational Mapping",
        "difficulty": "Hard", "bloom_level": "Create", "question_type": "Problem Solving"
    },

    # ------------------ UNIT II ------------------
    # Lesson 1: Relational Algebra Operations
    {
        "question_text": "Define select and project operations in relational algebra using formal mathematical notations.",
        "marks": 2, "unit": "Unit II", "topic": "Relational Algebra Operations",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "What is the Cartesian Product in relational algebra? Under what condition does a Cartesian Product simplify to a Natural Join?",
        "marks": 2, "unit": "Unit II", "topic": "Relational Algebra Operations",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the fundamental operations of relational algebra: Select, Project, Union, Set Difference, Cartesian Product, and Rename with illustrative relational examples.",
        "marks": 8, "unit": "Unit II", "topic": "Relational Algebra Operations",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain Set Intersection, Natural Join, Theta Join, and Division operations in relational algebra with input relations and output results.",
        "marks": 8, "unit": "Unit II", "topic": "Relational Algebra Operations",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "Given schema: Student(roll_no, name, dept), Enrolled(roll_no, course_id), Course(course_id, cname, credits). Formulate relational algebra expressions for: (i) Students enrolled in all courses, (ii) Students in AI dept with 4-credit courses, (iii) Courses with no enrollments, and (iv) Theta join vs Natural join on Student and Course.",
        "marks": 16, "unit": "Unit II", "topic": "Relational Algebra Operations",
        "difficulty": "Hard", "bloom_level": "Apply", "question_type": "Problem Solving"
    },

    # Lesson 2: Normalization & Functional Dependencies
    {
        "question_text": "State Armstrong's Axioms for functional dependencies: Reflexivity, Augmentation, and Transitivity rules.",
        "marks": 2, "unit": "Unit II", "topic": "Normalization & Functional Dependencies",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Define Boyce-Codd Normal Form (BCNF). How does BCNF differ from Third Normal Form (3NF)?",
        "marks": 2, "unit": "Unit II", "topic": "Normalization & Functional Dependencies",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain First Normal Form (1NF), Second Normal Form (2NF), and Third Normal Form (3NF) with a non-trivial relation and illustrate anomaly removal.",
        "marks": 8, "unit": "Unit II", "topic": "Normalization & Functional Dependencies",
        "difficulty": "Medium", "bloom_level": "Analyze", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain Lossless Join Decomposition and Dependency Preservation properties in database normalization with mathematical proofs and counterexamples.",
        "marks": 8, "unit": "Unit II", "topic": "Normalization & Functional Dependencies",
        "difficulty": "Hard", "bloom_level": "Evaluate", "question_type": "Descriptive"
    },
    {
        "question_text": "Given relation R(A, B, C, D, E) with functional dependencies F = {A -> BC, CD -> E, B -> D, E -> A}: (i) Find all candidate keys of R, (ii) Determine the highest normal form of R, (iii) Decompose R into 3NF and BCNF with dependency preservation and lossless join property.",
        "marks": 16, "unit": "Unit II", "topic": "Normalization & Functional Dependencies",
        "difficulty": "Hard", "bloom_level": "Evaluate", "question_type": "Problem Solving"
    },

    # ------------------ UNIT III ------------------
    # Lesson 1: SQL Commands & Queries
    {
        "question_text": "What is the difference between DELETE and TRUNCATE statements in SQL regarding transaction rollback and performance?",
        "marks": 2, "unit": "Unit III", "topic": "SQL Commands & Queries",
        "difficulty": "Easy", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the purpose of HAVING clause and contrast it with WHERE clause in SQL queries.",
        "marks": 2, "unit": "Unit III", "topic": "SQL Commands & Queries",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain Data Definition Language (DDL) and Data Manipulation Language (DML) commands in SQL with syntax and execution examples.",
        "marks": 8, "unit": "Unit III", "topic": "SQL Commands & Queries",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain SQL constraints: PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, and CHECK with DDL table definitions and violation behavior.",
        "marks": 8, "unit": "Unit III", "topic": "SQL Commands & Queries",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "Write SQL DDL and DML statements to create an Employee-Department enterprise database with primary key, foreign key, check constraints, and demonstrate complex queries using aggregate functions, GROUP BY, and HAVING.",
        "marks": 16, "unit": "Unit III", "topic": "SQL Commands & Queries",
        "difficulty": "Hard", "bloom_level": "Apply", "question_type": "Problem Solving"
    },

    # Lesson 2: Joins, Subqueries & Aggregations
    {
        "question_text": "Differentiate between correlated and non-correlated subqueries in SQL with a query execution explanation.",
        "marks": 2, "unit": "Unit III", "topic": "Joins, Subqueries & Aggregations",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "What are SQL views and why are they called virtual tables? How do views enhance database security?",
        "marks": 2, "unit": "Unit III", "topic": "Joins, Subqueries & Aggregations",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain INNER JOIN, LEFT OUTER JOIN, RIGHT OUTER JOIN, and FULL OUTER JOIN with query examples, Venn diagrams, and result sets.",
        "marks": 8, "unit": "Unit III", "topic": "Joins, Subqueries & Aggregations",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain nested subqueries using IN, ANY, ALL, EXISTS, and NOT EXISTS operators with sample relational queries on customer accounts.",
        "marks": 8, "unit": "Unit III", "topic": "Joins, Subqueries & Aggregations",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "Formulate nested subqueries, correlated subqueries with EXISTS and NOT EXISTS, and demonstrate multi-table joins on a banking schema: Account, Customer, Branch, and Depositor to extract top customer transaction metrics.",
        "marks": 16, "unit": "Unit III", "topic": "Joins, Subqueries & Aggregations",
        "difficulty": "Hard", "bloom_level": "Analyze", "question_type": "Problem Solving"
    },

    # ------------------ UNIT IV ------------------
    # Lesson 1: ACID Properties & Transactions
    {
        "question_text": "State the ACID properties of a database transaction and identify which DBMS subsystem guarantees each property.",
        "marks": 2, "unit": "Unit IV", "topic": "ACID Properties & Transactions",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "What is a transaction schedule? Differentiate serial, non-serial, and serializable execution schedules.",
        "marks": 2, "unit": "Unit IV", "topic": "ACID Properties & Transactions",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain conflict serializability and view serializability. Detail the precedence graph (serialization graph) testing algorithm with an example schedule.",
        "marks": 8, "unit": "Unit IV", "topic": "ACID Properties & Transactions",
        "difficulty": "Medium", "bloom_level": "Analyze", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain transaction states with a state transition diagram: Active, Partially Committed, Failed, Aborted, and Committed states.",
        "marks": 8, "unit": "Unit IV", "topic": "ACID Properties & Transactions",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Describe transaction states with a state transition diagram. Explain the concept of recoverable, cascadeless, and strict execution schedules with illustrative schedule examples.",
        "marks": 16, "unit": "Unit IV", "topic": "ACID Properties & Transactions",
        "difficulty": "Hard", "bloom_level": "Understand", "question_type": "Descriptive"
    },

    # Lesson 2: Concurrency Control & Deadlock Protocols
    {
        "question_text": "What is the Two-Phase Locking (2PL) protocol? How does strict 2PL differ from rigorous 2PL?",
        "marks": 2, "unit": "Unit IV", "topic": "Concurrency Control & Deadlock Protocols",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the phantom read problem and dirty read problem occurring in concurrent transaction execution.",
        "marks": 2, "unit": "Unit IV", "topic": "Concurrency Control & Deadlock Protocols",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain timestamp-based concurrency control protocol and Thomas' Write Rule with step-by-step transaction read and write operations.",
        "marks": 8, "unit": "Unit IV", "topic": "Concurrency Control & Deadlock Protocols",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain lock-based concurrency control protocols: Shared and Exclusive locks, Lock conversion, and how basic 2PL prevents conflict inconsistency.",
        "marks": 8, "unit": "Unit IV", "topic": "Concurrency Control & Deadlock Protocols",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Descriptive"
    },
    {
        "question_text": "Discuss deadlock handling in database management systems: prevention schemes (Wait-Die, Wound-Wait), detection via Wait-For-Graph (WFG), and recovery techniques including victim selection and rollback.",
        "marks": 16, "unit": "Unit IV", "topic": "Concurrency Control & Deadlock Protocols",
        "difficulty": "Hard", "bloom_level": "Evaluate", "question_type": "Problem Solving"
    },

    # ------------------ UNIT V ------------------
    # Lesson 1: Indexing & B+ Trees
    {
        "question_text": "What is the primary difference between dense index and sparse index in file organization?",
        "marks": 2, "unit": "Unit V", "topic": "Indexing & B+ Trees",
        "difficulty": "Easy", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Define clustered and non-clustered indexing. Can a table have multiple clustered indices? Justify.",
        "marks": 2, "unit": "Unit V", "topic": "Indexing & B+ Trees",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the structure of a B+ Tree index. Describe node splitting and merging operations during key insertion and deletion with diagrams.",
        "marks": 8, "unit": "Unit V", "topic": "Indexing & B+ Trees",
        "difficulty": "Medium", "bloom_level": "Apply", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain Static Hashing vs Dynamic Hashing (Extendible Hashing and Linear Hashing) with directory and bucket overflow management.",
        "marks": 8, "unit": "Unit V", "topic": "Indexing & B+ Trees",
        "difficulty": "Medium", "bloom_level": "Analyze", "question_type": "Descriptive"
    },
    {
        "question_text": "Construct a B+ Tree of order 4 step-by-step for the key sequence: 10, 20, 30, 40, 50, 60, 70, 80, 90. Show the resulting tree structure and illustrate deletion of keys 20 and 50.",
        "marks": 16, "unit": "Unit V", "topic": "Indexing & B+ Trees",
        "difficulty": "Hard", "bloom_level": "Create", "question_type": "Problem Solving"
    },

    # Lesson 2: Query Processing & Optimization
    {
        "question_text": "What are the basic steps involved in processing an SQL query in a relational DBMS from parser to execution engine?",
        "marks": 2, "unit": "Unit V", "topic": "Query Processing & Optimization",
        "difficulty": "Easy", "bloom_level": "Remember", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain the role of catalog metadata and statistical histograms in cost-based query optimization.",
        "marks": 2, "unit": "Unit V", "topic": "Query Processing & Optimization",
        "difficulty": "Medium", "bloom_level": "Understand", "question_type": "Short Answer"
    },
    {
        "question_text": "Explain heuristic optimization rules for relational algebra query trees with an illustrative query transformation example.",
        "marks": 8, "unit": "Unit V", "topic": "Query Processing & Optimization",
        "difficulty": "Medium", "bloom_level": "Analyze", "question_type": "Descriptive"
    },
    {
        "question_text": "Explain external merge-sort algorithm for sorting large database files that do not fit into memory with disk I/O cost estimation.",
        "marks": 8, "unit": "Unit V", "topic": "Query Processing & Optimization",
        "difficulty": "Hard", "bloom_level": "Evaluate", "question_type": "Descriptive"
    },
    {
        "question_text": "Discuss query evaluation plans and cost estimation for Selection and Join operations (Nested-Loop Join, Block Nested-Loop, and Hash Join) with cost formulas and buffer allocation.",
        "marks": 16, "unit": "Unit V", "topic": "Query Processing & Optimization",
        "difficulty": "Hard", "bloom_level": "Evaluate", "question_type": "Problem Solving"
    }
]

def seed():
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Get faculty user id
        cur.execute("SELECT id FROM users WHERE role = 'faculty' LIMIT 1")
        fac = cur.fetchone()
        faculty_id = fac['id'] if fac else None

        dept = "Artificial Intelligence & Data Science"
        subj = "Database Management Systems"
        year = "2025-2026"
        sem = "Semester 6"

        inserted = 0
        for q in QUESTIONS_DATA:
            # Check if exists
            cur.execute("SELECT id FROM questions WHERE question_text = %s", (q["question_text"],))
            if cur.fetchone():
                continue

            sql = """
                INSERT INTO questions
                (question_text, subject, department, academic_year, semester, unit, topic,
                 question_type, difficulty, bloom_level, concept, explanation, marks, status, is_in_bank, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Bank', TRUE, %s)
            """
            cur.execute(sql, (
                q["question_text"], subj, dept, year, sem, q["unit"], q["topic"],
                q["question_type"], q["difficulty"], q["bloom_level"], q["topic"],
                f"Reference guide for {q['topic']}", q["marks"], faculty_id
            ))
            inserted += 1

        conn.commit()
        print(f"Successfully seeded {inserted} questions into MySQL Question Bank!")

        cur.execute("SELECT count(*) as total, sum(is_in_bank) as in_bank FROM questions")
        row = cur.fetchone()
        print(f"Total questions in DB: {row['total']}, In Question Bank: {row['in_bank']}")

    conn.close()

if __name__ == '__main__':
    seed()
