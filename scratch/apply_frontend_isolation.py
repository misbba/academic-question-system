import os

base_dir = r"C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system"
app_js_path = os.path.join(base_dir, "js", "app.js")

with open(app_js_path, "r", encoding="utf-8") as f:
    code = f.read()

# Normalize CRLF for reliable string replacements
norm_code = code.replace("\r\n", "\n")

# 1. Add getScopedStorageKey at the top of app.js (after the first docstring/comment)
storage_helper = """
// Faculty Data Isolation & Storage Scoping Helper
function getScopedStorageKey(baseKey) {
  try {
    const userStr = localStorage.getItem('academic_user');
    if (userStr) {
      const u = JSON.parse(userStr);
      if (u && (u.id || u.identifier || u.email)) {
        const uid = u.id || (u.identifier ? u.identifier.replace(/[^a-zA-Z0-9]/g, '_') : 'guest');
        return `${baseKey}_${uid}`;
      }
    }
  } catch (e) {}
  return baseKey;
}
"""

if "function getScopedStorageKey(" not in norm_code:
    norm_code = storage_helper + "\n" + norm_code
    print("1. Added getScopedStorageKey helper")
else:
    print("1. getScopedStorageKey already present")

# 2. Add setupFacultyCourseContext and populateFacultyResourceSelects
faculty_context_funcs = """
// Setup Faculty Course Context & Strict Isolation across all modules
async function setupFacultyCourseContext(user) {
  if (!user) return;
  const userId = user.id;
  const userName = (user.full_name || user.name || '').toLowerCase();
  const userEmail = (user.email || '').toLowerCase();

  // 1. Fetch authorized courses for this faculty from backend API
  let courses = [];
  try {
    const res = await fetch('http://localhost:5000/api/faculty/courses', { credentials: 'include' });
    if (res.ok) {
      const data = await res.json();
      if (data.status === 'success' && Array.isArray(data.courses)) {
        courses = data.courses;
      }
    }
  } catch (err) {
    console.warn('Could not fetch faculty courses:', err);
  }

  // Fallback / deterministic defaults if no courses returned yet
  if (courses.length === 0) {
    if (userName.includes('kavitha') || userEmail.includes('kavitha') || userId === 25) {
      courses = [{ course_name: 'Distributed Computing', department: user.department || 'Artificial Intelligence & Data Science' }];
    } else {
      courses = [
        { course_name: 'Database Management Systems', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Distributed Computing', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Cloud Computing', department: 'Artificial Intelligence & Data Science' },
        { course_name: 'Machine Learning', department: 'Artificial Intelligence & Data Science' }
      ];
    }
  }

  window.facultyAuthorizedCourses = courses;

  // Determine primary authorized course
  let primaryCourse = courses[0].course_name;
  if (userName.includes('kavitha') || userEmail.includes('kavitha') || userId === 25) {
    primaryCourse = 'Distributed Computing';
  }

  const isCourseAuthorized = (subj) => {
    if (!subj) return false;
    return courses.some(c => c.course_name.toLowerCase() === subj.trim().toLowerCase());
  };

  // 2. Update subject input fields across all modules
  const subjectInputIds = [
    'genSubject', 'voiceSubjectSelect', 'imgSubjectSelect', 'transSubjectSelect',
    'paperSubject', 'addQSubject', 'quizSubject', 'asnSubject', 'pptSubjectSelect',
    'lpSubjectSelect', 'resSubject', 'filterSubject', 'paperFilterSubject'
  ];

  subjectInputIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      // If current value is not authorized for this faculty (e.g. DBMS for Kavitha) or is default
      if (!isCourseAuthorized(el.value) || el.value === 'Database Management Systems') {
        if (!courses.some(c => c.course_name.toLowerCase() === 'database management systems')) {
          el.value = primaryCourse;
        }
      }
    }
  });

  // 3. Update datalists with ONLY this faculty's authorized courses
  const datalistIds = [
    'genSubjectList', 'voiceSubjectList', 'imgSubjectList', 'transSubjectList',
    'paperSubjectList', 'quizSubjectList', 'asnSubjectList', 'pptSubjectList',
    'lpSubjectList', 'resSubjectList'
  ];

  const courseOptionsHtml = courses.map(c => `<option value="${c.course_name}">`).join('');
  datalistIds.forEach(dlId => {
    const dl = document.getElementById(dlId);
    if (dl) {
      dl.innerHTML = courseOptionsHtml;
    }
  });

  // 4. Update Department inputs
  const deptInputIds = [
    'genDept', 'voiceDeptSelect', 'imgDeptSelect', 'transDeptSelect',
    'paperDept', 'quizDept', 'asnDept', 'pptDeptSelect', 'lpDeptSelect', 'resDept'
  ];
  const userDept = user.department || 'Artificial Intelligence & Data Science';
  deptInputIds.forEach(id => {
    const el = document.getElementById(id);
    if (el && (!el.value || el.value.trim() === '')) {
      el.value = userDept;
    }
  });

  // 5. Fetch and populate Study Materials / Resources dropdowns with ONLY this faculty's materials
  try {
    const resResp = await fetch('http://localhost:5000/api/resources', { credentials: 'include' });
    if (resResp.ok) {
      const resData = await resResp.json();
      if (resData.status === 'success' && Array.isArray(resData.resources)) {
        window.facultyOwnedResources = resData.resources;
        populateFacultyResourceSelects(resData.resources, primaryCourse);
      }
    }
  } catch (err) {
    console.warn('Could not fetch faculty resources for dropdowns:', err);
  }
}

function populateFacultyResourceSelects(resources, selectedSubject) {
  const resourceSelectIds = [
    'genResourceSelect', 'notesResourceSelect', 'quizMaterialSelect',
    'voiceMaterialSelect', 'imgMaterialSelect', 'transMaterialSelect',
    'pptMaterialSelect', 'lpMaterialSelect'
  ];

  resourceSelectIds.forEach(selectId => {
    const sel = document.getElementById(selectId);
    if (!sel) return;

    const matching = selectedSubject
      ? resources.filter(r => (r.subject || '').toLowerCase() === selectedSubject.toLowerCase())
      : resources;
    const listToUse = matching.length > 0 ? matching : resources;

    let html = `<option value="">Choose Uploaded Material...</option>`;
    listToUse.forEach(r => {
      html += `<option value="${r.id}" data-subject="${r.subject}" data-unit="${r.unit || ''}">${r.title || r.subject} (${r.resource_type || 'Material'})</option>`;
    });
    sel.innerHTML = html;
  });
}
"""

