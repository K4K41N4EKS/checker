import { fetchTemplates, uploadFile, fetchOperations } from '../api/backendApi.js';
import { showNotification, showLoading } from '../ui/notifications.js';

export function setupFileUpload() {
  const uploadArea = document.getElementById('upload-area');
  const fileInput = document.getElementById('file-input');
  const selectFileBtn = document.getElementById('select-file-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const cancelBtn = document.getElementById('cancel-upload-btn');

  if (!uploadArea || !fileInput) return;

  uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
  });
  uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
  uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFileSelect(files[0]);
  });

  if (selectFileBtn) selectFileBtn.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleFileSelect(e.target.files[0]);
  });

  if (uploadBtn) uploadBtn.addEventListener('click', handleFileUpload);
  if (cancelBtn) cancelBtn.addEventListener('click', resetUpload);
}

function handleFileSelect(file) {
  if (!file.name.toLowerCase().endsWith('.docx')) {
    showNotification('Выберите файл .docx', 'error');
    return;
  }
  const sel = document.getElementById('template-selection');
  const actions = document.getElementById('upload-actions');
  if (sel) sel.style.display = 'block';
  if (actions) actions.style.display = 'block';
  loadTemplatesForUpload();
}

async function loadTemplatesForUpload() {
  try {
    const templates = await fetchTemplates();
    const select = document.getElementById('template-select');
    if (!select) return;
    select.innerHTML = '<option value="">Выберите шаблон...</option>';
    templates.forEach((t) => {
      const option = document.createElement('option');
      option.value = t.id;
      option.textContent = t.name;
      select.appendChild(option);
    });
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn) uploadBtn.disabled = true;
    select.addEventListener('change', function () {
      if (uploadBtn) uploadBtn.disabled = !this.value;
    });
  } catch (e) {
    showNotification('Ошибка загрузки списка шаблонов', 'error');
  }
}

async function handleFileUpload() {
  const fileInput = document.getElementById('file-input');
  const templateSelect = document.getElementById('template-select');
  if (!fileInput.files[0]) {
    showNotification('Выберите файл для загрузки', 'error');
    return;
  }
  const templateId = templateSelect.value;
  if (!templateId) {
    showNotification('Выберите шаблон перед отправкой', 'error');
    return;
  }
  try {
    showLoading(true);
    const resp = await uploadFile(fileInput.files[0], templateId);
    showNotification('Файл загружен и отправлен на обработку', 'success');
    resetUpload();
    const goResults = window.showPage;
    if (typeof goResults === 'function') goResults('results');
    if (resp && resp.operation_id) {
      if (typeof window.highlightOperation === 'function') window.highlightOperation(resp.operation_id);
      if (typeof pollOperationStatus === 'function') pollOperationStatus(resp.operation_id);
    }
  } catch (e) {
    showNotification('Ошибка загрузки файла: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

function resetUpload() {
  const fileInput = document.getElementById('file-input');
  const sel = document.getElementById('template-selection');
  const actions = document.getElementById('upload-actions');
  const uploadBtn = document.getElementById('upload-btn');
  if (fileInput) fileInput.value = '';
  if (sel) sel.style.display = 'none';
  if (actions) actions.style.display = 'none';
  if (uploadBtn) uploadBtn.disabled = true;
}




async function pollOperationStatus(operationId, { intervalMs = 2000, maxMs = 5 * 60 * 1000 } = {}) {
  const started = Date.now();
  let lastStatus = null;
  const schedule = () => setTimeout(tick, intervalMs);
  async function tick() {
    try {
      const ops = await fetchOperations();
      const op = ops.find(o => Number(o.id) === Number(operationId));
      if (!op) { if (Date.now() - started < maxMs) return schedule(); else return; }
      if (op.status !== lastStatus) {
        lastStatus = op.status;
        if (op.status === 'processing') showNotification('Файл обрабатывается…', 'info');
        if (op.status === 'done') { showNotification('Готово: результат можно скачать', 'success'); return; }
        if (op.status === 'error') { showNotification('Ошибка обработки файла', 'error'); return; }
      }
      if (Date.now() - started < maxMs) schedule();
    } catch (_) { if (Date.now() - started < maxMs) schedule(); }
  }
  schedule();
}


