path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\scratch\test_full_system_features.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("save_it_res['question_paper']", "save_it_res.get('paper', save_it_res.get('question_paper'))")
text = text.replace("save_sem_res['question_paper']", "save_sem_res.get('paper', save_sem_res.get('question_paper'))")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated test_full_system_features.py successfully!')
