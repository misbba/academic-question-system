// Frontend Simulation Test: Semester Examination Marks & Publish Validation
const fs = require('fs');
const path = require('path');

const appJsPath = path.join(__dirname, '..', 'js', 'app.js');
const appJsCode = fs.readFileSync(appJsPath, 'utf8');

// Create mock DOM environment
const domMock = {
  elements: {},
  addEventListener() {},
  getElementById(id) {
    if (!this.elements[id]) {
      this.elements[id] = {
        value: '',
        textContent: '',
        className: '',
        innerHTML: '',
        style: {},
        scrollIntoView() {},
        classList: { add() {}, remove() {}, contains() { return false; } }
      };
    }
    return this.elements[id];
  }
};

global.document = domMock;
global.window = {
  currentGeneratedTemplate: null,
  currentSavedPaper: null,
  paperSelectedQuestions: [],
  location: { search: '' }
};
global.showToastNotice = (title, message, type) => {
  lastToast = { title, message, type };
};

let lastToast = null;

// Evaluate app.js in context (or extract the functions)
eval(appJsCode);

// Override showToastNotice after app.js definition
const origToast = showToastNotice;
showToastNotice = (title, message, type) => {
  lastToast = { title, message, type };
  if (typeof origToast === 'function') origToast(title, message, type);
};

console.log("================================================================================");
console.log("RUNNING FRONTEND PUBLISH & MARKS CALCULATION SIMULATION");
console.log("================================================================================");

// TEST 1: calculateAttemptedMarks Compulsory
console.log("\n[TEST 1] Client-side calculateAttemptedMarks: Compulsory Questions");
const partA = [{
  name: "PART - A (10 x 2 = 20 Marks)",
  questions: Array.from({ length: 10 }, (_, i) => ({ id: i + 1, marks: 2 }))
}];
const attA = calculateAttemptedMarks(partA);
console.log(`  -> Calculated: ${attA} marks`);
if (attA !== 20) throw new Error(`Expected 20, got ${attA}`);

// TEST 2: calculateAttemptedMarks Either/Or Alternative (Single Choice Counted)
console.log("\n[TEST 2] Client-side calculateAttemptedMarks: Either/Or Alternative (Single Choice Counted)");
const partB = [{
  name: "PART - B (5 x 16 = 80 Marks)",
  groups: [
    {
      group_number: 1,
      alternative_a: { id: 101, marks: 16 },
      alternative_b: {
        is_subquestion: true,
        marks: 16,
        subquestions: [{ marks: 8 }, { marks: 8 }]
      }
    }
  ]
}];
const attB = calculateAttemptedMarks(partB);
console.log(`  -> Calculated: ${attB} marks (not 32M)`);
if (attB !== 16) throw new Error(`Expected 16, got ${attB}`);

// TEST 3: Total 100 Marks for Semester Examination Sections
console.log("\n[TEST 3] Total 100 Marks for Semester Examination Sections");
const semSections = [
  ...partA,
  {
    name: "PART - B (5 x 16 = 80 Marks)",
    groups: Array.from({ length: 5 }, (_, i) => ({
      group_number: i + 1,
      alternative_a: { id: 100 + i, marks: 16 },
      alternative_b: { id: 200 + i, marks: 16 }
    }))
  }
];
const totalSem = calculateAttemptedMarks(semSections);
console.log(`  -> Calculated Total Attempted: ${totalSem} marks`);
if (totalSem !== 100) throw new Error(`Expected 100, got ${totalSem}`);

// TEST 4: onExamTypeChanged sets correct target marks and duration
console.log("\n[TEST 4] onExamTypeChanged Form Synchronization");
document.getElementById('paperExamType').value = 'Semester Examination';
onExamTypeChanged();
console.log(`  -> Semester Exam: Max Marks = ${document.getElementById('paperMaxMarks').value}, Duration = ${document.getElementById('paperDuration').value}`);
if (document.getElementById('paperMaxMarks').value !== 100) throw new Error('Expected 100 marks');

document.getElementById('paperExamType').value = 'Internal Examination';
onExamTypeChanged();
console.log(`  -> Internal Exam: Max Marks = ${document.getElementById('paperMaxMarks').value}, Duration = ${document.getElementById('paperDuration').value}`);
if (document.getElementById('paperMaxMarks').value !== 50) throw new Error('Expected 50 marks');

// TEST 5: publishQuestionPaperAction halts and warns if paper has only 50 attempted marks
console.log("\n[TEST 5] publishQuestionPaperAction Rejects Incomplete 50-Mark Paper");
document.getElementById('paperExamType').value = 'Semester Examination';
window.currentGeneratedTemplate = {
  sections: [
    { name: "PART - A", count: 5, marks_per_q: 2 },
    { name: "PART - B", count: 1, marks_per_q: 8 },
    { name: "PART - C", count: 2, marks_per_q: 16 }
  ]
}; // Attempted: 10 + 8 + 32 = 50 marks
lastToast = null;
publishQuestionPaperAction();
console.log(`  -> Toast Notice Received: [${lastToast.title}] ${lastToast.message}`);
if (!lastToast || !lastToast.message.includes('Semester Examination must have exactly 100 attempted marks (calculated: 50 marks)')) {
  throw new Error(`Expected validation error toast for 50-mark paper, got: ${JSON.stringify(lastToast)}`);
}
console.log("  -> PASS: Frontend pre-publishing validation successfully intercepted 50-mark paper.");

console.log("\n================================================================================");
console.log("ALL FRONTEND SIMULATION TESTS PASSED SUCCESSFULLY!");
console.log("================================================================================");
