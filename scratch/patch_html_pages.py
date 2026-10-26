import os
import re

# 1. Patch faculty-generate-questions.html
fgq_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-generate-questions.html'
with open(fgq_path, 'r', encoding='utf-8') as f:
    fgq = f.read()

# Replace Department dropdown with text input + datalist
fgq = re.sub(
    r'<div class="col-md-6">\s*<label for="genDept" class="form-label fw-semibold">Department</label>\s*<select class="form-select" id="genDept" required>.*?</select>\s*</div>',
    '''<div class="col-md-6">
                <label for="genDept" class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="genDept" list="genDeptList" placeholder="Enter department name" value="Artificial Intelligence & Data Science" required>
                <datalist id="genDeptList">
                  <option value="Artificial Intelligence & Data Science">
                  <option value="Artificial Intelligence & Machine Learning">
                  <option value="Computer and Communication Engineering">
                  <option value="Computer Science and Engineering">
                  <option value="Information Technology">
                </datalist>
              </div>''',
    fgq,
    flags=re.DOTALL
)

# Replace Subject dropdown with text input + datalist
fgq = re.sub(
    r'<div class="col-md-6">\s*<label for="genSubject" class="form-label fw-semibold">Subject</label>\s*<select class="form-select" id="genSubject" required>.*?</select>\s*</div>',
    '''<div class="col-md-6">
                <label for="genSubject" class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="genSubject" list="genSubjectList" placeholder="Enter subject name" value="Database Management Systems" required>
                <datalist id="genSubjectList">
                  <option value="Database Management Systems">
                  <option value="Artificial Intelligence">
                  <option value="Machine Learning">
                  <option value="Distributed Computing">
                  <option value="Data Structures">
                  <option value="Computer Networks">
                  <option value="Operating Systems">
                  <option value="Python Programming">
                </datalist>
              </div>''',
    fgq,
    flags=re.DOTALL
)

# Replace Unit dropdown with editable text input + datalist
fgq = re.sub(
    r'<div class="col-md-4">\s*<label for="genUnit" class="form-label fw-semibold">Unit</label>\s*<select class="form-select" id="genUnit" required>.*?</select>\s*</div>',
    '''<div class="col-md-4">
                <label for="genUnit" class="form-label fw-semibold">Unit</label>
                <input type="text" class="form-control" id="genUnit" list="genUnitList" placeholder="e.g. Unit I — Introduction or All Units" value="All Units (Complete Syllabus)" required>
                <datalist id="genUnitList">
                  <option value="All Units (Complete Syllabus)">
                  <option value="Unit I — Introduction">
                  <option value="Unit II — Core Concepts">
                  <option value="Unit III — Advanced Methodologies">
                  <option value="Unit IV — Applications & Design">
                  <option value="Unit V — Emerging Trends">
                </datalist>
              </div>''',
    fgq,
    flags=re.DOTALL
)

# Replace Topic dropdown with editable text input + datalist
fgq = re.sub(
    r'<div class="col-md-6">\s*<label for="genTopic" class="form-label fw-semibold">Topic</label>\s*<select class="form-select" id="genTopic" required>.*?</select>\s*</div>',
    '''<div class="col-md-6">
                <label for="genTopic" class="form-label fw-semibold">Topic</label>
                <input type="text" class="form-control" id="genTopic" list="genTopicList" placeholder="Enter any topic or leave blank for all topics" value="">
                <datalist id="genTopicList">
                </datalist>
              </div>''',
    fgq,
    flags=re.DOTALL
)

