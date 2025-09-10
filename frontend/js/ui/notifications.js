export function showNotification(message, type = 'info') {
  const wrap = document.getElementById('notifications');
  if (!wrap) return;
  const el = document.createElement('div');
  el.className = `notification ${type}`;
  const i = document.createElement('i');
  i.className = ({ success: 'fas fa-check-circle', error: 'fas fa-exclamation-circle', warning: 'fas fa-exclamation-triangle', info: 'fas fa-info-circle' }[type]) || 'fas fa-info-circle';
  const span = document.createElement('span');
  span.textContent = String(message || '');
  el.appendChild(i);
  el.appendChild(span);
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 5000);
}

export function showLoading(show) {
  const buttons = document.querySelectorAll('button[type="submit"], .btn-primary');
  buttons.forEach((btn) => {
    if (show) {
      btn.classList.add('loading');
      btn.disabled = true;
    } else {
      btn.classList.remove('loading');
      btn.disabled = false;
    }
  });
}
