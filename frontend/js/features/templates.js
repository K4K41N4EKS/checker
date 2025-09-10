import { fetchTemplates, getTemplate, createTemplate, updateTemplate, deleteTemplate as apiDeleteTemplate } from '../api/backendApi.js';
import { showNotification, showLoading } from '../ui/notifications.js';
import { showModal, hideModal } from '../ui/modal.js';

export async function loadTemplates() {
  try {
    showLoading(true);
    const templates = await fetchTemplates();
    displayTemplates(templates);
  } catch (e) {
    showNotification('Ошибка загрузки списка шаблонов: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

export function attachTemplateHandlers() {
  const btn = document.getElementById('create-template-btn');
  const closeBtn = document.getElementById('modal-close');
  const cancelBtn = document.getElementById('modal-cancel');
  const form = document.getElementById('template-form');

  if (btn) btn.addEventListener('click', showCreateTemplateModal);
  if (closeBtn) closeBtn.addEventListener('click', hideModal);
  if (cancelBtn) cancelBtn.addEventListener('click', hideModal);
  if (form) form.addEventListener('submit', handleTemplateSubmit);
}

export function displayTemplates(templates) {
  const grid = document.getElementById('templates-grid');
  if (!grid) return;
  grid.textContent = '';
  if (!templates || templates.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<i class="fas fa-folder-open"></i><span>Шаблонов пока нет. Создайте первый!</span>';
    grid.appendChild(empty);
    return;
  }
  templates.forEach((tpl) => {
    const card = document.createElement('div');
    card.className = 'template-card';
    const h3 = document.createElement('h3');
    h3.textContent = tpl.name || '';
    const p = document.createElement('p');
    p.textContent = 'Создан: ' + new Date(tpl.created_at).toLocaleDateString();
    const actions = document.createElement('div');
    actions.className = 'template-actions';
    const editBtn = document.createElement('button');
    editBtn.className = 'btn btn-primary btn-small';
    editBtn.dataset.action = 'edit';
    editBtn.dataset.id = tpl.id;
    editBtn.innerHTML = '<i class="fas fa-edit"></i> Редактировать';
    const delBtn = document.createElement('button');
    delBtn.className = 'btn btn-secondary btn-small';
    delBtn.dataset.action = 'delete';
    delBtn.dataset.id = tpl.id;
    delBtn.innerHTML = '<i class="fas fa-trash"></i> Удалить';
    actions.appendChild(editBtn);
    actions.appendChild(delBtn);
    card.appendChild(h3);
    card.appendChild(p);
    card.appendChild(actions);
    grid.appendChild(card);
    editBtn.addEventListener('click', () => editTemplate(tpl.id));
    delBtn.addEventListener('click', () => deleteTemplate(tpl.id));
  });
}

export function showCreateTemplateModal() {
  const form = document.getElementById('template-form');
  if (!form) return;
  form.reset();
  delete form.dataset.templateId;
  const title = document.getElementById('modal-title');
  if (title) title.textContent = 'Создать шаблон';
  showModal();
}

export async function editTemplate(id) {
  try {
    showLoading(true);
    const template = await getTemplate(id);
    const form = document.getElementById('template-form');
    if (form) form.dataset.templateId = id;
    const title = document.getElementById('modal-title');
    if (title) title.textContent = 'Изменить шаблон';
    populateTemplateForm(template);
    showModal();
  } catch (e) {
    showNotification('Ошибка загрузки шаблона: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

export async function deleteTemplate(id) {
  if (!confirm('Удалить шаблон?')) return;
  try {
    await apiDeleteTemplate(id);
    showNotification('Шаблон удалён', 'success');
    await loadTemplates();
  } catch (e) {
    showNotification('Не удалось удалить: ' + e.message, 'error');
  }
}

async function handleTemplateSubmit(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const name = document.getElementById('template-name').value;
  const payload = { name, filters: collectFiltersFromForm() };
  const isEdit = !!form.dataset.templateId;
  try {
    showLoading(true);
    if (isEdit) await updateTemplate(form.dataset.templateId, payload);
    else await createTemplate(payload);
    hideModal();
    showNotification(isEdit ? 'Шаблон обновлён' : 'Шаблон создан', 'success');
    await loadTemplates();
  } catch (e) {
    showNotification('Ошибка сохранения шаблона: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

function val(id) {
  const el = document.getElementById(id);
  if (!el) return undefined;
  if (el.type === 'checkbox') return el.checked;
  return el.value;
}

function collectFiltersFromForm() {
  const filters = {};
  const startAfter = document.getElementById('start-after-heading')?.value || '';

  filters.top_margin = Number(val('top-margin'));
  filters.bottom_margin = Number(val('bottom-margin'));
  filters.left_margin = Number(val('left-margin'));
  filters.right_margin = Number(val('right-margin'));
  filters.start_after_heading = startAfter;

  filters.static_header = {
    font_name: val('static-font'),
    font_size: Number(val('static-size')),
    alignment: val('static-alignment'),
    first_line_indent: Number(val('static-indent')),
    line_spacing: Number(val('static-spacing')),
  };

  filters.main_header_level_1 = {
    font_name: val('h1-font'),
    font_size: Number(val('h1-size')),
    alignment: val('h1-alignment'),
    first_line_indent: Number(val('h1-indent')),
    line_spacing: Number(val('h1-spacing')),
    all_caps: Boolean(val('h1-all-caps')),
  };
  filters.main_header_level_2 = {
    font_name: val('h2-font'),
    font_size: Number(val('h2-size')),
    alignment: val('h2-alignment'),
    first_line_indent: Number(val('h2-indent')),
    line_spacing: Number(val('h2-spacing')),
    all_caps: Boolean(val('h2-all-caps')),
  };
  filters.main_header_level_3 = {
    font_name: val('h3-font'),
    font_size: Number(val('h3-size')),
    alignment: val('h3-alignment'),
    first_line_indent: Number(val('h3-indent')),
    line_spacing: Number(val('h3-spacing')),
    all_caps: Boolean(val('h3-all-caps')),
  };

  filters.body_text = {
    font_name: val('body-font'),
    font_size: Number(val('body-size')),
    alignment: val('body-alignment'),
    first_line_indent: Number(val('body-indent')),
    line_spacing: Number(val('body-spacing')),
  };

  filters.list_level_1 = {
    font_name: val('list1-font'),
    font_size: Number(val('list1-size')),
    alignment: val('list1-alignment'),
    first_line_indent: Number(val('list1-indent')),
    line_spacing: Number(val('list1-spacing')),
  };
  filters.list_level_2 = {
    font_name: val('list2-font'),
    font_size: Number(val('list2-size')),
    alignment: val('list2-alignment'),
    first_line_indent: Number(val('list2-indent')),
    line_spacing: Number(val('list2-spacing')),
  };

  filters.figure_caption = {
    font_name: val('figure-font'),
    font_size: Number(val('figure-size')),
    alignment: val('figure-alignment'),
    first_line_indent: Number(val('figure-indent')),
    line_spacing: Number(val('figure-spacing')),
  };
  filters.table_caption = {
    font_name: val('table-font'),
    font_size: Number(val('table-size')),
    alignment: val('table-alignment'),
    first_line_indent: Number(val('table-indent')),
    line_spacing: Number(val('table-spacing')),
  };
  // New: text inside table cells
  filters.table_cell_text = {
    font_name: val('tablecell-font'),
    font_size: Number(val('tablecell-size')),
    alignment: val('tablecell-alignment'),
    first_line_indent: Number(val('tablecell-indent')),
    line_spacing: Number(val('tablecell-spacing')),
  };
  return filters;
}

export function populateTemplateForm(template) {
  if (!template || !template.filters) return;
  const f = template.filters;
  if (f.top_margin !== undefined) document.getElementById('top-margin').value = f.top_margin;
  if (f.bottom_margin !== undefined) document.getElementById('bottom-margin').value = f.bottom_margin;
  if (f.left_margin !== undefined) document.getElementById('left-margin').value = f.left_margin;
  if (f.right_margin !== undefined) document.getElementById('right-margin').value = f.right_margin;
  if (f.start_after_heading) document.getElementById('start-after-heading').value = f.start_after_heading;

  if (f.static_header) {
    const s = f.static_header;
    if (s.font_name) document.getElementById('static-font').value = s.font_name;
    if (s.font_size) document.getElementById('static-size').value = s.font_size;
    if (s.alignment) document.getElementById('static-alignment').value = s.alignment;
    if (s.first_line_indent !== undefined) document.getElementById('static-indent').value = s.first_line_indent;
    if (s.line_spacing !== undefined) document.getElementById('static-spacing').value = s.line_spacing;
  }
  if (f.main_header_level_1) {
    const h1 = f.main_header_level_1;
    if (h1.font_name) document.getElementById('h1-font').value = h1.font_name;
    if (h1.font_size) document.getElementById('h1-size').value = h1.font_size;
    if (h1.alignment) document.getElementById('h1-alignment').value = h1.alignment;
    if (h1.first_line_indent !== undefined) document.getElementById('h1-indent').value = h1.first_line_indent;
    if (h1.line_spacing !== undefined) document.getElementById('h1-spacing').value = h1.line_spacing;
    if (h1.all_caps !== undefined) document.getElementById('h1-all-caps').checked = h1.all_caps;
  }
  if (f.main_header_level_2) {
    const h2 = f.main_header_level_2;
    if (h2.font_name) document.getElementById('h2-font').value = h2.font_name;
    if (h2.font_size) document.getElementById('h2-size').value = h2.font_size;
    if (h2.alignment) document.getElementById('h2-alignment').value = h2.alignment;
    if (h2.first_line_indent !== undefined) document.getElementById('h2-indent').value = h2.first_line_indent;
    if (h2.line_spacing !== undefined) document.getElementById('h2-spacing').value = h2.line_spacing;
    if (h2.all_caps !== undefined) document.getElementById('h2-all-caps').checked = h2.all_caps;
  }
  if (f.main_header_level_3) {
    const h3 = f.main_header_level_3;
    if (h3.font_name) document.getElementById('h3-font').value = h3.font_name;
    if (h3.font_size) document.getElementById('h3-size').value = h3.font_size;
    if (h3.alignment) document.getElementById('h3-alignment').value = h3.alignment;
    if (h3.first_line_indent !== undefined) document.getElementById('h3-indent').value = h3.first_line_indent;
    if (h3.line_spacing !== undefined) document.getElementById('h3-spacing').value = h3.line_spacing;
    if (h3.all_caps !== undefined) document.getElementById('h3-all-caps').checked = h3.all_caps;
  }
  if (f.body_text) {
    const b = f.body_text;
    if (b.font_name) document.getElementById('body-font').value = b.font_name;
    if (b.font_size) document.getElementById('body-size').value = b.font_size;
    if (b.alignment) document.getElementById('body-alignment').value = b.alignment;
    if (b.first_line_indent !== undefined) document.getElementById('body-indent').value = b.first_line_indent;
    if (b.line_spacing !== undefined) document.getElementById('body-spacing').value = b.line_spacing;
  }
  if (f.list_level_1) {
    const l1 = f.list_level_1;
    if (l1.font_name) document.getElementById('list1-font').value = l1.font_name;
    if (l1.font_size) document.getElementById('list1-size').value = l1.font_size;
    if (l1.alignment) document.getElementById('list1-alignment').value = l1.alignment;
    if (l1.first_line_indent !== undefined) document.getElementById('list1-indent').value = l1.first_line_indent;
    if (l1.line_spacing !== undefined) document.getElementById('list1-spacing').value = l1.line_spacing;
  }
  if (f.list_level_2) {
    const l2 = f.list_level_2;
    if (l2.font_name) document.getElementById('list2-font').value = l2.font_name;
    if (l2.font_size) document.getElementById('list2-size').value = l2.font_size;
    if (l2.alignment) document.getElementById('list2-alignment').value = l2.alignment;
    if (l2.first_line_indent !== undefined) document.getElementById('list2-indent').value = l2.first_line_indent;
    if (l2.line_spacing !== undefined) document.getElementById('list2-spacing').value = l2.line_spacing;
  }
  if (f.figure_caption) {
    const fg = f.figure_caption;
    if (fg.font_name) document.getElementById('figure-font').value = fg.font_name;
    if (fg.font_size) document.getElementById('figure-size').value = fg.font_size;
    if (fg.alignment) document.getElementById('figure-alignment').value = fg.alignment;
    if (fg.first_line_indent !== undefined) document.getElementById('figure-indent').value = fg.first_line_indent;
    if (fg.line_spacing !== undefined) document.getElementById('figure-spacing').value = fg.line_spacing;
  }
  if (f.table_caption) {
    const tb = f.table_caption;
    if (tb.font_name) document.getElementById('table-font').value = tb.font_name;
    if (tb.font_size) document.getElementById('table-size').value = tb.font_size;
    if (tb.alignment) document.getElementById('table-alignment').value = tb.alignment;
    if (tb.first_line_indent !== undefined) document.getElementById('table-indent').value = tb.first_line_indent;
    if (tb.line_spacing !== undefined) document.getElementById('table-spacing').value = tb.line_spacing;
  }
  if (f.table_cell_text) {
    const tc = f.table_cell_text;
    if (tc.font_name) document.getElementById('tablecell-font').value = tc.font_name;
    if (tc.font_size) document.getElementById('tablecell-size').value = tc.font_size;
    if (tc.alignment) document.getElementById('tablecell-alignment').value = tc.alignment;
    if (tc.first_line_indent !== undefined) document.getElementById('tablecell-indent').value = tc.first_line_indent;
    if (tc.line_spacing !== undefined) document.getElementById('tablecell-spacing').value = tc.line_spacing;
  }
}
