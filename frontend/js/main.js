import { getCurrentUser } from './state/storage.js';
import { showLoginPage, showRegisterPage, showAuthenticatedUI, showPage as routeShowPage } from './ui/router.js';
import { attachAuthHandlers } from './features/auth.js';
import { attachTemplateHandlers, loadTemplates, editTemplate, deleteTemplate } from './features/templates.js';
import { setupFileUpload } from './features/upload.js';
import { loadResults, attachResultsHandlers, downloadFile as downloadResultFile, highlightOperation } from './features/results.js';
import { loadDashboard } from './features/dashboard.js';
import { downloadFileBlob } from './api/backendApi.js';

function initNavigation() {
  // Top menu links
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = link.dataset.page;
      if (page) window.showPage(page);
    });
  });
  // Burger toggle
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');
  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      navToggle.classList.toggle('active');
    });
  }

  // Dashboard quick actions
  document.querySelectorAll('[data-nav]')?.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const target = btn.getAttribute('data-nav');
      if (target) window.showPage(target);
    });
  });
}

function bindGlobals() {
  window.showPage = (pageName) => routeShowPage(pageName, { loadDashboard, loadTemplates, loadResults });
  window.editTemplate = (id) => editTemplate(id);
  window.deleteTemplate = (id) => deleteTemplate(id);
  window.downloadFile = async (operationId) => {
    const blob = await downloadFileBlob(operationId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `result_${operationId}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };
  window.highlightOperation = (id) => highlightOperation(id);
}

function tuneNumericInputsPrecision() {
  document.querySelectorAll('#template-modal input[type="number"]').forEach((el) => {
    el.setAttribute('step', '0.01');
    el.setAttribute('inputmode', 'decimal');
    el.addEventListener('input', (e) => {
      const t = e.currentTarget;
      if (t && typeof t.value === 'string' && t.value.includes(',')) {
        t.value = t.value.replace(',', '.');
      }
    });
  });
}

async function bootstrap() {
  const user = getCurrentUser();
  if (user) showAuthenticatedUI(user.username); else showLoginPage();

  initNavigation();
  try {
    const mod = await import('./api/authApi.js');
    const { refreshAccess } = mod;
    const t = await refreshAccess().catch(() => null);
    if (t) {
      const authState = await import('./state/authState.js');
      authState.setAccessToken(t);
    }
  } catch (_) {}
  attachAuthHandlers({ onLoggedIn: () => { routeShowPage('dashboard', { loadDashboard, loadTemplates, loadResults }); } });
  attachTemplateHandlers();
  setupFileUpload();
  attachResultsHandlers();
  bindGlobals();
  tuneNumericInputsPrecision();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  bootstrap();
}

// Navigate to login on 401 (no hash routing)
window.addEventListener('app:unauthorized', () => {
  try { showLoginPage(); } catch (_) {}
});

