import { fetchOperationErrors } from '../api/backendApi.js';
import { showLoading, showNotification } from '../ui/notifications.js';

export function initResultsReport() {
  try { ensureModal(); } catch {}
  const list = document.getElementById('results-list');
  if (!list) return;
  const tick = () => {
    list.querySelectorAll('.result-item').forEach((item) => {
      const actions = item.querySelector('.result-actions');
      const status = actions?.querySelector('.result-status')?.className || '';
      if (!actions || !status.includes('status-done')) return;
      if (actions.querySelector('.btn-secondary.btn-small')) return; // already added
      const opId = item.dataset.opId ? +item.dataset.opId : null;
      if (!opId) return;
      const btn = document.createElement('button');
      btn.className = 'btn btn-secondary btn-small';
      btn.style.marginLeft = '8px';
      btn.innerHTML = '<i class="fas fa-list"></i> Отчет';
      btn.addEventListener('click', async () => { await showErrors(opId); });
      actions.appendChild(btn);
    });
  };
  const observer = new MutationObserver(tick);
  observer.observe(list, { childList: true, subtree: true });
  tick();
}

async function showErrors(operationId) {
  try {
    showLoading(true);
    const items = await fetchOperationErrors(operationId);
    renderErrorsModal(items);
  } catch (e) {
    showNotification('Не удалось получить отчет: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

function ensureModal() {
  if (document.getElementById('results-modal')) return;
  const modal = document.createElement('div');
  modal.id = 'results-modal';
  modal.className = 'modal';
  modal.innerHTML = `
    <div class="modal-content">
      <div class="modal-header">
        <h3>Отчет проверки</h3>
        <button class="modal-close">×</button>
      </div>
      <div class="modal-body"></div>
    </div>`;
  document.body.appendChild(modal);
  modal.querySelector('.modal-close')?.addEventListener('click', () => modal.classList.remove('active'));
}

function renderErrorsModal(items) {
  ensureModal();
  const modal = document.getElementById('results-modal');
  if (!modal) return;
  const body = modal.querySelector('.modal-body');
  const counts = items.reduce((acc, it) => { const c = it.category || 'other'; acc[c] = (acc[c] || 0) + 1; return acc; }, {});
  const header = Object.keys(counts).map(c => `${c}: ${counts[c]}`).join(' · ');
  const listHtml = items.slice(0, 100).map(it => `
    <li>
      <code>#${it.paragraph_index}</code> — <span class="err-msg">${escapeHtml(it.error || '')}</span>
      ${it.code ? `<span class="tag">${it.code}</span>` : ''}
      ${it.severity ? `<span class="tag tag-${it.severity}">${it.severity}</span>` : ''}
    </li>`).join('');
  body.innerHTML = `
    <div class="errors-summary">${header || 'Нет ошибок'}</div>
    <ol class="errors-list">${listHtml}</ol>
  `;
  modal.classList.add('active');
}

function escapeHtml(s) { return s.replace(/[&<>"']/g, (m) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[m])); }

