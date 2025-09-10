import { getCurrentUser } from './state/storage.js';
import { showLoginPage, showRegisterPage, showAuthenticatedUI, showPage as routeShowPage } from './ui/router.js';
import { attachAuthHandlers } from './features/auth.js';
import { attachTemplateHandlers, loadTemplates, editTemplate, deleteTemplate } from './features/templates.js';
import { setupFileUpload } from './features/upload.js';
import { loadResults, attachResultsHandlers, downloadFile as downloadResultFile, highlightOperation } from './features/results.js';
import { loadDashboard } from './features/dashboard.js';
import { downloadFileBlob } from './api/backendApi.js';
// Settings UI removed; single dark theme is used

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

// Theme is managed through account settings

function bindGlobals() {
  // Dashboard buttons rely on this
  window.showPage = (pageName) => routeShowPage(pageName, { loadDashboard, loadTemplates, loadResults });
  // Card actions rely on globals
  window.editTemplate = (id) => editTemplate(id);
  window.deleteTemplate = (id) => deleteTemplate(id);
  // Results download button (in legacy markup it used onclick)
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
  // Helper to highlight a just-created operation
  window.highlightOperation = (id) => highlightOperation(id);
}

function tuneNumericInputsPrecision() {
  // Allow hundredths everywhere in the template modal
  document.querySelectorAll('#template-modal input[type="number"]').forEach((el) => {
    el.setAttribute('step', '0.01');
    el.setAttribute('inputmode', 'decimal');
    // Support comma as decimal separator for RU users
    el.addEventListener('input', (e) => {
      const t = e.currentTarget;
      if (t && typeof t.value === 'string' && t.value.includes(',')) {
        t.value = t.value.replace(',', '.');
      }
    });
  });
}

// Hash routing removed for simplicity and to avoid conflicts.

async function bootstrap() {
  const user = getCurrentUser();
  if (user) showAuthenticatedUI(user.username); else showLoginPage();

  initNavigation();
  // Try to acquire access token from refresh cookie
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
  // hash routing disabled
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap);
} else {
  // DOM already parsed (module at end of body) — init immediately
  bootstrap();
}







// Показать форму входа по глобальному событию из http-клиента
window.addEventListener('app:unauthorized', () => {
  try { require('./ui/router.js'); } catch(_) {}
  try { showLoginPage(); } catch(_) {}
});
