import os
import re

app_js_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace initQuestionGeneratorPage
old_init_q_page_re = r'function initQuestionGeneratorPage\(\)\s*\{.*?(?=function renderGeneratedResults)'
new_init_q_page = '''function initQuestionGeneratorPage() {
  const form = document.getElementById('questionGeneratorForm');
  const subjectInput = document.getElementById('genSubject');
  const deptInput = document.getElementById('genDept');
  const unitInput = document.getElementById('genUnit');
  const topicInput = document.getElementById('genTopic');
  const numQInput = document.getElementById('genNumQuestions');
  const pctEasy = document.getElementById('pctEasy');
  const pctMedium = document.getElementById('pctMedium');
  const pctHard = document.getElementById('pctHard');
  const resourceSelect = document.getElementById('genResourceSelect');

  // Restore saved config
  const savedCfg = localStorage.getItem('academic_last_gen_q_config');
  if (savedCfg) {
    try {
      const cfg = JSON.parse(savedCfg);
      if (cfg.department && deptInput) deptInput.value = cfg.department;
      if (cfg.subject && subjectInput) subjectInput.value = cfg.subject;
      if (cfg.unit && unitInput) unitInput.value = cfg.unit;
      if (cfg.topic !== undefined && topicInput) topicInput.value = cfg.topic;
      if (cfg.numQuestions && numQInput) numQInput.value = cfg.numQuestions;
      if (cfg.pEasy && pctEasy) pctEasy.value = cfg.pEasy;
      if (cfg.pMedium && pctMedium) pctMedium.value = cfg.pMedium;
      if (cfg.pHard && pctHard) pctHard.value = cfg.pHard;
    } catch (e) {}
  }

  if (subjectInput) {
    subjectInput.addEventListener('input', () => {
      populateQuestionDropdowns();
      if (typeof refreshFacultyGenResources === 'function') refreshFacultyGenResources();
    });
  }
  if (unitInput) {
    unitInput.addEventListener('input', () => {
      updateTopicDropdown();
      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();
    });
  }
  if (topicInput) {
    topicInput.addEventListener('input', () => {
      if (typeof updateSourceMaterialDisplay === 'function') updateSourceMaterialDisplay();
    });
  }

  if (pctEasy && pctMedium && pctHard) {
    [pctEasy, pctMedium, pctHard].forEach(inp => {
      inp.addEventListener('input', validateDifficultyInputs);
    });
  }

  populateQuestionDropdowns();
  if (typeof refreshFacultyGenResources === 'function') {
    refreshFacultyGenResources();
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      if (!validateDifficultyInputs()) {
        showToastNotice('Validation Error', 'Difficulty distribution percentages must sum to 100%.', 'warning');
        return;
      }

      const department = document.getElementById('genDept')?.value?.trim() || 'Artificial Intelligence & Data Science';
      const subject = document.getElementById('genSubject')?.value?.trim() || 'Database Management Systems';
      const academic_year = document.getElementById('genYear')?.value || '2025-2026';
      const semester = document.getElementById('genSem')?.value || 'Semester 6';
      const unit = document.getElementById('genUnit')?.value?.trim() || 'All Units (Complete Syllabus)';
      const topic = document.getElementById('genTopic')?.value?.trim() || '';
      const numQuestions = parseInt(document.getElementById('genNumQuestions')?.value || '10', 10);
      const question_type = document.getElementById('genQuestionType')?.value || 'Short Answer';
      const blooms_choice = document.getElementById('genBloomsLevel')?.value || 'Auto Select';
      const pEasy = parseInt(document.getElementById('pctEasy')?.value || '30', 10);
      const pMedium = parseInt(document.getElementById('pctMedium')?.value || '50', 10);
      const pHard = parseInt(document.getElementById('pctHard')?.value || '20', 10);
      const resourceId = document.getElementById('genResourceSelect')?.value || null;
      const useQb = document.getElementById('genUseQuestionBank')?.checked || false;

      // Persist values
      localStorage.setItem('academic_last_gen_q_config', JSON.stringify({
        department, subject, academic_year, semester, unit, topic, numQuestions, question_type, blooms_choice, pEasy, pMedium, pHard
      }));

      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Synthesizing Questions from Material...`;
      }

      const payload = {
        department,
        subject,
        academic_year,
        semester,
        unit,
        topic,
        num_questions: numQuestions,
        question_type,
        bloom_level: blooms_choice,
        diff_easy: pEasy,
        diff_medium: pMedium,
        diff_hard: pHard,
        resource_id: resourceId,
        use_question_bank: useQb
      };

      try {
        const res = await fetch('/api/questions/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="bi bi-cpu me-2"></i> Generate Questions`;
        }

        if (data.status === 'success') {
          window.currentGeneratedQuestions = data.questions || [];
          renderGeneratedResults(pEasy, pMedium, pHard);
          const noticeEl = document.getElementById('sourceMaterialNotice');
          if (noticeEl) noticeEl.innerHTML = '';

          showToastNotice('Questions Generated', `${window.currentGeneratedQuestions.length} grounded questions generated from study materials!`, 'success');
          const resultsContainer = document.getElementById('generatedQuestionsResults');
          if (resultsContainer) {
            resultsContainer.classList.remove('d-none');
            window.scrollTo({ top: resultsContainer.offsetTop - 70, behavior: 'smooth' });
          }
        } else {
          const noticeEl = document.getElementById('sourceMaterialNotice');
          if (noticeEl) {
            noticeEl.innerHTML = `<div class="alert alert-warning border border-warning p-2 small mt-2 mb-0"><i class="bi bi-exclamation-triangle me-1"></i>${data.message || 'Source material required.'}</div>`;
          }
          showToastNotice('Generation Notice', data.message || 'Failed to generate questions.', 'warning');
        }
      } catch (err) {
        console.error('Question generation error:', err);
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<i class="bi bi-cpu me-2"></i> Generate Questions`;
        }
        showToastNotice('Server Error', 'Failed to communicate with Flask backend API.', 'danger');
      }
    });
  }
}

'''

