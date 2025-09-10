import { getCurrentUser } from './state/storage.js';
import { showLoginPage, showRegisterPage, showAuthenticatedUI, showPage as routeShowPage } from './ui/router.js';
import { attachAuthHandlers } from './features/auth.js';
import { attachTemplateHandlers, loadTemplates, editTemplate, deleteTemplate } from './features/templates.js';
import { setupFileUpload } from './features/upload.js';
import { loadResults, attachResultsHandlers, downloadFile as downloadResultFile } from './features/results.js';
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
  window.showPage = (pageName) => { routeShowPage(pageName, { loadDashboard, loadTemplates, loadResults }); location.hash = pageName; };
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

function setupHashRouting() {
  function applyFromHash() {
    const hash = (location.hash || '').replace('#', '');
    const user = getCurrentUser();
    if (!user) {
      if (hash === 'register') showRegisterPage(); else showLoginPage();
      return;
    }
    const allowed = ['dashboard', 'templates', 'upload', 'results'];
    const page = allowed.includes(hash) ? hash : 'dashboard';
    routeShowPage(page, { loadDashboard, loadTemplates, loadResults });
    if (!hash) { try { location.hash = page; } catch {} }
  }
  window.addEventListener('hashchange', applyFromHash);
  // Initial sync
  applyFromHash();
}

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
  attachAuthHandlers({ onLoggedIn: () => { location.hash = 'dashboard'; loadDashboard(); } });
  attachTemplateHandlers();
  setupFileUpload();
  attachResultsHandlers();
  bindGlobals();
  tuneNumericInputsPrecision();
  setupHashRouting();
}

document.addEventListener('DOMContentLoaded', bootstrap);




