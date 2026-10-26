# -*- coding: utf-8 -*-
"""
Seed 1 additional 8-mark question per unit for Machine Learning
so every unit has at least 4 questions of 8 marks.
"""
import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from models.database import get_db_connection

EXTRA_8M = [
    {
        "unit": "Unit I",
        "topic": "Feature Engineering & Scaling",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain feature scaling techniques in machine learning: Min-Max Normalization and Standardization (Z-score). Discuss why gradient descent converges faster with scaled features."
    },
    {
        "unit": "Unit II",
        "topic": "Multiclass Classification Strategies",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Understand",
        "question_text": "Describe One-vs-Rest (OvR) and One-vs-One (OvO) strategies for extending binary classifiers like SVM to multiclass classification problems. Compare their training computational complexities."
    },
    {
        "unit": "Unit III",
        "topic": "Gradient Boosting & XGBoost",
        "marks": 8,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Explain the working principle of Gradient Boosted Decision Trees (GBDT). Formulate how residual errors are fitted sequentially using gradient descent in functional space."
    },
    {
        "unit": "Unit IV",
        "topic": "Hierarchical Clustering",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain Agglomerative Hierarchical Clustering algorithm with single linkage, complete linkage, and average linkage distance metrics. Illustrate how a dendrogram is constructed and cut."
    },
    {
        "unit": "Unit V",
        "topic": "Transfer Learning in Deep Neural Networks",
        "marks": 8,
        "difficulty": "hard",
        "bloom_level": "Evaluate",
        "question_text": "Discuss the concept of Transfer Learning and Fine-tuning in deep Convolutional Neural Networks. Under what conditions should weights be frozen versus fine-tuned?"
    }
]

def seed_extra_8m():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT question_text FROM questions WHERE subject = 'Machine Learning'")
        existing_texts = {r['question_text'].strip() for r in cur.fetchall()}

        sql = """
            INSERT INTO questions (
                subject, department, academic_year, semester, unit, topic,
                marks, difficulty, bloom_level, question_type, explanation,
                is_in_bank, question_text, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        inserted = 0
        for q in EXTRA_8M:
            if q['question_text'].strip() not in existing_texts:
                cur.execute(sql, (
                    'Machine Learning', 'Artificial Intelligence & Data Science', '2025-2026', 'Semester 6',
                    q['unit'], q['topic'], q['marks'], q['difficulty'], q['bloom_level'],
                    'descriptive', 'Machine learning curriculum question', 1, q['question_text'], 1
                ))
                inserted += 1
                existing_texts.add(q['question_text'].strip())

        conn.commit()
    conn.close()
    print(f"Successfully added {inserted} extra 8M questions for Machine Learning.")

if __name__ == '__main__':
    seed_extra_8m()
