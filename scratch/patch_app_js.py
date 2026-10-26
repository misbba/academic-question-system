# patch_app_js.py
with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    code = f.read()

target1 = "const question_type = document.getElementById('genQuestionType')?.value || 'Short Answer';"
repl1 = """const marksVal = document.getElementById('genMarks')?.value || document.getElementById('genQuestionType')?.value || 'Mixed';
      let marks_per_question = 2;
      if (marksVal === '8') marks_per_question = 8;
      else if (marksVal === '16') marks_per_question = 16;
      else if (marksVal === 'Mixed') marks_per_question = 'Mixed';
      const question_type = marksVal === '2' ? 'Concise Definition (2 Marks)' : (marksVal === '8' ? 'Working Principle / Analysis (8 Marks)' : (marksVal === '16' ? 'Comprehensive Architecture (16 Marks)' : 'Mixed Marks (2, 8, 16M)'));"""

target2 = """        num_questions: numQuestions,

        question_type,"""

repl2 = """        num_questions: numQuestions,

        marks: marksVal,

        marks_per_question: marks_per_question,

        question_type,"""

assert target1 in code, 'target1 not found!'
code = code.replace(target1, repl1, 1)

code_norm = code.replace('\r\n', '\n')
target2_norm = target2.replace('\r\n', '\n')
repl2_norm = repl2.replace('\r\n', '\n')
assert target2_norm in code_norm, 'target2 not found!'
code_norm = code_norm.replace(target2_norm, repl2_norm, 1)

with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(code_norm)
print('Successfully patched initQuestionGeneratorPage in js/app.js!')
