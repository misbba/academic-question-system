import os
import re
import subprocess

def main():
    app_js_path = os.path.join(os.path.dirname(__file__), '..', 'js', 'app.js')
    with open(app_js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    helper = """// Global API Base URL Helper (supports Localhost and Render Production)
function getApiBaseUrl() {
  if (typeof window !== 'undefined') {
    if (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) {
      return window.APP_CONFIG.API_BASE_URL.replace(/\\/+$/, '');
    }
    try {
      const stored = localStorage.getItem('API_BASE_URL');
      if (stored && stored.trim()) return stored.trim().replace(/\\/+$/, '');
    } catch (e) {}
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '0.0.0.0') {
      return 'http://localhost:5000';
    }
    return 'https://academic-question-system-backend.onrender.com';
  }
  return 'http://localhost:5000';
}
window.getApiBaseUrl = getApiBaseUrl;

"""

    new_content = helper + content

    # 1. Replace single-quoted 'http://localhost:5000/api/...' with `${getApiBaseUrl()}/api/...`
    def repl_sq(match):
        path = match.group(1)
        return '`${getApiBaseUrl()}' + path + '`'

    new_content = re.sub(r"'http://localhost:5000(/api/[^']*)'", repl_sq, new_content)

    # 2. Replace backtick `http://localhost:5000 with `${getApiBaseUrl()}
    new_content = new_content.replace('`http://localhost:5000', '`${getApiBaseUrl()}')

    # 3. Replace inside template string href="http://localhost:5000 with href="${getApiBaseUrl()}
    new_content = new_content.replace('"http://localhost:5000', '"${getApiBaseUrl()}')

    # Write out to app.js
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully updated js/app.js!")

    # Verify with node syntax check
    res = subprocess.run(["node", "-c", app_js_path], capture_output=True, text=True)
    if res.returncode == 0:
        print("node -c verification SUCCESSFUL! Zero syntax errors.")
    else:
        print("node -c verification FAILED:", res.stderr)

if __name__ == '__main__':
    main()
