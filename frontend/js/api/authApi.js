import { AUTH_API_BASE } from '../constants.js';

export async function login(username, password) {
  const response = await fetch(`${AUTH_API_BASE}/login`, {
    method: 'GET',
    headers: {
      'username': username,
      'passwd': password,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Login failed');
  }

  const data = await response.json();
  const accessToken = response.headers.get('access-token');
  const refreshToken = response.headers.get('refresh-token');
  if (!accessToken) throw new Error('No access token');
  return { data, accessToken, refreshToken };
}

export async function register(username, password) {
  const response = await fetch(`${AUTH_API_BASE}/registration`, {
    method: 'POST',
    headers: {
      'username': username,
      'passwd': password,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'Registration failed');
  }
  return response.json();
}

export async function refreshAccess() {
  const response = await fetch(`${AUTH_API_BASE}/updateaccesst`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to refresh access token');
  const accessToken = response.headers.get('access-token');
  if (!accessToken) throw new Error('No access token');
  return accessToken;
}

export async function logout() {
  const response = await fetch(`${AUTH_API_BASE}/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Logout failed');
}
