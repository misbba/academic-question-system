const fs = require('fs');
const path = require('path');

// 1. Read faculty-image-question.html
const htmlContent = fs.readFileSync(path.join(__dirname, '..', 'faculty-image-question.html'), 'utf-8');

console.log("--- Test 1: Verify Initial Badge in HTML ---");
if (htmlContent.includes('<div id="imageAnalysisStatus"><span class="badge bg-light text-muted border"><i class="bi bi-image me-1"></i> No Image Selected</span></div>')) {
  console.log("[PASS] HTML initial badge correctly displays 'No Image Selected'");
} else {
  console.error("[FAIL] HTML still contains old/incorrect badge");
  process.exit(1);
}

console.log("--- Test 2: Verify File Input has onchange and accept attributes ---");
if (htmlContent.includes('id="imageFileInput"') && htmlContent.includes('onchange="handleImageFileUpload(event)"')) {
  console.log("[PASS] File input properly specifies onchange='handleImageFileUpload(event)'");
} else {
  console.error("[FAIL] File input does not have expected onchange handler");
  process.exit(1);
}

console.log("--- Test 3: Verify Cache Buster on script tags ---");
if (htmlContent.includes('js/app.js?v=20261026_image_v2')) {
  console.log("[PASS] Script tag uses updated cache buster '?v=20261026_image_v2'");
} else {
  console.error("[FAIL] Missing updated cache buster on app.js script tag");
  process.exit(1);
}

// 2. Read js/app.js
const appJsContent = fs.readFileSync(path.join(__dirname, '..', 'js', 'app.js'), 'utf-8');

console.log("--- Test 4: Verify JS Handlers and Global Bindings ---");
const checks = [
  'let selectedImageFile = null;',
  'window.selectedImageFile = null;',
  'function handleImageFileUpload',
  'function analyzeUploadedImage',
  'function generateQuestionsFromImage',
  'function removeUploadedImage',
  'function saveImageQuestionsToBank',
  'window.handleImageUploadSelection = handleImageFileUpload;',
  'window.handleImageFileUpload = handleImageFileUpload;',
  'window.analyzeUploadedImage = analyzeUploadedImage;',
  'window.generateQuestionsFromImage = generateQuestionsFromImage;',
  '/api/questions/analyze-image',
  '/api/questions/generate-image'
];

for (const check of checks) {
  if (appJsContent.includes(check)) {
    console.log(`[PASS] Found in app.js: '${check}'`);
  } else {
    console.error(`[FAIL] Missing in app.js: '${check}'`);
    process.exit(1);
  }
}

// 3. Read run_frontend.py
const feServerContent = fs.readFileSync(path.join(__dirname, '..', 'run_frontend.py'), 'utf-8');
console.log("--- Test 5: Verify Cache-Control Headers in run_frontend.py ---");
if (feServerContent.includes("no-cache, no-store, must-revalidate")) {
  console.log("[PASS] Frontend server enforces 'Cache-Control: no-cache, no-store, must-revalidate'");
} else {
  console.error("[FAIL] Missing Cache-Control headers in run_frontend.py");
  process.exit(1);
}

console.log("\n=======================================================");
console.log("ALL FRONTEND STATIC, BINDING & SERVER CHECKS PASSED!");
console.log("=======================================================");