# Replace Number of Questions with editable number input
fgq = re.sub(
    r'<div class="col-md-3">\s*<label for="genNumQuestions" class="form-label fw-semibold">Number of Questions</label>\s*<select class="form-select" id="genNumQuestions" required>.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="genNumQuestions" class="form-label fw-semibold">Number of Questions</label>
                <input type="number" class="form-control" id="genNumQuestions" min="1" max="100" value="10" placeholder="e.g. 10" required>
              </div>''',
    fgq,
    flags=re.DOTALL
)

# Enhance Source Material Section Panel
old_source_panel = re.search(r'<!-- Source Material Section Panel -->.*?(?=<!-- Main Submit Button -->)', fgq, re.DOTALL)
if old_source_panel:
    new_source_panel = '''<!-- Source Material Section Panel -->
              <div class="col-12 mt-3">
                <div class="card bg-light border p-3">
                  <div class="d-flex justify-content-between align-items-center mb-2 flex-wrap gap-2">
                    <span class="fw-bold text-primary"><i class="bi bi-file-earmark-medical me-2"></i> Study Materials & Syllabus Source</span>
                    <span class="badge" id="sourceMaterialStatusBadge" style="background:#0d6efd; color:#fff;">Status: Scanning Faculty Materials</span>
                  </div>
                  
                  <div class="row g-2 mb-3">
                    <div class="col-md-6">
                      <label class="form-label small fw-semibold text-muted mb-1">Select from Uploaded Materials</label>
                      <select class="form-select form-select-sm" id="genResourceSelect" onchange="onSourceResourceSelected()">
                        <option value="">-- All Uploaded Materials for this Subject --</option>
                      </select>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label small fw-semibold text-muted mb-1">Quick Upload Syllabus or Notes (PDF, DOCX, TXT)</label>
                      <div class="input-group input-group-sm">
                        <input type="file" class="form-control" id="genQuickUploadFile" accept=".pdf,.docx,.doc,.txt">
                        <select class="form-select" id="genQuickUploadType" style="max-width: 140px;">
                          <option value="Syllabus">Syllabus</option>
                          <option value="Study Material" selected>Study Notes</option>
                        </select>
                        <button type="button" class="btn btn-outline-primary" onclick="handleQuickUploadForGen()">
                          <i class="bi bi-upload"></i> Upload
                        </button>
                      </div>
                    </div>
                  </div>

                  <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" id="genUseQuestionBank" onchange="updateSourceMaterialDisplay()">
                    <label class="form-check-label small text-muted" for="genUseQuestionBank">
                      Also use verified questions from my Question Bank as a supplementary source
                    </label>
                  </div>

                  <div class="p-2 border rounded bg-white small" id="sourceDetailsBox">
                    <div class="row g-2 text-muted">
                      <div class="col-md-4"><strong>Subject:</strong> <span id="sourceSubjectDisplay" class="text-dark">Loading...</span></div>
                      <div class="col-md-4"><strong>Coverage:</strong> <span id="sourceUnitDisplay" class="text-dark">All Units</span></div>
                      <div class="col-md-4"><strong>Source Verified:</strong> <span id="sourceVerifiedDisplay" class="text-success fw-semibold"><i class="bi bi-check2-circle me-1"></i>Active</span></div>
                      <div class="col-12 mt-1"><strong>Syllabus / Topics Identified:</strong> <span id="sourceTopicsDisplay" class="text-dark">Detecting...</span></div>
                      <div class="col-12"><strong>Extracted Content:</strong> <span id="sourceConceptsDisplay" class="text-dark">Ready for grounded question synthesis</span></div>
                    </div>
                  </div>
                  <div id="sourceMaterialNotice" class="mt-2 small text-muted"></div>
                </div>
              </div>

              '''
    fgq = fgq.replace(old_source_panel.group(0), new_source_panel)

with open(fgq_path, 'w', encoding='utf-8') as f:
    f.write(fgq)

print("faculty-generate-questions.html patched.")


# 2. Patch faculty-generate-quiz.html
fgqz_path = r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\faculty-generate-quiz.html'
with open(fgqz_path, 'r', encoding='utf-8') as f:
    fgqz = f.read()

# Replace Dept
fgqz = re.sub(
    r'<div class="col-md-6">\s*<label for="quizDept" class="form-label fw-semibold">Department</label>\s*<select class="form-select" id="quizDept" required>.*?</select>\s*</div>',
    '''<div class="col-md-6">
                <label for="quizDept" class="form-label fw-semibold">Department</label>
                <input type="text" class="form-control" id="quizDept" list="quizDeptList" placeholder="Enter department name" value="Artificial Intelligence & Data Science" required>
                <datalist id="quizDeptList">
                  <option value="Artificial Intelligence & Data Science">
                  <option value="Artificial Intelligence & Machine Learning">
                  <option value="Computer and Communication Engineering">
                  <option value="Computer Science and Engineering">
                  <option value="Information Technology">
                </datalist>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Replace Subject
fgqz = re.sub(
    r'<div class="col-md-6">\s*<label for="quizSubject" class="form-label fw-semibold">Subject</label>\s*<select class="form-select" id="quizSubject" required>.*?</select>\s*</div>',
    '''<div class="col-md-6">
                <label for="quizSubject" class="form-label fw-semibold">Subject</label>
                <input type="text" class="form-control" id="quizSubject" list="quizSubjectList" placeholder="Enter subject name" value="Database Management Systems" required>
                <datalist id="quizSubjectList">
                  <option value="Database Management Systems">
                  <option value="Artificial Intelligence">
                  <option value="Machine Learning">
                  <option value="Distributed Computing">
                  <option value="Data Structures">
                  <option value="Computer Networks">
                </datalist>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Replace Unit
fgqz = re.sub(
    r'<div class="col-md-3">\s*<label for="quizUnit" class="form-label fw-semibold">Unit</label>\s*<select class="form-select" id="quizUnit" required>.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="quizUnit" class="form-label fw-semibold">Unit</label>
                <input type="text" class="form-control" id="quizUnit" list="quizUnitList" placeholder="e.g. All Units or Unit I" value="All Units (Complete Syllabus)" required>
                <datalist id="quizUnitList">
                  <option value="All Units (Complete Syllabus)">
                  <option value="Unit I — Introduction">
                  <option value="Unit II — Core Concepts">
                  <option value="Unit III — Advanced Topics">
                  <option value="Unit IV — Applications">
                  <option value="Unit V — Cloud & Emerging">
                </datalist>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Replace Topic
fgqz = re.sub(
    r'<div class="col-md-3">\s*<label for="quizTopic" class="form-label fw-semibold">Topic</label>\s*<select class="form-select" id="quizTopic" required>.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="quizTopic" class="form-label fw-semibold">Topic</label>
                <input type="text" class="form-control" id="quizTopic" list="quizTopicList" placeholder="Enter specific topic or leave blank for All">
                <datalist id="quizTopicList">
                </datalist>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Update Time Limit to default 30 minutes
fgqz = re.sub(
    r'<div class="col-md-3">\s*<label for="quizTimeLimit" class="form-label fw-semibold">Time Limit</label>\s*<select class="form-select" id="quizTimeLimit">.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="quizTimeLimit" class="form-label fw-semibold">Time Limit</label>
                <select class="form-select" id="quizTimeLimit">
                  <option value="30" selected>30 Minutes (Required Default)</option>
                  <option value="15">15 Minutes</option>
                  <option value="20">20 Minutes</option>
                  <option value="45">45 Minutes</option>
                  <option value="60">60 Minutes</option>
                </select>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Update Number of Questions to default 30 questions
fgqz = re.sub(
    r'<div class="col-md-3">\s*<label for="quizNumQuestions" class="form-label fw-semibold">Number of Questions</label>\s*<select class="form-select" id="quizNumQuestions">.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="quizNumQuestions" class="form-label fw-semibold">Number of Questions</label>
                <input type="number" class="form-control" id="quizNumQuestions" min="1" max="100" value="30" placeholder="e.g. 30" required>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

# Update Marks per Question to default 1 mark
fgqz = re.sub(
    r'<div class="col-md-3">\s*<label for="quizMarksPerQ" class="form-label fw-semibold">Marks per Question</label>\s*<select class="form-select" id="quizMarksPerQ">.*?</select>\s*</div>',
    '''<div class="col-md-3">
                <label for="quizMarksPerQ" class="form-label fw-semibold">Marks per Question</label>
                <select class="form-select" id="quizMarksPerQ">
                  <option value="1" selected>1 Mark (30 Questions = 30 Marks)</option>
                  <option value="2">2 Marks (15 Questions = 30 Marks)</option>
                </select>
              </div>''',
    fgqz,
    flags=re.DOTALL
)

with open(fgqz_path, 'w', encoding='utf-8') as f:
    f.write(fgqz)

print("faculty-generate-quiz.html patched.")