if "function setupFacultyCourseContext(" not in norm_code:
    norm_code = faculty_context_funcs + "\n" + norm_code
    print("2. Added setupFacultyCourseContext functions")
else:
    print("2. setupFacultyCourseContext already present")

# 3. Hook setupFacultyCourseContext into initRoleManagement
target_hook = "updateFacultyHeaderProfile(verifiedUser);"
hook_code = """updateFacultyHeaderProfile(verifiedUser);
    await setupFacultyCourseContext(verifiedUser);"""

if target_hook in norm_code and "await setupFacultyCourseContext(verifiedUser);" not in norm_code:
    norm_code = norm_code.replace(target_hook, hook_code, 1)
    print("3. Hooked setupFacultyCourseContext into initRoleManagement")
else:
    print("3. Hook already present or target missing")

# 4. Remove fallback to AcademicMockData.masterQuestionsPool in loadQuestionPaperBuilderPage
target_qb_pool = """      if (qData.status === 'success' && qData.questions && qData.questions.length > 0) {



        window.paperQuestionBankPool = qData.questions;



      } else if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {



        window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;



      }"""

repl_qb_pool = """      if (qData.status === 'success' && qData.questions && qData.questions.length > 0) {
        window.paperQuestionBankPool = qData.questions;
      } else {
        window.paperQuestionBankPool = [];
      }"""

if target_qb_pool in norm_code:
    norm_code = norm_code.replace(target_qb_pool, repl_qb_pool)
    print("4a. Replaced paper bank pool fallback")

target_qb_catch = """    if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {



      window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;



    }"""

repl_qb_catch = """    window.paperQuestionBankPool = [];"""

if target_qb_catch in norm_code:
    norm_code = norm_code.replace(target_qb_catch, repl_qb_catch)
    print("4b. Replaced paper bank pool catch fallback")

# 5. Fix Voice History rendering (remove AcademicMockData concat, use getScopedStorageKey)
target_voice_hist = "const stored = JSON.parse(localStorage.getItem('academic_voice_questions') || '[]').concat(AcademicMockData.publishedVoiceQuestions);"
repl_voice_hist = "const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_voice_questions')) || '[]');"
if target_voice_hist in norm_code:
    norm_code = norm_code.replace(target_voice_hist, repl_voice_hist)
    print("5a. Replaced voice history render")

# 5b. Fix Image History rendering
target_img_hist = "const stored = JSON.parse(localStorage.getItem('academic_image_questions') || '[]').concat(AcademicMockData.publishedImageQuestions);"
repl_img_hist = "const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_image_questions')) || '[]');"
if target_img_hist in norm_code:
    norm_code = norm_code.replace(target_img_hist, repl_img_hist)
    print("5b. Replaced image history render")

# 5c. Fix Translated History rendering
target_trans_hist = "const stored = JSON.parse(localStorage.getItem('academic_translated_questions') || '[]').concat(AcademicMockData.publishedTranslatedQuestions);"
repl_trans_hist = "const stored = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_translated_questions')) || '[]');"
if target_trans_hist in norm_code:
    norm_code = norm_code.replace(target_trans_hist, repl_trans_hist)
    print("5c. Replaced translated history render")

# 5d. Fix PPT History rendering
target_ppt_hist = "const storedPPTs = JSON.parse(localStorage.getItem('academic_ppts') || '[]').concat(AcademicMockData.publishedPPTs);"
repl_ppt_hist = "const storedPPTs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_ppts')) || '[]');"
if target_ppt_hist in norm_code:
    norm_code = norm_code.replace(target_ppt_hist, repl_ppt_hist)
    print("5d. Replaced PPT history render")

