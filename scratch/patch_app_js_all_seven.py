"""
Script to apply updates to js/app.js for:
1. saveGeneratedToBank() payload (sends { questions, question_ids }) and duplicate prevention
2. syncModuleDatalists helper function
3. Update populateVoiceTopics, populateImageTopics, populateTransTopics, populatePPTTopics, populateLPTopics, updateAssignmentUnitsDropdown
4. Update initVoiceQuestionForm, initImageQuestionForm, initLanguageConverterForm, initPPTGeneratorForm, initLessonPlanGeneratorForm, initAssignmentGeneratorForm
5. Update generateQuestionsFromVoice, generateQuestionsFromImage, convertAcademicLanguage, generatePPTContent, generateLessonPlanContent, generateAssignmentAction
"""

import os
import re

APP_JS = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js"

with open(APP_JS, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update saveGeneratedToBank
old_save_bank = re.compile(r'async function saveGeneratedToBank\(\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)')

new_save_bank = """async function saveGeneratedToBank() {
  const saveBtn = document.getElementById('saveGeneratedToBankBtn');
  const questions = window.currentGeneratedQuestions || [];

  if (!questions || questions.length === 0) {
    showToastNotice('Warning', 'No generated questions available to save.', 'warning');
    return;
  }

  // Prevent duplicate submissions
  if (saveBtn && (saveBtn.disabled || saveBtn.dataset.saving === 'true')) {
    return;
  }
  const originalBtnHtml = saveBtn ? saveBtn.innerHTML : '';
  if (saveBtn) {
    saveBtn.dataset.saving = 'true';
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Saving to Question Bank...';
  }

  const question_ids = questions.map(q => q.id);

  try {
    const res = await fetch(API_QUESTION_BANK_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        questions: questions,
        question_ids: question_ids
      })
    });

    const data = await safeParseJsonResponse(res);

    if (data.status === 'success') {
      if (data.questions && Array.isArray(data.questions) && data.questions.length > 0) {
        window.currentGeneratedQuestions = data.questions;
      } else {
        questions.forEach(q => q.is_in_bank = true);
      }
      renderGeneratedResults();
      showToastNotice('Question Bank Updated', data.message || `${data.saved_count || questions.length} questions successfully saved to Question Bank!`, 'success');
      if (saveBtn) {
        saveBtn.dataset.saving = 'false';
        saveBtn.innerHTML = '<i class="bi bi-check-circle-fill text-success me-1"></i> Saved to Question Bank';
        saveBtn.disabled = true;
      }
    } else {
      showToastNotice('Error', data.message || 'Failed to save to Question Bank.', 'danger');
      if (saveBtn) {
        saveBtn.dataset.saving = 'false';
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalBtnHtml;
      }
    }
  } catch (err) {
    console.error('Error saving to question bank:', err);
    showToastNotice('Network Error', 'Unable to reach backend to save questions.', 'danger');
    if (saveBtn) {
      saveBtn.dataset.saving = 'false';
      saveBtn.disabled = false;
      saveBtn.innerHTML = originalBtnHtml;
    }
  }
}
"""

m = old_save_bank.search(content)
if m:
    content = content[:m.start()] + new_save_bank + content[m.end():]
    print("SUCCESS: Updated saveGeneratedToBank")
else:
    print("WARN: saveGeneratedToBank not found")

# 2. Add syncModuleDatalists helper function before initVoiceQuestionForm or in helper section
helper_fn = """
// Dynamic Datalist Synchronizer for All 7 Academic Modules
function syncModuleDatalists(subjId, subjListId, unitId, unitListId, topicId, topicListId) {
  const subjEl = document.getElementById(subjId);
  const unitEl = document.getElementById(unitId);
  const topicEl = document.getElementById(topicId);
  const unitListEl = document.getElementById(unitListId);
  const topicListEl = document.getElementById(topicListId);

  const subjectVal = (subjEl?.value || '').trim();
  const unitVal = (unitEl?.value || '').trim();

  // Standard Units list options
  const defaultUnits = [
    "All Units (Complete Syllabus)",
    "Unit 1",
    "Unit 2",
    "Unit 3",
    "Unit 4",
    "Unit 5",
    "Unit I — Introduction",
    "Unit II — Core Concepts",
    "Unit III — Advanced Topics",
    "Unit IV — Applications",
    "Unit V — System Design"
  ];

  const struct = typeof AcademicMockData !== 'undefined' ? AcademicMockData?.subjectStructure?.[subjectVal] : null;
  let customUnits = [];

  if (struct && struct.units) {
    struct.units.forEach(u => {
      if (u.name) customUnits.push(u.name);
    });
  }

  if (unitListEl) {
    const combinedUnits = ["All Units (Complete Syllabus)", "Unit 1", "Unit 2", "Unit 3", "Unit 4", "Unit 5", ...customUnits];
    const uniqueUnits = Array.from(new Set(combinedUnits));
    unitListEl.innerHTML = uniqueUnits.map(u => `<option value="${u}">`).join('\\n');
  }

  if (topicListEl) {
    let matchedTopics = [];
    if (struct && struct.units) {
      const uObj = struct.units.find(u => (u.name || u.id) === unitVal || (u.id && unitVal.includes(u.id)));
      if (uObj && uObj.topics) {
        matchedTopics.push(...uObj.topics);
      }
    }
    if (matchedTopics.length === 0) {
      matchedTopics = [
        "Core Architectural Principles",
        "Functional Mechanisms and Operations",
        "Query Optimization & Indexing",
        "Transaction Management & Concurrency",
        "Practical Implementation & Case Studies",
        "System Analysis & Performance"
      ];
      if (subjectVal) {
        matchedTopics.unshift(`${subjectVal} Fundamentals`, `${subjectVal} Key Implementations`);
      }
    }
    const uniqueTopics = Array.from(new Set(matchedTopics));
    topicListEl.innerHTML = uniqueTopics.map(t => `<option value="${t}">`).join('\\n');
  }
}
"""

if "function syncModuleDatalists" not in content:
    # insert before initVoiceQuestionForm
    content = content.replace("function initVoiceQuestionForm()", helper_fn + "\nfunction initVoiceQuestionForm()")
    print("SUCCESS: Inserted syncModuleDatalists helper")

# 3. Replace populateVoiceTopics, populateImageTopics, populateTransTopics, populatePPTTopics, populateLPTopics, updateAssignmentUnitsDropdown
def replace_func(fn_name, new_code):
    global content
    pattern = re.compile(r'function\s+' + fn_name + r'\s*\([^)]*\)\s*\{[\s\S]*?(?=\n(?:async\s+)?function|\Z)')
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + new_code + "\n" + content[m.end():]
        print(f"SUCCESS: Replaced {fn_name}")
    else:
        print(f"WARN: Could not find {fn_name}")

replace_func('populateVoiceTopics', """function populateVoiceTopics() {
  syncModuleDatalists('voiceSubjectSelect', 'voiceSubjectList', 'voiceUnitSelect', 'voiceUnitList', 'voiceTopicSelect', 'voiceTopicList');
}""")

replace_func('populateImageTopics', """function populateImageTopics() {
  syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
}""")

replace_func('populateTransTopics', """function populateTransTopics() {
  syncModuleDatalists('transSubjectSelect', 'transSubjectList', 'transUnitSelect', 'transUnitList', 'transTopicSelect', 'transTopicList');
}""")

replace_func('populatePPTTopics', """function populatePPTTopics() {
  syncModuleDatalists('pptSubjectSelect', 'pptSubjectList', 'pptUnitSelect', 'pptUnitList', 'pptTopicSelect', 'pptTopicList');
}""")

replace_func('populateLPTopics', """function populateLPTopics() {
  syncModuleDatalists('lpSubjectSelect', 'lpSubjectList', 'lpUnitSelect', 'lpUnitList', 'lpTopicSelect', 'lpTopicList');
}""")

replace_func('updateAssignmentUnitsDropdown', """function updateAssignmentUnitsDropdown() {
  syncModuleDatalists('asnSubject', 'asnSubjectList', 'asnUnit', 'asnUnitList', 'asnTopic', 'asnTopicList');
  updateAssignmentSourcePanel();
}""")

# 4. Replace init forms
replace_func('initVoiceQuestionForm', """function initVoiceQuestionForm() {
  const subj = document.getElementById('voiceSubjectSelect');
  const unit = document.getElementById('voiceUnitSelect');
  const sync = () => syncModuleDatalists('voiceSubjectSelect', 'voiceSubjectList', 'voiceUnitSelect', 'voiceUnitList', 'voiceTopicSelect', 'voiceTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}""")

replace_func('initImageQuestionForm', """function initImageQuestionForm() {
  const subj = document.getElementById('imgSubjectSelect');
  const unit = document.getElementById('imgUnitSelect');
  const sync = () => syncModuleDatalists('imgSubjectSelect', 'imgSubjectList', 'imgUnitSelect', 'imgUnitList', 'imgTopicSelect', 'imgTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();

  const fileInput = document.getElementById('imageFileInput');
  if (fileInput) {
    fileInput.addEventListener('change', handleImageUploadSelection);
  }
}""")

replace_func('initLanguageConverterForm', """function initLanguageConverterForm() {
  const subj = document.getElementById('transSubjectSelect');
  const unit = document.getElementById('transUnitSelect');
  const sync = () => syncModuleDatalists('transSubjectSelect', 'transSubjectList', 'transUnitSelect', 'transUnitList', 'transTopicSelect', 'transTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}""")

replace_func('initPPTGeneratorForm', """function initPPTGeneratorForm() {
  const subj = document.getElementById('pptSubjectSelect');
  const unit = document.getElementById('pptUnitSelect');
  const sync = () => syncModuleDatalists('pptSubjectSelect', 'pptSubjectList', 'pptUnitSelect', 'pptUnitList', 'pptTopicSelect', 'pptTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}""")

replace_func('initLessonPlanGeneratorForm', """function initLessonPlanGeneratorForm() {
  const subj = document.getElementById('lpSubjectSelect');
  const unit = document.getElementById('lpUnitSelect');
  const sync = () => syncModuleDatalists('lpSubjectSelect', 'lpSubjectList', 'lpUnitSelect', 'lpUnitList', 'lpTopicSelect', 'lpTopicList');
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  sync();
}""")

replace_func('initAssignmentGeneratorForm', """function initAssignmentGeneratorForm() {
  const subj = document.getElementById('asnSubject');
  const unit = document.getElementById('asnUnit');
  const form = document.getElementById('assignmentGeneratorForm');
  const sync = () => {
    syncModuleDatalists('asnSubject', 'asnSubjectList', 'asnUnit', 'asnUnitList', 'asnTopic', 'asnTopicList');
    updateAssignmentSourcePanel();
  };
  if (subj) {
    subj.addEventListener('input', sync);
    subj.addEventListener('change', sync);
  }
  if (unit) {
    unit.addEventListener('input', sync);
    unit.addEventListener('change', sync);
  }
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      generateAssignmentAction();
    });
  }
  sync();
}""")

# 5. Update generateAssignmentAction
new_gen_assignment = """function generateAssignmentAction() {
  const numQuestions = Math.max(1, parseInt(document.getElementById('asnNumQuestions')?.value || 5));
  const dept = (document.getElementById('asnDept')?.value || '').trim() || "Artificial Intelligence & Data Science";
  const subject = (document.getElementById('asnSubject')?.value || '').trim() || "Database Management Systems";
  const unit = (document.getElementById('asnUnit')?.value || '').trim() || "Unit 1";
  const rawTopic = (document.getElementById('asnTopic')?.value || '').trim();
  const topic = rawTopic || (unit.includes('All Units') ? 'Complete Course Syllabus' : `${subject} Principles`);
  const maxMarks = parseInt(document.getElementById('asnTotalMarks')?.value || 50);

  const baseTopic = topic;
  const sampleAsnQuestions = [
    { text: `Explain the fundamental concepts and significance of ${baseTopic} in ${subject}.`, difficulty: "Easy", concept: `${baseTopic} Fundamentals`, blooms: "Understand" },
    { text: `Analyze the architectural requirements and operational workflow of ${baseTopic} (${unit}).`, difficulty: "Medium", concept: "System Architecture", blooms: "Analyze" },
    { text: `Apply key design patterns and implementation methodologies for ${baseTopic} in ${subject}.`, difficulty: "Medium", concept: "Applied Methodology", blooms: "Apply" },
    { text: `Compare alternative design approaches and optimization techniques used in ${baseTopic}.`, difficulty: "Hard", concept: "Comparative Analysis", blooms: "Evaluate" },
    { text: `Design an end-to-end framework solving real-world challenges related to ${baseTopic} in ${subject}.`, difficulty: "Hard", concept: "Framework Design", blooms: "Create" },
    { text: `Examine failure modes, error handling, and reliability strategies in ${baseTopic}.`, difficulty: "Medium", concept: "System Reliability", blooms: "Analyze" },
    { text: `Describe verification and testing methodologies applied to ${baseTopic} (${unit}).`, difficulty: "Easy", concept: "Testing & Validation", blooms: "Understand" },
    { text: `Formulate performance benchmarks and scaling strategies for ${baseTopic} implementations.`, difficulty: "Hard", concept: "Performance Scaling", blooms: "Evaluate" }
  ];

  const markPerQ = Math.max(1, Math.round(maxMarks / numQuestions));
  activeGeneratedAssignmentQuestions = [];

  for (let i = 0; i < numQuestions; i++) {
    const tmpl = sampleAsnQuestions[i % sampleAsnQuestions.length];
    activeGeneratedAssignmentQuestions.push({
      num: i + 1,
      text: tmpl.text,
      marks: markPerQ,
      difficulty: tmpl.difficulty,
      concept: tmpl.concept,
      blooms: tmpl.blooms,
      unit: unit,
      subject: subject,
      department: dept
    });
  }

  renderGeneratedAssignment();

  const resultsSection = document.getElementById('generatedAssignmentResults');
  if (resultsSection) resultsSection.classList.remove('d-none');
  if (resultsSection) window.scrollTo({ top: resultsSection.offsetTop - 70, behavior: 'smooth' });
}"""

replace_func('generateAssignmentAction', new_gen_assignment)

# 6. Fix unitText in generateQuestionsFromVoice, generateQuestionsFromImage, convertAcademicLanguage, generatePPTContent, generateLessonPlanContent
voice_unit_fix = (
    r"const unitText = document\.getElementById\('voiceUnitSelect'\)\?\.options\[document\.getElementById\('voiceUnitSelect'\)\?\.selectedIndex\]\?\.text \|\| [^;]+;",
    "const unitText = (document.getElementById('voiceUnitSelect')?.value || '').trim() || 'Unit 1';"
)
content = re.sub(voice_unit_fix[0], voice_unit_fix[1], content)

img_unit_fix = (
    r"const unitText = document\.getElementById\('imgUnitSelect'\)\?\.options\[document\.getElementById\('imgUnitSelect'\)\?\.selectedIndex\]\?\.text \|\| [^;]+;",
    "const unitText = (document.getElementById('imgUnitSelect')?.value || '').trim() || 'Unit 1';"
)
content = re.sub(img_unit_fix[0], img_unit_fix[1], content)

trans_unit_fix = (
    r"const unitText = document\.getElementById\('transUnitSelect'\)\?\.options\[document\.getElementById\('transUnitSelect'\)\?\.selectedIndex\]\?\.text \|\| [^;]+;",
    "const unitText = (document.getElementById('transUnitSelect')?.value || '').trim() || 'Unit 1';"
)
content = re.sub(trans_unit_fix[0], trans_unit_fix[1], content)

ppt_unit_fix = (
    r"const unitText = document\.getElementById\('pptUnitSelect'\)\?\.options\[document\.getElementById\('pptUnitSelect'\)\?\.selectedIndex\]\?\.text \|\| [^;]+;",
    "const unitText = (document.getElementById('pptUnitSelect')?.value || '').trim() || 'Unit 1';"
)
content = re.sub(ppt_unit_fix[0], ppt_unit_fix[1], content)

lp_unit_fix = (
    r"const unitText = document\.getElementById\('lpUnitSelect'\)\?\.options\[document\.getElementById\('lpUnitSelect'\)\?\.selectedIndex\]\?\.text \|\| [^;]+;",
    "const unitText = (document.getElementById('lpUnitSelect')?.value || '').trim() || 'Unit 1';"
)
content = re.sub(lp_unit_fix[0], lp_unit_fix[1], content)

with open(APP_JS, "w", encoding="utf-8") as f:
    f.write(content)
print("Done writing updated app.js")