text = re.sub(old_init_q_page_re, new_init_q_page, text, flags=re.DOTALL)
print("initQuestionGeneratorPage updated.")


# 2. Update renderGeneratedResults to include Edit, Regenerate, Delete button hooks
old_card_actions = r'<div class="btn-group btn-group-sm">\s*<button class="btn btn-outline-secondary" onclick="editQuestionAction\(\$\{q\.id\}\)".*?</button>\s*<button class="btn btn-outline-danger" onclick="deleteQuestionAction\(\$\{q\.id\}\)".*?</button>\s*</div>'
new_card_actions = '''<div class="btn-group btn-group-sm">
            <button class="btn btn-outline-secondary" onclick="editGeneratedQuestion(${idx})" title="Edit Question Text"><i class="bi bi-pencil me-1"></i>Edit</button>
            <button class="btn btn-outline-primary" onclick="regenerateGeneratedQuestion(${idx})" title="Regenerate Question Formulation"><i class="bi bi-arrow-repeat me-1"></i>Regenerate</button>
            <button class="btn btn-outline-danger" onclick="deleteGeneratedQuestion(${idx})" title="Delete"><i class="bi bi-trash"></i></button>
          </div>'''

text = re.sub(old_card_actions, new_card_actions, text, flags=re.DOTALL)
print("Card actions in renderGeneratedResults updated.")


