import { API_BASE } from '../constants.js';
import { apiFetch } from './http.js';

// common fetch logic moved to api/http.js

export async function fetchTemplates() {
  const response = await apiFetch(`${API_BASE}/templates/`);
  if (!response.ok) throw new Error('Failed to fetch templates');
  return response.json();
}

export async function getTemplate(id) {
  const response = await apiFetch(`${API_BASE}/templates/${id}`);
  if (!response.ok) throw new Error('Failed to fetch template');
  return response.json();
}

export async function createTemplate(payload) {
  const response = await apiFetch(`${API_BASE}/templates/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to create template');
  return response.json();
}

export async function updateTemplate(id, payload) {
  const response = await apiFetch(`${API_BASE}/templates/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error('Failed to update template');
  return response.json();
}

export async function deleteTemplate(id) {
  const response = await apiFetch(`${API_BASE}/templates/${id}`, { method: 'DELETE' });
  if (!response.ok) throw new Error('Failed to delete template');
  return response.json().catch(() => ({}));
}

export async function fetchOperations(statusFilter = null) {
  let url = `${API_BASE}/files/operations`;
  if (statusFilter) url += `?status=${encodeURIComponent(statusFilter)}`;
  const response = await apiFetch(url);
  if (!response.ok) throw new Error('Failed to fetch operations');
  return response.json();
}

export async function uploadFile(file, templateId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (templateId) formData.append('template_id', templateId);
  const response = await apiFetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Upload failed');
  return response.json();
}

export async function downloadFileBlob(operationId) {
  const response = await apiFetch(`${API_BASE}/files/download/${operationId}`);
  if (!response.ok) throw new Error('Download failed');
  return response.blob();
}
