

function handleOfSubmitLoginButton(event) 
{
    event.preventDefault();
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // Проверяем наличие токенов в хранилищах
    if (sessionStorage.getItem('access-token') && localStorage.getItem('refresh-token')) {
        var messageDiv = document.getElementById('message');
        messageDiv.innerHTML = 'Вы уже авторизованы';
        messageDiv.classList.add('show');

        // Скрываем сообщение через несколько секунд
        setTimeout(function() {
            messageDiv.classList.remove('show');
        }, 3000); // Скрываем через 3 секунды

        return; // Прерываем функцию, чтобы не отправлять запрос
    }

    fetch('http://localhost:3333/login', {
        method: 'GET',
        headers: {
            'username': username,
            'passwd': password
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(`${data.message}`);
            });
        }

        // Извлекаем токены из заголовков
        const accessToken = response.headers.get('access-token');
        const refreshToken = response.headers.get('refresh-token');

        // Извлекаем сообщение из тела ответа
        return response.json().then(data => {
            const message = data.message;

            if (accessToken && refreshToken) {
                // Сохраняем токены
                sessionStorage.setItem('access-token', accessToken);
                localStorage.setItem('refresh-token', refreshToken);

                // Показываем сообщение
                var messageDiv = document.getElementById('message');
                messageDiv.innerHTML = message + " Перенаправляем на главную страницу..";
                messageDiv.classList.add('show');

                // Скрываем сообщение через несколько секунд
                setTimeout(function() {
                    messageDiv.classList.remove('show');
                    window.location.href = 'http://localhost:3001/checker';
                }, 3000); // Скрываем через 3 секунды
            } else {
                throw new Error(message); // Выбрасываем ошибку с сообщением
            }
        });
    })
    .catch(error => {
        var messageDiv = document.getElementById('message');
        messageDiv.innerHTML = error.message;
        messageDiv.classList.add('show');

        // Скрываем сообщение через несколько секунд
        setTimeout(function() {
            messageDiv.classList.remove('show');
        }, 3000); // Скрываем через 3 секунды
    });
};

function handleOfSubmitRegistrationButton(event) 
{
    event.preventDefault();
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    fetch('http://localhost:3333/registration', {
        method: 'POST',
        headers: {
            'username': username,
            'passwd': password
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(`${data.message}`);
            });
        }
        return response.json();
    })
    .then(data => {
        var messageDiv = document.getElementById('message');
        messageDiv.innerHTML = data.message + " Перенаправляем на страницу входа...";
        messageDiv.classList.add('show');

        setTimeout(function() {
            messageDiv.classList.remove('show');
            window.location.href = 'http://localhost:3001/checker/login';
        }, 2000);
    })
    .catch(error => {
        var messageDiv = document.getElementById('message');
        messageDiv.innerHTML = error.message; // Выводим сообщение об ошибке
        messageDiv.classList.add('show');

        // Скрываем сообщение через несколько секунд
        setTimeout(function() {
            messageDiv.classList.remove('show');
        }, 3000); // Скрываем через 3 секунды
    });
};

