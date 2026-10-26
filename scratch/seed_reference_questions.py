# -*- coding: utf-8 -*-
"""
Seed questions from reference papers:
1. Machine Learning (AL 3451) from April May 2024 ML.pdf
   - 2-mark questions (Part A, Q1-Q10)
   - 8-mark & 5-mark subquestions (Part B, Q11-Q15)
   - 13-mark questions (Part B alternatives)
   - 15-mark comprehensive questions (Part C, Q16)
2. Big Data Analytics (23ADT502) from inter.pdf
   - 2-mark questions (Part A, Q1-Q5)
   - 8-mark questions (Part B & Part C subquestions)
   - 16-mark questions (Part C alternatives)
3. Complementary 5-mark, 13-mark, and 15-mark questions for DBMS so all templates generate smoothly.
"""

import sys
import os

sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")
from models.database import get_db_connection

ML_QUESTIONS = [
    # --- ML PART A (2 Marks) ---
    {
        "question_text": "Name any four applications of machine learning.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Machine Learning Foundations",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Spam filtering, medical diagnosis, recommendation systems, autonomous vehicles.",
        "is_in_bank": True
    },
    {
        "question_text": "What is hypothesis in machine learning?",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Machine Learning Foundations",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Understand",
        "question_type": "Short Answer",
        "explanation": "A hypothesis is a candidate function that approximates the target function mapping inputs to outputs.",
        "is_in_bank": True
    },
    {
        "question_text": "Define linear regression.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Linear Models & Regression",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Linear regression models the relationship between a scalar dependent variable y and one or more explanatory variables x.",
        "is_in_bank": True
    },
    {
        "question_text": "Mention the advantages of decision tree classification algorithm.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Tree-Based Models",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Understand",
        "question_type": "Short Answer",
        "explanation": "Easy to interpret and visualize, handles both numerical and categorical data, requires minimal data preprocessing.",
        "is_in_bank": True
    },
    {
        "question_text": "Comment your answer 'Voting mechanism plays a major role in ensemble learning'.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit III",
        "topic": "Ensemble Learning",
        "marks": 2,
        "difficulty": "Medium",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Voting combines predictions from multiple diverse base estimators via majority or weighted voting to reduce variance and error.",
        "is_in_bank": True
    },
    {
        "question_text": "Differentiate supervised and unsupervised learning mechanism.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Learning Paradigms",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Understand",
        "question_type": "Short Answer",
        "explanation": "Supervised learning uses labeled training data; unsupervised learning discovers hidden patterns from unlabeled inputs.",
        "is_in_bank": True
    },
    {
        "question_text": "Identify the purpose of activation functions in Neural networks.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Neural Networks & Perceptrons",
        "marks": 2,
        "difficulty": "Medium",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Activation functions introduce non-linearities, enabling deep neural networks to learn complex decision boundaries.",
        "is_in_bank": True
    },
    {
        "question_text": "Interpret the process of batch normalization.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Deep Neural Networks",
        "marks": 2,
        "difficulty": "Medium",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Batch normalization standardizes layer inputs across mini-batches, stabilizing training and accelerating convergence.",
        "is_in_bank": True
    },
    {
        "question_text": "Write the importance of cross validation.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit V",
        "topic": "Model Evaluation & Validation",
        "marks": 2,
        "difficulty": "Easy",
        "bloom_level": "Understand",
        "question_type": "Short Answer",
        "explanation": "Cross-validation provides an unbiased estimate of generalization performance and mitigates overfitting on fixed train-test splits.",
        "is_in_bank": True
    },
    {
        "question_text": "'Test is used to assess the performance of machine learning algorithms'. Justify.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit V",
        "topic": "Hypothesis Testing & Assessment",
        "marks": 2,
        "difficulty": "Medium",
        "bloom_level": "Remember",
        "question_type": "Short Answer",
        "explanation": "Statistical hypothesis testing evaluates whether performance differences between algorithms are statistically significant.",
        "is_in_bank": True
    },

    # --- ML PART B (Subquestions: 8 Marks & 5 Marks, Single: 13 Marks) ---
    # Unit I
    {
        "question_text": "Explain Vapnik-Chervonenkis (VC) dimension and Probably Approximately Correct (PAC) learning in machine learning.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Computational Learning Theory",
        "marks": 8,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "PAC learning framework, sample complexity bounds, shattering concept, and VC dimension definition.",
        "is_in_bank": True
    },
    {
        "question_text": "Describe the Inductive Bias in machine learning.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Inductive Learning & Bias",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Inductive bias represents the set of assumptions learners use to predict outputs of unseen inputs.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain the review of linear algebra in machine learning with matrix operations, eigenvalues, and transformations.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit I",
        "topic": "Linear Algebra for ML",
        "marks": 13,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Vectors, matrices, matrix decompositions (SVD, Eigen-decomposition), and projections in feature space.",
        "is_in_bank": True
    },

    # Unit II
    {
        "question_text": "Find the linear regression equation for the given dataset with coordinates (1.0, 1.6), (1.5, 2.0), (3.0, 4.0), (5.0, 7.0), (3.5, 5.0), (4.5, 5.0), (3.5, 4.5), (6.5, 7.5), (7.5, 8.0), (9.5, 10.0) and identify the B1 value for A1(8.0).",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Linear Regression Analysis",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Analyze",
        "question_type": "Problem Solving",
        "explanation": "Least squares computation: slope m, intercept c, regression line equation, and predicted value evaluation.",
        "is_in_bank": True
    },
    {
        "question_text": "Draw the architecture of single layer perceptron and explain its operations.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Perceptrons & Linear Separability",
        "marks": 8,
        "difficulty": "Medium",
        "bloom_level": "Analyze",
        "question_type": "Descriptive",
        "explanation": "Perceptron architecture diagram, weight summation, thresholding function, and learning rule update.",
        "is_in_bank": True
    },
    {
        "question_text": "Identify and explain the features of support vector in Support Vector Machine classification technique.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Support Vector Machines",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Analyze",
        "question_type": "Descriptive",
        "explanation": "Support vectors lie on the marginal hyperplanes; maximal margin classifier properties and geometric interpretation.",
        "is_in_bank": True
    },

    # Unit III
    {
        "question_text": "Apply K-Means clustering to given sample instances into 3 clusters and trace cluster centroid updates across iterations.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit III",
        "topic": "Clustering Algorithms",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Problem Solving",
        "explanation": "Distance calculation using Euclidean metric, assignment to closest centroids, recalculation of centroids.",
        "is_in_bank": True
    },
    {
        "question_text": "Apply KNN classification algorithm with K=3 for iris dataset instances and predict the class for sepal length=5.9, petal length=5.2, petal width=1.8.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit III",
        "topic": "K-Nearest Neighbors",
        "marks": 13,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Problem Solving",
        "explanation": "Calculate Euclidean distance from query point to all dataset samples, sort ascending, pick top 3, take majority vote.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain the working principle of Bagging and Random Forest ensemble algorithms with bootstrap sampling.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit III",
        "topic": "Ensemble Methods",
        "marks": 8,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Bootstrap aggregating, out-of-bag error estimation, random feature sub-selection at each split.",
        "is_in_bank": True
    },
    {
        "question_text": "Describe AdaBoost adaptive boosting algorithm and weight re-distribution formulation.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit III",
        "topic": "Boosting Techniques",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Sequential weak learners, sample weighting updates based on misclassification rates, final weighted combination.",
        "is_in_bank": True
    },

    # Unit IV
    {
        "question_text": "Explain the steps involved in the multilayer perceptron algorithm along with its advantages and disadvantages.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Multilayer Perceptron & Backprop",
        "marks": 13,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Feedforward propagation, error computation, backpropagation via gradient descent and chain rule weight updates.",
        "is_in_bank": True
    },
    {
        "question_text": "Describe Deep Neural Networks with ReLU activation function and hyperparameter tuning mechanisms.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Deep Learning Architectures",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Deep architectures, vanishing gradient mitigation with ReLU, dropout regularization, learning rate scheduling.",
        "is_in_bank": True
    },
    {
        "question_text": "Derive the backpropagation weight update equation using gradient descent and chain rule.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Backpropagation Mathematics",
        "marks": 8,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Error term delta for output layer and hidden layers, partial derivatives with respect to weights.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain convolutional layers and pooling operations in deep learning vision systems.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Convolutional Neural Networks",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Kernel convolutions, stride, padding, Max pooling, feature map spatial downsampling.",
        "is_in_bank": True
    },

    # Unit V
    {
        "question_text": "Demonstrate the concept of K-Fold cross validation with clear illustration and example.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit V",
        "topic": "Cross Validation Protocols",
        "marks": 8,
        "difficulty": "Medium",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Data splitting into K folds, rotating validation fold across K iterations, averaging metric scores.",
        "is_in_bank": True
    },
    {
        "question_text": "Analyze the K-fold CV paired t-test for comparing performance of two machine learning classifiers.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit V",
        "topic": "Statistical Hypothesis Testing",
        "marks": 5,
        "difficulty": "Hard",
        "bloom_level": "Analyze",
        "question_type": "Descriptive",
        "explanation": "Null hypothesis, difference vector, sample variance, t-statistic formulation, critical p-value threshold.",
        "is_in_bank": True
    },
    {
        "question_text": "Illustrate and assess the single classification algorithm and two classification algorithms using ROC curves and AUC metric.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit V",
        "topic": "ROC Analysis & Performance Metrics",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Confusion matrix metrics (Precision, Recall, F1), ROC curve plotting TPR vs FPR, AUC interpretation.",
        "is_in_bank": True
    },

    # --- ML PART C (15 Marks Comprehensive / Case Study) ---
    {
        "question_text": "Apply Decision tree algorithm to find the root node in the Buys-Laptop dataset (Age, Student, Credit rating). Compute the maximum information gain and entropy of the attributes to identify the optimal splitting feature.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit II",
        "topic": "Decision Tree Information Gain",
        "marks": 15,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Problem Solving",
        "explanation": "Calculate Info(D), Info_Age(D), Info_Student(D), Info_Credit(D). Find Gain for each attribute and pick maximum Gain.",
        "is_in_bank": True
    },
    {
        "question_text": "Consider a neural network with inputs x1=0.05, x2=0.10, bias b1=0.35, b2=0.60, initial weights w1=0.15, w2=0.20, w3=0.25, w4=0.30, w5=0.40, w6=0.45, w7=0.50, w8=0.55, and target values T1=0.01, T2=0.99. Perform Forward pass and calculate the error at the output layer. Update weights on each layer after the error computation using learning rate eta=0.5.",
        "subject": "Machine Learning",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 4",
        "unit": "Unit IV",
        "topic": "Neural Network Numerical Backpropagation",
        "marks": 15,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Problem Solving",
        "explanation": "Calculate net_h1, out_h1, net_h2, out_h2, net_y1, out_y1, net_y2, out_y2. Compute Total Error = 0.5*(T1-out_y1)^2 + 0.5*(T2-out_y2)^2. Update weights w5-w8 and w1-w4.",
        "is_in_bank": True
    }
]

