import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add getOptionDisplayString before initQuizGeneratorPage if not already present
if 'function getOptionDisplayString' not in text:
    target = 'function initQuizGeneratorPage() {'
    replacement = """function getOptionDisplayString(opt) {
  if (opt === null || opt === undefined) return '';
  if (typeof opt === 'string') {
    return opt === '[object Object]' ? '' : opt;
  }
  if (typeof opt === 'object') {
    return opt.option_text || opt.text || opt.title || opt.value || opt.label || '';
  }
  return String(opt);
}

function initQuizGeneratorPage() {"""
    text = text.replace(target, replacement, 1)
    print("Added getOptionDisplayString.")
else:
    print("getOptionDisplayString already present.")

# 2. Update generateQuizAction to include blooms and difficulty in payload
pattern_payload = r'(const payload = \{[\s\S]*?total_questions: numQuestions\s*)\};'
m = re.search(pattern_payload, text)
if m:
    rep = m.group(1) + """,
    difficulty: document.getElementById('quizDiffSelect')?.value || 'Mixed',
    bloom_level: document.getElementById('quizBloomsSelect')?.value || 'Auto Select',
    blooms_level: document.getElementById('quizBloomsSelect')?.value || 'Auto Select'
  };"""
    text = text[:m.start()] + rep + text[m.end():]
    print("Updated generateQuizAction payload.")
else:
    print("Warning: generateQuizAction payload pattern not found.")

# 3. Update renderGeneratedQuiz option display
# Look for <span class="fw-bold me-2">${String.fromCharCode(65 + oIdx)}.</span> ${opt}
pattern_opt1 = r'(\$\{String\.fromCharCode\(65 \+ oIdx\)\}\.</span>\s*)\$\{opt\}'
text = re.sub(pattern_opt1, r'\1${getOptionDisplayString(opt)}', text)
print("Updated renderGeneratedQuiz and student card option display.")

# Update correctAnswer badge
pattern_badge = r'(<span class="badge bg-success-subtle text-success border border-success fw-bold"><i class="bi bi-check-circle me-1"></i> Correct Answer:\s*)\$\{q\.correctAnswer\}'
text = re.sub(pattern_badge, r'\1${q.correctAnswer || (q.options && q.options[q.correctIndex] ? getOptionDisplayString(q.options[q.correctIndex]) : "")}', text)
print("Updated correctAnswer badge.")

# 4. Update previewStudentQuizView
pattern_preview = r'(\$\{String\.fromCharCode\(65 \+ i\)\}\.\s*)\$\{opt\}'
text = re.sub(pattern_preview, r'\1${getOptionDisplayString(opt)}', text)
print("Updated previewStudentQuizView option display.")

# 5. Update regenerateQuizQuestion to dynamically re-fetch grounded question
old_regen = """function regenerateQuizQuestion(idx) {
  const q = activeGeneratedQuizQuestions[idx];
  if (!q) return;
  const curMarks = (q.marks !== undefined && q.marks !== null) ? q.marks : parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);
  q.text = "Which SQL clause is used to group tuples having identical values in specified columns?";
  q.question_text = q.text;
  q.question = q.text;
  q.options = ["ORDER BY", "GROUP BY", "WHERE", "HAVING"];
  q.correctAnswer = "B. GROUP BY";
  q.correct_answer = "B";
  q.correctIndex = 1;
  q.marks = curMarks;
  q.marks_per_question = curMarks;
  q.type = `Quiz Question (${curMarks} ${curMarks === 1 ? 'Mark' : 'Marks'})`;
  q.question_type = q.type;
  renderGeneratedQuiz();
  renderQuizConceptCoverage();
}"""

new_regen = """function regenerateQuizQuestion(idx) {
  const q = activeGeneratedQuizQuestions[idx];
  if (!q) return;
  const curMarks = (q.marks !== undefined && q.marks !== null) ? q.marks : parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);
  const subject = document.getElementById('quizSubject')?.value || q.subject || "Distributed Computing";
  const topic = document.getElementById('quizTopic')?.value || q.topic || "";
  const unit = document.getElementById('quizUnit')?.value || q.unit || "All Units";

  const quizGenUrl = (typeof API_QUIZZES_BASE !== 'undefined' && API_QUIZZES_BASE)
    ? `${API_QUIZZES_BASE}/generate`
    : 'http://localhost:5000/api/quizzes/generate';

  fetch(quizGenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      subject,
      topic,
      unit,
      marks_per_question: curMarks,
      total_questions: 1
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success' && data.questions && data.questions.length > 0) {
      activeGeneratedQuizQuestions[idx] = data.questions[0];
      renderGeneratedQuiz();
      renderQuizDifficultyAnalysis();
      renderQuizConceptCoverage();
      showToastNotice('Question Regenerated', `Question ${idx + 1} regenerated successfully.`, 'success');
    }
  })
  .catch(err => {
    console.warn('Error regenerating quiz question:', err);
  });
}"""

if old_regen in text:
    text = text.replace(old_regen, new_regen, 1)
    print("Updated regenerateQuizQuestion.")
else:
    print("Warning: old_regen pattern not found verbatim.")

# 6. Update saveQuizToStorage to normalize options
pattern_save = r'(questions:\s*activeGeneratedQuizQuestions\.map\(q => \(\{ \.\.\.q, marks:[\s\S]*?\}\)\))'
m_save = re.search(pattern_save, text)
if m_save:
    new_save_q = """questions: activeGeneratedQuizQuestions.map(q => {
      const normOpts = (q.options || []).map((opt, oIdx) => {
        const textStr = getOptionDisplayString(opt);
        const letter = String.fromCharCode(65 + oIdx);
        const isCorrect = (oIdx === q.correctIndex) || (typeof opt === 'object' && opt.is_correct === true);
        return {
          label: letter,
          option_label: letter,
          text: textStr,
          option_text: textStr,
          is_correct: isCorrect
        };
      });
      return {
        ...q,
        marks: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ,
        marks_per_question: (q.marks !== undefined && q.marks !== null) ? q.marks : marksPerQ,
        options: normOpts,
        options_strings: normOpts.map(o => o.text)
      };
    })"""
    text = text[:m_save.start()] + new_save_q + text[m_save.end():]
    print("Updated saveQuizToStorage questions normalization.")
else:
    print("Warning: pattern_save not found.")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved js/app.js successfully!")
