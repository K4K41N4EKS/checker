import { fetchOperations, downloadFileBlob } from '../api/backendApi.js';
import { showNotification, showLoading } from '../ui/notifications.js';

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
}

export function displayResults(operations) {
  const list = document.getElementById('results-list');
  if (!list) return;
  list.textContent = '';
  if (!operations || operations.length === 0) {
    const wrap = document.createElement('div');
    wrap.className = 'empty-state';
    wrap.innerHTML = '<i class="fas fa-inbox"></i><span>Записей пока нет.</span>';
    list.appendChild(wrap);
    return;
  }
  operations.forEach((op) => {
    const date = new Date(op.created_at);
    const formatted = date.toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    const item = document.createElement('div');
    item.className = 'result-item';
    const info = document.createElement('div'); info.className = 'result-info';
    const h3 = document.createElement('h3'); h3.textContent = op.file_name || '';
    const p = document.createElement('p'); p.textContent = 'Загружено: ' + formatted;
    info.appendChild(h3); info.appendChild(p);
    const actions = document.createElement('div'); actions.className = 'result-actions';
    const status = document.createElement('span'); status.className = `result-status status-${op.status}`; status.textContent = getStatusText(op.status);
    actions.appendChild(status);
    if (op.status === 'done') {
      const btn = document.createElement('button'); btn.className = 'btn btn-primary btn-small'; btn.dataset.op = op.id; btn.innerHTML = '<i class="fas fa-download"></i> Скачать';
      btn.addEventListener('click', async () => { await downloadFile(+op.id); });
      actions.appendChild(btn);
    }
    item.appendChild(info); item.appendChild(actions);
    list.appendChild(item);
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
