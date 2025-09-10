export function hideAllPages() {
  document.querySelectorAll('.page').forEach((p) => p.classList.remove('active'));
}

export function showLoginPage() {
  hideAllPages();
  const nb = document.getElementById('navbar');
  if (nb) nb.style.display = 'none';
  const p = document.getElementById('login-page');
  if (p) p.classList.add('active');
}

export function showRegisterPage() {
  hideAllPages();
  const nb = document.getElementById('navbar');
  if (nb) nb.style.display = 'none';
  const p = document.getElementById('register-page');
  if (p) p.classList.add('active');
}

export function showAuthenticatedUI(username) {
  hideAllPages();
  const nb = document.getElementById('navbar');
  if (nb) nb.style.display = 'block';
  const p = document.getElementById('dashboard-page');
  if (p) p.classList.add('active');
  const u = document.getElementById('user-name');
  if (u) u.textContent = username || '';
}

export function showPage(pageName, loaders = {}) {
  hideAllPages();
  const p = document.getElementById(`${pageName}-page`);
  if (p) p.classList.add('active');

  document.querySelectorAll('.nav-link').forEach((l) => l.classList.remove('active'));
  const active = document.querySelector(`[data-page="${pageName}"]`);
  if (active) active.classList.add('active');

  if (pageName === 'dashboard' && loaders.loadDashboard) loaders.loadDashboard();
  if (pageName === 'templates' && loaders.loadTemplates) loaders.loadTemplates();
  if (pageName === 'results' && loaders.loadResults) loaders.loadResults();
}
