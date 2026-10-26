# -*- coding: utf-8 -*-
"""
Seed 16-mark and 8-mark questions for Machine Learning
to ensure internal examinations (50 marks, inter.pdf format)
can be generated for Machine Learning across any unit combination.
"""
import sys
sys.path.insert(0, r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend")

from models.database import get_db_connection

ML_16M_QUESTIONS = [
    # Unit I
    {
        "unit": "Unit I",
        "topic": "Inductive Bias & Learning Models",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Describe the complete machine learning lifecycle from data ingestion, preprocessing, feature extraction, model selection to validation. Explain the concept of inductive bias and hypothesis space search with concrete examples."
    },
    {
        "unit": "Unit I",
        "topic": "Linear Regression and Optimization",
        "marks": 16,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain multivariate linear regression in detail. Derive the closed-form normal equations for least squares parameter estimation and compare its computational complexity against gradient descent optimization."
    },
    {
        "unit": "Unit I",
        "topic": "PAC Learning",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Understand",
        "question_text": "Explain the Probably Approximately Correct (PAC) learning framework. Define epsilon-exhausted version space and sample complexity bounds."
    },
    {
        "unit": "Unit I",
        "topic": "Supervised vs Unsupervised",
        "marks": 8,
        "difficulty": "easy",
        "bloom_level": "Understand",
        "question_text": "Differentiate between supervised, unsupervised, and reinforcement learning paradigms with practical application scenarios and mathematical objective functions."
    },

    # Unit II
    {
        "unit": "Unit II",
        "topic": "Support Vector Machines",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Evaluate",
        "question_text": "Formulate the maximum margin optimization problem for Support Vector Machines (SVM). Derive the Lagrangian dual formulation and explain how Mercer kernel functions construct non-linear decision boundaries."
    },
    {
        "unit": "Unit II",
        "topic": "Neural Networks & Backpropagation",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Explain the architecture, forward propagation, and mathematical derivation of the Backpropagation algorithm for a Multilayer Perceptron. Discuss the vanishing gradient problem and how modern activation functions address it."
    },
    {
        "unit": "Unit II",
        "topic": "VC Dimension",
        "marks": 8,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Define Vapnik-Chervonenkis (VC) dimension. Calculate the VC dimension of linear decision boundaries in 2D space and explain its relationship to model capacity and generalization bounds."
    },
    {
        "unit": "Unit II",
        "topic": "Logistic Regression",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain logistic regression for binary classification. Formulate the cross-entropy loss function and derive the gradient update rule using maximum likelihood estimation."
    },

    # Unit III
    {
        "unit": "Unit III",
        "topic": "Decision Trees",
        "marks": 16,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain the ID3 and CART decision tree algorithms. Derive the mathematical expressions for Entropy, Information Gain, and Gini Impurity, and demonstrate step-by-step how optimal split attributes are chosen."
    },
    {
        "unit": "Unit III",
        "topic": "Ensemble Methods & Boosting",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Evaluate",
        "question_text": "Discuss the theory of ensemble learning. Contrast Bagging (Random Forests) and Boosting (AdaBoost). Detail the AdaBoost weight update mechanism, proving why it focuses subsequent weak learners on previously misclassified samples."
    },
    {
        "unit": "Unit III",
        "topic": "Random Forests",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Understand",
        "question_text": "Explain Random Forest construction, bootstrap aggregation, and out-of-bag (OOB) error estimation. Discuss how feature sub-sampling reduces tree correlation."
    },
    {
        "unit": "Unit III",
        "topic": "Tree Pruning",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain pre-pruning and post-pruning techniques in decision trees. Describe Reduced Error Pruning and Cost-Complexity Pruning mechanisms."
    },

    # Unit IV
    {
        "unit": "Unit IV",
        "topic": "Expectation-Maximization",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Evaluate",
        "question_text": "Explain the Expectation-Maximization (EM) algorithm in full mathematical rigor. Derive the E-step and M-step parameter estimation updates for fitting a Gaussian Mixture Model (GMM) to unlabelled multi-dimensional data."
    },
    {
        "unit": "Unit IV",
        "topic": "Hidden Markov Models",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Provide an in-depth analysis of Hidden Markov Models (HMMs). Formulate the Forward-Backward algorithm for evaluation, the Viterbi algorithm for decoding, and the Baum-Welch algorithm for parameter estimation."
    },
    {
        "unit": "Unit IV",
        "topic": "Principal Component Analysis",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Derive Principal Component Analysis (PCA) as variance maximization. Explain the steps of computing the covariance matrix, eigendecomposition, and dimensionality projection."
    },
    {
        "unit": "Unit IV",
        "topic": "K-Means Clustering",
        "marks": 8,
        "difficulty": "easy",
        "bloom_level": "Apply",
        "question_text": "Explain the K-Means clustering algorithm, objective function, and convergence properties. Discuss sensitivity to centroid initialization and how K-Means++ improves performance."
    },

    # Unit V
    {
        "unit": "Unit V",
        "topic": "Deep Convolutional Networks",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Create",
        "question_text": "Explain the architecture of Deep Convolutional Neural Networks (CNNs). Detail convolutional layers, receptive fields, max-pooling, batch normalization, and skip connections in ResNet architectures."
    },
    {
        "unit": "Unit V",
        "topic": "Recurrent Neural Networks & LSTM",
        "marks": 16,
        "difficulty": "hard",
        "bloom_level": "Analyze",
        "question_text": "Analyze sequential deep learning models. Explain why standard RNNs suffer from vanishing and exploding gradients, and derive the mathematical equations governing Forget, Input, and Output gates in LSTM networks."
    },
    {
        "unit": "Unit V",
        "topic": "Regularization in Deep Learning",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Apply",
        "question_text": "Explain key regularization techniques used in deep learning: Dropout, L1 and L2 weight decay, and Data Augmentation. Contrast their mechanisms for preventing overfitting."
    },
    {
        "unit": "Unit V",
        "topic": "Autoencoders",
        "marks": 8,
        "difficulty": "medium",
        "bloom_level": "Understand",
        "question_text": "Explain the architecture of Autoencoders and Variational Autoencoders (VAEs). Describe the reconstruction loss, latent distribution parameters, and the reparameterization trick."
    }
]

def seed_ml_questions():
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
        for q in ML_16M_QUESTIONS:
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
    print(f"Seeded {inserted} questions for Machine Learning into Question Bank.")

if __name__ == '__main__':
    seed_ml_questions()