# Complementary DBMS 13-mark, 15-mark, and 5-mark questions
DBMS_EXTRA_QUESTIONS = [
    # 5 Marks
    {
        "question_text": "Explain the differences between Specialization and Generalization in Enhanced Entity-Relationship (EER) modeling.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I",
        "topic": "ER Modeling & Relational Mapping",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Top-down specialization vs bottom-up generalization, attribute inheritance, and constraint specifications.",
        "is_in_bank": True
    },
    {
        "question_text": "State Armstrong's Axioms for functional dependencies and explain Reflexivity, Augmentation, and Transitivity rules.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit II",
        "topic": "Normalization & Functional Dependencies",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Armstrong's axioms provide sound and complete inference rules for deriving closures of functional dependencies.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain SQL Views and discuss the conditions under which a view is updatable.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit III",
        "topic": "SQL Commands & Queries",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Virtual tables defined by queries; updatable only when defined on a single base table without aggregate functions.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain the concept of Shadow Paging technique for crash recovery in database management systems.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit IV",
        "topic": "ACID Properties & Transactions",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Current page table vs shadow page table, atomicity via page table pointer swap.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain Dense Indexing vs Sparse Indexing with suitable diagrams and comparative criteria.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit V",
        "topic": "Indexing & B+ Trees",
        "marks": 5,
        "difficulty": "Medium",
        "bloom_level": "Understand",
        "question_type": "Descriptive",
        "explanation": "Dense index contains an index record for every search key value; sparse index has records only for some search keys.",
        "is_in_bank": True
    },

    # 13 Marks (for Semester Part B)
    {
        "question_text": "Explain the detailed relational database design process from requirements collection, conceptual schema design using ER diagram, to relational model logical mapping with comprehensive constraints.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I",
        "topic": "ER Modeling & Relational Mapping",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Descriptive",
        "explanation": "Detailed lifecycle phases, ER constructs, mapping rules for 1:1, 1:N, M:N relations, weak entities, and integrity rules.",
        "is_in_bank": True
    },
    {
        "question_text": "Given a relational schema R(A, B, C, D, E, F) and set of functional dependencies F = {A -> BC, CD -> E, B -> D, E -> A}. Find all candidate keys of R, determine the highest normal form of R, and decompose into BCNF preserving dependencies where possible.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit II",
        "topic": "Normalization & Functional Dependencies",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Analyze",
        "question_type": "Problem Solving",
        "explanation": "Compute closures of attribute subsets, identify superkeys and minimal candidate keys, verify 2NF, 3NF, BCNF violations.",
        "is_in_bank": True
    },
    {
        "question_text": "Write complex SQL queries involving multi-table INNER and OUTER JOINs, nested correlated subqueries with EXISTS, GROUP BY with HAVING filters, and Window functions (ROW_NUMBER, RANK, DENSE_RANK).",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit III",
        "topic": "Joins, Subqueries & Aggregations",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Apply",
        "question_type": "Problem Solving",
        "explanation": "Construct syntax-compliant SQL queries demonstrating deep join evaluation, aggregation conditions, and analytical partitions.",
        "is_in_bank": True
    },
    {
        "question_text": "Discuss the Two-Phase Locking (2PL) protocols (Basic 2PL, Conservative 2PL, Strict 2PL, and Rigorous 2PL). Prove how Strict 2PL guarantees serializability and avoids cascading aborts.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit IV",
        "topic": "Concurrency Control & Deadlock Protocols",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Analyze",
        "question_type": "Descriptive",
        "explanation": "Growing and shrinking phases, exclusive lock retention until commit in Strict 2PL, precedence graph equivalence.",
        "is_in_bank": True
    },
    {
        "question_text": "Explain query optimization in relational DBMS. Discuss relational algebra equivalence rules, cost estimation based on catalog statistics, and dynamic programming join ordering algorithms.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit V",
        "topic": "Query Processing & Optimization",
        "marks": 13,
        "difficulty": "Hard",
        "bloom_level": "Analyze",
        "question_type": "Descriptive",
        "explanation": "Canonical query trees, pushdown predicates, selectivity factor calculations, and search space exploration.",
        "is_in_bank": True
    },

    # 15 Marks (for Semester Part C)
    {
        "question_text": "Design an enterprise database schema for a Healthcare Hospital Management System. Formulate the comprehensive ER diagram with at least 6 entities, weak entities, and multivalued attributes. Map the ER diagram to a relational schema in 3NF, identify primary keys and foreign keys, and construct complex SQL queries to generate patient billing statements and physician schedule reports.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit I",
        "topic": "Enterprise Database Case Study",
        "marks": 15,
        "difficulty": "Hard",
        "bloom_level": "Create",
        "question_type": "Problem Solving",
        "explanation": "Complete ER modeling, relationship cardinalities, structural mapping to relations in 3NF, DDL specifications, and analytical query formulations.",
        "is_in_bank": True
    },
    {
        "question_text": "A high-frequency financial trading system processes concurrent balance transfers and portfolio settlements. Analyze potential concurrency anomalies (Dirty Read, Non-repeatable Read, Phantom Read, Write Skew). Architect a complete ACID-compliant concurrency and Write-Ahead Logging (WAL) recovery mechanism utilizing ARIES algorithm with Analysis, Redo, and Undo passes to ensure zero data loss during sudden system crashes.",
        "subject": "Database Management Systems",
        "department": "Artificial Intelligence & Data Science",
        "academic_year": "2025-2026",
        "semester": "Semester 6",
        "unit": "Unit IV",
        "topic": "Mission-Critical Transaction Engineering",
        "marks": 15,
        "difficulty": "Hard",
        "bloom_level": "Create",
        "question_type": "Problem Solving",
        "explanation": "Detailed ARIES recovery protocol analysis: LSN tracking, Dirty Page Table, Transaction Table, Redo repeat history, Undo active transactions with CLRs.",
        "is_in_bank": True
    }
]

