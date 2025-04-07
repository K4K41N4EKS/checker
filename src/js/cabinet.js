document.addEventListener('DOMContentLoaded', () => {
    // Проверка авторизации
    if (!localStorage.getItem('token')) {
        window.location.href = 'auth.html';
    }

    // Заглушка имени пользователя (бэкенд не предоставляет реальных данных)
    document.getElementById('userDisplayName').textContent = "Пользователь #1";

    // Логика выхода
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = 'auth.html';
    });
});