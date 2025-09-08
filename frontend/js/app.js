
// Глобальные переменные
let currentUser = null;
let authToken = null;
const API_BASE = '/api';
const AUTH_API_BASE = '/auth';

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Проверяем, есть ли сохраненный токен
    authToken = localStorage.getItem('authToken');
    currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null');
    
    if (authToken && currentUser) {
        showAuthenticatedUI();
    } else {
        showLoginPage();
    }
    
    setupEventListeners();
}

function setupEventListeners() {
    // Навигация
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            if (page) {
                showPage(page);
            }
        });
    });
    
    // Мобильное меню
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    navToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });
    
    // Аутентификация
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('show-register').addEventListener('click', showRegisterPage);
    document.getElementById('show-login').addEventListener('click', showLoginPage);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Загрузка файлов
    setupFileUpload();
    
    // Шаблоны
    document.getElementById('create-template-btn').addEventListener('click', showCreateTemplateModal);
    
    // Модальные окна
    document.getElementById('modal-close').addEventListener('click', hideModal);
    document.getElementById('modal-cancel').addEventListener('click', hideModal);
    document.getElementById('template-form').addEventListener('submit', handleTemplateSubmit);
    
    // Фильтры
    document.getElementById('status-filter').addEventListener('change', loadResults);
}

