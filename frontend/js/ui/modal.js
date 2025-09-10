export function showModal() {
  const m = document.getElementById('template-modal');
  if (m) m.classList.add('active');
}

export function hideModal() {
  const m = document.getElementById('template-modal');
  if (m) m.classList.remove('active');
}