def seed():
    conn = get_db_connection()
    inserted_ml = 0
    inserted_dbms = 0
    
    with conn.cursor() as cur:
        # Check existing questions to prevent duplicates
        cur.execute("SELECT question_text FROM questions")
        existing_texts = {r['question_text'].strip() for r in cur.fetchall()}

        sql = """
            INSERT INTO questions (
                subject, department, academic_year, semester, unit, topic,
                marks, difficulty, bloom_level, question_type, explanation,
                is_in_bank, question_text, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for q in ML_QUESTIONS:
            if q['question_text'].strip() not in existing_texts:
                cur.execute(sql, (
                    q['subject'], q['department'], q['academic_year'], q['semester'],
                    q['unit'], q['topic'], q['marks'], q['difficulty'], q['bloom_level'],
                    q['question_type'], q['explanation'], 1, q['question_text'], 1
                ))
                inserted_ml += 1
                existing_texts.add(q['question_text'].strip())

        for q in DBMS_EXTRA_QUESTIONS:
            if q['question_text'].strip() not in existing_texts:
                cur.execute(sql, (
                    q['subject'], q['department'], q['academic_year'], q['semester'],
                    q['unit'], q['topic'], q['marks'], q['difficulty'], q['bloom_level'],
                    q['question_type'], q['explanation'], 1, q['question_text'], 1
                ))
                inserted_dbms += 1
                existing_texts.add(q['question_text'].strip())

        conn.commit()

    conn.close()
    print(f"Successfully seeded: {inserted_ml} ML questions, {inserted_dbms} DBMS questions.")

if __name__ == '__main__':
    seed()