# 5e. Fix Lesson Plan History rendering
target_lp_hist = "const storedLPs = JSON.parse(localStorage.getItem('academic_lesson_plans') || '[]').concat(AcademicMockData.publishedLessonPlans);"
repl_lp_hist = "const storedLPs = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_lesson_plans')) || '[]');"
if target_lp_hist in norm_code:
    norm_code = norm_code.replace(target_lp_hist, repl_lp_hist)
    print("5e. Replaced Lesson Plan history render")

# 5f. Fix Assignments rendering in student / faculty pages
target_asn_hist = "const storedAsns = JSON.parse(localStorage.getItem('academic_assignments') || '[]').concat(AcademicMockData.publishedAssignments);"
repl_asn_hist = "const storedAsns = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_assignments')) || '[]');"
if target_asn_hist in norm_code:
    norm_code = norm_code.replace(target_asn_hist, repl_asn_hist)
    print("5f. Replaced Assignments render")

# 5g. Scoped storage for saving
norm_code = norm_code.replace(
    "localStorage.setItem('academic_voice_questions', JSON.stringify(voiceList));",
    "localStorage.setItem(getScopedStorageKey('academic_voice_questions'), JSON.stringify(voiceList));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_voice_questions', JSON.stringify(list));",
    "localStorage.setItem(getScopedStorageKey('academic_voice_questions'), JSON.stringify(list));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_image_questions', JSON.stringify(list));",
    "localStorage.setItem(getScopedStorageKey('academic_image_questions'), JSON.stringify(list));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_translated_questions', JSON.stringify(list));",
    "localStorage.setItem(getScopedStorageKey('academic_translated_questions'), JSON.stringify(list));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_ppts', JSON.stringify(ppts));",
    "localStorage.setItem(getScopedStorageKey('academic_ppts'), JSON.stringify(ppts));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_lesson_plans', JSON.stringify(lps));",
    "localStorage.setItem(getScopedStorageKey('academic_lesson_plans'), JSON.stringify(lps));"
)
norm_code = norm_code.replace(
    "localStorage.setItem('academic_assignments', JSON.stringify(storedAsns));",
    "localStorage.setItem(getScopedStorageKey('academic_assignments'), JSON.stringify(storedAsns));"
)
print("5g. Replaced save calls with getScopedStorageKey")

# 6. Fix handleLogout
target_logout = """function handleLogout() {

  try {

    await fetch('http://localhost:5000/api/auth/logout', {

      method: 'POST',

      credentials: 'include'

    });

  } catch (err) {

    console.warn('Server logout failed:', err);

  }

  localStorage.removeItem('academic_role');

  localStorage.removeItem('academic_user');

  sessionStorage.clear();

  window.location.href = 'index.html';

}"""

repl_logout = """async function handleLogout() {
  try {
    await fetch('http://localhost:5000/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
  } catch (err) {
    console.warn('Server logout failed:', err);
  }
  // Clear all academic session, cache and user data
  const keysToRemove = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (k && (k.startsWith('academic_') || k.startsWith('faculty_') || k.startsWith('paper_'))) {
      keysToRemove.push(k);
    }
  }
  keysToRemove.forEach(k => localStorage.removeItem(k));
  sessionStorage.clear();
  window.paperQuestionBankPool = [];
  window.facultyAuthorizedCourses = [];
  window.currentFacultyQuestions = [];
  window.location.href = 'index.html';
}"""

if target_logout in norm_code:
    norm_code = norm_code.replace(target_logout, repl_logout)
    print("6. Successfully replaced handleLogout")
else:
    print("6. Target for handleLogout not found")

# 7. Also fix getAllFacultyHistory and getAllStudentResults
target_get_hist = """function getAllFacultyHistory() {



  const localHist = JSON.parse(localStorage.getItem('academic_faculty_history') || '[]');



  return localHist;



}"""

repl_get_hist = """function getAllFacultyHistory() {
  const localHist = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_faculty_history')) || '[]');
  return localHist;
}"""

if target_get_hist in norm_code:
    norm_code = norm_code.replace(target_get_hist, repl_get_hist)
    print("7a. Successfully updated getAllFacultyHistory")

target_get_res = """function getAllStudentResults() {



  const localResults = JSON.parse(localStorage.getItem('academic_quiz_results') || '[]');



  return localResults;



}"""

repl_get_res = """function getAllStudentResults() {
  const localResults = JSON.parse(localStorage.getItem(getScopedStorageKey('academic_quiz_results')) || '[]');
  return localResults;
}"""

if target_get_res in norm_code:
    norm_code = norm_code.replace(target_get_res, repl_get_res)
    print("7b. Successfully updated getAllStudentResults")

with open(app_js_path, "w", encoding="utf-8") as f:
    f.write(norm_code)

print("\nApp.js updated successfully!")
