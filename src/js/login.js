document.addEventListener('DOMContentLoaded', () => {
    // Обработчик формы авторизации
    if (document.getElementById('loginForm')) {
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Заглушка, пока нет реального API авторизации
            localStorage.setItem('token', 'testtoken');
            window.location.href = 'cabinet.html';
        });
    }

    // Проверка авторизации при загрузке кабинета
    if (document.getElementById('logoutBtn')) {
        if (!localStorage.getItem('token')) {
            window.location.href = 'index.html';
        }
        
        // Загрузка данных операций
        try {
            const response = await fetch('http://localhost:3000/file/operations', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });
            
            const operations = await response.json();
            console.log('Operations:', operations);
            // Здесь можно добавить отображение операций
        } catch (error) {
            console.error('Ошибка загрузки операций:', error);
        }

        // Выход из системы
        document.getElementById('logoutBtn').addEventListener('click', () => {
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        });
    }
});