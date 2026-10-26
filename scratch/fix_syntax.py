# -*- coding: utf-8 -*-
with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix the two multiline instruction strings
old_str_1 = '''        instructions = "1. Answer ALL Questions.
2. Part A: 5 Questions x 2 Marks = 10 Marks.
3. Part B: 1 Question x 8 Marks = 8 Marks.
4. Part C: 2 Questions x 16 Marks = 32 Marks.
5. Maximum Attempted Marks: 50 Marks."'''

new_str_1 = '''        instructions = "1. Answer ALL Questions.\\n2. Part A: 5 Questions x 2 Marks = 10 Marks.\\n3. Part B: 1 Question x 8 Marks = 8 Marks.\\n4. Part C: 2 Questions x 16 Marks = 32 Marks.\\n5. Maximum Attempted Marks: 50 Marks."'''

old_str_2 = '''        instructions = "1. Answer ALL Questions.
2. Part A: 10 Questions x 2 Marks = 20 Marks.
3. Part B: 5 Questions x 13 Marks = 65 Marks.
4. Part C: 1 Question x 15 Marks = 15 Marks.
5. Maximum Attempted Marks: 100 Marks."'''

new_str_2 = '''        instructions = "1. Answer ALL Questions.\\n2. Part A: 10 Questions x 2 Marks = 20 Marks.\\n3. Part B: 5 Questions x 13 Marks = 65 Marks.\\n4. Part C: 1 Question x 15 Marks = 15 Marks.\\n5. Maximum Attempted Marks: 100 Marks."'''

text = text.replace(old_str_1, new_str_1)
text = text.replace(old_str_2, new_str_2)

with open(r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\backend\services\question_paper_service.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed syntax in question_paper_service.py!")
