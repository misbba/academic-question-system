const fs = require('fs');
const path = require('path');
const http = require('http');

const projectRoot = path.resolve(__dirname, '..');

// Step 1: Log in as Turing to get session cookie
async function getTuringCookie() {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ email: 'turing@university.edu', password: 'Password123!', role: 'faculty' });
    const req = http.request({
      hostname: 'localhost',
      port: 5000,
      path: '/api/auth/login',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    }, (res) => {
      const cookie = res.headers['set-cookie'] ? res.headers['set-cookie'][0] : '';
      console.log('Login returned status:', res.statusCode, 'Cookie:', cookie ? 'Present' : 'None');
      resolve(cookie);
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

(async () => {
  const cookie = await getTuringCookie();

  const localStorageData = {
    'academic_role': 'faculty',
    'academic_user': JSON.stringify({
      name: 'Dr. Alan Turing',
      full_name: 'Dr. Alan Turing',
      identifier: 'turing@university.edu',
      department: 'Artificial Intelligence & Data Science',
      semester: 'N/A',
      academic_year: '2025-2026'
    })
  };

  const localStorageMock = {
    getItem: (key) => localStorageData[key] || null,
    setItem: (key, val) => { localStorageData[key] = String(val); },
    removeItem: (key) => { delete localStorageData[key]; }
  };

  const elements = {};
  function getOrCreateElement(id) {
    if (!elements[id]) {
      elements[id] = {
        id,
        textContent: '--',
        innerHTML: '',
        classList: { add: () => {}, remove: () => {}, contains: () => false },
        setAttribute: () => {},
        addEventListener: () => {}
      };
    }
    return elements[id];
  }

  const documentMock = {
    getElementById: (id) => getOrCreateElement(id),
    querySelector: (sel) => ({ textContent: '', innerHTML: '', querySelector: () => null, addEventListener: () => {} }),
    querySelectorAll: () => [],
    addEventListener: () => {},
    createElement: () => ({ setAttribute: () => {}, appendChild: () => {}, classList: { add: () => {} } }),
    body: { appendChild: () => {} }
  };

  global.window = {
    location: {
      href: 'http://localhost:8080/faculty-dashboard.html',
      pathname: '/faculty-dashboard.html'
    }
  };
  global.document = documentMock;
  global.localStorage = localStorageMock;

  global.fetch = async (url, opts) => {
    return new Promise((resolve, reject) => {
      const parsed = new URL(url);
      const req = http.request({
        hostname: parsed.hostname,
        port: parsed.port,
        path: parsed.pathname + parsed.search,
        method: opts?.method || 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Cookie': cookie
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            json: async () => JSON.parse(data || '{}')
          });
        });
      });
      req.on('error', reject);
      req.end();
    });
  };

  const authCode = fs.readFileSync(path.join(projectRoot, 'js', 'auth.js'), 'utf8');
  const appCode = fs.readFileSync(path.join(projectRoot, 'js', 'app.js'), 'utf8');

  eval(authCode);
  eval(appCode);

  console.log('\nRunning renderFacultyData() with valid Dr. Alan Turing session...');
  await renderFacultyData();

  console.log('\nResults with valid Dr. Alan Turing session:');
  console.log('facultyNameDisplay:', elements['facultyNameDisplay']?.textContent);
  console.log('totalQuestionsCount:', elements['totalQuestionsCount']?.textContent);
  console.log('activeCoursesCount:', elements['activeCoursesCount']?.textContent);
  console.log('draftPapersCount:', elements['draftPapersCount']?.textContent);
  console.log('publishedExamsCount:', elements['publishedExamsCount']?.textContent);
})();