// Аутентификация
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        showLoading(true);
        
        // Вызов к C++ auth-сервису
        const response = await fetch(`${AUTH_API_BASE}/login`, {
            method: 'GET',
            headers: {
                'username': username,
                'passwd': password
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            const accessToken = response.headers.get('access-token');
            const refreshToken = response.headers.get('refresh-token');
            
            if (accessToken) {
                authToken = accessToken;
                currentUser = { username: username };
                
                localStorage.setItem('authToken', authToken);
                localStorage.setItem('refreshToken', refreshToken);
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                
                showAuthenticatedUI();
                showNotification('Успешный вход в систему', 'success');
            } else {
                throw new Error('Токен не получен');
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Ошибка входа');
        }
    } catch (error) {
        showNotification('Ошибка входа: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm').value;
    
    if (password !== confirmPassword) {
        showNotification('Пароли не совпадают', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        // Регистрация через C++ auth-сервис
        const response = await fetch(`${AUTH_API_BASE}/registration`, {
            method: 'POST',
            headers: {
                'username': username,
                'passwd': password
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showNotification('Регистрация успешна! Теперь войдите в систему.', 'success');
            showLoginPage();
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Ошибка регистрации');
        }
    } catch (error) {
        showNotification('Ошибка регистрации: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    authToken = null;
    currentUser = null;
    showLoginPage();
    showNotification('Вы вышли из системы', 'info');
}

// Синхронизация пользователя с Python API происходит автоматически в C++ auth-сервисе

// UI управление
function showLoginPage() {
    hideAllPages();
    document.getElementById('login-page').classList.add('active');
    document.getElementById('navbar').style.display = 'none';
}

function showRegisterPage() {
    hideAllPages();
    document.getElementById('register-page').classList.add('active');
}

function showAuthenticatedUI() {
    hideAllPages();
    document.getElementById('navbar').style.display = 'block';
    document.getElementById('dashboard-page').classList.add('active');
    document.getElementById('user-name').textContent = currentUser.username;
    loadDashboard();
}

function showPage(pageName) {
    hideAllPages();
    document.getElementById(`${pageName}-page`).classList.add('active');
    
    // Обновляем активную ссылку в навигации
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-page="${pageName}"]`).classList.add('active');
    
    // Загружаем данные для страницы
    switch(pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'templates':
            loadTemplates();
            break;
        case 'results':
            loadResults();
            break;
    }
}

function hideAllPages() {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
}

// Загрузка данных
async function loadDashboard() {
    // Загружаем статистику или последние операции
    try {
        const operations = await fetchOperations();
        // Можно добавить статистику на dashboard
    } catch (error) {
        console.error('Ошибка загрузки dashboard:', error);
    }
}

async function loadTemplates() {
    try {
        showLoading(true);
        const templates = await fetchTemplates();
        displayTemplates(templates);
    } catch (error) {
        showNotification('Ошибка загрузки шаблонов: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function loadResults() {
    try {
        showLoading(true);
        const statusFilter = document.getElementById('status-filter').value;
        const operations = await fetchOperations(statusFilter);
        displayResults(operations);
    } catch (error) {
        showNotification('Ошибка загрузки результатов: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// API вызовы
async function fetchTemplates() {
    const response = await fetch(`${API_BASE}/templates/`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Ошибка загрузки шаблонов');
    }
    
    return await response.json();
}

async function fetchOperations(statusFilter = null) {
    let url = `${API_BASE}/files/operations`;
    if (statusFilter) {
        url += `?status=${statusFilter}`;
    }
    
    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Ошибка загрузки операций');
    }
    
    return await response.json();
}

async function createTemplate(templateData) {
    const response = await fetch(`${API_BASE}/templates/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(templateData)
    });
    
    if (!response.ok) {
        throw new Error('Ошибка создания шаблона');
    }
    
    return await response.json();
}

async function uploadFile(file, templateId = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (templateId) {
        formData.append('template_id', templateId);
    }
    
    const response = await fetch(`${API_BASE}/files/upload`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Ошибка загрузки файла');
    }
    
    return await response.json();
}

async function downloadFile(operationId) {
    const response = await fetch(`${API_BASE}/files/download/${operationId}`, {
        headers: {
            'Authorization': `Bearer ${authToken}`
        }
    });
    
    if (!response.ok) {
        throw new Error('Ошибка скачивания файла');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `result_${operationId}.docx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Загрузка файлов
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const cancelBtn = document.getElementById('cancel-upload-btn');
    
    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Выбор файла
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Загрузка
    uploadBtn.addEventListener('click', handleFileUpload);
    
    // Отмена
    cancelBtn.addEventListener('click', resetUpload);
}

function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.docx')) {
        showNotification('Пожалуйста, выберите .docx файл', 'error');
        return;
    }
    
    document.getElementById('template-selection').style.display = 'block';
    document.getElementById('upload-actions').style.display = 'block';
    
    // Загружаем шаблоны для выбора
    loadTemplatesForUpload();
}

async function loadTemplatesForUpload() {
    try {
        const templates = await fetchTemplates();
        const select = document.getElementById('template-select');
        select.innerHTML = '<option value="">Выберите шаблон...</option>';
        
        templates.forEach(template => {
            const option = document.createElement('option');
            option.value = template.id;
            option.textContent = template.name;
            select.appendChild(option);
        });
        
        // Кнопка загрузки остается отключенной до выбора шаблона
        document.getElementById('upload-btn').disabled = true;
        
        // Добавляем обработчик изменения выбора шаблона
        select.addEventListener('change', function() {
            document.getElementById('upload-btn').disabled = !this.value;
        });
        
    } catch (error) {
        showNotification('Ошибка загрузки шаблонов', 'error');
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
        showNotification('Выберите шаблон для обработки файла', 'error');
        return;
    }
    
    try {
        showLoading(true);
        const result = await uploadFile(fileInput.files[0], templateId);
        
        showNotification('Файл успешно загружен! Обработка началась.', 'success');
        resetUpload();
        showPage('results');
    } catch (error) {
        showNotification('Ошибка загрузки: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

function resetUpload() {
    document.getElementById('file-input').value = '';
    document.getElementById('template-selection').style.display = 'none';
    document.getElementById('upload-actions').style.display = 'none';
    document.getElementById('upload-btn').disabled = true;
}

// Шаблоны
function displayTemplates(templates) {
    const grid = document.getElementById('templates-grid');
    grid.innerHTML = '';
    
    if (templates.length === 0) {
        grid.innerHTML = '<p>Шаблоны не найдены. Создайте первый шаблон!</p>';
        return;
    }
    
    templates.forEach(template => {
        const card = document.createElement('div');
        card.className = 'template-card';
        card.innerHTML = `
            <h3>${template.name}</h3>
            <p>Создан: ${new Date(template.created_at).toLocaleDateString()}</p>
            <div class="template-actions">
                <button class="btn btn-primary btn-small" onclick="editTemplate('${template.id}')">
                    <i class="fas fa-edit"></i> Редактировать
                </button>
                <button class="btn btn-secondary btn-small" onclick="deleteTemplate('${template.id}')">
                    <i class="fas fa-trash"></i> Удалить
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function showCreateTemplateModal() {
    document.getElementById('modal-title').textContent = 'Создать шаблон';
    document.getElementById('template-form').reset();
    delete document.getElementById('template-form').dataset.templateId;
    showModal();
}

function buildTemplateForm() {
    const sections = document.querySelector('.template-sections');
    sections.innerHTML = `
        <div class="template-section">
            <h3>Поля страницы</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Верхнее поле (см)</label>
                    <input type="number" name="top_margin" step="0.1" placeholder="2.0">
                </div>
                <div class="form-group">
                    <label>Нижнее поле (см)</label>
                    <input type="number" name="bottom_margin" step="0.1" placeholder="2.0">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Левое поле (см)</label>
                    <input type="number" name="left_margin" step="0.1" placeholder="3.0">
                </div>
                <div class="form-group">
                    <label>Правое поле (см)</label>
                    <input type="number" name="right_margin" step="0.1" placeholder="1.5">
                </div>
            </div>
        </div>
        
        <div class="template-section">
            <h3>Заголовки</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Шрифт</label>
                    <select name="static_header.font_name">
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Arial">Arial</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Размер</label>
                    <input type="number" name="static_header.font_size" placeholder="14">
                </div>
            </div>
            <div class="form-group">
                <label>Выравнивание</label>
                <select name="static_header.alignment">
                    <option value="center">По центру</option>
                    <option value="left">По левому краю</option>
                    <option value="right">По правому краю</option>
                    <option value="justify">По ширине</option>
                </select>
            </div>
        </div>
        
        <div class="template-section">
            <h3>Основной текст</h3>
            <div class="form-row">
                <div class="form-group">
                    <label>Шрифт</label>
                    <select name="body_text.font_name">
                        <option value="Times New Roman">Times New Roman</option>
                        <option value="Arial">Arial</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Размер</label>
                    <input type="number" name="body_text.font_size" placeholder="14">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Отступ первой строки (см)</label>
                    <input type="number" name="body_text.first_line_indent" step="0.1" placeholder="1.25">
                </div>
                <div class="form-group">
                    <label>Межстрочный интервал</label>
                    <input type="number" name="body_text.line_spacing" step="0.1" placeholder="1.5">
                </div>
            </div>
            <div class="form-group">
                <label>Выравнивание</label>
                <select name="body_text.alignment">
                    <option value="justify">По ширине</option>
                    <option value="left">По левому краю</option>
                    <option value="center">По центру</option>
                    <option value="right">По правому краю</option>
                </select>
            </div>
        </div>
    `;
}

async function handleTemplateSubmit(e) {
    e.preventDefault();
    
    const name = document.getElementById('template-name').value;
    const isEdit = document.getElementById('modal-title').textContent.includes('Редактировать');
    const templateId = document.getElementById('template-form').dataset.templateId;
    
    try {
        showLoading(true);
        
        // Собираем все настройки из формы
        const filters = collectTemplateSettings();
        
        const url = isEdit ? `${API_BASE}/templates/${templateId}` : `${API_BASE}/templates/`;
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                name: name,
                filters: filters
            })
        });
        
        if (response.ok) {
            const message = isEdit ? 'Шаблон обновлен успешно' : 'Шаблон создан успешно';
            showNotification(message, 'success');
            document.getElementById('template-form').reset();
            hideModal();
            loadTemplates();
        } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = isEdit ? 'Ошибка обновления шаблона' : 'Ошибка создания шаблона';
            throw new Error(errorData.detail || errorMessage);
        }
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Сбор настроек шаблона из формы
function collectTemplateSettings() {
    const filters = {};
    
    // Поля документа
    filters.top_margin = parseFloat(document.getElementById('top-margin').value);
    filters.bottom_margin = parseFloat(document.getElementById('bottom-margin').value);
    filters.left_margin = parseFloat(document.getElementById('left-margin').value);
    filters.right_margin = parseFloat(document.getElementById('right-margin').value);
    
    // Начало после заголовка
    filters.start_after_heading = document.getElementById('start-after-heading').value;
    
    // Статические заголовки
    filters.static_header = {
        font_name: document.getElementById('static-font').value,
        font_size: parseInt(document.getElementById('static-size').value),
        alignment: document.getElementById('static-alignment').value,
        first_line_indent: parseFloat(document.getElementById('static-indent').value),
        line_spacing: parseFloat(document.getElementById('static-spacing').value)
    };
    
    // Заголовки 1 уровня
    filters.main_header_level_1 = {
        font_name: document.getElementById('h1-font').value,
        font_size: parseInt(document.getElementById('h1-size').value),
        alignment: document.getElementById('h1-alignment').value,
        first_line_indent: parseFloat(document.getElementById('h1-indent').value),
        line_spacing: parseFloat(document.getElementById('h1-spacing').value),
        all_caps: document.getElementById('h1-all-caps').checked
    };
    
    // Заголовки 2 уровня
    filters.main_header_level_2 = {
        font_name: document.getElementById('h2-font').value,
        font_size: parseInt(document.getElementById('h2-size').value),
        alignment: document.getElementById('h2-alignment').value,
        first_line_indent: parseFloat(document.getElementById('h2-indent').value),
        line_spacing: parseFloat(document.getElementById('h2-spacing').value),
        all_caps: document.getElementById('h2-all-caps').checked
    };
    
    // Заголовки 3 уровня
    filters.main_header_level_3 = {
        font_name: document.getElementById('h3-font').value,
        font_size: parseInt(document.getElementById('h3-size').value),
        alignment: document.getElementById('h3-alignment').value,
        first_line_indent: parseFloat(document.getElementById('h3-indent').value),
        line_spacing: parseFloat(document.getElementById('h3-spacing').value),
        all_caps: document.getElementById('h3-all-caps').checked
    };
    
    // Основной текст
    filters.body_text = {
        font_name: document.getElementById('body-font').value,
        font_size: parseInt(document.getElementById('body-size').value),
        alignment: document.getElementById('body-alignment').value,
        first_line_indent: parseFloat(document.getElementById('body-indent').value),
        line_spacing: parseFloat(document.getElementById('body-spacing').value)
    };
    
    // Списки 1 уровня
    filters.list_level_1 = {
        font_name: document.getElementById('list1-font').value,
        font_size: parseInt(document.getElementById('list1-size').value),
        alignment: document.getElementById('list1-alignment').value,
        first_line_indent: parseFloat(document.getElementById('list1-indent').value),
        line_spacing: parseFloat(document.getElementById('list1-spacing').value)
    };
    
    // Списки 2 уровня
    filters.list_level_2 = {
        font_name: document.getElementById('list2-font').value,
        font_size: parseInt(document.getElementById('list2-size').value),
        alignment: document.getElementById('list2-alignment').value,
        first_line_indent: parseFloat(document.getElementById('list2-indent').value),
        line_spacing: parseFloat(document.getElementById('list2-spacing').value)
    };
    
    // Подписи к рисункам
    filters.figure_caption = {
        font_name: document.getElementById('figure-font').value,
        font_size: parseInt(document.getElementById('figure-size').value),
        alignment: document.getElementById('figure-alignment').value,
        first_line_indent: parseFloat(document.getElementById('figure-indent').value),
        line_spacing: parseFloat(document.getElementById('figure-spacing').value)
    };
    
    // Подписи к таблицам
    filters.table_caption = {
        font_name: document.getElementById('table-font').value,
        font_size: parseInt(document.getElementById('table-size').value),
        alignment: document.getElementById('table-alignment').value,
        first_line_indent: parseFloat(document.getElementById('table-indent').value),
        line_spacing: parseFloat(document.getElementById('table-spacing').value)
    };
    
    return filters;
}

// Заполнение формы данными шаблона
function populateTemplateForm(template) {
    // Название шаблона
    document.getElementById('template-name').value = template.name || '';
    
    // Поля документа
    if (template.filters.top_margin !== undefined) {
        document.getElementById('top-margin').value = template.filters.top_margin;
    }
    if (template.filters.bottom_margin !== undefined) {
        document.getElementById('bottom-margin').value = template.filters.bottom_margin;
    }
    if (template.filters.left_margin !== undefined) {
        document.getElementById('left-margin').value = template.filters.left_margin;
    }
    if (template.filters.right_margin !== undefined) {
        document.getElementById('right-margin').value = template.filters.right_margin;
    }
    
    // Начало после заголовка
    if (template.filters.start_after_heading) {
        document.getElementById('start-after-heading').value = template.filters.start_after_heading;
    }
    
    // Статические заголовки
    if (template.filters.static_header) {
        const staticHeader = template.filters.static_header;
        if (staticHeader.font_name) document.getElementById('static-font').value = staticHeader.font_name;
        if (staticHeader.font_size) document.getElementById('static-size').value = staticHeader.font_size;
        if (staticHeader.alignment) document.getElementById('static-alignment').value = staticHeader.alignment;
        if (staticHeader.first_line_indent !== undefined) document.getElementById('static-indent').value = staticHeader.first_line_indent;
        if (staticHeader.line_spacing !== undefined) document.getElementById('static-spacing').value = staticHeader.line_spacing;
    }
    
    // Заголовки 1 уровня
    if (template.filters.main_header_level_1) {
        const h1 = template.filters.main_header_level_1;
        if (h1.font_name) document.getElementById('h1-font').value = h1.font_name;
        if (h1.font_size) document.getElementById('h1-size').value = h1.font_size;
        if (h1.alignment) document.getElementById('h1-alignment').value = h1.alignment;
        if (h1.first_line_indent !== undefined) document.getElementById('h1-indent').value = h1.first_line_indent;
        if (h1.line_spacing !== undefined) document.getElementById('h1-spacing').value = h1.line_spacing;
        if (h1.all_caps !== undefined) document.getElementById('h1-all-caps').checked = h1.all_caps;
    }
    
    // Заголовки 2 уровня
    if (template.filters.main_header_level_2) {
        const h2 = template.filters.main_header_level_2;
        if (h2.font_name) document.getElementById('h2-font').value = h2.font_name;
        if (h2.font_size) document.getElementById('h2-size').value = h2.font_size;
        if (h2.alignment) document.getElementById('h2-alignment').value = h2.alignment;
        if (h2.first_line_indent !== undefined) document.getElementById('h2-indent').value = h2.first_line_indent;
        if (h2.line_spacing !== undefined) document.getElementById('h2-spacing').value = h2.line_spacing;
        if (h2.all_caps !== undefined) document.getElementById('h2-all-caps').checked = h2.all_caps;
    }
    
    // Заголовки 3 уровня
    if (template.filters.main_header_level_3) {
        const h3 = template.filters.main_header_level_3;
        if (h3.font_name) document.getElementById('h3-font').value = h3.font_name;
        if (h3.font_size) document.getElementById('h3-size').value = h3.font_size;
        if (h3.alignment) document.getElementById('h3-alignment').value = h3.alignment;
        if (h3.first_line_indent !== undefined) document.getElementById('h3-indent').value = h3.first_line_indent;
        if (h3.line_spacing !== undefined) document.getElementById('h3-spacing').value = h3.line_spacing;
        if (h3.all_caps !== undefined) document.getElementById('h3-all-caps').checked = h3.all_caps;
    }
    
    // Основной текст
    if (template.filters.body_text) {
        const body = template.filters.body_text;
        if (body.font_name) document.getElementById('body-font').value = body.font_name;
        if (body.font_size) document.getElementById('body-size').value = body.font_size;
        if (body.alignment) document.getElementById('body-alignment').value = body.alignment;
        if (body.first_line_indent !== undefined) document.getElementById('body-indent').value = body.first_line_indent;
        if (body.line_spacing !== undefined) document.getElementById('body-spacing').value = body.line_spacing;
    }
    
    // Списки 1 уровня
    if (template.filters.list_level_1) {
        const list1 = template.filters.list_level_1;
        if (list1.font_name) document.getElementById('list1-font').value = list1.font_name;
        if (list1.font_size) document.getElementById('list1-size').value = list1.font_size;
        if (list1.alignment) document.getElementById('list1-alignment').value = list1.alignment;
        if (list1.first_line_indent !== undefined) document.getElementById('list1-indent').value = list1.first_line_indent;
        if (list1.line_spacing !== undefined) document.getElementById('list1-spacing').value = list1.line_spacing;
    }
    
    // Списки 2 уровня
    if (template.filters.list_level_2) {
        const list2 = template.filters.list_level_2;
        if (list2.font_name) document.getElementById('list2-font').value = list2.font_name;
        if (list2.font_size) document.getElementById('list2-size').value = list2.font_size;
        if (list2.alignment) document.getElementById('list2-alignment').value = list2.alignment;
        if (list2.first_line_indent !== undefined) document.getElementById('list2-indent').value = list2.first_line_indent;
        if (list2.line_spacing !== undefined) document.getElementById('list2-spacing').value = list2.line_spacing;
    }
    
    // Подписи к рисункам
    if (template.filters.figure_caption) {
        const figure = template.filters.figure_caption;
        if (figure.font_name) document.getElementById('figure-font').value = figure.font_name;
        if (figure.font_size) document.getElementById('figure-size').value = figure.font_size;
        if (figure.alignment) document.getElementById('figure-alignment').value = figure.alignment;
        if (figure.first_line_indent !== undefined) document.getElementById('figure-indent').value = figure.first_line_indent;
        if (figure.line_spacing !== undefined) document.getElementById('figure-spacing').value = figure.line_spacing;
    }
    
    // Подписи к таблицам
    if (template.filters.table_caption) {
        const table = template.filters.table_caption;
        if (table.font_name) document.getElementById('table-font').value = table.font_name;
        if (table.font_size) document.getElementById('table-size').value = table.font_size;
        if (table.alignment) document.getElementById('table-alignment').value = table.alignment;
        if (table.first_line_indent !== undefined) document.getElementById('table-indent').value = table.first_line_indent;
        if (table.line_spacing !== undefined) document.getElementById('table-spacing').value = table.line_spacing;
    }
}

// Результаты
function displayResults(operations) {
    const list = document.getElementById('results-list');
    list.innerHTML = '';
    
    if (operations.length === 0) {
        list.innerHTML = '<p>Операции не найдены.</p>';
        return;
    }
    
    operations.forEach(operation => {
        const item = document.createElement('div');
        item.className = 'result-item';
        
        // Форматируем дату без времени
        const date = new Date(operation.created_at);
        const formattedDate = date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        item.innerHTML = `
            <div class="result-info">
                <h3>${operation.file_name}</h3>
                <p>Загружено: ${formattedDate}</p>
            </div>
            <div class="result-actions">
                <span class="result-status status-${operation.status}">${getStatusText(operation.status)}</span>
                ${operation.status === 'done' ? `
                    <button class="btn btn-primary btn-small" onclick="downloadFile(${operation.id})">
                        <i class="fas fa-download"></i> Скачать
                    </button>
                ` : ''}
            </div>
        `;
        list.appendChild(item);
    });
}

function getStatusText(status) {
    const statusTexts = {
        'uploaded': 'Загружено',
        'processing': 'Обработка',
        'done': 'Готово',
        'error': 'Ошибка'
    };
    return statusTexts[status] || status;
}

// Модальные окна
function showModal() {
    document.getElementById('template-modal').classList.add('active');
}

function hideModal() {
    document.getElementById('template-modal').classList.remove('active');
}

// Утилиты
function showNotification(message, type = 'info') {
    const notifications = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type];
    
    notification.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
    `;
    
    notifications.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function showLoading(show) {
    const buttons = document.querySelectorAll('button[type="submit"], .btn-primary');
    buttons.forEach(btn => {
        if (show) {
            btn.classList.add('loading');
            btn.disabled = true;
        } else {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    });
}

// Глобальные функции для onclick
window.showPage = showPage;
window.editTemplate = async function(id) {
    try {
        showLoading(true);
        
        // Загружаем данные шаблона
        const response = await fetch(`${API_BASE}/templates/${id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки шаблона');
        }
        
        const template = await response.json();
        
        // Сохраняем ID шаблона в форме
        document.getElementById('template-form').dataset.templateId = id;
        
        // Обновляем заголовок модального окна
        document.getElementById('modal-title').textContent = 'Редактировать шаблон';
        
        // Заполняем форму данными шаблона
        populateTemplateForm(template);
        
        // Показываем модальное окно
        showModal('edit');
        
    } catch (error) {
        showNotification('Ошибка загрузки шаблона: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
};

window.deleteTemplate = async function(id) {
    if (confirm('Вы уверены, что хотите удалить этот шаблон?')) {
        try {
            const response = await fetch(`${API_BASE}/templates/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                showNotification('Шаблон удален', 'success');
                loadTemplates();
            } else {
                throw new Error('Ошибка удаления шаблона');
            }
        } catch (error) {
            showNotification('Ошибка удаления: ' + error.message, 'error');
        }
    }
};

window.downloadFile = downloadFile;
