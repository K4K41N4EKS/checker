import { getAccessToken, setAccessToken, clearAccessToken } from '../state/authState.js';
import { clearCurrentUser } from '../state/storage.js';
import { refreshAccess } from './authApi.js';
import { showNotification } from '../ui/notifications.js';

function authHeaders() {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

let refreshPromise = null;
let unauthorizedHandler = defaultUnauthorizedHandler;

export function setUnauthorizedHandler(handler) {
  unauthorizedHandler = typeof handler === 'function' ? handler : defaultUnauthorizedHandler;
}

async function ensureAccessToken() {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const token = await refreshAccess();
        if (token) setAccessToken(token);
        return token;
      } finally {
        refreshPromise = null;
      }
    })();
  }
  return refreshPromise;
}

export async function apiFetch(url, options = {}) {
  const make = (headers) => fetch(url, { ...options, headers: { ...(options.headers || {}), ...headers } });
  let res = await make(authHeaders());

  if (res.status === 401) {
    try {
      const t = await ensureAccessToken();
      if (!t) throw new Error('No access after refresh');
      res = await make(authHeaders());
    } catch (_) {
      unauthorizedHandler();
      throw new Error('Unauthorized');
    }
    if (res.status === 401) {
      unauthorizedHandler();
      throw new Error('Unauthorized');
    }
  }

  return res;
}

function defaultUnauthorizedHandler() {
  try { clearAccessToken(); } catch {}
  try { clearCurrentUser(); } catch {}
  try { showNotification("Сессия истекла. Пожалуйста, войдите снова.", "warning"); } catch {}
  try { window.dispatchEvent(new Event("app:unauthorized")); } catch {}
  try { if (location && location.hash) { history.replaceState(null, "", location.pathname + location.search); } } catch {}
}
export default apiFetch;