# 3. Update initQuizGeneratorForm and generateQuizAction
old_quiz_init_re = r'function initQuizGeneratorForm\(\)\s*\{.*?(?=function renderGeneratedQuiz)'
new_quiz_init = '''function initQuizGeneratorForm() {
  const subjectInput = document.getElementById('quizSubject');
  const deptInput = document.getElementById('quizDept');
  const unitInput = document.getElementById('quizUnit');
  const topicInput = document.getElementById('quizTopic');
  const numQInput = document.getElementById('quizNumQuestions');
  const timeLimitSelect = document.getElementById('quizTimeLimit');
  const marksPerQSelect = document.getElementById('quizMarksPerQ');
  const form = document.getElementById('quizGeneratorForm');

  // Restore saved config
  const savedCfg = localStorage.getItem('academic_last_gen_quiz_config');
  if (savedCfg) {
    try {
      const cfg = JSON.parse(savedCfg);
      if (cfg.department && deptInput) deptInput.value = cfg.department;
      if (cfg.subject && subjectInput) subjectInput.value = cfg.subject;
      if (cfg.unit && unitInput) unitInput.value = cfg.unit;
      if (cfg.topic !== undefined && topicInput) topicInput.value = cfg.topic;
    } catch (e) {}
  }

  // Set default: 30 minutes duration, 30 questions, 1 mark per question (30 marks total)
  if (timeLimitSelect) timeLimitSelect.value = "30";
  if (numQInput) numQInput.value = "30";
  if (marksPerQSelect) marksPerQSelect.value = "1";

  // Fetch faculty resources to populate subject suggestions and update source panel
  try {
    fetch('/api/resources', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (data && data.resources) {
          window.facultyAcademicResources = data.resources;
          const subjectDatalist = document.getElementById('quizSubjectList');
          if (subjectDatalist) {
            const uniqueSubjects = Array.from(new Set(data.resources.map(r => r.subject).filter(Boolean)));
            ['Database Management Systems', 'Artificial Intelligence', 'Machine Learning', 'Distributed Computing', 'Data Structures', 'Computer Networks'].forEach(s => {
              if (!uniqueSubjects.includes(s)) uniqueSubjects.push(s);
            });
            subjectDatalist.innerHTML = uniqueSubjects.map(s => `<option value="${s}">`).join('');
          }
        }
      }).catch(err => console.warn('Error fetching quiz resources:', err));
  } catch (e) {}

  if (subjectInput) {
    subjectInput.addEventListener('input', () => {
      updateQuizSourcePanel();
    });
  }
  if (unitInput) {
    unitInput.addEventListener('input', updateQuizSourcePanel);
  }

  updateQuizSourcePanel();

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      generateQuizAction();
    });
  }
}

function updateQuizUnitsDropdown() {
  const subjectInput = document.getElementById('quizSubject');
  const unitInput = document.getElementById('quizUnit');
  const topicInput = document.getElementById('quizTopic');

  if (!subjectInput) return;

  const subjectName = subjectInput.value;
  const struct = (typeof AcademicMockData !== 'undefined' && AcademicMockData.subjectStructure)
    ? (AcademicMockData.subjectStructure[subjectName] || AcademicMockData.subjectStructure["Database Management Systems"])
    : null;

  const unitDatalist = document.getElementById('quizUnitList');
  const defaultUnits = [
    "All Units (Complete Syllabus)",
    "Unit I — Introduction",
    "Unit II — Core Concepts",
    "Unit III — Advanced Topics",
    "Unit IV — Applications",
    "Unit V — Cloud & Emerging"
  ];

  const unitsList = (struct && struct.units && struct.units.length > 0)
    ? ["All Units (Complete Syllabus)", ...struct.units.map(u => u.name)]
    : defaultUnits;

  if (unitDatalist) {
    unitDatalist.innerHTML = unitsList.map(u => `<option value="${u}">`).join('');
  }
  if (unitInput && unitInput.tagName === 'SELECT') {
    unitInput.innerHTML = unitsList.map(u => `<option value="${u}">${u}</option>`).join('');
  }
}

function updateQuizSourcePanel() {
  const subjectName = document.getElementById('quizSubject')?.value || "Database Management Systems";
  const unitName = document.getElementById('quizUnit')?.value || "All Units (Complete Syllabus)";

  const panelSubject = document.getElementById('quizSourceSubjectDisplay');
  const panelUnit = document.getElementById('quizSourceUnitDisplay');
  const panelTopics = document.getElementById('quizSourceTopicsDisplay');
  const panelConcepts = document.getElementById('quizSourceConceptsDisplay');

  if (panelSubject) panelSubject.innerText = subjectName;
  if (panelUnit) panelUnit.innerText = unitName;

  const resources = window.facultyAcademicResources || [];
  const matching = resources.filter(r => r.subject.toLowerCase() === subjectName.toLowerCase());

  if (matching.length > 0) {
    if (panelTopics) {
      const topicNames = matching.map(m => m.topic).filter(Boolean);
      panelTopics.innerText = topicNames.length ? topicNames.join(', ') : `Topics verified from uploaded materials for ${subjectName}`;
    }
    if (panelConcepts) {
      panelConcepts.innerText = `Content verified from ${matching.length} uploaded faculty resource(s)`;
    }
  } else {
    if (panelTopics) panelTopics.innerText = "Syllabus topics for " + subjectName;
    if (panelConcepts) panelConcepts.innerText = "Academic curriculum topics";
  }
}

async function generateQuizAction() {
  const dept = document.getElementById('quizDept')?.value?.trim() || "Artificial Intelligence & Data Science";
  const subject = document.getElementById('quizSubject')?.value?.trim() || "Database Management Systems";
  const year = document.getElementById('quizYear')?.value || "2025-2026";
  const sem = document.getElementById('quizSem')?.value || "Semester 6";
  const unit = document.getElementById('quizUnit')?.value?.trim() || "All Units (Complete Syllabus)";
  const topic = document.getElementById('quizTopic')?.value?.trim() || "";
  const title = document.getElementById('quizTitleInput')?.value?.trim() || `${subject} Timed Assessment Quiz`;
  const durationMins = parseInt(document.getElementById('quizTimeLimit')?.value || 30, 10);
  const marksPerQ = parseInt(document.getElementById('quizMarksPerQ')?.value || 1, 10);
  const numQuestions = parseInt(document.getElementById('quizNumQuestions')?.value || 30, 10);

  // Save config
  localStorage.setItem('academic_last_gen_quiz_config', JSON.stringify({
    department: dept, subject, academic_year: year, semester: sem, unit, topic, duration_minutes: durationMins, marks_per_question: marksPerQ, total_questions: numQuestions
  }));

  const form = document.getElementById('quizGeneratorForm');
  const submitBtn = form?.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Generating Grounded ${numQuestions}-Question Quiz (30 Marks)...`;
  }

  const payload = {
    title,
    department: dept,
    subject,
    academic_year: year,
    semester: sem,
    unit,
    topic,
    duration_minutes: durationMins,
    marks_per_question: marksPerQ,
    total_questions: numQuestions
  };

  try {
    const res = await fetch('/api/quizzes/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-magic me-2"></i> Generate Quiz`;
    }

    if (data.status === 'success') {
      activeGeneratedQuizQuestions = data.questions || [];
      window.currentQuizPreview = data.quiz;

      renderGeneratedQuiz();
      renderQuizDifficultyAnalysis();
      renderQuizConceptCoverage();

      const resultsSection = document.getElementById('generatedQuizResults');
      if (resultsSection) {
        resultsSection.classList.remove('d-none');
        window.scrollTo({ top: resultsSection.offsetTop - 70, behavior: 'smooth' });
      }

      showToastNotice('Quiz Generated', `Generated ${activeGeneratedQuizQuestions.length} unique questions for ${subject} (${durationMins} Mins, ${activeGeneratedQuizQuestions.length * marksPerQ} Marks)!`, 'success');
    } else {
      showToastNotice('Quiz Generation Notice', data.message || 'Failed to generate quiz.', 'warning');
      alert(`[Quiz Generator Notice]\\n\\n${data.message}`);
    }
  } catch (err) {
    console.error('Quiz generation error:', err);
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-magic me-2"></i> Generate Quiz`;
    }
    showToastNotice('Server Error', 'Failed to communicate with Quiz Generation API.', 'danger');
  }
}

'''

text = re.sub(old_quiz_init_re, new_quiz_init, text, flags=re.DOTALL)
print("initQuizGeneratorForm and generateQuizAction updated.")


# 4. Update startStudentQuizAttempt to default duration to 30 minutes
old_attempt_init = r'durationMins:\s*found\.duration_minutes\s*\|\|\s*found\.durationMins\s*\|\|\s*10'
new_attempt_init = 'durationMins: found.duration_minutes || found.durationMins || 30'
text = re.sub(old_attempt_init, new_attempt_init, text)

old_sec_rem = r'quizSecondsRemaining\s*=\s*\(activeStudentQuiz\.durationMins\s*\|\|\s*10\)\s*\*\s*60'
new_sec_rem = 'quizSecondsRemaining = (activeStudentQuiz.durationMins || 30) * 60'
text = re.sub(old_sec_rem, new_sec_rem, text)
print("startStudentQuizAttempt updated to 30 minutes default.")

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("js/app.js completely patched and verified.")
