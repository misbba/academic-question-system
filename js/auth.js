/**
 * Academic Question System -- Authentication Client Helper
 * Flask REST API Integration (STEP 9B)
 */

const API_AUTH_BASE = 'http://localhost:5000/api/auth';

const Auth = {
  /**
   * Register a new Faculty or Student user
   */
  async register(data) {
    try {
      const response = await fetch(`${API_AUTH_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data)
      });
      const result = await response.json();
      return { ok: response.ok, status: response.status, data: result };
    } catch (err) {
      console.error('Registration fetch error:', err);
      return {
        ok: false,
        status: 0,
        data: { status: 'error', message: 'Unable to connect to the server. Please make sure the Flask backend is running.' }
      };
    }
  },

  /**
   * Log in user
   */
  async login(email, password, role) {
    try {
      const response = await fetch(`${API_AUTH_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password, role })
      });
      const result = await response.json();
      if (response.ok && result.user) {
        localStorage.setItem('academic_role', result.user.role);
        localStorage.setItem('academic_user', JSON.stringify({
          name: result.user.full_name,
          identifier: result.user.email,
          department: result.user.department,
          semester: result.user.semester,
          academic_year: result.user.academic_year
        }));
      }
      return { ok: response.ok, status: response.status, data: result };
    } catch (err) {
      console.error('Login fetch error:', err);
      return {
        ok: false,
        status: 0,
        data: { status: 'error', message: 'Unable to connect to the server. Please make sure the Flask backend is running.' }
      };
    }
  },

  /**
   * Get current authenticated user session from Flask
   */
  async getCurrentUser() {
    try {
      const response = await fetch(`${API_AUTH_BASE}/me`, {
        method: 'GET',
        credentials: 'include'
      });
      if (!response.ok) {
        return null;
      }
      const result = await response.json();
      return result.user || null;
    } catch (err) {
      console.error('getCurrentUser fetch error:', err);
      return null;
    }
  },

  /**
   * Enforce page-level authentication & role protection
   */
  async requireRole(expectedRole) {
    const user = await this.getCurrentUser();

    if (!user) {
      // Unauthenticated -> redirect to login page
      console.warn('Unauthenticated access attempt. Redirecting to login.');
      const redirectTarget = expectedRole === 'faculty' ? 'faculty-login.html' : 'student-login.html';
      window.location.href = redirectTarget;
      return null;
    }

    if (user.role !== expectedRole) {
      // Role mismatch -> redirect to own dashboard
      console.warn(`Role mismatch: user role '${user.role}' vs page role '${expectedRole}'.`);
      const targetDashboard = user.role === 'faculty' ? 'faculty-dashboard.html' : 'student-dashboard.html';
      window.location.href = targetDashboard;
      return null;
    }

    // Keep localStorage in sync for STEPS 1-8 compatibility
    localStorage.setItem('academic_role', user.role);
    localStorage.setItem('academic_user', JSON.stringify({
      name: user.full_name,
      identifier: user.email,
      department: user.department,
      semester: user.semester,
      academic_year: user.academic_year
    }));

    // Update header UI elements
    this.updateHeaderProfile(user);
    return user;
  },

  /**
   * Populate header profile UI elements across all pages
   */
  updateHeaderProfile(user) {
    if (!user) return;
    const fullName = user.full_name || user.name || 'User';
    const dept = user.department || 'Artificial Intelligence & Data Science';
    const sem = user.semester || 'Sem 6';
    const year = user.academic_year || '2025-2026';

    const facName = document.getElementById('facultyNameDisplay');
    const facDept = document.getElementById('facultyDeptDisplay');
    const studName = document.getElementById('studentNameDisplay');
    const studRoll = document.getElementById('studentRollDisplay');
    const welcomeH1 = document.querySelector('.dashboard-main h1');
    const studWelcome = document.getElementById('studentWelcomeHeading');
    const paperAuthor = document.getElementById('paperAuthorDisplay');

    if (facName) facName.textContent = fullName;
    if (facDept) facDept.textContent = `${dept} • ${year}`;
    if (studName) studName.textContent = fullName;
    if (studRoll) studRoll.textContent = `${dept} • ${sem}`;
    if (paperAuthor) paperAuthor.textContent = fullName;

    if (studWelcome) {
      studWelcome.textContent = `Welcome back, ${fullName.split(' ')[0]}!`;
    } else if (welcomeH1 && (window.location.pathname.includes('student-dashboard.html') || window.location.pathname.includes('faculty-dashboard.html'))) {
      welcomeH1.textContent = `Welcome back, ${fullName}!`;
    }
  },

  /**
   * Synchronously populate profile UI from localStorage immediately upon page load
   */
  syncFromLocalStorage() {
    try {
      const stored = localStorage.getItem('academic_user');
      if (stored) {
        const user = JSON.parse(stored);
        this.updateHeaderProfile(user);
      }
    } catch (e) {
      console.warn('Could not sync user from localStorage:', e);
    }
  },

  /**
   * Reset Password API call
   */
  async resetPassword(email, role, newPassword, confirmPassword) {
    try {
      const response = await fetch(`${API_AUTH_BASE}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          email: email.trim(),
          role: role,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });
      const result = await response.json();
      return { ok: response.ok, status: response.status, data: result };
    } catch (err) {
      console.error('Password reset fetch error:', err);
      return {
        ok: false,
        status: 0,
        data: { status: 'error', message: 'Unable to connect to server. Ensure Flask backend is running.' }
      };
    }
  },

  /**
   * Log out user
   */
  async logout() {
    try {
      await fetch(`${API_AUTH_BASE}/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (err) {
      console.error('Logout API error:', err);
    }
    const currentRole = localStorage.getItem('academic_role') || 'student';
    localStorage.removeItem('academic_role');
    localStorage.removeItem('academic_user');

    const loginRedirect = currentRole === 'faculty' ? 'faculty-login.html' : 'student-login.html';
    window.location.href = loginRedirect;
  }
};

/**
 * Open interactive Forgot Password modal
 */
function openForgotPasswordModal(defaultRole) {
  const role = defaultRole || (window.location.pathname.includes('faculty') ? 'faculty' : 'student');
  let modalEl = document.getElementById('forgotPasswordModal');

  if (!modalEl) {
    const modalHtml = `
      <div class="modal fade" id="forgotPasswordModal" tabindex="-1" aria-labelledby="forgotPasswordModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content card-academic shadow">
            <div class="modal-header card-academic-header">
              <h5 class="modal-title" id="forgotPasswordModalLabel"><i class="bi bi-shield-lock me-2 text-warning"></i>Reset Password</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4">
              <div id="forgotPasswordAlert" class="alert d-none small"></div>
              <form id="forgotPasswordForm">
                <div class="mb-3">
                  <label for="resetEmail" class="form-label fw-semibold">Registered Email Address</label>
                  <input type="email" class="form-control" id="resetEmail" placeholder="e.g. user@vsb.com" required>
                </div>
                <div class="mb-3">
                  <label for="resetRole" class="form-label fw-semibold">Account Role</label>
                  <select class="form-select" id="resetRole" required>
                    <option value="faculty" ${role === 'faculty' ? 'selected' : ''}>Faculty</option>
                    <option value="student" ${role === 'student' ? 'selected' : ''}>Student</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label for="resetNewPassword" class="form-label fw-semibold">New Password (min 8 chars)</label>
                  <input type="password" class="form-control" id="resetNewPassword" placeholder="Enter new password" minlength="8" required>
                </div>
                <div class="mb-3">
                  <label for="resetConfirmPassword" class="form-label fw-semibold">Confirm New Password</label>
                  <input type="password" class="form-control" id="resetConfirmPassword" placeholder="Confirm new password" minlength="8" required>
                </div>
                <button type="submit" class="btn btn-academic-primary w-100 py-2" id="resetSubmitBtn">
                  <i class="bi bi-arrow-repeat me-1"></i> Update Password
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    modalEl = document.getElementById('forgotPasswordModal');

    const form = document.getElementById('forgotPasswordForm');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('resetEmail').value;
      const selRole = document.getElementById('resetRole').value;
      const newPwd = document.getElementById('resetNewPassword').value;
      const confPwd = document.getElementById('resetConfirmPassword').value;
      const alertBox = document.getElementById('forgotPasswordAlert');
      const submitBtn = document.getElementById('resetSubmitBtn');

      if (newPwd !== confPwd) {
        alertBox.className = 'alert alert-danger small';
        alertBox.textContent = 'Passwords do not match.';
        alertBox.classList.remove('d-none');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Updating...';

      const res = await Auth.resetPassword(email, selRole, newPwd, confPwd);

      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-arrow-repeat me-1"></i> Update Password';

      if (res.ok) {
        alertBox.className = 'alert alert-success small';
        alertBox.textContent = res.data.message || 'Password updated successfully! You can now log in.';
        alertBox.classList.remove('d-none');
        setTimeout(() => {
          const bsModal = bootstrap.Modal.getInstance(modalEl);
          if (bsModal) bsModal.hide();
        }, 2000);
      } else {
        alertBox.className = 'alert alert-danger small';
        alertBox.textContent = res.data.message || 'Password reset failed. Please check your credentials.';
        alertBox.classList.remove('d-none');
      }
    });
  }

  // Pre-fill email if available in login field
  const loginEmail = document.getElementById('facultyId') || document.getElementById('rollNumber') || document.getElementById('email');
  if (loginEmail && loginEmail.value) {
    const resetEmailInput = document.getElementById('resetEmail');
    if (resetEmailInput) resetEmailInput.value = loginEmail.value;
  }

  const alertBox = document.getElementById('forgotPasswordAlert');
  if (alertBox) alertBox.classList.add('d-none');

  const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
  bsModal.show();
}

// Auto-sync profile as soon as auth.js loads
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Auth.syncFromLocalStorage());
  } else {
    Auth.syncFromLocalStorage();
  }
}

/**
 * Sidebar Toggle Controller
 * Clean collapse and expand without page closing or unintended navigation
 */
function toggleSidebar(e) {
  if (e) {
    if (typeof e.preventDefault === 'function') e.preventDefault();
    if (typeof e.stopPropagation === 'function') e.stopPropagation();
  }
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) {
    sidebar.classList.toggle('collapsed');
    const isCollapsed = sidebar.classList.contains('collapsed');
    try {
      localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');
    } catch (_) {}
  }
  return false;
}
window.toggleSidebar = toggleSidebar;

if (typeof document !== 'undefined') {
  const restoreSidebar = () => {
    try {
      if (localStorage.getItem('sidebar_collapsed') === 'true') {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.add('collapsed');
      }
    } catch (_) {}
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', restoreSidebar);
  } else {
    restoreSidebar();
  }
}

