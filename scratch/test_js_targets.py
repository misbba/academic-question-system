with open(r'C:\Users\Nisha\.gemini\antigravity\scratch\academic-question-system\js\app.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Test finding targets
targets = [
    # 1. initRoleManagement after updateFacultyHeaderProfile(verifiedUser);
    """    updateFacultyHeaderProfile(verifiedUser);



    if (path.includes('faculty-dashboard')) {""",
    
    # 2. Paper builder fallback
    """      if (qData.status === 'success' && qData.questions && qData.questions.length > 0) {



        window.paperQuestionBankPool = qData.questions;



      } else if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {



        window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;



      }""",

    # 3. Paper builder catch fallback
    """  } catch (err) {



    console.warn('Backend fetch failed for Question Bank, falling back to mock pool:', err);



    if (typeof AcademicMockData !== 'undefined' && AcademicMockData.masterQuestionsPool) {



      window.paperQuestionBankPool = AcademicMockData.masterQuestionsPool;



    }



  }""",

    # 4. Voice save and render
    """  const stored = JSON.parse(localStorage.getItem('academic_voice_questions') || '[]').concat(AcademicMockData.publishedVoiceQuestions);""",

    # 5. Image render
    """  const stored = JSON.parse(localStorage.getItem('academic_image_questions') || '[]').concat(AcademicMockData.publishedImageQuestions);""",

    # 6. Translated render
    """  const stored = JSON.parse(localStorage.getItem('academic_translated_questions') || '[]').concat(AcademicMockData.publishedTranslatedQuestions);""",

    # 7. PPT render
    """  const storedPPTs = JSON.parse(localStorage.getItem('academic_ppts') || '[]').concat(AcademicMockData.publishedPPTs);""",

    # 8. Lesson plan render
    """  const storedLPs = JSON.parse(localStorage.getItem('academic_lesson_plans') || '[]').concat(AcademicMockData.publishedLessonPlans);""",

    # 9. handleLogout
    """function handleLogout() {
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
]

c_norm = c.replace('\r\n', '\n')
for i, t in enumerate(targets):
    t_norm = t.replace('\r\n', '\n')
    found = t_norm in c_norm
    print(f"Target {i+1} found: {found}")
    if not found:
        # print snippet of where it might be
        first_line = t_norm.strip().split('\n')[0]
        pos = c_norm.find(first_line)
        print(f"  First line '{first_line}': pos {pos}")
