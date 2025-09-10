import { fetchOperations, downloadFileBlob } from '../api/backendApi.js';
import { showNotification, showLoading } from '../ui/notifications.js';

const opNodes = new Map(); // id -> { el, statusEl, status }
let autoRefreshTimer = null;

export async function loadResults() {
  try {
    showLoading(true);
    const status = document.getElementById('status-filter')?.value || null;
    const operations = await fetchOperations(status);
    displayResults(operations);
  } catch (e) {
    showNotification('Ошибка загрузки истории проверок: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

export function attachResultsHandlers() {
  const status = document.getElementById('status-filter');
  if (status) status.addEventListener('change', loadResults);
  if (!autoRefreshTimer) {
    autoRefreshTimer = setInterval(() => {
      const page = document.getElementById('results-page');
      if (page && page.classList.contains('active')) loadResults();
    }, 1500);
  }
}

export function displayResults(operations) {
  const list = document.getElementById('results-list');
  if (!list) return;

  // Empty view
  if (!operations || operations.length === 0) {
    if (!list.firstChild) {
      const wrap = document.createElement('div');
      wrap.className = 'empty-state';
      wrap.innerHTML = '<i class="fas fa-inbox"></i><span>Записей пока нет.</span>';
      list.appendChild(wrap);
    } else if (!list.querySelector('.empty-state')) {
      list.textContent = '';
      const wrap = document.createElement('div');
      wrap.className = 'empty-state';
      wrap.innerHTML = '<i class="fas fa-inbox"></i><span>Записей пока нет.</span>';
      list.appendChild(wrap);
    }
    return;
  }

  const seen = new Set();
  operations.forEach((op) => {
    seen.add(String(op.id));
    renderOrUpdate(op);
  });
  // Remove items that no longer exist
  Array.from(opNodes.keys()).forEach((id) => {
    if (!seen.has(String(id))) {
      const node = opNodes.get(id);
      if (node?.el?.parentElement) node.el.parentElement.removeChild(node.el);
      opNodes.delete(id);
    }
  });
}

export function getStatusText(status) {
  const map = { uploaded: 'Загружено', processing: 'В обработке', done: 'Готово', error: 'Ошибка' };
  return map[status] || status;
}

export async function downloadFile(operationId) {
  try {
    const blob = await downloadFileBlob(operationId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `result_${operationId}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } catch (e) {
    showNotification('Ошибка скачивания результата: ' + e.message, 'error');
  }
}

function renderOrUpdate(op) {
  const list = document.getElementById('results-list');
  let entry = opNodes.get(String(op.id));
  if (!entry) {
    // Create item
    const item = document.createElement('div');
    item.className = 'result-item';
    item.dataset.opId = String(op.id);
    const info = document.createElement('div'); info.className = 'result-info';
    const h3 = document.createElement('h3'); h3.textContent = op.file_name || '';
    const p = document.createElement('p'); p.textContent = 'Загружено: ' + formatDate(op.created_at);
    info.appendChild(h3); info.appendChild(p);
    const actions = document.createElement('div'); actions.className = 'result-actions';
    const statusEl = document.createElement('span'); statusEl.className = `result-status status-${op.status}`; statusEl.textContent = getStatusText(op.status);
    actions.appendChild(statusEl);
    if (op.status === 'done') {
      const btn = document.createElement('button'); btn.className = 'btn btn-primary btn-small'; btn.dataset.op = op.id; btn.innerHTML = '<i class="fas fa-download"></i> Скачать';
      btn.addEventListener('click', async () => { await downloadFile(+op.id); });
      actions.appendChild(btn);
    }
    item.appendChild(info); item.appendChild(actions);
    list.appendChild(item);
    opNodes.set(String(op.id), { el: item, statusEl, status: op.status });
    return;
  }
  // Update existing
  const { el, statusEl, status } = entry;
  const h3 = el.querySelector('h3'); if (h3) h3.textContent = op.file_name || '';
  const p = el.querySelector('p'); if (p) p.textContent = 'Загружено: ' + formatDate(op.created_at);
  if (status !== op.status) {
    // Animate status change
    statusEl.classList.add('status-out');
    const newClass = `result-status status-${op.status}`;
    const newText = getStatusText(op.status);
    statusEl.addEventListener('animationend', function handler() {
      statusEl.removeEventListener('animationend', handler);
      statusEl.className = newClass + ' status-in';
      statusEl.textContent = newText;
      statusEl.addEventListener('animationend', function handler2() {
        statusEl.removeEventListener('animationend', handler2);
        statusEl.className = newClass;
      });
    });
    entry.status = op.status;
  }
  // Toggle download button
  const hasBtn = el.querySelector('button.btn-primary.btn-small');
  if (op.status === 'done' && !hasBtn) {
    const btn = document.createElement('button'); btn.className = 'btn btn-primary btn-small'; btn.dataset.op = op.id; btn.innerHTML = '<i class="fas fa-download"></i> Скачать';
    btn.addEventListener('click', async () => { await downloadFile(+op.id); });
    el.querySelector('.result-actions').appendChild(btn);
  } else if (op.status !== 'done' && hasBtn) {
    hasBtn.remove();
  }
}

function formatDate(d) {
  const date = new Date(d);
  return date.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export function highlightOperation(operationId) {
  const maxMs = 10000; const start = Date.now();
  const timer = setInterval(() => {
    const el = document.querySelector(`[data-op-id="${operationId}"]`);
    if (el) {
      clearInterval(timer);
      try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch {}
      el.classList.add('highlight-pulse');
      setTimeout(() => el.classList.remove('highlight-pulse'), 2400);
    } else if (Date.now() - start > maxMs) {
      clearInterval(timer);
    }
  }, 300);
}
