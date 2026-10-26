import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='sqlamzad@123',
    database='academic_question_system',
    cursorclass=pymysql.cursors.DictCursor
)

questions_to_add = [
    # 2-mark questions (Units I to V)
    ("What is Data Redundancy and how does DBMS reduce it?", 2, "Unit I", "Remember", "Easy", "Data Independence", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Define Primary Key and Foreign Key with an example.", 2, "Unit I", "Remember", "Easy", "Relational Keys", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("State the differences between DDL and DML commands in SQL.", 2, "Unit II", "Understand", "Medium", "SQL Commands", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is an Entity-Relationship (ER) model? Name its core components.", 2, "Unit II", "Remember", "Easy", "ER Modeling", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Define Functional Dependency in relational databases.", 2, "Unit III", "Understand", "Medium", "Functional Dependencies", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is Boyce-Codd Normal Form (BCNF)? State its condition.", 2, "Unit III", "Remember", "Medium", "Normalization", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Explain the difference between 3NF and BCNF.", 2, "Unit III", "Understand", "Medium", "Normalization Comparison", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is a Transaction? List its four essential ACID properties.", 2, "Unit IV", "Remember", "Easy", "ACID Properties", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Explain Serializability and its significance in transaction processing.", 2, "Unit IV", "Understand", "Medium", "Serializability", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is Deadlock in DBMS? Name two methods for deadlock handling.", 2, "Unit IV", "Understand", "Medium", "Deadlock Prevention", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is a B+ Tree index? Why is it preferred over B Tree in databases?", 2, "Unit V", "Understand", "Medium", "B+ Tree Indexing", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Distinguish between Dense Index and Sparse Index.", 2, "Unit V", "Remember", "Easy", "Indexing Techniques", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("What is Static Hashing and Dynamic Hashing?", 2, "Unit V", "Understand", "Medium", "Hashing Techniques", "Database Management Systems", "Artificial Intelligence & Data Science", 24),

    # 16-mark questions (Units I to V)
    ("Explain the Three-Schema Architecture of DBMS with a neat diagram and discuss physical and logical data independence in detail.", 16, "Unit I", "Understand", "Medium", "Three-Schema Architecture", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Design an Entity-Relationship (ER) diagram for a University Management System including Entities, Attributes, Relationships, and Cardinality Constraints. Map it to Relational Schema.", 16, "Unit I", "Apply", "Hard", "ER Modeling & Relational Mapping", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Discuss Relational Algebra operations (Select, Project, Cartesian Product, Join, Union, Intersection, Difference) with suitable examples and formal notation.", 16, "Unit II", "Understand", "Medium", "Relational Algebra", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Formulate complex SQL queries using Aggregate Functions, Nested Subqueries, Correlated Subqueries, and GROUP BY / HAVING clauses with sample database tables.", 16, "Unit II", "Apply", "Medium", "Advanced SQL", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Explain the normalization process from First Normal Form (1NF) up to Boyce-Codd Normal Form (BCNF) with illustrative relation schemas and functional dependencies.", 16, "Unit III", "Apply", "Hard", "Normalization 1NF-BCNF", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Discuss Multi-Valued Dependencies and 4NF, along with Join Dependencies and 5NF, using appropriate practical examples.", 16, "Unit III", "Analyze", "Hard", "Higher Normal Forms", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Explain Concurrency Control Protocols: Lock-Based Protocols, Two-Phase Locking (2PL), Timestamp-Based Protocols, and Validation-Based Protocols in detail.", 16, "Unit IV", "Analyze", "Hard", "Concurrency Control Protocols", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Discuss Database Recovery Techniques: Log-Based Recovery (Deferred and Immediate Update) and Checkpoints with relevant scenarios.", 16, "Unit IV", "Understand", "Medium", "Database Recovery", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Explain B+ Tree indexing in detail. Illustrate insertion and deletion operations in a B+ Tree with step-by-step diagrams.", 16, "Unit V", "Analyze", "Hard", "B+ Tree Indexing Operations", "Database Management Systems", "Artificial Intelligence & Data Science", 24),
    ("Describe Query Processing and Optimization steps in detail, including Query Parsing, Translation to Relational Algebra, and Cost Estimation.", 16, "Unit V", "Understand", "Hard", "Query Optimization", "Database Management Systems", "Artificial Intelligence & Data Science", 24)
]

with conn.cursor() as cur:
    for q in questions_to_add:
        # Check if already exists for faculty 24
        cur.execute("SELECT id FROM questions WHERE question_text = %s AND created_by = %s", (q[0], q[8]))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO questions (
                    question_text, marks, unit, bloom_level, difficulty, topic, subject, department, created_by, is_in_bank, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
            """, q)
    conn.commit()
    print(f"Successfully ensured Murugan (ID 24) has standard DBMS questions.")

conn.close()
