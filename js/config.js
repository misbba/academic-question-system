/**
 * Academic Question Generation and Difficulty Balancing System
 * Frontend Environment Configuration
 * 
 * INSTRUCTIONS FOR DEPLOYMENT:
 * 1. Localhost Development:
 *    When running on http://localhost:8080, API calls automatically route to http://localhost:5000.
 * 
 * 2. Static Site Deployment (Render / Vercel / Netlify / GitHub Pages):
 *    Replace the default production URL below with your actual deployed Flask Web Service URL
 *    (e.g., 'https://academic-question-system-backend.onrender.com' - without trailing slash).
 * 
 * 3. Runtime Override (No code change needed):
 *    You can also override the API URL anytime in browser DevTools Console:
 *    localStorage.setItem('API_BASE_URL', 'https://your-backend.onrender.com');
 */
(function (root) {
  function detectDefaultApiUrl() {
    if (typeof window !== 'undefined') {
      // 1. Runtime override from browser localStorage
      try {
        const stored = localStorage.getItem('API_BASE_URL');
        if (stored && stored.trim()) {
          return stored.trim().replace(/\/+$/, '');
        }
      } catch (e) {
        // localStorage may be disabled or restricted
      }

      // 2. Automatic Localhost Detection
      const hostname = window.location.hostname;
      if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '0.0.0.0') {
        return 'http://localhost:5000';
      }

      // 3. If hosted together on the same origin (e.g. reverse proxy / unified container)
      if (window.location.origin && !window.location.origin.includes('null') && !window.location.origin.startsWith('file:')) {
        // Default to Render production backend URL for standalone static hosting:
        return 'https://academic-question-system.onrender.com';
      }
    }
    return 'http://localhost:5000';
  }

  const detectedUrl = detectDefaultApiUrl();

  root.APP_CONFIG = {
    // Current active API Base URL (without trailing slash)
    API_BASE_URL: detectedUrl,
    APP_NAME: 'Academic Question Generation and Difficulty Balancing System',
    VERSION: '1.0.0'
  };

  root.getApiBaseUrl = function () {
    if (root.APP_CONFIG && root.APP_CONFIG.API_BASE_URL) {
      return root.APP_CONFIG.API_BASE_URL.replace(/\/+$/, '');
    }
    return detectDefaultApiUrl();
  };
})(typeof window !== 'undefined' ? window : this);
