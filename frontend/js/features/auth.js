import { login, register, logout as apiLogout } from '../api/authApi.js';
import { showNotification, showLoading } from '../ui/notifications.js';
import { showLoginPage, showRegisterPage, showAuthenticatedUI } from '../ui/router.js';
import { setCurrentUser, clearCurrentUser } from '../state/storage.js';
import { setAccessToken, clearAccessToken } from '../state/authState.js';

export function attachAuthHandlers({ onLoggedIn } = {}) {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const showReg = document.getElementById('show-register');
  const showLog = document.getElementById('show-login');
  const logoutBtn = document.getElementById('logout-btn');

  if (loginForm)
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('login-username').value;
      const password = document.getElementById('login-password').value;
      try {
        showLoading(true);
        const { accessToken } = await login(username, password);
        setAccessToken(accessToken);
        setCurrentUser({ username });
        showAuthenticatedUI(username);
        showNotification('Вход выполнен', 'success');
        if (onLoggedIn) onLoggedIn();
      } catch (err) {
        showNotification('Ошибка входа: ' + err.message, 'error');
      } finally {
        showLoading(false);
      }
    });

  if (registerForm)
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('register-username').value;
      const password = document.getElementById('register-password').value;
      const confirm = document.getElementById('register-confirm').value;
      if (password !== confirm) {
        showNotification('Пароли не совпадают', 'error');
        return;
      }
      try {
        showLoading(true);
        await register(username, password);
        showNotification('Регистрация успешна. Войдите в систему.', 'success');
        showLoginPage();
      } catch (err) {
        showNotification('Ошибка регистрации: ' + err.message, 'error');
      } finally {
        showLoading(false);
      }
    });

  if (showReg)
    showReg.addEventListener('click', (e) => {
      e.preventDefault();
      showRegisterPage();
    });

  if (showLog)
    showLog.addEventListener('click', (e) => {
      e.preventDefault();
      showLoginPage();
    });

  if (logoutBtn)
    logoutBtn.addEventListener('click', () => {
      (async () => {
        try { await apiLogout(); } catch (_) {}
        clearAccessToken();
        clearCurrentUser();
        try { (function(){ try { if (location.hash) history.replaceState(null, '', location.pathname + location.search); } catch(_) {} })(); } catch (_) {}
        showLoginPage();
        showNotification('Вы вышли из системы', 'info');
      })();
    });
}

