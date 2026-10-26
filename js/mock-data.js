/**
 * Mock Data Store for Academic Question Generation & Difficulty Balancing System
 */

const AcademicMockData = {
  // Official Departments
  departments: [
    "Artificial Intelligence & Data Science",
    "Artificial Intelligence & Machine Learning",
    "Computer and Communication Engineering"
  ],

  // Default Accounts
  facultyAccount: {
    id: "FAC-9082",
    name: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
    email: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").identifier) || "faculty@university.edu",
    department: "Artificial Intelligence & Data Science",
    designation: "Associate Professor",
    courses: [
      { code: "CS402", name: "Database Management Systems", students: 95 },
      { code: "CS505", name: "Artificial Intelligence", students: 88 },
      { code: "CS301", name: "Data Structures", students: 120 }
    ]
  },

  studentAccount: {
    id: "STU-2024-8841",
    name: (typeof localStorage !== 'undefined' && JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Student User",
    email: (typeof localStorage !== 'undefined' && JSON.parse(localStorage.getItem('academic_user') || '{}').identifier) || "student@university.edu",
    rollNo: "2024-AIDS-042",
    department: "Artificial Intelligence & Data Science",
    semester: "Semester 6",
    enrolledCourses: [
      { code: "CS402", name: "Database Management Systems", instructor: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member", attendance: "88%" },
      { code: "CS505", name: "Artificial Intelligence", instructor: "Prof. Sarah Jenkins", attendance: "95%" },
      { code: "CS301", name: "Data Structures", instructor: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member", attendance: "92%" },
      { code: "CS304", name: "Computer Networks", instructor: "Dr. Marcus Bell", attendance: "90%" }
    ]
  },

  // Published Quizzes Store (STEP 5)
  publishedQuizzes: [
    {
      quizId: "QUIZ-2026-0001",
      title: "DBMS SQL Basics Quiz",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      academicYear: "2025-2026",
      semester: "Semester 6",
      unit: "Unit III — SQL",
      topic: "SQL Commands & SELECT Statements",
      durationMins: 10,
      marksPerQuestion: 2,
      totalMarks: 10,
      status: "Published",
      createdDate: "18 Sep 2026",
      createdBy: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
      questions: [
        {
          id: "QZ-01",
          text: "Which SQL command is used to retrieve data from a database table?",
          options: ["INSERT", "SELECT", "UPDATE", "DELETE"],
          correctAnswer: "B. SELECT",
          correctIndex: 1,
          difficulty: "Easy",
          concept: "SQL Commands",
          blooms: "Remember",
          unit: "Unit III — SQL"
        },
        {
          id: "QZ-02",
          text: "Which SQL clause is used to filter rows based on a specific condition?",
          options: ["GROUP BY", "ORDER BY", "WHERE", "JOIN"],
          correctAnswer: "C. WHERE",
          correctIndex: 2,
          difficulty: "Easy",
          concept: "Filtering",
          blooms: "Understand",
          unit: "Unit III — SQL"
        },
        {
          id: "QZ-03",
          text: "Which SQL statement is used to modify existing records in a database?",
          options: ["UPDATE", "ALTER", "CHANGE", "MODIFY"],
          correctAnswer: "A. UPDATE",
          correctIndex: 0,
          difficulty: "Medium",
          concept: "SQL Commands",
          blooms: "Understand",
          unit: "Unit III — SQL"
        },
        {
          id: "QZ-04",
          text: "Which aggregate function returns the total number of rows matching a criteria?",
          options: ["SUM()", "COUNT()", "TOTAL()", "MAX()"],
          correctAnswer: "B. COUNT()",
          correctIndex: 1,
          difficulty: "Easy",
          concept: "Aggregate Functions",
          blooms: "Apply",
          unit: "Unit III — SQL"
        },
        {
          id: "QZ-05",
          text: "Which join returns all rows from the left table and matching rows from the right table?",
          options: ["INNER JOIN", "RIGHT JOIN", "LEFT JOIN", "FULL JOIN"],
          correctAnswer: "C. LEFT JOIN",
          correctIndex: 2,
          difficulty: "Medium",
          concept: "Joins",
          blooms: "Apply",
          unit: "Unit III — SQL"
        }
      ]
    }
  ],

  // Published Assignments Store (STEP 5)
  publishedAssignments: [
    {
      assignmentId: "ASSIGN-2026-0001",
      title: "SQL Query Practice Assignment",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      academicYear: "2025-2026",
      semester: "Semester 6",
      unit: "Unit III — SQL",
      topic: "Complex SQL Queries & Joins",
      type: "Problem Solving",
      dueDate: "2026-09-25",
      maxMarks: 50,
      instructions: "Solve all SQL queries. Submit complete statements along with brief explanations.",
      status: "Published",
      createdDate: "18 Sep 2026",
      createdBy: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
      questions: [
        { num: 1, text: "Explain the difference between DDL and DML commands with suitable syntax examples.", marks: 10, difficulty: "Easy", concept: "SQL Commands", blooms: "Understand" },
        { num: 2, text: "Write SQL queries to retrieve employee records where salary > $60,000 using WHERE conditions.", marks: 10, difficulty: "Medium", concept: "Filtering", blooms: "Apply" },
        { num: 3, text: "Explain GROUP BY and aggregate functions (COUNT, AVG, SUM) with suitable relational examples.", marks: 10, difficulty: "Medium", concept: "Aggregate Functions", blooms: "Understand" },
        { num: 4, text: "Design SQL queries demonstrating INNER JOIN, LEFT JOIN, and RIGHT JOIN on Employee and Department tables.", marks: 10, difficulty: "Hard", concept: "Joins", blooms: "Apply" },
        { num: 5, text: "Analyze a multi-table database scenario and construct a nested subquery to find top 3 departments by average score.", marks: 10, difficulty: "Hard", concept: "Complex Queries", blooms: "Analyze" }
      ]
    }
  ],

  // Student History & Attempts (STEP 5)
  studentQuizHistory: [
    {
      quizId: "QUIZ-2026-0001",
      title: "DBMS SQL Basics Quiz",
      subject: "Database Management Systems",
      score: "8 / 10",
      correct: 4,
      total: 5,
      percentage: "80%",
      date: "18 Sep 2026",
      conceptPerformance: {
        "SQL Commands": true,
        "Filtering": true,
        "Aggregate Functions": true,
        "Joins": false
      }
    }
  ],

  studentAssignmentSubmissions: [
    {
      assignmentId: "ASSIGN-2026-0001",
      title: "SQL Query Practice Assignment",
      subject: "Database Management Systems",
      submittedDate: "18 Sep 2026",
      status: "Submitted",
      answers: {
        "Q1": "DDL commands (CREATE, ALTER, DROP) define database schema. DML commands (SELECT, INSERT, UPDATE, DELETE) manipulate data.",
        "Q2": "SELECT * FROM Employees WHERE Salary > 60000;"
      }
    }
  ],

  // Published Question Papers Store (STEP 4)
  publishedQuestionPapers: [
    {
      paperId: "EXAM-2026-0001",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      examType: "Model Examination",
      academicYear: "2025-2026",
      semester: "Semester 6",
      examDate: "2026-10-15",
      examTime: "10:00 AM - 01:00 PM",
      duration: "3 Hours",
      maxMarks: 100,
      instructions: "1. Answer all questions in Section A.\n2. Answer the required questions in Section B.\n3. Assume suitable data wherever necessary.",
      status: "Published",
      fingerprint: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      qrPayload: "EXAM-2026-0001|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      createdBy: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
      createdDate: "18 Sep 2026",
      questions: [
        { num: 1, text: "What is a database management system?", marks: 2, section: "A", difficulty: "Easy", concept: "DBMS Basics" },
        { num: 2, text: "Define primary key and foreign key constraints.", marks: 2, section: "A", difficulty: "Easy", concept: "Integrity Constraints" },
        { num: 3, text: "Explain DDL vs DML commands with syntax.", marks: 6, section: "B", difficulty: "Medium", concept: "SQL Commands" },
        { num: 4, text: "Design an optimized 3-way JOIN SQL query for department salaries.", marks: 10, section: "C", difficulty: "Hard", concept: "SQL Joins" }
      ]
    }
  ],

  // Subject -> Units & Topics Mapping
  subjectStructure: {
    "Database Management Systems": {
      units: [
        { id: "U1", name: "Unit I — Introduction to DBMS", topics: ["Database Architecture", "DBMS vs File System", "ER Model", "Data Models"] },
        { id: "U2", name: "Unit II — Relational Model", topics: ["Relational Algebra", "Tuple Calculus", "Integrity Constraints", "Keys"] },
        { id: "U3", name: "Unit III — SQL", topics: ["SQL Queries", "DDL & DML Commands", "GROUP BY & Having", "Joins & Subqueries", "Aggregate Functions"] },
        { id: "U4", name: "Unit IV — Normalization", topics: ["Functional Dependencies", "1NF & 2NF", "3NF & BCNF", "Decomposition"] },
        { id: "U5", name: "Unit V — Transactions", topics: ["ACID Properties", "Concurrency Control", "Two-Phase Locking", "Deadlocks"] }
      ]
    },
    "Artificial Intelligence": {
      units: [
        { id: "U1", name: "Unit I — AI Fundamentals & Search", topics: ["State Space Search", "Uninformed Search (BFS/DFS)", "Heuristic Search (A*)", "Adversarial Search (Minimax)"] },
        { id: "U2", name: "Unit II — Knowledge Representation", topics: ["Propositional Logic", "First-Order Logic", "Ontologies", "Semantic Networks"] }
      ]
    },
    "Machine Learning": {
      units: [
        { id: "U1", name: "Unit I — Supervised Learning", topics: ["Linear Regression", "Logistic Regression", "Decision Trees", "Support Vector Machines (SVM)"] },
        { id: "U2", name: "Unit II — Unsupervised Learning", topics: ["K-Means Clustering", "Hierarchical Clustering", "Principal Component Analysis (PCA)"] }
      ]
    },
    "Data Structures": {
      units: [
        { id: "U1", name: "Unit I — Linear Structures", topics: ["Arrays", "Linked Lists", "Stacks & Queues"] },
        { id: "U2", name: "Unit II — Non-Linear Structures", topics: ["Binary Search Trees", "AVL Trees", "B-Trees", "Heaps"] }
      ]
    }
  },

  // Master Question Pool
  masterQuestionsPool: [
    {
      id: "Q011",
      subject: "Database Management Systems",
      unit: "Unit III — SQL",
      topic: "SQL Queries",
      concept: "DBMS Basics",
      question: "What is a database management system, and what are its primary objectives in modern enterprise software?",
      difficulty: "Easy",
      type: "Short Answer",
      blooms: "Remember",
      marks: 2,
      similarityPairId: "SIM-01"
    },
    {
      id: "Q012",
      subject: "Database Management Systems",
      unit: "Unit III — SQL",
      topic: "SQL Commands",
      concept: "SQL Commands",
      question: "Explain the difference between DDL and DML commands with suitable examples.",
      difficulty: "Medium",
      type: "Short Answer",
      blooms: "Understand",
      marks: 6
    }
  ],

  // Faculty Academic Resources Data
  academicResources: [
    {
      id: "RES-101",
      name: "DBMS Syllabus 2026",
      type: "Syllabus",
      subject: "Database Management Systems",
      department: "Artificial Intelligence & Data Science",
      year: "2025-2026",
      semester: "Semester 6",
      unit: "All Units",
      topic: "Course Overview & Learning Outcomes",
      fileName: "DBMS_Syllabus_2026.pdf",
      fileType: "application/pdf",
      uploadedDate: "18 Sep 2026",
      status: "Analyzed",
      publishedToStudents: true
    }
  ],

  // Faculty Question Bank Repository Storage
  facultyQuestionBank: [
    {
      id: "Q011",
      department: "Artificial Intelligence & Data Science",
      course: "Database Management Systems",
      topic: "SQL Queries",
      text: "What is a database management system, and what are its primary objectives in modern enterprise software?",
      difficulty: "Easy",
      bloomsTaxonomy: "Remember",
      type: "Short Answer",
      concept: "DBMS Basics",
      unit: "Unit I — Introduction to DBMS",
      marks: 2,
      dateAdded: "2026-09-10"
    }
  ],

  // Published PPT Presentations Store (STEP 6)
  publishedPPTs: [
    {
      id: "PPT-2026-0001",
      title: "SQL Join Operations & Query Optimization",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      academicYear: "2025-2026",
      semester: "Semester 6",
      unit: "Unit III — SQL",
      topic: "Joins & Subqueries",
      sourceMaterial: "DBMS Syllabus 2026 (RES-101)",
      slideCount: 8,
      presentationType: "Classroom Teaching",
      status: "Published",
      createdAt: "18 Sep 2026",
      publishedAt: "18 Sep 2026",
      createdBy: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
      slides: [
        {
          slideNum: 1,
          title: "SQL Join Operations & Query Optimization",
          content: "Comprehensive Overview of Relational Joins in DBMS",
          bullets: ["Department: AI & Data Science", "Course: CS402 Database Management Systems", "Instructor: Faculty Member"],
          example: "",
          visualSuggestion: "College Logo & Course Title Header Banner"
        },
        {
          slideNum: 2,
          title: "Learning Objectives",
          content: "What students will master by the end of this presentation:",
          bullets: ["Understand INNER, LEFT, RIGHT, and FULL OUTER JOINs", "Formulate complex multi-table SQL queries", "Analyze query execution plans and performance bottlenecks"],
          example: "",
          visualSuggestion: "Objective Checklist Diagram with Checkmark Badges"
        },
        {
          slideNum: 3,
          title: "Introduction to Relational Joins",
          content: "Combining tuples from two or more relations based on related columns.",
          bullets: ["Primary Key - Foreign Key relationships form the basis of joins.", "Cross Join produces Cartesian Product (N × M tuples).", "Inner Join filters tuples matching the join condition."],
          example: "SELECT * FROM Students JOIN Enrolments ON Students.id = Enrolments.sid;",
          visualSuggestion: "Venn Diagram showing intersecting sets A ∩ B"
        },
        {
          slideNum: 4,
          title: "INNER JOIN vs OUTER JOIN",
          content: "Distinction between matching and unmatched tuple retention:",
          bullets: ["INNER JOIN: Returns only matching rows from both tables.", "LEFT OUTER JOIN: Returns all rows from left table + matched right rows.", "RIGHT OUTER JOIN: Returns all rows from right table + matched left rows."],
          example: "SELECT E.name, D.dept_name FROM Emp E LEFT JOIN Dept D ON E.did = D.id;",
          visualSuggestion: "Side-by-side comparison table of Join results"
        },
        {
          slideNum: 5,
          title: "Multi-Table Joins & Complex Syntax",
          content: "Joining 3 or more tables in enterprise data retrieval.",
          bullets: ["Use clear table aliases (e.g., E for Employees, D for Departments).", "Ensure proper indexing on foreign key columns for speed.", "Avoid unindexed cross-joins in production databases."],
          example: "SELECT S.name, C.course_title FROM Students S JOIN Marks M ON S.id = M.sid JOIN Courses C ON M.cid = C.id;",
          visualSuggestion: "Relational Schema ER Graph with Join Connectors"
        },
        {
          slideNum: 6,
          title: "Query Optimization & Index Usage",
          content: "How the Query Engine processes joins efficiently:",
          bullets: ["Nested Loop Join vs Hash Join vs Sort-Merge Join algorithms.", "Indexing join columns reduces cost from O(N*M) to O(N log M).", "EXPLAIN ANALYZE command reveals execution cost."],
          example: "EXPLAIN ANALYZE SELECT * FROM Orders O JOIN Customers C ON O.cid = C.id;",
          visualSuggestion: "Query Execution Tree Diagram"
        },
        {
          slideNum: 7,
          title: "Summary & Key Takeaways",
          content: "Essential points for examination and practical database design:",
          bullets: ["Always specify explicit JOIN syntax rather than implicit comma joins.", "Verify Foreign Key constraints to prevent orphan records.", "Use LEFT JOIN when missing relationship data must be preserved."],
          example: "",
          visualSuggestion: "Summary Infographic Box"
        },
        {
          slideNum: 8,
          title: "Review Questions & Practice",
          content: "Self-assessment questions for students:",
          bullets: ["Q1: What is the result of a LEFT JOIN if no match exists in the right table?", "Q2: Write an SQL query to find employees with no assigned department.", "Q3: Compare Hash Join and Nested Loop Join execution speeds."],
          example: "",
          visualSuggestion: "Q&A Helpdesk Icon Banner"
        }
      ]
    }
  ],

  // Published Lesson Plans Store (STEP 6)
  publishedLessonPlans: [
    {
      id: "LP-2026-0001",
      title: "Transaction Processing & ACID Properties",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      academicYear: "2025-2026",
      semester: "Semester 6",
      unit: "Unit V — Transactions",
      topic: "ACID Properties & Concurrency",
      sourceMaterial: "DBMS Syllabus 2026 (RES-101)",
      duration: "45 minutes",
      teachingMethod: "Demonstration & Problem Solving",
      status: "Published",
      createdAt: "18 Sep 2026",
      publishedAt: "18 Sep 2026",
      createdBy: (typeof localStorage !== "undefined" && JSON.parse(localStorage.getItem("academic_user") || "{}").name) || "Faculty Member",
      objectives: "1. Define a transaction as a logical unit of database work.\n2. Explain the four ACID properties with bank transfer examples.\n3. Identify concurrency anomalies such as dirty reads and lost updates.",
      prerequisites: "Basic understanding of SQL SELECT, UPDATE, and relational schema concepts.",
      concepts: "Atomicity, Consistency, Isolation, Durability, Transaction States (Active, Partially Committed, Committed, Failed, Aborted), Lock Protocols.",
      activities: "Interactive live terminal demonstration of concurrent SQL transactions using PostgreSQL/MySQL sessions.",
      resources: "Classroom Projector, DBMS Reference Textbook (Chapter 14), Database Server Terminal Tool.",
      explanationPoints: "1. Atomicity: All or nothing execution principle.\n2. Consistency: Database transitions from one valid state to another.\n3. Isolation: Concurrent transactions execute independently without mutual interference.\n4. Durability: Committed changes survive system failures.",
      studentActivities: "Students form pairs to trace transaction execution logs and identify concurrency conflicts on worksheet.",
      assessment: "5-minute pop quiz asking students to categorize real-world scenarios into Atomicity, Consistency, Isolation, or Durability failures.",
      homework: "Solve Exercise Questions 14.1 to 14.5 from Unit V textbook chapter on Two-Phase Locking.",
      outcomes: "Students will be capable of diagnosing transaction deadlocks and selecting appropriate isolation levels in production databases.",
      summary: "Transaction processing guarantees data integrity and concurrency safety in multi-user database engines.",
      timeline: [
        { time: "0–5 min", activity: "Introduction & Motivation", facultyRole: "Present real-world banking failure scenario during network disconnect.", studentRole: "Listen and answer warm-up questions." },
        { time: "5–15 min", activity: "Concept Explanation (ACID)", facultyRole: "Explain Atomicity, Consistency, Isolation, and Durability using slides.", studentRole: "Take notes and highlight key definitions." },
        { time: "15–30 min", activity: "Live Demonstration", facultyRole: "Execute dual terminal SQL commands showing concurrent updates and locks.", studentRole: "Observe state changes and note transaction status." },
        { time: "30–40 min", activity: "Student Pair Activity", facultyRole: "Distribute log worksheets and guide student pairs.", studentRole: "Analyze transaction logs and identify isolation errors." },
        { time: "40–45 min", activity: "Assessment & Summary", facultyRole: "Conduct 5-min pop quiz and summarize core takeaways.", studentRole: "Complete assessment and clarify doubts." }
      ]
    }
  ],

  // Published Voice Questions Store (STEP 7)
  publishedVoiceQuestions: [
    {
      id: "VOICE-2026-0001",
      transcript: "Generate five medium difficulty questions about SQL joins for DBMS.",
      language: "en-IN",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      unit: "Unit III — SQL",
      topic: "Joins & Subqueries",
      count: 5,
      difficulty: "Medium",
      createdAt: "19 Sep 2026",
      questions: [
        {
          num: 1,
          question: "Differentiate between INNER JOIN and LEFT OUTER JOIN with a relational database query example.",
          difficulty: "Medium",
          type: "Short Answer",
          blooms: "Understand",
          concept: "Relational Joins",
          similarityStatus: "Unique Concept"
        },
        {
          num: 2,
          question: "Explain the performance implications of executing an unindexed CROSS JOIN on two large tables.",
          difficulty: "Hard",
          type: "Descriptive",
          blooms: "Analyze",
          concept: "Query Optimization",
          similarityStatus: "Unique Concept"
        }
      ]
    }
  ],

  // Published Image / Diagram Questions Store (STEP 7)
  publishedImageQuestions: [
    {
      id: "IMG-2026-0001",
      fileName: "er_diagram_university.png",
      fileType: "image/png",
      fileSize: "245 KB",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      unit: "Unit I — Introduction to DBMS",
      topic: "ER Model",
      description: "Entity-Relationship diagram showing Student, Course, and Enrollment entities with primary/foreign key attributes.",
      createdAt: "19 Sep 2026",
      questions: [
        {
          num: 1,
          question: "Identify the entity types and their relationship cardinality depicted in the uploaded ER diagram.",
          difficulty: "Medium",
          type: "Diagram Interpretation",
          blooms: "Analyze",
          concept: "ER Model Cardinality",
          imageRef: "er_diagram_university.png"
        },
        {
          num: 2,
          question: "Based on the diagram schema, convert the multivalued attribute into a normalized 3NF relational table.",
          difficulty: "Hard",
          type: "Problem Solving",
          blooms: "Apply",
          concept: "ER-to-Relational Mapping",
          imageRef: "er_diagram_university.png"
        }
      ]
    }
  ],

  // Published Translated Questions Store (STEP 7)
  publishedTranslatedQuestions: [
    {
      id: "TRANS-2026-0001",
      sourceLanguage: "English",
      targetLanguage: "Tamil",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      unit: "Unit IV — Normalization",
      topic: "Functional Dependencies",
      difficulty: "Medium",
      questionType: "Short Answer",
      bloomLevel: "Understand",
      concept: "Database Normalization",
      originalQuestion: "What is the primary purpose of normalization in DBMS, and how does 3NF eliminate transitive dependencies?",
      translatedQuestion: "தரவுத்தள மேலாண்மை அமைப்பில் (DBMS) Normalization-ன் முக்கிய நோக்கம் என்ன, மற்றும் 3NF எவ்வாறு Transitive Dependencies-ஐ நீக்குகிறது?",
      createdAt: "19 Sep 2026"
    }
  ],

  // STEP 8: Demo Student Results Store
  demoStudentResults: [
    {
      id: "RES-2026-0001",
      title: "DBMS Unit III Quick Assessment",
      type: "Quiz",
      subject: "Database Management Systems",
      department: "Artificial Intelligence & Data Science",
      dateCompleted: "18 Sep 2026",
      score: 8,
      totalMarks: 10,
      percentage: 80,
      academicStatus: "Good Progress",
      questions: [
        {
          num: 1,
          question: "Which SQL join returns all rows from the left table and matched rows from the right table?",
          userAnswer: "LEFT OUTER JOIN",
          correctAnswer: "LEFT OUTER JOIN",
          isCorrect: true,
          concept: "Relational Joins",
          difficulty: "Easy",
          blooms: "Remember",
          explanation: "LEFT JOIN retains all tuples from the left relation, substituting NULL for missing right matches."
        },
        {
          num: 2,
          question: "What is the result of an unindexed CROSS JOIN between Table A (100 rows) and Table B (500 rows)?",
          userAnswer: "50,000 Cartesian tuples",
          correctAnswer: "50,000 Cartesian tuples",
          isCorrect: true,
          concept: "Query Execution",
          difficulty: "Medium",
          blooms: "Understand",
          explanation: "Cartesian product length is equal to N x M = 100 x 500 = 50,000 rows."
        },
        {
          num: 3,
          question: "Which normal form eliminates transitive functional dependencies?",
          userAnswer: "Second Normal Form (2NF)",
          correctAnswer: "Third Normal Form (3NF)",
          isCorrect: false,
          concept: "Database Normalization",
          difficulty: "Medium",
          blooms: "Analyze",
          explanation: "3NF requires that no non-prime attribute is transitively dependent on any candidate key."
        },
        {
          num: 4,
          question: "What does the ACID property 'Atomicity' guarantee in DBMS transactions?",
          userAnswer: "All operations execute completely or none execute",
          correctAnswer: "All operations execute completely or none execute",
          isCorrect: true,
          concept: "Transaction Processing",
          difficulty: "Hard",
          blooms: "Evaluate",
          explanation: "Atomicity enforces the 'all or nothing' execution paradigm for database transaction units."
        },
        {
          num: 5,
          question: "Which index structure is best suited for range queries in relational databases?",
          userAnswer: "B+ Tree Index",
          correctAnswer: "B+ Tree Index",
          isCorrect: true,
          concept: "Indexing & Hashing",
          difficulty: "Hard",
          blooms: "Apply",
          explanation: "B+ Trees maintain sorted leaf nodes linked in a doubly linked list, enabling fast range scans."
        }
      ]
    },
    {
      id: "RES-2026-0002",
      title: "Python Data Structures & OOP Quiz",
      type: "Quiz",
      subject: "Python Programming",
      department: "Artificial Intelligence & Data Science",
      dateCompleted: "16 Sep 2026",
      score: 9,
      totalMarks: 10,
      percentage: 90,
      academicStatus: "Strong",
      questions: [
        {
          num: 1,
          question: "What is the time complexity of searching a key in a Python dictionary on average?",
          userAnswer: "O(1)",
          correctAnswer: "O(1)",
          isCorrect: true,
          concept: "Dictionary Data Structure",
          difficulty: "Easy",
          blooms: "Remember",
          explanation: "Python dictionaries use hash tables offering O(1) average lookup complexity."
        }
      ]
    }
  ],

  // STEP 8: Demo Assignment Submissions Store
  demoAssignmentEvaluations: [
    {
      id: "SUB-2026-0001",
      title: "Database Normalization & BCNF Design Case Study",
      type: "Assignment",
      studentName: (typeof localStorage !== 'undefined' && JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Student User",
      registerNum: "710023104042",
      department: "Artificial Intelligence & Data Science",
      subject: "Database Management Systems",
      dateSubmitted: "18 Sep 2026",
      score: 44,
      maxMarks: 50,
      percentage: 88,
      academicStatus: "Strong",
      status: "Evaluated",
      facultyFeedback: "Excellent normalization decomposition diagram and clear functional dependency proof.",
      submittedFile: "Rohan_Sharma_DBMS_Assignment1.pdf"
    },
    {
      id: "SUB-2026-0002",
      title: "AI Search Algorithms Comparison Report",
      type: "Assignment",
      studentName: (typeof localStorage !== 'undefined' && JSON.parse(localStorage.getItem('academic_user') || '{}').name) || "Student User",
      registerNum: "710023104042",
      department: "Artificial Intelligence & Data Science",
      subject: "Artificial Intelligence & Machine Learning",
      dateSubmitted: "19 Sep 2026",
      score: 0,
      maxMarks: 50,
      percentage: 0,
      academicStatus: "Evaluation Pending",
      status: "Evaluation Pending",
      facultyFeedback: "Pending review by subject instructor.",
      submittedFile: "Rohan_Sharma_AI_Search_Report.pdf"
    }
  ],

  // STEP 8: Demo Student Activity Log Store
  demoStudentHistory: [
    {
      id: "HIST-S-001",
      timestamp: "19 Sep 2026, 11:30 AM",
      category: "Quiz",
      title: "Attempted DBMS Unit III Quick Assessment",
      details: "Score: 8/10 (80%) — Academic Status: Good Progress",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-S-002",
      timestamp: "19 Sep 2026, 09:15 AM",
      category: "Assignment",
      title: "Submitted Assignment: AI Search Algorithms Comparison Report",
      details: "File: Rohan_Sharma_AI_Search_Report.pdf | Status: Submitted",
      subject: "Artificial Intelligence & Machine Learning"
    },
    {
      id: "HIST-S-003",
      timestamp: "18 Sep 2026, 04:20 PM",
      category: "Study Material",
      title: "Downloaded Resource: SQL Joins Reference Manual (RES-102)",
      details: "Format: PDF | Size: 1.8 MB",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-S-004",
      timestamp: "18 Sep 2026, 02:00 PM",
      category: "Presentation",
      title: "Viewed PPT: SQL Join Operations & Query Optimization",
      details: "Slide count: 8 slides reviewed",
      subject: "Database Management Systems"
    }
  ],

  // STEP 8: Demo Faculty Activity Log Store
  demoFacultyHistory: [
    {
      id: "HIST-F-001",
      timestamp: "19 Sep 2026, 10:15 AM",
      category: "Exam Paper",
      title: "Generated & Fingerprinted Question Paper (QP-2026-8941)",
      details: "Subject: Database Management Systems | SHA-256: 4a8f9c... | QR Verified",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-F-002",
      timestamp: "19 Sep 2026, 08:45 AM",
      category: "AI Questions",
      title: "Generated 10 AI Questions from Voice Input",
      details: "Topic: SQL Joins | Language: English (en-IN)",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-F-003",
      timestamp: "18 Sep 2026, 03:30 PM",
      category: "Quiz",
      title: "Created & Published Timed Quiz: DBMS Unit III Quick Assessment",
      details: "Duration: 15 mins | 5 Questions | Auto-Scoring Enabled",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-F-004",
      timestamp: "18 Sep 2026, 01:10 PM",
      category: "Presentation",
      title: "Generated Classroom PPT: SQL Join Operations & Query Optimization",
      details: "Slide count: 8 slides | Visual prompts included",
      subject: "Database Management Systems"
    },
    {
      id: "HIST-F-005",
      timestamp: "17 Sep 2026, 11:00 AM",
      category: "Lesson Plan",
      title: "Generated Lesson Plan: Transaction Processing & ACID Properties",
      details: "Duration: 45 mins | Interactive Pair Activity",
      subject: "Database Management Systems"
    }
  ]
};

